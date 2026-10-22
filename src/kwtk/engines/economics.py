"""Plant economics with NREL PySAM (Single Owner), from the plant's hourly export.

Lifetime generation is built here and handed to PySAM hour by hour
(system_use_lifetime_output = 1), so degradation is explicit:
  PV part     year-one export x (1 - first-year loss) x (1 - annual rate)^(n-1)
  battery     its discharge share fades by calendar + cycle loss each year, unless
              augmentation maintains energy (then the augmentation cost is a yearly
              O&M line at the configured storage price)
Weather years cycle through the life in order. Leap days are dropped (8760 h).

Costs are read from the unit in each key:
  *_usd_per_wp      x DC capacity          *_usd_per_kwac    x inverter AC rating
  *_usd_per_kwh     x storage energy       *_usd_per_kw      x storage power
  *_usd             lump sum               *_pct_of_capex    x the other capex lines
  (opex) *_usd_per_kwdc_year, *_usd_per_kw_year, *_usd_year, *_pct_of_capex (per year)
An unrecognised unit is an error. Auxiliary power imported at night (battery
cooling) is netted against export at the PPA price. PySAM runs in USD; KWD figures use the assumption
fx.kwd_per_usd. Taxes default to zero (Kuwait levies no corporate income tax on
Kuwaiti companies; the configuration may set one), no depreciation or incentives."""

from __future__ import annotations

import numpy as np
import pandas as pd
import PySAM.Singleowner as so

from ..config.models import PlantConfig
from ..plant.resolve import Resolver


def _base(key: str, cfg: PlantConfig, pv: dict | None) -> float:
    dc_wp = (pv["dc_capacity_mwp"] * 1e6) if pv else 0.0
    ac_kw = (pv["ac_rating_mw"] * 1e3) if pv else 0.0
    st_kwh = sum(b.energy_mwh for b in cfg.storage.blocks) * 1e3 if cfg.storage else 0.0
    st_kw = sum(b.power_mw for b in cfg.storage.blocks) * 1e3 if cfg.storage else 0.0
    for suffix, base in (("_usd_per_wp", dc_wp), ("_usd_per_kwac", ac_kw), ("_usd_per_kwh", st_kwh),
                         ("_usd_per_kwdc_year", dc_wp / 1e3), ("_usd_per_kw_year", st_kw if key.startswith("storage") else ac_kw),
                         ("_usd_per_kw", st_kw), ("_usd_year", 1.0), ("_usd", 1.0)):
        if key.endswith(suffix):
            return base
    raise ValueError(f"economics: cannot tell the unit of '{key}' (use a suffix such as _usd_per_wp, _usd_per_kwh, _usd)")


def costs(cfg: PlantConfig, pv: dict | None, r: Resolver, cleanings_per_year: float) -> dict:
    capex_lines, pct = {}, 0.0
    for k, v in cfg.economics.capex.items():
        x = float(r(v, f"economics.capex.{k}"))
        if k.endswith("_pct_of_capex"):
            pct += x / 100
        else:
            capex_lines[k] = x * _base(k, cfg, pv)
    capex = sum(capex_lines.values()) * (1 + pct)
    capex_lines["percentage_items"] = sum(capex_lines.values()) * pct
    opex_lines = {}
    for k, v in cfg.economics.opex.items():
        x = float(r(v, f"economics.opex.{k}"))
        opex_lines[k] = capex * x / 100 if k.endswith("_pct_of_capex") else x * _base(k, cfg, pv)
    if cfg.om.cleaning.method != "none" and pv:
        c = float(r(cfg.om.cleaning.cost_usd_per_mwp_per_cleaning, "om.cleaning.cost_usd_per_mwp_per_cleaning"))
        opex_lines["cleaning"] = c * pv["dc_capacity_mwp"] * cleanings_per_year
    return {"capex_usd": capex, "capex_lines": capex_lines, "opex_usd_year": sum(opex_lines.values()), "opex_lines": opex_lines}


def lifetime_generation(cfg: PlantConfig, hourly: pd.DataFrame, r: Resolver, efc_per_year: float | None) -> tuple[np.ndarray, list]:
    life = cfg.economics.life_years
    h = hourly[~((hourly.index.month == 2) & (hourly.index.day == 29))]
    years = sorted(set(h.index.year))
    d1 = float(r(cfg.om.degradation.pv_first_year_pct, "om.degradation.pv_first_year_pct")) / 100
    d = float(r(cfg.om.degradation.pv_pct_per_year, "om.degradation.pv_pct_per_year")) / 100
    fade, aug_mwh = [], []
    cap = 1.0
    blocks = cfg.storage.blocks if cfg.storage else []
    E = sum(b.energy_mwh for b in blocks)
    for n in range(life):
        loss = 0.0
        for b in blocks:
            dg = b.degradation
            if dg.model == "none":
                continue
            yearly = dg.calendar_pct_per_year / 100 + (dg.cycle_pct_per_1000_efc / 100 * (efc_per_year or 0) / 1000
                                                      if dg.model == "calendar_plus_cycle" else 0)
            loss += yearly * b.energy_mwh / E
        maintain = blocks and all(b.augmentation == "maintain_energy" for b in blocks)
        aug_mwh.append(loss * E if (maintain and n > 0) else 0.0)
        if not maintain and n > 0:
            cap = max(cap - loss, min((b.degradation.end_of_life_capacity for b in blocks), default=0))
        fade.append(cap)
    gen = []
    for n in range(life):
        y = h[h.index.year == years[n % len(years)]]
        pv_part = (y.export - y.battery.clip(lower=0)).clip(lower=0)
        batt_part = np.minimum(y.battery.clip(lower=0), y.export)
        pv_f = (1 - d1) * (1 - d) ** n
        gen.append((pv_part * pv_f + batt_part * fade[n] - y["import"]).values)
    return np.concatenate(gen), aug_mwh


def run(cfg: PlantConfig, pv: dict | None, disp: dict, r: Resolver, cleanings_per_year: float) -> dict:
    e = cfg.economics
    fx = float(r.assumption("fx.kwd_per_usd", "economics.currency"))
    c = costs(cfg, pv, r, cleanings_per_year)
    gen_mw, aug_mwh = lifetime_generation(cfg, disp["hourly"], r, disp.get("efc_per_year"))
    m = so.default("PVWattsSingleOwner")
    m.Lifetime.system_use_lifetime_output = 1
    m.FinancialParameters.analysis_period = e.life_years
    m.SystemOutput.gen = tuple(gen_mw * 1000)            # kW, hourly over the life
    m.SystemOutput.degradation = (0,)
    m.value("system_pre_curtailment_kwac", tuple(gen_mw * 1000))   # curtailment is already applied upstream
    cap_kw = (pv["ac_rating_mw"] if pv else sum(b.power_mw for b in cfg.storage.blocks)) * 1000
    m.SystemOutput.system_capacity = cap_kw
    m.FinancialParameters.system_capacity = cap_kw
    m.SystemCosts.total_installed_cost = c["capex_usd"]
    storage_price = next((float(r(v, f"economics.capex.{k}")) for k, v in e.capex.items() if k.startswith("storage") and k.endswith("_usd_per_kwh")), 0.0)
    aug_cost = [a * 1000 * storage_price for a in aug_mwh]
    infl_for_om = float(r.assumption("finance.inflation", "economics.finance.inflation"))
    # costs in the configuration are real (base-year USD); PySAM takes a schedule as
    # nominal dollars, so each year is inflated here
    m.SystemCosts.om_fixed = tuple((c["opex_usd_year"] + a) * (1 + infl_for_om) ** (n + 1) for n, a in enumerate(aug_cost))
    m.SystemCosts.om_capacity = (0,)
    m.SystemCosts.om_production = (0,)
    m.SystemCosts.om_fixed_escal = 0
    f = e.finance
    wacc = float(r(f.wacc_real, "economics.finance.wacc_real"))
    infl = float(r.assumption("finance.inflation", "economics.finance.inflation"))
    m.FinancialParameters.real_discount_rate = wacc * 100
    m.FinancialParameters.inflation_rate = infl * 100
    m.Lifetime.inflation_rate = infl * 100
    m.FinancialParameters.debt_option = 0                 # 0 = debt as a percent of cost (1 would size by DSCR)
    m.FinancialParameters.dscr_reserve_months = 0
    for k in ("equip1_reserve_cost", "equip2_reserve_cost", "equip3_reserve_cost"):
        setattr(m.FinancialParameters, k, 0)
    m.FinancialParameters.debt_percent = float(r(f.debt_fraction, "economics.finance.debt_fraction")) * 100
    if f.debt_rate is not None:
        m.FinancialParameters.term_int_rate = float(r(f.debt_rate, "economics.finance.debt_rate")) * 100
    if f.tenor_years:
        m.FinancialParameters.term_tenor = f.tenor_years
    tax = float(r(f.tax_rate, "economics.finance.tax_rate")) * 100
    m.FinancialParameters.federal_tax_rate = (tax,)
    m.FinancialParameters.state_tax_rate = (0,)
    m.FinancialParameters.property_tax_rate = 0
    m.FinancialParameters.insurance_rate = 0               # insurance belongs in opex (insurance_pct_of_capex)
    m.FinancialParameters.cost_debt_closing = 0
    m.FinancialParameters.cost_debt_fee = 0
    m.FinancialParameters.construction_financing_cost = 0
    m.FinancialParameters.salvage_percentage = 0
    m.FinancialParameters.months_working_reserve = 0
    m.FinancialParameters.months_receivables_reserve = 0
    for k in m.Depreciation.export():
        if k.startswith("depr_alloc") or k.startswith("depr_bonus"):
            setattr(m.Depreciation, k, 0)
    m.Depreciation.depr_alloc_custom_percent = 100
    m.Depreciation.depr_custom_schedule = (0,)
    # No US incentives (the PySAM default case carries a production tax credit):
    # every credit and incentive amount or percent is zeroed, scalar or schedule.
    for g in (m.TaxCreditIncentives, m.PaymentIncentives):
        for k, v in g.export().items():
            if ("amount" in k or "percent" in k) and "deprbas" not in k and "tax_" not in k and "maxvalue" not in k:
                setattr(g, k, (0,) if isinstance(v, (tuple, list)) else 0)
    rev = e.revenue
    if rev.ppa_price_fils_per_kwh is not None:
        price_kwd = float(r(rev.ppa_price_fils_per_kwh, "economics.revenue.ppa_price_fils_per_kwh")) / 1000
        m.Revenue.ppa_soln_mode = 1
        m.Revenue.ppa_price_input = (price_kwd / fx,)
    else:
        m.Revenue.ppa_soln_mode = 0
    m.Revenue.ppa_escalation = rev.escalation_pct
    m.Revenue.dispatch_factors_ts = (1,) * 8760
    m.Revenue.ppa_multiplier_model = 0
    m.ElectricityRates.en_electricity_rates = 0      # no US utility bill: auxiliary imports net against export
    m.UtilityBill.utility_bill_w_sys = (0,) * (e.life_years + 1)
    m.LandLease.land_area = 0
    m.execute()
    o = m.Outputs
    usd = lambda x: float(x)
    lcoe_real = usd(o.lcoe_real) / 100                     # cents/kWh -> USD/kWh
    # independent cross-check: capital recovery at the real WACC, level energy
    crf = wacc / (1 - (1 + wacc) ** -e.life_years)
    yearly_mwh = gen_mw.reshape(e.life_years, 8760).sum(axis=1)
    disc = (1 + wacc) ** -np.arange(1, e.life_years + 1)
    simple = (c["capex_usd"] * crf + c["opex_usd_year"] + np.dot(aug_cost, disc) * crf) / (np.dot(yearly_mwh, disc) * crf * 1000)
    return {
        "capex_usd": c["capex_usd"], "capex_lines_usd": c["capex_lines"], "opex_usd_year": c["opex_usd_year"],
        "opex_lines_usd": c["opex_lines"], "year1_export_mwh": float(yearly_mwh[0]),
        "lifetime_export_mwh": float(yearly_mwh.sum()),
        "lcoe_real_usd_per_kwh": lcoe_real, "lcoe_real_fils_per_kwh": lcoe_real * fx * 1000,
        "lcoe_crf_check_usd_per_kwh": float(simple),
        "npv_usd": usd(o.project_return_aftertax_npv), "irr_pct": usd(o.project_return_aftertax_irr),
        "ppa_price_usd_per_kwh": usd(o.ppa) / 100, "fx_kwd_per_usd": fx, "wacc_real": wacc,
    }

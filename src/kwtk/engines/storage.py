"""Storage dispatch, export limit and curtailment, hour by hour.

Inputs: the PV engine's hourly AC output (after availability), the export limit at
the point of interconnection, the storage blocks and the control strategy. Blocks
are pooled into one equivalent battery (powers and energies add; efficiency and
limits are the capacity-weighted means). DC-coupled blocks may also take the
energy their array's inverters clipped.

Strategies (controls.strategy), all without foresight beyond the day unless stated:
  export_limit  store what the export limit would curtail; discharge into the
                headroom under the limit, from `discharge_from_hour` (local, default 0)
  pv_firming    hold a committed export (`committed_mw` between `from_hour` and
                `to_hour`, local); charge surplus, discharge deficits; report
                hours delivered within `tolerance_pct`
  peak_shaving  discharge evenly over `window` (local hours [start, end)) on days
                the system load exceeds its `threshold_percentile` (default 90);
                charge from PV
  arbitrage     each day, charge the cheapest hours and discharge the dearest
                against a price series (perfect foresight within the day)
  reserve       as export_limit, but never below the energy that holds
                `reserve_mw` for `reserve_hours` (default 1)
  rule          a user function: parameters.function = "path.py:name", called as
                name(hour_index, state, inputs) -> MW (positive discharge)

Battery model: charge and discharge efficiencies are each the square root of the
AC round-trip efficiency; state of charge stays within soc_limits; auxiliary HVAC
load is the assumption's kW per MWh of capacity, drawn every hour from the plant
output (or the grid when there is none); output is scaled by storage availability.
Degradation over the life (calendar + cycle) is applied in economics from the
equivalent full cycles counted here."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..config.models import PlantConfig
from ..plant.resolve import Resolver


@dataclass
class Pool:
    power: float
    energy: float
    eta_c: float
    eta_d: float
    soc_min: float
    soc_max: float
    soc0: float
    aux_mw: float
    availability: float
    dc_arrays: set


def pool(cfg: PlantConfig, r: Resolver) -> Pool | None:
    if not cfg.storage:
        return None
    bl = cfg.storage.blocks
    E = sum(b.energy_mwh for b in bl)
    w = [b.energy_mwh / E for b in bl]
    rte = sum(wi * float(r(b.round_trip_efficiency, f"storage.blocks[{b.id}].round_trip_efficiency")) for wi, b in zip(w, bl))
    hvac = sum(float(r(b.thermal.hvac_load_kw_per_mwh, f"storage.blocks[{b.id}].thermal.hvac_load_kw_per_mwh")) * b.energy_mwh
               for b in bl) / 1000
    return Pool(power=sum(b.power_mw for b in bl), energy=E, eta_c=rte ** 0.5, eta_d=rte ** 0.5,
                soc_min=sum(wi * b.soc_limits.min for wi, b in zip(w, bl)),
                soc_max=sum(wi * b.soc_limits.max for wi, b in zip(w, bl)),
                soc0=sum(wi * b.initial_soc for wi, b in zip(w, bl)), aux_mw=hvac,
                availability=float(r(cfg.om.availability.storage, "om.availability.storage")),
                dc_arrays={b.dc_bus for b in bl if b.coupling == "dc"})


def _local_hour(idx: pd.DatetimeIndex) -> np.ndarray:
    return (idx + pd.Timedelta(hours=3)).hour.values


def dispatch(cfg: PlantConfig, pv: dict, r: Resolver, system_load: pd.Series | None = None,
             price: pd.Series | None = None) -> dict:
    p_pv = pv["p_ac"].values
    idx = pv["p_ac"].index
    n = len(p_pv)
    limit = cfg.site.grid_connection.export_limit_mw
    b = pool(cfg, r)
    par = cfg.controls.parameters
    strat = cfg.controls.strategy
    hour = _local_hour(idx)
    clipped_dc = np.zeros(n)
    if b and b.dc_arrays:
        for aid in b.dc_arrays:
            a = pv["arrays"][aid]
            clipped_dc += (a.pac_before_clip - a.pac).clip(lower=0).values

    # Target battery power per hour (+ discharge, - charge), before physical limits.
    target = np.zeros(n)
    if b:
        if strat in ("export_limit", "reserve"):
            start = int(par.get("discharge_from_hour", 0))
            target = np.where(p_pv > limit, -(p_pv - limit), np.where(hour >= start, limit - p_pv, 0.0))
        elif strat == "pv_firming":
            c = float(par["committed_mw"])
            on = (hour >= int(par.get("from_hour", 6))) & (hour < int(par.get("to_hour", 18)))
            commit = np.where(on, c, 0.0)
            target = commit - p_pv                      # deficit -> discharge, surplus -> charge
            target = np.where(on, target, -np.clip(p_pv, 0, None))
        elif strat == "peak_shaving":
            if system_load is None:
                raise ValueError("peak_shaving needs the system load (evaluation.system_context)")
            s, e = par.get("window", [12, 18])
            load = system_load.reindex(idx).values
            day = (idx + pd.Timedelta(hours=3)).normalize()
            thr = np.nanpercentile(pd.Series(load).groupby(day).max(), float(par.get("threshold_percentile", 90)))
            hot = pd.Series(load, index=idx).groupby(day).transform("max").values >= thr
            win = (hour >= s) & (hour < e)
            target = np.where(win & hot, b.power, -np.clip(p_pv, 0, None))
            target = np.where(win & ~hot, 0.0, target)
        elif strat == "arbitrage":
            if price is None:
                raise ValueError("arbitrage needs a price series (economics.revenue.tariff or system context)")
            pr = price.reindex(idx).values
            day = (idx + pd.Timedelta(hours=3)).normalize()
            k = max(1, int(round(b.energy * (b.soc_max - b.soc_min) / b.power)))
            for _, pos in pd.Series(np.arange(n), index=day).groupby(level=0):
                ii = pos.values
                order = ii[np.argsort(pr[ii])]
                target[order[:k]] = -b.power
                target[order[-k:]] = b.power
        elif strat == "rule":
            path, name = par["function"].split(":")
            spec = importlib.util.spec_from_file_location("kwtk_user_rule", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            fn = getattr(mod, name)
        else:
            raise ValueError(f"unknown strategy {strat}")

    soc = np.zeros(n + 1)
    batt = np.zeros(n)          # + discharge to AC, - charge from AC/DC
    ch_from_clip = np.zeros(n)
    if b:
        e_lo, e_hi = b.energy * b.soc_min, b.energy * b.soc_max
        floor = e_lo
        if strat == "reserve":
            floor = min(e_hi, e_lo + float(par["reserve_mw"]) * float(par.get("reserve_hours", 1)) / b.eta_d)
        soc[0] = b.energy * b.soc0
        P = b.power * b.availability
        for t in range(n):
            if strat == "rule":
                tg = float(fn(t, {"soc_mwh": soc[t], "energy_mwh": b.energy, "power_mw": b.power},
                              {"pv_mw": p_pv[t], "export_limit_mw": limit, "hour_local": hour[t]}))
            else:
                tg = target[t]
            if b.dc_arrays and clipped_dc[t] > 0:       # dc-coupled: clipped energy first
                c = min(clipped_dc[t], P, (e_hi - soc[t]) / b.eta_c)
                ch_from_clip[t] = c
                soc[t] += c * b.eta_c                    # stored within the hour
            if tg >= 0:
                d = min(tg, P, max(0.0, (soc[t] - floor)) * b.eta_d)
                batt[t] = d
                soc[t + 1] = soc[t] - d / b.eta_d
            else:
                room = P - ch_from_clip[t]
                c = min(-tg, max(room, 0), (e_hi - soc[t]) / b.eta_c, max(p_pv[t], 0))
                batt[t] = -c
                soc[t + 1] = soc[t] + c * b.eta_c
        aux = np.full(n, b.aux_mw)
    else:
        aux = np.zeros(n)

    gross = p_pv + batt - aux                            # at the POI, before the export limit
    export = np.clip(gross, None, limit)
    curtailed = np.clip(gross - limit, 0, None)
    imported = np.clip(-export, 0, None)
    export = np.clip(export, 0, None)
    res = pd.DataFrame({"pv_ac": p_pv, "battery": batt, "charge_from_clipping": ch_from_clip, "aux": aux,
                        "export": export, "import": imported, "curtailed": curtailed,
                        "soc_mwh": soc[1:]}, index=idx)
    out = {"hourly": res}
    if b:
        throughput = (res.battery.clip(lower=0).sum())
        years = len(set(idx.year))
        out["efc_per_year"] = float(throughput / (b.energy * (b.soc_max - b.soc_min)) / years)
    if strat == "pv_firming" and b:
        on = (hour >= int(par.get("from_hour", 6))) & (hour < int(par.get("to_hour", 18)))
        c = float(par["committed_mw"])
        tol = float(par.get("tolerance_pct", 5)) / 100
        ok = np.abs(export[on] - c) <= tol * c
        out["firming_hours_within_tolerance"] = float(ok.mean())
    if strat == "peak_shaving" and system_load is not None:
        L = system_load.reindex(idx)
        out["system_peak_before"] = float(L.max())
        out["system_peak_after"] = float((L - pd.Series(export, index=idx)).max())
        out["system_peak_after_pv_only"] = float((L - pd.Series(np.clip(p_pv, 0, limit), index=idx)).max())
    return out

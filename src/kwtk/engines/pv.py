"""PV yield and losses with pvlib, hour by hour, for each array of a plant.

Chain (each step's loss is recorded for the loss waterfall):
  1. Sun position at the hour's midpoint (ERA5 irradiance is an hourly mean).
  2. Orientation: fixed, or single-axis tracking with backtracking and wind stow.
  3. Plane-of-array irradiance, front and rear, with row-to-row shading and sky
     and ground view factors: pvlib infinite_sheds (Hay-Davies sky diffuse).
  4. Incidence-angle losses: pvlib physical IAM (glass, n = 1.526, De Soto 2006).
  5. Soiling: daily accumulation at the month's Kuwaiti soiling rate, reset by rain
     above a threshold and by the configured cleaning, capped at a maximum loss.
  6. Cell temperature: PVsyst model with the assumption file's U values.
  7. DC power: PVWatts (rated power x effective irradiance x temperature
     coefficient), then DC mismatch and wiring losses.
  8. Inverter: efficiency curve by load, AC limit with the ambient-temperature
     derate, so clipping is explicit.
  9. AC collection and transformer losses, then availability.

Export limits, storage and curtailment are applied afterwards (engines/storage.py).
Degradation over the plant's life is applied in economics, not here: this module
returns year-one performance for each weather year."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pvlib

from ..config.models import Array, PlantConfig
from ..plant.resolve import Resolver


def _module(a: Array, r: Resolver, path: str) -> dict:
    if a.module.inline:
        m = a.module.inline.model_dump()
        r.used[path] = {"value": "inline", "origin": "configuration", "source": m["source"]}
        return m
    return r(a.module.ref, path)


def _inverter(u, r: Resolver, path: str) -> dict:
    if u.inline:
        inv = u.inline.model_dump()
        r.used[path] = {"value": "inline", "origin": "configuration", "source": inv["source"]}
        return inv
    return r(u.ref, path)


def _orientation(a: Array, sp: pd.DataFrame, wx: pd.DataFrame, gcr: float) -> pd.DataFrame:
    m = a.mounting
    if m.type == "fixed":
        return pd.DataFrame({"surface_tilt": m.tilt_deg, "surface_azimuth": m.azimuth_deg}, index=sp.index)
    t = pvlib.tracking.singleaxis(sp.apparent_zenith, sp.azimuth, axis_tilt=0, axis_azimuth=m.axis_azimuth_deg,
                                  max_angle=m.max_angle_deg, backtrack=m.backtracking, gcr=gcr)
    tilt = t.surface_tilt.fillna(0.0)
    az = t.surface_azimuth.fillna(m.axis_azimuth_deg + 90)
    if m.stow:
        # ERA5 gives the hourly mean wind at 10 m; tracker stow is triggered by gusts,
        # so stow hours are underestimated (stated in the run report).
        stow = wx.wind_speed > m.stow.wind_speed_m_s
        tilt = tilt.where(~stow, abs(m.stow.angle_deg))
        az = az.where(~stow, m.axis_azimuth_deg + (90 if m.stow.angle_deg >= 0 else -90))
    else:
        stow = pd.Series(False, index=sp.index)
    return pd.DataFrame({"surface_tilt": tilt, "surface_azimuth": az % 360, "stow": stow})


def soiling_ratio(wx: pd.DataFrame, cfg: PlantConfig, r: Resolver) -> tuple[pd.Series, float]:
    """Fraction of light reaching the cells after soiling (1 = clean), daily steps,
    and the number of scheduled cleanings per year."""
    if cfg.site.soiling_source == "flat":
        return pd.Series(1 - cfg.om.soiling_flat_pct / 100, index=wx.index), 0.0
    rates = r.assumption("soiling.kuwait_rate_by_month", "site.soiling_source")      # % per day, Jan..Dec
    rain_mm = r.assumption("soiling.rain_cleaning_threshold", "soiling.rain_cleaning_threshold")
    cap = r.assumption("soiling.max_loss", "soiling.max_loss")                         # %
    c = cfg.om.cleaning
    eff = r(c.effectiveness, "om.cleaning.effectiveness") if c.method != "none" else 0.0
    local = wx.index + pd.Timedelta(hours=3)
    rain = wx.precip_mm.groupby(local.normalize()).sum()
    loss, out, n_clean = 0.0, {}, 0
    last_clean = rain.index[0]
    sched = c.schedule
    dates = {pd.Timestamp(d) for d in (sched.dates or [])}
    for day, mm in rain.items():
        loss = min(loss + rates[day.month - 1], cap)
        if mm >= rain_mm:
            loss = 0.0
        due = (sched.type == "interval" and (day - last_clean).days >= sched.interval_days) or \
              (sched.type == "threshold" and loss >= sched.soiling_loss_pct) or \
              (sched.type == "calendar" and day.replace(year=2000) in {d.replace(year=2000) for d in dates})
        if c.method != "none" and due:
            loss *= 1 - eff
            last_clean = day
            n_clean += 1
        out[day] = loss
    daily = pd.Series(out)
    years = len(set(local.year))
    return pd.Series(1 - daily.reindex(local.normalize()).values / 100, index=wx.index), n_clean / years


def array_dc(a: Array, cfg: PlantConfig, wx: pd.DataFrame, sp: pd.DataFrame, r: Resolver, soil: pd.Series) -> pd.DataFrame:
    p = f"pv.arrays[{a.id}]"
    mod = _module(a, r, f"{p}.module")
    width = float(r(a.layout.collector_width_m, f"{p}.layout.collector_width_m"))
    if a.layout.gcr is not None:
        gcr, pitch = a.layout.gcr, width / a.layout.gcr
    else:
        pitch, gcr = a.layout.pitch_m, width / a.layout.pitch_m
    albedo = r(cfg.site.terrain.albedo, "site.terrain.albedo")
    if isinstance(albedo, list):
        albedo = pd.Series(np.asarray(albedo)[wx.index.month - 1], index=wx.index)
    o = _orientation(a, sp, wx, gcr)
    bif = float(mod.get("bifaciality") or 0.0)
    height = a.layout.module_height_m + width / 2 * np.sin(np.radians(o.surface_tilt.mean()))   # axis height approx.
    irr = pvlib.bifacial.infinite_sheds.get_irradiance(
        surface_tilt=o.surface_tilt, surface_azimuth=o.surface_azimuth, solar_zenith=sp.apparent_zenith,
        solar_azimuth=sp.azimuth, gcr=gcr, height=height, pitch=pitch, ghi=wx.ghi, dhi=wx.dhi, dni=wx.dni,
        albedo=albedo, model="haydavies", dni_extra=pvlib.irradiance.get_extra_radiation(wx.index),
        iam_front=1.0, iam_back=1.0, bifaciality=bif, shade_factor=-0.02, transmission_factor=0)
    aoi = pvlib.irradiance.aoi(o.surface_tilt, o.surface_azimuth, sp.apparent_zenith, sp.azimuth)
    iam = pvlib.iam.physical(aoi).fillna(0)
    front_beam = irr["poa_front_direct"]
    front_eff = (irr["poa_front"] - front_beam * (1 - iam)) * soil
    back_eff = irr["poa_back"] * bif
    eff = front_eff + back_eff

    uc, uv = r.assumption("thermal.pvsyst_uc" if a.mounting.type == "fixed" else "thermal.pvsyst_uc_tracker",
                          f"{p}.thermal_model.u_c"), r.assumption("thermal.pvsyst_uv", f"{p}.thermal_model.u_v")
    eta = mod["stc_power_w"] / (1000 * mod["area_m2"]) if mod.get("area_m2") else 0.1
    tcell = pvlib.temperature.pvsyst_cell(irr["poa_front"] + back_eff, wx.temp_air, wx.wind_speed,
                                          u_c=uc, u_v=uv, module_efficiency=eta)
    gamma = mod["temp_coeff_pmax_pct_per_c"] / 100
    pdc0 = a.dc_capacity_mwp
    pdc_stc_irr = pdc0 * eff / 1000
    pdc = pvlib.pvsystem.pvwatts_dc(eff, tcell, pdc0, gamma)
    mism = r.assumption("losses.dc_mismatch_pct", f"{p}.losses.dc_mismatch_pct") / 100
    wire = r.assumption("losses.dc_wiring_pct", f"{p}.losses.dc_wiring_pct") / 100
    pdc_net = pdc * (1 - mism) * (1 - wire)
    return pd.DataFrame({
        "poa_front": irr["poa_front"], "poa_back": irr["poa_back"], "poa_front_after_iam": irr["poa_front"] - front_beam * (1 - iam),
        "poa_effective": eff, "t_cell": tcell, "pdc_at_25c": pdc_stc_irr, "pdc": pdc, "pdc_net": pdc_net,
        "surface_tilt": o.surface_tilt, "stow": o.get("stow", False)})


def _inverter_ac(pdc: pd.Series, units: list, wx: pd.DataFrame, cfg: PlantConfig, r: Resolver, aid: str) -> pd.DataFrame:
    rating = 0.0
    curve = None
    derate = None
    for i, u in enumerate(units):
        inv = _inverter(u, r, f"inverters.units[{aid}#{i}]")
        rating += inv["ac_rating_kva"] * u.count / 1000          # MVA ~ MW at unity power factor
        curve = np.asarray(inv["efficiency_curve"])
        derate = inv.get("temperature_derate")
    load = (pdc / rating).clip(lower=0)
    eff = np.interp(load, curve[:, 0], curve[:, 1], left=curve[0, 1], right=curve[-1, 1])
    pac_raw = pdc * eff
    limit = pd.Series(rating, index=pdc.index)
    if derate:
        d = np.asarray(derate)
        limit = rating * pd.Series(np.interp(wx.temp_air, d[:, 0], d[:, 1]), index=pdc.index)
    pac = np.minimum(pac_raw, limit)
    return pd.DataFrame({"pac_before_clip": pac_raw, "pac": pac, "ac_limit": limit, "inverter_rating": rating})


def simulate(cfg: PlantConfig, wx: pd.DataFrame, r: Resolver) -> dict:
    """Hourly PV output at the inverter terminals and after AC losses and availability
    (MW, positive), plus per-array detail and the loss waterfall (MWh per year)."""
    la, lo = cfg.site.location.lat, cfg.site.location.lon
    sp = pvlib.solarposition.get_solarposition(wx.index, la, lo, pressure=wx.pressure, temperature=wx.temp_air)
    soil, cleanings = soiling_ratio(wx, cfg, r)
    arrays, ac = {}, []
    wf = {}
    for a in cfg.pv.arrays:
        dc = array_dc(a, cfg, wx, sp, r, soil)
        units = [u for u in cfg.inverters.units if u.array == a.id]
        inv = _inverter_ac(dc.pdc_net, units, wx, cfg, r, a.id)
        arrays[a.id] = pd.concat([dc, inv], axis=1)
        ac.append(inv.pac)
    pac = sum(ac)
    coll = cfg.inverters.ac_collection_losses_pct / 100
    trafo = cfg.inverters.transformer_losses_pct / 100
    avail_plant = float(r(cfg.om.availability.plant, "om.availability.plant"))
    avail_inv = float(r(cfg.om.availability.inverter, "om.availability.inverter"))
    p_poi = pac * (1 - coll) * (1 - trafo)
    p_avail = p_poi * avail_plant * avail_inv

    # Loss waterfall, MWh per weather year (energy at each stage, summed over arrays)
    total = lambda col: sum(arrays[k][col] for k in arrays)
    dc_cap = sum(a.dc_capacity_mwp for a in cfg.pv.arrays)
    ghi_mwh = wx.ghi / 1000 * dc_cap                                # "nameplate x GHI" reference
    stages = {
        "nameplate_x_ghi": ghi_mwh,
        "front_poa": sum(arrays[a.id].poa_front / 1000 * a.dc_capacity_mwp for a in cfg.pv.arrays),
        "after_iam": sum(arrays[a.id].poa_front_after_iam / 1000 * a.dc_capacity_mwp for a in cfg.pv.arrays),
        "after_soiling": sum(arrays[a.id].poa_front_after_iam * soil / 1000 * a.dc_capacity_mwp for a in cfg.pv.arrays),
        "after_bifacial_gain": total("pdc_at_25c"),
        "after_temperature": total("pdc"),
        "after_dc_losses": total("pdc_net"),
        "after_inverter_efficiency": total("pac_before_clip"),
        "after_clipping": pac,
        "after_ac_losses": p_poi,
        "after_availability": p_avail,
    }
    yearly = pd.DataFrame({k: v.groupby(v.index.year).sum() for k, v in stages.items()})
    return {"p_ac": p_avail, "p_ac_available_before_availability": p_poi, "arrays": arrays, "soiling_ratio": soil,
            "solar_position": sp, "waterfall_mwh": yearly, "cleanings_per_year": cleanings, "dc_capacity_mwp": dc_cap,
            "ac_rating_mw": sum(arrays[k].inverter_rating.iloc[0] for k in arrays)}

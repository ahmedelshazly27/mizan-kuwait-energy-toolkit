"""Evaluate a plant configuration: validate, resolve, simulate, cost, report.

The result is a dictionary that serialises to JSON, plus hourly series. Every
input the run used is listed with its origin (configuration, assumption with its
status and source, or library entry), every default and every warning, so a
reviewer sees exactly what the numbers rest on."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config.validate import validate
from ..engines import economics, pv as pv_engine, storage
from ..inputs import era5
from .resolve import Resolver

NOTES = [
    "Weather: ERA5 reanalysis at the nearest 0.25-degree cell (hourly means). ERA5 uses an aerosol "
    "climatology, so dust events are smoothed; irradiance on dusty days may be overstated.",
    "Tracker wind stow uses ERA5's hourly mean 10 m wind; stow is triggered by gusts in practice, "
    "so stow hours are understated.",
]


def evaluate(path: Path | str, system_load: pd.Series | None = None, price: pd.Series | None = None,
             resolver: Resolver | None = None, system_hourly: bool = False) -> dict:
    rep = validate(path)
    if not rep.ok:
        raise ValueError("configuration is not valid:\n" + rep.text())
    cfg = rep.config
    r = resolver or Resolver()
    years = cfg.evaluation.years
    wx = era5.site_weather(cfg.site.location.lat, cfg.site.location.lon, years)
    pv = pv_engine.simulate(cfg, wx, r) if cfg.pv else None
    if pv is None:
        pv = {"p_ac": pd.Series(0.0, index=wx.index), "arrays": {}, "cleanings_per_year": 0.0}
    if cfg.controls.strategy == "peak_shaving" and system_load is None:
        from ..inputs import demand
        system_load = demand.load_series().tz_localize("Asia/Kuwait").tz_convert("UTC")
        system_load.index = system_load.index + pd.Timedelta(minutes=30)
    disp = storage.dispatch(cfg, pv, r, system_load=system_load, price=price)
    econ = economics.run(cfg, pv if cfg.pv else None, disp, r, pv.get("cleanings_per_year", 0.0))
    grid = None
    if cfg.evaluation.system_context:
        import contextlib
        import io
        import logging
        from ..engines import system
        yrs = [y for y in years if 2019 <= y <= 2023] or [2023]
        exp = disp["hourly"].export.copy()
        exp.index = exp.index.tz_convert("Asia/Kuwait").tz_localize(None).floor("h")
        logging.getLogger("linopy").setLevel(logging.ERROR)
        logging.getLogger("pypsa").setLevel(logging.ERROR)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            grid = system.interaction(exp, cfg.site.location.lat, cfg.site.location.lon, max(yrs),
                                      float(r.assumption("fx.kwd_per_usd", "system_context.fx")), hourly=system_hourly)
        system_hourly_out = grid.pop("hourly", None)
    h = disp["hourly"]
    by_year = h.groupby(h.index.year).sum()
    energy = pd.DataFrame({
        "pv_ac_mwh": by_year.pv_ac, "export_mwh": by_year.export, "curtailed_mwh": by_year.curtailed,
        "battery_discharge_mwh": h.battery.clip(lower=0).groupby(h.index.year).sum(),
        "battery_charge_mwh": (-h.battery.clip(upper=0)).groupby(h.index.year).sum() + by_year.charge_from_clipping,
        "aux_mwh": by_year.aux, "import_mwh": by_year["import"]})
    if cfg.pv:
        a = pv["arrays"]
        energy["inverter_clipping_mwh"] = sum((a[k].pac_before_clip - a[k].pac).groupby(h.index.year).sum() for k in a)
        energy["capacity_factor_ac"] = energy.export_mwh / (pv["ac_rating_mw"] * h.groupby(h.index.year).size())
        energy["specific_yield_kwh_per_kwp"] = energy.export_mwh / pv["dc_capacity_mwp"]
    result = {
        "id": cfg.id, "name": cfg.name, "status": cfg.status, "weather_cell": wx.attrs["cell"],
        "years": years, "energy_by_year": energy.round(1).reset_index(names="year").to_dict("records"),
        "waterfall_mwh": pv["waterfall_mwh"].round(1).reset_index(names="year").to_dict("records") if cfg.pv else [],
        "mean_soiling_loss_pct": float((1 - pv["soiling_ratio"]).mean() * 100) if cfg.pv else None,
        "cleanings_per_year": pv.get("cleanings_per_year"),
        "storage": {k: v for k, v in disp.items() if k != "hourly"},
        "system_context": grid,
        "economics": econ, "inputs": r.used, "warnings": rep.range, "defaults": rep.defaults, "notes": NOTES,
        "unverified_inputs": sorted({v["origin"] for v in r.used.values() if v.get("status") == "unverified"}),
    }
    out = {"result": result, "hourly": h, "pv": pv, "weather": wx, "config": cfg}
    if cfg.evaluation.system_context and system_hourly:
        out["system_hourly"] = system_hourly_out
    return out

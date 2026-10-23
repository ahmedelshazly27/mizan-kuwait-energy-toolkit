"""Write web/toolkit.json, the data behind mizan-energy.com/research/kuwait-energy-toolkit.
Run after evaluating the examples: uv run python scripts/web_data.py
Every number on the page comes from this file, which comes from the toolkit's outputs."""

import json
from pathlib import Path

import pandas as pd
import yaml

from kwtk.engines import system, water
from kwtk.inputs import demand
from kwtk.plant.evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ["shagaya-pv1-approximation", "shagaya-scale-pv-tracker", "shagaya-scale-pv-storage-export-limit",
            "shagaya-scale-pv-storage-peak-shaving", "shagaya-scale-pv-ro"]


def r(x, d=1):
    return None if x is None or (isinstance(x, float) and x != x) else round(float(x), d)


YEAR = 2023


def _local(series: pd.Series) -> pd.Series:
    """UTC hour-midpoint series -> Kuwait local hours of YEAR (8760 values)."""
    x = series.copy()
    x.index = x.index.tz_convert("Asia/Kuwait").tz_localize(None).floor("h")
    x = x[x.index.year == YEAR]
    return x.reindex(pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31 23:00", freq="h")).fillna(0)


def _ints(x, scale=1):
    return [int(round(v * scale)) for v in x]


def components(run) -> list:
    """The plant's parts, for the diagram: what each is, from the configuration."""
    cfg, lib = run["config"], None
    from kwtk.config.validate import load_library
    lib = load_library()
    out = []
    for a in (cfg.pv.arrays if cfg.pv else []):
        mod = a.module.inline.model_dump() if a.module.inline else lib[a.module.ref.split(":", 1)[1]]
        n_mod = a.layout.modules_per_string * a.layout.strings
        out.append({"kind": "array", "id": a.id, "mwp": a.dc_capacity_mwp, "modules": n_mod,
                    "module": (a.module.ref or "inline").replace("library:", ""), "module_w": mod["stc_power_w"],
                    "technology": mod["technology"], "mounting": a.mounting.type,
                    "tilt": a.mounting.tilt_deg, "max_angle": a.mounting.max_angle_deg, "gcr": a.layout.gcr})
    if cfg.inverters:
        for u in cfg.inverters.units:
            inv = u.inline.model_dump() if u.inline else lib[u.ref.split(":", 1)[1]]
            out.append({"kind": "inverter", "array": u.array, "count": u.count, "model": (u.ref or "inline").replace("library:", ""),
                        "mw": r(inv["ac_rating_kva"] * u.count / 1000, 1), "dc_ac": cfg.inverters.dc_ac_ratio})
    for b in (cfg.storage.blocks if cfg.storage else []):
        out.append({"kind": "battery", "id": b.id, "mw": b.power_mw, "mwh": b.energy_mwh, "chemistry": b.chemistry,
                    "coupling": b.coupling, "strategy": cfg.controls.strategy})
    for d in (cfg.desalination.blocks if cfg.desalination else []):
        out.append({"kind": "ro", "id": d.id, "m3_day": d.capacity_m3_per_day, "store_m3": d.water_storage_m3})
    g = cfg.site.grid_connection
    out.append({"kind": "connection", "kv": g.voltage_kv, "export_mw": g.export_limit_mw, "import_mw": g.import_limit_mw})
    return out


def visuals(runs):
    import numpy as np
    from kwtk.engines import system
    wdir = ROOT / "web" / "plants"
    wdir.mkdir(parents=True, exist_ok=True)
    base_written = False
    st = system.station_table(YEAR)
    z = system.zones()
    for k, run in runs.items():
        h, pv = run["hourly"], run["pv"]
        arrays = pv["arrays"]
        dc = sum(a.pdc_net for a in arrays.values()) if arrays else h.pv_ac * 0
        ac_raw = sum(a.pac_before_clip for a in arrays.values()) if arrays else h.pv_ac * 0
        ac = sum(a.pac for a in arrays.values()) if arrays else h.pv_ac * 0
        poa = (sum(a.poa_front * run["config"].pv.arrays[i].dc_capacity_mwp for i, a in enumerate(arrays.values()))
               / sum(x.dc_capacity_mwp for x in run["config"].pv.arrays)) if arrays else h.pv_ac * 0
        tcell = list(arrays.values())[0].t_cell if arrays else h.pv_ac * 0
        wx = run["weather"]
        b = run["config"].storage
        emax = sum(x.energy_mwh for x in b.blocks) if b else 0
        series = {
            "poa_w_m2": _ints(_local(poa)), "t_air_c": _ints(_local(wx.temp_air), 10), "t_cell_c": _ints(_local(tcell), 10),
            "dc_mw": _ints(_local(dc)), "ac_mw": _ints(_local(ac)), "clipped_mw": _ints(_local(ac_raw - ac)),
            "pv_mw": _ints(_local(h.pv_ac)), "battery_mw": _ints(_local(h.battery)),
            "soc_pct": _ints(_local(h.soc_mwh / emax * 100)) if emax else None,
            "aux_mw": _ints(_local(h.aux), 10), "desal_mw": _ints(_local(h.desal)) if "desal" in h else None,
            "export_mw": _ints(_local(h.export)), "curtailed_mw": _ints(_local(h.curtailed)),
            "import_mw": _ints(_local(h["import"])),
        }
        soil = pv.get("soiling_ratio")
        daily = None
        if soil is not None:
            sl = _local(soil).groupby(lambda t: t.dayofyear).mean()
            rain = _local(wx.precip_mm).groupby(lambda t: t.dayofyear).sum()
            daily = {"soiling_pct": [r((1 - v) * 100, 2) for v in sl.values], "rain_mm": [r(v, 1) for v in rain.values]}
        out = {"id": k, "year": YEAR, "components": components(run), "hourly": series, "daily": daily,
               "annual_gwh": {key: r(v / 1e3) for key, v in pd.DataFrame(run["result"]["energy_by_year"]).mean(numeric_only=True).items() if key.endswith("_mwh")},
               "waterfall_gwh": {key: r(v / 1e3) for key, v in pd.DataFrame(run["result"]["waterfall_mwh"]).mean(numeric_only=True).items() if key != "year"}}
        sh = run.get("system_hourly")
        if sh is not None:
            loc = lambda df: df.set_axis(pd.DatetimeIndex(df.index), axis=0)
            w = loc(sh["with"])
            out["system_with"] = {c: _ints(w[c].values) for c in w.columns}
            out["flows_with"] = {c: _ints(loc(sh["flows_with"])[c].values) for c in sh["flows_with"].columns}
            if not base_written:
                wo = loc(sh["without"])
                base = {"year": YEAR, "stations": [c for c in wo.columns],
                        "load_mw": _ints(sh["load"].values), "without": {c: _ints(wo[c].values) for c in wo.columns},
                        "floor_mw": {c: r(st.loc[c, "min_monthly_avg_mw"], 0) for c in wo.columns},
                        "kd_per_mwh": {c: r(st.loc[c, "kd_per_mwh"], 2) for c in wo.columns},
                        "zone": {c: z["stations"][c] for c in wo.columns}}
                (ROOT / "web" / "system.json").write_text(json.dumps(base))
                base_written = True
        (wdir / f"{k}.json").write_text(json.dumps(out, default=float))
    # map: annual GHI per ERA5 cell, stations, zones, interfaces
    from kwtk.inputs import era5
    cells = []
    for la, lo in era5.CELLS:
        w = era5.site_weather(la, lo, [2019, 2020, 2021, 2022, 2023])
        cells.append({"lat": la, "lon": lo, "ghi": r(w.ghi.sum() / 1000 / 5, 0)})
    fleet = __import__("kwtk.inputs.dataset", fromlist=["fleet"]).fleet("mew-yb-2023")
    caps = fleet.groupby("plant_id").capacity_mw.sum()
    stations = [{"id": s_, "lat": c[0], "lon": c[1], "mw": r(caps.get(s_), 0), "zone": z["stations"][s_]}
                for s_, c in z["station_coords"].items()]
    (ROOT / "web" / "map.json").write_text(json.dumps({"cells": cells, "stations": stations, "interfaces": z["interfaces"],
                                                       "zone_of_governorate": {"KW-JA": "north", "KW-KU": "central", "KW-HA": "central",
                                                                               "KW-FA": "central", "KW-AH": "south", "KW-MU": "south"}}))


def main():
    runs = {k: evaluate(ROOT / "configs" / "examples" / f"{k}.yaml", system_hourly=True) for k in EXAMPLES}
    visuals(runs)
    ex = []
    for k, run in runs.items():
        res = run["result"]
        e = pd.DataFrame(res["energy_by_year"]).mean(numeric_only=True)
        sc = res.get("system_context") or {}
        cfg = yaml.safe_load((ROOT / "configs" / "examples" / f"{k}.yaml").read_text())
        ex.append({
            "id": k, "name": res["name"], "years": res["years"],
            "dc_mwp": r(run["pv"].get("dc_capacity_mwp"), 2), "ac_mw": r(run["pv"].get("ac_rating_mw"), 1),
            "export_limit_mw": cfg["site"]["grid_connection"]["export_limit_mw"],
            "storage": cfg.get("storage", {}).get("blocks", [{}])[0].get("energy_mwh") if cfg.get("storage") else None,
            "strategy": cfg["controls"]["strategy"],
            "export_gwh": r(e.export_mwh / 1e3), "specific_yield": r(e.get("specific_yield_kwh_per_kwp"), 0),
            "cf_ac": r(e.get("capacity_factor_ac"), 3), "clipping_gwh": r(e.get("inverter_clipping_mwh", 0) / 1e3, 2),
            "curtailed_gwh": r(e.curtailed_mwh / 1e3, 2), "battery_gwh": r(e.battery_discharge_mwh / 1e3, 1),
            "soiling_pct": r(res["mean_soiling_loss_pct"], 2), "lcoe_fils": r(res["economics"]["lcoe_real_fils_per_kwh"], 1),
            "lcoe_usd_c": r(res["economics"]["lcoe_real_usd_per_kwh"] * 100, 2),
            "capex_musd": r(res["economics"]["capex_usd"] / 1e6, 1),
            "fuel_avoided_kd_mwh": r(sc.get("fuel_cost_avoided_kd_per_mwh")), "system_curtailed_gwh": r((sc.get("system_curtailment_mwh") or 0) / 1e3),
            "peak_after": r(res["storage"].get("system_peak_after"), 0), "peak_after_pv": r(res["storage"].get("system_peak_after_pv_only"), 0),
            "water": res["storage"].get("water"), "unverified": [u.split(":", 1)[1] for u in res["unverified_inputs"]],
        })
    track = runs["shagaya-scale-pv-tracker"]
    wf = pd.DataFrame(track["result"]["waterfall_mwh"]).set_index("year").mean()
    meta = json.loads((ROOT / "inputs" / "demand" / "kuwait-gross-load-reconstructed.json").read_text())
    curves = demand.peak_curves()
    L = demand.load_series()
    day = {}
    for sid, c in curves.groupby("source_id"):
        dt = c.t.iloc[0].date()
        m = L[str(dt)]
        day[sid] = {"date": str(dt), "printed": [[r(t.hour + t.minute / 60, 2), r(v, 0)] for t, v in zip(c.t, c.mw)][:-1],
                    "model": [[int(t.hour), r(v, 0)] for t, v in m.items()]}
    st = system.station_table(2023)
    sc = track["result"]["system_context"]
    assumptions = yaml.safe_load((ROOT / "inputs" / "assumptions.yaml").read_text())["assumptions"]
    manifest = yaml.safe_load((ROOT / "inputs" / "dataset" / "MANIFEST.yaml").read_text())
    out = {
        "version": "0.1.0", "dataset_commit": manifest["commit"][:12],
        "examples": ex,
        "waterfall": [{"k": k, "gwh": r(v / 1e3)} for k, v in wf.items() if k != "nameplate_x_ghi"],
        "demand": {"label": meta["label"], "validation": meta["validation_peak_days"], "fit": meta["fit"]["rmse_relative"],
                   "stretch": meta["peak_stretch_k"], "days": day,
                   "annual": [{"y": int(y), "twh": r(g.sum() / 1e6, 2), "peak": r(g.max(), 0)} for y, g in L.groupby(L.index.year) if len(g) > 8000]},
        "stations": [{"id": i, "kd_per_mwh": r(v.kd_per_mwh, 2), "mmbtu_per_mwh": r(v.mmbtu_per_mwh, 2),
                      "floor_mw": r(v.min_monthly_avg_mw, 0), "gen_gwh": r(v.gen_mwh / 1e3, 0)} for i, v in st.sort_values("kd_per_mwh").iterrows()],
        "displaced": [{"id": k, "gwh": r(v / 1e3, 0)} for k, v in sorted(sc["displaced_mwh_by_station"].items(), key=lambda x: -x[1]) if v > 1],
        "system": {k: sc[k] for k in ("year", "zone", "fuel_avoided_bbtu", "fuel_cost_avoided_kd", "fuel_cost_avoided_kd_per_mwh",
                                      "system_curtailment_mwh", "plant_offered_mwh", "max_interface_loading")},
        "zones": {k: r(v, 4) for k, v in system.zone_shares().items()},
        "water_profile": {int(k): r(v, 3) for k, v in water.seasonal_profile().items()},
        "assumptions": [{"key": k, "value": v.get("value") if not isinstance(v.get("value"), list) else f"{v['value'][0]} (every month)",
                         "unit": v.get("unit"), "status": v.get("status"), "source": v.get("source")} for k, v in assumptions.items()],
        "config_example": (ROOT / "configs" / "examples" / "shagaya-scale-pv-tracker.yaml").read_text(),
    }
    (ROOT / "web").mkdir(exist_ok=True)
    (ROOT / "web" / "toolkit.json").write_text(json.dumps(out, default=float))
    print("web/toolkit.json", (ROOT / "web" / "toolkit.json").stat().st_size, "bytes")


if __name__ == "__main__":
    main()

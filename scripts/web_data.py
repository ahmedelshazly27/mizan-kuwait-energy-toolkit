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


def main():
    runs = {k: evaluate(ROOT / "configs" / "examples" / f"{k}.yaml") for k in EXAMPLES}
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

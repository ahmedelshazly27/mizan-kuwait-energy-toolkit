"""Write an evaluation to results/<id>/ and compare evaluations side by side."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def _plain(x):
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    return x


def write(run: dict, out: Path | None = None) -> Path:
    r = run["result"]
    d = out or ROOT / "results" / r["id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "result.json").write_text(json.dumps(_plain(r), indent=2, default=str))
    run["hourly"].round(3).to_csv(d / "hourly.csv.gz")
    return d


ROWS = [  # label, getter
    ("Export, MWh/yr (mean)", lambda r: np.mean([y["export_mwh"] for y in r["energy_by_year"]])),
    ("Specific yield, kWh/kWp", lambda r: np.mean([y.get("specific_yield_kwh_per_kwp", np.nan) for y in r["energy_by_year"]])),
    ("AC capacity factor", lambda r: np.mean([y.get("capacity_factor_ac", np.nan) for y in r["energy_by_year"]])),
    ("Inverter clipping, MWh/yr", lambda r: np.mean([y.get("inverter_clipping_mwh", 0) for y in r["energy_by_year"]])),
    ("Curtailed at POI, MWh/yr", lambda r: np.mean([y["curtailed_mwh"] for y in r["energy_by_year"]])),
    ("Battery discharge, MWh/yr", lambda r: np.mean([y["battery_discharge_mwh"] for y in r["energy_by_year"]])),
    ("Mean soiling loss, %", lambda r: r["mean_soiling_loss_pct"]),
    ("Cleanings per year", lambda r: r["cleanings_per_year"]),
    ("Capex, million USD", lambda r: r["economics"]["capex_usd"] / 1e6),
    ("LCOE real, fils/kWh", lambda r: r["economics"]["lcoe_real_fils_per_kwh"]),
    ("LCOE real, USD/kWh", lambda r: r["economics"]["lcoe_real_usd_per_kwh"]),
    ("Break-even flat nominal PPA, fils/kWh", lambda r: r["economics"]["breakeven_ppa_fils_per_kwh"]),
    ("Project NPV, million USD", lambda r: r["economics"]["npv_usd"] / 1e6),
    ("Project IRR, %", lambda r: r["economics"]["irr_pct"]),
    ("System peak after, MW", lambda r: r["storage"].get("system_peak_after", np.nan)),
    ("System peak after PV alone, MW", lambda r: r["storage"].get("system_peak_after_pv_only", np.nan)),
    ("Assumptions used", lambda r: sum(1 for v in r["inputs"].values() if str(v.get("origin", "")).startswith("assumption:"))),
    ("Warnings", lambda r: len(r["warnings"])),
]


def compare(results: list[dict]) -> pd.DataFrame:
    return pd.DataFrame({r["id"]: {label: f(r) for label, f in ROWS} for r in results})

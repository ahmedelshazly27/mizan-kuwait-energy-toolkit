"""Plant-level reverse osmosis coupled to the plant's power, hour by hour.

An RO block sits behind the plant's connection. Each day it must deliver that day's
water demand from production plus product-water storage. Demand is the block's
capacity scaled by Kuwait's measured monthly seasonality of distilled-water
production (MEW Water yearbooks: each month's national net production over the
year's highest month; profile `mew-water-seasonal`). The block:
  - runs at least min_load_fraction of capacity whenever it is on (it stays on),
  - follows the plant's surplus power (after storage) up to capacity, within its
    ramp limit, filling the water store,
  - draws from the grid (up to the import limit) when PV cannot cover its minimum
    or when the store would otherwise not meet the day's demand.
Electricity per m3 is the block's specific energy (default: Kuwait's measured RO
plants, inputs/assumptions.yaml ro.specific_energy_seawater)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..config.models import PlantConfig
from ..inputs import dataset
from ..plant.resolve import Resolver


def seasonal_profile() -> pd.Series:
    """Month (1-12) -> production relative to the year's highest month, mean over the
    water yearbook editions in the dataset."""
    o = dataset.observations()
    w = o[(o.table_no == "distilled-monthly") & (o.level == "national") & (o.variable == "water_production_net")].copy()
    w["v"] = pd.to_numeric(w.canonical_value)
    w["y"], w["m"] = w.period_start.str[:4], w.period_start.str[5:7].astype(int)
    rel = w.v / w.groupby("y").v.transform("max")
    return rel.groupby(w.m).mean()


def run(cfg: PlantConfig, surplus_mw: pd.Series, r: Resolver) -> dict:
    """surplus_mw: plant output available after storage, before export (MW, UTC index)."""
    prof = seasonal_profile()
    local = surplus_mw.index + pd.Timedelta(hours=3)
    imp_lim = cfg.site.grid_connection.import_limit_mw
    out = {}
    load_total = pd.Series(0.0, index=surplus_mw.index)
    for b in cfg.desalination.blocks:
        sec = float(r(b.specific_energy_kwh_per_m3, f"desalination.blocks[{b.id}].specific_energy_kwh_per_m3"))
        cap_h = b.capacity_m3_per_day / 24                        # m3 per hour at full load
        p_max = cap_h * sec / 1000                                # MW
        p_min = p_max * b.min_load_fraction
        ramp = p_max * b.ramp_pct_per_hour / 100
        demand_day = b.capacity_m3_per_day * prof.reindex(local.month).values    # m3/day, per hour's day
        store_max = b.water_storage_m3
        store = store_max / 2
        p_prev = p_min
        days = local.normalize()
        power = np.zeros(len(surplus_mw))
        shortfall = 0.0
        avail = surplus_mw.values.copy()
        for d, pos in pd.Series(np.arange(len(days)), index=days).groupby(level=0):
            ii = pos.values
            need = float(demand_day[ii[0]])
            produced = 0.0
            for j, t in enumerate(ii):
                left_h = len(ii) - j
                # power that keeps the day feasible if the rest of the day runs at full load
                must = max(p_min, (need - produced - store - (left_h - 1) * cap_h) / 1 * sec / 1000)
                want = max(must, min(p_max, avail[t])) if store < store_max else must
                p = float(np.clip(want, max(p_min, p_prev - ramp), min(p_max, p_prev + ramp)))
                power[t] = p
                produced += p * 1000 / sec
                p_prev = p
            store = store + produced - need
            if store < 0:
                shortfall += -store
                store = 0.0
            store = min(store, store_max)
        load_total = load_total + power
        out[b.id] = {"water_m3_per_year": float(power.sum() * 1000 / sec) / len(set(local.year)),
                     "energy_mwh_per_year": float(power.sum()) / len(set(local.year)),
                     "unmet_water_m3_per_year": shortfall / len(set(local.year))}
        avail = np.clip(avail - power, 0, None)
    from_plant = np.minimum(load_total.values, np.clip(surplus_mw.values, 0, None))
    from_grid = load_total.values - from_plant
    if (from_grid > imp_lim + 1e-6).any():
        out["import_limit_exceeded_hours"] = int((from_grid > imp_lim + 1e-6).sum())
    out["hourly_load_mw"] = load_total
    out["from_grid_mwh_per_year"] = float(from_grid.sum()) / len(set(local.year))
    return out

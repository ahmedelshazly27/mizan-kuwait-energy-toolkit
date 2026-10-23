"""System context: what a plant does to Kuwait's dispatch, fuel and costs.

A zonal PyPSA model (three zones, inputs/zones.yaml) is solved hour by hour for one
year with HiGHS, twice: without the plant and with it. The difference is the plant's
grid interaction: fuel energy and fuel cost avoided, which stations it displaces, the
system's net peak, inter-zonal flows and system-level curtailment of the plant.

Everything here is measured Kuwaiti data from the dataset, except where stated:
  load        the hourly reconstruction (inputs/demand/, labelled a reconstruction),
              split across zones by the supply-area loads at the 2023 peak (D7)
  fleet       every unit in the MEW 2023 yearbook's station pages, by station and
              technology
  cost        each station's 2023 fuel cost (KD) over its 2023 gross generation:
              an average cost per MWh, used as the marginal cost (D8). It includes
              the fuel that makes steam for distillation at cogeneration stations
  fuel        each station's 2023 fuel energy over its gross generation (MMBtu/MWh),
              to count fuel avoided; same caveat
  water       power-water coupling (D9): a station with thermal distillation must
              generate at least its lowest monthly average output in 2023 every hour,
              the floor it held while producing water; RO plants are part of the load
  imports     the GCC interconnector is not modelled (system load includes the
              interchange, which is small and not published hourly)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from ..inputs import dataset, demand

ROOT = Path(__file__).resolve().parents[3]
DESAL = {"shuwaikh", "shuaiba-north", "shuaiba-south", "doha-east", "doha-west", "zour-south", "sabiya", "zour-north"}


def zones() -> dict:
    return yaml.safe_load((ROOT / "inputs" / "zones.yaml").read_text())


def zone_shares() -> pd.Series:
    z = zones()
    o = dataset.observations()
    r = o[(o.table_no == "regional-peak") & (o.period_start == "2023-08-02")].copy()
    r["mw"] = pd.to_numeric(r.value).fillna(0)
    r["zone"] = r.row_label.astype(int).map(lambda i: z["area_rows"][i]["zone"])
    by = r.groupby("zone").mw.sum()
    fleet = dataset.fleet("mew-yb-2023")
    cap = fleet.groupby(fleet.plant_id.map(z["stations"])).capacity_mw.sum()
    by = by.drop("stations").add(by["stations"] * cap / cap.sum(), fill_value=0)
    return by / by.sum()


def station_table(year: int = 2023) -> pd.DataFrame:
    o = dataset.observations()
    y = str(year)
    f = o[(o.table_no == "station-fuel-history") & (o.level == "plant") & (o.period_start.str[:4] == y)]
    f = f.assign(v=pd.to_numeric(f.value)).pivot_table(index="plant_id", columns="variable", values="v")
    g = o[(o.source_id == "mew-yb-2023") & (o.table_no == "generation-history") & (o.level == "plant")
          & (o.variable == "generation_gross") & (o.period_start.str[:4] == y)]
    f["gen_mwh"] = pd.to_numeric(g.groupby("plant_id").canonical_value.last())
    m = o[(o.source_id == "mew-yb-2023") & (o.variable == "generation_gross") & (o.level == "plant")
          & (o.frequency == "monthly") & (o.period_start.str[:4] == y)].copy()
    m["mwh"] = pd.to_numeric(m.canonical_value)
    m["hours"] = pd.to_datetime(m.period_start).dt.days_in_month * 24
    floor = (m.groupby(["plant_id", "period_start"]).apply(lambda d: d.mwh.sum() / d.hours.iloc[0], include_groups=False)
             .groupby("plant_id").min())
    f["min_monthly_avg_mw"] = floor
    f["kd_per_mwh"] = f.fuel_cost / f.gen_mwh
    f["mmbtu_per_mwh"] = f.fuel_energy * 1000 / f.gen_mwh
    return f.dropna(subset=["gen_mwh"])


def build_network(year: int, plant: pd.Series | None, plant_zone: str | None, fx: float):
    import pypsa
    z = zones()
    load = demand.load_series()
    load = load[load.index.year == year]
    snaps = load.index
    n = pypsa.Network()
    n.set_snapshots(snaps)
    shares = zone_shares()
    for zn in z["zones"]:
        n.add("Bus", zn, carrier="AC")
        n.add("Load", f"load-{zn}", bus=zn, p_set=load.values * shares[zn])
    for pair, s in z["interfaces"].items():
        a, b = pair.split("-")
        n.add("Line", pair, bus0=a, bus1=b, s_nom=s, x=0.1, r=0.01)
    st = station_table(year if year in (2019, 2020, 2021, 2022, 2023) else 2023)
    fleet = dataset.fleet("mew-yb-2023")
    caps = fleet[~fleet.technology.isin(["pv", "wind", "csp"])].groupby("plant_id").capacity_mw.sum()
    for pid, cap in caps.items():
        if pid not in st.index:
            continue
        floor = float(st.loc[pid, "min_monthly_avg_mw"]) / cap if pid in DESAL else 0.0
        n.add("Generator", pid, bus=z["stations"][pid], p_nom=cap, carrier="thermal",
              marginal_cost=float(st.loc[pid, "kd_per_mwh"]) / fx, p_min_pu=min(floor, 1.0))
    # Load shedding at a high cost keeps the problem feasible and makes shortfalls visible.
    for zn in z["zones"]:
        n.add("Generator", f"shed-{zn}", bus=zn, p_nom=1e5, marginal_cost=10000.0, carrier="shed")
    if plant is not None:
        p = plant.reindex(snaps).fillna(0).clip(lower=0)
        nom = max(float(p.max()), 1e-3)
        n.add("Generator", "plant", bus=plant_zone, p_nom=nom, p_max_pu=(p / nom).values, marginal_cost=0.0, carrier="plant")
    return n, st


def zone_of(lat: float, lon: float) -> str:
    """The zone of a site: the zone of the nearest power station (coarse; Shagaya and
    the west are north, the Ahmadi coast south, Kuwait City central)."""
    sites = {"north": [(29.2055, 47.0524), (29.5642, 48.1707), (29.3652, 47.7873)],
             "central": [(29.3504, 47.9400)], "south": [(28.7135, 48.3806), (29.0359, 48.1536)]}
    d = {zn: min((la - lat) ** 2 + (lo - lon) ** 2 for la, lo in pts) for zn, pts in sites.items()}
    return min(d, key=d.get)


def interaction(plant_export_local: pd.Series, lat: float, lon: float, year: int, fx: float,
                hourly: bool = False) -> dict:
    """Solve the year without and with the plant; plant_export_local is hourly MW in
    Kuwait local time (naive), the plant's export at its connection."""
    zn = zone_of(lat, lon)
    out = {}
    for case, p in (("without", None), ("with", plant_export_local)):
        n, st = build_network(year, p, zn, fx)
        n.optimize(solver_name="highs", solver_options={"log_to_console": False})
        g = n.generators_t.p
        thermal = [c for c in g.columns if c in st.index]
        fuel_mmbtu = sum(g[c].sum() * st.loc[c, "mmbtu_per_mwh"] for c in thermal)
        out[case] = {
            "fuel_bbtu": fuel_mmbtu / 1000, "fuel_cost_kd": sum(g[c].sum() * st.loc[c, "kd_per_mwh"] for c in thermal),
            "by_station_mwh": {c: float(g[c].sum()) for c in thermal},
            "shed_mwh": float(g[[c for c in g.columns if c.startswith("shed")]].sum().sum()),
            "plant_dispatched_mwh": float(g["plant"].sum()) if "plant" in g else 0.0,
            "max_interface_loading": {l: float((n.lines_t.p0[l].abs() / n.lines.s_nom[l]).max()) for l in n.lines.index},
        }
        if hourly:
            out[case]["dispatch"] = g[thermal + (["plant"] if "plant" in g else [])].copy()
            out[case]["flows"] = n.lines_t.p0.copy()
            out[case]["load"] = n.loads_t.p_set.sum(axis=1)
    w, wo = out["with"], out["without"]
    offered = float(plant_export_local[plant_export_local.index.year == year].clip(lower=0).sum())
    return {
        "year": year, "zone": zn, "plant_offered_mwh": offered, "plant_dispatched_mwh": w["plant_dispatched_mwh"],
        "system_curtailment_mwh": offered - w["plant_dispatched_mwh"],
        "fuel_avoided_bbtu": wo["fuel_bbtu"] - w["fuel_bbtu"],
        "fuel_cost_avoided_kd": wo["fuel_cost_kd"] - w["fuel_cost_kd"],
        "fuel_cost_avoided_kd_per_mwh": (wo["fuel_cost_kd"] - w["fuel_cost_kd"]) / max(w["plant_dispatched_mwh"], 1e-9),
        "displaced_mwh_by_station": {c: wo["by_station_mwh"][c] - w["by_station_mwh"].get(c, 0) for c in wo["by_station_mwh"]},
        "load_shed_mwh": {"without": wo["shed_mwh"], "with": w["shed_mwh"]},
        "max_interface_loading": w["max_interface_loading"],
        **({"hourly": {"without": wo["dispatch"], "with": w["dispatch"], "flows_with": w["flows"], "load": w["load"]}} if hourly else {}),
    }

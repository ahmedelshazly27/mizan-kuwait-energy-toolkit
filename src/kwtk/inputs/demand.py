"""Hourly gross system load for Kuwait: a reconstruction, not a measurement.

Decisions D1-D3 (docs/decisions.md); method in docs/demand-reconstruction.md.

Model, in Kuwait local time (UTC+03:00, no daylight saving):

    L(t) = a_m * [1 + s(h) + b * max(0, Te(t) - T0)] * (1 + g * weekend(t))
    Te(t) = phi * T(t) + (1 - phi) * EWMA_tau(T)(t)

    s(h)    base diurnal shape, two harmonics in the hour of day (4 parameters)
    T(t)    population-weighted ERA5 2 m temperature; Te blends it with its
            exponential smoothing over tau hours (thermal lag of buildings)
    b, T0   cooling response and its threshold
    g       Friday/Saturday effect
    a_m     one scale per month, set so the month sums to its printed gross
            generation (closed form, not fitted)

The seven shape parameters are fitted only to daily measurements: daily maximum,
minimum and energy where printed (MEW monthly books: May-July 2025 energy,
July 2025 peak and minimum, May-June 2024 and 2025 maximum and minimum). The
half-hourly curves on the yearly peak days (yearbooks 2020-2023) are never used in
fitting; they are the validation.

After scaling, each year with a printed peak is stretched about its monthly means,
L' = M_m + k (L - M_m) with one k per year, so the year's maximum equals the
printed peak and every month keeps its energy. k is reported; k far from 1 means
the shape model and the printed peak disagree.

Known simplifications, stated in the output: printed peaks are half-hourly
instants, the model is hourly; system load includes GCC interchange, the monthly
energy is gross station generation (interchange is not published monthly);
Ramadan and public holidays are not modelled."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from . import dataset, era5

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "inputs" / "demand"
TZ_OFFSET = pd.Timedelta(hours=3)
PARAMS = ["c1", "s1", "c2", "s2", "b_per_K", "t0_c", "tau_h", "weekend", "phi"]


def _local_temperature() -> pd.Series:
    t = era5.temperature().t2m_c
    t.index = t.index + TZ_OFFSET
    return t


def _smooth(t: np.ndarray, tau: float) -> np.ndarray:
    a = 1.0 / max(tau, 1.0)
    out = np.empty_like(t)
    acc = t[0]
    for i, x in enumerate(t):
        acc += a * (x - acc)
        out[i] = acc
    return out


def _shape(p, idx: pd.DatetimeIndex, temp: np.ndarray) -> np.ndarray:
    c1, s1, c2, s2, b, t0, tau, g, phi = p
    w = 2 * np.pi * idx.hour.values / 24
    base = 1 + c1 * np.cos(w) + s1 * np.sin(w) + c2 * np.cos(2 * w) + s2 * np.sin(2 * w)
    cool = b * np.maximum(0, phi * temp + (1 - phi) * _smooth(temp, tau) - t0)
    weekend = np.isin(idx.dayofweek.values, (4, 5))       # Friday, Saturday
    return (base + cool) * (1 + g * weekend)


def _scale_to_months(shape: pd.Series, monthly_mwh: pd.Series) -> pd.Series:
    m = shape.index.to_period("M")
    s = shape.groupby(m).transform("sum")
    target = m.map(lambda p: monthly_mwh.get(p, np.nan))
    return shape / s * np.asarray(target, dtype=float)


def monthly_energy(series: tuple[str, ...]) -> pd.Series:
    """Printed national gross generation by month (MWh) from the named series. Within
    a series the newest edition is used; two series may not cover the same month
    (the toolkit does not choose between sources)."""
    parts = []
    for name in series:
        s = dataset.series("generation_gross", "national", "monthly", series=name)
        s = s.sort_values("source_id").groupby("period_start").last()
        parts.append(pd.Series(s.canonical_value.values, index=pd.PeriodIndex(s.index, freq="M"), name=name))
    both = set.intersection(*(set(p.index) for p in parts)) if len(parts) > 1 else set()
    if both:
        raise ValueError(f"series {series} both cover {sorted(map(str, both))[:3]}...; name series that do not overlap")
    return pd.concat(parts).sort_index()


def daily_targets() -> pd.DataFrame:
    o = dataset.observations()
    o = o[(o.level == "national") & (o.frequency == "daily")]
    pick = lambda var, tables: o[(o.variable == var) & o.table_no.isin(tables)].assign(v=lambda d: pd.to_numeric(d.value))
    mx = pd.concat([pick("peak_load", ["daily-load"]), pick("max_load", ["daily-load-compare"])])
    mn = pick("min_load", ["daily-load", "daily-load-compare"])
    en = pick("generation_gross", ["generation-daily"])
    hours = lambda var: (o[o.variable == var].set_index("period_start").value_printed
                         .map(lambda t: int(t.split(":")[0]) + int(t.split(":")[1]) / 60))
    df = pd.DataFrame({"max_mw": mx.groupby("period_start").v.first(), "min_mw": mn.groupby("period_start").v.first(),
                       "energy_mwh": en.groupby("period_start").v.first(),
                       "peak_hour": hours("peak_load_time"), "min_hour": hours("min_load_time")})
    df.index = pd.to_datetime(df.index)
    return df


def peak_curves() -> pd.DataFrame:
    o = dataset.observations()
    c = o[o.table_no == "peak-day-load"].copy()
    c["t"] = pd.to_datetime(c.observed_at.str[:19])
    c["mw"] = pd.to_numeric(c.value)
    return c[["source_id", "t", "mw"]]


def annual_peaks() -> pd.Series:
    p = dataset.series("peak_load", "national", "annual", series="mew-yb")
    p = p.sort_values("source_id").groupby("period_start").last()      # newest edition printing that year
    return pd.Series(p.value.values, index=pd.to_datetime(p.index).year)


def fit(monthly: pd.Series) -> dict:
    temp = _local_temperature()
    tgt = daily_targets()
    months = sorted({d.to_period("M") for d in tgt.index} & set(monthly.index))
    idx = temp.index[temp.index.to_period("M").isin(months)]
    # warm-up: smooth from 30 days earlier so the lag state is settled
    start = idx[0] - pd.Timedelta(days=30)
    tw = temp[start:idx[-1]]
    tgt = tgt[tgt.index.to_period("M").isin(months)]

    def residuals(p):
        sh = pd.Series(_shape(p, tw.index, tw.values), index=tw.index)[idx[0]:]
        load = _scale_to_months(sh, monthly)
        day = load.groupby(load.index.normalize())
        r = []
        for col, f in (("max_mw", day.max()), ("min_mw", day.min()), ("energy_mwh", day.sum())):
            t = tgt[col].dropna()
            r.append((f.reindex(t.index).values - t.values) / t.values)
        # Where the time of the peak and minimum is printed, the model at that time
        # (linear between hours) must equal the printed load: this fixes the timing.
        for col, hcol in (("max_mw", "peak_hour"), ("min_mw", "min_hour")):
            t = tgt[[col, hcol]].dropna()
            at = pd.DatetimeIndex(t.index + pd.to_timedelta(t[hcol].values, unit="h"))
            lo_, hi_ = at.floor("h"), at.floor("h") + pd.Timedelta(hours=1)
            frac = (at - lo_) / pd.Timedelta(hours=1)
            v = load.reindex(lo_).values * (1 - frac) + load.reindex(hi_).values * frac
            r.append((np.asarray(v) - t[col].values) / t[col].values)
        return np.concatenate(r)

    p0 = [0.0, 0.0, 0.0, 0.0, 0.02, 28.0, 6.0, 0.0, 0.5]
    lo = [-0.6, -0.6, -0.6, -0.6, 0.0, 10.0, 1.0, -0.3, 0.0]
    hi = [0.6, 0.6, 0.6, 0.6, 0.5, 40.0, 96.0, 0.3, 1.0]
    res = least_squares(residuals, p0, bounds=(lo, hi), x_scale="jac")
    names = PARAMS
    r = residuals(res.x)
    sizes = [tgt.max_mw.notna().sum(), tgt.min_mw.notna().sum(), tgt.energy_mwh.notna().sum(),
             tgt[["max_mw", "peak_hour"]].dropna().shape[0], tgt[["min_mw", "min_hour"]].dropna().shape[0]]
    parts = np.split(r, np.cumsum(sizes)[:-1])
    keys = ["daily_max", "daily_min", "daily_energy", "load_at_printed_peak_time", "load_at_printed_min_time"]
    return {"params": dict(zip(names, map(float, res.x))), "fit_months": [str(m) for m in months],
            "fit_days": int(len(tgt)), "rmse_relative": {k: float(np.sqrt(np.mean(x ** 2))) for k, x in zip(keys, parts)}}


def reconstruct(monthly: pd.Series, params: dict, peaks: pd.Series) -> tuple[pd.Series, dict]:
    temp = _local_temperature()
    p = [params[k] for k in PARAMS]
    sh = pd.Series(_shape(p, temp.index, temp.values), index=temp.index)
    sh = sh[sh.index.to_period("M").isin(monthly.index)]
    load = _scale_to_months(sh, monthly)
    stretch = {}
    for y, g in load.groupby(load.index.year):
        full = g.index.to_period("M").nunique() == 12
        if y in peaks.index and full:
            mean = g.groupby(g.index.to_period("M")).transform("mean")
            dev = g - mean
            # max over hours of (mean + k dev) rises with k; bisect for the printed peak
            lo, hi = 0.0, 3.0
            for _ in range(60):
                k = (lo + hi) / 2
                lo, hi = (k, hi) if (mean + k * dev).max() < peaks[y] else (lo, k)
            load.loc[g.index] = mean + k * dev
            stretch[int(y)] = float(k)
    return load, stretch


def validate(load: pd.Series) -> pd.DataFrame:
    """Held-out check: the printed half-hourly curves on the yearly peak days."""
    rows = []
    for sid, c in peak_curves().groupby("source_id"):
        c = c[c.t.dt.minute == 0].set_index("t").mw
        m = load.reindex(c.index)
        if m.isna().all():
            continue
        e = (m - c) / c
        rows.append({"source_id": sid, "day": str(c.index[0].date()), "hours": int(m.notna().sum()),
                     "mape": float(e.abs().mean()), "max_abs_error": float(e.abs().max()),
                     "printed_peak_hour": int(c.idxmax().hour), "model_peak_hour": int(m.idxmax().hour),
                     "printed_min_hour": int(c.idxmin().hour), "model_min_hour": int(m.idxmin().hour)})
    return pd.DataFrame(rows)


def build(series: tuple[str, ...] = ("csb-env", "mew-mb")) -> dict:
    monthly = monthly_energy(series)
    f = fit(monthly)
    peaks = annual_peaks()
    load, stretch = reconstruct(monthly, f["params"], peaks)
    val = validate(load)
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({"load_mw": load.round(1)})
    df.index.name = "time_kuwait"
    with gzip.GzipFile(OUT / "kuwait-gross-load-reconstructed.csv.gz", "wb", mtime=0) as fh:
        fh.write(df.to_csv().encode())
    meta = {"label": "RECONSTRUCTION: hourly gross system load modelled from monthly energy, annual peaks and "
                     "ERA5 temperature; not a measurement",
            "decisions": ["D1", "D2", "D3"], "monthly_energy_series": list(series), "fit": f,
            "peak_stretch_k": stretch, "validation_peak_days": val.to_dict("records"),
            "years_without_printed_peak": sorted(int(y) for y in set(load.index.year) - set(stretch)),
            "assumption_nonsummer_shape": "demand.base_shape_nonsummer"}
    (OUT / "kuwait-gross-load-reconstructed.json").write_text(json.dumps(meta, indent=2))
    return meta


def load_series() -> pd.Series:
    """The committed reconstruction, hourly MW, Kuwait local time (naive)."""
    return pd.read_csv(OUT / "kuwait-gross-load-reconstructed.csv.gz", index_col=0, parse_dates=True).load_mw

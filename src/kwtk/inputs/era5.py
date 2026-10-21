"""Population-weighted hourly temperature for Kuwait, from ERA5.

Demand responds to the temperature where people live, so the series is the
population-weighted mean over ERA5's 0.25° cells: WorldPop 2020 (constrained,
UN-adjusted, 100 m) summed into each cell, keeping the most populated cells until
98.8% of the population is covered (15 cells). Each cell's series comes from the
CDS dataset `reanalysis-era5-single-levels-timeseries` (ERA5 at a grid point), and
the returned grid point must be the requested cell centre.

Committed outputs (inputs/weather/): the weighted hourly series in °C (UTC) and the
cell weights. Raw cell files are cached in data/era5/ and not committed. Rebuilding
needs a CDS account (CDS_API_KEY or ~/.cdsapirc) and the WorldPop raster; using
the committed outputs needs neither."""

from __future__ import annotations

import gzip
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data" / "era5"
OUT = ROOT / "inputs" / "weather"
COVER = 0.985
DATES = "2013-01-01/2025-12-31"


def cell_weights(worldpop_tif: Path) -> pd.DataFrame:
    import rasterio
    r = rasterio.open(worldpop_tif)
    a = r.read(1).astype(float)
    a[~np.isfinite(a) | (a < 0)] = 0
    rows, cols = np.nonzero(a)
    lon, lat = rasterio.transform.xy(r.transform, rows, cols)
    df = pd.DataFrame({"lat": np.round(np.array(lat) / 0.25) * 0.25, "lon": np.round(np.array(lon) / 0.25) * 0.25,
                       "population": a[rows, cols]})
    w = df.groupby(["lat", "lon"], as_index=False).population.sum().sort_values("population", ascending=False)
    w["share_of_kuwait"] = w.population / w.population.sum()
    keep = w[w.share_of_kuwait.cumsum().shift(fill_value=0) < COVER].copy()
    keep["weight"] = keep.population / keep.population.sum()
    return keep.reset_index(drop=True)


def fetch_cell(lat: float, lon: float) -> pd.DataFrame:
    import cdsapi
    CACHE.mkdir(parents=True, exist_ok=True)
    z = CACHE / f"cell_{lat:.2f}_{lon:.2f}.zip"
    if not z.exists():
        cdsapi.Client(quiet=True).retrieve("reanalysis-era5-single-levels-timeseries", {
            "variable": ["2m_temperature", "2m_dewpoint_temperature"],
            "location": {"latitude": lat, "longitude": lon}, "date": [DATES], "data_format": "csv"}, str(z))
    with zipfile.ZipFile(z) as f:
        df = pd.read_csv(io.BytesIO(f.read(f.namelist()[0])), parse_dates=["valid_time"])
    got = (df.latitude.iloc[0], df.longitude.iloc[0])
    if not np.allclose(got, (lat, lon)):
        raise ValueError(f"requested cell {lat}, {lon}; CDS returned grid point {got}")
    return df


def build(worldpop_tif: Path) -> pd.DataFrame:
    w = cell_weights(worldpop_tif)
    t2m = d2m = None
    for c in w.itertuples():
        df = fetch_cell(c.lat, c.lon).set_index("valid_time")
        t2m = df.t2m * c.weight if t2m is None else t2m + df.t2m * c.weight
        d2m = df.d2m * c.weight if d2m is None else d2m + df.d2m * c.weight
    out = pd.DataFrame({"t2m_c": (t2m - 273.15).round(2), "d2m_c": (d2m - 273.15).round(2)})
    out.index.name = "time_utc"
    if out.isna().any().any() or len(out) != len(pd.date_range(*DATES.split("/"), freq="h")) + 23:
        raise ValueError("ERA5 cell series do not share one complete hourly index")
    OUT.mkdir(parents=True, exist_ok=True)
    w.to_csv(OUT / "era5-cells-population-weights.csv", index=False)
    with gzip.GzipFile(OUT / "era5-t2m-popweighted.csv.gz", "wb", mtime=0) as f:
        f.write(out.to_csv().encode())
    return out


def temperature() -> pd.DataFrame:
    """The committed series: hourly, UTC, °C (t2m_c, d2m_c), population-weighted."""
    return pd.read_csv(OUT / "era5-t2m-popweighted.csv.gz", parse_dates=["time_utc"], index_col="time_utc")

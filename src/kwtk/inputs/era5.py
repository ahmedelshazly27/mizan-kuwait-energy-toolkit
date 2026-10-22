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


# ------------------------------------------------------------------ site weather grid
#
# Every ERA5 0.25° cell whose square overlaps Kuwait (45 cells; selected once with the
# country outline from PyPSA-Earth's GADM shapes, which are not redistributed here).
# One compressed file per cell, integers with fixed scales, hourly 2013-2024 UTC,
# stamped at the END of each hour (ERA5 convention for accumulated fields).

GRID = ROOT / "inputs" / "weather" / "grid"
GRID_YEARS = ("2013-01-01", "2024-12-31")
CELLS = [(28.5, 47.75), (28.5, 48.0), (28.5, 48.25), (28.5, 48.5), (28.75, 47.5), (28.75, 47.75), (28.75, 48.0),
         (28.75, 48.25), (28.75, 48.5), (29.0, 46.5), (29.0, 46.75), (29.0, 47.0), (29.0, 47.25), (29.0, 47.5),
         (29.0, 47.75), (29.0, 48.0), (29.0, 48.25), (29.25, 46.5), (29.25, 46.75), (29.25, 47.0), (29.25, 47.25),
         (29.25, 47.5), (29.25, 47.75), (29.25, 48.0), (29.25, 48.25), (29.5, 46.75), (29.5, 47.0), (29.5, 47.25),
         (29.5, 47.5), (29.5, 47.75), (29.5, 48.0), (29.5, 48.25), (29.75, 47.0), (29.75, 47.25), (29.75, 47.5),
         (29.75, 47.75), (29.75, 48.0), (29.75, 48.25), (29.75, 48.5), (30.0, 47.0), (30.0, 47.25), (30.0, 47.5),
         (30.0, 47.75), (30.0, 48.0), (30.0, 48.25)]
# name: (ERA5 variable, CSV column, converter to the stored unit, scale of the stored integer)
FIELDS = {"ghi_w_m2": ("surface_solar_radiation_downwards", "ssrd", lambda x: x / 3600, 1),
          "dir_h_w_m2": ("total_sky_direct_solar_radiation_at_surface", "fdir", lambda x: x / 3600, 1),
          "t2m_c": ("2m_temperature", "t2m", lambda x: x - 273.15, 10),
          "d2m_c": ("2m_dewpoint_temperature", "d2m", lambda x: x - 273.15, 10),
          "u10_m_s": ("10m_u_component_of_wind", "u10", lambda x: x, 10),
          "v10_m_s": ("10m_v_component_of_wind", "v10", lambda x: x, 10),
          "tp_mm": ("total_precipitation", "tp", lambda x: x * 1000, 100),
          "sp_hpa": ("surface_pressure", "sp", lambda x: x / 100, 10)}


def _cell_file(lat: float, lon: float) -> Path:
    return GRID / f"era5_{lat:.2f}_{lon:.2f}.npz"


def fetch_grid_cell(lat: float, lon: float) -> Path:
    import cdsapi
    CACHE.mkdir(parents=True, exist_ok=True)
    z = CACHE / f"grid_{lat:.2f}_{lon:.2f}.zip"
    if not z.exists():
        cdsapi.Client(quiet=True).retrieve("reanalysis-era5-single-levels-timeseries", {
            "variable": [v[0] for v in FIELDS.values()], "location": {"latitude": lat, "longitude": lon},
            "date": ["/".join(GRID_YEARS)], "data_format": "csv"}, str(z))
    with zipfile.ZipFile(z) as f:
        df = pd.read_csv(io.BytesIO(f.read(f.namelist()[0])), parse_dates=["valid_time"])
    if not np.allclose((df.latitude.iloc[0], df.longitude.iloc[0]), (lat, lon)):
        raise ValueError(f"requested cell {lat}, {lon}; CDS returned {df.latitude.iloc[0]}, {df.longitude.iloc[0]}")
    want = pd.date_range(GRID_YEARS[0], pd.Timestamp(GRID_YEARS[1]) + pd.Timedelta(hours=23), freq="h")
    if not df.valid_time.equals(pd.Series(want, name="valid_time")):
        raise ValueError(f"cell {lat}, {lon}: incomplete hourly series")
    GRID.mkdir(parents=True, exist_ok=True)
    arrays = {k: np.round(conv(df[col].values) * scale).astype(np.int16) for k, (_, col, conv, scale) in FIELDS.items()}
    np.savez_compressed(_cell_file(lat, lon), start=np.array(GRID_YEARS[0]), **arrays)
    return _cell_file(lat, lon)


def nearest_cell(lat: float, lon: float) -> tuple[float, float]:
    d = [((la - lat) ** 2 + ((lo - lon) * np.cos(np.radians(lat))) ** 2, (la, lo)) for la, lo in CELLS]
    return min(d)[1]


def site_weather(lat: float, lon: float, years: list[int] | None = None) -> pd.DataFrame:
    """Hourly weather at the nearest ERA5 cell, indexed at each hour's MIDPOINT (UTC):
    irradiance is that hour's mean; temperature, dewpoint, wind and pressure are the
    mean of the instantaneous values at the hour's two ends. Diffuse = global - direct
    on the horizontal; DNI = direct horizontal / cos(zenith at the midpoint), set to
    0 when the sun is below 5° elevation (where the division is unstable)."""
    import pvlib
    la, lo = nearest_cell(lat, lon)
    f = np.load(_cell_file(la, lo))
    end = pd.date_range(str(f["start"]), periods=len(f["ghi_w_m2"]), freq="h", tz="UTC")
    raw = pd.DataFrame({k: f[k] / FIELDS[k][3] for k in FIELDS}, index=end)
    inst = ["t2m_c", "d2m_c", "u10_m_s", "v10_m_s", "sp_hpa"]
    mid = raw.copy()
    mid[inst] = (raw[inst] + raw[inst].shift(1)) / 2
    mid = mid.iloc[1:]
    mid.index = mid.index - pd.Timedelta(minutes=30)
    if years:
        mid = mid[mid.index.year.isin(years)]
    sp = pvlib.solarposition.get_solarposition(mid.index, la, lo, pressure=mid.sp_hpa.values * 100,
                                               temperature=mid.t2m_c.values)
    cosz = np.cos(np.radians(sp.apparent_zenith.values))
    up = sp.apparent_elevation.values > 5
    out = pd.DataFrame(index=mid.index)
    out["ghi"] = mid.ghi_w_m2.clip(lower=0)
    out["dni"] = np.where(up, mid.dir_h_w_m2 / np.where(up, cosz, 1), 0.0).clip(0, 1100)
    out["dhi"] = (mid.ghi_w_m2 - np.where(up, mid.dir_h_w_m2, 0)).clip(lower=0)
    out["temp_air"] = mid.t2m_c
    out["temp_dew"] = mid.d2m_c
    out["wind_speed"] = np.hypot(mid.u10_m_s, mid.v10_m_s)
    out["precip_mm"] = mid.tp_mm
    out["pressure"] = mid.sp_hpa * 100
    out.attrs = {"cell": (la, lo), "source": "ERA5 (C3S), reanalysis-era5-single-levels-timeseries"}
    return out

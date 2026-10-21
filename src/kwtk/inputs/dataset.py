"""The Kuwait Electricity Open Dataset, as the toolkit's single source of measured data.

`inputs/dataset/` is a snapshot of the dataset's build outputs, copied unchanged
(rows, ids and columns are the dataset's own) and pinned by MANIFEST.yaml to a
dataset commit with the SHA-256 of every file. It is committed so the toolkit runs
offline after one clone. `kwtk inputs import --dataset PATH` refreshes it from a
local build of the dataset repository; nothing here edits a value.

The loaders never choose between sources. Where several documents print the same
quantity, the caller names the source; a quantity with an open conflict in the
dataset is reported, not resolved."""

from __future__ import annotations

import gzip
import hashlib
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT / "inputs" / "dataset"
REPO = "https://github.com/ahmedelshazly27/mizan-kuwait-electricity-data"
FILES = ["observations.csv", "plants.csv", "sources.csv", "source_tables.csv", "variables.csv", "conflicts.csv"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def import_snapshot(dataset: Path, dest: Path = SNAPSHOT) -> dict:
    """Copy a dataset build into the toolkit. The observations file is gzipped
    (deterministically, mtime 0) so the snapshot stays small; the others are copied."""
    out = Path(dataset) / "data" / "out"
    missing = [f for f in FILES if not (out / f).exists()]
    if missing:
        raise FileNotFoundError(f"{out} has no {', '.join(missing)}; run `make` in the dataset repository first")
    git = lambda *a: subprocess.run(["git", "-C", str(dataset), *a], capture_output=True, text=True).stdout.strip()
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError(f"{dataset} has uncommitted changes; import only from a committed dataset build")
    dest.mkdir(parents=True, exist_ok=True)
    files = {}
    for f in FILES:
        src = out / f
        if f == "observations.csv":
            target = dest / (f + ".gz")
            with src.open("rb") as i, gzip.GzipFile(target, "wb", mtime=0) as o:
                shutil.copyfileobj(i, o)
        else:
            target = dest / f
            shutil.copyfile(src, target)
        files[target.name] = {"sha256": _sha(target), "source_sha256": _sha(src)}
    manifest = {"dataset": REPO, "commit": git("rev-parse", "HEAD"), "imported": date.today().isoformat(),
                "licence": "CC BY 4.0 (Kuwait Electricity Open Dataset, Mizan Energy)", "files": files}
    (dest / "MANIFEST.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    return manifest


def verify(dest: Path = SNAPSHOT) -> list[str]:
    """Problems with the snapshot: a missing file or one whose SHA-256 differs from the manifest."""
    m = yaml.safe_load((dest / "MANIFEST.yaml").read_text())
    return [f"inputs/dataset/{n}: {'missing' if not (dest / n).exists() else 'SHA-256 does not match MANIFEST.yaml'}"
            for n, v in m["files"].items() if not (dest / n).exists() or _sha(dest / n) != v["sha256"]]


def observations(dest: Path = SNAPSHOT) -> pd.DataFrame:
    return pd.read_csv(dest / "observations.csv.gz", dtype=str, keep_default_na=False).replace({"": None})


def _num(df: pd.DataFrame, *cols: str) -> pd.DataFrame:
    for c in cols:
        df[c] = pd.to_numeric(df[c])
    return df


def open_conflicts(obs_ids, dest: Path = SNAPSHOT) -> pd.DataFrame:
    """Open dataset conflicts that involve any of the given observation ids."""
    c = pd.read_csv(dest / "conflicts.csv", dtype=str)
    ids = set(map(str, obs_ids))
    hit = c["members"].fillna("").map(lambda m: bool(ids & set(m.split())))
    return c[hit & (c["status"] == "open")]


def fleet(source_id: str, dest: Path = SNAPSHOT) -> pd.DataFrame:
    """Every generating unit in one yearbook edition (station pages): plant, block,
    unit, technology, rating and the commissioning date exactly as printed."""
    o = observations(dest)
    o = o[(o.source_id == source_id) & (o.table_no == "station-units")]
    if o.empty:
        raise ValueError(f"{source_id} has no station-units table in the dataset snapshot")
    keys = ["plant_id", "unit_group", "row_label", "technology", "page_pdf"]
    cap = o[o.variable == "unit_capacity"].set_index(keys)
    com = o[o.variable == "unit_commissioning_year"].set_index(keys)
    df = pd.DataFrame({"capacity_mw": cap["value"], "commissioning_year": com["value"],
                       "commissioning_printed": com["value_printed"], "obs_id_capacity": cap["id"]}).reset_index()
    df["unit"] = df.row_label.str.split(" / ").str[-1]
    df["source_id"] = source_id
    return _num(df, "capacity_mw", "commissioning_year", "page_pdf")[
        ["plant_id", "unit_group", "unit", "technology", "capacity_mw", "commissioning_year",
         "commissioning_printed", "source_id", "page_pdf", "obs_id_capacity"]]


def series(variable: str, level: str, frequency: str, source_id: str | None = None,
           series: str | None = None, dest: Path = SNAPSHOT) -> pd.DataFrame:
    """One variable as printed. Give `source_id` for one edition, or `series` (a
    source id prefix such as "mew-yb" or "csb-env") for all editions of one series,
    which keeps every edition's value side by side (restatements stay visible)."""
    if (source_id is None) == (series is None):
        raise ValueError("name exactly one of source_id or series; the toolkit does not choose between sources")
    o = observations(dest)
    o = o[(o.variable == variable) & (o.level == level) & (o.frequency == frequency)]
    o = o[o.source_id == source_id] if source_id else o[o.source_id.str.startswith(series + "-")]
    return _num(o.copy(), "value", "canonical_value")

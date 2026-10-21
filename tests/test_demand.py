import json

import pandas as pd
import pytest

from kwtk.inputs import demand as d

LOAD = d.OUT / "kuwait-gross-load-reconstructed.csv.gz"
META = json.loads((d.OUT / "kuwait-gross-load-reconstructed.json").read_text())


@pytest.fixture(scope="module")
def load():
    return pd.read_csv(LOAD, index_col=0, parse_dates=True).load_mw


def test_labelled_as_reconstruction():
    assert META["label"].startswith("RECONSTRUCTION")


def test_months_sum_to_printed_energy(load):
    printed = d.monthly_energy(tuple(META["monthly_energy_series"]))
    got = load.groupby(load.index.to_period("M")).sum()
    assert (abs(got / printed.reindex(got.index) - 1) < 1e-4).all()


def test_years_reach_printed_peak(load):
    peaks = d.annual_peaks()
    for y in META["peak_stretch_k"]:
        assert load[str(y)].max() == pytest.approx(peaks[int(y)], abs=0.1)


def test_held_out_curves_reported():
    assert len(META["validation_peak_days"]) == 4

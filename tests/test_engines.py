"""Engine tests on a placeholder plant with placeholder assumptions (tests/fixtures):
they check the mechanics, not Kuwaiti numbers."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
from test_assumptions import TEST_ASSUMPTIONS  # noqa: E402

from kwtk.inputs import era5  # noqa: E402
from kwtk.plant.evaluate import evaluate  # noqa: E402
from kwtk.plant.resolve import OpenAssumption, Resolver  # noqa: E402

SMOKE = Path(__file__).parent / "fixtures" / "smoke.yaml"
pytestmark = pytest.mark.skipif(not era5._cell_file(*era5.nearest_cell(28.55, 47.8)).exists(),
                                reason="weather grid cell not present")


@pytest.fixture(scope="module")
def run():
    return evaluate(SMOKE, resolver=Resolver(assumptions=TEST_ASSUMPTIONS))


def test_open_assumption_refuses_to_run():
    with pytest.raises(OpenAssumption, match="still open"):
        evaluate(SMOKE)


def test_waterfall_only_loses_after_poa(run):
    w = run["result"]["waterfall_mwh"][0]
    order = ["after_iam", "after_soiling", "after_temperature", "after_dc_losses", "after_inverter_efficiency",
             "after_clipping", "after_ac_losses", "after_availability"]
    assert all(w[a] >= w[b] for a, b in zip(order, order[1:]) if (a, b) != ("after_soiling", "after_temperature"))
    assert w["after_bifacial_gain"] >= w["after_soiling"]          # bifacial rear gain is the only gain after POA


def test_energy_balance(run):
    h = run["hourly"]
    lhs = h.pv_ac + h.battery - h.aux
    assert ((lhs.clip(upper=120) - h.export - h.curtailed + h["import"]).abs() < 1e-6).all()


def test_pysam_matches_capital_recovery_check(run):
    e = run["result"]["economics"]
    assert e["lcoe_real_usd_per_kwh"] == pytest.approx(e["lcoe_crf_check_usd_per_kwh"], rel=0.01)


def test_every_input_has_an_origin(run):
    assert all("origin" in v for v in run["result"]["inputs"].values())

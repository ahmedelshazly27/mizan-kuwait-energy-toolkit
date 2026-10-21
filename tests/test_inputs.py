import pytest

from kwtk.inputs import dataset as d


def test_snapshot_matches_manifest():
    assert d.verify() == []


def test_fleet_sums_to_mew_national_capacity():
    # MEW 2023 yearbook: installed capacity 2023 = 20,250 MW (capacity-history Total)
    f = d.fleet("mew-yb-2023")
    nat = d.series("installed_capacity", "national", "annual", source_id="mew-yb-2023")
    assert f.capacity_mw.sum() == pytest.approx(nat[nat.period_start == "2023-01-01"].value.item())
    assert set(f.plant_id) <= set(d.pd.read_csv(d.SNAPSHOT / "plants.csv").id)


def test_series_requires_a_named_source():
    with pytest.raises(ValueError, match="does not choose"):
        d.series("peak_load", "national", "annual")


def test_conflicts_are_reported():
    cap = d.series("installed_capacity", "national", "annual", series="mew-yb")
    assert len(d.open_conflicts(cap.id)) > 0

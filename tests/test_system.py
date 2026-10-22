import pytest

from kwtk.engines import system


def test_zone_shares_from_the_mew_table():
    s = system.zone_shares()
    assert s.sum() == pytest.approx(1.0)
    # hand sums of the zone mapping (inputs/zones.yaml) over the 2023 table: 16,940 MW
    assert s["central"] == pytest.approx((8033 + 1302 * 252 / 20250) / 16940, abs=1e-4)


def test_station_costs_come_from_mew_fuel_and_generation():
    st = system.station_table(2023)
    assert st.loc["zour-north", "kd_per_mwh"] == pytest.approx(234551614 / 13994000, rel=1e-6)
    assert (st.min_monthly_avg_mw >= 0).all()


def test_every_station_has_a_zone():
    z = system.zones()
    assert set(system.station_table(2023).index) <= set(z["stations"])
    assert all(r["zone"] in z["zones"] + ["stations"] for r in z["area_rows"].values())

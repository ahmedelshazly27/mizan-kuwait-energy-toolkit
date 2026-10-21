from pathlib import Path

import yaml

from kwtk.config.validate import validate

EX = Path(__file__).resolve().parents[1] / "configs" / "examples" / "schema-example-pv-storage.yaml"


def _variant(tmp_path, edit):
    d = yaml.safe_load(EX.read_text())
    edit(d)
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(d))
    return validate(p)


def test_example_is_valid():
    r = validate(EX)
    assert r.ok, r.text()


def test_dc_ac_ratio_outside_range(tmp_path):
    def e(d):
        d["inverters"]["dc_ac_ratio"] = 2.4
        d["inverters"]["units"][0]["count"] = 12      # keep it consistent: 120 MWp / 48 MVA ≈ 2.5
        d["inverters"]["units"][0]["inline"]["ac_rating_kva"] = 4000
    r = _variant(tmp_path, e)
    assert any("DC to AC ratio above 2 is outside the modelled range" in x for x in r.range), r.text()
    assert not r.ok


def test_inconsistent_capacity(tmp_path):
    r = _variant(tmp_path, lambda d: d["pv"]["arrays"][0].__setitem__("dc_capacity_mwp", 150))
    assert any("dc_capacity_mwp is 150" in x for x in r.errors), r.text()


def test_misspelt_key(tmp_path):
    r = _variant(tmp_path, lambda d: d["site"].__setitem__("exprt_limit", 5))
    assert any("site.exprt_limit is not a field" in x for x in r.errors), r.text()


def test_outside_kuwait(tmp_path):
    r = _variant(tmp_path, lambda d: d["site"]["location"].__setitem__("lat", 24.5))
    assert any("site.location.lat is 24.5; it must be at least 28.5" in x for x in r.errors), r.text()


def test_unknown_assumption(tmp_path):
    r = _variant(tmp_path, lambda d: d["economics"]["finance"].__setitem__("wacc_real", "assumption:wacc.nowhere"))
    assert any("assumption:wacc.nowhere, which is not in inputs/assumptions.yaml" in x for x in r.errors), r.text()


def test_dc_storage_needs_bus(tmp_path):
    r = _variant(tmp_path, lambda d: d["storage"]["blocks"][0].__setitem__("coupling", "dc"))
    assert any("dc-coupled storage block needs dc_bus" in x for x in r.errors), r.text()

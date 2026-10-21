"""Validate a plant configuration and report problems as sentences.

Three kinds of finding:
  error    the file cannot be evaluated (wrong type, missing field, inconsistency,
           unresolved reference)
  range    legal, but outside the range the methods are validated for; an error
           unless evaluation.allow_outside_modelled_range is true, then a warning
  default  a field the user did not set, filled from the schema or the assumptions
           file; listed so a reviewer sees what was not chosen
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import PlantConfig

ROOT = Path(__file__).resolve().parents[3]

# Ranges the methods are validated for. Changing one is a modelling decision and is
# recorded in docs/modelled-range.md.
MODELLED = {
    "dc_ac_ratio": (1.0, 2.0, "DC to AC ratio"),
    "storage_duration_h": (0.25, 12.0, "storage duration (energy / power)"),
    "gcr": (0.15, 0.70, "ground coverage ratio"),
    "fixed_tilt_deg": (0.0, 45.0, "fixed tilt"),
    "tracker_max_angle_deg": (30.0, 60.0, "tracker rotation limit"),
    "array_mwp": (0.1, 5000.0, "array DC capacity (MWp)"),
    "round_trip_efficiency": (0.60, 0.95, "round-trip efficiency"),
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    range: list[str] = field(default_factory=list)
    defaults: list[str] = field(default_factory=list)
    config: PlantConfig | None = None

    @property
    def ok(self) -> bool:
        allow = bool(self.config and self.config.evaluation.allow_outside_modelled_range)
        return not self.errors and (allow or not self.range)

    def text(self) -> str:
        out = []
        allow = bool(self.config and self.config.evaluation.allow_outside_modelled_range)
        for e in self.errors:
            out.append(f"error: {e}")
        for r in self.range:
            out.append(f"{'warning' if allow else 'error'}: {r}")
        if self.ok:
            out.append(f"valid ({len(self.defaults)} defaults applied; see the run report)")
        return "\n".join(out)


def _sentence(err: dict) -> str:
    loc = ".".join(str(p) for p in err["loc"]) or "(top level)"
    t, msg, ctx = err["type"], err["msg"], err.get("ctx", {})
    val = err.get("input")
    if t == "missing":
        return f"{loc} is required"
    if t == "extra_forbidden":
        return f"{loc} is not a field of this schema (check the spelling)"
    if t in ("greater_than_equal", "less_than_equal", "greater_than", "less_than"):
        bound = next(iter(ctx.values()))
        word = {"greater_than_equal": "at least", "less_than_equal": "at most",
                "greater_than": "more than", "less_than": "less than"}[t]
        return f"{loc} is {val}; it must be {word} {bound}"
    if t == "literal_error":
        return f"{loc} is {val!r}; it must be one of {ctx.get('expected')}"
    if t == "string_pattern_mismatch":
        return f"{loc} is {val!r}, which is not a number or a reference (assumption:..., library:..., profile:...)"
    if t == "value_error":
        return f"{loc}: {msg.removeprefix('Value error, ')}"
    return f"{loc}: {msg}"


def _check_refs(raw, path: str, report: Report, assumptions: dict, library: set[str]) -> None:
    if isinstance(raw, dict):
        for k, v in raw.items():
            _check_refs(v, f"{path}.{k}" if path else k, report, assumptions, library)
    elif isinstance(raw, list):
        for i, v in enumerate(raw):
            _check_refs(v, f"{path}[{i}]", report, assumptions, library)
    elif isinstance(raw, str):
        if raw.startswith("assumption:") and raw.split(":", 1)[1] not in assumptions:
            report.errors.append(f"{path} refers to {raw}, which is not in inputs/assumptions.yaml")
        if raw.startswith("library:") and raw.split(":", 1)[1] not in library:
            report.errors.append(f"{path} refers to {raw}, which is not in library/")


def _range(report: Report, key: str, value: float, where: str) -> None:
    lo, hi, label = MODELLED[key]
    if value > hi:
        report.range.append(f"{label} above {hi:g} is outside the modelled range ({where} = {value:g})")
    elif value < lo:
        report.range.append(f"{label} below {lo:g} is outside the modelled range ({where} = {value:g})")


def load_assumptions(root: Path = ROOT) -> dict:
    p = root / "inputs" / "assumptions.yaml"
    return (yaml.safe_load(p.read_text()) or {}).get("assumptions", {}) if p.exists() else {}


def load_library(root: Path = ROOT) -> dict[str, dict]:
    out = {}
    for f in (root / "library").glob("*/*.yaml"):
        d = yaml.safe_load(f.read_text())
        out[d["id"]] = d
    return out


def validate(path: Path | str, root: Path = ROOT) -> Report:
    report = Report()
    try:
        raw = yaml.safe_load(Path(path).read_text())
    except yaml.YAMLError as e:
        report.errors.append(f"the file is not valid YAML: {e.problem} at line {e.problem_mark.line + 1}" if hasattr(e, "problem_mark") else f"the file is not valid YAML: {e}")
        return report
    if not isinstance(raw, dict):
        report.errors.append("the file must be a mapping of sections (site, pv, controls, ...)")
        return report
    try:
        cfg = PlantConfig.model_validate(raw)
    except ValidationError as e:
        report.errors += [_sentence(x) for x in e.errors()]
        return report
    report.config = cfg
    assumptions, library = load_assumptions(root), load_library(root)
    _check_refs(raw, "", report, assumptions, set(library))

    if cfg.pv:
        dc_total = 0.0
        for a in cfg.pv.arrays:
            where = f"pv.arrays[{a.id}]"
            dc_total += a.dc_capacity_mwp
            _range(report, "array_mwp", a.dc_capacity_mwp, f"{where}.dc_capacity_mwp")
            if a.layout.gcr is not None:
                _range(report, "gcr", a.layout.gcr, f"{where}.layout.gcr")
            if a.mounting.type == "fixed":
                _range(report, "fixed_tilt_deg", a.mounting.tilt_deg, f"{where}.mounting.tilt_deg")
            else:
                _range(report, "tracker_max_angle_deg", a.mounting.max_angle_deg, f"{where}.mounting.max_angle_deg")
            mod = a.module.inline.model_dump() if a.module.inline else library.get(a.module.ref.split(":", 1)[1], {})
            if mod.get("stc_power_w"):
                implied = a.layout.modules_per_string * a.layout.strings * mod["stc_power_w"] / 1e6
                if abs(implied - a.dc_capacity_mwp) > 0.01 * a.dc_capacity_mwp:
                    report.errors.append(
                        f"{where}: dc_capacity_mwp is {a.dc_capacity_mwp:g}, but modules_per_string × strings × "
                        f"module power gives {implied:.2f} MWp (more than 1% apart)")
        _range(report, "dc_ac_ratio", cfg.inverters.dc_ac_ratio, "inverters.dc_ac_ratio")
        ac = 0.0
        for u in cfg.inverters.units:
            inv = u.inline.model_dump() if u.inline else library.get(u.ref.split(":", 1)[1], {})
            if inv.get("ac_rating_kva"):
                ac += inv["ac_rating_kva"] * u.count / 1e3
        if ac:
            implied = dc_total / ac
            if abs(implied - cfg.inverters.dc_ac_ratio) > 0.02 * cfg.inverters.dc_ac_ratio:
                report.errors.append(
                    f"inverters.dc_ac_ratio is {cfg.inverters.dc_ac_ratio:g}, but the arrays ({dc_total:g} MWp) "
                    f"over the inverters ({ac:g} MVA) give {implied:.2f}")

    for b in (cfg.storage.blocks if cfg.storage else []):
        _range(report, "storage_duration_h", b.energy_mwh / b.power_mw, f"storage.blocks[{b.id}] energy/power")
        if isinstance(b.round_trip_efficiency, float):
            _range(report, "round_trip_efficiency", b.round_trip_efficiency, f"storage.blocks[{b.id}].round_trip_efficiency")

    set_fields = {k for k in raw}
    for name in ("pv", "storage", "desalination"):
        if name not in set_fields:
            report.defaults.append(f"{name}: none")
    if "availability" not in (raw.get("om") or {}):
        report.defaults.append("om.availability: from inputs/assumptions.yaml")
    if "degradation" not in (raw.get("om") or {}):
        report.defaults.append("om.degradation: from inputs/assumptions.yaml")
    return report

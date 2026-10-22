"""Turn configuration values into numbers, recording where each came from.

A value is one of:
  a number             set by the configuration's author
  assumption:<key>     an entry in inputs/assumptions.yaml; refused if its status is
                       `open` or its value is null (evaluation never runs on an open
                       assumption)
  library:<id>         a component in library/
Every resolution is recorded, so the run report lists each input and its origin."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..config.validate import load_assumptions, load_library


class OpenAssumption(Exception):
    pass


@dataclass
class Resolver:
    assumptions: dict = field(default_factory=load_assumptions)
    library: dict = field(default_factory=load_library)
    used: dict = field(default_factory=dict)          # path -> {"value", "origin", "source"}

    def __call__(self, value, path: str):
        if isinstance(value, str) and value.startswith("assumption:"):
            key = value.split(":", 1)[1]
            a = self.assumptions.get(key)
            if a is None:
                raise OpenAssumption(f"{path}: {value} is not in inputs/assumptions.yaml")
            if a.get("status") == "open" or a.get("value") is None:
                raise OpenAssumption(f"{path}: {value} is still open (no sourced value); "
                                     f"set a number in the configuration or source the assumption")
            self.used[path] = {"value": a["value"], "origin": value, "status": a["status"], "source": a.get("source")}
            return a["value"]
        if isinstance(value, str) and value.startswith("library:"):
            key = value.split(":", 1)[1]
            if key not in self.library:
                raise KeyError(f"{path}: {value} is not in library/")
            self.used[path] = {"value": key, "origin": value, "source": self.library[key].get("source")}
            return self.library[key]
        self.used[path] = {"value": value, "origin": "configuration"}
        return value

    def assumption(self, key: str, path: str | None = None):
        """An input the engines need that the schema does not expose per plant."""
        return self(f"assumption:{key}", path or key)

"""Plant configuration schema, kuwait-plant/0.1.

A configuration describes a plant the way an engineer specifies it. Numbers carry
their unit in the key. Any number may instead be a reference:
  assumption:<key>   an entry in inputs/assumptions.yaml (sourced, reviewable)
  library:<id>       a module, inverter or battery in library/
  profile:<id>       a time series in inputs/
Structural checks live here; checks against the modelled range live in validate.py.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Ref = Annotated[str, StringConstraints(pattern=r"^(assumption|library|profile):[a-z0-9_.\-/]+$")]
Num = float | Ref
Frac = Annotated[float, Field(ge=0, le=1)]
FracOrRef = Frac | Ref


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")   # a misspelt key is an error, not silently ignored


# ------------------------------------------------------------------ site

class Location(Strict):
    lat: float = Field(ge=28.5, le=30.15, description="decimal degrees, within Kuwait")
    lon: float = Field(ge=46.5, le=48.6, description="decimal degrees, within Kuwait")


class Terrain(Strict):
    slope_deg: float = Field(0.0, ge=0, le=30)
    slope_azimuth_deg: float = Field(180.0, ge=0, lt=360)
    albedo: FracOrRef | list[Frac] = "assumption:albedo.desert"


class GridConnection(Strict):
    point: str
    voltage_kv: float = Field(gt=0)
    export_limit_mw: float = Field(gt=0)
    import_limit_mw: float = Field(0.0, ge=0)


class Site(Strict):
    location: Location
    zone: str | None = None
    land_area_ha: float | None = Field(None, gt=0)
    terrain: Terrain = Terrain()
    grid_connection: GridConnection
    weather: str = "era5"
    soiling_source: Literal["dust-atlas", "flat"] = "dust-atlas"


# ------------------------------------------------------------------ pv

class ModuleInline(Strict):
    stc_power_w: float = Field(gt=0)
    technology: str
    vmp_v: float = Field(gt=0)
    imp_a: float = Field(gt=0)
    voc_v: float = Field(gt=0)
    isc_a: float = Field(gt=0)
    temp_coeff_pmax_pct_per_c: float = Field(lt=0)
    bifaciality: Frac = 0.0
    source: str


class Module(Strict):
    ref: Ref | None = None
    inline: ModuleInline | None = None

    @model_validator(mode="after")
    def one_of(self):
        if (self.ref is None) == (self.inline is None):
            raise ValueError("give the module either as ref (library:...) or inline, not both or neither")
        return self


class Stow(Strict):
    wind_speed_m_s: float = Field(gt=0)
    angle_deg: float = Field(ge=-90, le=90)


class Mounting(Strict):
    type: Literal["fixed", "single_axis"]
    tilt_deg: float | None = Field(None, ge=0, le=60)
    azimuth_deg: float | None = Field(None, ge=0, lt=360)
    axis_azimuth_deg: float | None = Field(None, ge=0, lt=360)
    max_angle_deg: float | None = Field(None, gt=0, le=90)
    backtracking: bool = True
    stow: Stow | None = None

    @model_validator(mode="after")
    def by_type(self):
        if self.type == "fixed" and (self.tilt_deg is None or self.azimuth_deg is None):
            raise ValueError("fixed mounting needs tilt_deg and azimuth_deg")
        if self.type == "single_axis" and (self.axis_azimuth_deg is None or self.max_angle_deg is None):
            raise ValueError("single-axis tracking needs axis_azimuth_deg and max_angle_deg")
        return self


class Layout(Strict):
    gcr: float | None = Field(None, gt=0, lt=1)
    pitch_m: float | None = Field(None, gt=0)
    module_height_m: float = Field(1.0, ge=0)
    modules_per_string: int = Field(gt=0)
    strings: int = Field(gt=0)

    @model_validator(mode="after")
    def gcr_or_pitch(self):
        if (self.gcr is None) == (self.pitch_m is None):
            raise ValueError("give the row spacing as gcr or pitch_m, exactly one of them")
        return self


class Array(Strict):
    id: str
    dc_capacity_mwp: float = Field(gt=0)
    module: Module
    mounting: Mounting
    layout: Layout
    thermal_model: str = "assumption:thermal.pvsyst_freestanding"


class PV(Strict):
    arrays: list[Array] = Field(min_length=1)


# ------------------------------------------------------------------ inverters

class InverterInline(Strict):
    ac_rating_kva: float = Field(gt=0)
    efficiency_curve: list[tuple[Frac, Frac]] = Field(min_length=3)
    mppt_count: int = Field(1, gt=0)
    temperature_derate: list[tuple[float, Frac]] | None = None
    source: str


class InverterUnit(Strict):
    array: str
    ref: Ref | None = None
    inline: InverterInline | None = None
    count: int = Field(gt=0)

    @model_validator(mode="after")
    def one_of(self):
        if (self.ref is None) == (self.inline is None):
            raise ValueError("give the inverter either as ref (library:...) or inline, not both or neither")
        return self


class Inverters(Strict):
    topology: Literal["central", "string"]
    units: list[InverterUnit] = Field(min_length=1)
    dc_ac_ratio: float = Field(gt=0)
    transformer_losses_pct: float = Field(1.0, ge=0, le=10)
    ac_collection_losses_pct: float = Field(1.0, ge=0, le=10)


# ------------------------------------------------------------------ storage

class Degradation(Strict):
    model: Literal["none", "linear", "calendar_plus_cycle"]
    calendar_pct_per_year: float = Field(0.0, ge=0, le=10)
    cycle_pct_per_1000_efc: float = Field(0.0, ge=0, le=20)
    end_of_life_capacity: Frac = 0.7


class SocLimits(Strict):
    min: Frac
    max: Frac

    @model_validator(mode="after")
    def ordered(self):
        if self.min >= self.max:
            raise ValueError("soc_limits.min must be below soc_limits.max")
        return self


class StorageThermal(Strict):
    hvac_load_kw_per_mwh: Num = "assumption:storage.hvac_load"
    derate_above_c: float | None = None


class StorageBlock(Strict):
    id: str
    coupling: Literal["ac", "dc"]
    grid_mode: Literal["grid_following", "grid_forming"] = "grid_following"
    power_mw: float = Field(gt=0)
    energy_mwh: float = Field(gt=0)
    chemistry: Literal["lfp", "nmc", "other"]
    round_trip_efficiency: FracOrRef
    soc_limits: SocLimits
    initial_soc: Frac = 0.5
    degradation: Degradation
    augmentation: Literal["none", "maintain_energy"] = "none"
    thermal: StorageThermal = StorageThermal()
    dc_bus: str | None = None

    @model_validator(mode="after")
    def dc_needs_bus(self):
        if self.coupling == "dc" and not self.dc_bus:
            raise ValueError("a dc-coupled storage block needs dc_bus: the id of the array it shares a bus with")
        return self


class Storage(Strict):
    blocks: list[StorageBlock] = Field(min_length=1)


# ------------------------------------------------------------------ desalination

class DesalBlock(Strict):
    id: str
    process: Literal["reverse_osmosis"]
    capacity_m3_per_day: float = Field(gt=0)
    specific_energy_kwh_per_m3: Num = "assumption:ro.specific_energy_seawater"
    min_load_fraction: Frac = 0.4
    ramp_pct_per_hour: float = Field(20.0, gt=0, le=100)
    water_storage_m3: float = Field(0.0, ge=0)
    water_demand: str = "profile:mew-water-seasonal"


class Desalination(Strict):
    blocks: list[DesalBlock] = Field(min_length=1)


# ------------------------------------------------------------------ controls

Strategy = Literal["pv_firming", "peak_shaving", "export_limit", "arbitrage", "reserve", "rule"]


class Poi(Strict):
    ramp_limit_pct_per_min: float | None = Field(None, gt=0, le=100)
    power_factor_range: tuple[float, float] | None = None


class Controls(Strict):
    strategy: Strategy
    parameters: dict = Field(default_factory=dict)
    poi: Poi = Poi()
    curtailment_priority: list[Literal["pv_clip", "storage", "pv_curtail", "desal"]] = ["pv_clip", "storage", "pv_curtail"]

    @model_validator(mode="after")
    def rule_needs_target(self):
        if self.strategy == "rule" and "function" not in self.parameters:
            raise ValueError("strategy 'rule' needs parameters.function, e.g. 'configs/rules/my_rule.py:dispatch'")
        return self


# ------------------------------------------------------------------ o&m

class CleaningSchedule(Strict):
    type: Literal["interval", "threshold", "calendar", "none"]
    interval_days: int | None = Field(None, gt=0, le=365)
    soiling_loss_pct: float | None = Field(None, gt=0, le=50)
    dates: list[date] | None = None

    @model_validator(mode="after")
    def by_type(self):
        need = {"interval": "interval_days", "threshold": "soiling_loss_pct", "calendar": "dates"}.get(self.type)
        if need and getattr(self, need) is None:
            raise ValueError(f"a '{self.type}' cleaning schedule needs {need}")
        return self


class Cleaning(Strict):
    method: Literal["robotic_dry", "manual_wet", "none"]
    schedule: CleaningSchedule
    effectiveness: FracOrRef = "assumption:cleaning.effectiveness"
    cost_usd_per_mwp_per_cleaning: Num = "assumption:cleaning.cost"


class Availability(Strict):
    plant: FracOrRef = "assumption:availability.plant"
    inverter: FracOrRef = "assumption:availability.inverter"
    storage: FracOrRef = "assumption:availability.storage"


class PvDegradation(Strict):
    pv_pct_per_year: Num = "assumption:degradation.pv_annual"
    pv_first_year_pct: Num = "assumption:degradation.pv_first_year"


class OM(Strict):
    availability: Availability = Availability()
    cleaning: Cleaning
    degradation: PvDegradation = PvDegradation()
    soiling_flat_pct: float | None = Field(None, ge=0, le=50)


# ------------------------------------------------------------------ economics

class Finance(Strict):
    structure: Literal["ppa", "merchant", "regulated"]
    wacc_real: Num
    debt_fraction: FracOrRef = 0.0
    debt_rate: Num | None = None
    tenor_years: int | None = Field(None, gt=0, le=40)
    tax_rate: FracOrRef = 0.0


class Revenue(Strict):
    ppa_price_fils_per_kwh: Num | None = None
    tariff: str | None = None
    escalation_pct: float = 0.0


class Economics(Strict):
    currency: Literal["KWD", "USD"] = "USD"
    base_year: int = Field(ge=2015, le=2050)
    life_years: int = Field(gt=0, le=50)
    capex: dict[str, Num]
    opex: dict[str, Num]
    finance: Finance
    revenue: Revenue


# ------------------------------------------------------------------ evaluation

class Evaluation(Strict):
    years: list[int] = Field(min_length=1)
    time_step: Literal["1h", "15min"] = "1h"
    system_context: str | None = None
    sensitivity: list[str] = Field(default_factory=list)
    allow_outside_modelled_range: bool = False


# ------------------------------------------------------------------ top level

class SourceRef(Strict):
    title: str
    url: str | None = None
    retrieved: date | None = None
    note: str | None = None


class PlantConfig(Strict):
    schema_: Literal["kuwait-plant/0.1"] = Field(alias="schema")
    id: Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9\-]*$")]
    name: str
    description: str = ""
    status: Literal["reference", "example", "user"] = "user"
    sources: list[SourceRef] = Field(default_factory=list)
    site: Site
    pv: PV | None = None
    inverters: Inverters | None = None
    storage: Storage | None = None
    desalination: Desalination | None = None
    controls: Controls
    om: OM
    economics: Economics
    evaluation: Evaluation

    @model_validator(mode="after")
    def cross(self):
        if self.pv and not self.inverters:
            raise ValueError("a plant with pv needs an inverters section")
        if not (self.pv or self.storage or self.desalination):
            raise ValueError("a plant needs at least one of pv, storage or desalination")
        if self.status == "reference" and not self.sources:
            raise ValueError("a reference configuration must list its sources")
        if self.site.soiling_source == "flat" and self.om.soiling_flat_pct is None:
            raise ValueError("site.soiling_source 'flat' needs om.soiling_flat_pct")
        ids = {a.id for a in self.pv.arrays} if self.pv else set()
        for u in (self.inverters.units if self.inverters else []):
            if u.array not in ids:
                raise ValueError(f"inverter unit refers to array '{u.array}', which is not in pv.arrays ({', '.join(sorted(ids))})")
        for b in (self.storage.blocks if self.storage else []):
            if b.dc_bus and b.dc_bus not in ids:
                raise ValueError(f"storage block '{b.id}' has dc_bus '{b.dc_bus}', which is not in pv.arrays")
        return self

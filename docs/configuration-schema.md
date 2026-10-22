# Plant configuration schema (v0.1)

A plant configuration is one YAML file describing a plant the way an engineer
specifies it. The toolkit evaluates it under Kuwaiti conditions. This document
fixes the schema before anything is built on it.

**Every number in the examples below is a placeholder showing the format. None
is an input, an assumption or a fact about a real plant.**

## Principles

1. **Physical description, not model settings.** The file says what the plant
   *is*: modules, inverters, rows, batteries, rules. How each engine models it is
   the engine's business. The same file feeds pvlib, PySAM and the PyPSA system
   model.
2. **Units in the key.** `rating_mw`, `pitch_m`, `capex_usd_per_kwdc`. No bare
   numbers whose unit has to be guessed.
3. **Every value is a value, a reference, or a labelled assumption.** A field
   either holds a number, points to a library entry (`module: library:jinko-tiger-neo-575`),
   or points to the assumptions file (`wacc: assumption:wacc.kuwait_ipp`). The
   evaluation report lists which kind each field was.
4. **Explicit over defaulted.** Defaults exist, but a run report lists every
   default applied, so a reviewer sees what the user did not choose.
5. **Kuwaiti conditions are inputs, not configuration.** Weather, soiling,
   tariffs and fleet come from `inputs/`. A configuration names a site; it does
   not carry its own climate.
6. **Versioned.** `schema: kuwait-plant/0.1`. A breaking change bumps the version,
   and old files keep validating against the version they declare.

## Top level

```yaml
schema: kuwait-plant/0.1
id: example-pv-storage-a             # slug; unique in a library
name: Example PV and storage plant A
description: >-
  Free text. For a reference configuration, how it reproduces the published plan.
sources:                              # where the configuration comes from
  - {title: "...", url: "...", retrieved: 2026-10-21, note: "capacity and area"}
status: reference | example | user   # reference = reproduces a real plan, with sources

site: {...}
pv: {...}                             # optional; a plant may be storage-only
inverters: {...}
storage: {...}                        # optional
desalination: {...}                   # optional
controls: {...}
om: {...}
economics: {...}
evaluation: {...}                     # what to compute, not how the plant is built
```

## site

```yaml
site:
  location: {lat: 29.0, lon: 47.5}       # WGS84, decimal degrees (placeholder)
  zone: jahra                            # governorate zone in the system model; derived from location if omitted
  land_area_ha: 1200
  terrain:
    slope_deg: 0.5
    slope_azimuth_deg: 180
    albedo: assumption:albedo.desert_gravel   # or a number, or monthly list of 12
  grid_connection:
    point: example-400kv                 # name only; no coordinates of grid assets are published
    voltage_kv: 400
    export_limit_mw: 1000                # at the point of interconnection
    import_limit_mw: 20                  # auxiliary supply
  weather: era5:2013-2023                # source and years; resolved from inputs/
  soiling_source: kuwait-rates           # kuwait-rates | flat (flat needs om.soiling_flat_pct)
                                         # kuwait-rates: monthly Kuwaiti soiling rates (assumptions file)
                                         # with ERA5 rain cleaning and the om.cleaning schedule
```

## pv

A plant has one or more **arrays**. An array is one homogeneous block: one
module type, one mounting, one string design. Big plants with mixed technology
are several arrays.

```yaml
pv:
  arrays:
    - id: a1
      dc_capacity_mwp: 500                  # checked against modules × strings
      module:
        ref: library:generic-topcon-bifacial-580
        # or inline:
        # stc_power_w: 580
        # technology: mono-c-Si-TOPCon
        # vmp_v / imp_a / voc_v / isc_a
        # temp_coeff_pmax_pct_per_c: -0.29
        # bifaciality: 0.80
        # area_m2: 2.58                     # gives the efficiency used by the thermal model
      mounting:
        type: single_axis                   # fixed | single_axis
        # fixed:
        #   tilt_deg: 25
        #   azimuth_deg: 180
        # single_axis:
        axis_azimuth_deg: 180               # N-S axis
        max_angle_deg: 60
        backtracking: true
        stow:                               # wind or dust stow
          wind_speed_m_s: 18
          angle_deg: 0
      layout:
        gcr: 0.33                           # or pitch_m; one is derived from the other
        module_height_m: 1.5                # clearance, for bifacial rear irradiance
        collector_width_m: 2.4              # table width across the slope; default from the assumptions file
        modules_per_string: 28
        strings: 30860
```

## inverters

```yaml
inverters:
  topology: central                          # central | string
  units:
    - array: a1
      ref: library:generic-central-4400kva
      count: 100
      # or inline:
      # ac_rating_kva: 4400
      # efficiency: cec | curve
      # curve: [[0.1, 0.962], [0.2, 0.978], ...]   # fraction of rating, efficiency
      # mppt_count: 1
      # temperature_derate: [[25, 1.0], [45, 0.95], [50, 0.90]]   # ambient °C, fraction of rating
  dc_ac_ratio: 1.20                          # checked against arrays and units; mismatch is an error
  transformer_losses_pct: 1.0
  ac_collection_losses_pct: 0.8
```

## storage

```yaml
storage:
  blocks:
    - id: b1
      coupling: ac                             # ac | dc
      grid_mode: grid_following                # grid_following | grid_forming
      power_mw: 250                            # at the point of connection
      energy_mwh: 1000                         # usable at beginning of life
      chemistry: lfp                           # lfp | nmc | other (then inline parameters)
      round_trip_efficiency: 0.86              # AC-AC at the POC, beginning of life
      soc_limits: {min: 0.05, max: 0.95}
      initial_soc: 0.5
      degradation:
        model: calendar_plus_cycle            # none | linear | calendar_plus_cycle
        calendar_pct_per_year: 1.0
        cycle_pct_per_1000_efc: 2.0
        end_of_life_capacity: 0.70
      augmentation:                            # optional
        policy: maintain_energy                # none | maintain_energy
      thermal:
        hvac_load_kw_per_mwh: 2.0              # auxiliary load, drawn every hour
      dc_bus: a1                               # dc-coupled only: which array
```

## desalination

```yaml
desalination:
  blocks:
    - id: ro1
      process: reverse_osmosis                  # reverse_osmosis | (thermal processes are system-level, not plant-level)
      capacity_m3_per_day: 100000
      specific_energy_kwh_per_m3: assumption:ro.specific_energy_seawater
      min_load_fraction: 0.4
      ramp_pct_per_hour: 20
      water_storage_m3: 300000                  # product water storage that lets RO follow solar
      water_demand: profile:mew-seasonal         # what the stored water must meet
```

## controls

Dispatch is a first-class choice. Exactly one strategy, with its own
parameters; strategies are a closed list plus a user rule.

```yaml
controls:
  strategy: pv_firming
  # pv_firming:        hold a committed export profile; parameters: profile, tolerance_pct
  # peak_shaving:      reduce the system's net peak; parameters: window, target
  # export_limit:      store what would be clipped at the POC
  # arbitrage:         charge/discharge against a tariff in economics.tariff
  # reserve:           hold headroom; parameters: reserve_mw, product
  # rule:              python: configs/rules/my_rule.py:dispatch  (a user function, sandboxed signature)
  parameters:
    committed_profile: flat_daytime          # named profile or a file
    tolerance_pct: 5
  poi:
    ramp_limit_pct_per_min: 10               # of export limit
    power_factor_range: [0.95, 0.95]
  curtailment:
    priority: [pv_clip, storage, pv_curtail] # order applied when the POI binds
```

## om

```yaml
om:
  availability:
    plant: 0.99
    inverter: 0.995
    storage: 0.98
  cleaning:
    method: robotic_dry                      # robotic_dry | manual_wet | none
    schedule:
      type: interval                          # interval | threshold | calendar
      interval_days: 7
      # threshold: {soiling_loss_pct: 3}
      # calendar: [2026-03-01, ...]
    effectiveness: 0.95                       # fraction of soiling removed per cleaning
    cost_usd_per_mwp_per_cleaning: assumption:cleaning.robotic_dry_cost
  degradation:
    pv_pct_per_year: 0.4
    pv_first_year_pct: 1.0
```

## economics

```yaml
economics:
  currency: KWD                               # KWD | USD; reported in both
  base_year: 2026
  life_years: 25
  capex:                                      # by component; each line a value or an assumption reference
    modules_usd_per_wp: 0.11
    trackers_usd_per_wp: 0.07
    inverters_usd_per_kwac: 30
    bos_usd_per_wp: 0.12
    storage_usd_per_kwh: 180
    storage_usd_per_kw: 60
    grid_connection_usd: 15000000
    development_pct_of_capex: 3
  opex:
    fixed_usd_per_kwdc_year: 7
    storage_fixed_usd_per_kw_year: 6
    insurance_pct_of_capex: 0.3
  finance:
    structure: ppa                            # ppa | merchant | regulated
    wacc_real: assumption:wacc.kuwait_ipp
    debt_fraction: 0.7
    debt_rate: 0.055
    tenor_years: 20
    tax_rate: 0.0
  revenue:
    ppa_price_fils_per_kwh: 4.5               # or tariff: file / named Kuwaiti tariff
    escalation_pct: 0
```

## evaluation

```yaml
evaluation:
  years: [2019, 2023]                        # weather years run; results reported per year and on average
  time_step: 1h                              # 1h | 15min (15 min only where weather allows)
  system_context: base-2023                  # system scenario for grid interaction, or none
  sensitivity: [wacc, capex.storage_usd_per_kwh, soiling]   # tornado on these
```

## Validation

The validator runs before any engine:

- **Schema:** types, required fields, units. For example, "`site.location.lat` must be
  between 28.5 and 30.1 (Kuwait)".
- **Consistency:** `dc_capacity_mwp` against modules × strings; `dc_ac_ratio` against
  arrays and inverters; storage `energy_mwh / power_mw` between 0.25 and 12 h.
- **Modelled range:** where an input is legal but outside what the methods are
  validated for, the message says so. For example, "DC to AC ratio above 2.0 is
  outside the modelled range".
- **Provenance:** for `status: reference`, every number must have a source or an
  assumption reference.

Errors read as sentences naming the field, the value and the allowed range,
never a stack trace. Warnings (outside the validated range) do not stop a run but
appear at the top of every result.

## Library

`library/` holds named modules, inverters and battery products as small YAML
files, each with its datasheet source. Generic entries (for example
`generic-topcon-bifacial-580`) are labelled generic and carry the source of their
parameters. No manufacturer is shown on the site as an endorsement.

## What this schema leaves out on purpose

- **Electrical design below the inverter.** Cable sizing, string combiner layouts
  and protection don't change the questions this toolkit answers; the losses are
  parameters instead.
- **Cell temperature model choice.** The PVsyst model is used for every array, with
  U values from the assumptions file chosen by mounting type (fixed or tracker).
- **Concentrated solar power and wind.** Not part of v0.1. Shagaya's CSP and wind
  blocks are represented by their reported output, not modelled.
- **Thermal plant configuration.** Gas and steam units belong to the system
  model's fleet, which comes from the dataset, not from user files.

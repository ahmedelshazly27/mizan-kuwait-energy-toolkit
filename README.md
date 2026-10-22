# Kuwait Energy Toolkit

A plant configuration workbench for Kuwait. You describe a real plant component by
component (site, PV arrays, inverters, storage, desalination, controls, O&M,
economics) in a YAML file, and the toolkit models how that configuration performs
under Kuwaiti conditions, then what it does to the national system.

Page: <https://mizan-energy.com/research/kuwait-energy-toolkit/> ·
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ahmedelshazly27/mizan-kuwait-energy-toolkit/main?labpath=notebooks)

## Quick start

```sh
git clone https://github.com/ahmedelshazly27/mizan-kuwait-energy-toolkit && cd mizan-kuwait-energy-toolkit
uv sync --extra pv --extra econ --extra system
uv run kwtk validate configs/examples/*.yaml
uv run kwtk compare configs/examples/shagaya-scale-pv-tracker.yaml configs/examples/shagaya-scale-pv-storage-peak-shaving.yaml
```

Everything runs offline after the clone: the measured data, ERA5 weather for every
0.25° cell over Kuwait (2013–2024) and the demand reconstruction are in the
repository. No account, key or network is needed.

## What it does (v0.1)

For one plant file, `kwtk evaluate`:

1. **validates** it against the schema (`kuwait-plant/0.1`) and the modelled ranges, in
   sentences;
2. **resolves every input** to a number with its origin (the configuration, the
   library, or `inputs/assumptions.yaml` with its status and source). It refuses to run on
   an open assumption, and lists every unverified one in the result;
3. **simulates PV hour by hour** with pvlib over the chosen ERA5 weather years. It covers
   row-to-row shading and rear-side irradiance (infinite sheds), tracking with
   backtracking and wind stow, reflection, Kuwaiti soiling with rain and the cleaning
   schedule, cell temperature, DC losses, the inverter efficiency curve, clipping, AC
   losses and outages, all recorded as a loss waterfall;
4. **dispatches storage** with one of six strategies (export limit, PV firming, peak
   shaving, arbitrage, reserve, or a user rule), and counts curtailment at the
   connection and auxiliary loads;
5. **couples an RO plant** behind the connection to the PV surplus, with water demand
   following Kuwait's measured monthly seasonality;
6. **costs it** with NREL PySAM (Single Owner, lifetime hourly generation, explicit
   degradation). The result includes LCOE and a break-even PPA, checked against an
   independent capital-recovery calculation;
7. **places it in Kuwait's system**: a three-zone PyPSA dispatch (HiGHS) of every unit
   in MEW's 2023 yearbook, with measured fuel cost per station and must-run floors for
   water production. It reports fuel and fuel cost avoided, which stations the plant
   displaces, and curtailment by the system.

`kwtk compare A.yaml B.yaml ...` puts several plants side by side.

Read before using the numbers:

- [docs/decisions.md](docs/decisions.md): every modelling judgement (D1–D9).
- [docs/demand-reconstruction.md](docs/demand-reconstruction.md): the hourly demand
  model and its known defects.
- [inputs/assumptions.yaml](inputs/assumptions.yaml) and
  [docs/assumption-sources.md](docs/assumption-sources.md): every assumed number.
  Many sources could not be opened from the build environment and are marked
  `unverified`.
- [configs/reference/README.md](configs/reference/README.md): why no reference plant
  is complete yet.

## Notebooks

| | |
|---|---|
| [1. Quickstart](notebooks/01-quickstart.ipynb) | validate, evaluate, inputs and their origins |
| [2. The Kuwaiti inputs](notebooks/02-kuwaiti-inputs.ipynb) | dataset snapshot, fleet, peaks, conflicts, assumptions |
| [3. Demand reconstruction](notebooks/03-demand-reconstruction.ipynb) | the held-out check against MEW's peak-day curves |
| [4. Weather and resource](notebooks/04-weather.ipynb) | the ERA5 grid, irradiance across Kuwait |
| [5. PV yield and losses](notebooks/05-pv-losses.ipynb) | loss waterfall; the Shagaya Phase I approximation |
| [6. Storage and controls](notebooks/06-storage-and-controls.ipynb) | export limit vs peak shaving |
| [7. Economics](notebooks/07-economics.ipynb) | what the capex source does to LCOE |
| [8. System and water](notebooks/08-system-and-water.ipynb) | fuel avoided, displaced stations, RO coupling |

Each opens in Colab from the badge at its top. `uv run python scripts/make_notebooks.py`
rebuilds and re-executes them.

## Network: zonal, deliberately

The system model represents Kuwait as governorate zones joined by aggregate transfer
capacities, not as a nodal network. Zonal detail is enough for what this toolkit
answers (what a plant does to dispatch, fuel burn and the evening ramp), and it avoids
publishing infrastructure detail that is not ours to publish. No transmission is
traced from imagery and no new grid geodata is created; where line or substation data
is used, it is what OpenStreetMap and PyPSA-Earth already publish, aggregated to zones.

## Credits and licences

Built on [pvlib](https://github.com/pvlib/pvlib-python) (BSD-3),
[NREL SAM / PySAM](https://github.com/NREL/pysam) (BSD-3),
[PyPSA](https://github.com/PyPSA/PyPSA) (MIT),
[PyPSA-Earth](https://github.com/pypsa-meets-earth/pypsa-earth) (code AGPL-3.0-or-later,
data CC BY 4.0 / CC0; used as a separate workflow, none of its code is copied here),
[atlite](https://github.com/PyPSA/atlite) (MIT) and, optionally,
[WaterTAP](https://github.com/watertap-org/watertap) (BSD-3). Their licences apply to
their code. Our code is MIT ([LICENSE](LICENSE)); our inputs and documentation are
CC BY 4.0 ([LICENSE-DATA](LICENSE-DATA)). Cite with [CITATION.cff](CITATION.cff).

Data in `inputs/`: the Kuwait Electricity Open Dataset (CC BY 4.0); ERA5
temperature, "generated using Copernicus Climate Change Service information"
(Hersbach et al., ERA5 hourly time-series data on single levels from 1940 to
present, C3S Climate Data Store; Copernicus licence), neither the European
Commission nor ECMWF is responsible for any use of it; WorldPop 2020 constrained,
UN-adjusted population (CC BY 4.0, worldpop.org).

Mizan builds and maintains this. <https://mizan-energy.com>

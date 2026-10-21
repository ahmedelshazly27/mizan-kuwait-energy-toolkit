# Kuwait Energy Toolkit

A plant configuration workbench for Kuwait. You describe a real plant component by
component (site, PV arrays, inverters, storage, desalination, controls, O&M,
economics) in a YAML file, and the toolkit models how that configuration performs
under Kuwaiti conditions, then what it does to the national system.

**Status: early.** What exists today:

- the configuration schema (`kuwait-plant/0.1`) with a validator that reports
  problems as sentences: `kwtk validate configs/examples/*.yaml`
- the assumptions file, with every entry still open until it is sourced
- the measured inputs: a snapshot of the Kuwait Electricity Open Dataset in
  `inputs/dataset/`, unchanged and pinned to a dataset commit by `MANIFEST.yaml`
  (`kwtk inputs verify`; refresh with `kwtk inputs import --dataset PATH`). Loaders in
  `kwtk.inputs.dataset` return the dataset's own rows; every series call names its
  source, and open dataset conflicts are reported, never resolved. The fleet is the
  unit list from the MEW yearbook station pages (2023 edition: 117 units, 20,250 MW)
- a gap analysis of PyPSA-Earth's Kuwait defaults (in the Mizan-Energy repository,
  `research-src/energy-toolkit/GAP_ANALYSIS.md`)

The hourly demand reconstruction, weather and resource inputs, the evaluation engines
(pvlib, PySAM, PyPSA, water), notebooks and validation come next, in that order.

## Layout

```
inputs/          canonical Kuwait inputs, imported from the electricity dataset; assumptions.yaml
plant/           configuration model and evaluation engine
engines/         pvlib (PV), pysam (techno-economics), pypsa (system), water (power-water coupling)
configs/         plant configurations: reference/ (real plans, with sources), examples/
library/         modules, inverters and batteries, each with its datasheet source
src/kwtk/        the package; config/ holds the schema and validator
notebooks/       end-to-end examples, each under ten minutes on free Colab
```

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

Mizan builds and maintains this. <https://mizan-energy.com>

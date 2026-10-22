# Reference configurations

A reference configuration reproduces a real plant from published facts, every number
with a source. None is complete yet, because the build environment could not open the
documents that publish the remaining facts. What is known, from
[docs/plant-and-water-sources.md](../../docs/plant-and-water-sources.md):

| Plant | Verified (MEW/CSB documents) | Reported, not verified | Missing |
|---|---|---|---|
| Shagaya Phase I PV | 10 MW, in service 29/11/2016 (MEW yearbook 2023 p50); park gross generation 2021-2024 | 34,560 Solar Frontier SF160-S (thin film) + 17,820 Jinko JKM315PP-72 (poly), about 11.14 MWp, fixed mounting, SMA Sunny Central inverters; first-year yield 1,805/1,810 kWh/kWp, PR 80 % (Al-Rasheedi et al., RSER 133, 2020) | tilt, azimuth, row spacing, string layout, inverter model and count |
| Shagaya Phase III Zone 1 | none | 1,100 MW PV, 30-year PPA via KAPP, 400 kV connection; consortium selection reported | everything technical, tariff |
| Shagaya Phase III Zone 2 | none | 500 MW, bids due July 2026 | everything |

Until those are verified, `configs/examples/shagaya-pv1-approximation.yaml` approximates
Phase I PV with the reported facts and labelled design choices, and the
`shagaya-scale-*` examples show plants at the Zone 1 scale.

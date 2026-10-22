# Modelling decisions

Every judgement call the toolkit makes, who made it, and what it rules out. A
decision changes only by a new entry here.

## D1 — Hourly demand: what is reconstructed (2026-10-21, owner)

**Gross system load**, as MEW prints "Kuwait System Load": station output plus
GCC interchange. It is the basis of every printed peak, the four peak-day
half-hourly curves (yearbooks 2020–2023) and the July 2025 daily peak and minimum
table, so the reconstruction can be checked against them. Station use and
desalination use are reported beside it, never subtracted inside it.

Rejected: net sent-out load (no printed peak or curve on that basis to check
against).

## D2 — Hourly demand: method (2026-10-21, owner)

**Temperature-driven, constrained.** Hourly load is a base diurnal shape plus a
cooling term on ERA5 2 m temperature, with the lag fitted. The model is fitted to
daily measurements only (July 2025 daily peak and minimum with their times;
May–June 2024 and 2025 daily maximum and minimum; daily generation May–July 2025),
then scaled so each month sums to its printed energy and each year reaches its
printed peak. The four peak-day curves are not used in fitting; they are the
validation test, and the scores are published with the series. The output is
labelled a reconstruction everywhere it appears.

Rejected: scaling the measured peak-day shape by monthly energy (no weather, so
no heatwaves or day-to-day variation); PyPSA-Earth's demand (see the gap
analysis: energy equals gross generation, peak 12–14% low, peak hour 17:00
against MEW's 13:30–14:30).

## D3 — Hourly demand: October–April (2026-10-21, owner)

No sub-daily load is published for October–April. The same model is used; in
those months the cooling term is small and the **base diurnal shape outside
summer is an explicit open assumption** (`demand.base_shape_nonsummer` in
inputs/assumptions.yaml), flagged in every output that uses those hours, until
MEW hourly data is obtained. Hourly data for research has been supplied by MEW on
request (papers cited in docs/demand-reconstruction.md); a request is the way to
close this assumption.

## D4 — Monthly energy source for the demand reconstruction (2026-10-22, Claude, delegated by the owner)

**CSB Environment Statistics for 2013–2024; MEW Monthly Statistics Books for
2025.** CSB is the only series covering every month from 2013 to 2024. Where the
MEW yearbooks print the same quantity (national gross generation by month,
2020–2023), the two agree exactly in all 48 months. The dataset's open conflicts
are all at plant level or in annual history tables, so this choice changes no
hourly value. A test (`tests/test_demand.py`) fails if a future dataset build
breaks that agreement, and the decision must then be revisited.

## D5 — Request hourly load data from MEW (2026-10-22, Claude, delegated by the owner)

**Yes.** One year of hourly system load would replace the two weakest parts of
the reconstruction with measurements: the night shape and October–April. It would
also test the peak overshoot. The request is drafted in
[docs/mew-data-request.md](mew-data-request.md) for the owner to send. Until data
arrives, D3's proxy stands.

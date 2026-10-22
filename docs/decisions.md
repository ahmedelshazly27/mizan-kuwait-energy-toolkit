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

## D6 — Assumptions whose sources could not be opened (2026-10-22, Claude, delegated)

The build environment's network blocks most publishers, so many cited values were
seen only in search summaries. Such values enter `inputs/assumptions.yaml` with
status **unverified**, their full citation and the note that the document was not
opened. They are used, and every result lists them (`unverified_inputs`) so a reader
knows which numbers to check. Values with no citable source stay `open`, and
evaluation refuses to run on them.

## D7 — Zones and their load shares (2026-10-22, Claude, delegated)

Three zones by governorate (north: Jahra; central: Capital, Hawalli, Farwaniya;
south: Ahmadi, Mubarak Al-Kabeer). Load is split by MEW's supply-area loads at the
2023 peak (yearbook p86), each area assigned by reading its districts on the page
image (inputs/zones.yaml lists every row). The stations' own load is split by
station capacity. The peak-day shares apply to every hour. Interfaces are PyPSA-Earth's
line ratings summed across zone boundaries (5.5, 15.5 and 13.2 GVA), standard line
types rather than MEW ratings. Rejected: six governorate zones (two have no
transmission buses in the network), and population shares (the MEW table measures
load directly).

## D8 — Merit order from measured average fuel cost (2026-10-22, Claude, delegated)

Each station's marginal cost is its 2023 fuel cost over its 2023 gross generation
(MEW yearbook p188 and the generation history), and fuel avoided uses its fuel
energy per MWh. These are averages, and at cogeneration stations they include the
fuel that raises steam for distillation, so they overstate the electricity-only cost
of those stations. No published source splits fuel between power and water by
station.

## D9 — Power-water coupling as a must-run floor (2026-10-22, Claude, delegated)

A station with thermal distillation must generate, every hour, at least its lowest
monthly average output in 2023: the output it held while producing water. That
floor (about 5.6 GW in total) is what makes solar curtailment appear on mild days.
RO plants are electricity load inside the system load. Rejected: a steam-per-water
coupling, because no published figure gives steam or electricity per unit of
distilled water by station.

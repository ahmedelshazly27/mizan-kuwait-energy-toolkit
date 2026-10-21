# Hourly demand: a reconstruction

`inputs/demand/kuwait-gross-load-reconstructed.csv.gz` is hourly gross system load
for Kuwait, January 2013 – December 2024 plus May–July 2025, in Kuwait local time
(UTC+03:00). **It is a model, not a measurement.** No hourly Kuwaiti load is
published. The series reproduces every printed monthly energy and annual peak
exactly. Everything between those points comes from the model below. Decisions:
[D1–D3](decisions.md). Code: `src/kwtk/inputs/demand.py`. Rebuild: `kwtk inputs demand`.

## What it is built from

| Input | Source (all in the dataset snapshot unless noted) | Used for |
|---|---|---|
| Monthly gross generation, 2013–2024 | CSB Environment Statistics workbooks (newest edition per month) | monthly energy, exact |
| Monthly gross generation, May–July 2025 | MEW Monthly Statistics Books | monthly energy, exact |
| Annual peak load, 2013–2023 | MEW yearbooks (newest edition printing the year) | annual peak, exact |
| Daily peak and minimum load with their times, July 2025 | MEW Monthly Statistics Book, July 2025 | fitting |
| Daily maximum and minimum load, May–June 2024 and 2025 | MEW Monthly Statistics Books, May and June 2025 | fitting |
| Daily gross generation, May–July 2025 | MEW Monthly Statistics Books | fitting |
| Half-hourly load on the yearly peak day, 2020–2023 | MEW yearbooks 2020–2023 | **validation only** |
| Hourly 2 m temperature, population-weighted | ERA5 (`reanalysis-era5-single-levels-timeseries`, Copernicus Climate Change Service) over the 15 most populated 0.25° cells (98.8% of the population), weighted by WorldPop 2020; `inputs/weather/` | the cooling term |

## Model

    L(t) = a_m [1 + s(h) + b max(0, Te(t) − T0)] (1 + g weekend(t))
    Te(t) = φ T(t) + (1 − φ) EWMA_τ(T)(t)

- s(h): base diurnal shape, two harmonics.
- b, T0: cooling response and its threshold.
- φ, τ: how much of the temperature acts at once, and with what lag.
- g: the Friday/Saturday effect.
- a_m: set per month so the month sums to its printed energy.

The nine shape parameters are fitted by least squares on relative errors in daily
maximum, minimum and energy. Where a time is printed, the error at that time also
counts, so the model's load at the printed peak time must equal the printed peak.

Each year with a printed peak is then stretched about its monthly means,
`L' = M_m + k (L − M_m)`, with one k per year solved so the year's maximum equals the
printed peak. Every month keeps its energy.

## Fit and validation

Fitted values (from the JSON beside the series): T0 = 28.1 °C, b = 0.046 per K,
φ = 0.50, τ = 23 h, weekend −1.1%. Errors on the fit data (relative RMSE): daily
maximum 3.5%, minimum 3.6%, energy 1.8%, load at the printed peak time 3.2%, load
at the printed minimum time 1.4%.

**Held out**, the printed curves on the four yearly peak days:

| Day | MAPE | Worst hour | Peak hour printed / model | Minimum hour printed / model |
|---|---|---|---|---|
| 30 Jul 2020 | 4.9% | 12.8% | 15 / 14 | 6 / 7 |
| 28 Jul 2021 | 3.8% | 9.7% | 15 / 15 | 6 / 7 |
| 9 Aug 2022 | 3.8% | 10.7% | 14 / 15 | 6 / 7 |
| 2 Aug 2023 | 4.0% | 10.2% | 14 / 15 | 6 / 7 |

(Printed curve values are instants on the half hour. The comparison uses the full
hours.)

### How the model form was chosen

The first version had a single lagged temperature and no printed times in the fit.
It put the peak at 17:00 and the minimum at midnight, the same timing error found in
PyPSA-Earth's demand. Adding the printed times fixed the peak hour but not the
night. Seven forms were then compared: two to four harmonics, additive or
multiplicative cooling, with and without the blend φ. They were ranked by
cross-validation **within the fit data**: fit on 2024 and May–June 2025, score
July 2025. The simplest form within 0.002 of the best CV error was chosen (2
harmonics, additive, with the blend: CV 2.8%, against 7.0% for the first version).
The held-out curves were printed for every form during that comparison. They were
not the selection criterion, but they were seen, so the hold-out is not fully blind.

## Known defects

1. **The night is too high.** On the peak days the model holds about 14,800 MW
   at 03:00 where MEW prints about 13,500, and its minimum comes an hour late.
   The pre-dawn fall in load is behavioural, not thermal: ERA5 cools less than 2 °C
   overnight. The base shape can't fully reproduce it.
2. **The peak stretch is large.** Unstretched, the model's annual peaks are
   4–10% above the printed ones for 2013–2023, so k comes out at 0.56–0.82. That
   compresses every intra-month swing in those years by 18–44%. The model is
   calibrated on 2024–2025 days. Either the load's response to heat has changed, or
   the 2024–2025 loads are served load rather than demand: scheduled power cuts were
   reported in Kuwait in summer 2024. Not resolved.
3. **October–April shape is an assumption.** No sub-daily load is published for
   those months. Their hours use the base shape fitted to summer days
   (`demand.base_shape_nonsummer`, status `proxy`). It has a 03:00 maximum that is
   probably an artefact. Outputs using those hours are flagged.
4. **2024 and 2025 have no printed annual peak** (no 2024 yearbook; 2025 is partial),
   so they are not stretched. 2025 covers May–July only.
5. Not modelled: Ramadan, public holidays, GCC interchange (in system load, but not
   published monthly; 20 MW at the 2022 peak). ERA5 runs cooler than MEW's printed
   temperatures at the peak (ERA5 population-weighted maximum 47.0 °C; MEW prints
   up to 50 °C). The fit absorbs a uniform bias, but not one that varies.

## How to close the gaps

MEW's National Control Center has supplied hourly load to researchers on request.
One study of COVID-19's effect on Kuwait's grid used hourly MEW data up to April
2020, and a 2021 *Electricity Journal* paper hosted by KISR used hourly load for
2009 and 2019. A year of hourly MEW data would replace defects 1 and 3 with
measurements and would test defect 2.

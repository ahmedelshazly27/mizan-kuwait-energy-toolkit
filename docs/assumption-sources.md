# Cited assumptions for a Kuwait solar + storage plant evaluation toolkit

Research date: 2026-10-22. Prepared for the `mizan-kuwait-electricity-data` toolkit.

## How to read this file

Each value has a **verification status**:

- **VERIFIED**: I read the primary source text or data file myself (downloaded and parsed). Page, table or field references are exact.
- **SNIPPET ONLY, NOT VERIFIED**: the value came from a web-search result summary or snippet. I could not open the source because of network blocks (see the end of this file). Check it against the source before using it in the toolkit.
- **DERIVED**: simple arithmetic I did on values from a verified source. The source does not state the derived number. It is labelled as derived wherever it appears.

Kuwait-specificity tags: `kuwait`, `gcc-desert` (GCC or other Middle East or North African desert), `generic`.

I found no value that I could verify as Kuwait-measured for albedo, soiling rate, module temperature coefficients, degradation, or SWRO SEC. For those items the file lists the closest proxies and says "no source found (verified)".

---

## Summary table

| # | Item | Best value found | Unit | Source (short) | Specificity | Status |
|---|---|---|---|---|---|---|
| 1 | Ground albedo, Kuwaiti desert | **No Kuwait measurement found.** Proxies: 0.30 for sand with gravel (Saudi, TÜV Rheinland site, 12.7 % bifacial gain); ~0.30 assumed for a central-Saudi tracker; ">40 %" for Qatar desert sand (QEERI albedometer network) | fraction | IEA-PVPS T13-14:2021 (bifacial report) as summarised; PV-Tech article on QEERI | gcc-desert | SNIPPET ONLY |
| 2a | PVsyst Uc/Uv, free-standing (default) | Uc = 29.0, Uv = 0.0 (insulated 15.0/0; semi-integrated 20.0/0) | W/m²K; W/m²K/(m/s) | pvlib `temperature.py` citing "PVsyst 7 Help" | generic | VERIFIED (pvlib); PVsyst help itself blocked |
| 2b | Faiman U0/U1 (Negev desert fit) | U0 = 25.0, U1 = 6.84 (7 c-Si modules, Negev desert, open rack, 30.9° tilt) | W/m²K; W·s/m³K | Faiman 2008, Prog. Photovolt. 16(4):307-315, via pvlib docstring | gcc-desert (Middle East desert) | VERIFIED (pvlib docstring); paper itself blocked |
| 2c | Tracker-specific Uc | No source found that gives a tracker-specific PVsyst default; pvlib says "freestanding" covers "fixed racking or single axis trackers" | n/a | pvlib | generic | VERIFIED (pvlib text) |
| 3a | Soiling rate, Kuwait | **No verified %/day for Kuwait.** Kuwait proxies: 17 % loss after 6 days (Kuwait City, early 1980s study); monthly-cleaning losses vs daily cleaning of 15.07 % (Apr), 13.74 % (May), 10.685 % (Oct), 8.742 % (Dec); modelled annual loss ~25 % without cleaning (100 MW, Al Wafra) | % | various, see §3 | kuwait | SNIPPET ONLY |
| 3b | Soiling rate, Gulf proxy | 0.49 %/day average (Doha, 22° tilt, rain excluded); range ~0.3–0.5 %/day | %/day | QEERI Solar Test Facility 5-year report; Aïssa et al. 2023 Energies 16:5224 | gcc-desert | SNIPPET ONLY |
| 3c | Cleaning effectiveness, robotic dry vs wet | **No source found** with a quantified fraction removed in a desert comparison. Qualitative: nylon-brush cleaning "not as high as cleaning using water and delicate wipers" (Doha) | n/a | Energy Convers. Manag. 2019 (Doha drone-retrofit study) | gcc-desert | SNIPPET ONLY |
| 3d | Cleaning cost | Manual ≈ 0.19 USD/kW per cycle (Saudi plants); 1.80 SAR/kWp per cleaning event (Arar base case); 0.0183–0.0383 USD per panel per cycle (Middle East scheduling study) | various | see §3 | gcc-desert | SNIPPET ONLY |
| 4a | BESS RTE (AC-AC, modelling assumption) | 0.85 (all scenarios, 2023–2060) | fraction | NREL ATB 2025 data file, citing Cole, Ramasamy & Turan 2025 | generic | VERIFIED (ATB data) |
| 4b | BESS RTE (measured fleet) | 82 % (US utility-scale battery fleet, 2019 monthly average) | % | EIA Today in Energy, 12 Feb 2021 | generic | VERIFIED |
| 4c | BESS HVAC / auxiliary load in hot climate | **No peer-reviewed hot-climate value found.** Non-peer-reviewed: 8–13 kW per 5 MWh container, 12–14 kW at 45–50 °C ambient; 1–3 % of annual throughput | kW per container; % | Energy Central post; TWAICE glossary | generic | SNIPPET ONLY |
| 5 | SWRO SEC, Arabian Gulf | **No Kuwait plant-level value found.** Gulf: 3.6–5.4 kWh/m³ (DAF + two-pass RO plants, Gulf seawater); 4–6 kWh/m³ with ERDs (older); Kuwait modelling assumption 5.5 kWh/m³. Note: Az-Zour North Phase 1 is MED-TVC, **not RO**. | kWh/m³ | Desalination 2023 pilot study; Qatar pilot-plant paper; see §5 | gcc-desert / kuwait | SNIPPET ONLY |
| 6a | PV system availability | P50 = 0.99, P90 = 0.95 (1,128 US C&I and utility systems) | fraction | NREL PV Fleet Performance Data Initiative slides (OSTI 2323270) | generic | SNIPPET ONLY |
| 6b | BESS availability (contracted) | 95–98 % typical guarantees; LTSA tiers 95/96/97 %; 97–99 % system, ≥ 98 % BESS in some contracts | % | Energy-Storage.News; BESS.courses | generic | SNIPPET ONLY (trade press) |
| 7a | Degradation, generic | Median 0.5 %/yr (nearly 2,000 rates); mean 0.8 %/yr | %/yr | Jordan & Kurtz 2013, Prog. Photovolt. 21(1):12-29 | generic | SNIPPET ONLY |
| 7b | Degradation, fleet | Median −0.75 %/yr system PLR | %/yr | Jordan et al. 2022, Prog. Photovolt. 30:1166-1175 | generic | SNIPPET ONLY |
| 7c | Degradation, Gulf desert | DEWA OTF (Dubai), 96 modules: median ~0.21 %/yr mono, ~0.49 %/yr poly; hot-desert >10-yr-old modules 1.5–2.65 %/yr (review) | %/yr | DEWA R&D papers | gcc-desert | SNIPPET ONLY |
| 7d | First-year (LID/LeTID) | Initial ~2 % LID for standard PERC, plus 6–8 % LeTID over 3 years in early PERC (Cyprus/Germany); Qatar 3-yr test: mc-PERC and cast-mono PERC had higher first-year loss than mono-PERC and TOPCon | % | Kersten et al.; Solar Energy 2025 (Qatar PERC/TOPCon/SHJ) | generic / gcc-desert | SNIPPET ONLY |
| 8a | Cost of capital, solar PV | Kuwait 5.3 %, Saudi Arabia 6.2 %, UAE 5.6 % | % (IRENA CoC/WACC, appendix sourced from RPGC 2021) | IRENA 2023 *Cost of financing for renewable power*, data appendix | kuwait / gcc | SNIPPET ONLY |
| 8b | Kuwait IWPP financing | Az-Zour North 1: USD 1.8 bn total, ~80:20 debt:equity; debt reported as USD 1.43 bn (NBK/Clifford Chance) or USD 1.6 bn (IJGlobal); JBIC up to USD 645 m; 40-year ECWPA; ownership 60 % Kuwaiti public, 40 % private | various | ENGIE newsroom; IJGlobal; Clifford Chance | kuwait | SNIPPET ONLY |
| 9a | Utility PV capex (US benchmark) | ATB 2025 Moderate: CAPEX 1,526 (2024) and 1,473 (2025) $/kW; OCC 1,301 (2024) $/kW; FOM 24.66 (2024) $/kW-yr | $/kW (ATB basis) | NREL ATB 2025 data | generic | VERIFIED (data) |
| 9b | Utility BESS capex (US benchmark) | ATB 2025 Moderate, 4 h: CAPEX 1,449 $/kW (2024); OCC 1,297 $/kW; FOM 51.90 $/kW-yr | $/kW | NREL ATB 2025 data | generic | VERIFIED (data) |
| 9c | GCC BESS prices | Saudi SEC Tabuk/Hail (Aug 2025): equipment 73–75 $/kWh, plus EPC 47–48 $/kWh; Ember: ~125 $/kWh all-in, Saudi auctions ~120 $/kWh | $/kWh | Ember 2025; Saur Energy | gcc-desert | SNIPPET ONLY |
| 9d | Global PV installed cost | 691 USD/kW (2024 global weighted average) | USD/kW | IRENA RPGC 2024 | generic | SNIPPET ONLY |
| 9e | Gulf PV tariffs | Al Dhafra 1.35 → 1.32 US¢/kWh (AED 4.97 → 4.85 fils); Al Kharsaah 1.6 US¢/kWh; Saudi range 1.04–2.34 US¢/kWh (21 projects) | US¢/kWh | Masdar fact sheet; Research Square preprint 2026 | gcc-desert | SNIPPET ONLY |
| 10a | Kuwait electricity tariff | Residential 2; Investment & commercial 5; Industrial & agriculture 5; Productive industrial & agriculture 3; Governmental 25; Others (chalets, farms) 12 fils/kWh; reactive energy 3 fils/kVARh | fils/kWh | MEW *Statistical Year Book: Electrical Energy 2023*, PDF p. 104 | kuwait | VERIFIED |
| 10b | MEW fuel bill (all fuels, power + desalination) | 2023: 781,864 B Btu, KD 2,496,101,942 (2019: 696,732 / 1,442,750,517; 2022: 753,097 / 3,340,292,201) | B Btu; KD | MEW Yearbook 2023, PDF pp. 188-189 | kuwait | VERIFIED. Implied 3.19 KD/MMBtu in 2023 is DERIVED |
| 10c | Kuwait generation cost (claims) | 29.5 fils/kWh generation + 8.39 fils/kWh distribution (MEW, cited in a 2016 paper); "46 fils" (official, quoted in press, ~2025) | fils/kWh | see §10 | kuwait | SNIPPET ONLY |
| 10d | Fuel unit prices (crude, HFO, gas oil, LNG) | **No source found** that states administered or opportunity-cost prices per unit for Kuwaiti power generation | n/a | n/a | kuwait | not found |

---

## 1. Ground albedo for Kuwaiti desert

**Result: no Kuwait or Shagaya measurement found.** The proxies below are all SNIPPET ONLY, NOT VERIFIED.

| Value | Context | Source | Specificity |
|---|---|---|---|
| 0.30 (sand with gravel), 12.7 % bifacial energy gain | Saudi entry in a review table, TÜV Rheinland test site. Snippet does not say whether the system was tracked. | Review table, as surfaced by search; likely traced to IEA-PVPS T13-14:2021, *Bifacial Photovoltaic Modules and Systems: Experience and Results*, https://iea-pvps.org/wp-content/uploads/2021/04/IEA-PVPS-T13-14_2021-Bifacial-Photovoltaic-Modules-and-Systems-report.pdf | gcc-desert |
| "around 30 %" (assumed, not measured) | Horizontal single-axis tracked system in central Saudi Arabia | IEA-PVPS T13-14:2021 (same URL) | gcc-desert |
| Bifacial gain "generally less than 10 %" for albedo 0.2–0.3 on single-axis trackers | General statement | IEA-PVPS T13-14:2021 | generic |
| "exceeding 40 %" for desert sand in Qatar | QEERI deployed albedometer stations at 15 sites across Qatar. No site table published in the article. | PV Tech, "Challenges of PV soiling in desert climates", https://www.pv-tech.org/challenges-of-pv-soiling-in-desert-climates/ | gcc-desert |
| 0.3 for sand (model input) | GCC hybrid-plant techno-economic study | Sawafi et al., *Energy Science & Engineering* (Wiley), https://scijournals.onlinelibrary.wiley.com/doi/10.1002/ese3.70682 | gcc-desert (assumed) |
| ~0.4 for dry desert sand | Vendor blog, generic | OTT HydroMet blog, https://blog.otthydromet.com/en/albedo-measurement-for-bifacial-pv-modules/ | generic (low quality) |

**Kuwait leads I could not open:**

- Al-Rasheedi M., Gueymard C.A., Al-Khayat M., Ismail A., Lee J.A., Al-Duaj O. (2020). "Performance evaluation of a utility-scale dual-technology photovoltaic power plant at the Shagaya Renewable Energy Park in Kuwait." *Renewable and Sustainable Energy Reviews* 133:110139. DOI 10.1016/j.rser.2020.110139.
  - Snippets say it recommends bifacial modules on single-axis trackers "which benefit from the high sand albedo". They also say KISR stations measure GHI and POA.
  - No albedo number was visible. Check the full text for an albedometer record.
  - Same paper (snippet): 11.15 MW plant at 29.2° N; annual reference yields of 1805 kWh/kW (thin film) and 1810 kWh/kW (poly); PR of 80.0 % and 80.2 %; dust storms can cause an "instantaneous 30 % drop" in PV output.
- A 2017 MODIS-based paper covering a dust event over Kuwait City used the MODIS BRDF/albedo product, but no Kuwait value appeared in the snippet: https://link.springer.com/article/10.1007/s12517-017-3187-6
- NASA POWER (`ALLSKY_SRF_ALB`) would give a satellite-derived value for Shagaya (29.2 N, 47.04 E), but power.larc.nasa.gov was blocked.

---

## 2. PV module temperature model coefficients

### 2a. PVsyst defaults: VERIFIED via pvlib source

- **Source:** pvlib-python, `pvlib/temperature.py` (main branch, retrieved 2026-10-22 from raw.githubusercontent.com). Function `pvsyst_cell` and `TEMPERATURE_MODEL_PARAMETERS['pvsyst']`.
  - The docstring cites: [1] "PVsyst 7 Help", https://www.pvsyst.com/help/index.html?thermal_loss.htm (accessed 30-Jan-2024 by pvlib); [2] Faiman 2008.
- **Values, verbatim table:**
  - freestanding: Uc = 29.0, Uv = 0.0
  - insulated: Uc = 15.0, Uv = 0.0
  - semi_integrated: Uc = 20.0, Uv = 0.0
- **Units:** Uc in W/m²/°C; Uv in W/m²/°C/(m/s).
- **Verbatim quote on mounting:** "'freestanding' refers to mounting that allows relatively free air circulation around the modules. This case is typical of ground-mounted systems on tilted, fixed racking or single axis trackers."
- **Other defaults:** module_efficiency 0.1 and alpha_absorption 0.9 (pvlib function defaults).
- **Specificity:** generic. PVsyst's own help page was blocked; a search snippet of the PVsyst help page repeats "Uc = 29 W/m²·k, Uv = 0 ... for free-standing" (SNIPPET).

### 2b. Faiman U0/U1: VERIFIED via pvlib docstring

- **Values:** U0 = 25.0 W/m²/°C and U1 = 6.84 W/m²/°C/(m/s).
- **Verbatim:** "The default value is for module temperature determined by Faiman for 7 silicon modules in the Negev desert on an open rack at 30.9° tilt."
- **Source:** Faiman, D. (2008). "Assessing the outdoor operating temperature of photovoltaic modules." *Progress in Photovoltaics* 16(4):307-315. DOI 10.1002/pip.813. The model is adopted in IEC 61853-2 and IEC 61853-3 (2018).
- **Specificity:** gcc-desert (Middle East desert, Sede Boqer, Negev). This is the closest verified hot-desert fit.
- **Spread (SNIPPET):** U0 ranged 23.5–26.5 and U1 6.25–7.68 across the seven modules. Source: Sandia PVPMC Faiman page, https://pvpmc.sandia.gov/modeling-guide/2-dc-module-iv/module-temperature/faiman-module-temperature-model/ (blocked).

### 2c. Other fits and tracker values: SNIPPET ONLY

- **Köhl, Heck, Wiesmeier, Wirth (2011)**, *Sol. Energy Mater. Sol. Cells*, DOI 10.1016/j.solmat.2011.01.020.
  - Outdoor sites included Sede Boqer (arid).
  - Slide table as extracted (column order "U1 U0", so read with care): c-Si U1 = 6.2, U0 = 30.0; CdTe 5.4/23.4; CIS 3.1–4.1 / 23.0–25.0.
  - The authors state the parameters are "module-specific but location independent".
- **Tracker-specific defaults: no source found.**
  - An arXiv study (https://arxiv.org/pdf/2312.02373) found that configuration-specific heat-loss factors instead of PVsyst defaults raised predicted annual yield by 3.3 % for single-axis trackers and 2.9 % for fixed tilt. I did not see its Uc values.
  - SunPower (Bourne, Sandia PVPMC 2019) reported that coefficient choice changes annual energy by 2–3 % and that wind matters more than PVsyst indicates.
- **No Gulf-fitted Uc/Uv or U0/U1 found.**
  - A Qatar and Algeria validation exists (thermal-electrical simulation validated against Qatar and Algeria desert data), but its coefficients were not visible.
  - The desert free-standing comparison "Outdoor testing of free standing PV module temperature under desert climate: A comparative study" (ResearchGate 332693555) reports RMSE < 2.85 °C, but its site and coefficients were not visible.

---

## 3. PV soiling in Kuwait, cleaning effectiveness and cleaning cost

All entries in this section are SNIPPET ONLY, NOT VERIFIED.

### 3a. Kuwait-specific

| Value | Context | Source | Note |
|---|---|---|---|
| 17 % PV power loss after 6 days of dust exposure | Kuwait City, frequently cited 1981 study | Cited in reviews (e.g. JEAS table, https://jeas.springeropen.com/articles/10.1186/s44147-021-00052-6/tables/2) | Implies ~2.8 %/day average. That is my arithmetic: DERIVED, non-linear in time. Another review quotes "17 % after 6 months", so the period is inconsistent between secondary sources. |
| 30 % transmittance loss after 3 days at 0° tilt; 64 % to 17 % losses for tilts of 0° to 60° over 38 days | Kuwait glass-plate study | Same review table | Transmittance, not module power |
| Efficiency reduction vs daily-cleaned panel with monthly cleaning: Apr 15.07 %, May 13.74 %, Oct 10.685 %, Dec 8.742 % | Kuwait washing-period study | "Enhancing the Performance of Photovoltaic Panel by Proper Washing Periods in Kuwait", SCIRP (2016), https://www.scirp.org/html/2-6401459_67341.htm | Recommends weekly water washing in Apr, May, Oct and Dec, monthly otherwise |
| 45.8 % (Azda) and 42 % (Sawda) total soiling loss after 3 months | Listed under Kuwait in a review table | JEAS review table | Site names are odd for Kuwait; treat as unverified |
| Up to 55 % degradation over 14 months unexposed to cleaning; weekly cleaning keeps losses at 2–5 % | Al-Busairi & Al-Kandari, cited by a review | Review snippet | |
| Soiling ~50 % during dusty season, average 25.4 %; > 25 % of annual generation lost without mitigation; automated cleaning raises modelled output from 112,092 to 207,300 MWh | PVsyst model of a 100 MW plant at Al Wafra (modelling, not measurement) | "Soiling Effect and Remedial Measures of Solar Photovoltaic System Performance in Kuwait", *J. Power Energy Eng.* 11(4), 2023, DOI 10.4236/jpee.2023.114003 | Monthly soiling factor table: annual mean 10.91×10⁻⁵, April max 29.17×10⁻⁵, units unclear |
| Sandstorm soiling effect limited to PM10 ≥ 2700 ppb (as stated); ≥ 57 % reduction in daily irradiance; summer max output 13 % below spring | Alshawaf, Poudineh, Alhajeri (2020) | "Solar PV in Kuwait: The effect of ambient temperature and sandstorms on output variability and uncertainty", *RSER* 134:110346, DOI 10.1016/j.rser.2020.110346 | Secondary summaries disagree on whether it is a plant evaluation or a 2 GW simulation |
| "Instantaneous 30 % drop" in PV power during sudden dust storms | Shagaya 10 MW | Al-Rasheedi et al. 2020 (see §1) | Event drop, not a rate |

- **Rain effect, Kuwait:** no Kuwait-specific source found.
- **KISR Shagaya per-day soiling rate:** no source found.

### 3b. Gulf proxies

| Value | Context | Source | Specificity |
|---|---|---|---|
| 0.49 %/day average energy loss | QEERI Solar Test Facility, Doha, modules at 22° tilt; rate excludes rain; heavy rain fully restored power | QEERI Solar Test Facility 5-Year Report (ResearchGate 324438287) | gcc-desert |
| ~0.3–0.5 %/day; dust accumulation 75–250 mg/m²/day; 75 mg/m²/day ≈ 0.20 % power loss | Decade review of QEERI OTF | Aïssa B. et al. (2023), "A Comprehensive Review of a Decade of Field PV Soiling Assessment in QEERI's Outdoor Test Facility in Qatar", *Energies* 16(13):5224, DOI 10.3390/en16135224 | gcc-desert |
| −0.52 %/day (modules cleaned every 6 months); −0.55 %/day (cleaned every 2 months); dust 260 ± 100 mg/m²/day | One-year Qatar study | HBKU record, "Photovoltaic performance degradation due to soiling and characterization of the accumulated dust" | gcc-desert |
| Seasonality conflict | 5-year report: rate slightly higher in winter (humidity). 2023 review: more loss in summer (dust events). | as above | gcc-desert |
| 4.6–5.5 %/day | Rumah, Saudi Arabia | as surfaced by search | gcc-desert. Outlier; check the source |
| Soiling costs ~3–5 % of annual PV yield globally; dry spells can push losses above 20 % | IEA-PVPS T13-21:2022, *Soiling Losses – Impact on the Performance of Photovoltaic Power Plants* | https://iea-pvps.org/wp-content/uploads/2023/01/IEA-PVPS-T13-21-2022-REPORT-Soiling-Losses-PV-Plants.pdf | generic |

### 3c. Cleaning effectiveness: robotic dry vs manual wet

**No source found** that gives a quantified fraction of soiling removed in a desert comparison of dry-robotic and wet-manual cleaning.

- **Doha:** for thin-film panels, "the cleaning efficiency of the nylon brushes was not as high as cleaning using water and delicate wipers". Source: "Experimental investigations on PV cleaning of large-scale solar power plants in desert climates: Comparison of cleaning techniques for drone retrofitting", *Energy Conversion and Management* (2019), https://www.sciencedirect.com/science/article/abs/pii/S0196890419301049. No percentage visible in the snippet.
- **KAUST/Aramco Robotic Dust Mitigation (silicone foam brush, Thuwal):** no recovery percentage in available text.
- **Vendor claim:** "94 % restoration" at a 50 MW desert farm. Marketing only; do not use.

### 3d. Cleaning cost

- **Manual cleaning ≈ 0.19 USD/kW per cycle; mechanised ≈ 0.005 USD/m².** From a study citing large Saudi plants (reference [11] in that paper). The two units are not comparable.
- **1.80 SAR/kWp per scheduled cleaning event (base case).** Optimum interval 60 days; total of 22.56 SAR/kWp·yr includes lost energy. Source: "Seasonal Soiling Rates and Cleaning Optimization for PV Systems in Saudi Arabia: Arar Desert Climate", *Energies* 19(18):4373, https://www.mdpi.com/1996-1073/19/18/4373.
- **0.0183–0.0383 USD per panel per cycle (experimental design range).** Source: "Optimal Scheduling of PV Panel Cleaning and Policy Implications Considering Uncertain Dusty Weather Conditions in the Middle East", *Systems* 12(10):418, DOI 10.3390/systems12100418.
- **Jones R.K. et al. (2016)**, "Optimized Cleaning Cost and Schedule Based on Observed Soiling Conditions for Photovoltaic Plants in Central Saudi Arabia", *IEEE J. Photovolt.* 6:730-738, DOI 10.1109/JPHOTOV.2016.2535308.
  - Conclusion (snippet): "costs attributable to cleaning to an optimum schedule are a small fraction of typical operation and maintenance costs even for completely manual cleaning".
  - Its numeric costs were not visible.
- **USD per MWp per year from a citable non-vendor source: no source found.** Vendor and market-report claims range from under 1,000 USD/MW/yr up to 18,000–36,000 USD/MW/yr (robotics-as-a-service). Not citable.

---

## 4. BESS auxiliary (HVAC) load and round-trip efficiency

### 4a. RTE, NREL ATB 2025: VERIFIED (data file)

- **Source:** NREL (now "National Laboratory of the Rockies") Annual Technology Baseline 2025, electricity data file `ATBe.parquet` v1.0.0, retrieved from the OEDI data lake: https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2025/v1.0.0/ATBe.parquet
- **Value:** `core_metric_parameter = "Round-Trip Efficiency"`, technology "Utility-Scale Battery Storage": **0.85** in every scenario (Advanced, Moderate, Conservative) and every case, for 2023–2060.
- **Reference given in the file:** Cole, W., Ramasamy, V., Turan, M.O. "Cost Projections for Utility-Scale Battery Storage: 2025 Update." Golden, CO, 2025. https://www.nlr.gov/docs/fy25osti/93281.pdf (blocked; not read).
- **AC/DC basis:** a search snippet of the ATB 2025 web page says "roundtrip efficiency of 85 %". I could not verify the AC-AC basis and whether auxiliary loads are included.
- **Specificity:** generic.

### 4b. Measured RTE, EIA: VERIFIED

- **Source:** U.S. EIA, *Today in Energy*, "Utility-scale batteries and pumped storage return about 80% of the electricity they store", 12 Feb 2021, principal contributor Alex Mey. https://www.eia.gov/todayinenergy/detail.php?id=46756
- **Verbatim:** "in 2019, the U.S. utility-scale battery fleet operated with an average monthly round-trip efficiency of 82%, and pumped-storage facilities operated with an average monthly round-trip efficiency of 79%."
- **Basis:** computed from EIA Power Plant Operations Report monthly consumption and gross generation, so it is plant-level and AC-side. It is a fleet mix, not only LFP.
- **Specificity:** generic.

### 4c. PNNL: SNIPPET ONLY

- **PNNL 2020 ESGC Cost and Performance Assessment** (Mongird et al.). The RTE table shows "86 % / 88 %" for LFP across 1, 10 and 100 MW 4-h cases, but the snippet does not show which column is 2020 and which is 2030.
- **PNNL-33283 (2022)** lists 2021 installed cost for 100 MW / 4 h LFP of 385 USD/kWh and for 100 MW / 10 h of 356 USD/kWh. Its RTE was not visible.
- **DOE "Storage Innovations 2030: Lithium-ion"** gives a baseline LFP RTE of 85 % for 100 MW / 10 h.

### 4d. HVAC / auxiliary load in hot climates

**No peer-reviewed hot-climate value found.**

- **Sandia (cold climates only):** "Impact of heating and cooling loads on battery energy storage system sizing in extreme cold climates", *Energy* (2023), DOI 10.1016/j.energy.2023.127878 (OSTI 2311513).
  - HVAC parasitic loads took 8 % (Massachusetts, PCS inside the enclosure) to 34 % (Alaska/Fairbanks, PCS outside) of battery energy (snippet).
  - Sizing increases: energy capacity +42–300 %, power rating +43–217 %, capital cost +43–296 %.
  - Cold-dominated, so not a Kuwait proxy.
- **Non-peer-reviewed (do not cite as authoritative):**
  - Energy Central post "BESS 5 MWh Aux consumption": 8–13 kW per 5 MWh container depending on ambient; 12–14 kW at 45–50 °C.
  - TWAICE glossary: auxiliary load 0.5–5 % of rated power.
  - Industry glossary: 1–3 % of annual throughput.
- **Recommended next step:** use an LFP container manufacturer datasheet that gives HVAC rated power at 50–55 °C ambient. I did not reach any (manufacturer sites blocked).

---

## 5. SWRO specific energy consumption, Arabian Gulf

### Important correction

- **Az-Zour North Phase 1 IWPP uses MED-TVC, not RO.**
  - 107 MIGD (≈ 405,000 m³/d) from 10 MED units of 10.84 MIGD each.
  - Design GOR 11.2; tested GOR 12.1.
  - Sources (SNIPPET): SIDEM/Veolia case study https://www.sidem-desalination.com/az-zour-north-phase-1-iwpp ; ENGIE newsroom.
- **Az-Zour North Phase 2 & 3** (ACWA Power / GIC / KAPP; ECWPA signed 11 Feb 2026, 25-year BOT) has 545,500 m³/d net desalination. The technology was not stated in the snippets (SNIPPET).

### Values found: all SNIPPET ONLY

| Value | Context | Source | Specificity |
|---|---|---|---|
| 3.6–5.4 kWh/m³ | Gulf SWRO plants with DAF and two-pass RO; expected 3.11–3.13 kWh/m³ for a new 100,000–200,000 m³/d plant | "Pilot study of emerging low-energy seawater reverse osmosis desalination technologies for high-salinity, high-temperature, and high-turbidity seawater", *Desalination* (2023), https://www.sciencedirect.com/science/article/abs/pii/S0011916423005039 | gcc-desert |
| 4–6 kWh/m³ with ERDs; 5–6 kWh/m³ for Gulf conditions | Older Gulf literature | Darwish et al., "Needed seawater reverse osmosis pilot plant in Qatar", *Desalination and Water Treatment* 57(9), DOI 10.1080/19443994.2014.989921 | gcc-desert |
| SWRO < 5 kWh/m³ (mechanical); < 6 kWh/m³ equivalent work vs 22 kWh/m³ for Kuwait MSF | Kuwait | "On the reduction of desalting energy and its cost in Kuwait" (ResearchGate 343818251) | kuwait (general) |
| 5.5 kWh/m³ (assumption "based on Kuwait's RO performance data") | Kuwait RE-desalination study | Renewable-desalination paper (as surfaced) | kuwait (assumption) |
| 2.6–13 kWh/m³ (range cited) | Doha RO plant (Kuwait) upgrade study | "Cost Assessment of a Proposed Combined MDC–RO Process as a Performance Upgrade of the Doha Plant (Kuwait)", *Water* 18(12):1460, https://www.mdpi.com/2073-4441/18/12/1460 | kuwait (wide range) |
| MSF 22.3 → SWRO 7.16 kWh/m³ | Kuwait sustainability paper | "Energy and water in Kuwait: A sustainability viewpoint, Part II" | kuwait |

### Kuwait official data: VERIFIED that the data exist, but no SEC can be derived

- **Source:** CSB *Environment Statistics 2024* (file `data/raw/csb-env-2024.xlsx`, SHA-256 25badc0e…).
  - Table 112 lists electricity consumed by RO units in 2024 (MWh): Shuwaikh (RO) 151,421; Doha West (RO) 311,230; South Zour (RO) 55,899.
  - Footnote: "The consumption of electric energy to desalinate water is reflected in reverse osmosis and is therefore negative".
  - Table 114 gives "Production by Reverse Osmosis Unit (4)" in MIG.
- **Why no SEC:** the column alignment of Table 114 is ambiguous after extraction. Every plausible reading gives > 80 kWh/m³, which is not physically plausible for SWRO. So these tables cannot support a plant-level SEC without clarification from MEW or CSB.
- **Not found:** plant-level SEC for Shuwaikh RO, Doha RO or Az-Zour South RO.

---

## 6. Availability: PV plant, inverter, BESS

All entries in this section are SNIPPET ONLY.

- **PV system availability, measured:** P50 = 0.99 and P90 = 0.95 across 1,128 systems that passed data-quality checks.
  - Inverter availability is low in the first 6 months and reaches steady state by the end of year 1.
  - Larger systems show worse inverter availability.
  - Source: NREL, "PV System Availability from Commercial and Utility-Scale Systems" [slides], OSTI 2323270, https://www.osti.gov/biblio/2323270. Specificity: generic (US).
- **DOE FEMP benchmark:** "95 % availability ... should be achievable", alongside an 85 % performance ratio. Source: https://www.energy.gov/cmei/femp/life-cycle-photovoltaic-systems-operate-and-maintain-existing-photovoltaic-system. Generic.
- **NREL/SunSpec *Best Practices for O&M of PV and Energy Storage Systems*, 3rd ed.** (NREL/TP-7A40-73822, 2018): no numeric availability guarantee was visible.
- **SolarPower Europe O&M Best Practice Guidelines:** they define availability KPIs, but no contractual percentage was visible.
- **BESS contracted availability (trade press, low authority):**
  - 95–98 % guaranteed annually; mature LFP sites target ≥ 97 % (BESS.courses glossary).
  - LTSA pricing tiers at 95 %, 96 % and 97 % (Energy-Storage.News, "LTSAs under scrutiny").
  - "system availability of at least 97–99 %, BESS availability of at least 98 %" (Energy-Storage.News availability article).
  - A vendor LTSA with a base of 96 % and add-ons at 97 % and 98 % (Stem one-pager, July 2024).
  - Generic.
- **Inverter availability as a separate contractual figure:** no source found.

---

## 7. PV module degradation

All entries in this section are SNIPPET ONLY.

| Value | Context | Source | Specificity |
|---|---|---|---|
| Median 0.5 %/yr (nearly 2,000 rates); mean 0.8 %/yr (2,128 rates; mean from NREL presentation) | Literature meta-analysis | Jordan D.C., Kurtz S.R. (2013), "Photovoltaic Degradation Rates—An Analytical Review", *Prog. Photovolt.* 21(1):12-29; NREL/JA-5200-51664 | generic. No hot-climate breakdown visible |
| Median −0.75 %/yr system PLR, "slightly higher than historical (module-based) values" | US fleet, one vote per inverter | Jordan D.C. et al. (2022), "Photovoltaic fleet degradation insights", *Prog. Photovolt.* 30:1166-1175, DOI 10.1002/pip.3566. Data: DuraMAT DataHub "Photovoltaic Fleet Degradation Insights – Data" (has PV climate zone per system) | generic. Climate-zone values would need the DuraMAT CSV (host blocked) |
| Median ~0.21 %/yr (mono-Si), ~0.49 %/yr (poly-Si) | 96 modules, DEWA R&D Outdoor Test Facility, Dubai | DEWA R&D paper (ResearchGate, "Performance degradation and reliability evaluation ... desert area", *Renewable Energy* 2023, https://www.sciencedirect.com/science/article/abs/pii/S0960148123013368) | gcc-desert |
| 1.5–2.65 %/yr for hot-desert modules > 10 years old (vs 0.5–1.4 %/yr milder climates); ~1.63 %/yr average hot-desert 10-yr estimate | DEWA R&D review proposing a desert test cycle | PV Tech, "Towards a new desert testing standard for PV modules"; DEWA paper as above | gcc-desert (review) |
| 0.612 %/yr (m-Si), 0.535 %/yr (p-Si), 5 years | Algerian Sahara | *Renewable Energy* 2025, https://www.sciencedirect.com/science/article/abs/pii/S0960148125027089 | gcc-desert (N. Africa) |
| 0.89 %/yr mono, 0.81 %/yr poly | Desert maritime climate, Algeria | *Renewable Energy* 2022, S0960148122000660 | gcc-desert (N. Africa) |
| Kuwait-measured degradation | no source found | n/a | kuwait |

**First-year degradation (LID/LeTID):**

| Finding | Source | Specificity |
|---|---|---|
| Standard PERC: initial ~2 % LID, then a further 6–8 % LeTID over 3 years. LeTID "more severe in hotter climates". | Kersten et al., field test in Cyprus and Germany | generic |
| Qatar 3-year test: PERC degraded significantly at first, then markedly less after year 1. Multicrystalline PERC and cast-mono PERC had higher first-year degradation than mono-PERC and TOPCon. | "Comprehensive assessment of performance and reliability of PERC, TOPCon and SHJ modules in desert climates", *Solar Energy* (2025), https://www.sciencedirect.com/science/article/pii/S0038092X25003184 | gcc-desert |
| Warranty framing: 98 % of rated power in year 1 (≈ 2 % maximum drop), then < 0.5 %/yr. Manufacturer warranty, not a measurement. | Energy America guidance document | generic, low authority |
| A peer-reviewed first-year % for n-type TOPCon in the Gulf | no source found | gcc-desert |

---

## 8. Kuwait and Gulf IPP financing terms and WACC

All entries in this section are SNIPPET ONLY.

- **IRENA (2023), *The cost of financing for renewable power*, Data Appendix**, https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/May/IRENA_Cost_of_financing_renewable_power_Appendix_2023.pdf
  - Solar PV cost of capital: **Kuwait 5.30 %**, **Saudi Arabia 6.20 %**, **UAE 5.60 %**.
  - The appendix says these are sourced from *Renewable Power Generation Costs in 2021*.
  - Nominal or real basis not confirmed. The report uses CoC and WACC interchangeably.
  - Same report: Middle East and Africa average 8.2 % (2019–2021, all technologies). Renewable CoC is "200–300 basis points above the country risk".
- **IRENA, *Renewable Power Generation Costs in 2023*, Figure A1** (country real after-tax WACC): the figure exists, but its values were not visible.
- **Az-Zour North 1 IWPP (Kuwait's first IWPP; financial close Dec 2013 or 10 Jan 2014):**
  - Total cost USD 1.8 bn, debt:equity ≈ 80:20 (ENGIE).
  - Debt: USD 1.43 bn (NBK/Clifford Chance) or USD 1.6 bn (IJGlobal, "long-dated"). JBIC up to USD 645 m. Commercial lenders BTMU, SMBC, Standard Chartered, NBK. ECAs: JBIC and NEXI.
  - One summary mentions three tranches with a 23-year tenor. Unconfirmed; treat with caution.
  - 40-year ECWPA with MEW.
  - Equity: 60 % Kuwaiti public entities, 40 % GDF Suez, Sumitomo and Al Sagar.
  - Sources: IJGlobal "Middle Eastern PPP Deal of the Year 2013: Az Zour North"; Clifford Chance press release Dec 2013; ENGIE newsroom.
- **Az-Zour North 2 & 3:**
  - USD 4.1 bn ECWPA signed 11 Feb 2026 (USD 4.0 bn reported at the Aug 2025 letter-of-award stage).
  - 2,700 MW, 545,500 m³/d, 25-year BOT. ACWA Power effective stake 24 %.
  - No financing terms found.
- **Al Dibdibah / Shagaya Phase III, Zone 2 (500 MW):**
  - KAPP tender with a 30-year PPA (MEW as offtaker).
  - Five shortlisted: Jinko Power, EDF Renewables, Masdar, ACWA Power, Swift Current Energy.
  - Technical bids opened (Reuters, 28 Jul 2026). No tariff or financing published in the snippets.
  - A separate 1.1 GW Zone 1 tender exists.
- **Al Dhafra (2 GW, UAE):**
  - Financial close Dec 2020; ~USD 1 bn from seven banks.
  - Tariff fell from 1.35 to 1.32 US¢/kWh at close, attributed to hedging and financing improvements.
  - 30-year PPA with EWEC.
  - AidData lists a USD 851 m syndicated loan with a "4-year maturity", which is likely a mini-perm or the China-bank tranche. Unclear.
  - Equity: TAQA 40 %, Masdar/EDF/Jinko 20 % each.
- **Not found:** a debt rate or margin, or a fully disclosed tenor for any Gulf solar IPP from a citable source.

---

## 9. PV and BESS capex, fixed O&M, Gulf tariffs

### 9a. NREL ATB: VERIFIED (data files)

- **Source files:**
  - ATB 2025: https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2025/v1.0.0/ATBe.parquet
  - ATB 2024: https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2024/v4.0.0/ATBe.parquet
- **Units and dollar year:** units are as given in the files. I could not confirm the dollar year or the kW basis because the documentation host was blocked. ATB documentation normally states PV in $/kWAC; verify before use.

**ATB 2025, core_metric_case "Exp", Moderate scenario:**

| Tech | Parameter | 2024 | 2025 | 2030 | Units |
|---|---|---|---|---|---|
| UtilityPV (Class1; capex identical across classes) | CAPEX | 1,525.75 | 1,473.14 | 1,210.08 | $/kW |
| UtilityPV | OCC | 1,300.56 | 1,254.14 | 1,022.01 | $/kW |
| UtilityPV | Fixed O&M | 24.66 | 23.97 | 20.73 | $/kW-yr |
| Battery 2 h | CAPEX / OCC / FOM | 965.11 / 829.36 / 33.17 | 936.37 / 801.55 / 32.06 | 843.90 / 712.12 / 28.48 | $/kW, $/kW-yr |
| Battery 4 h | CAPEX / OCC / FOM | 1,448.99 / 1,297.38 / 51.90 | 1,396.73 / 1,246.82 / 49.87 | 1,228.61 / 1,084.22 / 43.37 | $/kW, $/kW-yr |
| Battery 8 h | CAPEX / OCC / FOM | 2,416.76 / 2,233.42 / 89.34 | 2,317.44 / 2,137.36 / 85.49 | 1,998.02 / 1,828.41 / 73.14 | $/kW, $/kW-yr |

- **Per-kWh equivalent (DERIVED):** 4 h OCC 1,297.38 $/kW ÷ 4 h ≈ 324 $/kWh in 2024.
- **References in the file:**
  - UtilityPV OCC: Ramasamy et al., *U.S. Solar PV System and Energy Storage Cost Benchmarks ... Q1 2023*, NREL/TP-7A40-87303.
  - Battery: Cole, Ramasamy & Turan 2025.

**ATB 2024 (Market case, Moderate, crp 20 or 30 identical):**

- UtilityPV CAPEX 1,610.90 $/kW (2023), OCC 1,434.79 $/kW, FOM 22.22 $/kW-yr.
- Battery 4 h: CAPEX 2,080.30 $/kW, OCC 1,906.96 $/kW, FOM 47.67 $/kW-yr (2023).

**Specificity:** generic (US). Gulf EPC costs are well below these (see 9b).

### 9b. Gulf and IRENA: SNIPPET ONLY

- **IRENA *Renewable Power Generation Costs in 2024*** (July 2025): global weighted-average utility PV total installed cost 691 USD/kW (−11 % year on year); LCOE 0.043 USD/kWh. Country tables for Saudi Arabia and UAE capex were not visible.
- **IRENA RPGC 2023:** global PV LCOE 0.044 USD/kWh. IRENA RPGC 2025 executive summary: PV unchanged at 44 USD/MWh.
- **Saudi BESS:**
  - SEC Tabuk and Hail (awarded Aug 2025; 2.45 GWh each): equipment USD 179–183 m, equal to 73–75 $/kWh; EPC USD 116–118 m, equal to 47–48 $/kWh.
  - Ember: all-in ≈ 125 $/kWh for ≥ 4 h projects, of which ≈ 75 $/kWh is core equipment; two Saudi auctions ≈ 120 $/kWh.
  - Source: Ember, "How cheap is battery storage?" (Dec 2025), https://ember-energy.org/app/uploads/2025/12/How-cheap-is-battery-storage.pdf
  - Bisha 500 MW / 2,000 MWh (BYD; State Grid / Alfanar EPC): no price disclosed.
- **Gulf PV tariffs (context only):**

| Project | Tariff | Source |
|---|---|---|
| Al Dhafra, 2 GW | 1.35 → 1.32 US¢/kWh (AED 4.97 → 4.85 fils) | Masdar fact sheet, https://masdar.ae/-/media/corporate-revamp/projects/downloads/al-dhafra-solar-pv/al-dhafra-factsheet-en-v2.pdf |
| Al Kharsaah, 800 MW, Qatar | 1.6 US¢/kWh | as surfaced by search |
| Saudi PV projects (21) | 1.04 to 2.3417 US¢/kWh | Research Square preprint, "Low solar tariffs coexist with public participation and uneven disclosure in Saudi Arabia and the United Arab Emirates", https://www.researchsquare.com/article/rs-10945321/v1 |
| Sudair 1.239 US¢/kWh; Shuaibah 2.6 GW 1.04 US¢/kWh | not confirmed. The Saudi lowest price in the preprint sample is 1.04 US¢/kWh, but the project was not named in the snippet | |

- **Not found:** PV fixed O&M for GCC plants from a citable source.

---

## 10. Kuwait electricity tariff and fuel prices for power generation

### 10a. Tariff: VERIFIED

- **Source:** Ministry of Electricity & Water (MEW), *Statistical Year Book: Electrical Energy 2023*, chapter 4 "Customers", table "Tariff Of Electricity In All Sectors Of Consumption KW.H (Fills)", PDF page 104.
  - Original URL: https://www.mew.gov.kw/media/3zvjuf0s/electrical-annual-report-2023.pdf
  - Archived in the project as `data/raw/mew-yb-2023.pdf`, SHA-256 e5f357a4ebb0c7c4…
  - The same table appears in the 2020, 2021 and 2022 yearbooks.
- **Values (fils per kWh):**

| Sector | Tariff |
|---|---|
| Governmental | 25 |
| Residential | 2 |
| Investmental & Commercial | 5 |
| Industrial & Agriculture | 5 |
| Productive Industrial & Agriculture (related facilities) | 3 |
| Others (chalets and farms, "الشاليهات والجواخير") | 12 |
| Inactive (reactive) energy, governmental, commercial and industrial | 3 fils per kVARh |

- **Specificity:** kuwait.

### 10b. MEW fuel consumption and fuel cost: VERIFIED (DERIVED per-MMBtu)

- **Source:** MEW Yearbook 2023, table "Consumption of Fuel Energy & Fuel Cost of Power Stations During 2019 – 2023", PDF pp. 188-189 (printed p. 187), totals row. The yearbook also gives monthly and per-station fuel cost by fuel type (Gas HP/LP, Gas Oil, Crude, HFO, LSFO) on printed pp. 177-183.

| Year | Fuel energy (billion Btu) | Fuel cost (KD) | DERIVED KD/MMBtu |
|---|---|---|---|
| 2019 | 696,732 | 1,442,750,517 | 2.071 |
| 2020 | 703,454 | 1,034,082,548 | 1.470 |
| 2021 | 744,516 | 2,085,538,355 | 2.801 |
| 2022 | 753,097 | 3,340,292,201 | 4.435 |
| 2023 | 781,864 | 2,496,101,942 | 3.193 |

- The source does not state the KD/MMBtu ratio. It is my division (KD ÷ (B Btu × 1000)).
- The MEW cost covers power and distillation plants and all fuels combined.
- It reflects whatever transfer price KPC charges MEW. The yearbook does not say whether that is an international or administered price.
- **Specificity:** kuwait.

### 10c. Fuel unit prices and generation cost: SNIPPET ONLY

- **KPC–MEW fuel supply agreement (2015, to 2035):** reported as "based on fueling power stations as per the international price"; the price includes infrastructure, operation, transport and maintenance costs. Arab Times, "MEW, KPC ink deal for fuel to power stations", https://www.arabtimesonline.com/news/mew-kpc-ink-deal-for-fuel-to-power-stations/
- **Generation cost:**
  - "electricity production costs the Kuwaiti government 29.5 fils/kWh ($0.104/kWh) ... distribution cost is 8.39 fils/kWh". MEW figure cited in a 2016 paper on subsidies (*Energy and Buildings*, S0378778816300184).
  - Arab Times (~2025): customers pay 2 fils; "the ministry covers the cost of 46 fils". An official's statement.
  - Gelan (2018), *Energy Policy*, "Economic and environmental impacts of electricity subsidy reform in Kuwait: A general equilibrium analysis": cost rose "from 7 cents in 2000 to about 14 cents in 2010".
- **Subsidy scale:**
  - Baker Institute, "Distortionary Effects of Kuwait's Cheap Electricity and the Case for a Just Reform": fuel for subsidised power cost "more than $10 billion" in 2022; > 99 % of power from fossil fuels.
  - IMF 2019 Article IV: fuel, electricity and water subsidies "almost 6 percent of GDP".
  - IMF 2025 Article IV (Feb 2026): recommends raising retail fuel, electricity and water prices toward GCC averages.
- **KISR *Kuwait Energy Outlook* 2023** (KISR/KFAS), https://www.kisr.edu.kw/media/filer_public/62/bb/62bb91a9-81da-4428-86ff-ab044317db93/keo_2023_-_english_10-12-2023.pdf: likely contains fuel-price assumptions, but the KISR host was blocked and no numbers were visible.
- **IFRI note** "Powering Kuwait into the 21st century: Alternatives for power generation" values the power-sector oil bill at the opportunity cost of oil (2009 MEW data, OPEC prices).
- **LNG:**
  - Al-Zour LNG terminal (KIPIC, ~22 Mtpa, fully operable 21 Feb 2022); 15-year QatarEnergy–KPC SPA.
  - No import price found.
- **Not found:** explicit per-unit administered or opportunity-cost prices for crude, HFO, gas oil, natural gas or LNG used in Kuwaiti power generation.

---

## Network notes (blocked or unreachable hosts)

**WebFetch failed** with DNS errors (`getaddrinfo ENOTFOUND`) for every URL tried: pvpmc.sandia.gov, pvsyst.com, mdpi.com, atb.nrel.gov, pvlib-python.readthedocs.io.

**curl through the proxy returned "403 CONNECT tunnel failed"** for:

| Group | Hosts |
|---|---|
| Modelling tools and docs | pvsyst.com, pvlib-python.readthedocs.io, pvpmc.sandia.gov, sandia.gov, energy.sandia.gov |
| NREL / NLR | nrel.gov, docs.nrel.gov, atb.nrel.gov, nlr.gov, docs.nlr.gov, atb.nlr.gov, research-hub.nrel.gov, nrel.github.io |
| Agencies and international bodies | irena.org, iea-pvps.org, pnnl.gov, osti.gov, energy.gov, imf.org, worldbank.org (incl. openknowledge, documents), ebrd.com, adb.org, oecd.org, kapsarc.org, oxfordenergy.org, data.openei.org, power.larc.nasa.gov |
| Publishers and journals | mdpi.com, sciencedirect.com, link.springer.com, jeas.springeropen.com, e3s-conferences.org, ieeexplore.ieee.org, onlinelibrary.wiley.com, tandfonline.com, iopscience.iop.org, nature.com, cell.com, frontiersin.org, plos, pubs.acs.org, hindawi, scirp.org, preprints.org, aimspress.com, dergipark.org.tr, epj-pv.org |
| Scholarly indexes and repositories | doi.org, api.crossref.org, unpaywall, semanticscholar (incl. pdfs), openalex, arxiv.org, export.arxiv.org, europepmc.org, ncbi.nlm.nih.gov / pmc, researchgate.net, academia.edu, core.ac.uk, scholar.archive.org, web.archive.org, hal.science, MIT DSpace, Qatar University QSpace, QNL Manara, KFUPM scholar, White Rose eprints, DiVA, JRC publications, EconStor, figshare, datahub.duramat.org |
| Kuwait and Gulf institutions and companies | kisr.edu.kw, repository.kisr.edu.kw, kapp.gov.kw, kpc.com.kw, knpc.com.kw, kahramaa.qa, ewec.ae, spp.gov.sa, dewa.gov.ae, acwapower.com, masdar.ae |
| Industry, press and data vendors | lazard.com, ens.dk, solarpowereurope.org, bnef.com, pv-magazine.com, pv-tech.org, thenationalnews.com, zawya.com, meed.com |
| General | Wikipedia, Google, Google Scholar, huggingface.co, jsdelivr, unpkg, cdnjs |

**Reachable and used:**

- raw.githubusercontent.com and api.github.com (pvlib source)
- oedi-data-lake.s3.amazonaws.com (NREL ATB data)
- www.eia.gov
- zenodo.org (searched; nothing relevant found)
- Local copies of the MEW yearbooks and CSB workbooks already in the project (`data/raw/`)

**Not tried:** www.mew.gov.kw needs legacy TLS renegotiation (see `config/openssl-mew.cnf`). I used the local archived copies instead.

All "SNIPPET ONLY" values came from the WebSearch tool's result summaries, which paraphrase or quote the indexed pages. Before any of these values goes into the toolkit, open the primary document on a machine that can reach these hosts and confirm the page or table reference.

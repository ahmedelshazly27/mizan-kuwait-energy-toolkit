# Kuwait reference plants, water statistics and grid structure — research notes

Compiled 2026-10-22 for the Kuwait plant evaluation toolkit.

## Provenance tags (read first)

- **[V]** Verified. Read in a primary document downloaded in this session or already archived by the project: MEW yearbooks and monthly books, and CSB Environment Statistics workbooks. The table or page is cited.
- **[S]** Snippet only, not verified. Seen only in a web-search result summary. **No third-party web page could be opened in this session** (see "Access limits" below), so every non-MEW/CSB fact is [S]. Re-check these before you use them as model inputs.
- **[D]** Derived. Calculated here from [V] numbers. The arithmetic is shown.

### Access limits (blocked hosts)
- The egress proxy allowed only `www.csb.gov.kw` and `www.mew.gov.kw`. MEW also needs the legacy-TLS OpenSSL config in `config/openssl-mew.cnf`.
- Every other host was refused (CONNECT 403). This includes `www.kisr.edu.kw`, `kisr.edu.kw`, `kreps.kisr.edu.kw`, `climate2023.arabfund.org`, `pubs.aip.org`, `www.irena.org`, `kapp.gov.kw`, `www.kapp.gov.kw`, `www.kuna.net.kw`, `www.gccia.com.sa`, `www.knpc.com`, `www.kockw.com`, `www.mdpi.com`, `www.sciencedirect.com`, `www.tandfonline.com`, `www.researchgate.net`, `www.pv-magazine.com`, `www.zawya.com`, `www.meed.com`, `www.agbi.com`, `en.wikipedia.org`, `www.gem.wiki`, `openinframap.org`, `solarpaces.nrel.gov`, `www.sbp.de`, `doi.org`, `web.archive.org`, `api.crossref.org` and `api.openalex.org`.
- The WebFetch tool failed with DNS `ENOTFOUND` on every host tried: kisr.edu.kw, climate2023.arabfund.org and en.wikipedia.org.

---

## SUMMARY

**A. Plants**

- **Shagaya Phase I is 70 MW in total** [V, MEW YB 2023 p.50 "Al-Shaqaya Station"]:
  - PV 10 MW, commissioned 29/11/2016.
  - Wind 10 MW, commissioned 13/12/2016.
  - CSP 50 MW, commissioned 09/07/2018.
- **Shagaya annual gross generation (whole station)** [V]:
  - 2018: 4 GWh; 2019: 11 GWh; 2020: 14.3 GWh. These early years look incompletely reported (see A1.6).
  - 2021: 212 GWh; 2022: 177 GWh; 2023: 172 GWh; 2024: 162.8 GWh.
  - Station use was about 22–27 GWh/yr. Sent-out was 147.6 GWh in 2023 and 141.1 GWh in 2024.
  - Implied whole-park capacity factor [D]: 34.6% (2021), 28.9%, 28.0%, 26.5% (2024).
- **Shagaya PV, published details** [S]:
  - Two halves: about 5.5 MWp CIS thin film and about 5.6 MWp polycrystalline, about 11.14–11.15 MWp DC in total.
  - Modules: Solar Frontier SF160‑S (34,560 pcs) and Jinko JKM315PP‑72 (17,820 pcs).
  - Inverters: SMA Sunny Central. The number of units is unclear.
  - Mounting: fixed tilt. The tilt angle was not found.
  - First-year measured performance: about 20.0 GWh, reference yield 1805/1810 kWh/kW, PR about 80%, CF about 20.6%.
- **Shagaya wind** [S]: 5 × Gamesa G97 2 MW turbines, 79 m hub height. They are **not Vestas**. Measured CF was 45.2% in year 1 (about 40 GWh) and 42.1% in year 2.
- **Shagaya CSP** [S]:
  - Parabolic trough, 50 MWe, molten-salt storage of about 10 h (1,200 MWh_th).
  - EPC: TSK. Reported EPC contract about USD 385 M.
  - Measured output 75.0 GWh (2019, partial year), 160.6 GWh (2020) and 140.0 GWh (2021).
- **Phase III Zone 1 (1,100 MW PV IPP via KAPP)** [S]:
  - 30‑year PPA. The scope includes a 400 kV substation.
  - Six bidders prequalified (June 2025). Bids came from ACWA/AEPC, Masdar/Fouad Alghanim and EDF/Al Sagar/KOWEPO.
  - MEED and MVA Pulse report that the **Masdar + Fouad Alghanim & Sons consortium was selected** (2026; the exact date was not verified).
  - No tariff was found.
- **Phase III Zone 2 (500 MW PV)** [S]: five or more bidders shortlisted (October 2025). The bid deadline was extended several times, latest 26 July 2026. No award was found.
- **Earlier and parallel projects** [S]:
  - KNPC's Al‑Dibdibah 1.5 GW (5 × 300 MW) was cancelled by Cabinet in 2020 and folded into KAPP Shagaya Phase III.
  - The Al‑Abdaliyah 280 MW ISCC tender (60 MW solar) was cancelled by KAPP about 16 months after its November 2015 RFP. It was never built.
  - MEW lists "Al‑Shagaya renewable energy phases 2–5" ramping to 4,500 MW [V, MEW YB 2023 p.55].
- **Other PV**:
  - KOC Sidrah 500 at Umm Gudair: 10 MW, started October 2016 [S].
  - MEW "PV on the roofs of Sabiya water reservoirs", 24–30 MW, is planned [V].
  - No KNPC Al‑Zour PV project was found.

**B. Water**

- **MEW Water Statistical Yearbooks found** [V, downloaded]:
  - Cover "2018" edition, data year 2017.
  - Data year 2020 edition (cover 2021).
  - Data year 2021 edition ("final water book 2021").
  - **No 2019, 2022, 2023 or 2024 water-yearbook URLs were found.** The 2023 edition is cited in literature but was not located.
- **Monthly books** (2023 binder; 2025 Feb, May, Jun, Jul) carry the full daily water tables [V].
- **Distillation technology** [V, MEW Water YB]:
  - All thermal plants use MSF (24–26 stages). Az‑Zour North uses MED (10 × 10.7 MIGD).
  - Total thermal capacity is 683.3 MIGD (2020–2021 editions), up from 623.8 MIGD in the 2018 edition.
  - SWRO: Shuwaikh 30 MIGD, Az‑Zour South 30 MIGD, Doha West 60 MIGD (from 07/07/2019).
- **RO specific electricity 2024** [D, from CSB T111/T113]: Shuwaikh RO about 5.5 kWh/m³, Doha West RO about 5.3 kWh/m³, Az‑Zour South RO about 4.6 kWh/m³.
- **Thermal desal electricity**: per‑station "Dist." auxiliary MWh is published daily in the MEW monthly books. No kWh/m³ or steam-per-MIG figure is published.

**C. Grid**

- **MEW voltage levels are 400 / 300 / 132 / 33 kV** [V]. Kuwait's "275 kV" in the literature is the system MEW tabulates as 300 kV [S].
- **2023 network** [V]:
  - 18 × 400 kV substations, 38 × 300 kV, 515 × 132 kV, 122 × 33 kV, 193 × 33 kV spur.
  - 400 kV: 923 km of overhead route plus 403 km of cable.
  - 300 kV: 956 km of overhead route plus 917 km of cable.
- **Peak-time load by feeding substation/area for 2021–2023**: 37 rows, total 16,940 MW on 02/08/2023 [V, MEW YB 2023 p.85–86]. This is the best published basis for a zonal split.
- **GCCIA link** [S]: 400 kV from Al‑Zour via Ghunan to Al‑Fadhili, 1,200 MW exchange limit. A new 2.5 GW Wafra (Z) substation is raising this to 3.6 GW (commissioning reported in 2025).

---

## A. Reference plant specifications

### A1. Shagaya Renewable Energy Park — Phase I (KISR-led, MEW-owned station "SGRE")

#### A1.1 Park-level data
| Item | Value | Tag / source |
|---|---|---|
| Location | Al‑Shagaya desert, Jahra Governorate, about 100 km west of Kuwait City | [S] KISR PV paper; KAPP tender coverage (solarquarter.com 2024‑01‑03) |
| Coordinates | Pilot PV 29.2055 N, 47.0524 E; Pilot CSP 29.1987 N, 47.0465 E | [S] Global Energy Monitor (gem.wiki/Al_Shagaya_Solar_Energy_I) |
| Park area | 100 km² (IEA policy database) vs "nearly 84 km²" (Worley case study). The two figures conflict. | [S] |
| Phase I total | 70 MW = PV 10 + Wind 10 + CSP 50 | [V] MEW Statistical Year Book Electrical Energy 2023, p.50 "9 – Al‑Shaqaya Station, Installed Capacity 70 MW" |
| MEW commissioning dates | PV 29/11/2016; Wind 13/12/2016; CSP 09/07/2018 | [V] same page |
| Other reported dates | PV completion 4/5/2017 (Arab Fund presentation); wind commissioned May 2017 (KISR page); CSP COD 17/10/2018, December 2018, February 2019 or 6/2/2019 (various). These conflict with MEW. | [S] |
| Installed capacity series | 20 MW (2016–2017), 70 MW (2018–2024) | [V] MEW YB 2020 capacity history; CSB Env. Stat. 2024 T108 (operating year 2016, 70 MW) |
| Grid connection | Shagaya substation exports to the national grid by a 132 kV overhead line, 32.5 km long | [S] gov.pl "Visit at Al Shagaya renewable energy park" |
| Grid area | MEW peak-load table: "JAHR W, X … Shagaya … (Part of JAHR AW is feeding from SGRE by SGRE–SHAG A feeders (38 MW))" | [V] MEW YB 2023 p.86, row 5 |
| New 400 kV link | MEED reports a 400 kV package linking the Shagaya solar substation to Subiya (Dec 2024/Mar 2025). A March 2026 MEED item says a USD 158 m link goes to Wafra. The destinations conflict. | [S] meed.com headlines only |
| MEW "available capacity" table | Shygaya: Wind 10, PV 10, CSP 50, total 70. The header reads "(5W+6PV+CSP)". | [V] MEW YB 2023 p.39 |
| Monthly max available / on-bar | Max available 55 MW for the year (W+PV column). Monthly on-bar figures are given per month. | [V] MEW YB 2023 monthly data p.196 |
| Phase I cost | No park total was found. The CSP EPC was about USD 385 M (TSK, 2015) [S]. NREL SolarPACES lists "116.00 million" with the currency missing [S]. KOC Sidrah is a separate project (A3). | [S] |

#### A1.2 Shagaya measured generation (MEW/CSB, whole station = PV+wind+CSP)
| Year | Gross gen. (MWh) | Station use (MWh) | Sent out (MWh) | Source | Implied CF on 70 MW [D] |
|---|---|---|---|---|---|
| 2018 | 4,000 | – | 3,920 | [V] MEW YB 2020 generation history; CSB 2018 T112 | (incomplete, see note) |
| 2019 | 11,000 | – | 10,926 | [V] MEW YB 2020/21/22/23; CSB 2019 T114 | (incomplete) |
| 2020 | 14,300 | – | 14,300 | [V] MEW YB 2020 | (incomplete) |
| 2021 | 212,000 | 27,271 | 184,756 | [V] MEW YB 2021 | 34.6% |
| 2022 | 177,000 | 22,787 | 154,588 | [V] MEW YB 2022 | 28.9% |
| 2023 | 172,000 | 23,963 | 147,558 | [V] MEW YB 2023 | 28.0% |
| 2024 | 162,793 | 21,666 | 141,127 | [V] CSB Env. Stat. 2024 T110–T112 | 26.5% |

Note on 2018–2020: the measured CSP output alone was 75 GWh (2019) and 161 GWh (2020) [S, ScienceDirect S2213138824001796]. MEW's 11 and 14.3 GWh for those years are therefore almost certainly incomplete reporting, possibly only the PV/wind feed. CSB adds the footnote "*** Shuqaya plant production data of renewable energy has been added for 2018" (T112). **Use 2021+ for calibration.** MEW does not split annual generation by technology in the yearbooks seen. The monthly tables give W&PV and CSP capacity columns only.

#### A1.3 Shagaya PV (10 MW nominal; about 11.14 MWp DC)
| Item | Value | Tag / source |
|---|---|---|
| Split | 5 MW thin film (CIS) + 5 MW polycrystalline; fixed tilt | [S] KISR project page kisr.edu.kw/en/gi/2/details (blocked); AIP Conf. Proc. 2126, 040003 (2019) "fixed tilt, 10 MW PV plant" |
| DC capacity | 11.14 MWp = 5.5296 MWp thin film + 5.612 MWp poly (Arab Fund 2023 presentation). The Renewable Energy paper uses 11.15 MW (5.5 + 5.6). | [S] |
| Modules | Thin film: Solar Frontier SF160‑S, 160 W, **34,560 panels**. Poly: Jinko Solar JKM315PP‑72, 315 W, **17,820 panels**. Check: 34,560 × 160 W = 5.5296 MWp ✓ and 17,820 × 315 W = 5.613 MWp ✓ [D]. | [S] KISR page per search summary |
| Inverters | SMA Sunny Central. The summary says "three 2,200 kW units", which is ambiguous (per subsystem or in total). Not verified. | [S] |
| Tilt / azimuth | **Not found.** One ResearchGate figure suggesting 10° is from an unrelated Philippine design. Do not use it. | – |
| Tracker | None. All sources say fixed. | [S] |
| EPC / O&M | TSK built and operates the site (Solar Frontier/TSK release, Dec 2015). | [S] pv-tech.org, solarserver.de |
| Measured year 1 | Combined 20,003,054 kWh (+3.9% vs developer guarantee). Reference yield 1805 kWh/kW (TF) and 1810 (poly). PR 80.0% / 80.2%. CF 20.61% / 20.66%. Annual mean efficiency 10.42% TF / 13.02% poly (another summary gives 10.88 / 13.60). Dust storms caused instant drops of up to 30%. | [S] Al‑Rasheedi, Gueymard et al., *Renewable & Sustainable Energy Reviews* 133 (2020) 110139, doi:10.1016/j.rser.2020.110139 (ScienceDirect S1364032120304305; UCAR OpenSky articles:23528). The abstract prints the longitude as "47.04 W"; it should be E. |

#### A1.4 Shagaya wind (10 MW)
| Item | Value | Tag / source |
|---|---|---|
| Turbines | 5 × Gamesa G97, 2 MW each, hub height 79 m, blade about 47 m (rotor 97 m). **Not Vestas.** | [S] KISR page gi/3 (blocked); tandfonline doi 10.1080/15567249.2025.2507683; gov.pl ("Siemens Gamesa G97") |
| Measured | Year 1: CF 45.2%, about 40 GWh. Year 2: CF 42.1%, about 37 GWh. Summer months CF about 70%. Dust losses 0.31% / 1.45% per turbine. Sep 2017–Aug 2019 CF about 45%. | [S] "Performance analysis of a 10‑MW wind farm in a hot and dusty desert environment. Part 1" (*Sustainable Energy Technologies & Assessments*, ScienceDirect S2213138821004987); "Climatology of wind variability for the Shagaya region" |

#### A1.5 Shagaya CSP (50 MWe parabolic trough)
| Item | Value | Tag / source |
|---|---|---|
| Configuration | Parabolic trough, 206 loops, SKAL‑ET (EuroTrough-based) collectors. Two-tank indirect molten-salt storage, 10 h / 1,200 MWh_th ("more than 9 equivalent hours" in the AIP paper). | [S] AIP Conf. Proc. 2126, 040003; cspfocus.cn fact sheet; sbp.de project page |
| Guaranteed output | Minimum net 170 GWh_e/yr (contract); 180 GWh/yr (KISR/fact sheet) | [S] |
| EPC | TSK (Spain), contract signed 2015, about USD 385 M | [S] cspfocus.cn |
| Measured | 74.99 GWh (2019, partial from about Feb 2019), 160.62 GWh (2020), 140.04 GWh (2021). CF 19% / 40.75% / 35.53%. Monitoring period Jan 2019–May 2022. | [S] "Thermal efficiency and performance analysis of 50 MW concentrated solar power plant", ScienceDirect S2213138824001796 (2024) |
| KISR 2023 | The CSP "operates almost continuously as a conventional power plant" thanks to storage. The three plants deliver about 200 GWh/yr together. | [S] KISR Kuwait Energy Outlook 2023 PDF (kisr.edu.kw, blocked) |

#### A1.6 Things not found (Phase I)
- Inverter count and AC rating per subsystem (only an ambiguous snippet).
- Tilt angle.
- Exact land area per plant.
- Phase I total capex.
- PPA or tariff: none; it is a government-owned R&D plant.
- KISR's official annual performance reports.

### A2. Shagaya Phase II / Phase III / Al‑Dibdibah / Al‑Khairan / Al‑Abdaliyah

| Project | Status and facts | Tag / source |
|---|---|---|
| Original Shagaya master plan | 2,000 MW by 2030 in three phases. The IEA database lists Phase 2 as 1,000 MW (550 CSP, 380 PV, 70 wind), originally due 2020. OBG 2013 gave Phase 2 930 MW and Phase 3 1,000 MW. Never procured in that form. | [S] iea.org/policies/5541; oxfordbusinessgroup.com |
| MEW plan | "Al‑Shygaya second and third stages with installed capacity not less than (4500 MW)". The future-capacity table "Al‑Shagaya renewable energy-phase(2‑5)" ramps 0, 0, 1100, 4300, 4500, 4500 MW over the six planning years shown. | [V] MEW YB 2023 p.17–18 and p.55 |
| MEW renewable programme (31/12/2023) | National: 179 projects, 4,887,909 kW in total. Implemented: 50 projects, 57,422 kW. Under tender/construction: 46 projects, 166,541 kW. Future: 83 projects, 4,663,946 kW. MEW's own share: 26 projects, 2,823,826 kW; implemented 7 projects, 15,207 kW. | [V] MEW YB 2023 p.19 |
| KNPC Al‑Dibdibah (Dabdaba) PV | KNPC tendered 1 GW in 2018, enlarged to 1.5 GW (5 × 300 MW). Lowest bid about KWD 439 m. Cancelled by Cabinet in 2020 (COVID/oil). In January 2021 it was proposed for folding into Shagaya Phase 3 under KAPP as an IPP. | [S] taiyangnews.info "1.5 GW planned Kuwait solar project scrapped"; pv-magazine 2020‑07‑07 |
| **Phase III Zone 1 (Al Dibdibah Power & Al Shagaya RE Ph III Zone 1)** | 1,100 MW net PV IPP. 30‑yr PPA with MEWRE from COD. The scope includes a 400 kV transmission substation. RFP issued December 2023/January 2024. Six prequalified (June 2025: TotalEnergies, Trung Nam, ACWA+AEPC and others). Bid deadline 14 Sep 2025, then 15 Jan 2026. Financial bids opened by mid‑2026. Bidders: ACWA+Alternative Energy Projects Co; Masdar+Fouad Alghanim & Sons; EDF Renewables+A.H. Al Sagar+KOWEPO. **MEED: "Kuwait selects developer for Shagaya zone one plant" — Masdar/Fouad Alghanim** (also MVA Pulse "Kuwait awards 1.1 GW solar project"). An unverified mention says L&T is EPC. Module suppliers reportedly Aiko, Yingli and DMEGC. **Tariff not found.** GEM lists planned COD 2027. | [S] solarquarter.com (2024‑01‑03, 2024‑08‑28, 2026‑05‑13, 2026‑06‑03); pv-magazine 2025‑06‑16; zawya; utilities-me.com; meed.com; mvapulse.com |
| Phase III Zone 2 | 500 MW PV IPP, 30‑yr PPA. Five shortlisted (October 2025: Jinko Power, EDF, Masdar, ACWA, Swift Current consortia); another report says nine prequalified. Bid deadline 16 Feb 2026, then 30 Apr 2026, then 26 Jul 2026. No award found. | [S] pv-magazine 2025‑10‑07; solarquarter 2025‑11‑27 and 2026‑02‑20; zawya |
| China framework (Mar 2025) | Kuwait–China framework agreement for "third and fourth zones" of Shagaya and Al‑Abdaliya solar: 3,500 MW, expandable to 5,000 MW. AGBI (May 2025) says a Chinese state firm was awarded phases 3 and 4, 4,800 MW by 2028. Not confirmed by KAPP/MEW. | [S] arabnews 2594037; agbi.com 2025/05; Bloomberg 2025‑03‑17; MEES 2025‑03‑21 |
| Al‑Abdaliyah ISCC | 280 MW ISCC with a 60 MW solar field, 25‑yr BOT via KAPP. RFP Nov 2015; KAPP cancelled the tender about 16 months later and planned to re-tender. Not built. Later "Al‑Abdiliya solar" appears only in the 2025 China framework. | [S] meed.com; ScienceDirect S0960148118308735; mdpi.com 1996‑1073/19/20/4844 |
| Al‑Khairan IWPP Phase 1 | MEW: 1,800 MW and **33 MIGD** (YB 2023 p.18). News: 1,800 MW / **125 MIGD**. The figures conflict. RFP 31 Aug 2025. Bids opened about June 2026 with two bidders: TAQA+Al Sagar+JERA and ACWA+GIC. | [V] MEW YB 2023 for 1,800 MW/33 MIGD; [S] zawya/tradingview 2026‑06‑03, smartwatermagazine |
| Az‑Zour North 2 & 3 IWPP (context) | 2,700 MW CCGT + SWRO about 545,500 m³/d. ACWA Power + GIC (40%), KAPP (60%). ECWPA about USD 4.1 bn signed 3 Feb 2026, 25‑yr BOT. MEW lists 2,700 MW + 120 MIGD. | [S] ACWA Tadawul filing; [V] MEW YB 2023 p.18 |

### A3. Other Kuwaiti PV

| Plant | Facts | Tag / source |
|---|---|---|
| KOC Sidrah 500 (Umm Gudair, West Kuwait) | 10 MWp DC. Started 26 Oct 2016 (Reuters/GSN). Half to the MEW grid, half to the oil field. About KD 30 m (about USD 99 m). KOC owns 100%; Gestamp Solar operates. | [S] gem.wiki/Sidrah_500_solar_farm; gsn-online.com; eqmagpro.com |
| KNPC Al‑Zour refinery PV | **Not found.** No KNPC rooftop or carport PV at Al‑Zour located. | – |
| MEW Sabiya reservoir rooftop PV | "Supply, installation, operation and maintenance of PV on the roofs of Al‑Sabiya ground reservoir with a capacity of (24–30 MW)". 24 MW appears in the future-capacity table. | [V] MEW YB 2023 p.17, p.55 |
| Souk Sharq (commercial) | 8.77 MW rooftop and carport PV; APECO EPC/O&M, 15‑yr deal with Marasi United. | [S] meed.com / igrownews |
| National totals | 57.4 MW implemented renewables nationally at end‑2023 (all owners) [V]. Rystad (via pv‑magazine 2025‑09‑24) gives "about 50 MW solar". | [V]/[S] |

---

## B. Kuwait water (desalination) statistics

### B1. MEW "Statistical Year Book — Water" editions found
All were downloaded in this session through the legacy-TLS MEW config (`OPENSSL_CONF=config/openssl-mew.cnf`).

| Edition (cover) | Data year | URL | Pages | SHA‑256 |
|---|---|---|---|---|
| 2018 | 2017 (monthly chapter "Monthly Statistical Data – 2017") | https://www.mew.gov.kw/media/ayel3rql/%D9%83%D8%AA%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%A7%D8%A1.pdf | 274 | ec0c3a3c39256ab37d58d95b6a84c4789363b0ad73adb00a678087048cc45c8e |
| 2021 (cover text "2021") | 2020 ("Executed Projects During 2020", distilled data "During 2020") | https://www.mew.gov.kw/media/rckpzmm4/%D9%83%D8%AA%D8%A7%D8%A8-%D8%A7%D9%84%D8%A7%D8%AD%D8%B5%D8%A7%D8%A1-%D8%A7%D9%84%D8%B3%D9%86%D9%88%D9%8A-%D8%A7%D9%84%D9%85%D9%8A%D8%A7%D9%87-compressed.pdf | 227 | 6712b2ef3108aca90556db3826c34b8b20d40d12e0f147be29502642c2c37abd |
| "final water book 2021" | 2021 (series run to 2021) | https://www.mew.gov.kw/media/2i1l4phf/final-water-book-2021_compressed.pdf | 207 | 5da14fc37e7d87b6319b6f18ca9e88f9db94866732a8d54ca64d28829becc7e3 |

**Not found:** the editions for data years 2018, 2019, 2022, 2023 and 2024.
- MEW's statistics page (`/en/about/statistics/`) renders an empty "Annual Statistics" list.
- `/en/statistics/` returns HTTP 500.
- There is no sitemap or robots file.
- Umbraco media IDs are random, so the URLs cannot be guessed.
- An MDPI paper (*Sustainability* 18(5) 2253, 2026) cites a "Water Statistics Year Book … 2023" [S], so that edition exists somewhere.
- Kuwait-only workaround: MEW monthly books and CSB (B3).

Text-layer quality:
- The 2018 edition extracts cleanly.
- In the 2020 and 2021 editions, the Arabic and cover text is garbled, but the English table headings and numbers extract with `pdftotext -layout`.

#### B1.1 Contents (2018 edition TOC; the 2020/2021 editions have the same structure)
Units: MIG (million imperial gallons) and MIGPD/MIGD. 1 MIG = 4,546.09 m³ (MEW monthly books print an "in Mm³" total row at this factor [V]).

- **Ch.1 Projects**: distillation projects under implementation and future projects.
- **Ch.2 Fresh Water**:
  - Desalination outlook and fresh-water history.
  - **Water Desalination Plants**: unit-by-unit tables with commissioning date and MIGPD per unit, p.67–74.
  - Development of distillation installed capacity, 1992–year (MIGPD).
  - Future installed-capacity estimates.
  - **Gross production of distilled water by station, 1992–year (MIG)**, with RO columns.
  - Gross fresh-water production (MEW).
  - Quarterly production and consumption.
  - Total and daily-average production and consumption.
  - Max, min and daily-average consumption; maximum daily gross consumption; per-capita consumption.
  - The 2020/21 editions add RO production ("Production … By Reverse Osmosis Method During 2020/2021") and WRDC lab analyses.
- **Ch.3 Brackish Water**:
  - Production by MEW and Kuwait total.
  - Net and gross composition.
  - Quarterly production and consumption; net and daily-average consumption; max daily; per-capita.
- **Ch.4 Fresh and brackish storage**:
  - Storage capacity development; daily max/min reservoir available capacity.
  - Elevated towers; ground reservoirs.
  - Location and capacity of underground tanks.
  - Pump-station capacity.
- **Ch.5 Networks**: pipeline lengths, new connections, pipe breakage, connection damages.
- **Ch.6 Consumers**: fresh and brackish consumers; sales revenue.
- **Ch.7 Monthly data (fresh)**:
  - Gross and net distilled-water production per station.
  - Fresh-water production.
  - Distilled water consumed in power stations.
  - Fresh-water consumption.
  - **Boiler feed-water make-up by D/plants (MIG)**.
  - **Sea-water consumption (MIG)**.
  - **Distiller running hours and production by distillation plant**.
  - **Distillation plant availability**.
- **Ch.7 Monthly data (brackish)**: gross and net brackish production and consumption.
- **Ch.8 Fuel**:
  - Station consumption of natural gas, gas oil, crude and heavy oil, split Steam / Gas Turbines / RO.
  - **Thermal energy consumption (billion BTU) by power and distillation plants**, split Steam / Gas / RO / Boilers.
  - Fuel cost (KD), split the same way.

#### B1.2 Gross distilled-water production by station, MIG (MEW Water YB data‑2021 edition, "Gross Production of Distilled Water (MIG) During 1992–2021") [V]
| Year | Total | AZN (MED) | Sabiya | AZS RO | AZS | DW RO | DW | DE | SS | SN | Shuw RO | Shuw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 158,948 | 38,088.5 | 25,720.3 | 6,812.1 | 22,391.1 | 5,005.4 | 23,570.8 | 12,328.1 | 8,368.3 | 8,075.4 | 4,090.7 | 4,497.5 |
| 2020 | 166,244 | 37,970.2 | 26,529.0 | 2,776.8 | 27,174.6 | 12,440.2 | 22,384.8 | 9,790.4 | 8,838.9 | 9,164.1 | 4,764.5 | 4,410.1 |
| 2021 | 163,352 | 37,317.54 | 20,934 | 4,126 | 29,409 | 12,097 | 25,800 | 11,715 | 8,634 | 3,685 | 4,881 | 4,755 |

The columns were mapped from the English header order. The rows sum to the totals.

Gross fresh-water production (MIG) [V]: 2017 160,236; 2018 159,828; 2019 160,430; 2020 167,772; 2021 164,663. Daily average 2021: 451.1 MIG/d.

### B2. Thermal desalination technology by station [V, MEW Water YB 2018 p.67–74 and 2021 edition]
- "The distillation units in the Power Stations and Water Distillation use the multi stage flash evaporation method (**MSF**) except Az‑Zour North station uses multi effect distillation method (**MED**). Each distillation unit consists of number of stages ranging between 24–26 stages and the capacity of the units is between (5–15) MIG/Day."
- Total distillation capacity: 623.8 MIGD (2018 edition) and 683.3 MIGD (2020 and 2021 editions).

| Station | Thermal units | Capacity | RO | Notes |
|---|---|---|---|---|
| Shuwaikh | 3 MSF (D‑1, D‑2, D‑3), commissioned Jan–Apr 1982; 6/6.5 MIGPD each | 18.5 MIGD (2021; 19 in 2018). Fed only from boilers 12B/12C/12D | SWRO 30 MIGD, commissioned 4/7/2011 | Current available capacity 48.5 MIGD incl. RO |
| Shuaiba North | 3 MSF × 15 MIGPD (D1–D3, Aug–Nov 2011; in service Q2 2012) | 45 MIGD | – | |
| Shuaiba South | 6 MSF × 5 MIGPD (A‑1…A‑6, 1971–75) | 30 MIGD | – | |
| Doha East | 7 MSF × 6 MIGPD (A‑1…A‑7, 1978–79) | 42 MIGD | – | |
| Doha West | 16 MSF: Stage I 4 × 6 MIGPD; Stage II 12 × 7.2 MIGPD at HTO (1983–85) | 110.4 MIGD | **SWRO 60 MIGD, commissioned 7/7/2019** | 170.4 MIGD total |
| Az‑Zour South | 16 MSF: Stage I 8 × 7.2 (1988–89); Stage II 4 × 6, uprated to 7.2 at HTO (1998); Stage III 4 × 6 (D13–D16, 2001) | 110.4 MIGD | SWRO 30 MIGD, commissioned 5/4/2014 | 140.4 MIGD total |
| Sabiya | 8 MSF × 12.5 MIGPD (D1–D8, Aug 2006–Oct 2007) | 100 MIGD | – | |
| Az‑Zour North (Ph 1 IWPP) | **10 MED × 10.7 MIGPD** (MED 21–25, 32–35, 54; commissioned 27–29/9/2016) | 107 MIGD | – | |
| Shagaya | – | – | – | Brackish-water field "Al‑Shaqiaya" (CSB T115), not desal |

CSB Env. Stat. 2024 Table 109 repeats these capacities as Shuwaikh 18 + RO 30, Shuaiba N 45, Shuaiba S 30, Doha E 42, Doha W 110.4 + RO 60, Zour S 110.4 + RO 30, Zour N 107, Sabiya 100. **The column header there wrongly says "Total Capacity (MW)"; the values are MIGD** [V].

### B3. CSB Environment Statistics — "Electrical Energy and Water" chapter
- **Page**: https://www.csb.gov.kw/Pages/Statistics?ID=44&ParentCatID=4 (Environment Statistics). Files are served via an ASP.NET postback per year and chapter, so there are **no stable direct file URLs**. The project's `kwelec.fetch.csb.download(session, 44, 4, year, "كهرب")` reproduces the download. Years 2013–2024 are archived in the project release `sources-2026-10-21`.
- The same CSB publication also has a separate "المياه" chapter of **water-quality analyses** (drinking water by area, etc.). It is not production data.
- **2024 workbook tables** [V] (MW/H means MWh; M.I.G means million imperial gallons):
  - T108: power stations, operating year, total capacity (MW).
  - T109: desalination plants, operating year, capacity (MIGD mislabelled MW), type (distillation/RO).
  - T110: gross generation by month and station (MWh).
  - T111: **electricity consumed within stations by month and station, with separate RO columns** (Shuwaikh RO, Doha West RO, Zour South RO) and Shagaya.
  - T112: net export, including "Consumed electrical units in Shuwaikh distilled water production plant" and boilers.
  - T113: **net distilled water production by month and station, including the RO plants (M.I.G)**, plus distilled water consumed in the Shuaiba industrial area and net sent to tanks.
  - T114: mixed (blending) water, RO production, total net fresh production and consumption by month.
  - T115: brackish production by field (Sulaibiya, Al‑Shaqaya, Um‑Qudair, Al‑Wafra, Al‑Atraf) and net consumption.
  - T116–T119: fuel by station (gas in thousand ft³; gas oil, crude and heavy oil in barrels).
  - T120: fuel cost (KD).
  - T121: revenues (electricity, fresh water, brackish).
- **2024 totals** [V]:
  - Net distilled production 168,539.86 MIG; Shuaiba industrial use 5,752.82; sent to tanks 162,787.04.
  - Total net fresh production 164,426.83 MIG; net fresh consumption 164,764.13 MIG.
  - Brackish production 12,693.25 MIG; net brackish consumption 10,745.43 MIG.
  - By station, net MIG: Shuwaikh 4,744.86; Shuwaikh RO 6,088.09; Shuaiba N 6,397.76; Shuaiba S 8,100.09; Doha E 11,041.80; Doha W 29,730.32; Doha W RO 12,847.84; Zour N 35,761.32; Zour S 28,312.10; Zour S RO 2,648.73; Sabiya 22,866.95.

### B4. Electricity and steam per unit of desalinated water
- **RO, 2024** [D from CSB T111 MWh ÷ T113 net MIG; 1 MIG = 4,546.09 m³]:

  | Plant | MWh | Net MIG | MWh/MIG | kWh/m³ |
  |---|---|---|---|---|
  | Shuwaikh RO | 151,421 | 6,088.09 | 24.87 | **5.47** |
  | Doha West RO | 311,230 | 12,847.84 | 24.22 | **5.33** |
  | Az‑Zour South RO | 55,899 | 2,648.73 | 21.10 | **4.64** |

  Net rather than gross production is used, so these are slight overestimates.
- **Thermal (MSF/MED)**: MEW publishes no kWh/m³ or kg-steam/MIG figure in the editions read.
  - **MEW Monthly Statistics Books** (e.g., July 2025, p.29–30, "Auxiliary Units (M.Whr) Used For Generation Of Power & Prod. Of Distilled Water") split each station's auxiliary electricity into Station (Power) / Common / **Dist.** / RO columns, daily, alongside daily gross and net distilled production per station (p.49–50).
  - Specific pumping electricity for distillation can therefore be derived. Check the column order against the PDF first: the text layer flattens the right-to-left layout.
  - For example, July 2025 Doha West row: 95,325 | 39,472 | 21,987 | 14,537 | total 171,321 MWh.
  - Thermal energy (billion BTU) by power and distillation plant, split Steam / Gas / RO / Boilers, is in Water YB Ch.8 and the CSB/MEW fuel tables. There is no explicit steam-to-distiller allocation.
- **Monthly books with water tables** [V, archived by the project]:
  - May 2025: https://www.mew.gov.kw/media/rfzlhpco/may-2025.pdf
  - Jun 2025: https://www.mew.gov.kw/media/ehipshov/jun-2025.pdf
  - Jul 2025: https://www.mew.gov.kw/media/ldji5kdv/july2025.pdf
  - Feb 2025: https://www.mew.gov.kw/media/402jlp1p/febmonthly-2025.pdf (HTTP 200 checked, not parsed)
  - June 2023 monthly summary binder (fresh and brackish water reports): https://www.mew.gov.kw/media/23qpzmi5/binder1.pdf (downloaded, SHA‑256 9489761a…a6e)
- **Monthly book water tables** include:
  - Gross and net production of distilled water (MIG, with an Mm³ total row).
  - Distilled water consumption within stations.
  - Boiler feed-water make-up.
  - Sea-water consumption.
  - Production and consumption of fresh and brackish water.
  - Maximum daily fresh consumption and station shares.
  - Brackish blended into potable supply (July 2025: 147.869 MIG).

---

## C. Kuwait grid structure for a zonal model

### C1. Voltage levels and network size [V, MEW YB 2023 p.87–89]
- MEW tabulates **400 kV, 300 kV, 132 kV and 33 kV**.
- Academic papers call the older EHV system "275 kV" [S, academia.edu "Upgrading Study of Kuwait High Voltage Network 275 kV"; "Reducing the Short Circuit Levels in Kuwait Transmission Network"; ScienceDirect S0378779698001485 modelled a 300 kV and a 132 kV double-circuit line]. Treat 275/300 kV as the same layer (nominal 275 kV, highest system voltage 300 kV). That equivalence is inferred, not stated by MEW.

| Year | 400 kV S/S | 300 kV S/S | 132 kV S/S | 33 kV S/S | 33 kV spur | Total |
|---|---|---|---|---|---|---|
| 2010 | 3 | 23 | 299 | 120 | 174 | 619 |
| 2019 | 13 | 32 | 438 | 120 | 193 | 796 |
| 2023 | **18** | **38** | **515** | 122 | 193 | **886** |

Transforming capacity (column header, 2023): 400 kV 43,648 MVA; 300 kV 20,000 MVA; 132 kV 10,000 MVA; 33 kV 1,000–1,500 MVA.

Circuit lengths (km). Overhead figures are route lengths; circuit length is double.

| Year | OHL 33 | OHL 132 | OHL 300 | OHL 400 | Cable 33 | Cable 132 | Cable 300 | Cable 400 | Total |
|---|---|---|---|---|---|---|---|---|---|
| 2022 | 1,464 | 1,969 | 956 | 847 | 1,670 | 9,950 | 870 | 268.5 | 17,995 |
| 2023 | 1,464 | 1,969 | 956 | 923 | 1,675 | 10,050 | 917 | 403 | 18,357 |

### C2. Interconnection
- **GCCIA** [S]:
  - 400 kV, 50 Hz double-circuit from **Al‑Zour (Kuwait) – Ghunan – Al‑Fadhili** (Saudi Arabia).
  - Kuwait can import or export up to **1,200 MW**.
  - Al‑Fadhili back-to-back HVDC: 3 × 600 MW = 1,800 MW (50/60 Hz).
  - Expansion: GCCIA began commissioning a new **2.5 GW Wafra (Z) substation** in Kuwait, linked to Fadhili, raising Kuwait interconnector capacity to **3.6 GW** (MEES 2025‑08‑01).
  - Sources: Wikipedia "Al‑Fadhili back‑to‑back HVDC converter station"; GE Vernova GCCIA brochure; ResearchGate "The Operation of the GCCIA HVDC Project"; IRENA 2013 RSB slides; mees.com.
- MEW records "GCC Interchange" as a supply column in its demand tables [V, MEW YB 2023 p.~226 "System Demand … SGRE … GCC Interchange"].

### C3. Power stations — location and governorate
| Station | Area | Governorate | Tag |
|---|---|---|---|
| Shuwaikh | Shuwaikh port | Al‑Asimah (Capital) | [S] GEM "Shuwaikh Power Plant" (location); governorate by standard admin geography, not verified |
| Doha East, Doha West | Doha / Jaber Al‑Ahmad area | GEM lists **Al Jahra** | [S] gem.wiki (conflicts with some sources that place Doha in Al‑Asimah; verify) |
| Shuaiba North, Shuaiba South | Shuaiba industrial area | Al‑Ahmadi | [S]/standard geography |
| Az‑Zour South, Az‑Zour North | Al‑Zour | Al‑Ahmadi | [S] GEM "Az Zour South … Zour, Al Ahmadi" |
| Sabiya | Subiya, north of Kuwait Bay | Al‑Jahra | not verified in a source this session |
| Shagaya (SGRE) | Al‑Shagaya, west | Al‑Jahra | [S] KAPP tender coverage ("Jahra Governorate") |
| Future: Al‑Khairan (1,800 MW), Nuwaiseeb (3,600 MW) | far south | Al‑Ahmadi | MEW YB 2023 (names) [V]; governorate [S] |

### C4. Regional load split [V, MEW YB 2023 p.85–86, "Loads of Different Areas During Peak Time for the Years 2021/2022/2023"]
- Peaks: 28/07/2021 = 15,670 MW; 09/08/2022 = 16,180 MW; **02/08/2023 = 16,940 MW**.
- Substation codes ending W/X/Y/Z are the feeding grid substations: likely 300/400 kV bulk supply points, not verified.

| # | Feeding S/S | Sub-areas (abridged) | 2021 MW | 2022 MW | 2023 MW |
|---|---|---|---|---|---|
| 1 | Power stations | Station auxiliaries and distillation | 1,319 | 1,302 | 1,302 |
| 2 | ZSPS A | Al Zour, Khiran, Nweseeb, Khiran Pearl, Mina Azzour pumping station | 370 | 310 | 300 |
| 3 | DEPS | Part of Ardiya, Doha, part of Sulaibiya, Sulaibikhat, part of Riqee, part of Jahra, Andalus, Qairawan | 721 | 616 | 609 |
| 4 | SLBY W | Sulaibiya, Um Qadair, Al‑Manageesh | 165 | 217 | 207 |
| 5 | JAHR W,X | Jahra, Oyoon, Tima, Qasr, Abdali, Ratqa, Sabiya water DC, **Shagaya**, bases (38 MW fed from SGRE) | 979 | 993 | 1,023 |
| 6 | SABD W | Saad Al‑Abdallah, Naseem | 210 | 226 | 231 |
| 7 | MUTL 1Z–4Z | Mutlaa | – | – | 12 |
| 8 | RDTN W,X | Rawdatain, Sabriya, part of Ratqa | 173 | 190 | 193 |
| 9 | JBAH W,X,Y | Jaber Al Ahmad, part of Sulaibikhat | 315 | 340 | 355 |
| 10 | ARDY X | New 2022, part of FRDS | – | 39 | 81 |
| 11 | ARDY W | Sabah Al‑Naser, Ardiya, Jewan, Riqee | 565 | 714 | 723 |
| 12 | OMAR W | Omaria, Shuwaikh industrial, Al‑Rai, Jaleeb | 545 | 469 | 484 |
| 13 | WJLB W | S. Ardiya, Jaleeb Al‑Shuyookh, new airport, Ishbelia | 595 | 474 | 491 |
| 14 | WABM 1Z | West Abdullah Mubarak | 85 | 167 | 221 |
| 15 | SSUR W | South Surrah, Hiteen, Salam, Zahra, Sideeq, Shuhada | 456 | 453 | 476 |
| 16 | SRRD W | 6th Ring Rd, Salwa, Mishref, Sabah Al‑Salem, Rumaithiya | 795 | 787 | 830 |
| 17 | SALM W,X | Salmiya, E. Hawalli, Ras, Bayan, Jabriya, Failaka | 999 | 997 | 1,032 |
| 18 | JABR W | Jabriya, Dasma, embassies, Hawalli, Rawda, Surra | 510 | 504 | 530 |
| 19 | SDIQ W | Siddiq, Qadsiya, Surra, Hawalli, Daiya, Nuzha, Abdullah Salem, Farwaniya, Khaitan, Rai | 565 | 559 | 584 |
| 20 | FRRD W | Khaitan, Edaliya, Khaldiya, Qurtuba, Yarmouk, Farwaniya, old airport, Rabya | 560 | 515 | 556 |
| 21 | UNIV W | University, Farwaniya, S. Ardiya, Jaleeb | 220 | 337 | 346 |
| 22 | SHKH W | Watia, Shuwaikh, port, KISR, Kifan, Shamiya (124 MW fed from SHGT) | 425 | 222 | 345 |
| 23 | KIFN W | Kifan, Shamiya, Fayhaa | 92 | 206 | 214 |
| 24 | TOWN W | City, Dasman, Murgab, Sharq, Abdullah Salem, Bneid Al‑Gar | 337 | 447 | 451 |
| 25 | GBLT W | Mirgab, Jibla, Amiri (54 MW fed from SHGT) | 112 | 19 | 60 |
| 26 | FINT W | Fintas, Mahboula, Abu Halifa, Zahr, Riqqa, Egaila, Sabhan | 597 | 569 | 583 |
| 27 | ABFT Z | Abu Fatira, Masilah, Egaila, Fintas | 272 | 328 | 347 |
| 28 | FNTS Z | Masilah, Sabah Al‑Salem, Funaitees | 193 | 214 | 246 |
| 29 | QURN W | Sabhan, Middle Area, S. Sabah Al‑Salem | 175 | 192 | 198 |
| 30 | SSSM W | S. Sabah Al‑Salem, Funaitees, Abu Fatira | 523 | 536 | 559 |
| 31 | AHMD W | Ahmadi, Fahd Al‑Ahmad, Sabahiya, Mangaf, Riqqa, Hadiya, Adan hospital | 655 | 638 | 652 |
| 32 | SHUB W,X | Shuaiba (non-major), Fahaheel, Mina Abdullah, Um Al‑Hayman, Sabahiya, Zour, Khiran Pearl | 660 | 809 | 659 |
| 33 | Major industries | KNPC/KIPIC refineries, KCFC, PIC, Burgan field, Wafra wells, LPG, steel, cement and others | 1,058 | 1,281 | 1,428 |
| 34 | UMHN W | New 2022, not loaded | – | 0 | 0 |
| 35 | SBAH 1Z–4Z | Sabah Al‑Ahmad | 276 | 322 | 349 |
| 36 | WAFR Z | Wafra | 119 | 131 | 175 |
| 37 | KHRN Z | Khiran | 29 | 57 | 88 |
| | **Total** | | **15,670** | **16,180** | **16,940** |

Mapping these areas to governorates is the user's own step; no official crosswalk was found. As a rough guide:
- Jahra: rows 3–9 and part of 10–11.
- Capital: rows 12, 22–25.
- Hawalli: rows 15–19.
- Farwaniya: rows 11–13, 20–21.
- Mubarak Al‑Kabeer: rows 26–30 in part.
- Ahmadi: rows 2, 31–37.

Other governorate-level MEW tables [V, MEW YB 2023 p.~108–109]:
- "Electrical Installations (Load in kW) & Numbers for Governorates During 2023". This covers **new connections only**: 5,277 installations, 1,110,151 kW. By governorate (count / kW):

  | Governorate | Count | kW |
  |---|---|---|
  | Al‑Asimah | 454 | 199,929 |
  | Hawalli | 436 | 79,338 |
  | Al‑Ahmadi | 1,590 | 436,517 |
  | Al‑Farwaniyah | 1,314 | 159,030 |
  | Al‑Jahra | 1,027 | 138,912 |
  | Mubarak Al‑Kabir | 456 | 96,426 |

- Number of electricity customers by governorate at 31/12/2023 (chart pages).

No published load-by-governorate time series or area-control-centre split was found. A web search for MEW area control centres returned nothing Kuwait-specific apart from an ABB note on the National Control Centre at Shuwaikh (water SCADA) [S].

### C5. Other grid notes
- The MEW YB 2023 future-capacity table lists:
  - Sabiya CCGT‑3 (870 MW) and CCGT‑4 (900 MW).
  - Az‑Zour South OCGT‑3 (750 MW).
  - Az‑Zour North Ph1 (1,560 MW) and Ph2&3 (2,700 MW).
  - Khiran Ph1 (1,800 MW) and Nuwaiseeb (3,600 MW).
  - Shagaya 2–5 (4,500 MW) and the Sabiya rooftop PV (24 MW).
  - Total installed rises from 18,960 to 32,734 MW over the planning horizon [V].
- Available capacity at 31/12/2023: total 20,250 MW, of which gas turbines 8,116, steam 8,970, combined cycle 3,094 and renewables 70 [V, MEW YB 2023 p.39].
- US ITA notes that MEW plans 31 HV substations (132/300/400 kV) in FY ending March 2027 [S, trade.gov "Kuwait Power Transmission Grid Expansion"].

---

## Local files produced this session
- `/tmp/claude-0/-home-user/7e37b7f1-376b-5bc0-aac0-e208babf511f/scratchpad/water/` contains:
  - The water yearbook PDFs: `w2018.pdf` (data 2017), `w2020.pdf` (data 2020), `w2021.pdf` (data 2021) and `brack2023-06.pdf`.
  - Their `pdftotext -layout` text files.
- The existing MEW/CSB text is in `/tmp/claude-0/-home-user/7e37b7f1-376b-5bc0-aac0-e208babf511f/scratchpad/txt/`. The CSB workbooks are in `/tmp/claude-0/-home-user/7e37b7f1-376b-5bc0-aac0-e208babf511f/scratchpad/dl/csb/`.

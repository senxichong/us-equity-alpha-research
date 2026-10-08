# Timing audit

survivorship_biased = true; candidate_selection_biased = true

All prices below are read independently from the frozen Phase 2 panel. Adjusted opens are checked against vendor open × adj_close / close. Session offsets are checked against XNYS; no missing bar is skipped. UTC timestamps preserve daylight saving and early-close schedules. Null means unavailable, not a zero return.

| Ticker / case | Signal / latest factor input | After-close marker UTC | Entry session / adjusted open (vendor open) | 5D exit session / adjusted open (vendor open) | FWD_RET_5D | eligible / target available |
|---|---|---|---|---|---|---|
| AAPL: normal | 2022-06-10 / 2022-06-10 00:00:00 | 2022-06-10 20:00:00.000000001+00:00 | 2022-06-13 / 130.1430272 (132.8699951) | 2022-06-21 / 130.6817223 (133.4199982) | 0.004139254331 | True / True |
| AAPL: near Independence Day | 2022-07-01 / 2022-07-01 00:00:00 | 2022-07-01 20:00:00.000000001+00:00 | 2022-07-05 / 134.9424545 (137.7700043) | 2022-07-12 / 142.7684557 (145.7599945) | 0.05799510061 | True / True |
| AAPL: dataset end | 2026-10-07 / 2026-10-07 00:00:00 | 2026-10-07 20:00:00.000000001+00:00 | 2026-10-08 / null (null) | 2026-10-15 / null (null) | null | True / False |
| MSFT: normal | 2022-06-10 / 2022-06-10 00:00:00 | 2022-06-10 20:00:00.000000001+00:00 | 2022-06-13 / 236.7064569 (245.1100006) | 2022-06-21 / 241.6798737 (250.2599945) | 0.02101090491 | True / True |
| MSFT: near Independence Day | 2022-07-01 / 2022-07-01 00:00:00 | 2022-07-01 20:00:00.000000001+00:00 | 2022-07-05 / 247.3776046 (256.1600037) | 2022-07-12 / 256.764334 (265.8800049) | 0.03794494378 | True / True |
| MSFT: dataset end | 2026-10-07 / 2026-10-07 00:00:00 | 2026-10-07 20:00:00.000000001+00:00 | 2026-10-08 / null (null) | 2026-10-15 / null (null) | null | True / False |
| NVDA: normal | 2022-06-10 / 2022-06-10 00:00:00 | 2022-06-10 20:00:00.000000001+00:00 | 2022-06-13 / 15.93786971 (16) | 2022-06-21 / 16.4110246 (16.47500038) | 0.02968746172 | True / True |
| NVDA: near Independence Day | 2022-07-01 / 2022-07-01 00:00:00 | 2022-07-01 20:00:00.000000001+00:00 | 2022-07-05 / 14.11995752 (14.17500019) | 2022-07-12 / 15.20871032 (15.26799965) | 0.07710737095 | True / True |
| NVDA: dataset end | 2026-10-07 / 2026-10-07 00:00:00 | 2026-10-07 20:00:00.000000001+00:00 | 2026-10-08 / null (null) | 2026-10-15 / null (null) | null | True / False |
| META: normal | 2022-06-10 / 2022-06-10 00:00:00 | 2022-06-10 20:00:00.000000001+00:00 | 2022-06-13 / 168.9716093 (170.5899963) | 2022-06-21 / 164.3558193 (165.9299927) | -0.02731695601 | True / True |
| META: near Independence Day | 2022-07-01 / 2022-07-01 00:00:00 | 2022-07-01 20:00:00.000000001+00:00 | 2022-07-05 / 156.6397461 (158.1399994) | 2022-07-12 / 163.2365685 (164.8000031) | 0.04211461348 | True / True |
| META: dataset end | 2026-10-07 / 2026-10-07 00:00:00 | 2026-10-07 20:00:00.000000001+00:00 | 2026-10-08 / null (null) | 2026-10-15 / null (null) | null | True / False |
| UBER: normal | 2022-06-10 / 2022-06-10 00:00:00 | 2022-06-10 20:00:00.000000001+00:00 | 2022-06-13 / 22.21999931 (22.21999931) | 2022-06-21 / 22 (22) | -0.009900959503 | True / True |
| UBER: near Independence Day | 2022-07-01 / 2022-07-01 00:00:00 | 2022-07-01 20:00:00.000000001+00:00 | 2022-07-05 / 21.17000008 (21.17000008) | 2022-07-12 / 21.28000069 (21.28000069) | 0.005196060933 | True / True |
| UBER: dataset end | 2026-10-07 / 2026-10-07 00:00:00 | 2026-10-07 20:00:00.000000001+00:00 | 2026-10-08 / null (null) | 2026-10-15 / null (null) | null | True / False |
| UBER: first available history; not eligible | 2019-05-10 / 2019-05-10 00:00:00 | 2019-05-10 20:00:00.000000001+00:00 | 2019-05-13 / 38.79000092 (38.79000092) | 2019-05-20 / 41.18999863 (41.18999863) | 0.06187155593 | False / True |
| CHTR: next scheduled entry missing/zero volume | 2010-01-05 / 2010-01-05 00:00:00 | 2010-01-05 21:00:00.000000001+00:00 | 2010-01-06 / null (null) | 2010-01-13 / 33.00999832 (33.00999832) | null | False / False |
| CHTR: invalid signal observation | 2010-01-06 / NaT | 2010-01-06 21:00:00.000000001+00:00 | 2010-01-07 / 35.25 (35.25) | 2010-01-14 / 32.75 (32.75) | -0.07092198582 | False / True |

18 independent source traces passed. The 2022-07-01 signals enter on July 5; the five-session exit is July 12. An IPO/first-history row can have a calculable future label while being ineligible at t; a final-date signal can be eligible while its label is unavailable. These are deliberately separate states.

No execution cash ledger is certified. Both adjusted and vendor prices retain Yahoo retrospective normalization. See TIMING_CONVENTION.md.

# Phase 3 — Factor engine, target alignment and leakage tests

survivorship_biased = true; candidate_selection_biased = true

**PASS is limited to the frozen, biased prototype research interface. No predictive evaluation was performed.**

Dataset `20261008T141100218333Z`: 1,563,421 rows, 393 candidates, 4216 sessions; 2010-01-04 through 2026-10-07.
Source Phase 2 ID `20261008T085506951888Z`, SHA-256 `a095e7b3bad2f6ee19ca507e640895e5d6568d5c0fde46d29f80758c437be55a`. Source Phase 2.5 mask SHA-256 `b8855d9099da55f180696f7596581b2e8c3a72ff129585f04c9b40208b93b028`. Upstream file inventory, panel bytes and eligibility mask were preserved; no rebuild or download.

## Timing

**After close(t) and completed-bar availability, form the signal; buy at scheduled open(t+1), and measure the primary return from that open to scheduled open(t+6).** The h-day label exits at open(t+h+1), h=1/5/10/20. The after-close +1ns timestamp is a logical ordering marker, not measured feed latency. Actual bar delivery before next open remains an assumption. Prices at both endpoints use the frozen adjusted-open basis; this is a research label proxy, not certified executable cash PnL. Detailed timestamp/price definitions are in TIMING_CONVENTION.md. Overlapping targets require later purging/embargo and dependence-aware inference; no portfolio cohorts are constructed here.

## Eligibility and missing sessions

The unchanged Phase 2.5 mask yields 1,442,588 eligible rows. It is past-only conditional on the frozen candidates/values: valid t, 252 valid observations through t, 60 complete trailing sessions, median vendor Close×Volume >= USD10m. Future eligibility cannot change historical membership. This is not PIT index membership or proof of real-time vendor vintage.
Invalid/zero-volume/missing sessions remain calendar positions and are never filled or dropped to shorten a lookback. Factor availability is separate from eligibility, entry/exit validity and target availability. Missing scheduled entry/exit prices yield null targets, without delaying endpoints. Future target availability never affects normalization membership. Intermediate holding-period gaps do not erase an otherwise calculable endpoint label and do not prove continuous tradability.

## Factors and preprocessing

| Factor | Required sessions |
|---|---:|
| RET_5 | 6 |
| RET_10 | 11 |
| RET_20 | 21 |
| RET_60 | 61 |
| REV_5 | 6 |
| VOL_10 | 11 |
| VOL_20 | 21 |
| VOL_60 | 61 |
| ILLIQ_20 | 21 |
| DOLLAR_VOLUME_20 | 20 |
| VOLUME_RATIO_20 | 21 |
| VOLUME_SURPRISE_20 | 21 |
| PRICE_MA20 | 20 |
| PRICE_MA60 | 60 |
| DIST_52W_HIGH | 252 |
| INTRADAY_RANGE | 1 |
| OPEN_CLOSE_RETURN | 1 |

All 17 factors, their raw values, winsorized values and z-scores are retained, including exact sign duplicate REV_5. Volume-based fields use the vendor activity proxy, not share turnover. Factor-specific windows are complete and trailing. Definitions/formulas/units are in FACTOR_DEFINITIONS.md and reports/phase3/factor_metadata.json. Beta is deferred without an approved benchmark; size and neutralization are deferred without PIT inputs.
At each date/factor: eligible-at-t finite raw values define 1%/99% linear winsorization, then population z-score. Fewer than two names or zero variance -> null processed values. No target, future row or future complete-case flag participates; no global fitting, model, training/test split or scaler is introduced.

## Diagnostics and validation

Full suite: **68 passed, 0 failed, 0 errors, 0 skipped; 28 warnings**. Logs and JUnit are retained under reports/phase3. Warnings are unsuppressed NumPy generic-timedelta deprecations in pandas/exchange-calendars; they indicate a future dependency compatibility issue, not a hidden failed assertion.
Artifact checks: 24/24 passed; 18 independent real-data timing traces across at least five tickers, normal/holiday/missing/IPO/end dates. Exact Parquet read-back matches the in-memory matrix.
Adversarial tests hand-check every formula and pandas shift(+1/−1/+5/−5); insert present and absent missing bars; separate IPO histories and tickers; mutate all future numeric fields and validity; truncate future rows; remove scheduled future entry/exit observations; change future liquidity; inject targets/availability into transform input; and append an extreme future test-period cross section. Historical features, eligibility and normalization remain unchanged. Real AAPL/META/UBER prefix checks also pass.
Complete raw-factor rows: 1,462,181. Primary complete-feature, eligible, target-available rows: 1,438,498. This count is a label-availability diagnostic, never the historical normalization population.
factor_coverage.csv records date-level eligible denominators and factor-specific raw/processed coverage. factor_summary.csv records finite counts, nonnull rates, mean/std/quantiles, infinities, fixed-threshold extremes and earliest dates. target_summary.csv reports all-row and eligible-at-t label distributions and missingness separately. Extremes are flags only, not removals; these descriptive statistics are not strategy performance. Final h+1 signal sessions have no h-day labels.

## Artifacts and remaining risks

Frozen matrix: `data\processed\phase3\20261008T141100218333Z\research_matrix.parquet`; SHA-256 `0da610d74a63cfd48c003dce4372933eb14c5e4b365b0dbe11ae10df0b3470cf`. Read with `src.factors.dataset.load_factor_panel()`. Versioned source/config/rule/code/dependency hashes, test evidence and diagnostics are in reports/phase3/validation.json and the dataset metadata. Raw/processed factor and independent sample/label flags are retained for every original source key.
The frozen current-member universe remains survivorship-biased and candidate-selection-biased. Global short-history/full-period gaps/extreme-event/complex-action exclusions are not all demonstrated vendor corruption and remain economic selection bias; no quarantine decision was changed. PIT membership, delisting outcomes, permanent identity, historical share basis and full corporate-action cash economics remain unresolved. Retrospective adjustment revisions can alter historical levels. Next-open prices and bar latency are indicative assumptions, not certified fills. No IC, RankIC, quantile returns, models, portfolio returns, Sharpe or parameter optimization was computed. Work stops at Phase 3.

PHASE 3: PASS

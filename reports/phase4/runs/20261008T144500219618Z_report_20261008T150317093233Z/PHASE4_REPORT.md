# Phase 4 — Single-factor research and linear baselines

**survivorship_biased = true; candidate_selection_biased = true**

**PASS: methodological/reproducibility gate, not a positive-alpha or profitability claim.**

## Dataset

Frozen Phase 3 dataset `20261008T141100218333Z`: 1,563,421 source rows, 393 candidates, 4216 exchange sessions. Source SHA-256 `0da610d74a63cfd48c003dce4372933eb14c5e4b365b0dbe11ae10df0b3470cf`; source bytes and all upstream inventories remain unchanged.
The actual first scored primary cross section is 2010-12-31; latest is 2026-09-29. Each factor scores 3,959–3,959 dates, 393–393 distinct stocks and 1,438,498–1,440,211 stock-date pairs. Exact individual counts remain in factor_statistics.csv. The 252-observation eligibility warm-up is not bypassed. Model history starts in 2011 and test folds start in 2017.

## Single-factor findings

Highest raw signed mean RankIC: ILLIQ_20 (0.01395); largest absolute primary RankIC HAC t: ILLIQ_20 (4.23). The weakest magnitude is VOLUME_RATIO_20 (0.00048, HAC t=0.27). Negative means are retained and are not automatically failures.

| factor | IC_mean | RankIC_mean | RankIC_hac_t | RankIC_hac_t_lag20 | RankIC_hac_BH_q | rankic_years_same_sign_as_full | complete_years |
|---|---|---|---|---|---|---|---|
| ILLIQ_20 | 0.0183117 | 0.0139539 | 4.22952 | 3.92765 | 0.000398131 | 14 | 15 |
| VOL_60 | 0.0262755 | 0.0138369 | 1.82458 | 1.69296 | 0.105191 | 11 | 15 |
| REV_5 | 0.0141425 | 0.0132162 | 2.92373 | 2.77069 | 0.0117594 | 11 | 15 |
| VOL_10 | 0.020476 | 0.0123642 | 1.97745 | 1.85994 | 0.0978501 | 11 | 15 |
| VOL_20 | 0.0228605 | 0.0121118 | 1.75346 | 1.62301 | 0.112657 | 11 | 15 |

Strongest absolute HAC evidence (direction preserved):

| factor | IC_mean | RankIC_mean | RankIC_hac_t | RankIC_hac_t_lag20 | RankIC_hac_BH_q | rankic_years_same_sign_as_full | complete_years |
|---|---|---|---|---|---|---|---|
| ILLIQ_20 | 0.0183117 | 0.0139539 | 4.22952 | 3.92765 | 0.000398131 | 14 | 15 |
| OPEN_CLOSE_RETURN | -0.00974635 | -0.00884709 | -3.59108 | -3.70757 | 0.00279911 | 12 | 15 |
| DOLLAR_VOLUME_20 | 0.0043694 | -0.00990498 | -3.17038 | -2.93161 | 0.00862706 | 11 | 15 |
| RET_5 | -0.0141425 | -0.0132162 | -2.92373 | -2.77069 | 0.0117594 | 11 | 15 |
| REV_5 | 0.0141425 | 0.0132162 | 2.92373 | 2.77069 | 0.0117594 | 11 | 15 |
| PRICE_MA20 | -0.012997 | -0.0127468 | -2.52975 | -2.42543 | 0.0323405 | 13 | 15 |

Weakest magnitude / inconclusive ranking rows, retained unchanged:

| factor | IC_mean | RankIC_mean | RankIC_hac_t | RankIC_hac_t_lag20 | RankIC_hac_BH_q | rankic_years_same_sign_as_full | complete_years |
|---|---|---|---|---|---|---|---|
| VOLUME_RATIO_20 | 0.00201249 | 0.000484616 | 0.273204 | 0.248879 | 0.784696 | 10 | 15 |
| VOLUME_SURPRISE_20 | 0.00258506 | 0.00159936 | 0.951018 | 0.872288 | 0.387141 | 9 | 15 |
| DIST_52W_HIGH | -0.0145834 | -0.00501017 | -0.758234 | -0.71717 | 0.47633 | 8 | 15 |
| RET_60 | -0.00452302 | -0.00645281 | -1.16645 | -1.16262 | 0.295595 | 10 | 15 |

Most consistent full-period sign across complete calendar years (2011–2025):

| factor | rankic_years_same_sign_as_full | complete_years | min_yearly_rankic | max_yearly_rankic |
|---|---|---|---|---|
| ILLIQ_20 | 14 | 15 | -4.65405e-05 | 0.0349805 |
| PRICE_MA20 | 13 | 15 | -0.0304329 | 0.0204196 |
| RET_10 | 13 | 15 | -0.0317112 | 0.0295711 |
| OPEN_CLOSE_RETURN | 12 | 15 | -0.0311709 | 0.00499766 |
| RET_20 | 12 | 15 | -0.0477541 | 0.0198633 |

All positive/negative yearly counts, uncertainty and rolling estimates are available; no factor is proclaimed stable solely from its full-period mean.

## Redundancy

| factor_a | factor_b | mean_daily_spearman |
|---|---|---|
| RET_5 | REV_5 | -1 |
| RET_10 | PRICE_MA20 | 0.894729 |
| RET_20 | PRICE_MA20 | 0.831917 |
| RET_60 | PRICE_MA60 | 0.838213 |
| VOL_10 | VOL_20 | 0.826136 |
| VOL_20 | VOL_60 | 0.816664 |
| ILLIQ_20 | DOLLAR_VOLUME_20 | -0.928041 |
| VOLUME_RATIO_20 | VOLUME_SURPRISE_20 | 0.933452 |

The exact RET_5/REV_5 inverse is one effect. Related windows and liquidity/activity proxies are not independent discoveries. Only REV_5 was removed from model inputs by definition, before performance.

## Quantile monotonicity

| factor | monotonicity_score | spread_bp | top_minus_bottom_hac_t | spread_years_same_sign_as_full | spread_complete_years |
|---|---|---|---|---|---|
| RET_5 | -1 | -15.5851 | -2.67487 | 13 | 15 |
| RET_10 | -0.9 | -11.5802 | -1.92105 | 13 | 15 |
| RET_20 | -1 | -11.0217 | -1.80453 | 12 | 15 |
| RET_60 | -0.4 | -11.2063 | -1.6407 | 11 | 15 |
| REV_5 | 1 | 15.5851 | 2.67487 | 13 | 15 |
| VOL_10 | 1 | 21.7607 | 3.08663 | 11 | 15 |
| VOL_20 | 1 | 22.2926 | 2.86145 | 10 | 15 |
| VOL_60 | 1 | 25.5765 | 3.036 | 11 | 15 |
| ILLIQ_20 | 0.9 | 15.9676 | 4.50183 | 15 | 15 |
| DOLLAR_VOLUME_20 | -0.3 | -8.67499 | -2.47935 | 12 | 15 |
| VOLUME_RATIO_20 | 0.4 | 0.986951 | 0.476646 | 9 | 15 |
| VOLUME_SURPRISE_20 | 0.3 | 2.78795 | 1.43001 | 10 | 15 |
| PRICE_MA20 | -1 | -13.4724 | -2.17387 | 12 | 15 |
| PRICE_MA60 | -0.7 | -11.3747 | -1.72297 | 12 | 15 |
| DIST_52W_HIGH | -1 | -17.1478 | -2.20395 | 11 | 15 |
| INTRADAY_RANGE | 1 | 18.2827 | 3.13437 | 12 | 15 |
| OPEN_CLOSE_RETURN | -0.9 | -10.8637 | -3.48614 | 13 | 15 |

These are raw-sign Q5−Q1 overlapping forward-return diagnostics. Strong aggregate ordering can coexist with weak or unstable RankIC, and significant mean association can lack a clean ordering. The annual sign counts expose this distinction; no spread is compounded into a strategy or Sharpe.

## Linear OOS baselines

Equal Weight OOS RankIC is 0.01931, versus the strongest raw-signed individual factor on the identical OOS sample, VOL_20 (0.01805). Thus Equal Weight exceeds that individual-factor ranking mean. Ridge has RankIC 0.02014, above Equal Weight. Lasso has the highest observed OOS RankIC (0.02238) among the five fixed baselines. These are observed comparisons, not proof that differences are statistically significant.

| model | observations | valid_dates | IC_mean | RankIC_mean | IC_IR | RankIC_IR | RankIC_hac_t | MSE | MAE | R2 |
|---|---|---|---|---|---|---|---|---|---|---|
| ElasticNet | 928158 | 2448 | 0.0279909 | 0.0200078 | 0.147986 | 0.101282 | 2.78475 | 0.00212525 | 0.0317902 | 0.000473 |
| EqualWeight | 928158 | 2448 | 0.0248572 | 0.0193064 | 0.11896 | 0.0910444 | 2.50902 | 0.00212533 | 0.03179 | 0.000438776 |
| Lasso | 928158 | 2448 | 0.0298962 | 0.022378 | 0.15305 | 0.108844 | 2.99999 | 0.00212491 | 0.0317879 | 0.000635715 |
| OLS | 928158 | 2448 | 0.0293762 | 0.0222028 | 0.152725 | 0.111022 | 3.10343 | 0.00212484 | 0.0317888 | 0.000668953 |
| Ridge | 928158 | 2448 | 0.0268344 | 0.0201354 | 0.127141 | 0.093954 | 2.59734 | 0.00212534 | 0.0317877 | 0.000430637 |

Primary Phase 5 benchmark remains preregistered **Ridge**, RankIC 0.02014. Also compare against the strongest observed simple model, **Lasso**, RankIC 0.02238, and Equal Weight. The latter observed ranking is not a new test-tuned model specification.

## Stability

| year | ElasticNet | EqualWeight | Lasso | OLS | Ridge |
|---|---|---|---|---|---|
| 2017 | 0.016094 | 0.013707 | 0.0228456 | 0.0291818 | 0.0168594 |
| 2018 | 0.0145719 | 0.0169402 | 0.0255762 | 0.0228114 | 0.0228879 |
| 2019 | 0.0416487 | 0.0429228 | 0.0416119 | 0.0421953 | 0.0421344 |
| 2020 | 0.0138882 | 0.0165644 | 0.0147526 | 0.0133344 | 0.0126139 |
| 2021 | 0.0130803 | 0.0154686 | 0.0126217 | 0.0141106 | 0.0136381 |
| 2022 | -0.00719087 | -0.00221637 | -0.00662299 | -0.00763561 | -0.00897348 |
| 2023 | 0.0428385 | 0.0415147 | 0.0437106 | 0.0413817 | 0.0414479 |
| 2024 | 0.0136355 | 0.00685913 | 0.0142591 | 0.0131805 | 0.0134974 |
| 2025 | 0.0280519 | 0.0233502 | 0.0291662 | 0.0257895 | 0.0257522 |
| 2026 | 0.0248529 | 0.0176119 | 0.0273016 | 0.0297944 | 0.0221492 |

| model | coefficient_sign_changes | near_zero_factor_folds | largest_absolute_coefficient | most_variable_coefficient |
|---|---|---|---|---|
| ElasticNet | 7 | 62 | 0.000852278 | PRICE_MA20 |
| Lasso | 4 | 53 | 0.000673032 | PRICE_MA20 |
| OLS | 22 | 0 | 0.00111516 | RET_10 |
| Ridge | 31 | 0 | 0.000827373 | PRICE_MA20 |

All five models have negative mean RankIC in 2022; the stronger years include 2023, 2019. The aggregate positive association is not uniform across regimes. Calendar patterns alone do not establish their economic cause.

OLS has 22 adjacent nonzero coefficient sign changes across the ten folds and maximum absolute loading 0.001115 per Phase 3 z-score unit. Its coefficients are not numerically explosive, but their signs vary. Ridge has 31 such changes; changing validation-selected penalties does not uniformly stabilize signs. Lasso adds 0.00307 mean OOS RankIC versus Equal Weight and 0.00018 versus OLS. ElasticNet has RankIC 0.02001, below Ridge. The gains are small and no paired difference significance is claimed; sparsity alone is not evidence of better generalization.

The complete yearly and ablation tables retain regime dependence and coefficient instability. Neither a favorable year nor a best-looking factor family changes the specification. OOS correlation differences are descriptive comparisons unless supported by a paired model-comparison test; no such significance claim is made.

## Statistical caution and known bias

Daily 5D labels overlap, so IID t-statistics overstate precision when ICs are serially correlated. Primary inference uses Bartlett Newey-West lag 5, plus fixed lag-20 sensitivity, on the exchange-session grid. ICIR is unannualized mean/std. HAC does not remove universe bias or guarantee that a five-lag bandwidth captures all dependence. BH q-values separately cover the 17 primary IC and 17 primary RankIC tests; correlated factors, secondary horizons and researcher exposure still create multiple-testing/data-snooping concerns. No p-value alone establishes discovery.

These are conditional associations in a frozen current-member universe, not unbiased historical strategy evidence. Global candidate/quarantine selection, retrospective vendor revisions, unresolved identity/delistings and indicative adjusted-open prices remain. Risk/industry/size neutrality is not established. No transaction costs, auction-fill realism, borrow or overlapping-capital accounting are modeled.

No current membership is treated as historical PIT membership. Future target availability affects only evaluation/training labels, not signal-date eligibility, normalization or quantile formation. This first descriptive research phase exposes the historical sample; chronological OOS fitting is not an untouched external replication.

## Tests, artifacts and stopping condition

Complete suite: **87 passed, 0 failed, 0 errors, 0 skipped; 37 warnings**. These are visible generic-timedelta deprecations in the installed NumPy/pandas/calendar combination; logs are preserved. The initial two quantile-column implementation failures and correction remain in RESEARCH_LOG.md. Custom HAC matches statsmodels. Tests cover daily versus pooled correlation, tied ranks, minimum cross sections, no future-label quantile formation, purged fold boundaries, train-only scalers/orientations, test-target mutation, future-fold mutation, row-order invariance and test-only tagging.
Artifact checks: 28/28 passed. Ten saved test-prediction Parquets were checksum/read-back audited for exact sample keys, fold tags, label availability and squared/absolute-error sums. All tried configurations are retained; solver convergence warnings were checked. Eight fixed diagnostic figures were rendered. No source data was downloaded or rebuilt.
See [single-factor report](reports/single_factor_report.md), [baseline report](reports/baseline_report.md), [preregistered protocol](PHASE4_PROTOCOL.md), and reports/phase4/validation.json. No new factors, complex ML, capital-aware portfolio, strategy Sharpe or transaction-cost optimization was run. Stop after Phase 4.

PHASE 4: PASS

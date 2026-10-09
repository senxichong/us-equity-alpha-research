# Phase 5 failure analysis

survivorship_biased = true; candidate_selection_biased = true; point_in_time_membership = false

No year-specific retuning or model changes followed these results. The comparison includes all negative years, each model's two lowest-RankIC years, and 2022. This descriptive rule selects years for diagnosis only. 2026 is incomplete.

## Negative years and 2022

| model | year | RankIC_mean |
| --- | --- | --- |
| Ridge | 2022 | -0.008973 |
| RandomForest | 2022 | -0.001858 |

| model | IC_mean | RankIC_mean | RankIC_hac_t | RankIC_ci95_low | RankIC_ci95_high |
| --- | --- | --- | --- | --- | --- |
| Ridge | -0.009795 | -0.008973 | -0.291677 | -0.069272 | 0.051325 |
| RandomForest | -0.002888 | -0.001858 | -0.112500 | -0.034224 | 0.030508 |
| LightGBM | 0.018318 | 0.011325 | 0.874474 | -0.014058 | 0.036708 |

In 2022 Ridge RankIC was -0.008973; RandomForest remained negative at -0.001858 but failed less severely; LightGBM changed the sign to 0.011325. LightGBM beat Ridge in only 2/10 years overall, so its 2022 advantage did not imply broad improvement. Ridge's stronger 2019/2023 results are visible in the full annual table. These descriptive outcomes did not trigger any tuning.

RandomForest beats Ridge in 4/10 years and loses in 6/10. Improvement is neither uniform nor proof of a persistent nonlinear mechanism. Annual confidence intervals and overlapping targets limit year-level causal interpretation.

## Prediction distribution and collapse

| model | year | mean | std | median_daily_cs_std | min_daily_cs_std | p01 | p99 | minimum | maximum | near_constant_dates | extreme_abs_gt_50pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ridge | 2020 | 0.003062 | 0.000213 | 0.000211 | 0.000110 | 0.002651 | 0.003680 | 0.002203 | 0.004296 | 0 | 0 |
| RandomForest | 2020 | 0.002928 | 0.000635 | 0.000543 | 0.000369 | 0.002248 | 0.005175 | -0.002088 | 0.020353 | 0 | 0 |
| LightGBM | 2020 | 0.003026 | 0.001239 | 0.001196 | 0.000750 | 0.001037 | 0.007910 | -0.005395 | 0.019998 | 0 | 0 |
| Ridge | 2022 | 0.003683 | 0.000333 | 0.000335 | 0.000200 | 0.003097 | 0.004738 | 0.002712 | 0.005435 | 0 | 0 |
| RandomForest | 2022 | 0.003921 | 0.001293 | 0.001231 | 0.000799 | 0.002773 | 0.009067 | -0.001374 | 0.025270 | 0 | 0 |
| LightGBM | 2022 | 0.004232 | 0.002156 | 0.002116 | 0.001506 | 0.001449 | 0.011904 | -0.011672 | 0.026367 | 0 | 0 |
| Ridge | 2024 | 0.003371 | 0.001070 | 0.001072 | 0.000836 | 0.001350 | 0.006574 | -0.000150 | 0.010215 | 0 | 0 |
| RandomForest | 2024 | 0.003223 | 0.000899 | 0.000822 | 0.000595 | 0.002052 | 0.006858 | -0.003559 | 0.016839 | 0 | 0 |
| LightGBM | 2024 | 0.002912 | 0.001461 | 0.001433 | 0.001052 | 0.000051 | 0.008262 | -0.008444 | 0.021639 | 0 | 0 |

Fixed descriptive flags are daily cross-sectional standard deviation below 1e-10 and absolute prediction above 50%. They are diagnostics, not tuning criteria. Total nearly constant dates: 0; extreme predictions: 0. Full yearly distributions, including strong years, are in prediction_distributions.csv.

## Feature distribution

| fold | feature | mean | std | p01 | median | p99 | median_daily_cs_std |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020 | RET_5 | 0.000633 | 0.998729 | -2.407677 | -0.025536 | 2.705843 | 1.001274 |
| 2020 | VOL_20 | 0.000302 | 0.999624 | -1.559820 | -0.193657 | 3.341777 | 1.001686 |
| 2020 | ILLIQ_20 | -0.007746 | 0.989413 | -0.994135 | -0.301117 | 4.387822 | 0.992455 |
| 2020 | PRICE_MA20 | 0.001290 | 0.998384 | -2.353096 | -0.025935 | 2.678330 | 1.001257 |
| 2022 | RET_5 | 0.000000 | 1.000005 | -2.707198 | 0.017515 | 2.551844 | 1.001298 |
| 2022 | VOL_20 | 0.000000 | 1.000005 | -1.477589 | -0.210646 | 3.421938 | 1.001298 |
| 2022 | ILLIQ_20 | 0.000000 | 1.000005 | -1.055893 | -0.250631 | 4.914692 | 1.001298 |
| 2022 | PRICE_MA20 | -0.000000 | 1.000005 | -2.731512 | 0.031959 | 2.461773 | 1.001298 |
| 2024 | RET_5 | -0.000000 | 1.000005 | -2.610677 | -0.032567 | 2.877554 | 1.001288 |
| 2024 | VOL_20 | 0.000000 | 1.000005 | -1.302697 | -0.263347 | 3.619325 | 1.001288 |
| 2024 | ILLIQ_20 | 0.000000 | 1.000005 | -1.145345 | -0.273672 | 4.005004 | 1.001288 |
| 2024 | PRICE_MA20 | -0.000000 | 1.000005 | -2.542237 | -0.022291 | 2.870824 | 1.001288 |

Features were normalized cross-sectionally upstream. Similar z-score moments do not imply stable relationships with returns. Eligibility and complete-case selection can also shift these moments. All 16 feature distributions are retained for every test year in feature_distributions.csv.

## Factor relationships and importance

| factor | year | RankIC_mean | RankIC_hac_t |
| --- | --- | --- | --- |
| RET_5 | 2020 | -0.036856 | -1.255099 |
| RET_5 | 2022 | -0.025643 | -1.509149 |
| RET_5 | 2024 | -0.016111 | -1.030166 |
| VOL_20 | 2020 | 0.009498 | 0.307459 |
| VOL_20 | 2022 | -0.027313 | -0.836697 |
| VOL_20 | 2024 | 0.009837 | 0.407663 |
| ILLIQ_20 | 2020 | 0.006997 | 0.355217 |
| ILLIQ_20 | 2022 | 0.006745 | 0.675039 |
| ILLIQ_20 | 2024 | 0.001739 | 0.118531 |
| PRICE_MA20 | 2020 | -0.012741 | -0.428696 |
| PRICE_MA20 | 2022 | -0.023044 | -1.148681 |
| PRICE_MA20 | 2024 | -0.020935 | -1.056896 |

These raw-sign factor statistics are reused from Phase 4 and use each factor's upstream available sample, not the model's stricter complete-case sample. They are contextual evidence, not an exact decomposition of model IC.

| model | year | top_three_native |
| --- | --- | --- |
| RandomForest | 2020 | VOL_60, DOLLAR_VOLUME_20, ILLIQ_20 |
| RandomForest | 2022 | VOL_60, DIST_52W_HIGH, RET_60 |
| RandomForest | 2024 | VOL_60, DOLLAR_VOLUME_20, DIST_52W_HIGH |
| LightGBM | 2020 | DIST_52W_HIGH, ILLIQ_20, DOLLAR_VOLUME_20 |
| LightGBM | 2022 | DIST_52W_HIGH, RET_5, ILLIQ_20 |
| LightGBM | 2024 | DIST_52W_HIGH, VOL_60, DOLLAR_VOLUME_20 |

VOL_60 is the most consistently important RF feature, while DIST_52W_HIGH leads LightGBM; each appears in its model’s top three in all ten folds. ILLIQ_20 also recurs. Price-position, volatility, momentum and liquidity families all contribute native importance; no isolated group is established as the causal source of return predictability.

Native importance is learned on training rows, so fold-2022 importance describes the pre-2022 fitted model. Importance changes and raw-factor sign changes offer possible explanations, not identified causes. Correlated factor substitutes and market exposure remain unresolved.

## Disagreement examples

| fold | date | ticker | Ridge | LightGBM | Ridge_percentile | LightGBM_percentile | absolute_rank_gap | target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017 | 2017-10-25 | CMG | 0.004197 | -0.002489 | 1.000000 | 0.002755 | 0.997245 | -0.019394 |
| 2017 | 2017-02-10 | DECK | 0.003865 | -0.009508 | 1.000000 | 0.002762 | 0.997238 | 0.003045 |
| 2017 | 2017-09-21 | KR | 0.003969 | -0.005659 | 1.000000 | 0.005510 | 0.994490 | 0.003455 |
| 2017 | 2017-02-03 | DECK | 0.004205 | -0.004166 | 1.000000 | 0.005525 | 0.994475 | 0.143634 |
| 2017 | 2017-06-16 | KR | 0.004083 | -0.002374 | 1.000000 | 0.005525 | 0.994475 | -0.012625 |
| 2017 | 2017-07-11 | ORLY | 0.003962 | -0.005902 | 0.994490 | 0.002755 | 0.991736 | 0.074584 |
| 2017 | 2017-10-26 | CMG | 0.003952 | -0.004451 | 0.994490 | 0.002755 | 0.991736 | -0.011651 |
| 2017 | 2017-01-24 | LITE | 0.003885 | -0.003014 | 0.994475 | 0.002762 | 0.991713 | -0.001297 |
| 2017 | 2017-03-03 | PANW | 0.004212 | -0.009374 | 0.994475 | 0.002762 | 0.991713 | 0.027344 |
| 2017 | 2017-03-07 | PANW | 0.004105 | -0.006279 | 0.994475 | 0.002762 | 0.991713 | 0.017684 |

The CSV retains ten largest absolute rank gaps per fold and all 16 z-scores. Selection uses only predictions, ties date/ticker; target sign/availability never selects examples. These are examples of ranking disagreement, not proof of profitable interactions.

## Warnings, failures and metadata

LightGBM printed repeated “No further splits with positive gain” warnings. These indicate constrained trees stopped splitting; all attempted primary trials remain recorded, with no parameter relaxation. Native console warning counts were not captured by Python warnings, so no exact count is claimed. The 37 pytest warnings are retained in final_pytest.log.

Primary trial outcomes: {"success": 40}. No failed trial was dropped. Toy tests, independent saved-prediction audits, and controls are recorded separately. A metadata naming issue was found: runtime_details.csv originally labels every no-new-fit result reused_from_phase4, including ValidationWinner/All copied from the Phase 5 primary model. The raw file is preserved. runtime_summary.csv supplies the corrected boolean and explicit reuse_origin. Predictions and fit decisions were unaffected.

## Adversarial controls

| model | RankIC_mean | RankIC_hac_t | RankIC_ci95_low | RankIC_ci95_high |
| --- | --- | --- | --- | --- |
| RandomLabelControl | 0.002076 | 0.672931 | -0.003970 | 0.008122 |

| RankIC_mean | RankIC_hac_t | RankIC_ci95_low | RankIC_ci95_high |
| --- | --- | --- | --- |
| -0.001525 | -1.443691 | -0.003596 | 0.000545 |

| importance_type | mean_normalized_importance | mean_rank | top3_folds |
| --- | --- | --- | --- |
| gain | 0.001584 | 17.000000 | 0 |
| split | 0.003222 | 17.000000 | 0 |

Predeclared investigation flags: {"random_label_requires_investigation": false, "random_feature_importance_requires_investigation": false, "random_feature_rankic_requires_investigation": false}. These controls are finite-sample checks, not proof that all leakage or vendor revisions are absent.

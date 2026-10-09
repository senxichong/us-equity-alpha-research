# Phase 5 report

survivorship_biased = true; candidate_selection_biased = true; point_in_time_membership = false

Research conclusion: **NO RELIABLE IMPROVEMENT**. Descriptive best ML: RandomForest. Ridge remains the predeclared benchmark.

## Upstream integrity, models and selection

Phase 1–4 artifacts unchanged: True. Exact ten Phase 4 folds/sample keys reused: True. No data rebuild/download, factor/target/eligibility change or Phase 6 work. Actual models: reused Ridge, sklearn RandomForestRegressor, LightGBM LGBMRegressor; no fallback. Versions: {"numpy": "2.5.3", "pandas": "2.3.3", "scikit-learn": "1.9.1", "lightgbm": "4.7.0", "scipy": "1.18.1", "pyarrow": "23.0.1", "joblib": "1.6.0"}.

Two fixed configurations per nonlinear family/fold; select validation mean daily RankIC, with MSE then grid-order tie-breaks. Test used only for saved predictions and evaluation. No test fitting, early stopping or tuning. Identity tree preprocessing uses existing z-scores and complete cases; Ridge's training-only scaler is unchanged. Signal after close(t), buy at next adjusted open(t+1), measure return to adjusted open(t+6).

## OOS evidence

| model | IC_mean | RankIC_mean | IC_IR | RankIC_IR | RankIC_hac_t | RankIC_ci95_low | RankIC_ci95_high | MSE | MAE | R2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ridge | 0.026834 | 0.020135 | 0.127141 | 0.093954 | 2.597337 | 0.004941 | 0.035330 | 0.002125 | 0.031788 | 0.000431 |
| RandomForest | 0.023861 | 0.016376 | 0.144468 | 0.113148 | 3.157415 | 0.006211 | 0.026541 | 0.002126 | 0.031792 | 0.000236 |
| LightGBM | 0.025735 | 0.015598 | 0.177264 | 0.126206 | 3.597039 | 0.007099 | 0.024097 | 0.002125 | 0.031795 | 0.000400 |

| model | mean | median | positive_ratio | hac_t | ci95_low | ci95_high | years_better | years_worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RandomForest | -0.003759 | -0.001447 | 0.493873 | -0.857735 | -0.012350 | 0.004831 | 4 | 6 |
| LightGBM | -0.004537 | -0.000505 | 0.498366 | -0.858737 | -0.014892 | 0.005818 | 2 | 8 |

RandomForest paired ΔRankIC vs Ridge: -0.003759, HAC t -0.857735, 95% CI [-0.012350, 0.004831]. Against Lasso: -0.006002, 95% CI [-0.014115, 0.002111]. Descriptive difference vs OLS: -0.005827. Full OOS dates, breadth, medians, positive ratios, errors and inference appear in reports/ml_walkforward_report.md and machine tables.

## Year stability and 2022

| year | Ridge | RandomForest | LightGBM |
| --- | --- | --- | --- |
| 2017 | 0.016859 | 0.009643 | 0.014838 |
| 2018 | 0.022888 | 0.020867 | 0.009983 |
| 2019 | 0.042134 | 0.020904 | 0.021042 |
| 2020 | 0.012614 | 0.011470 | 0.008172 |
| 2021 | 0.013638 | 0.023948 | 0.018881 |
| 2022 | -0.008973 | -0.001858 | 0.011325 |
| 2023 | 0.041448 | 0.027451 | 0.025220 |
| 2024 | 0.013497 | 0.000114 | 0.006770 |
| 2025 | 0.025752 | 0.030118 | 0.022808 |
| 2026 | 0.022149 | 0.022962 | 0.017583 |

RandomForest wins 4/10 years against Ridge and loses 6/10. All negative years remain in the table; 2026 partial. 2022 outcomes are directly visible; no 2022 tuning occurred. See reports/phase5/failure_analysis.md for weak-year distributions, factor IC and importance.

In 2022 Ridge RankIC was -0.008973; RandomForest remained negative at -0.001858 but failed less severely; LightGBM changed the sign to 0.011325. LightGBM beat Ridge in only 2/10 years overall, so its 2022 advantage did not imply broad improvement. Ridge's stronger 2019/2023 results are visible in the full annual table. These descriptive outcomes did not trigger any tuning.

## Quintiles, importance and ablation

| model | monotonicity_score | top_minus_bottom_mean | top_minus_bottom_hac_t |
| --- | --- | --- | --- |
| Ridge | 1.000000 | 0.003036 | 2.941089 |
| RandomForest | 0.900000 | 0.002387 | 3.359787 |
| LightGBM | 1.000000 | 0.002446 | 4.002405 |

These are forward-return diagnostics, not capital-aware portfolio results.

| model | importance_type | family | mean | std |
| --- | --- | --- | --- | --- |
| LightGBM | gain | Liquidity_Volume | 0.243616 | 0.011616 |
| LightGBM | gain | Momentum_Reversal | 0.253266 | 0.024358 |
| LightGBM | gain | Price_Position_Intraday | 0.299883 | 0.026236 |
| LightGBM | gain | Volatility | 0.203234 | 0.013589 |
| RandomForest | impurity | Liquidity_Volume | 0.211547 | 0.038586 |
| RandomForest | impurity | Momentum_Reversal | 0.239294 | 0.028583 |
| RandomForest | impurity | Price_Position_Intraday | 0.278845 | 0.028363 |
| RandomForest | impurity | Volatility | 0.270314 | 0.036470 |

| model | feature | mean_rank | std_rank | top3_folds |
| --- | --- | --- | --- | --- |
| LightGBM | DIST_52W_HIGH | 1.100000 | 0.316228 | 10 |
| LightGBM | ILLIQ_20 | 2.900000 | 0.994429 | 8 |
| LightGBM | VOL_60 | 3.400000 | 1.505545 | 4 |
| LightGBM | DOLLAR_VOLUME_20 | 4.300000 | 1.636392 | 4 |
| LightGBM | RET_5 | 4.700000 | 1.888562 | 2 |
| LightGBM | RET_60 | 6.000000 | 1.825742 | 1 |
| RandomForest | VOL_60 | 1.100000 | 0.316228 | 10 |
| RandomForest | DIST_52W_HIGH | 2.300000 | 1.059350 | 9 |
| RandomForest | ILLIQ_20 | 3.900000 | 1.100505 | 5 |
| RandomForest | RET_60 | 4.300000 | 1.337494 | 4 |
| RandomForest | DOLLAR_VOLUME_20 | 5.000000 | 2.403701 | 2 |
| RandomForest | RET_5 | 5.700000 | 1.337494 | 0 |

Importance varies by fold; native and validation-permutation details are retained. Correlated substitutes complicate attribution and importance is not causal.

VOL_60 is the most consistently important RF feature, while DIST_52W_HIGH leads LightGBM; each appears in its model’s top three in all ten folds. ILLIQ_20 also recurs. Price-position, volatility, momentum and liquidity families all contribute native importance; no isolated group is established as the causal source of return predictability.

| model | feature_group | RankIC_mean | RankIC_hac_t |
| --- | --- | --- | --- |
| Ridge | All | 0.020135 | 2.597337 |
| Ridge | Momentum_Reversal | 0.015156 | 2.379990 |
| Ridge | Volatility | 0.018721 | 1.943629 |
| Ridge | Liquidity_Volume | 0.009937 | 2.372732 |
| Ridge | Price_Position_Intraday | 0.014294 | 1.913013 |
| ValidationWinner | Momentum_Reversal | 0.016608 | 3.172442 |
| ValidationWinner | Volatility | 0.012930 | 2.082057 |
| ValidationWinner | Liquidity_Volume | 0.008957 | 2.285260 |
| ValidationWinner | Price_Position_Intraday | 0.007204 | 1.521253 |
| ValidationWinner | All | 0.013764 | 2.861585 |

Nonlinear ablation uses the validation-winning family per fold, fixed all-feature parameters; no test-selected subsets. Family choices are archived.

Among the predefined group-only fits, Ridge's strongest is Volatility (RankIC 0.018721); the validation-winner nonlinear rule's strongest is Momentum_Reversal (0.016608). These observed diagnostic rankings do not authorize selecting that group for production. The nonlinear all-feature rule does not automatically improve on every group-only fit.

## Controls, tests and complexity

| model | RankIC_mean | RankIC_hac_t |
| --- | --- | --- |
| RandomLabelControl | 0.002076 | 0.672931 |

Random-feature standalone RankIC -0.001525; HAC t -1.443691. Unresolved predeclared control flags: 0. Future mutations, later-fold changes, row shuffling, seeded reproducibility and serialized replay pass. Full pytest: **97 passed, 37 warnings**, 0 failures, 0 errors, 0 skipped. Logs preserve warnings.

| model | role | selected_fit_seconds | grid_fit_seconds | test_prediction_seconds |
| --- | --- | --- | --- | --- |
| Lasso | secondary | 0.000000 | 0.000000 | 0.000000 |
| LightGBM | primary | 20.271357 | 39.961263 | 1.528574 |
| OLS | secondary | 0.000000 | 0.000000 | 0.000000 |
| RandomFeatureControl | control | 17.807985 | 0.000000 | 1.101786 |
| RandomForest | primary | 103.068487 | 219.973220 | 0.552343 |
| RandomLabelControl | control | 19.387430 | 0.000000 | 1.368794 |
| Ridge | ablation | 0.000000 | 0.000000 | 0.000000 |
| Ridge | primary | 0.000000 | 0.000000 | 0.000000 |
| ValidationWinner | ablation | 82.650079 | 0.000000 | 3.664717 |

Additional compute must be judged against the paired intervals above; different rankings alone do not establish valuable nonlinear interactions. Total experiment wall time 577.3 seconds. No strategy performance claim is justified. All saved full/yearly/paired metrics are recomputed and report numbers generated from CSVs. A metadata naming issue was found: runtime_details.csv originally labels every no-new-fit result reused_from_phase4, including ValidationWinner/All copied from the Phase 5 primary model. The raw file is preserved. runtime_summary.csv supplies the corrected boolean and explicit reuse_origin. Predictions and fit decisions were unaffected.

Under the predeclared interpretation rule, the extra nonlinear complexity is not justified by reliable incremental OOS ranking evidence in this experiment. Both nonlinear point estimates fall below Ridge, Lasso and OLS, but paired intervals include zero: this is not a statistically established claim that every nonlinear approach is inferior.

## Remaining bias and decision

survivorship_biased = true; candidate_selection_biased = true. Current candidate list is not historical PIT membership. Vendor/adjusted-price limitations, complete cases, overlapping labels, multiple comparisons and partial 2026 remain. Phase 5 is not unbiased strategy evidence. Engineering PASS means the documented pipeline is sound enough for a separately authorized capital-aware phase; it does not mean ML wins or is deployable.

Conclusion: **NO RELIABLE IMPROVEMENT**. Detailed report: reports/ml_walkforward_report.md. MODEL_CARD.md and PHASE5_FEATURE_SET.md document intended use and inputs. Stop after Phase 5.

PHASE 5: PASS

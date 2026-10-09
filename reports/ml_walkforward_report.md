# Phase 5 — walk-forward machine learning research

survivorship_biased = true; candidate_selection_biased = true; point_in_time_membership = false

## Research question and frozen inputs

Can nonlinear models improve OOS cross-sectional ranking over Ridge? This run concludes **NO RELIABLE IMPROVEMENT** under the fixed interpretation rule. Engineering status: **PASS**. A negative research outcome is retained.

Phase 1–4 reports/data/artifacts were unchanged; all ten Phase 4 folds and complete-case sample keys were reused. Source Phase 3 ID: 20261008T141100218333Z; experiment: 20261009T033111412374Z. The pre-fit artifact audit verified Ridge 0.0201353637, Lasso 0.0223780231, OLS 0.0222028202, EW 0.0193064047, ElasticNet 0.0200077578, and all five negative in 2022. Ridge remains primary.

## Features, models and selection

PHASE5_FEATURE_SET.md lists all upstream definitions and the 16 retained features; only the exact REV_5 duplicate is omitted. Tree inputs use existing date-local winsorized z-scores with complete-case identity, no fitted imputation or global rescaling. Ridge uses its frozen training-only scaler. No new production alpha factors.

RandomForest and LightGBM each use two predeclared configurations per fold (40 attempts total). See PHASE5_PROTOCOL.md and hyperparameter_trials.csv for every setting, selection and failure. Validation mean daily RankIC is primary; MSE then simpler grid order break numerical ties. No test-based retuning, refit, sign change or early stopping. Package versions: {"numpy": "2.5.3", "pandas": "2.3.3", "scikit-learn": "1.9.1", "lightgbm": "4.7.0", "scipy": "1.18.1", "pyarrow": "23.0.1", "joblib": "1.6.0"}.

## Walk-forward and leakage controls

Exact expanding Phase 4 folds: train from 2011 through year Y−2, validate Y−1, test Y, with labels ending strictly before the next partition. Signal after close(t), entry open(t+1), exit open(t+6), using the frozen adjusted-open target proxy. Eligibility is at t only; test target availability affects scoring, never training or prediction membership. All feature-complete test rows are predicted, including unlabeled tail rows.

Future-target and later-feature mutations, changed later folds, shuffled row order, repeat seeds, no learned imputation, serialization replay and disk-metric checks pass. Full suite: 97 passed, 0 failures, 0 errors, 0 skipped, 37 warnings. Full logs and XML are retained. Tests are evidence against specified failure modes, not a guarantee against all leakage.

## OOS results

| model | IC_mean | RankIC_mean | IC_IR | RankIC_IR | RankIC_hac_t | RankIC_ci95_low | RankIC_ci95_high | MSE | MAE | R2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ridge | 0.026834 | 0.020135 | 0.127141 | 0.093954 | 2.597337 | 0.004941 | 0.035330 | 0.002125 | 0.031788 | 0.000431 |
| RandomForest | 0.023861 | 0.016376 | 0.144468 | 0.113148 | 3.157415 | 0.006211 | 0.026541 | 0.002126 | 0.031792 | 0.000236 |
| LightGBM | 0.025735 | 0.015598 | 0.177264 | 0.126206 | 3.597039 | 0.007099 | 0.024097 | 0.002125 | 0.031795 | 0.000400 |

| model | IC_median | RankIC_median | IC_positive_ratio | RankIC_positive_ratio | valid_dates | median_stocks_per_date | observations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ridge | 0.024405 | 0.015855 | 0.554739 | 0.529412 | 2448 | 381.000000 | 928158 |
| RandomForest | 0.022996 | 0.013906 | 0.567402 | 0.549837 | 2448 | 381.000000 | 928158 |
| LightGBM | 0.023888 | 0.014075 | 0.578023 | 0.548203 | 2448 | 381.000000 | 928158 |

ICIR/RankICIR are unannualized daily mean/std. MSE/MAE/R² pool valid stock-date labels; R² uses the pooled observed target mean. HAC is the frozen calendar-preserving Bartlett lag-5 estimator; paired lag-20 sensitivity is also saved. Separate model significance does not establish incremental value.

## Primary paired comparison vs Ridge

Columns mean/median are daily paired ΔRankIC; positive_ratio is the fraction of comparable dates on which ML beats Ridge.

| model | mean | median | positive_ratio | hac_t | ci95_low | ci95_high | years_better | years_worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RandomForest | -0.003759 | -0.001447 | 0.493873 | -0.857735 | -0.012350 | 0.004831 | 4 | 6 |
| LightGBM | -0.004537 | -0.000505 | 0.498366 | -0.858737 | -0.014892 | 0.005818 | 2 | 8 |

| model | hac_t_lag20 | ci95_low_lag20 | ci95_high_lag20 |
| --- | --- | --- | --- |
| RandomForest | -0.857544 | -0.012352 | 0.004833 |
| LightGBM | -0.862208 | -0.014851 | 0.005777 |

Descriptive best nonlinear model is RandomForest: paired gain -0.003759, 95% CI [-0.012350, 0.004831], HAC t -0.8577. The interval includes zero. This is conditional on the frozen biased sample and two compared ML families.

## Secondary comparison vs observed Lasso and OLS

| model | mean | hac_t | ci95_low | ci95_high |
| --- | --- | --- | --- | --- |
| RandomForest | -0.006002 | -1.449991 | -0.014115 | 0.002111 |
| LightGBM | -0.006780 | -1.365322 | -0.016512 | 0.002953 |

| model | RankIC_mean | RankIC_hac_t | MSE | MAE | R2 |
| --- | --- | --- | --- | --- | --- |
| Lasso | 0.022378 | 2.999991 | 0.002125 | 0.031788 | 0.000636 |
| OLS | 0.022203 | 3.103427 | 0.002125 | 0.031789 | 0.000669 |

RandomForest minus Lasso is -0.006002; minus OLS aggregate mean RankIC is -0.005827. Neither replaces Ridge as primary. The OLS number is descriptive, not a separate paired significance test.

## Yearly stability and 2022

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

RandomForest beats Ridge in 4/10 years, loses in 6/10. 2026 is partial. Negative years and distribution/importance comparisons are retained in phase5/failure_analysis.md. No favorable year was removed.

| model | RankIC_mean | RankIC_hac_t | RankIC_ci95_low | RankIC_ci95_high |
| --- | --- | --- | --- | --- |
| Ridge | -0.008973 | -0.291677 | -0.069272 | 0.051325 |
| RandomForest | -0.001858 | -0.112500 | -0.034224 | 0.030508 |
| LightGBM | 0.011325 | 0.874474 | -0.014058 | 0.036708 |

In 2022 Ridge RankIC was -0.008973; RandomForest remained negative at -0.001858 but failed less severely; LightGBM changed the sign to 0.011325. LightGBM beat Ridge in only 2/10 years overall, so its 2022 advantage did not imply broad improvement. Ridge's stronger 2019/2023 results are visible in the full annual table. These descriptive outcomes did not trigger any tuning.

Year-specific outcomes do not justify an ex-post regime rule. Weak years are examined against prediction dispersion, feature distributions, upstream factor IC and training-derived importance, without new macro inputs.

## Prediction quintiles

| model | quantile | mean_forward_return | monotonicity_score | top_minus_bottom_mean | top_minus_bottom_hac_t | top_minus_bottom_ci95_low | top_minus_bottom_ci95_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ridge | 1 | 0.002221 | 1.000000 | 0.003036 | 2.941089 | 0.001013 | 0.005060 |
| Ridge | 2 | 0.002589 | 1.000000 | 0.003036 | 2.941089 | 0.001013 | 0.005060 |
| Ridge | 3 | 0.002981 | 1.000000 | 0.003036 | 2.941089 | 0.001013 | 0.005060 |
| Ridge | 4 | 0.003953 | 1.000000 | 0.003036 | 2.941089 | 0.001013 | 0.005060 |
| Ridge | 5 | 0.005258 | 1.000000 | 0.003036 | 2.941089 | 0.001013 | 0.005060 |
| RandomForest | 1 | 0.002562 | 0.900000 | 0.002387 | 3.359787 | 0.000995 | 0.003780 |
| RandomForest | 2 | 0.002506 | 0.900000 | 0.002387 | 3.359787 | 0.000995 | 0.003780 |
| RandomForest | 3 | 0.003192 | 0.900000 | 0.002387 | 3.359787 | 0.000995 | 0.003780 |
| RandomForest | 4 | 0.003798 | 0.900000 | 0.002387 | 3.359787 | 0.000995 | 0.003780 |
| RandomForest | 5 | 0.004950 | 0.900000 | 0.002387 | 3.359787 | 0.000995 | 0.003780 |
| LightGBM | 1 | 0.002650 | 1.000000 | 0.002446 | 4.002405 | 0.001248 | 0.003644 |
| LightGBM | 2 | 0.002802 | 1.000000 | 0.002446 | 4.002405 | 0.001248 | 0.003644 |
| LightGBM | 3 | 0.002936 | 1.000000 | 0.002446 | 4.002405 | 0.001248 | 0.003644 |
| LightGBM | 4 | 0.003522 | 1.000000 | 0.002446 | 4.002405 | 0.001248 | 0.003644 |
| LightGBM | 5 | 0.005096 | 1.000000 | 0.002446 | 4.002405 | 0.001248 | 0.003644 |

Tie-preserving at-t membership is assigned before label filtering. This is average forward-return association, **not tradable portfolio performance**: no overlapping holdings, costs or capital accounting. Monotonicity is Spearman correlation of five aggregate bin means; spread uses the same lag-5 HAC method.

## Importance and stability

| model | importance_type | feature | mean_normalized_importance | mean_rank | std_rank | top3_folds |
| --- | --- | --- | --- | --- | --- | --- |
| LightGBM | gain | DIST_52W_HIGH | 0.138609 | 1.100000 | 0.316228 | 10 |
| LightGBM | gain | ILLIQ_20 | 0.102873 | 2.900000 | 0.994429 | 8 |
| LightGBM | gain | VOL_60 | 0.102121 | 3.400000 | 1.505545 | 4 |
| LightGBM | gain | DOLLAR_VOLUME_20 | 0.091431 | 4.300000 | 1.636392 | 4 |
| LightGBM | gain | RET_5 | 0.090345 | 4.700000 | 1.888562 | 2 |
| LightGBM | gain | RET_60 | 0.078568 | 6.000000 | 1.825742 | 1 |
| RandomForest | impurity | VOL_60 | 0.165913 | 1.100000 | 0.316228 | 10 |
| RandomForest | impurity | DIST_52W_HIGH | 0.112260 | 2.300000 | 1.059350 | 9 |
| RandomForest | impurity | ILLIQ_20 | 0.091996 | 3.900000 | 1.100505 | 5 |
| RandomForest | impurity | RET_60 | 0.090155 | 4.300000 | 1.337494 | 4 |
| RandomForest | impurity | DOLLAR_VOLUME_20 | 0.082614 | 5.000000 | 2.403701 | 2 |
| RandomForest | impurity | RET_5 | 0.070842 | 5.700000 | 1.337494 | 0 |

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

| model | feature | mean_importance | mean_rank | std_rank |
| --- | --- | --- | --- | --- |
| LightGBM | ILLIQ_20 | 0.007295 | 5.700000 | 5.498485 |
| LightGBM | RET_5 | 0.003447 | 7.700000 | 5.396501 |
| LightGBM | PRICE_MA60 | 0.003147 | 7.600000 | 4.599517 |
| LightGBM | RET_20 | 0.002506 | 7.300000 | 3.622461 |
| LightGBM | DOLLAR_VOLUME_20 | 0.002323 | 7.300000 | 5.375872 |
| RandomForest | ILLIQ_20 | 0.005876 | 6.500000 | 6.258328 |
| RandomForest | RET_5 | 0.004779 | 5.300000 | 4.738729 |
| RandomForest | DOLLAR_VOLUME_20 | 0.002814 | 7.100000 | 4.306326 |
| RandomForest | PRICE_MA20 | 0.002297 | 6.000000 | 3.464102 |
| RandomForest | RET_20 | 0.002190 | 6.600000 | 4.195235 |

VOL_60 is the most consistently important RF feature, while DIST_52W_HIGH leads LightGBM; each appears in its model’s top three in all ten folds. ILLIQ_20 also recurs. Price-position, volatility, momentum and liquidity families all contribute native importance; no isolated group is established as the causal source of return predictability.

Native importance and one seeded within-date permutation per feature on 20 validation sessions per fold are diagnostic only. Validation permutation values are RankIC losses, not gain units. Negative values remain. Native gain/impurity is not comparable across algorithms; correlated factors can substitute. Ranking variation across folds is retained rather than hidden behind a global average. **Feature importance is not causal evidence.**

## Controlled ablation

| model | feature_group | RankIC_mean | RankIC_hac_t | IC_mean |
| --- | --- | --- | --- | --- |
| Ridge | All | 0.020135 | 2.597337 | 0.026834 |
| Ridge | Momentum_Reversal | 0.015156 | 2.379990 | 0.012921 |
| Ridge | Volatility | 0.018721 | 1.943629 | 0.030744 |
| Ridge | Liquidity_Volume | 0.009937 | 2.372732 | 0.016028 |
| Ridge | Price_Position_Intraday | 0.014294 | 1.913013 | 0.021520 |
| ValidationWinner | Momentum_Reversal | 0.016608 | 3.172442 | 0.019342 |
| ValidationWinner | Volatility | 0.012930 | 2.082057 | 0.021035 |
| ValidationWinner | Liquidity_Volume | 0.008957 | 2.285260 | 0.010045 |
| ValidationWinner | Price_Position_Intraday | 0.007204 | 1.521253 | 0.014816 |
| ValidationWinner | All | 0.013764 | 2.861585 | 0.024897 |

Among the predefined group-only fits, Ridge's strongest is Volatility (RankIC 0.018721); the validation-winner nonlinear rule's strongest is Momentum_Reversal (0.016608). These observed diagnostic rankings do not authorize selecting that group for production. The nonlinear all-feature rule does not automatically improve on every group-only fit.

ValidationWinner means the higher validation-RankIC nonlinear family in each fold, with its selected all-feature parameters fixed for four upstream group-only fits. ablation_family_by_fold.csv records actual families. Ridge group predictions are reused from Phase 4. These are group-only diagnostics, not leave-one-out causal contributions or a searched production feature subset.

## Random-label and random-feature controls

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

Training labels were permuted only within allowed training rows; controls use the first fixed LightGBM configuration and are never tuned. Random features are reproducible key-based noise and appear only in a separate diagnostic model. Predeclared investigation flags: {"random_label_requires_investigation": false, "random_feature_importance_requires_investigation": false, "random_feature_rankic_requires_investigation": false}. All control results, including negative years, remain saved.

## Complexity, similarity and disagreements

| model_a | model_b | Pearson_mean | Spearman_mean | Spearman_std |
| --- | --- | --- | --- | --- |
| RandomForest | LightGBM | 0.722990 | 0.726048 | 0.089673 |
| Ridge | LightGBM | 0.551143 | 0.511281 | 0.151028 |
| Ridge | RandomForest | 0.617259 | 0.634637 | 0.181214 |

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

Under the predeclared interpretation rule, the extra nonlinear complexity is not justified by reliable incremental OOS ranking evidence in this experiment. Both nonlinear point estimates fall below Ridge, Lasso and OLS, but paired intervals include zero: this is not a statistically established claim that every nonlinear approach is inferior.

Experiment wall time: 577.3 seconds, including data/test/serialization/diagnostic overhead. Grid fit seconds include the selected fit, so do not add those columns together. Ridge/Lasso/OLS zero incremental fit times mean reuse, not free original training. Runtime per model/fold is retained; four CPU workers, one BLAS thread. Different prediction correlations demonstrate different rankings, not genuine profitable interactions by themselves. Incremental paired evidence determines whether added complexity is supported.

Ten largest LightGBM/Ridge absolute percentile-rank gaps per fold are saved with all factor z-scores and realized targets; no target-sign selection. The failure-analysis report shows a fixed first-fold excerpt. SHAP was omitted; native and validation-permutation diagnostics suffice without extra dependencies.

## Integrity, consistency and limitations

All final metrics were computed from saved OOS Parquets, then full/yearly/paired results independently recomputed from them. Report tables are generated from the resulting CSVs, with machine checks of their rendered values. Source/model/prediction hashes, exact upstream preservation and append-only research-log prefix are audited in phase5/validation.json.

A metadata naming issue was found: runtime_details.csv originally labels every no-new-fit result reused_from_phase4, including ValidationWinner/All copied from the Phase 5 primary model. The raw file is preserved. runtime_summary.csv supplies the corrected boolean and explicit reuse_origin. Predictions and fit decisions were unaffected.

LightGBM printed repeated “No further splits with positive gain” warnings. These indicate constrained trees stopped splitting; all attempted primary trials remain recorded, with no parameter relaxation. Native console warning counts were not captured by Python warnings, so no exact count is claimed. The 37 pytest warnings are retained in final_pytest.log.

The frozen current-candidate universe remains survivor and selection biased; this is not PIT index membership or unbiased strategy evidence. Other limitations include vendor revisions, globally quarantined corrupt data, adjusted-price execution proxy, no delisting reconstruction/sector-size neutralization, complete-case restriction, overlapping labels, weak return signal, limited grid and folds, partial 2026, and multiple exploratory diagnostics. HAC intervals do not remove these biases or all multiple-testing risk. No Sharpe, CAGR, capital portfolio or transaction-cost optimization was performed.

## Conclusion

**NO RELIABLE IMPROVEMENT**. The predeclared classification uses paired uncertainty and year consistency, not an obligation to make ML win. Engineering decision: **PASS**, independently of whether ML outperforms. This result supports only the bounded experiment performed; other grids or production implementations are untested. Stop before Phase 6.

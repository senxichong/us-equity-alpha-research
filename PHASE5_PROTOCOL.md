# Phase 5 preregistration — nonlinear value over frozen Ridge

survivorship_biased = true; candidate_selection_biased = true

Written before fitting nonlinear models or examining their test results. Phase 4 metrics were programmatically verified: 10 folds, Ridge RankIC 0.0201353637, Lasso 0.0223780231, OLS 0.0222028202, Equal Weight 0.0193064047, ElasticNet 0.0200077578; all five negative in 2022. Ridge remains primary; Lasso and OLS remain secondary observed comparators.

## Frozen sample and timing

Read the Phase 3 checksum-verified matrix and Phase 4 fold manifest. Reuse its 16-feature complete-case sample, exact training/validation/test bounds, and strict label-end purges. Training starts 2011, tests are 2017–2026 (2026 partial). No validation refit. Primary target remains adjusted_open(t+6)/adjusted_open(t+1)−1 after a signal formed after close(t). No future eligibility, source rebuild, data download, feature changes or target changes.

Ridge predictions, all Ridge group ablations, Lasso and OLS predictions are reused from saved Phase 4 Parquets and checked by key/target. RF and LightGBM use the same sample keys. Tree inputs are the existing Phase 3 z-scores. **No additional scaling or imputation**: complete cases preserve the exact baseline sample; missing inputs fail closed. Thus no learned imputation statistic can depend on a test distribution. The reused Ridge carries its training-only scaler unchanged. Tests explicitly cover this absence of fitted imputation and invariant train preprocessing.

## Small fixed grids and seeds

Python and NumPy base seed 42; estimator seed = 42 + test year. All stochastic library seeds are recorded. Sort by date/ticker before fitting. CPU workers capped at four; BLAS capped at one. LightGBM uses deterministic CPU execution and force_col_wise. Reproducibility tolerance is 1e-12 absolute/relative within the locked environment; cross-version/platform byte identity is not promised.

- RandomForestRegressor: **two** candidates, max_depth 4 or 6. Both n_estimators=64, min_samples_leaf=100, max_features=.75, bootstrap=True, max_samples=.10, criterion=squared_error. All allowed training rows enter fit; the fixed 10% per-tree bootstrap is an estimator/runtime setting, not a new universe or external sample selection.
- LGBMRegressor: **two** candidates, (num_leaves=7, max_depth=3) or (num_leaves=15, max_depth=4). Both n_estimators=150, learning_rate=.05, min_child_samples=200, max_bin=63, subsample=.8, subsample_freq=1, colsample_bytree=.8, reg_lambda=1, objective=regression. No early stopping or hidden adaptive trial expansion.
- No substitution: LightGBM 4.7.0 installed successfully. No additional model family or new alpha feature.
- Selection: highest validation mean daily RankIC (50-stock minimum), ties within 1e-12 by lower validation MSE then the first/simpler candidate. Save successes and failures. Test labels never enter fit, selection, orientation or stopping. Evaluate/save the selected test predictions once; reloading and deterministic consistency checks are audits, not retuning.

## Evaluation and paired evidence

Final metrics come **only from reloaded saved OOS predictions**. MSE/MAE/R², daily Pearson IC and average-tie Spearman RankIC, medians, unannualized IRs, positive ratios, counts and annual breakdown match Phase 4. HAC uses its calendar-preserving Bartlett lag-5 mean estimator and small-sample correction, with fixed lag-20 sensitivity. Pair RF−Ridge and LightGBM−Ridge on identical dates/stock samples; also pair each against frozen Lasso. Report mean/median difference, positive-day fraction and HAC 95% interval. No separate-mean significance claim substitutes for a paired comparison.

Prediction quintiles reuse Phase 4 tie-preserving formation from at-t predictions before label availability filtering; require 50 assigned names and 10 available labels per bin. Report Q5−Q1, monotonicity and HAC as forward-return diagnostics only. No capital accounting, Sharpe, CAGR, drawdown or cost optimization.

## Fixed diagnostics

- Native RF impurity and LightGBM gain/split importance by fold. Additionally use one seeded within-date feature permutation per retained feature on **20 evenly spaced full validation sessions** per fold; measure mean daily RankIC loss. This controlled, noisy importance diagnostic never selects features or changes parameters. Correlated substitutes complicate attribution; importance is not causal.
- Group ablations: reuse all five Phase 4 Ridge groups. For nonlinear ablations, **strongest means the validation-winning nonlinear family in each fold**, selected between already tuned RF/LightGBM using validation RankIC, never aggregate test results. Keep that fold's all-feature selected parameters fixed; fit the four upstream groups plus reuse All. Report actual family per fold and the validation-winner rule prominently. This avoids choosing a family or subset from future folds/test outcomes. It is a diagnostic conditional on that rule, not a new primary ensemble.
- Yearly feature/prediction distributions, daily cross-sectional dispersion, collapse/extremes and all weak years including 2022. Reference upstream yearly factor IC and fold importances; no new regime classifier or macro data.
- Pairwise daily prediction correlations use all at-t feature-complete test rows, without label filtering. Disagreement examples are the **ten largest absolute LightGBM−Ridge percentile-rank gaps in each fold**, ties sorted by date/ticker; include targets without selecting on their sign or availability.

## Adversarial controls

For every fold, train one **untuned first-grid LightGBM** on a seeded permutation of labels across that fold's allowed training rows only. Validation/test labels stay intact; controls cannot select configurations. Global within-training permutation destroys feature/label and calendar association while preserving the training label distribution. Retain all outcomes. Investigate if |mean OOS RankIC| > .005 and |HAC t| >= 2.58; do not rerun seeds until a favorable control appears.

Separately train the same fixed LightGBM with all retained features plus one diagnostic uniform random feature. The feature is a SHA-256 mapping of (seed, session, ticker), scaled to [-sqrt(3),sqrt(3)], with no global RNG-order/future-row dependence. It never enters primary models. Report its importance by fold and standalone OOS IC/RankIC; investigate stable major importance (mean normalized gain > .15 or top-three gain in >= 5 folds) or standalone |RankIC| > .005 with |HAC t| >= 2.58. A noisy importance estimate is not automatically leakage, but flagged controls require explicit investigation.

Toy and saved-artifact tests cover identical Phase 4 folds, target mutation, later-fold feature mutation, shuffled rows, repeated seeded fits, no fitted imputers/test scaling, test-only tags, serialized prediction consistency and disk-recomputed metrics. Prior reports/data remain immutable; RESEARCH_LOG.md is append-only with its Phase 4 prefix preserved.

## Interpretation rule (engineering PASS is independent)

Report both nonlinear families. For narrative only, best ML means higher aggregate test RankIC among those two fixed families, an explicitly descriptive comparison. **STRONG IMPROVEMENT** requires mean paired gain >= .005, lag-5 95% lower bound > 0, improvement in >= 7/10 years, winning-day fraction > .52, beating observed Lasso and prediction-quintile |monotonicity| >= .8. **MODEST IMPROVEMENT** requires positive paired gain with lower bound > 0 and improvement in >= 6/10 years when the strong rule is not met. **ML UNDERPERFORMS** requires both nonlinear models' paired upper bounds < 0 and each losing in >= 6/10 years. Otherwise **NO RELIABLE IMPROVEMENT**. These thresholds are interpretive, not a guarantee of economic usefulness; assess uncertainty from comparing two model families and many diagnostics. Complexity costs and controls can qualify any conclusion. Do not force a positive outcome or retune after observing tests.

Method references: [RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html) and [LightGBM parameters](https://lightgbm.readthedocs.io/en/stable/Parameters.html). Upstream HAC/quantile definitions remain unchanged. Stop after Phase 5.

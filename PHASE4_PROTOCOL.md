# Phase 4 preregistered analysis

survivorship_biased = true; candidate_selection_biased = true

Written before computing Phase 4 predictive statistics. No upstream data, eligibility, factor, target or quarantine changes. Input is the checksum-verified frozen Phase 3 matrix. No complex models, strategy Sharpe or capital-aware portfolio accounting.

## Single-factor analysis

- Primary target: FWD_RET_5D. Secondary 1D/10D/20D receive IC diagnostics only, all reported.
- Primary IC representation: **raw Phase 3 factor**, unchanged sign. Pearson measures raw linear association; Spearman uses average ranks for ties. Models separately use existing Phase 3 z-scores.
- Pairwise sample: eligible_at_t, that factor available and finite, entry valid, horizon exit valid, target available and finite. Future eligibility is never required. Missing labels are exclusions from evaluation, not changes to historical membership or normalization. No outcome-magnitude exclusions.
- At least **50** paired stocks and nonconstant factor/target per date. Preserve below-threshold/constant dates as unavailable. Report exact scored dates, stocks and observations per factor; all means weight scored dates equally.
- ICIR = daily mean / sample standard deviation, **not annualized**. Positive ratios exclude unavailable dates; zero is not positive.
- Newey-West mean inference: Bartlett kernel, **lag 5** for primary labels, lag 20 as a fixed sensitivity check. Secondary lag = horizon (including lag 1). Mean-score sandwich variance with n/(n−1) correction and asymptotic normal two-sided p-values/95% intervals. Reindex to the full source session grid; missing ICs have zero estimating-equation residual, not a fabricated zero IC, and never compress calendar lags. Naive IID t is reported only for comparison. Dependence can extend beyond these lags.
- Benjamini-Hochberg adjusted p-values separately over the 17 primary Pearson tests and the 17 primary RankIC tests. Dependent/redundant factors and shared data limit this diagnostic; no discovery claim and no pooling of favorable horizons.
- Yearly means and 126-/252-session rolling means (minimum 100/200 valid daily values). 2010 and 2026 are explicitly partial years. Predetermined example figures: RET_20, REV_5, VOL_20, ILLIQ_20, VOLUME_RATIO_20, DIST_52W_HIGH; retain tables for every factor.
- Correlation: average daily pairwise-complete Spearman factor correlation among eligible-at-t finite values, minimum 50 per pair, **without target filtering**. Report pair/date counts. |mean correlation| >= .80 marks strong redundancy; exact REV_5 = −RET_5 is known before results.

## Forward-return quantile diagnostics

Assign Q1–Q5 from eligible-at-t raw factor values **before accessing future labels**, using average-rank midpoint percentile bins. Ties stay together; skip dates with fewer than 50 names, fewer than five distinct values or an empty bin. Then join available labels. A daily diagnostic requires at least 10 labeled names in every bin. Record assigned/labeled counts. Q1 is lowest raw factor, Q5 highest; always report Q5−Q1 without sign flipping.

Full-period means are equal-weight averages of daily bin means. Also report medians of daily bin means and pooled stock-label medians with their distinct weighting. Monotonicity = Spearman correlation of bin number with the five mean bin returns; report adjacent-step signs and yearly spreads. |monotonicity| >= .8 flags a strong aggregate ordering, not a profitable strategy. HAC lag 5 tests the daily spread mean. These overlapping forward labels have no capital, turnover, cost, auction-fill or borrow accounting.

## Linear baselines and folds

Feature set chosen solely from definitions: all 17 z-scores **except REV_5**, because it is exactly −RET_5. No performance-selected features. Common complete-case eligible/finite 16-feature sample and valid 5D labels for model evaluation/training; no imputation. Inference predictions are generated using only test-date feature availability, separately from test-label availability.

Expanding annual scheme: fixed training start 2011-01-01. For test year Y=2017,...,2026, train signal dates through Dec 31 of Y−2, validation year Y−1, test year Y (2026 partial through the frozen endpoint). Require **training return_end_timestamp_5D < validation-year start UTC**, and **validation return_end_timestamp_5D < test-year start UTC**. This purges labels crossing the next split. No future data enters preprocessing/fitting. Models are frozen for the full test year; **do not refit on validation**. Earlier test years may enter later folds' historical training sets, which is legitimate expanding walk-forward use.

StandardScaler is fitted to training features only; intercepts are unpenalized. Train targets are decimal returns, untransformed. Stock-date rows receive equal training weight. No model-wide target cross-sectional normalization or test-period preprocessing fit.

- Equal Weight: orient each of 16 features by its mean training-only daily RankIC (zero/undefined -> +1), then equally average training-standardized features. Fit an intercept and a nonnegative slope to this score using training data only, so predictions have return units for MSE/MAE. Save all signs and calibration. This calibration cannot reverse the composite direction.
- OLS: intercept + the same features; no tuning.
- Ridge (primary future-ML benchmark): normalized penalty lambda in **[.001, .1, 10]**, implemented as sklearn alpha = n_train * lambda for objective mean squared error + lambda ||beta||².
- Lasso: alpha in **[.00001, .0001, .001]**.
- ElasticNet: the same three alphas, fixed l1_ratio=.5. Lasso/ElasticNet use sklearn's (1/(2n)) squared-loss convention, cyclic coordinate descent, precomputed Gram, max_iter=50000, tol=1e-6. Numerical convergence warnings must be retained and reviewed, not hidden.
- Select a regularizer by highest validation mean daily RankIC; ties within 1e-12 use lower validation MSE, then stronger penalty. Undefined RankIC ranks last. Save every tried configuration. Test results cannot change choices.

All test predictions retain fold boundaries, target/availability, model and feature-group tags. Combined OOS reports contain only test predictions; all five baselines use matched test cases. Report full/yearly MSE, MAE, R², daily IC/RankIC, nonannualized ICIR/RankICIR and lag-5 HAC. Constant predictions retain regression metrics but have unavailable correlations. Compare single factors versus Equal Weight additionally on the **same OOS common sample**; avoid comparing full-history factors to shorter OOS models.

## Predefined group diagnostics

Ridge ablations use identical folds, common all-feature sample and three-lambda validation grid. Groups: Momentum/Reversal = RET_5/10/20/60 (inverse omitted); Volatility = VOL_10/20/60; Liquidity/Volume = ILLIQ_20, DOLLAR_VOLUME_20, VOLUME_RATIO_20, VOLUME_SURPRISE_20; Price Position/Intraday = PRICE_MA20/60, DIST_52W_HIGH, INTRADAY_RANGE, OPEN_CLOSE_RETURN; All = 16 factors. These are diagnostic comparisons, never a search to replace the primary all-feature Ridge baseline. Coefficients are saved in training-scaled and original Phase 3 z-score units; report sign changes and near-zero fraction (|coefficient| <= 1e-8).

Full-period single-factor analysis exposes those years descriptively, but cannot change this specification. OOS refers to chronological fitting/tuning isolation, not an untouched external replication sample. Future ML must use the same folds and frozen primary target; beating one exploratory table is insufficient evidence.

## Method references

Bartlett/Newey-West implementation is cross-checked with [statsmodels cov_hac](https://www.statsmodels.org/dev/generated/statsmodels.stats.sandwich_covariance.cov_hac.html). Penalty conventions follow [Ridge](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html), [Lasso](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html) and [ElasticNet](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html). These references specify methods, not evidence about this dataset.

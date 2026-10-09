# Research log

survivorship_biased = true; candidate_selection_biased = true

## Phase 4 preregistration — before predictive analysis

Hypothesis: the frozen factor families may exhibit weak, redundant and regime-dependent cross-sectional associations; positive predictive evidence is not required for an engineering PASS.

Method: PHASE4_PROTOCOL.md fixes the 5D primary label, raw signs, 50-stock threshold, HAC lags, 17-factor diagnostics, annual model folds, purge rules, 16-feature baseline set and small regularization grids before results. No results have been calculated at this entry.

Result: pending. Interpretation: pending. Next step: implement and test analysis primitives, then run the following predeclared stages in order. Append outcomes without altering this entry.

### Stage A — all single factors and quantiles

Hypothesis: evidence may differ between raw Pearson association, rank ordering, and quantile monotonicity. Method: daily primary IC/RankIC, HAC/FDR, yearly/rolling tables, untuned raw-sign Q1–Q5 diagnostics. Result: pending. Interpretation: pending. Next step: preserve every factor, including negative and failed results.

### Stage B — redundancy and limited horizon robustness

Hypothesis: momentum/price-position and volatility signals overlap; REV_5 is mechanically redundant. Method: target-free date-local Spearman correlations and all three secondary-horizon IC tables. Result: pending. Interpretation: pending. Next step: retain the definition-selected model set; do not choose a new primary horizon.

### Stage C — linear OOS baseline

Hypothesis: train-oriented equal weights and regularized linear models may be competitive with OLS, but could fail out of sample. Method: expanding training, one-year validation, subsequent-year tests, label purging, training-only scaling/signs/calibration, modest grids. Result: pending. Interpretation: pending. Next step: report all five models on matched OOS observations.

### Stage D — stability and predefined ablations

Hypothesis: apparent aggregate results may depend on regimes or unstable coefficients. Method: yearly OOS metrics, coefficient signs/near-zero counts, four predetermined Ridge group ablations with identical samples/folds. Result: pending. Interpretation: pending. Next step: report all groups without replacing the predeclared primary Ridge baseline; stop after Phase 4.

## Implementation test failure retained (before predictive analysis)

Initial Phase 4 toy test run: 17 passed, 2 failed, 9 dependency deprecation warnings. Both failures exposed a pandas attribute-name collision: `.quantile` resolved to the DataFrame method rather than the column in a test and the pooled-median diagnostic. Replaced attribute access with explicit `['quantile']` indexing. No predictive dataset analysis had run and no research definition was changed. Next step: rerun these checks and the complete repository suite.

## 20261008T144501813406Z

Stage A BEGIN. Hypothesis/method: unchanged PHASE4_PROTOCOL.md raw-sign 5D IC and forward-return quantiles. Result/interpretation pending. Next: retain all 17 factors.

## 20261008T144719225797Z

Stage A COMPLETE. Result: all 17 factors retained in dated IC/RankIC, HAC/FDR, yearly/rolling and raw-sign Q1–Q5 tables. Interpretation deferred to the report after the fixed pipeline completes. Next: target-free redundancy and all secondary horizons; no specification changes.

## 20261008T144719237544Z

Stage B BEGIN. Hypothesis: redundant families and horizon dependence. Method: target-free pairwise cross-sectional Spearman and all 1D/10D/20D diagnostics. Results pending; do not change the primary 5D target.

## 20261008T145048365204Z

Stage B COMPLETE. Result: complete correlation/date-count and all-horizon tables saved, including negative associations. Interpretation remains descriptive and does not change feature membership, signs, grids or primary horizon. Next: preregistered linear folds.

## 20261008T145048378896Z

Stage C/D BEGIN. Hypothesis: simple linear combinations may have unstable OOS rankings. Method: fixed expanding folds 2017–2026, label purging, train-only scaling/orientation/calibration, all five baselines and four predefined Ridge groups. Results pending. Next: retain every configuration and test prediction; no performance-dependent reruns.

## 20261008T150022794056Z

Stage C/D COMPLETE. Result: 10 annual folds, all five primary models, four Ridge ablations, all validation configurations, training-only coefficients/scalers/signs and test-only predictions saved. Interpretation will compare matched OOS periods, yearly instability and coefficient behavior without changing the predeclared baseline. Next: figures, source-preservation audit and final reports; no Phase 5.

## 20261008T150317091718Z

Phase 4 FINAL outcomes. Result: Highest raw signed mean RankIC: ILLIQ_20 (0.01395); largest absolute primary RankIC HAC t: ILLIQ_20 (4.23). The weakest magnitude is VOLUME_RATIO_20 (0.00048, HAC t=0.27). Negative means are retained and are not automatically failures. Equal Weight OOS RankIC is 0.01931, versus the strongest raw-signed individual factor on the identical OOS sample, VOL_20 (0.01805). Thus Equal Weight exceeds that individual-factor ranking mean. Ridge has RankIC 0.02014, above Equal Weight. Lasso has the highest observed OOS RankIC (0.02238) among the five fixed baselines. These are observed comparisons, not proof that differences are statistically significant. Tests: 87 passed, 0 failed. Interpretation: overlapping-label, survivorship/candidate-selection-biased prototype associations; no strategy profitability claim. Next step: STOP; Phase 5 requires a new instruction. Decision: PASS. Negative/inconclusive factors and all attempted grids remain saved.

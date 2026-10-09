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

## Phase 5 preregistration — separately authorized, before ML outcomes

Hypothesis: constrained RF/LightGBM may capture nonlinear ranking structure, but may not reliably beat frozen Ridge or observed Lasso. Method: PHASE5_PROTOCOL.md fixes exact Phase 4 folds/samples, two candidates per nonlinear family, training-only operations, validation RankIC selection, paired HAC comparisons and the fixed decision thresholds. Saved Phase 4 facts and 10-fold identity were programmatically verified. LightGBM 4.7.0 is available. Expected interpretation: negative/inconclusive evidence is valid; no outcome-dependent new factors or trials.

Primary experiment: run all ten folds and preserve every trial/model/test prediction; results pending. Next step: audit saved outputs, never retune a tested fold.

Controlled diagnostics: validation-only fold importance and validation-winning-family group ablations, fixed random-label and random-feature controls in every fold; results pending. Expected interpretation: correlated features and unstable importance are not causal discoveries; suspicious controls trigger investigation. Next step: year/2022/disagreement analysis without selecting cases by target profitability, then stop after Phase 5.

## 20261009T033111731269Z — Phase 5

PRIMARY/CONTROLS BEGIN. Hypothesis: nonlinear value may be weak or absent. Fixed two-candidate RF/LightGBM grids, exact Phase 4 samples/folds, reused Ridge, training-only fit and validation-only selection. Controls and validation-winner group diagnostics are predeclared. Results pending; no test-based retuning.

## 20261009T034015323250Z — Phase 5

EXPERIMENTS COMPLETE. Result: ten frozen folds, selected RF/LightGBM and reused linear predictions, fixed controls and validation-winner ablations saved. Interpretation pending disk-based evaluation and paired HAC audit. Next: evaluate artifacts and report; no retuning or new factors.

## 20261009T034434556909Z — Phase 5 completed

Hypothesis: nonlinear ranking may not improve on frozen Ridge. Result: NO RELIABLE IMPROVEMENT; RandomForest RankIC 0.0163758779, paired Ridge gain -0.0037594858, lag-5 HAC CI [-0.0123500864, 0.0048311148], wins 4/10 years. Fixed experiments retained; no test retuning. Controls: 0 investigation flags. Full suite 97 passed/37 warnings. Upstream unchanged. Interpretation: bounded biased-prototype evidence, not strategy performance. Runtime metadata origin corrected in derived summary; native LightGBM stopping warnings retained descriptively. Next: stop; Phase 6 requires a new instruction.

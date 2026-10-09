# Model card — Phase 5 prototype

survivorship_biased = true; candidate_selection_biased = true; point_in_time_membership = false

Purpose: test incremental cross-sectional 5D OOS ranking over the predeclared Ridge benchmark. No deployable strategy or unbiased investable universe is claimed.

Models actually run: sklearn Ridge (saved Phase 4 benchmark), RandomForestRegressor and LightGBM LGBMRegressor. Lasso and OLS are reused secondary comparisons. Versions: {"numpy": "2.5.3", "pandas": "2.3.3", "scikit-learn": "1.9.1", "lightgbm": "4.7.0", "scipy": "1.18.1", "pyarrow": "23.0.1", "joblib": "1.6.0"}.

Inputs: the 16 retained Phase 4 z-scores documented in PHASE5_FEATURE_SET.md. REV_5 is excluded as exactly -RET_5. Eligibility, factors, target, dates and upstream preprocessing are immutable. Tree inputs use stateless complete-case identity; no extra scaler/imputer. Ridge retains its frozen training-only scaler. No rows are forward-filled.

Signal after close(t); entry at adjusted open(t+1); exit adjusted open(t+6). Target is the adjusted-open return proxy; no same-close execution or capital/transaction-cost assumptions.

Ten expanding training / prior-year validation / annual test folds, 2017–2026, reuse Phase 4 exactly with label-end purges. No validation refit. Two fixed configurations per nonlinear family per fold; validation mean daily RankIC selects parameters, MSE then grid order break ties. Test never selects parameters, sign, features or early stopping. All 40 trials and selected configurations are in reports/phase5/hyperparameter_trials.csv.

Base Python/NumPy seed 42, model seed 42 + test year, explicit LightGBM bagging/feature/data seeds; CPU deterministic mode, four workers and one BLAS thread. Controls use the documented fixed seed offsets; random feature is keyed SHA-256 noise. Config and versions are serialized per fold and in reports/phase5/config.json. Same-environment toy repeats/reloads agree to 1e-12; portability across versions/hardware is not guaranteed.

Saved model/metadata/prediction artifacts: experiments\phase5\20261009T033111412374Z. Reused linear models point to frozen Phase 4 provenance; fitted trees and diagnostic models have joblib snapshots. Every prediction has model/version/fold/full boundaries/selected parameters/eligibility/feature version/source dataset ID and inherited bias flags. Source Phase 3 ID 20261008T141100218333Z; SHA-256 0da610d74a63cfd48c003dce4372933eb14c5e4b365b0dbe11ae10df0b3470cf.

Metrics are loaded from saved test Parquets. Primary Ridge remains fixed although observed Lasso/OLS are stronger than Ridge. Best ML (RandomForest) is a descriptive label after both fixed families are evaluated, not a test-selected deployment policy. Nonlinear ablation instead chooses the validation-winning family separately per fold and fixes its all-feature parameters.

Limitations: survivor/candidate selection, globally quarantined vendor integrity, adjusted-price proxy and possible vendor revisions, absent PIT index/sector/size membership, complete-case sample restriction, overlapping 5D targets, limited model grid, correlated importance, only ten folds and partial 2026. HAC intervals are asymptotic and do not correct all exploratory comparisons or research history. No costs, capital, risk neutralization, leverage, trading constraints or delisting reconstruction. Controls cannot certify an unbiased pipeline. Importance is not causal evidence.

Conclusion: NO RELIABLE IMPROVEMENT. Engineering decision: PASS. See reports/ml_walkforward_report.md for paired evidence and reports/phase5/failure_analysis.md for weak years and warnings. Stop before Phase 6.

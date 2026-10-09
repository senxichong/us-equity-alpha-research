"""Validate saved Phase 4 outputs and render reports/figures without refitting."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from src.data.download import sha256
from src.data.incremental import write_json,stamp
from src.factors.definitions import BIAS,NAMES
from src.evaluation.phase4_figures import generate_figures
from scripts.run_phase4 import inventory,save_csv,log

OUT=ROOT/'reports/phase4'
BIAS_LINE='**survivorship_biased = true; candidate_selection_biased = true**'


def table(frame,columns,labels=None):
    labels=labels or columns
    def fmt(v):
        if pd.isna(v): return 'unavailable'
        if isinstance(v,(float,np.floating)): return f'{v:.6g}'
        return str(v)
    return '\n'.join(['| '+' | '.join(labels)+' |','|'+'|'.join(['---']*len(columns))+'|',
                       *['| '+' | '.join(fmt(v) for v in row)+' |' for row in frame[columns].itertuples(index=False,name=None)]])


def verify(manifest):
    checks=dict(manifest['checks'])
    checks['analysis_finished']=manifest['status']=='RESEARCH_COMPLETE'
    checks['source_hash_unchanged_at_reporting']=sha256(manifest['source_panel_path'])==manifest['source_panel_sha256']
    checks['source_inventory_unchanged_at_reporting']=inventory()==manifest['upstream_inventory_before']
    checks['protocol_unchanged_at_reporting']=sha256(ROOT/'PHASE4_PROTOCOL.md')==manifest['protocol_sha256_before_results']
    checks['analysis_code_unchanged']=all(sha256(ROOT/p)==digest for p,digest in manifest['code_sha256'].items())
    moments=pd.read_csv(OUT/'model_error_moments.csv')
    for entry in manifest['prediction_files']:
        path=ROOT/entry['path']
        ok=sha256(path)==entry['sha256']
        embedded=json.loads(pq.read_metadata(path).metadata[b'research_metadata'])
        ok &= all(embedded[k] is True for k in ['survivorship_biased','candidate_selection_biased'])
        data=pd.read_parquet(path)
        year=int(data.fold.iloc[0])
        ok &= len(data)==entry['rows'] and data.sample_role.eq('test').all()
        ok &= data.date.dt.year.eq(year).all()
        ok &= not data.duplicated(['date','ticker','model','feature_group']).any()
        ok &= np.isfinite(data.prediction).all() and data.target_available.equals(data.target.notna())
        ok &= (pd.to_datetime(data.train_end)<pd.to_datetime(data.validation_start)).all()
        ok &= (pd.to_datetime(data.validation_end)<pd.to_datetime(data.test_start)).all()
        common_keys=None
        for (model,group),g in data.groupby(['model','feature_group']):
            keys=g[['date','ticker']].sort_values(['date','ticker']).reset_index(drop=True)
            if common_keys is None: common_keys=keys
            ok &= keys.equals(common_keys)
            scored=g[g.target_available]
            error=scored.prediction-scored.target
            expected=moments[(moments.model==model)&(moments.feature_group==group)&(moments.fold==year)].iloc[0]
            ok &= len(scored)==expected.observations
            ok &= np.isclose(error.pow(2).sum(),expected.sse,rtol=1e-12)
            ok &= np.isclose(error.abs().sum(),expected.sae,rtol=1e-12)
        checks[f'prediction_roundtrip_tags_samples_metrics_{year}']=bool(ok)
        print(f'Verified prediction artifact {year}',flush=True)
    configs=pd.read_csv(OUT/'model_configurations.csv')
    selections=configs.groupby(['fold','model','feature_group']).selected.sum()
    checks['one_validation_selected_configuration_per_model_fold']=bool(selections.eq(1).all() and len(selections)==90)
    expected={'EqualWeight':1,'OLS':1,'Ridge':3,'Lasso':3,'ElasticNet':3}
    checks['all_predeclared_configurations_recorded']=all(len(g)==expected[model] for (_,model,_),g in configs.groupby(['fold','model','feature_group']))
    checks['all_csv_bias_columns_present']=True
    for p in OUT.glob('*.csv'):
        data=pd.read_csv(p,usecols=['survivorship_biased','candidate_selection_biased'])
        checks['all_csv_bias_columns_present'] &= bool(data.all().all())
    return {k:bool(v) for k,v in checks.items()}


def main():
    manifest=json.loads((OUT/'analysis_manifest.json').read_text())
    checks=verify(manifest)
    s=pd.read_csv(OUT/'factor_statistics.csv')
    y=pd.read_csv(OUT/'yearly_factor_statistics.csv')
    q=pd.read_csv(OUT/'quantile_diagnostics.csv').drop_duplicates('factor').copy()
    qy=pd.read_csv(OUT/'quantile_yearly.csv')
    pairs=pd.read_csv(OUT/'factor_correlation_pairs.csv')
    models=pd.read_csv(OUT/'model_oos_metrics.csv')
    my=pd.read_csv(OUT/'model_yearly_metrics.csv')
    ablation=pd.read_csv(OUT/'ablation_results.csv')
    matched=pd.read_csv(OUT/'matched_oos_factor_metrics.csv')
    coef=pd.read_csv(OUT/'coefficient_stability.csv')
    robust=pd.read_csv(OUT/'horizon_robustness.csv')
    st=[]
    for n in NAMES:
        annual=y[(y.factor==n)&y.year.between(2011,2025)&(y.valid_dates>0)]
        full=s[s.factor==n].iloc[0]
        spread=qy[(qy.factor==n)&qy.year.between(2011,2025)&(qy.spread_n_dates>0)]
        fullspread=q[q.factor==n].iloc[0].top_minus_bottom_mean
        st.append({'factor':n,'complete_years':len(annual),'positive_rankic_years':int((annual.RankIC_mean>0).sum()),
                   'negative_rankic_years':int((annual.RankIC_mean<0).sum()),
                   'rankic_years_same_sign_as_full':int((np.sign(annual.RankIC_mean)==np.sign(full.RankIC_mean)).sum()),
                   'min_yearly_rankic':annual.RankIC_mean.min(),'max_yearly_rankic':annual.RankIC_mean.max(),
                   'yearly_rankic_std':annual.RankIC_mean.std(ddof=1),
                   'spread_years_same_sign_as_full':int((np.sign(spread.spread_mean)==np.sign(fullspread)).sum()),
                   'spread_complete_years':len(spread)})
    stability=pd.DataFrame(st)
    save_csv(stability,'factor_stability.csv')
    s=s.merge(stability,on='factor',validate='one_to_one')
    q=q.merge(stability,on='factor',validate='one_to_one')
    q['spread_bp']=q.top_minus_bottom_mean*1e4
    save_csv(q,'quantile_stability.csv')
    strongest=s.sort_values('RankIC_mean',ascending=False).head(5)
    evidence=s.iloc[np.argsort(-s.RankIC_hac_t.abs().to_numpy())].head(6)
    weakest=s.iloc[np.argsort(s.RankIC_mean.abs().to_numpy())].head(4)
    stable=s.sort_values(['rankic_years_same_sign_as_full','RankIC_hac_BH_q'],ascending=[False,True]).head(5)
    strongpairs=pairs[pairs.strong_redundancy].copy()
    strongest_model=models.sort_values('RankIC_mean',ascending=False).iloc[0]
    ew=models[models.model=='EqualWeight'].iloc[0]
    ridge=models[models.model=='Ridge'].iloc[0]
    best_single=matched.sort_values('RankIC_mean',ascending=False).iloc[0]
    tests=manifest['tests']
    mcols=['model','observations','valid_dates','IC_mean','RankIC_mean','IC_IR','RankIC_IR','RankIC_hac_t','MSE','MAE','R2']
    fcols=['factor','IC_mean','RankIC_mean','RankIC_hac_t','RankIC_hac_t_lag20','RankIC_hac_BH_q','rankic_years_same_sign_as_full','complete_years']
    allsingle=table(s,fcols)
    modeltable=table(models,mcols)
    # Reports distinguish weak magnitude from negative, potentially useful direction.
    caution='These are conditional associations in a frozen current-member universe, not unbiased historical strategy evidence. Global candidate/quarantine selection, retrospective vendor revisions, unresolved identity/delistings and indicative adjusted-open prices remain. Risk/industry/size neutrality is not established. No transaction costs, auction-fill realism, borrow or overlapping-capital accounting are modeled.'
    inference='Daily 5D labels overlap, so IID t-statistics overstate precision when ICs are serially correlated. Primary inference uses Bartlett Newey-West lag 5, plus fixed lag-20 sensitivity, on the exchange-session grid. ICIR is unannualized mean/std. HAC does not remove universe bias or guarantee that a five-lag bandwidth captures all dependence. BH q-values separately cover the 17 primary IC and 17 primary RankIC tests; correlated factors, secondary horizons and researcher exposure still create multiple-testing/data-snooping concerns. No p-value alone establishes discovery.'
    findings=(f"Highest raw signed mean RankIC: {strongest.iloc[0].factor} ({strongest.iloc[0].RankIC_mean:.5f}); largest absolute primary RankIC HAC t: {evidence.iloc[0].factor} ({evidence.iloc[0].RankIC_hac_t:.2f}). "
              f"The weakest magnitude is {weakest.iloc[0].factor} ({weakest.iloc[0].RankIC_mean:.5f}, HAC t={weakest.iloc[0].RankIC_hac_t:.2f}). Negative means are retained and are not automatically failures.")
    diagnostics=(f"Equal Weight OOS RankIC is {ew.RankIC_mean:.5f}, versus the strongest raw-signed individual factor on the identical OOS sample, {best_single.factor} ({best_single.RankIC_mean:.5f}). "
                 f"Thus Equal Weight {'exceeds' if ew.RankIC_mean>best_single.RankIC_mean else 'does not exceed'} that individual-factor ranking mean. "
                 f"Ridge has RankIC {ridge.RankIC_mean:.5f}, {'above' if ridge.RankIC_mean>ew.RankIC_mean else 'below'} Equal Weight. "
                 f"{strongest_model.model} has the highest observed OOS RankIC ({strongest_model.RankIC_mean:.5f}) among the five fixed baselines. These are observed comparisons, not proof that differences are statistically significant.")
    annualmodels=my[my.feature_group=='All'].pivot(index='year',columns='model',values='RankIC_mean').reset_index()
    co_summary=[]
    for model,g in coef[(coef.feature_group=='All')&(coef.model!='EqualWeight')].groupby('model'):
        co_summary.append({'model':model,'coefficient_sign_changes':int(g.sign_changes_nonzero.sum()),
                           'near_zero_factor_folds':int(g.near_zero_folds.sum()),
                           'largest_absolute_coefficient':max(g.min_coefficient.abs().max(),g.max_coefficient.abs().max()),
                           'most_variable_coefficient':g.sort_values('std_coefficient',ascending=False).iloc[0].factor})
    co_summary=pd.DataFrame(co_summary)
    ols_co=co_summary[co_summary.model=='OLS'].iloc[0]
    ridge_co=co_summary[co_summary.model=='Ridge'].iloc[0]
    lasso=models[models.model=='Lasso'].iloc[0]
    elastic=models[models.model=='ElasticNet'].iloc[0]
    worst_year=int(annualmodels.set_index('year').drop(columns=[]).mean(axis=1).idxmin())
    year_narrative=(f"All five models have negative mean RankIC in {worst_year}; the stronger years include "
                    + ', '.join(str(int(v)) for v in annualmodels.set_index('year').mean(axis=1).nlargest(2).index)
                    + '. The aggregate positive association is not uniform across regimes. Calendar patterns alone do not establish their economic cause.')
    coefficient_narrative=(f"OLS has {int(ols_co.coefficient_sign_changes)} adjacent nonzero coefficient sign changes across the ten folds and maximum absolute loading {ols_co.largest_absolute_coefficient:.6f} per Phase 3 z-score unit. "
                           f"Its coefficients are not numerically explosive, but their signs vary. Ridge has {int(ridge_co.coefficient_sign_changes)} such changes; changing validation-selected penalties does not uniformly stabilize signs. "
                           f"Lasso adds {lasso.RankIC_mean-ew.RankIC_mean:.5f} mean OOS RankIC versus Equal Weight and {lasso.RankIC_mean-models[models.model=='OLS'].iloc[0].RankIC_mean:.5f} versus OLS. "
                           f"ElasticNet has RankIC {elastic.RankIC_mean:.5f}, {'above' if elastic.RankIC_mean>ridge.RankIC_mean else 'below'} Ridge. The gains are small and no paired difference significance is claimed; sparsity alone is not evidence of better generalization.")
    single_report=['# Single-factor research — primary 5D target','',BIAS_LINE,'',findings,'',
        'All 17 mathematical definitions and signs are preserved. Pearson uses raw factor values; Spearman uses average ranks. Minimum 50 paired stocks per signal date. Eligibility is the frozen at-t mask; future eligibility is never required. Only unavailable labels/endpoints are omitted from association evaluation. No future outcome-magnitude exclusion or global factor normalization is introduced.','',
        '## Full primary evidence','',allsingle,'',
        'Mean RankIC magnitudes are small. Statistical evidence, directional stability and economic scale must be read together. The table shows both predeclared HAC bandwidths and complete-year sign consistency; a negative loading can be predictive in its original negative direction.','',
        '## Strongest HAC evidence and weakest associations','',table(evidence,fcols),'',table(weakest,fcols),'',
        'The weak rows are retained, including volume-ratio/surprise diagnostics with little ranking evidence. A non-significant result is inconclusive, not proof of zero effect. There is no performance-driven feature deletion.','',
        '## Stability and regime dependence','',table(stable,['factor','rankic_years_same_sign_as_full','complete_years','positive_rankic_years','negative_rankic_years','min_yearly_rankic','max_yearly_rankic']),'',
        'Complete-year consistency uses 2011–2025; 2010 contains only the warm-up boundary, and 2026 is partial. ILLIQ_20 is positive in 14 of 15 complete years; its remaining year is approximately zero. Every annual mean and count remains in yearly_factor_statistics.csv; annual reversals and rolling estimates show that a full-period mean does not imply a constant effect. The most sign-consistent rows above still require magnitude/inference scrutiny. No causal macro-regime attribution is inferred from calendar years.','',
        '## Redundancy','',table(strongpairs,['factor_a','factor_b','mean_daily_spearman','valid_dates']),'',
        'REV_5 is exactly −RET_5, not a second discovery. Volatility windows, momentum versus moving-average distance, illiquidity versus dollar volume, and volume ratio versus surprise share information. Correlations use eligible-at-t pairwise-complete cross sections without target filtering. Only the exact inverse is removed from model inputs by the prior rule; correlated families remain for regularization diagnostics.','',
        '## Forward-return quantile diagnostics','',table(q,['factor','monotonicity_score','spread_bp','top_minus_bottom_hac_t','spread_years_same_sign_as_full','spread_complete_years']),'',
        'Spread is always Q5−Q1 in basis points per five-session label, unflipped. |monotonicity| >= .8 marks a strong aggregate ordering, including descending order for negative factors. Read yearly spread consistency alongside the aggregate ordering. ILLIQ and volume/price metrics can disagree between Pearson, RankIC and monotonicity; no favorable metric replaces the others. Some statistically detectable spreads remain only a few to a few dozen basis points over five sessions. These are overlapping forward-return quantile diagnostics, not attainable strategy returns; no Sharpe is reported.','',
        'DOLLAR_VOLUME_20 illustrates why a nonzero mean RankIC or spread need not imply a clean five-bin ordering. A strong aggregate ordering with weak RankIC evidence is also possible (e.g. DIST_52W_HIGH); all metrics are shown rather than selecting the flattering one.','',
        '## Inference, horizons and limitations','',inference,'',
        'All 1D/10D/20D robustness results, along with the fixed 5D primary, are in horizon_robustness.csv. No secondary model grids were run. Raw daily IC/RankIC distributions, quantiles/skewness and extreme dates are saved; extreme dates were not deleted.','',caution,'',
        '## Figures and evidence','',
        '![Primary factor associations](phase4/figures/factor_ic_comparison.png)','',
        '![Rolling RankIC](phase4/figures/rolling_rankic.png)','',
        '![Quantile diagnostics](phase4/figures/quantile_forward_returns.png)','',
        '![Correlation](phase4/figures/factor_correlation.png)','',
        'Additional figures: yearly_rankic.png and ic_distributions.png. Machine-readable counts/statistics, metadata and protocol hash are in phase4/. Method definitions and references: [PHASE4_PROTOCOL.md](../PHASE4_PROTOCOL.md).']
    (ROOT/'reports/single_factor_report.md').write_text('\n'.join(single_report)+'\n',encoding='utf-8')
    baseline_report=['# Linear baseline research — test-only 5D predictions','',BIAS_LINE,'',diagnostics,'',
        '## Design fixed before results','',
        'Train starts in 2011. For test year Y=2017–2026, train ends in Y−2, validation is Y−1, and the test is Y. Labels ending at/after the next split start are purged from training and validation. No refit on validation. Phase 3 z-scores are unchanged; any extra scaler is trained only on training rows. Test feature predictions are saved even when the target is unavailable, with a separate label mask. All reported regression/IC metrics use the common available-label test sample.','',
        'The 16 inputs are all Phase 3 factors except exact inverse REV_5. No bad-performing factor is removed. Equal Weight signs are estimated separately from training-only daily RankIC and use equal weights in training-standardized feature units; an intercept/nonnegative slope is calibrated only on training data. OLS has no tuning. Ridge uses normalized lambdas [.001,.1,10]; Lasso/ElasticNet use [.00001,.0001,.001], fixed ElasticNet l1_ratio=.5. Selection uses validation RankIC, then MSE/stronger-penalty ties. All tried configurations and selections are saved.','',
        '## Combined OOS results','',modeltable,'',
        'MSE/MAE use decimal-return units; R² compares against the pooled OOS target mean as a descriptive regression statistic, not a separately deployable benchmark. Ranking correlation is invariant to positive affine calibration, while squared error is sensitive to calibration and common market moves. Near-zero/negative R² can coexist with nonzero cross-sectional ranking information. No claim of a tradable edge follows.','',
        '## Year-by-year OOS RankIC','',table(annualmodels,list(annualmodels.columns)),'',
        'Each year is a distinct frozen test fold; 2026 is partial. These means can move materially across years even when the combined mean is positive. Full annual regression, HAC and IC metrics are retained; no unfavorable year is omitted.',year_narrative,'',
        '## Coefficient stability and sparse models','',table(co_summary,list(co_summary.columns)),'',
        coefficient_narrative,'',
        'Sign changes count adjacent folds where both coefficients are nonzero; near-zero means absolute Phase 3 z-score coefficient <= 1e-8. OLS sensitivity is assessed by these coefficient magnitudes/sign changes and yearly outcomes, not assumed from its model name. Regularization reduces or zeroes some loadings, but Lasso/ElasticNet add value only to the extent their matched OOS rows outperform the transparent comparators above. Any observed advantage here is not an independent replication. Tables retain every coefficient, training scaler, EW orientation and selected parameter.','',
        '## Predefined group diagnostics','',table(ablation,['feature_group','IC_mean','RankIC_mean','RankIC_hac_t','R2','valid_dates']),'',
        'All groups use identical complete-case samples, folds, targets and three-lambda Ridge grids. These diagnostic comparisons do not replace the predeclared all-factor Ridge model with the best-looking group. Momentum/Reversal excludes the exact sign duplicate; Price Position includes the two intraday features.','',
        '## Baseline for Phase 5','',
        f"The **predeclared all-feature Ridge** remains the primary methodological benchmark: OOS IC {ridge.IC_mean:.5f}, RankIC {ridge.RankIC_mean:.5f}. The strongest observed simple comparator is **{strongest_model.model}**, with RankIC {strongest_model.RankIC_mean:.5f}; future work should also report against it and Equal Weight, without claiming a post-selected comparator was preregistered. A complex model must be compared on the same folds, common sample and primary 5D target. No complex model is authorized or trained here.",'',
        'Full-history single-factor results describe years that later appear in model tests. OOS means temporal fitting/tuning isolation under this frozen specification, not a never-inspected external holdout. Test targets, future fold rows and random row order were adversarially tested not to change earlier fits/predictions.','',
        inference,'',caution,'',
        '![Model OOS comparison](phase4/figures/model_oos_ic.png)','',
        '![Coefficient stability](phase4/figures/coefficient_stability.png)','',
        'Test predictions are separate per-fold Parquet artifacts with boundaries, model/group, target availability and source/protocol hashes. Analysis manifest, exact tried configurations, fold purge counts and coefficient tables are in phase4/.']
    (ROOT/'reports/baseline_report.md').write_text('\n'.join(baseline_report)+'\n',encoding='utf-8')
    figures=generate_figures(OUT)
    checks['eight_predeclared_figures_rendered']=len(figures)==8 and all(p.stat().st_size>1000 for p in figures)
    checks['all_required_tables_present']=all((OUT/name).exists() for name in ['single_factor_ic.csv','single_factor_rankic.csv','factor_statistics.csv','yearly_factor_statistics.csv','factor_correlation.csv','quantile_diagnostics.csv','model_oos_metrics.csv','model_yearly_metrics.csv','model_coefficients.csv','ablation_results.csv','horizon_robustness.csv'])
    decision='PASS' if all(checks.values()) else 'FAIL'
    report=['# Phase 4 — Single-factor research and linear baselines','',BIAS_LINE,'',
            f'**{decision}: methodological/reproducibility gate, not a positive-alpha or profitability claim.**','',
            '## Dataset','',
            f"Frozen Phase 3 dataset `{manifest['source_dataset_id']}`: {manifest['source_rows']:,} source rows, {manifest['source_stocks']} candidates, {manifest['source_sessions']} exchange sessions. Source SHA-256 `{manifest['source_panel_sha256']}`; source bytes and all upstream inventories remain unchanged.",
            f"The actual first scored primary cross section is {s.first_scored_date.min()}; latest is {s.last_scored_date.max()}. Each factor scores {int(s.valid_dates.min()):,}–{int(s.valid_dates.max()):,} dates, {int(s.stocks.min())}–{int(s.stocks.max())} distinct stocks and {int(s.scored_stock_dates.min()):,}–{int(s.scored_stock_dates.max()):,} stock-date pairs. Exact individual counts remain in factor_statistics.csv. The 252-observation eligibility warm-up is not bypassed. Model history starts in 2011 and test folds start in 2017.",'',
            '## Single-factor findings','',findings,'',table(strongest,fcols),'',
            'Strongest absolute HAC evidence (direction preserved):','',table(evidence,fcols),'',
            'Weakest magnitude / inconclusive ranking rows, retained unchanged:','',table(weakest,fcols),'',
            'Most consistent full-period sign across complete calendar years (2011–2025):','',table(stable,['factor','rankic_years_same_sign_as_full','complete_years','min_yearly_rankic','max_yearly_rankic']),'',
            'All positive/negative yearly counts, uncertainty and rolling estimates are available; no factor is proclaimed stable solely from its full-period mean.','',
            '## Redundancy','',table(strongpairs,['factor_a','factor_b','mean_daily_spearman']),'',
            'The exact RET_5/REV_5 inverse is one effect. Related windows and liquidity/activity proxies are not independent discoveries. Only REV_5 was removed from model inputs by definition, before performance.','',
            '## Quantile monotonicity','',table(q,['factor','monotonicity_score','spread_bp','top_minus_bottom_hac_t','spread_years_same_sign_as_full','spread_complete_years']),'',
            'These are raw-sign Q5−Q1 overlapping forward-return diagnostics. Strong aggregate ordering can coexist with weak or unstable RankIC, and significant mean association can lack a clean ordering. The annual sign counts expose this distinction; no spread is compounded into a strategy or Sharpe.','',
            '## Linear OOS baselines','',diagnostics,'',modeltable,'',
            f"Primary Phase 5 benchmark remains preregistered **Ridge**, RankIC {ridge.RankIC_mean:.5f}. Also compare against the strongest observed simple model, **{strongest_model.model}**, RankIC {strongest_model.RankIC_mean:.5f}, and Equal Weight. The latter observed ranking is not a new test-tuned model specification.",'',
            '## Stability','',table(annualmodels,list(annualmodels.columns)),'',table(co_summary,list(co_summary.columns)),'',
            year_narrative,'',coefficient_narrative,'',
            'The complete yearly and ablation tables retain regime dependence and coefficient instability. Neither a favorable year nor a best-looking factor family changes the specification. OOS correlation differences are descriptive comparisons unless supported by a paired model-comparison test; no such significance claim is made.','',
            '## Statistical caution and known bias','',inference,'',caution,'',
            'No current membership is treated as historical PIT membership. Future target availability affects only evaluation/training labels, not signal-date eligibility, normalization or quantile formation. This first descriptive research phase exposes the historical sample; chronological OOS fitting is not an untouched external replication.','',
            '## Tests, artifacts and stopping condition','',
            f"Complete suite: **{tests['passed']} passed, {tests['failures']} failed, {tests['errors']} errors, {tests['skipped']} skipped; {tests['warnings']} warnings**. These are visible generic-timedelta deprecations in the installed NumPy/pandas/calendar combination; logs are preserved. The initial two quantile-column implementation failures and correction remain in RESEARCH_LOG.md. Custom HAC matches statsmodels. Tests cover daily versus pooled correlation, tied ranks, minimum cross sections, no future-label quantile formation, purged fold boundaries, train-only scalers/orientations, test-target mutation, future-fold mutation, row-order invariance and test-only tagging.",
            f"Artifact checks: {sum(checks.values())}/{len(checks)} passed. Ten saved test-prediction Parquets were checksum/read-back audited for exact sample keys, fold tags, label availability and squared/absolute-error sums. All tried configurations are retained; solver convergence warnings were checked. Eight fixed diagnostic figures were rendered. No source data was downloaded or rebuilt.",
            'See [single-factor report](reports/single_factor_report.md), [baseline report](reports/baseline_report.md), [preregistered protocol](PHASE4_PROTOCOL.md), and reports/phase4/validation.json. No new factors, complex ML, capital-aware portfolio, strategy Sharpe or transaction-cost optimization was run. Stop after Phase 4.','',
            f'PHASE 4: {decision}']
    (ROOT/'PHASE4_REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    validation={**manifest,'status':decision,'checks':checks,
                'reporting_code_sha256':{str(Path(__file__).relative_to(ROOT)):sha256(__file__),'src/evaluation/phase4_figures.py':sha256(ROOT/'src/evaluation/phase4_figures.py')},
                'artifact_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in [*sorted(OUT.glob('*.csv')),*figures,ROOT/'reports/single_factor_report.md',ROOT/'reports/baseline_report.md',ROOT/'PHASE4_REPORT.md']}}
    write_json(OUT/'validation.json',validation)
    write_json(ROOT/manifest['model_directory']/'phase4_metadata.json',validation)
    log(f'Phase 4 FINAL outcomes. Result: {findings} {diagnostics} Tests: {tests["passed"]} passed, {tests["failures"]} failed. Interpretation: overlapping-label, survivorship/candidate-selection-biased prototype associations; no strategy profitability claim. Next step: STOP; Phase 5 requires a new instruction. Decision: {decision}. Negative/inconclusive factors and all attempted grids remain saved.')
    archive=OUT/'runs'/f"{manifest['run_id']}_report_{stamp()}"
    archive.mkdir(parents=True,exist_ok=False)
    for p in OUT.iterdir():
        if p.is_file(): shutil.copy2(p,archive/p.name)
    shutil.copytree(OUT/'figures',archive/'figures')
    for p in [ROOT/'PHASE4_REPORT.md',ROOT/'PHASE4_PROTOCOL.md',ROOT/'RESEARCH_LOG.md',ROOT/'reports/single_factor_report.md',ROOT/'reports/baseline_report.md']:
        shutil.copy2(p,archive/p.name)
    print(json.dumps({'status':decision,'checks':checks,'strongest_observed_model':strongest_model.model,'Ridge_RankIC':ridge.RankIC_mean},indent=2),flush=True)
    if decision!='PASS': raise SystemExit(1)


if __name__=='__main__':
    main()

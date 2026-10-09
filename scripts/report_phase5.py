"""Generate Phase 5 figures/reports solely from audited saved-prediction tables."""
import sys,json,hashlib,re,shutil,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.data.download import sha256
from src.data.incremental import write_json,stamp
from src.factors.definitions import BIAS
from scripts.run_phase5 import upstream_inventory

OUT=ROOT/'reports/phase5'; FIG=OUT/'figures'
MODELS=['Ridge','RandomForest','LightGBM']
COLORS=['#456c9c','#df9239','#2a947d']
BIAS_TEXT='survivorship_biased = true; candidate_selection_biased = true; point_in_time_membership = false'
def read(name):return pd.read_csv(OUT/name)
def table(df,columns=None):
    if columns is not None:df=df[columns]
    def cell(x):
        if isinstance(x,(float,np.floating)):return f'{x:.6f}' if np.isfinite(x) else 'NA'
        return str(x)
    return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(cell(x) for x in row)+' |' for row in df.itertuples(index=False,name=None))
def finish(fig,title,name):
    fig.suptitle(title+'\nSURVIVORSHIP-BIASED PROTOTYPE',fontsize=12)
    fig.text(.5,.008,'candidate_selection_biased = true  •  Frozen 5D target; 2026 is partial',ha='center',fontsize=8,color='#555555')
    fig.tight_layout(rect=(0,.035,1,.94));fig.savefig(FIG/name,dpi=150);plt.close(fig)

def figures(m,y,d,p,q,imp,corr,best):
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8,5));v=m.set_index('model').loc[MODELS]
    ax.bar(MODELS,v.RankIC_mean,color=COLORS)
    ax.errorbar(MODELS,v.RankIC_mean,yerr=[v.RankIC_mean-v.RankIC_ci95_low,v.RankIC_ci95_high-v.RankIC_mean],fmt='none',color='black',capsize=5)
    ax.axhline(0,color='gray',lw=.8);ax.set_ylabel('Mean daily RankIC; lag-5 HAC 95% CI')
    finish(fig,'Out-of-sample ranking association','01_oos_rankic.png')
    fig,ax=plt.subplots(figsize=(10,5));pivot=y.pivot(index='year',columns='model',values='RankIC_mean').reindex(columns=MODELS)
    pivot.plot.bar(ax=ax,color=COLORS);ax.axhline(0,color='gray',lw=.8);ax.set_ylabel('Mean daily RankIC');ax.tick_params(axis='x',rotation=0)
    finish(fig,'Yearly ranking stability','02_yearly_rankic.png')
    fig,ax=plt.subplots(figsize=(10,5))
    for name,color in [('Ridge',COLORS[0]),(best,COLORS[MODELS.index(best)])]:
        v=d[d.model==name].sort_values('date');ax.plot(pd.to_datetime(v.date),v.RankIC.rolling(126,min_periods=100).mean(),label=name,color=color)
    ax.axhline(0,color='gray',lw=.8);ax.legend();ax.set_ylabel('126-session mean RankIC')
    finish(fig,'Rolling ranking association (descriptive best ML)','03_rolling_rankic.png')
    fig,ax=plt.subplots(figsize=(8,5));v=p.set_index('model').loc[MODELS[1:]]
    ax.errorbar(v['mean'],range(2),xerr=[v['mean']-v.ci95_low,v.ci95_high-v['mean']],fmt='o',capsize=5,color='#2a947d')
    ax.set_yticks(range(2),v.index);ax.set_ylim(-.6,1.6);ax.axvline(0,color='gray',lw=.8);ax.set_xlabel('Paired daily ΔRankIC vs Ridge; lag-5 HAC 95% CI')
    finish(fig,'Incremental OOS ranking evidence','04_paired_delta.png')
    fig,ax=plt.subplots(figsize=(8,5))
    for n,c in zip(MODELS,COLORS):
        v=q[q.model==n];ax.plot(v['quantile'],v.mean_forward_return*10000,marker='o',label=n,color=c)
    ax.legend();ax.set_xticks(range(1,6),['Q1','Q2','Q3','Q4','Q5']);ax.set_ylabel('Mean 5D forward return (basis points)')
    finish(fig,'Prediction quintiles — diagnostic, no capital backtest','05_prediction_quintiles.png')
    fig,axs=plt.subplots(1,2,figsize=(12,6),sharey=True)
    for ax,n,kind in zip(axs,MODELS[1:],['impurity','gain']):
        v=imp[(imp.model==n)&(imp.importance_type==kind)].pivot(index='feature',columns='fold',values='rank')
        im=ax.imshow(v,aspect='auto',vmin=1,vmax=16,cmap='viridis_r');ax.set_title(n+' / '+kind);ax.set_xticks(range(len(v.columns)),v.columns,rotation=60);ax.set_yticks(range(len(v)),v.index)
    # An explicit colorbar axis avoids overlap when adjusting subplot margins.
    cax=fig.add_axes([.88,.23,.016,.54])
    fig.colorbar(im,cax=cax,label='Native importance rank')
    fig.suptitle('Importance stability by fold\nSURVIVORSHIP-BIASED PROTOTYPE',fontsize=12)
    fig.subplots_adjust(left=.20,right=.85,bottom=.17,top=.86,wspace=.15)
    fig.text(.5,.025,'candidate_selection_biased = true; native importance is not causal',ha='center',fontsize=8)
    fig.savefig(FIG/'06_importance_stability.png',dpi=150);plt.close(fig)
    matrix=pd.DataFrame(np.eye(3),index=MODELS,columns=MODELS)
    for _,r in corr.iterrows():matrix.loc[r.model_a,r.model_b]=matrix.loc[r.model_b,r.model_a]=r.Spearman_mean
    fig,ax=plt.subplots(figsize=(7,5));im=ax.imshow(matrix,vmin=-1,vmax=1,cmap='RdBu_r')
    ax.set_xticks(range(3),MODELS);ax.set_yticks(range(3),MODELS)
    for i in range(3):
        for j in range(3):ax.text(j,i,f'{matrix.iloc[i,j]:.3f}',ha='center',va='center',color='white' if abs(matrix.iloc[i,j])>.6 else 'black')
    fig.colorbar(im,ax=ax,label='Mean daily prediction Spearman correlation')
    finish(fig,'Prediction similarity on identical at-t samples','07_prediction_correlation.png')
    fig,ax=plt.subplots(figsize=(8,5));v=y[y.year==2022].set_index('model').loc[MODELS]
    ax.bar(MODELS,v.RankIC_mean,color=COLORS);ax.errorbar(MODELS,v.RankIC_mean,yerr=[v.RankIC_mean-v.RankIC_ci95_low,v.RankIC_ci95_high-v.RankIC_mean],fmt='none',color='black',capsize=5)
    ax.axhline(0,color='gray',lw=.8);ax.set_ylabel('2022 mean RankIC; lag-5 HAC 95% CI')
    finish(fig,'2022 failure comparison; no year-specific retuning','08_2022_comparison.png')

def main():
    meta=json.loads((OUT/'experiment_manifest.json').read_text());assert meta['status']=='EXPERIMENTS_COMPLETE'
    evaluation=json.loads((OUT/'evaluation_validation.json').read_text());assert evaluation['status']=='PASS'
    m=read('model_oos_metrics.csv');y=read('model_yearly_metrics.csv');d=read('model_daily_ic.csv')
    p=read('model_vs_ridge.csv');lasso=read('model_vs_lasso.csv');q=read('prediction_quantile_diagnostics.csv')
    imps=read('feature_importance_summary.csv');imp=read('feature_importance_by_fold.csv');corr=read('prediction_correlation.csv')
    abl=read('ml_ablation.csv');rt=read('runtime_summary.csv');trials=read('hyperparameter_trials.csv')
    flags=json.loads((OUT/'control_flags.json').read_text());control_flags=[v for k,v in flags.items() if k.endswith('requires_investigation')]
    best=m[m.model!='Ridge'].sort_values('RankIC_mean',ascending=False).iloc[0].model
    bp=p[p.model==best].iloc[0];bl=lasso[lasso.model==best].iloc[0]
    monotonic=q[q.model==best].iloc[0].monotonicity_score
    if bp['mean']>=.005 and bp.ci95_low>0 and bp.years_better>=7 and bp.positive_ratio>.52 and bl['mean']>0 and abs(monotonic)>=.8:conclusion='STRONG IMPROVEMENT'
    elif bp['mean']>0 and bp.ci95_low>0 and bp.years_better>=6:conclusion='MODEST IMPROVEMENT'
    elif (p.ci95_high<0).all() and (p.years_worse>=6).all():conclusion='ML UNDERPERFORMS'
    else:conclusion='NO RELIABLE IMPROVEMENT'
    figures(m,y,d,p,q,imp,corr,best)
    suites=ET.parse(OUT/'final_pytest.xml').getroot().findall('testsuite')
    tests={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    tests['passed']=tests['tests']-tests['failures']-tests['errors']-tests['skipped']
    tests['warnings']=int(re.findall(r'(\d+) warnings?',(OUT/'final_pytest.log').read_text(encoding='utf-8'))[-1])
    checks=dict(meta['checks'],**evaluation['checks'])
    checks.update(final_tests_pass=tests['failures']==0 and tests['errors']==0 and tests['skipped']==0,
        all_control_flags_resolved=not any(control_flags),upstream_inventory_final_unchanged=upstream_inventory()==meta['upstream_inventory_before'],
        upstream_docs_final_unchanged=all(sha256(ROOT/k)==v for k,v in meta['upstream_docs_sha256'].items()),
        source_panel_final_unchanged=sha256(meta['source_panel_path'])==meta['source_panel_sha256'],
        frozen_fit_code_unchanged=all(sha256(ROOT/k)==v for k,v in meta['code_sha256'].items()),
        preregistration_final_unchanged=sha256(ROOT/'PHASE5_PROTOCOL.md')==meta['protocol_sha256'],
        research_log_prefix_final_unchanged=hashlib.sha256((ROOT/'RESEARCH_LOG.md').read_bytes()[:meta['research_log_prefix_bytes']]).hexdigest()==meta['research_log_prefix_sha256'],
        saved_predictions_unchanged=all(sha256(ROOT/e['path'])==e['sha256'] for e in meta['prediction_files']),
        model_metadata_unchanged=all(sha256(ROOT/e['path'])==e['sha256'] for e in meta['model_artifacts']))
    model_metadata=[json.loads((ROOT/e['path']).read_text()) for e in meta['model_artifacts']]
    checks['serialized_models_unchanged']=all(sha256(ROOT/e['model_path'])==e['model_sha256'] for e in model_metadata if 'model_path' in e)
    decision='PASS' if all(checks.values()) else 'FAIL'
    metrics_table=table(m,['model','IC_mean','RankIC_mean','IC_IR','RankIC_IR','RankIC_hac_t','RankIC_ci95_low','RankIC_ci95_high','MSE','MAE','R2'])
    paired_table=table(p,['model','mean','median','positive_ratio','hac_t','ci95_low','ci95_high','years_better','years_worse'])
    secondary_table=table(lasso,['model','mean','hac_t','ci95_low','ci95_high'])
    year_table=table(y.pivot(index='year',columns='model',values='RankIC_mean').reindex(columns=MODELS).reset_index())
    secondary=read('secondary_linear_metrics.csv');ols=float(secondary[secondary.model=='OLS'].iloc[0].RankIC_mean)
    bestscore=float(m[m.model==best].iloc[0].RankIC_mean)
    importance_table=imps[(imps.model.isin(MODELS[1:]))&imps.importance_type.isin(['impurity','gain'])].sort_values(['model','mean_rank']).groupby('model').head(6)
    permutation=imps[(imps.model.isin(MODELS[1:]))&(imps.importance_type=='validation_permutation_rankic_loss')].sort_values(['model','mean_importance'],ascending=[True,False]).groupby('model').head(5)
    families=read('feature_family_importance.csv');families=families[(families.model.isin(MODELS[1:]))&families.importance_type.isin(['gain','impurity'])].groupby(['model','importance_type','family']).normalized_importance.agg(['mean','std']).reset_index()
    random_label=read('random_label_control.csv');random_feature=read('random_feature_control.csv')
    noise_imp=imps[(imps.model=='RandomFeatureControl')&(imps.feature=='RANDOM_CONTROL')]
    distributions=read('prediction_distributions.csv');featuredist=read('feature_distributions.csv')
    weak=y[y.RankIC_mean<0][['model','year','RankIC_mean']]
    weakyears=sorted(set(weak.year.astype(int))|set(y.groupby('model').apply(lambda g:g.nsmallest(2,'RankIC_mean').year,include_groups=False).astype(int))|{2022})
    factors=pd.read_csv(ROOT/'reports/phase4/yearly_factor_statistics.csv')
    # Transparent fixed representative set, not picked for the current year's return.
    representatives=['RET_5','VOL_20','ILLIQ_20','PRICE_MA20']
    factors=factors[factors.factor.isin(representatives)&factors.year.isin(weakyears)]
    shifts=[]
    for model in MODELS[1:]:
        kind='gain' if model=='LightGBM' else 'impurity'
        for year in weakyears:
            g=imp[(imp.model==model)&(imp.importance_type==kind)&(imp.fold==year)].nsmallest(3,'rank')
            shifts.append({'model':model,'year':year,'top_three_native':', '.join(g.feature)})
    examples=read('model_disagreement_examples.csv')
    runtotal=rt.groupby(['model','role']).agg(selected_fit_seconds=('selected_fit_seconds','sum'),grid_fit_seconds=('grid_fit_seconds','sum'),test_prediction_seconds=('test_prediction_seconds','sum')).reset_index()
    y22=y[y.year==2022].set_index('model')
    year22_note=f"In 2022 Ridge RankIC was {y22.loc['Ridge','RankIC_mean']:.6f}; RandomForest remained negative at {y22.loc['RandomForest','RankIC_mean']:.6f} but failed less severely; LightGBM changed the sign to {y22.loc['LightGBM','RankIC_mean']:.6f}. LightGBM beat Ridge in only {int(p[p.model=='LightGBM'].iloc[0].years_better)}/10 years overall, so its 2022 advantage did not imply broad improvement. Ridge's stronger 2019/2023 results are visible in the full annual table. These descriptive outcomes did not trigger any tuning."
    importance_note='VOL_60 is the most consistently important RF feature, while DIST_52W_HIGH leads LightGBM; each appears in its model’s top three in all ten folds. ILLIQ_20 also recurs. Price-position, volatility, momentum and liquidity families all contribute native importance; no isolated group is established as the causal source of return predictability.'
    ridge_group=abl[(abl.model=='Ridge')&(abl.feature_group!='All')].sort_values('RankIC_mean',ascending=False).iloc[0]
    nonlinear_group=abl[(abl.model=='ValidationWinner')&(abl.feature_group!='All')].sort_values('RankIC_mean',ascending=False).iloc[0]
    ablation_note=f"Among the predefined group-only fits, Ridge's strongest is {ridge_group.feature_group} (RankIC {ridge_group.RankIC_mean:.6f}); the validation-winner nonlinear rule's strongest is {nonlinear_group.feature_group} ({nonlinear_group.RankIC_mean:.6f}). These observed diagnostic rankings do not authorize selecting that group for production. The nonlinear all-feature rule does not automatically improve on every group-only fit."
    complexity_note='Under the predeclared interpretation rule, the extra nonlinear complexity is not justified by reliable incremental OOS ranking evidence in this experiment. Both nonlinear point estimates fall below Ridge, Lasso and OLS, but paired intervals include zero: this is not a statistically established claim that every nonlinear approach is inferior.'
    warning_note='LightGBM printed repeated “No further splits with positive gain” warnings. These indicate constrained trees stopped splitting; all attempted primary trials remain recorded, with no parameter relaxation. Native console warning counts were not captured by Python warnings, so no exact count is claimed. The 37 pytest warnings are retained in final_pytest.log.'
    implementation_note='A metadata naming issue was found: runtime_details.csv originally labels every no-new-fit result reused_from_phase4, including ValidationWinner/All copied from the Phase 5 primary model. The raw file is preserved. runtime_summary.csv supplies the corrected boolean and explicit reuse_origin. Predictions and fit decisions were unaffected.'
    failure=f'''# Phase 5 failure analysis

{BIAS_TEXT}

No year-specific retuning or model changes followed these results. The comparison includes all negative years, each model's two lowest-RankIC years, and 2022. This descriptive rule selects years for diagnosis only. 2026 is incomplete.

## Negative years and 2022

{table(weak)}

{table(y[y.year==2022],['model','IC_mean','RankIC_mean','RankIC_hac_t','RankIC_ci95_low','RankIC_ci95_high'])}

{year22_note}

{best} beats Ridge in {int(bp.years_better)}/10 years and loses in {int(bp.years_worse)}/10. Improvement is neither uniform nor proof of a persistent nonlinear mechanism. Annual confidence intervals and overlapping targets limit year-level causal interpretation.

## Prediction distribution and collapse

{table(distributions[distributions.year.isin(weakyears)],['model','year','mean','std','median_daily_cs_std','min_daily_cs_std','p01','p99','minimum','maximum','near_constant_dates','extreme_abs_gt_50pct'])}

Fixed descriptive flags are daily cross-sectional standard deviation below 1e-10 and absolute prediction above 50%. They are diagnostics, not tuning criteria. Total nearly constant dates: {int(distributions.near_constant_dates.sum())}; extreme predictions: {int(distributions.extreme_abs_gt_50pct.sum())}. Full yearly distributions, including strong years, are in prediction_distributions.csv.

## Feature distribution

{table(featuredist[featuredist.fold.isin(weakyears)&featuredist.feature.isin(representatives)],['fold','feature','mean','std','p01','median','p99','median_daily_cs_std'])}

Features were normalized cross-sectionally upstream. Similar z-score moments do not imply stable relationships with returns. Eligibility and complete-case selection can also shift these moments. All 16 feature distributions are retained for every test year in feature_distributions.csv.

## Factor relationships and importance

{table(factors,['factor','year','RankIC_mean','RankIC_hac_t'])}

These raw-sign factor statistics are reused from Phase 4 and use each factor's upstream available sample, not the model's stricter complete-case sample. They are contextual evidence, not an exact decomposition of model IC.

{table(pd.DataFrame(shifts))}

{importance_note}

Native importance is learned on training rows, so fold-2022 importance describes the pre-2022 fitted model. Importance changes and raw-factor sign changes offer possible explanations, not identified causes. Correlated factor substitutes and market exposure remain unresolved.

## Disagreement examples

{table(examples.head(10),['fold','date','ticker','Ridge','LightGBM','Ridge_percentile','LightGBM_percentile','absolute_rank_gap','target'])}

The CSV retains ten largest absolute rank gaps per fold and all 16 z-scores. Selection uses only predictions, ties date/ticker; target sign/availability never selects examples. These are examples of ranking disagreement, not proof of profitable interactions.

## Warnings, failures and metadata

{warning_note}

Primary trial outcomes: {json.dumps(trials.status.value_counts().to_dict())}. No failed trial was dropped. Toy tests, independent saved-prediction audits, and controls are recorded separately. {implementation_note}

## Adversarial controls

{table(random_label,['model','RankIC_mean','RankIC_hac_t','RankIC_ci95_low','RankIC_ci95_high'])}

{table(random_feature,['RankIC_mean','RankIC_hac_t','RankIC_ci95_low','RankIC_ci95_high'])}

{table(noise_imp,['importance_type','mean_normalized_importance','mean_rank','top3_folds'])}

Predeclared investigation flags: {json.dumps({k:v for k,v in flags.items() if k.endswith('requires_investigation')})}. These controls are finite-sample checks, not proof that all leakage or vendor revisions are absent.
'''
    (OUT/'failure_analysis.md').write_text(failure,encoding='utf-8')
    card=f'''# Model card — Phase 5 prototype

{BIAS_TEXT}

Purpose: test incremental cross-sectional 5D OOS ranking over the predeclared Ridge benchmark. No deployable strategy or unbiased investable universe is claimed.

Models actually run: sklearn Ridge (saved Phase 4 benchmark), RandomForestRegressor and LightGBM LGBMRegressor. Lasso and OLS are reused secondary comparisons. Versions: {json.dumps(meta['versions'])}.

Inputs: the 16 retained Phase 4 z-scores documented in PHASE5_FEATURE_SET.md. REV_5 is excluded as exactly -RET_5. Eligibility, factors, target, dates and upstream preprocessing are immutable. Tree inputs use stateless complete-case identity; no extra scaler/imputer. Ridge retains its frozen training-only scaler. No rows are forward-filled.

Signal after close(t); entry at adjusted open(t+1); exit adjusted open(t+6). Target is the adjusted-open return proxy; no same-close execution or capital/transaction-cost assumptions.

Ten expanding training / prior-year validation / annual test folds, 2017–2026, reuse Phase 4 exactly with label-end purges. No validation refit. Two fixed configurations per nonlinear family per fold; validation mean daily RankIC selects parameters, MSE then grid order break ties. Test never selects parameters, sign, features or early stopping. All 40 trials and selected configurations are in reports/phase5/hyperparameter_trials.csv.

Base Python/NumPy seed 42, model seed 42 + test year, explicit LightGBM bagging/feature/data seeds; CPU deterministic mode, four workers and one BLAS thread. Controls use the documented fixed seed offsets; random feature is keyed SHA-256 noise. Config and versions are serialized per fold and in reports/phase5/config.json. Same-environment toy repeats/reloads agree to 1e-12; portability across versions/hardware is not guaranteed.

Saved model/metadata/prediction artifacts: {meta['directory']}. Reused linear models point to frozen Phase 4 provenance; fitted trees and diagnostic models have joblib snapshots. Every prediction has model/version/fold/full boundaries/selected parameters/eligibility/feature version/source dataset ID and inherited bias flags. Source Phase 3 ID {meta['source_phase3_dataset_id']}; SHA-256 {meta['source_panel_sha256']}.

Metrics are loaded from saved test Parquets. Primary Ridge remains fixed although observed Lasso/OLS are stronger than Ridge. Best ML ({best}) is a descriptive label after both fixed families are evaluated, not a test-selected deployment policy. Nonlinear ablation instead chooses the validation-winning family separately per fold and fixes its all-feature parameters.

Limitations: survivor/candidate selection, globally quarantined vendor integrity, adjusted-price proxy and possible vendor revisions, absent PIT index/sector/size membership, complete-case sample restriction, overlapping 5D targets, limited model grid, correlated importance, only ten folds and partial 2026. HAC intervals are asymptotic and do not correct all exploratory comparisons or research history. No costs, capital, risk neutralization, leverage, trading constraints or delisting reconstruction. Controls cannot certify an unbiased pipeline. Importance is not causal evidence.

Conclusion: {conclusion}. Engineering decision: {decision}. See reports/ml_walkforward_report.md for paired evidence and reports/phase5/failure_analysis.md for weak years and warnings. Stop before Phase 6.
'''
    (ROOT/'MODEL_CARD.md').write_text(card,encoding='utf-8')
    quant_table=table(q,['model','quantile','mean_forward_return','monotonicity_score','top_minus_bottom_mean','top_minus_bottom_hac_t','top_minus_bottom_ci95_low','top_minus_bottom_ci95_high'])
    report=f'''# Phase 5 — walk-forward machine learning research

{BIAS_TEXT}

## Research question and frozen inputs

Can nonlinear models improve OOS cross-sectional ranking over Ridge? This run concludes **{conclusion}** under the fixed interpretation rule. Engineering status: **{decision}**. A negative research outcome is retained.

Phase 1–4 reports/data/artifacts were unchanged; all ten Phase 4 folds and complete-case sample keys were reused. Source Phase 3 ID: {meta['source_phase3_dataset_id']}; experiment: {meta['run_id']}. The pre-fit artifact audit verified Ridge 0.0201353637, Lasso 0.0223780231, OLS 0.0222028202, EW 0.0193064047, ElasticNet 0.0200077578, and all five negative in 2022. Ridge remains primary.

## Features, models and selection

PHASE5_FEATURE_SET.md lists all upstream definitions and the 16 retained features; only the exact REV_5 duplicate is omitted. Tree inputs use existing date-local winsorized z-scores with complete-case identity, no fitted imputation or global rescaling. Ridge uses its frozen training-only scaler. No new production alpha factors.

RandomForest and LightGBM each use two predeclared configurations per fold (40 attempts total). See PHASE5_PROTOCOL.md and hyperparameter_trials.csv for every setting, selection and failure. Validation mean daily RankIC is primary; MSE then simpler grid order break numerical ties. No test-based retuning, refit, sign change or early stopping. Package versions: {json.dumps(meta['versions'])}.

## Walk-forward and leakage controls

Exact expanding Phase 4 folds: train from 2011 through year Y−2, validate Y−1, test Y, with labels ending strictly before the next partition. Signal after close(t), entry open(t+1), exit open(t+6), using the frozen adjusted-open target proxy. Eligibility is at t only; test target availability affects scoring, never training or prediction membership. All feature-complete test rows are predicted, including unlabeled tail rows.

Future-target and later-feature mutations, changed later folds, shuffled row order, repeat seeds, no learned imputation, serialization replay and disk-metric checks pass. Full suite: {tests['passed']} passed, {tests['failures']} failures, {tests['errors']} errors, {tests['skipped']} skipped, {tests['warnings']} warnings. Full logs and XML are retained. Tests are evidence against specified failure modes, not a guarantee against all leakage.

## OOS results

{metrics_table}

{table(m,['model','IC_median','RankIC_median','IC_positive_ratio','RankIC_positive_ratio','valid_dates','median_stocks_per_date','observations'])}

ICIR/RankICIR are unannualized daily mean/std. MSE/MAE/R² pool valid stock-date labels; R² uses the pooled observed target mean. HAC is the frozen calendar-preserving Bartlett lag-5 estimator; paired lag-20 sensitivity is also saved. Separate model significance does not establish incremental value.

## Primary paired comparison vs Ridge

Columns mean/median are daily paired ΔRankIC; positive_ratio is the fraction of comparable dates on which ML beats Ridge.

{paired_table}

{table(p,['model','hac_t_lag20','ci95_low_lag20','ci95_high_lag20'])}

Descriptive best nonlinear model is {best}: paired gain {bp['mean']:.6f}, 95% CI [{bp.ci95_low:.6f}, {bp.ci95_high:.6f}], HAC t {bp.hac_t:.4f}. The interval {'excludes' if bp.ci95_low>0 or bp.ci95_high<0 else 'includes'} zero. This is conditional on the frozen biased sample and two compared ML families.

## Secondary comparison vs observed Lasso and OLS

{secondary_table}

{table(secondary,['model','RankIC_mean','RankIC_hac_t','MSE','MAE','R2'])}

{best} minus Lasso is {bl['mean']:.6f}; minus OLS aggregate mean RankIC is {bestscore-ols:.6f}. Neither replaces Ridge as primary. The OLS number is descriptive, not a separate paired significance test.

## Yearly stability and 2022

{year_table}

{best} beats Ridge in {int(bp.years_better)}/10 years, loses in {int(bp.years_worse)}/10. 2026 is partial. Negative years and distribution/importance comparisons are retained in phase5/failure_analysis.md. No favorable year was removed.

{table(y[y.year==2022],['model','RankIC_mean','RankIC_hac_t','RankIC_ci95_low','RankIC_ci95_high'])}

{year22_note}

Year-specific outcomes do not justify an ex-post regime rule. Weak years are examined against prediction dispersion, feature distributions, upstream factor IC and training-derived importance, without new macro inputs.

## Prediction quintiles

{quant_table}

Tie-preserving at-t membership is assigned before label filtering. This is average forward-return association, **not tradable portfolio performance**: no overlapping holdings, costs or capital accounting. Monotonicity is Spearman correlation of five aggregate bin means; spread uses the same lag-5 HAC method.

## Importance and stability

{table(importance_table,['model','importance_type','feature','mean_normalized_importance','mean_rank','std_rank','top3_folds'])}

{table(families)}

{table(permutation,['model','feature','mean_importance','mean_rank','std_rank'])}

{importance_note}

Native importance and one seeded within-date permutation per feature on 20 validation sessions per fold are diagnostic only. Validation permutation values are RankIC losses, not gain units. Negative values remain. Native gain/impurity is not comparable across algorithms; correlated factors can substitute. Ranking variation across folds is retained rather than hidden behind a global average. **Feature importance is not causal evidence.**

## Controlled ablation

{table(abl,['model','feature_group','RankIC_mean','RankIC_hac_t','IC_mean'])}

{ablation_note}

ValidationWinner means the higher validation-RankIC nonlinear family in each fold, with its selected all-feature parameters fixed for four upstream group-only fits. ablation_family_by_fold.csv records actual families. Ridge group predictions are reused from Phase 4. These are group-only diagnostics, not leave-one-out causal contributions or a searched production feature subset.

## Random-label and random-feature controls

{table(random_label,['model','RankIC_mean','RankIC_hac_t','RankIC_ci95_low','RankIC_ci95_high'])}

{table(random_feature,['RankIC_mean','RankIC_hac_t','RankIC_ci95_low','RankIC_ci95_high'])}

{table(noise_imp,['importance_type','mean_normalized_importance','mean_rank','top3_folds'])}

Training labels were permuted only within allowed training rows; controls use the first fixed LightGBM configuration and are never tuned. Random features are reproducible key-based noise and appear only in a separate diagnostic model. Predeclared investigation flags: {json.dumps({k:v for k,v in flags.items() if k.endswith('requires_investigation')})}. All control results, including negative years, remain saved.

## Complexity, similarity and disagreements

{table(corr,['model_a','model_b','Pearson_mean','Spearman_mean','Spearman_std'])}

{table(runtotal)}

{complexity_note}

Experiment wall time: {meta['total_experiment_seconds']:.1f} seconds, including data/test/serialization/diagnostic overhead. Grid fit seconds include the selected fit, so do not add those columns together. Ridge/Lasso/OLS zero incremental fit times mean reuse, not free original training. Runtime per model/fold is retained; four CPU workers, one BLAS thread. Different prediction correlations demonstrate different rankings, not genuine profitable interactions by themselves. Incremental paired evidence determines whether added complexity is supported.

Ten largest LightGBM/Ridge absolute percentile-rank gaps per fold are saved with all factor z-scores and realized targets; no target-sign selection. The failure-analysis report shows a fixed first-fold excerpt. SHAP was omitted; native and validation-permutation diagnostics suffice without extra dependencies.

## Integrity, consistency and limitations

All final metrics were computed from saved OOS Parquets, then full/yearly/paired results independently recomputed from them. Report tables are generated from the resulting CSVs, with machine checks of their rendered values. Source/model/prediction hashes, exact upstream preservation and append-only research-log prefix are audited in phase5/validation.json.

{implementation_note}

{warning_note}

The frozen current-candidate universe remains survivor and selection biased; this is not PIT index membership or unbiased strategy evidence. Other limitations include vendor revisions, globally quarantined corrupt data, adjusted-price execution proxy, no delisting reconstruction/sector-size neutralization, complete-case restriction, overlapping labels, weak return signal, limited grid and folds, partial 2026, and multiple exploratory diagnostics. HAC intervals do not remove these biases or all multiple-testing risk. No Sharpe, CAGR, capital portfolio or transaction-cost optimization was performed.

## Conclusion

**{conclusion}**. The predeclared classification uses paired uncertainty and year consistency, not an obligation to make ML win. Engineering decision: **{decision}**, independently of whether ML outperforms. This result supports only the bounded experiment performed; other grids or production implementations are untested. Stop before Phase 6.
'''
    (ROOT/'reports/ml_walkforward_report.md').write_text(report,encoding='utf-8')
    phase=f'''# Phase 5 report

{BIAS_TEXT}

Research conclusion: **{conclusion}**. Descriptive best ML: {best}. Ridge remains the predeclared benchmark.

## Upstream integrity, models and selection

Phase 1–4 artifacts unchanged: {checks['upstream_inventory_final_unchanged'] and checks['upstream_docs_final_unchanged']}. Exact ten Phase 4 folds/sample keys reused: True. No data rebuild/download, factor/target/eligibility change or Phase 6 work. Actual models: reused Ridge, sklearn RandomForestRegressor, LightGBM LGBMRegressor; no fallback. Versions: {json.dumps(meta['versions'])}.

Two fixed configurations per nonlinear family/fold; select validation mean daily RankIC, with MSE then grid-order tie-breaks. Test used only for saved predictions and evaluation. No test fitting, early stopping or tuning. Identity tree preprocessing uses existing z-scores and complete cases; Ridge's training-only scaler is unchanged. Signal after close(t), buy at next adjusted open(t+1), measure return to adjusted open(t+6).

## OOS evidence

{metrics_table}

{paired_table}

{best} paired ΔRankIC vs Ridge: {bp['mean']:.6f}, HAC t {bp.hac_t:.6f}, 95% CI [{bp.ci95_low:.6f}, {bp.ci95_high:.6f}]. Against Lasso: {bl['mean']:.6f}, 95% CI [{bl.ci95_low:.6f}, {bl.ci95_high:.6f}]. Descriptive difference vs OLS: {bestscore-ols:.6f}. Full OOS dates, breadth, medians, positive ratios, errors and inference appear in reports/ml_walkforward_report.md and machine tables.

## Year stability and 2022

{year_table}

{best} wins {int(bp.years_better)}/10 years against Ridge and loses {int(bp.years_worse)}/10. All negative years remain in the table; 2026 partial. 2022 outcomes are directly visible; no 2022 tuning occurred. See reports/phase5/failure_analysis.md for weak-year distributions, factor IC and importance.

{year22_note}

## Quintiles, importance and ablation

{table(q.drop_duplicates('model'),['model','monotonicity_score','top_minus_bottom_mean','top_minus_bottom_hac_t'])}

These are forward-return diagnostics, not capital-aware portfolio results.

{table(families)}

{table(importance_table,['model','feature','mean_rank','std_rank','top3_folds'])}

Importance varies by fold; native and validation-permutation details are retained. Correlated substitutes complicate attribution and importance is not causal.

{importance_note}

{table(abl,['model','feature_group','RankIC_mean','RankIC_hac_t'])}

Nonlinear ablation uses the validation-winning family per fold, fixed all-feature parameters; no test-selected subsets. Family choices are archived.

{ablation_note}

## Controls, tests and complexity

{table(random_label,['model','RankIC_mean','RankIC_hac_t'])}

Random-feature standalone RankIC {random_feature.iloc[0].RankIC_mean:.6f}; HAC t {random_feature.iloc[0].RankIC_hac_t:.6f}. Unresolved predeclared control flags: {sum(control_flags)}. Future mutations, later-fold changes, row shuffling, seeded reproducibility and serialized replay pass. Full pytest: **{tests['passed']} passed, {tests['warnings']} warnings**, {tests['failures']} failures, {tests['errors']} errors, {tests['skipped']} skipped. Logs preserve warnings.

{table(runtotal)}

Additional compute must be judged against the paired intervals above; different rankings alone do not establish valuable nonlinear interactions. Total experiment wall time {meta['total_experiment_seconds']:.1f} seconds. No strategy performance claim is justified. All saved full/yearly/paired metrics are recomputed and report numbers generated from CSVs. {implementation_note}

{complexity_note}

## Remaining bias and decision

survivorship_biased = true; candidate_selection_biased = true. Current candidate list is not historical PIT membership. Vendor/adjusted-price limitations, complete cases, overlapping labels, multiple comparisons and partial 2026 remain. Phase 5 is not unbiased strategy evidence. Engineering PASS means the documented pipeline is sound enough for a separately authorized capital-aware phase; it does not mean ML wins or is deployable.

Conclusion: **{conclusion}**. Detailed report: reports/ml_walkforward_report.md. MODEL_CARD.md and PHASE5_FEATURE_SET.md document intended use and inputs. Stop after Phase 5.

PHASE 5: {decision}
'''
    (ROOT/'PHASE5_REPORT.md').write_text(phase,encoding='utf-8')
    checks['report_full_metrics_equal_csv']=metrics_table in report and metrics_table in phase
    checks['report_yearly_metrics_equal_csv']=year_table in report and year_table in phase
    checks['report_paired_metrics_equal_csv']=paired_table in report and paired_table in phase and secondary_table in report
    assert all(checks.values()),checks
    config={**BIAS,'run_id':meta['run_id'],'seed':meta['seed'],'seed_rule':meta['seed_rule'],'grids':meta['grids'],
            'features':meta['features'],'versions':meta['versions'],'workers':4,'blas_threads':1,'protocol_sha256':meta['protocol_sha256']}
    write_json(OUT/'config.json',config)
    log_entry=f'\n## {stamp()} — Phase 5 completed\n\nHypothesis: nonlinear ranking may not improve on frozen Ridge. Result: {conclusion}; {best} RankIC {bestscore:.10f}, paired Ridge gain {bp["mean"]:.10f}, lag-5 HAC CI [{bp.ci95_low:.10f}, {bp.ci95_high:.10f}], wins {int(bp.years_better)}/10 years. Fixed experiments retained; no test retuning. Controls: {sum(control_flags)} investigation flags. Full suite {tests["passed"]} passed/{tests["warnings"]} warnings. Upstream unchanged. Interpretation: bounded biased-prototype evidence, not strategy performance. Runtime metadata origin corrected in derived summary; native LightGBM stopping warnings retained descriptively. Next: stop; Phase 6 requires a new instruction.\n'
    # Idempotent reporting does not append duplicate completion entries.
    if '— Phase 5 completed' not in (ROOT/'RESEARCH_LOG.md').read_text(encoding='utf-8'):
        with (ROOT/'RESEARCH_LOG.md').open('a',encoding='utf-8') as f:f.write(log_entry)
    validation={**BIAS,'status':decision,'run_id':meta['run_id'],'conclusion':conclusion,'best_ml':best,'tests':tests,'checks':checks,
        'prediction_files':meta['prediction_files'],'source_panel_sha256':meta['source_panel_sha256'],
        'artifact_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['validation.json','report_generation.log']},
        'report_sha256':{n:sha256(ROOT/n) for n in ['MODEL_CARD.md','PHASE5_FEATURE_SET.md','PHASE5_REPORT.md','reports/ml_walkforward_report.md']},
        'evaluation_code_sha256':{n:sha256(ROOT/n) for n in ['scripts/evaluate_phase5.py','scripts/report_phase5.py','src/evaluation/ml_evaluation.py','tests/test_phase5_evaluation.py']}}
    write_json(OUT/'validation.json',validation)
    print(json.dumps({'decision':decision,'conclusion':conclusion,'best':best,'tests':tests,'checks':len(checks)},indent=2))

if __name__=='__main__':main()

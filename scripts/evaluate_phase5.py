"""Evaluate frozen saved predictions; never fit or select a model here."""
import sys,json,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from src.evaluation.ml_evaluation import metrics_from_saved,read_prediction,regression_metrics,paired_comparison
from src.evaluation.statistics import daily_ic,ic_summary
from src.evaluation.single_factor import quantile_analysis
from src.factors.definitions import BIAS
from src.models.linear_baselines import FEATURES,GROUPS
from src.data.incremental import write_json

OUT=ROOT/'reports/phase5'
PRIMARY=['Ridge','RandomForest','LightGBM']
def save(df,name):
    df.assign(**BIAS).to_csv(OUT/name,index=False)

def main():
    meta=json.loads((OUT/'experiment_manifest.json').read_text())
    assert meta['status']=='EXPERIMENTS_COMPLETE'
    sessions=pd.DatetimeIndex(sorted(pd.read_parquet(meta['source_panel_path'],columns=['date']).date.unique()))
    sessions=sessions[sessions.year>=2017]
    daily_parts={}; moments={}; yearly=[]; distributions=[]; quintiles={n:[] for n in PRIMARY}
    correlations=[]; disagreements=[]; noise=[]; keys_equal=True
    for year in range(2017,2027):
        current={}
        for e in [e for e in meta['prediction_files'] if e['fold']==year]:
            f,d,m,s=metrics_from_saved(e,sessions[sessions.year==year])
            key=(e['role'],e['model'],e['group'])
            daily_parts.setdefault(key,[]).append(d)
            moments.setdefault(key,[]).append(m)
            yearly.append(dict(role=e['role'],model=e['model'],feature_group=e['group'],family=e['family'],year=year,**s))
            if e['role'] in ['primary','secondary']:
                current[e['model']]=f
            if e['role']=='primary':
                x=f.prediction; cs=f.groupby('date').prediction.std()
                distributions.append(dict(model=e['model'],year=year,n_predictions=len(f),mean=x.mean(),std=x.std(),minimum=x.min(),maximum=x.max(),
                    p01=x.quantile(.01),p05=x.quantile(.05),median=x.median(),p95=x.quantile(.95),p99=x.quantile(.99),
                    median_daily_cs_std=cs.median(),min_daily_cs_std=cs.min(),near_constant_dates=int((cs<1e-10).sum()),extreme_abs_gt_50pct=int((x.abs()>.5).sum())))
                quintiles[e['model']].append(f[['date','ticker','prediction','target','target_available','eligible_at_t']])
            if e['model']=='RandomFeatureControl':
                noise.append(daily_ic(f,'random_feature',sessions=sessions[sessions.year==year]))
        reference=current['Ridge']
        for f in current.values():
            pd.testing.assert_frame_equal(reference[['date','ticker','target','target_available']],f[['date','ticker','target','target_available']])
        for a,b in itertools.combinations(PRIMARY,2):
            pair=reference[['date','ticker']].assign(a=current[a].prediction,b=current[b].prediction)
            c=daily_ic(pair,'a',target='b',sessions=sessions[sessions.year==year])
            correlations.append(c.rename(columns={'IC':'Pearson','RankIC':'Spearman'}).assign(model_a=a,model_b=b,year=year))
        gap=reference[['date','ticker','target']].assign(Ridge=current['Ridge'].prediction,LightGBM=current['LightGBM'].prediction)
        gap['Ridge_percentile']=gap.groupby('date').Ridge.rank(pct=True,method='average')
        gap['LightGBM_percentile']=gap.groupby('date').LightGBM.rank(pct=True,method='average')
        gap['absolute_rank_gap']=(gap.LightGBM_percentile-gap.Ridge_percentile).abs()
        disagreements.append(gap.sort_values(['absolute_rank_gap','date','ticker'],ascending=[False,True,True]).head(10).assign(fold=year))
        print(f'Evaluated saved predictions {year}',flush=True)
    summaries=[]; daily_all=[]
    for key,parts in daily_parts.items():
        role,model,group=key
        d=pd.concat(parts).sort_values('date').reset_index(drop=True)
        daily_parts[key]=d
        summed={k:sum(m[k] for m in moments[key]) for k in moments[key][0]}
        summaries.append(dict(role=role,model=model,feature_group=group,**regression_metrics(summed),**ic_summary(d)))
        daily_all.append(d.assign(role=role,model=model,feature_group=group))
    full=pd.DataFrame(summaries); annual=pd.DataFrame(yearly); daily=pd.concat(daily_all,ignore_index=True)
    save(full,'all_saved_prediction_metrics.csv');save(annual,'all_saved_prediction_yearly_metrics.csv')
    save(full[full.role=='primary'],'model_oos_metrics.csv');save(annual[annual.role=='primary'],'model_yearly_metrics.csv')
    save(daily[daily.role.isin(['primary','secondary'])],'model_daily_ic.csv')
    save(full[full.role=='secondary'],'secondary_linear_metrics.csv')
    save(annual[annual.role=='secondary'],'secondary_linear_yearly_metrics.csv')
    paired=[]; pair_daily=[]
    for benchmark in ['Ridge','Lasso']:
        for model in ['RandomForest','LightGBM']:
            a=daily_parts[('primary',model,'All')]
            b=daily_parts[('primary' if benchmark=='Ridge' else 'secondary',benchmark,'All')]
            p,s=paired_comparison(a,b,model,benchmark);paired.append(s);pair_daily.append(p)
    paired=pd.DataFrame(paired);pdaily=pd.concat(pair_daily,ignore_index=True)
    save(paired[paired.benchmark=='Ridge'],'model_vs_ridge.csv');save(paired[paired.benchmark=='Lasso'],'model_vs_lasso.csv')
    save(pdaily,'paired_daily_rankic.csv')
    py=pdaily.assign(year=pdaily.date.dt.year).groupby(['model','benchmark','year']).delta_RankIC.agg(['mean','median','count']).reset_index()
    save(py,'paired_yearly_rankic.csv')
    qsummary=[];qdaily=[];qyear=[]
    for model,parts in quintiles.items():
        f=pd.concat(parts,ignore_index=True)
        f=f.assign(factor_available_prediction=True,FWD_RET_5D=f.target,entry_price_valid=f.target_available,
            exit_price_valid_5D=f.target_available,target_available_5D=f.target_available)
        d,s,y=quantile_analysis(f,'prediction',sessions)
        qsummary.append(s.assign(model=model));qdaily.append(d.assign(model=model));qyear.append(y.assign(model=model))
    save(pd.concat(qsummary),'prediction_quantile_diagnostics.csv');save(pd.concat(qdaily),'prediction_quantile_daily.csv');save(pd.concat(qyear),'prediction_quantile_yearly.csv')
    save(pd.DataFrame(distributions),'prediction_distributions.csv')
    corr=pd.concat(correlations,ignore_index=True);save(corr,'prediction_correlation_daily.csv')
    save(corr.groupby(['model_a','model_b'])[['Pearson','Spearman']].agg(['mean','median','std']).set_axis(['Pearson_mean','Pearson_median','Pearson_std','Spearman_mean','Spearman_median','Spearman_std'],axis=1).reset_index(),'prediction_correlation.csv')
    examples=pd.concat(disagreements,ignore_index=True)
    features=pd.read_parquet(meta['source_panel_path'],columns=['date','ticker',*[n+'_zscore' for n in FEATURES]])
    examples=examples.merge(features,on=['date','ticker'],validate='one_to_one')
    save(examples,'model_disagreement_examples.csv')
    imp=pd.read_csv(OUT/'feature_importance_by_fold.csv')
    imp['top3']=imp['rank']<=3
    impsum=imp.groupby(['model','importance_type','feature']).agg(mean_importance=('importance','mean'),mean_normalized_importance=('normalized_importance','mean'),mean_rank=('rank','mean'),std_rank=('rank','std'),top3_folds=('top3','sum'),folds=('fold','nunique')).reset_index()
    save(impsum,'feature_importance_summary.csv')
    family={n:g for g,names in GROUPS.items() if g!='All' for n in names}
    imp['family']=imp.feature.map(family).fillna('Random_Control')
    fam=imp.groupby(['model','importance_type','fold','family']).normalized_importance.sum().reset_index()
    save(fam,'feature_family_importance.csv')
    ablation=full[(full.role=='ablation')|((full.model=='Ridge')&(full.feature_group=='All'))]
    save(ablation,'ml_ablation.csv');save(annual[(annual.role=='ablation')|((annual.model=='Ridge')&(annual.feature_group=='All'))],'ml_ablation_yearly.csv')
    winners=[json.loads((ROOT/meta['directory']/f'fold_{y}'/'complete.json').read_text()) for y in range(2017,2027)]
    save(pd.DataFrame([{'fold':w['fold'],'validation_winner':w['validation_winner']} for w in winners]),'ablation_family_by_fold.csv')
    save(full[full.model=='RandomLabelControl'],'random_label_control.csv');save(annual[annual.model=='RandomLabelControl'],'random_label_control_yearly.csv')
    save(full[full.model=='RandomFeatureControl'],'random_feature_model_control.csv')
    noise=pd.concat(noise).sort_values('date');save(noise,'random_feature_daily_ic.csv')
    ns=ic_summary(noise);save(pd.DataFrame([ns]),'random_feature_control.csv')
    label=full[full.model=='RandomLabelControl'].iloc[0]
    ni=impsum[(impsum.model=='RandomFeatureControl')&(impsum.feature=='RANDOM_CONTROL')&(impsum.importance_type=='gain')].iloc[0]
    flags={'random_label_requires_investigation':bool(abs(label.RankIC_mean)>.005 and abs(label.RankIC_hac_t)>=2.58),
        'random_feature_importance_requires_investigation':bool(ni.mean_normalized_importance>.15 or ni.top3_folds>=5),
        'random_feature_rankic_requires_investigation':bool(abs(ns['RankIC_mean'])>.005 and abs(ns['RankIC_hac_t'])>=2.58)}
    write_json(OUT/'control_flags.json',{**BIAS,**flags})
    runtime=pd.read_csv(OUT/'runtime_details.csv')
    runtime['reuse_origin']=np.where(runtime.model.isin(['Ridge','Lasso','OLS']),'Phase4',np.where((runtime.model=='ValidationWinner')&(runtime.group=='All'),'Phase5 primary','fit'))
    # Raw runner's boolean meant no new fit; this authoritative origin corrects its overly broad field name.
    runtime['reused_from_phase4']=runtime.reuse_origin.eq('Phase4')
    trials=pd.read_csv(OUT/'hyperparameter_trials.csv')
    cost=trials.groupby(['fold','model']).agg(grid_fit_seconds=('train_seconds','sum'),grid_validation_predict_seconds=('validation_prediction_seconds','sum')).reset_index()
    runtime=runtime.merge(cost,on=['fold','model'],how='left').fillna({'grid_fit_seconds':0,'grid_validation_predict_seconds':0})
    save(runtime,'runtime_summary.csv')
    # Independent second pass over ALL primary/secondary Parquets verifies published metrics.
    checks={'identical_test_keys_and_labels':keys_equal}; repeated={}; yearcsv=pd.read_csv(OUT/'all_saved_prediction_yearly_metrics.csv')
    for e in meta['prediction_files']:
        if e['role'] not in ['primary','secondary']:continue
        f,d,m,s=metrics_from_saved(e,sessions[sessions.year==e['fold']])
        row=yearcsv[(yearcsv.model==e['model'])&(yearcsv.year==e['fold'])&(yearcsv.feature_group=='All')].iloc[0]
        for k in ['MSE','MAE','R2','IC_mean','RankIC_mean','RankIC_hac_t']:
            np.testing.assert_allclose(s[k],row[k],rtol=1e-10,atol=1e-12)
        repeated.setdefault(e['model'],[]).append((d,m))
    for model,parts in repeated.items():
        d=pd.concat([x[0] for x in parts]).sort_values('date');m={k:sum(x[1][k] for x in parts) for k in parts[0][1]}
        s={**regression_metrics(m),**ic_summary(d)};row=full[(full.model==model)&(full.feature_group=='All')].iloc[0]
        for k in ['MSE','MAE','R2','IC_mean','RankIC_mean','RankIC_hac_t']:np.testing.assert_allclose(s[k],row[k],rtol=1e-10,atol=1e-12)
        repeated[model]=d
    for _,row in paired.iterrows():
        _,s=paired_comparison(repeated[row.model],repeated[row.benchmark],row.model,row.benchmark)
        for k in ['mean','median','positive_ratio','hac_t','ci95_low','ci95_high']:np.testing.assert_allclose(s[k],row[k],rtol=1e-10,atol=1e-12)
    checks.update(saved_full_metrics_recomputed=True,saved_yearly_metrics_recomputed=True,saved_paired_metrics_recomputed=True)
    write_json(OUT/'evaluation_validation.json',dict(status='PASS',checks=checks,**BIAS))
    print(full[full.role.isin(['primary','secondary','control'])][['model','RankIC_mean','RankIC_hac_t']].to_string(index=False))
    print(paired[['model','benchmark','mean','hac_t','ci95_low','ci95_high','years_better']].to_string(index=False))
    print(flags,flush=True)

if __name__=='__main__':main()

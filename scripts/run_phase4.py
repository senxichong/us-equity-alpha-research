"""Run the preregistered Phase 4 analyses on frozen Phase 3 data, offline."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.data.download import sha256
from src.data.incremental import stamp,write_json
from src.data.panel import write_panel_parquet
from src.factors.dataset import load_factor_panel
from src.factors.definitions import BIAS,NAMES
from src.evaluation.statistics import ic_summary,mean_inference,bh_adjust,daily_ic
from src.evaluation.single_factor import factor_ic,quantile_analysis,factor_correlations,label_mask
from src.models.linear_baselines import FEATURES,GROUPS,GRIDS,Fold,split_fold,fit_candidates,tag_predictions

OUT=ROOT/'reports/phase4'


def save_csv(frame,name):
    frame.assign(**BIAS).to_csv(OUT/name,index=False)


def log(text):
    with (ROOT/'RESEARCH_LOG.md').open('a',encoding='utf-8') as f:
        f.write(f'\n## {stamp()}\n\n{text}\n')
    print(text,flush=True)


def inventory():
    records=[]
    for directory in ['data/raw','data/processed/phase2','data/processed/phase2_5','data/processed/phase3','reports/phase2','reports/phase2_5','reports/phase3']:
        for p in sorted((ROOT/directory).rglob('*')):
            if p.is_file():
                s=p.stat()
                records.append((p.relative_to(ROOT).as_posix(),s.st_size,s.st_mtime_ns))
    return hashlib.sha256(json.dumps(records).encode()).hexdigest()


def test_suite():
    p=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml=reports/phase4/pytest.xml'],cwd=ROOT,capture_output=True,text=True)
    text=p.stdout+p.stderr
    (OUT/'pytest.log').write_text(text,encoding='utf-8')
    print(text,flush=True)
    suites=ET.parse(OUT/'pytest.xml').getroot().findall('testsuite')
    counts={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    counts['passed']=counts['tests']-counts['failures']-counts['errors']-counts['skipped']
    warning_counts=re.findall(r'(\d+) warnings?',text)
    counts['warnings']=int(warning_counts[-1]) if warning_counts else 0
    counts['returncode']=p.returncode
    if p.returncode or counts['skipped']:
        raise RuntimeError(f'Full suite failed: {counts}')
    return counts


def single_factors(panel,sessions):
    log('Stage A BEGIN. Hypothesis/method: unchanged PHASE4_PROTOCOL.md raw-sign 5D IC and forward-return quantiles. Result/interpretation pending. Next: retain all 17 factors.')
    daily_list,summaries,yearly,rolling,quantiles,quantile_daily,quantile_yearly,extremes=[],[],[],[],[],[],[],[]
    for n in NAMES:
        print(f'Single factor {n}',flush=True)
        daily,stats=factor_ic(panel,n,sessions)
        daily_list.append(daily)
        summaries.append(stats)
        for year,g in daily.groupby(daily.date.dt.year):
            yearly.append({'factor':n,'year':year,**ic_summary(g,5)})
        roll=daily[['date','factor','IC','RankIC']].copy()
        for window,minimum in [(126,100),(252,200)]:
            for c in ['IC','RankIC']:
                roll[f'{c}_rolling_{window}']=roll[c].rolling(window,min_periods=minimum).mean()
        rolling.append(roll)
        for c in ['IC','RankIC']:
            good=daily.loc[daily[c].notna()]
            for direction,part in [('lowest',good.nsmallest(3,c)),('highest',good.nlargest(3,c))]:
                for _,r in part.iterrows():
                    extremes.append({'factor':n,'metric':c,'direction':direction,'date':r.date,'value':r[c],'n_stocks':r.n_stocks})
        qd,qs,qy=quantile_analysis(panel,n,sessions)
        quantile_daily.append(qd)
        quantiles.append(qs)
        quantile_yearly.append(qy)
    daily=pd.concat(daily_list,ignore_index=True)
    summary=pd.DataFrame(summaries)
    summary['IC_hac_BH_q']=bh_adjust(summary.IC_hac_p)
    summary['RankIC_hac_BH_q']=bh_adjust(summary.RankIC_hac_p)
    save_csv(daily[['date','factor','horizon','n_stocks','IC']],'single_factor_ic.csv')
    save_csv(daily[['date','factor','horizon','n_stocks','RankIC']],'single_factor_rankic.csv')
    save_csv(summary,'factor_statistics.csv')
    save_csv(pd.DataFrame(yearly),'yearly_factor_statistics.csv')
    save_csv(pd.concat(rolling,ignore_index=True),'rolling_factor_statistics.csv')
    save_csv(pd.concat(quantiles,ignore_index=True),'quantile_diagnostics.csv')
    save_csv(pd.concat(quantile_daily,ignore_index=True),'quantile_daily.csv')
    save_csv(pd.concat(quantile_yearly,ignore_index=True),'quantile_yearly.csv')
    save_csv(pd.DataFrame(extremes),'ic_extreme_dates.csv')
    log('Stage A COMPLETE. Result: all 17 factors retained in dated IC/RankIC, HAC/FDR, yearly/rolling and raw-sign Q1–Q5 tables. Interpretation deferred to the report after the fixed pipeline completes. Next: target-free redundancy and all secondary horizons; no specification changes.')
    log('Stage B BEGIN. Hypothesis: redundant families and horizon dependence. Method: target-free pairwise cross-sectional Spearman and all 1D/10D/20D diagnostics. Results pending; do not change the primary 5D target.')
    corr,counts=factor_correlations(panel)
    save_csv(corr.rename_axis('factor').reset_index(),'factor_correlation.csv')
    save_csv(counts.rename_axis('factor').reset_index(),'factor_correlation_date_counts.csv')
    pairs=[]
    for i,a in enumerate(NAMES):
        for b in NAMES[i+1:]:
            pairs.append({'factor_a':a,'factor_b':b,'mean_daily_spearman':corr.loc[a,b],'valid_dates':counts.loc[a,b],'strong_redundancy':abs(corr.loc[a,b])>=.8})
    save_csv(pd.DataFrame(pairs),'factor_correlation_pairs.csv')
    robust=[]
    for h in [1,10,20]:
        print(f'Secondary IC horizon {h}D (no models)',flush=True)
        for n in NAMES:
            _,s=factor_ic(panel,n,sessions,h=h)
            robust.append(s)
    save_csv(pd.concat([summary.assign(role='primary'),pd.DataFrame(robust).assign(role='secondary')],ignore_index=True),'horizon_robustness.csv')
    log('Stage B COMPLETE. Result: complete correlation/date-count and all-horizon tables saved, including negative associations. Interpretation remains descriptive and does not change feature membership, signs, grids or primary horizon. Next: preregistered linear folds.')
    return summary


def error_moments(predictions):
    valid=predictions.target_available & np.isfinite(predictions.prediction) & np.isfinite(predictions.target)
    x=predictions.loc[valid]
    error=x.prediction-x.target
    return {'observations':len(x),'sse':float(error.pow(2).sum()),'sae':float(error.abs().sum()),
            'sum_y':float(x.target.sum()),'sum_y2':float(x.target.pow(2).sum()),'stocks':int(x.ticker.nunique()),
            'first_scored_date':x.date.min(),'last_scored_date':x.date.max()}


def regression_metrics(m):
    n=m['observations']
    sst=m['sum_y2']-m['sum_y']**2/n if n else np.nan
    return {'observations':n,'MSE':m['sse']/n if n else np.nan,'MAE':m['sae']/n if n else np.nan,'R2':1-m['sse']/sst if sst>0 else np.nan}


def models(panel,sessions,directory,base_metadata):
    log('Stage C/D BEGIN. Hypothesis: simple linear combinations may have unstable OOS rankings. Method: fixed expanding folds 2017–2026, label purging, train-only scaling/orientation/calibration, all five baselines and four predefined Ridge groups. Results pending. Next: retain every configuration and test prediction; no performance-dependent reruns.')
    daily_parts,yearly,configs,coefficients,folds,moments,matched=[],[],[],[],[],[],[]
    prediction_files=[]
    stocks_seen={}
    specifications=[(n,'All') for n in ['EqualWeight','OLS','Ridge','Lasso','ElasticNet']]+[('Ridge',g) for g in GROUPS if g!='All']
    for year in range(2017,2027):
        print(f'Walk-forward test year {year}',flush=True)
        fold=Fold(year)
        train,valid,test,audit=split_fold(panel,fold)
        folds.append(audit)
        assert train.return_end_timestamp_5D.max()<pd.Timestamp(audit['validation_start'],tz='UTC')
        assert valid.return_end_timestamp_5D.max()<pd.Timestamp(audit['test_start'],tz='UTC')
        test_sessions=sessions[sessions.year==year]
        fold_predictions=[]
        # Matching factor comparisons use exactly the common model test sample.
        scored=test.loc[label_mask(test,5)]
        for factor in NAMES:
            fd=daily_ic(scored[['date','ticker',factor,'FWD_RET_5D']],factor,'FWD_RET_5D',sessions=test_sessions)
            fd['factor'],fd['fold']=factor,year
            matched.append(fd)
        for model,group in specifications:
            fitted,grid=fit_candidates(train,valid,model,GROUPS[group])
            grid['feature_group'],grid['fold']=group,year
            configs.append(grid)
            co=fitted.coefficient_table().assign(model=model,feature_group=group,fold=year,selected_parameter=fitted.parameter)
            coefficients.append(co)
            prediction=fitted.predict(test)
            assert np.isfinite(prediction).all()
            pred=tag_predictions(test,prediction,model,group,fold)
            fold_predictions.append(pred)
            daily=daily_ic(pred,'prediction',sessions=test_sessions)
            daily['model'],daily['feature_group'],daily['fold']=model,group,year
            daily_parts.append(daily)
            m=error_moments(pred)
            moments.append({**m,'model':model,'feature_group':group,'fold':year})
            stocks_seen.setdefault((model,group),set()).update(pred.loc[pred.target_available,'ticker'])
            yearly.append({'model':model,'feature_group':group,'year':year,'selected_parameter':fitted.parameter,
                           **regression_metrics(m),**ic_summary(daily,5),'stocks':m['stocks'],
                           'first_scored_date':m['first_scored_date'],'last_scored_date':m['last_scored_date']})
        fold_frame=pd.concat(fold_predictions,ignore_index=True).assign(**BIAS)
        assert fold_frame.sample_role.eq('test').all()
        assert not fold_frame.duplicated(['date','ticker','model','feature_group']).any()
        path=directory/f'oos_predictions_{year}.parquet'
        write_panel_parquet(fold_frame,path,{**base_metadata,'purpose':'test_predictions','fold':audit})
        prediction_files.append({'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'rows':len(fold_frame)})
        # Checkpoint all tried configurations, never just winning parameters.
        save_csv(pd.concat(configs,ignore_index=True),'model_configurations.csv')
        save_csv(pd.DataFrame(folds),'walk_forward_folds.csv')
        print(f'Fold {year} complete: {len(train):,} train, {len(valid):,} validation, {len(test):,} feature-only test rows',flush=True)
    all_daily=pd.concat(daily_parts,ignore_index=True)
    save_csv(all_daily,'model_daily_ic.csv')
    year_frame=pd.DataFrame(yearly)
    save_csv(year_frame,'model_yearly_metrics.csv')
    coefficient_frame=pd.concat(coefficients,ignore_index=True)
    save_csv(coefficient_frame,'model_coefficients.csv')
    moment_frame=pd.DataFrame(moments)
    save_csv(moment_frame,'model_error_moments.csv')
    full=[]
    for (model,group),daily in all_daily.groupby(['model','feature_group']):
        d=daily.sort_values('date')
        m=moment_frame.loc[(moment_frame.model==model)&(moment_frame.feature_group==group)]
        total=m[['observations','sse','sae','sum_y','sum_y2']].sum().to_dict()
        full.append({'model':model,'feature_group':group,**regression_metrics(total),**ic_summary(d,5),
                     'stocks':len(stocks_seen[(model,group)]),'first_scored_date':m.first_scored_date.min(),'last_scored_date':m.last_scored_date.max()})
    full=pd.DataFrame(full)
    save_csv(full.loc[full.feature_group=='All'],'model_oos_metrics.csv')
    save_csv(full.loc[full.model=='Ridge'],'ablation_results.csv')
    matched=pd.concat(matched,ignore_index=True)
    save_csv(matched,'matched_oos_factor_daily_ic.csv')
    matched_summary=[]
    for factor,g in matched.groupby('factor'):
        matched_summary.append({'factor':factor,**ic_summary(g.sort_values('date'),5)})
    save_csv(pd.DataFrame(matched_summary),'matched_oos_factor_metrics.csv')
    stability=[]
    for (model,group,factor),g in coefficient_frame.groupby(['model','feature_group','factor']):
        c=g.sort_values('fold').coefficient_phase3_zscore
        signs=np.sign(c.where(c.abs()>1e-8,0))
        stability.append({'model':model,'feature_group':group,'factor':factor,'mean_coefficient':c.mean(),
                          'std_coefficient':c.std(ddof=1),'min_coefficient':c.min(),'max_coefficient':c.max(),
                          'positive_folds':int((signs>0).sum()),'negative_folds':int((signs<0).sum()),
                          'near_zero_folds':int((signs==0).sum()),'sign_changes_nonzero':int(((signs*signs.shift(1))<0).sum())})
    save_csv(pd.DataFrame(stability),'coefficient_stability.csv')
    log('Stage C/D COMPLETE. Result: 10 annual folds, all five primary models, four Ridge ablations, all validation configurations, training-only coefficients/scalers/signs and test-only predictions saved. Interpretation will compare matched OOS periods, yearly instability and coefficient behavior without changing the predeclared baseline. Next: figures, source-preservation audit and final reports; no Phase 5.')
    return prediction_files


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'analysis_manifest.json').exists():
        raise RuntimeError('Existing Phase 4 analysis manifest: preserve it; do not silently rerun predictive research')
    before=inventory()
    protocol_hash=sha256(ROOT/'PHASE4_PROTOCOL.md')
    tests=test_suite()
    print('Loading frozen Phase 3 matrix (no rebuild)...',flush=True)
    panel,source=load_factor_panel()
    assert source['status']=='PASS'
    sessions=pd.DatetimeIndex(sorted(panel.date.unique()))
    run_id=stamp()
    directory=ROOT/'data/processed/phase4'/run_id
    directory.mkdir(parents=True,exist_ok=False)
    code_paths=[Path(__file__),*sorted((ROOT/'src/evaluation').glob('*.py')),*sorted((ROOT/'src/models').glob('*.py')),ROOT/'tests/test_phase4.py',ROOT/'requirements-phase4-lock.txt']
    metadata={**BIAS,'phase':4,'run_id':run_id,'status':'RUNNING','source_dataset_id':source['dataset_id'],
              'source_panel_path':source['panel_path'],'source_panel_sha256':source['panel_sha256'],
              'source_rows':len(panel),'source_stocks':int(panel.ticker.nunique()),'source_sessions':len(sessions),
              'protocol_sha256_before_results':protocol_hash,'upstream_inventory_before':before,
              'primary_horizon':5,'minimum_cross_section':50,'primary_hac_lag':5,'sensitivity_hac_lag':20,
              'features':FEATURES,'groups':GROUPS,'grids':GRIDS,'tests':tests,'model_directory':str(directory.relative_to(ROOT)),
              'code_sha256':{p.relative_to(ROOT).as_posix():sha256(p) for p in code_paths}}
    write_json(OUT/'analysis_manifest.json',metadata)
    write_json(OUT/'predeclared_config.json',metadata)
    # Free unused source columns while keeping raw factors, z-scores, all masks and timestamps.
    needed=['date','ticker','eligible_at_t','entry_price_valid','return_end_timestamp_5D',*NAMES,
            *[f'{n}_zscore' for n in FEATURES],*[f'factor_available_{n}' for n in NAMES],
            *[f'{prefix}_{h}D' for h in [1,5,10,20] for prefix in ['FWD_RET','exit_price_valid','target_available']]]
    panel=panel[needed].sort_values(['date','ticker']).reset_index(drop=True)
    singles=single_factors(panel,sessions)
    metadata['prediction_files']=models(panel,sessions,directory,metadata)
    checks={'all_17_factors_retained':len(singles)==17,'all_10_folds':len(metadata['prediction_files'])==10,
            'source_panel_unchanged':sha256(source['panel_path'])==source['panel_sha256'],
            'upstream_inventory_unchanged':inventory()==before,'preregistration_unchanged':sha256(ROOT/'PHASE4_PROTOCOL.md')==protocol_hash,
            'all_tests_passed':tests['returncode']==0,'bias_flags_present':all(metadata[k] for k in ['survivorship_biased','candidate_selection_biased'])}
    grids=pd.read_csv(OUT/'model_configurations.csv')
    checks['no_solver_convergence_warnings']=not grids.fit_warnings.fillna('').str.contains('ConvergenceWarning').any()
    metadata.update(status='RESEARCH_COMPLETE' if all(checks.values()) else 'FAIL',checks={k:bool(v) for k,v in checks.items()},
                    upstream_inventory_after=inventory())
    write_json(OUT/'analysis_manifest.json',metadata)
    write_json(directory/'analysis_metadata.json',metadata)
    print(json.dumps({'status':metadata['status'],'checks':checks,'tests':tests},default=bool,indent=2),flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    original_warning=warnings.showwarning
    def record_warning(message,category,filename,lineno,file=None,line=None):
        with (OUT/'runtime_warnings.log').open('a',encoding='utf-8') as f:
            f.write(warnings.formatwarning(message,category,filename,lineno,line))
        original_warning(message,category,filename,lineno,file,line)
    warnings.showwarning=record_warning
    with threadpool_limits(limits=1):
        try:
            main()
        except Exception as exc:
            log(f'Phase 4 run failed: {type(exc).__name__}: {exc}. Evidence retained; do not modify research choices to improve performance.')
            raise

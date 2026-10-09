"""Fixed Phase 5 experiments. Save test predictions before any final evaluation."""
from __future__ import annotations
import hashlib
import importlib.metadata
import json
import random
import subprocess
import sys
import time
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.data.download import sha256
from src.data.incremental import stamp,write_json
from src.data.panel import write_panel_parquet
from src.factors.dataset import load_factor_panel
from src.factors.definitions import BIAS,FACTOR_VERSION
from src.models.linear_baselines import FEATURES,GROUPS,Fold,split_fold,tag_predictions
from src.models.ml_walkforward import GRIDS,BASE_SEED,verified_folds,select_model,fit_fixed,predict,random_feature,importance_records

OUT=ROOT/'reports/phase5'
DOCS=['PHASE1_REPORT.md','PHASE2_REPORT.md','PHASE2_5_REPORT.md','PHASE3_REPORT.md','PHASE4_REPORT.md',
      'DATA_CONVENTIONS.md','RESEARCH_PROTOCOL.md','POINT_IN_TIME_ELIGIBILITY.md','FACTOR_DEFINITIONS.md',
      'TIMING_CONVENTION.md','TIMING_AUDIT.md','DATA_LIMITATIONS.md','PHASE4_PROTOCOL.md','config.yaml',
      'reports/single_factor_report.md','reports/baseline_report.md','requirements-lock.txt','requirements-phase4-lock.txt']


def save_csv(frame,name):
    frame.assign(**BIAS).to_csv(OUT/name,index=False)


def log(text):
    with (ROOT/'RESEARCH_LOG.md').open('a',encoding='utf-8') as f: f.write(f'\n## {stamp()} — Phase 5\n\n{text}\n')
    print(text,flush=True)


def upstream_inventory():
    records=[]
    for directory in ['data/raw','data/processed/phase2','data/processed/phase2_5','data/processed/phase3','data/processed/phase4',
                      'reports/phase2','reports/phase2_5','reports/phase3','reports/phase4']:
        for p in sorted((ROOT/directory).rglob('*')):
            if p.is_file():
                s=p.stat()
                records.append((p.relative_to(ROOT).as_posix(),s.st_size,s.st_mtime_ns))
    return hashlib.sha256(json.dumps(records).encode()).hexdigest()


def phase4_facts():
    m=pd.read_csv(ROOT/'reports/phase4/model_oos_metrics.csv').set_index('model')
    expected={'EqualWeight':.0193,'OLS':.0222,'Ridge':.0201,'Lasso':.0224,'ElasticNet':.0200}
    if not all(abs(m.loc[n,'RankIC_mean']-v)<.0001 for n,v in expected.items()):
        raise ValueError('Material Phase 4 benchmark discrepancy; stop')
    y=pd.read_csv(ROOT/'reports/phase4/model_yearly_metrics.csv')
    if not (y[(y.year==2022)&(y.feature_group=='All')].RankIC_mean<0).all():
        raise ValueError('Phase 4 2022 result mismatch')
    v=json.loads((ROOT/'reports/phase4/validation.json').read_text())
    if v['status']!='PASS' or not all(v['checks'].values()): raise ValueError('Phase 4 not PASS')
    # Inspect every saved table and verify its archived digest, without changing it.
    for relative,digest in v['artifact_sha256'].items():
        if sha256(ROOT/relative)!=digest: raise ValueError(f'Phase 4 artifact changed: {relative}')
    return v,{n:float(m.loc[n,'RankIC_mean']) for n in expected}


def full_tests():
    p=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml=reports/phase5/pytest.xml'],cwd=ROOT,capture_output=True,text=True)
    output=p.stdout+p.stderr
    (OUT/'pytest.log').write_text(output,encoding='utf-8')
    print(output,flush=True)
    suites=ET.parse(OUT/'pytest.xml').getroot().findall('testsuite')
    d={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    d['passed']=d['tests']-d['failures']-d['errors']-d['skipped']
    import re
    w=re.findall(r'(\d+) warnings?',output)
    d['warnings']=int(w[-1]) if w else 0
    if p.returncode or d['skipped']: raise RuntimeError(f'Full tests failed: {d}')
    return d


def sample_hash(frame,labels=True):
    cols=['date','ticker',*[f'{n}_zscore' for n in FEATURES]]
    if labels: cols+=['FWD_RET_5D','return_end_timestamp_5D']
    values=pd.util.hash_pandas_object(frame[cols].sort_values(['date','ticker']),index=False).to_numpy()
    return hashlib.sha256(values.tobytes()).hexdigest()


def enriched_prediction(test,values,name,family,group,fold,params,metadata):
    out=tag_predictions(test,values,name,group,fold)
    version=metadata['versions']['scikit-learn' if family in ['Ridge','RandomForest','Lasso','OLS'] else 'lightgbm']
    return out.assign(model_name=name,model_family=family,model_version=version,fold_id=fold.year,
        selected_hyperparameters=json.dumps(params,sort_keys=True),eligible_at_t=test.eligible_at_t.to_numpy(),
        feature_version=FACTOR_VERSION,source_phase3_dataset_id=metadata['source_phase3_dataset_id'],**BIAS)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'experiment_manifest.json').exists(): raise RuntimeError('Existing Phase 5 experiment manifest; preserve experiments and investigate before resuming')
    started=time.perf_counter()
    before=upstream_inventory()
    upstream,verified=phase4_facts()
    folds=verified_folds()
    save_csv(folds,'fold_manifest.csv')
    tests=full_tests()
    panel,source=load_factor_panel()
    needed=['date','ticker','eligible_at_t','entry_price_valid','exit_price_valid_5D','target_available_5D',
            'FWD_RET_5D','return_end_timestamp_5D',*[f'{n}_zscore' for n in FEATURES]]
    panel=panel[needed].sort_values(['date','ticker']).reset_index(drop=True)
    run_id=stamp()
    directory=ROOT/'experiments/phase5'/run_id
    directory.mkdir(parents=True,exist_ok=False)
    paths=[Path(__file__),ROOT/'src/models/ml_walkforward.py',ROOT/'tests/test_phase5.py',ROOT/'requirements-phase5-lock.txt',ROOT/'PHASE5_FEATURE_SET.md']
    logbytes=(ROOT/'RESEARCH_LOG.md').read_bytes()
    metadata={**BIAS,'phase':5,'status':'RUNNING','run_id':run_id,'directory':str(directory.relative_to(ROOT)),
              'source_phase3_dataset_id':source['dataset_id'],'source_panel_path':source['panel_path'],'source_panel_sha256':source['panel_sha256'],
              'source_phase4_run_id':upstream['run_id'],'verified_phase4_RankIC':verified,
              'upstream_inventory_before':before,'upstream_docs_sha256':{p:sha256(ROOT/p) for p in DOCS},
              'research_log_prefix_bytes':len(logbytes),'research_log_prefix_sha256':hashlib.sha256(logbytes).hexdigest(),
              'protocol_sha256':sha256(ROOT/'PHASE5_PROTOCOL.md'),'code_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in paths},
              'features':FEATURES,'grids':GRIDS,'seed':BASE_SEED,'seed_rule':'42 + test year','tests':tests,
              'versions':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','lightgbm','scipy','pyarrow','joblib']},
              'prediction_files':[],'model_artifacts':[]}
    write_json(OUT/'experiment_manifest.json',metadata)
    write_json(directory/'predeclared_metadata.json',metadata)
    trials,importance,runtimes,fold_audit,feature_distributions=[],[],[],[],[]
    snapshot_map={int(json.loads(Path(e['path']).name.split('_')[-1].split('.')[0])):e for e in upstream['prediction_files']}
    ridge_configs=pd.read_csv(ROOT/'reports/phase4/model_configurations.csv')
    log('PRIMARY/CONTROLS BEGIN. Hypothesis: nonlinear value may be weak or absent. Fixed two-candidate RF/LightGBM grids, exact Phase 4 samples/folds, reused Ridge, training-only fit and validation-only selection. Controls and validation-winner group diagnostics are predeclared. Results pending; no test-based retuning.')
    for _,foldrow in folds.iterrows():
        year=int(foldrow.fold_id)
        fold=Fold(year)
        seed=BASE_SEED+year
        random.seed(seed); np.random.seed(seed)
        train,validation,test,audit=split_fold(panel,fold)
        for key in ['train_rows','validation_rows','test_feature_rows','train_purged_rows','validation_purged_rows']:
            if int(audit[key])!=int(foldrow[key]): raise ValueError(f'Phase 4 sample mismatch {year} {key}')
        audit.update(train_hash=sample_hash(train),validation_hash=sample_hash(validation),test_features_hash=sample_hash(test,False))
        fold_audit.append(audit)
        save_csv(pd.DataFrame(fold_audit),'sample_audit.csv')
        fold_dir=directory/f'fold_{year}'
        fold_dir.mkdir()
        print(f'Phase 5 fold {year}: {len(train):,} train / {len(validation):,} validation / {len(test):,} test features',flush=True)
        e=snapshot_map[year]
        if sha256(e['path'])!=e['sha256']: raise ValueError('Frozen Phase 4 prediction checksum mismatch')
        prior=pd.read_parquet(e['path'])
        reference=prior[(prior.model=='Ridge')&(prior.feature_group=='All')].sort_values(['date','ticker']).reset_index(drop=True)
        pd.testing.assert_frame_equal(reference[['date','ticker']],test[['date','ticker']])
        expected=tag_predictions(test,reference.prediction.to_numpy(),'Ridge','All',fold)
        pd.testing.assert_series_equal(reference.target,expected.target,check_names=False)
        for n in FEATURES:
            x=test[f'{n}_zscore']
            feature_distributions.append({'fold':year,'feature':n,'mean':x.mean(),'std':x.std(),'p01':x.quantile(.01),'median':x.median(),
                'p99':x.quantile(.99),'median_daily_cs_std':test.groupby('date')[f'{n}_zscore'].std().median()})

        def save_prediction(frame,name,family,group,role,params,model=None,transform=None,train_seconds=0.,prediction_seconds=0.):
            leaf=fold_dir/f'{role}_{name}_{group}'
            leaf.mkdir(parents=True,exist_ok=False)
            artifact={**BIAS,'model_name':name,'model_family':family,'role':role,'group':group,'fold_id':year,
                      **fold.boundaries(),'seed':seed,'parameters':params,'features':list(transform.features) if transform else GROUPS.get(group,FEATURES),
                      'preprocessing':'complete-case identity for trees; frozen Phase 4 scaler for reused linear models',
                      'versions':metadata['versions'],'source_phase3_dataset_id':source['dataset_id'],
                      'source_phase4_run_id':upstream['run_id'],'protocol_sha256':metadata['protocol_sha256'],
                      'train_sample_sha256':audit['train_hash'],'validation_sample_sha256':audit['validation_hash']}
            path=leaf/'oos_predictions.parquet'
            write_panel_parquet(frame,path,artifact)
            entry={'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'rows':len(frame),'model':name,'family':family,'group':group,'role':role,'fold':year}
            metadata['prediction_files'].append(entry)
            if model is not None:
                model_path=leaf/'model.joblib'
                joblib.dump((model,transform),model_path,compress=3)
                artifact['model_path']=str(model_path.relative_to(ROOT)); artifact['model_sha256']=sha256(model_path)
                # Verify reload prediction on a fixed prefix, no performance-based selection.
                reloaded,rt=joblib.load(model_path)
                replay=test.iloc[:min(200,len(test))].copy()
                if 'RANDOM_CONTROL' in rt.features: replay['RANDOM_CONTROL_zscore']=random_feature(replay)
                np.testing.assert_allclose(predict(reloaded,rt,replay),frame.prediction.iloc[:len(replay)],rtol=1e-12,atol=1e-12)
            write_json(leaf/'metadata.json',artifact)
            metadata['model_artifacts'].append({'path':str((leaf/'metadata.json').relative_to(ROOT)),'sha256':sha256(leaf/'metadata.json')})
            runtimes.append({'fold':year,'model':name,'family':family,'group':group,'role':role,
                             'selected_fit_seconds':train_seconds,'test_prediction_seconds':prediction_seconds,'reused_from_phase4':model is None})

        # Reuse all frozen Ridge groups and strong linear alternatives, without fitting.
        for name,group in [('Ridge','All'),('Lasso','All'),('OLS','All')]+[('Ridge',g) for g in GROUPS if g!='All']:
            g=prior[(prior.model==name)&(prior.feature_group==group)].sort_values(['date','ticker']).reset_index(drop=True)
            pd.testing.assert_frame_equal(g[['date','ticker']],test[['date','ticker']])
            c=ridge_configs[(ridge_configs.fold==year)&(ridge_configs.model==name)&(ridge_configs.feature_group==group)&ridge_configs.selected].iloc[0]
            params={'phase4_parameter':float(c.parameter),'reused':True}
            frame=enriched_prediction(test,g.prediction.to_numpy(),name,name,group,fold,params,metadata)
            role='primary' if name=='Ridge' and group=='All' else ('secondary' if name in ['Lasso','OLS'] else 'ablation')
            save_prediction(frame,name,name,group,role,params)
        selected={}
        for family in ['RandomForest','LightGBM']:
            def trial_callback(record):
                with (fold_dir/f'{family}_trial_events.jsonl').open('a',encoding='utf-8') as f:
                    f.write(json.dumps({**record,'fold':year},default=str,allow_nan=True)+'\n')
                print(f'{year} {family} trial {record["trial"]}: {record["status"]}, validation RankIC {record["validation_metric"]}',flush=True)
            model,transform,params,grid=select_model(train,validation,family,seed,on_trial=trial_callback)
            grid['fold']=year
            trials.append(grid)
            save_csv(pd.concat(trials,ignore_index=True),'hyperparameter_trials.csv')
            chosen=grid[grid.selected].iloc[0]
            start=time.perf_counter(); values=predict(model,transform,test); elapsed=time.perf_counter()-start
            frame=enriched_prediction(test,values,family,family,'All',fold,params,metadata)
            save_prediction(frame,family,family,'All','primary',params,model,transform,float(chosen.train_seconds),elapsed)
            imp=importance_records(model,transform,validation,family,seed).assign(model=family,fold=year)
            importance.append(imp)
            selected[family]=(float(chosen.validation_metric),model,transform,params,frame)
        # No test metric is computed here. Family choice is validation-only per fold.
        winner=max(['RandomForest','LightGBM'],key=lambda n:(selected[n][0],n=='RandomForest'))
        _,_,_,chosen_params,winner_frame=selected[winner]
        for group,features in GROUPS.items():
            if group=='All':
                frame=winner_frame.copy().assign(model='ValidationWinner',model_name='ValidationWinner')
                save_prediction(frame,'ValidationWinner',winner,group,'ablation',chosen_params)
                continue
            model,transform,seconds=fit_fixed(train,winner,chosen_params,features,seed)
            start=time.perf_counter(); values=predict(model,transform,test); elapsed=time.perf_counter()-start
            frame=enriched_prediction(test,values,'ValidationWinner',winner,group,fold,chosen_params,metadata)
            save_prediction(frame,'ValidationWinner',winner,group,'ablation',chosen_params,model,transform,seconds,elapsed)
        # Untuned adversarial controls, same fixed first LightGBM grid in every fold.
        params=GRIDS['LightGBM'][0]
        model,transform,seconds=fit_fixed(train,'LightGBM',params,FEATURES,seed,permuted_labels=True)
        start=time.perf_counter(); values=predict(model,transform,test); elapsed=time.perf_counter()-start
        frame=enriched_prediction(test,values,'RandomLabelControl','LightGBM','All',fold,params,metadata)
        save_prediction(frame,'RandomLabelControl','LightGBM','All','control',params,model,transform,seconds,elapsed)
        tr=train.assign(RANDOM_CONTROL_zscore=random_feature(train))
        te=test.assign(RANDOM_CONTROL_zscore=random_feature(test))
        model,transform,seconds=fit_fixed(tr,'LightGBM',params,[*FEATURES,'RANDOM_CONTROL'],seed)
        start=time.perf_counter(); values=predict(model,transform,te); elapsed=time.perf_counter()-start
        frame=enriched_prediction(te,values,'RandomFeatureControl','LightGBM','All',fold,params,metadata)
        frame['random_feature']=te.RANDOM_CONTROL_zscore.to_numpy()
        save_prediction(frame,'RandomFeatureControl','LightGBM','All','control',params,model,transform,seconds,elapsed)
        noise_imp=importance_records(model,transform,validation,'LightGBM',seed,validation_dates=0).assign(model='RandomFeatureControl',fold=year)
        importance.append(noise_imp)
        save_csv(pd.concat(importance,ignore_index=True),'feature_importance_by_fold.csv')
        save_csv(pd.DataFrame(runtimes),'runtime_details.csv')
        save_csv(pd.DataFrame(feature_distributions),'feature_distributions.csv')
        write_json(OUT/'experiment_manifest.json',metadata)
        write_json(fold_dir/'complete.json',{'fold':year,'validation_winner':winner,'sample_audit':audit,'complete':True,**BIAS})
        print(f'Fold {year} saved; nonlinear ablation validation winner: {winner}. No OOS tuning.',flush=True)
    checks={'phase4_values_verified':True,'fold_boundaries_identical':True,'fold_sample_counts_identical':True,
            'upstream_inventory_unchanged':upstream_inventory()==before,'source_panel_unchanged':sha256(source['panel_path'])==source['panel_sha256'],
            'upstream_documents_unchanged':all(sha256(ROOT/p)==h for p,h in metadata['upstream_docs_sha256'].items()),
            'preregistration_unchanged':sha256(ROOT/'PHASE5_PROTOCOL.md')==metadata['protocol_sha256'],
            'research_log_prefix_unchanged':hashlib.sha256((ROOT/'RESEARCH_LOG.md').read_bytes()[:metadata['research_log_prefix_bytes']]).hexdigest()==metadata['research_log_prefix_sha256'],
            'full_tests_passed':tests['failures']==0 and tests['errors']==0,
            'forty_primary_trials_recorded':len(pd.concat(trials))==40}
    metadata.update(status='EXPERIMENTS_COMPLETE' if all(checks.values()) else 'FAIL',checks=checks,
                    total_experiment_seconds=time.perf_counter()-started,upstream_inventory_after=upstream_inventory())
    write_json(OUT/'experiment_manifest.json',metadata)
    write_json(directory/'completed_metadata.json',metadata)
    log('EXPERIMENTS COMPLETE. Result: ten frozen folds, selected RF/LightGBM and reused linear predictions, fixed controls and validation-winner ablations saved. Interpretation pending disk-based evaluation and paired HAC audit. Next: evaluate artifacts and report; no retuning or new factors.')
    assert all(checks.values()),checks


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    original_warning=warnings.showwarning
    def record_warning(message,category,filename,lineno,file=None,line=None):
        with (OUT/'runtime_warnings.log').open('a',encoding='utf-8') as f: f.write(warnings.formatwarning(message,category,filename,lineno,line))
        original_warning(message,category,filename,lineno,file,line)
    warnings.showwarning=record_warning
    with threadpool_limits(limits=1): main()

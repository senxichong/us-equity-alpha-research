import hashlib
import joblib
import numpy as np
import pandas as pd
import pytest

from src.models.linear_baselines import FEATURES,Fold,split_fold
from src.models.ml_walkforward import verified_folds,CompleteCaseInputs,random_feature,select_model,fit_fixed,predict
from src.evaluation.statistics import daily_ic,ic_summary


@pytest.fixture
def ml_panel():
    rng=np.random.default_rng(17)
    dates=pd.bdate_range('2014-01-01','2018-12-31')[::10]
    frame=pd.DataFrame({'date':np.repeat(dates,20),'ticker':np.tile([f'T{i:02}' for i in range(20)],len(dates))})
    x=rng.normal(size=(len(frame),len(FEATURES)))
    for j,n in enumerate(FEATURES): frame[f'{n}_zscore']=x[:,j]
    frame['FWD_RET_5D']=.03*x[:,0]+.01*x[:,1]**2+rng.normal(0,.002,len(frame))
    for c in ['eligible_at_t','entry_price_valid','exit_price_valid_5D','target_available_5D']: frame[c]=True
    frame['return_end_timestamp_5D']=(frame.date+pd.offsets.BusinessDay(6)).dt.tz_localize('UTC')
    return frame


def grid(family):
    if family=='RandomForest':
        return [dict(n_estimators=12,max_depth=d,min_samples_leaf=4,max_features=1.,bootstrap=True,max_samples=.8) for d in [2,3]]
    return [dict(n_estimators=12,max_depth=d,num_leaves=2**d-1,min_child_samples=8,learning_rate=.15) for d in [2,3]]


def signature(model,family):
    if family=='LightGBM': return hashlib.sha256(model.booster_.model_to_string().encode()).hexdigest()
    return hashlib.sha256(b''.join(t.tree_.threshold.tobytes()+t.tree_.value.tobytes() for t in model.estimators_)).hexdigest()


def test_phase5_folds_are_identical_to_frozen_phase4(tmp_path):
    actual=verified_folds()
    original=pd.read_csv('reports/phase4/walk_forward_folds.csv').rename(columns={'fold':'fold_id'})
    pd.testing.assert_frame_equal(actual,original)
    changed=original.rename(columns={'fold_id':'fold'}).copy()
    changed.loc[0,'test_start']='2017-02-01'
    path=tmp_path/'bad.csv'
    changed.to_csv(path,index=False)
    with pytest.raises(ValueError,match='boundary'): verified_folds(path)


def test_complete_case_has_no_fitted_imputation_or_future_statistics(ml_panel):
    train,_,test,_=split_fold(ml_panel,Fold(2017))
    transform=CompleteCaseInputs(FEATURES).fit(train)
    state=vars(transform).copy()
    changed=test.copy()
    changed[[f'{n}_zscore' for n in FEATURES]]*=1e12
    transform.transform(changed)
    assert vars(transform)==state=={'features':tuple(FEATURES)}
    changed.loc[0,f'{FEATURES[0]}_zscore']=np.nan
    with pytest.raises(ValueError,match='no imputation'): transform.transform(changed)
    np.testing.assert_array_equal(transform.transform(train),train[[f'{n}_zscore' for n in FEATURES]])


@pytest.mark.parametrize('family',['RandomForest','LightGBM'])
def test_targets_future_features_and_row_order_cannot_change_earlier_model(ml_panel,family):
    train,valid,test,_=split_fold(ml_panel,Fold(2017))
    model,transform,params,trials=select_model(train,valid,family,2059,grid=grid(family),minimum=5,workers=1)
    before=predict(model,transform,test)
    changed=ml_panel.copy()
    changed.loc[changed.date.dt.year>=2017,'FWD_RET_5D']=1e20
    changed.loc[changed.date.dt.year>=2018,[f'{n}_zscore' for n in FEATURES]]=-1e20
    changed=changed.sample(frac=1,random_state=88)
    tr,va,te,_=split_fold(changed,Fold(2017))
    other,trans2,params2,trials2=select_model(tr,va,family,2059,grid=grid(family),minimum=5,workers=1)
    assert params==params2 and signature(model,family)==signature(other,family)
    np.testing.assert_allclose(before,predict(other,trans2,te),atol=1e-12,rtol=1e-12)
    pd.testing.assert_frame_equal(trials.drop(columns=['train_seconds','validation_prediction_seconds']),trials2.drop(columns=['train_seconds','validation_prediction_seconds']))


@pytest.mark.parametrize('family',['RandomForest','LightGBM'])
def test_repeated_seed_serialization_and_saved_fold_predictions(ml_panel,family,tmp_path):
    train,_,test,_=split_fold(ml_panel,Fold(2017))
    a,ta,_=fit_fixed(train,family,grid(family)[0],FEATURES,41,workers=1)
    b,tb,_=fit_fixed(train,family,grid(family)[0],FEATURES,41,workers=1)
    np.testing.assert_allclose(predict(a,ta,test),predict(b,tb,test),rtol=1e-12,atol=1e-12)
    model_path=tmp_path/'model.joblib'
    joblib.dump((a,ta),model_path)
    saved,transform=joblib.load(model_path)
    prediction=test[['date','ticker','FWD_RET_5D']].rename(columns={'FWD_RET_5D':'target'}).assign(prediction=predict(saved,transform,test),sample_role='test',fold_id=2017)
    path=tmp_path/'oos.parquet'
    prediction.to_parquet(path,index=False)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    in_memory=ic_summary(daily_ic(prediction,'prediction',minimum=5))
    loaded=pd.read_parquet(path)
    from_disk=ic_summary(daily_ic(loaded,'prediction',minimum=5))
    assert in_memory==from_disk
    # A later fold fit has no access to the earlier saved file.
    tr,_,_,_=split_fold(ml_panel,Fold(2018))
    fit_fixed(tr,family,grid(family)[0],FEATURES,2060,workers=1)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest


def test_random_feature_is_keyed_and_future_row_order_invariant(ml_panel):
    base=ml_panel.iloc[:100].copy()
    values=random_feature(base)
    whole=random_feature(ml_panel)
    np.testing.assert_array_equal(values,whole[:100])
    shuffled=base.sample(frac=1,random_state=3)
    assigned=pd.Series(random_feature(shuffled),index=shuffled.index).sort_index()
    np.testing.assert_array_equal(values,assigned.to_numpy())
    assert np.all(np.abs(values)<=np.sqrt(3))


def test_random_label_control_destroys_known_toy_signal(ml_panel):
    train,_,test,_=split_fold(ml_panel,Fold(2017))
    params=grid('LightGBM')[1]
    real,t,_=fit_fixed(train,'LightGBM',params,FEATURES,42,workers=1)
    noise,u,_=fit_fixed(train,'LightGBM',params,FEATURES,42,workers=1,permuted_labels=True)
    sample=test[['date','ticker','FWD_RET_5D']].copy()
    sample['prediction']=predict(real,t,test)
    original=daily_ic(sample,'prediction','FWD_RET_5D',minimum=5).RankIC.mean()
    sample['prediction']=predict(noise,u,test)
    control=daily_ic(sample,'prediction','FWD_RET_5D',minimum=5).RankIC.mean()
    assert original>.7 and abs(control)<.25

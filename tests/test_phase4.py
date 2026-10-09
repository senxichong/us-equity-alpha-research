import numpy as np
import pandas as pd
import pytest
from scipy.stats import spearmanr
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_hac

from src.evaluation.statistics import daily_ic, mean_inference, bh_adjust
from src.evaluation.single_factor import assign_quantiles, quantile_analysis
from src.models.linear_baselines import FEATURES, Fold, split_fold, fit_candidates, tag_predictions


def cross_section():
    return pd.DataFrame({'date':pd.to_datetime(['2020-01-02']*5+['2020-01-03']*5),
                         'ticker':list('ABCDE')*2,'factor':[1.,2,2,4,5]*2,
                         'target':[1.,2,3,4,5,5,4,3,2,1]})


def test_ic_is_by_date_not_pooled_and_rank_ties_are_average():
    data = cross_section()
    result = daily_ic(data,'factor',minimum=5)
    assert result.iloc[0].IC == pytest.approx(np.corrcoef(data.factor[:5],data.target[:5])[0,1])
    assert result.iloc[0].RankIC == pytest.approx(spearmanr(data.factor[:5],data.target[:5]).statistic)
    assert result.iloc[0].RankIC == pytest.approx(-result.iloc[1].RankIC)
    assert abs(data.factor.corr(data.target))<1e-14


def test_minimum_sample_and_constant_predictions_do_not_make_fake_ic():
    data = cross_section()
    assert daily_ic(data,'factor',minimum=6).IC.isna().all()
    assert daily_ic(data.assign(factor=1.),'factor',minimum=5).IC.isna().all()
    data.loc[0,'target'] = np.nan
    out = daily_ic(data,'factor',minimum=5)
    assert out.iloc[0].n_stocks==4 and np.isnan(out.iloc[0].IC)
    assert np.isfinite(out.iloc[1].IC)


def test_ic_order_invariance_and_duplicate_rejection():
    data = cross_section()
    pd.testing.assert_frame_equal(daily_ic(data,'factor',minimum=5),daily_ic(data.sample(frac=1,random_state=8),'factor',minimum=5))
    with pytest.raises(ValueError,match='Duplicate'):
        daily_ic(pd.concat([data,data.iloc[:1]]),'factor')


def test_quantiles_hand_assignment_ties_and_order():
    frame = pd.DataFrame({'date':pd.Timestamp('2020-01-02'),'ticker':[f'T{i:03}' for i in range(100)],'x':np.arange(100.)})
    result = assign_quantiles(frame,'x')
    np.testing.assert_array_equal(result['quantile'],np.repeat(np.arange(1,6),20))
    pd.testing.assert_frame_equal(result,assign_quantiles(frame.sample(frac=1,random_state=4),'x').reset_index(drop=True))
    tied = frame.assign(x=np.repeat(np.arange(10.),10))
    assert assign_quantiles(tied,'x').join(tied.x).groupby('x')['quantile'].nunique().max()==1
    assert assign_quantiles(frame.assign(x=1.),'x')['quantile'].isna().all()
    assert assign_quantiles(frame.iloc[:49],'x')['quantile'].isna().all()


def test_future_labels_cannot_change_quantile_assignment():
    frame = pd.DataFrame({'date':pd.Timestamp('2020-01-02'),'ticker':[str(i) for i in range(100)],'x':np.arange(100.),'target':np.arange(100.)})
    before = assign_quantiles(frame,'x')
    frame['target'] = np.nan
    frame['target_available_5D'] = False
    pd.testing.assert_frame_equal(before,assign_quantiles(frame,'x'))


def test_quantile_spread_preserves_negative_raw_sign():
    date = pd.Timestamp('2020-01-02')
    frame = pd.DataFrame({'date':date,'ticker':[f'T{i:03}' for i in range(100)],'RET_5':np.arange(100.),
                          'FWD_RET_5D':-np.arange(100.)/100,'eligible_at_t':True,'factor_available_RET_5':True,
                          'entry_price_valid':True,'exit_price_valid_5D':True,'target_available_5D':True})
    daily,summary,_ = quantile_analysis(frame,'RET_5',pd.DatetimeIndex([date]))
    assert len(daily)==5
    assert summary.iloc[0].mean_forward_return==pytest.approx(-.095)
    assert summary.iloc[0].top_minus_bottom_mean==pytest.approx(-.8)
    assert summary.iloc[0].monotonicity_score==pytest.approx(-1)


def test_hac_matches_statsmodels_mean_intercept():
    rng = np.random.default_rng(123)
    values = rng.normal(.03,.2,300)
    values[1:] += .5*values[:-1]
    result = sm.OLS(values,np.ones((len(values),1))).fit()
    expected = np.sqrt(cov_hac(result,nlags=5,use_correction=True)[0,0])
    actual = mean_inference(values,5)
    assert actual['hac_se']==pytest.approx(expected,rel=1e-12)
    assert actual['hac_t']==pytest.approx(values.mean()/expected,rel=1e-12)


def test_hac_does_not_compress_missing_calendar_sessions():
    assert mean_inference([1,np.nan,3],1)['hac_se']==pytest.approx(1.)
    assert mean_inference([1,3],1)['hac_se']==pytest.approx(np.sqrt(.5))
    assert np.isnan(mean_inference([1],5)['hac_t'])
    assert np.isnan(mean_inference([0,0,0],5)['hac_t'])
    with pytest.raises(ValueError):
        mean_inference([1,2],-1)


def test_hac_serial_correlation_widens_uncertainty():
    rng=np.random.default_rng(3)
    x=rng.normal(size=1000)
    for i in range(1,len(x)):
        x[i]+=.8*x[i-1]
    result=mean_inference(x,5)
    assert result['hac_se']>x.std(ddof=1)/np.sqrt(len(x))


def test_bh_known_example_with_missing_value():
    np.testing.assert_allclose(bh_adjust([.01,.04,.03,np.nan]),[.03,.04,.04,np.nan],equal_nan=True)


@pytest.fixture
def model_panel():
    rng=np.random.default_rng(42)
    dates=pd.bdate_range('2014-01-01','2018-12-31')[::5]
    data=pd.DataFrame({'date':np.repeat(dates,12),'ticker':np.tile([f'T{i:02}' for i in range(12)],len(dates))})
    x=rng.normal(size=(len(data),len(FEATURES)))
    for j,name in enumerate(FEATURES):
        data[f'{name}_zscore']=x[:,j]
    data['FWD_RET_5D']=.01*x[:,0]-.02*x[:,1]+rng.normal(0,.005,len(data))
    for name in ['eligible_at_t','entry_price_valid','exit_price_valid_5D','target_available_5D']:
        data[name]=True
    data['return_end_timestamp_5D']=(data.date+pd.offsets.BusinessDay(6)).dt.tz_localize('UTC')+pd.Timedelta(hours=14)
    return data


def test_walk_forward_boundaries_and_label_purging(model_panel):
    tr,va,te,audit=split_fold(model_panel,Fold(2017))
    assert tr.date.max()<va.date.min()<te.date.min()
    assert (tr.return_end_timestamp_5D<pd.Timestamp('2016-01-01',tz='UTC')).all()
    assert (va.return_end_timestamp_5D<pd.Timestamp('2017-01-01',tz='UTC')).all()
    assert audit['train_purged_rows']>0 and audit['validation_purged_rows']>0
    assert te.date.dt.year.eq(2017).all()


@pytest.mark.parametrize('model',['EqualWeight','OLS','Ridge','Lasso','ElasticNet'])
def test_test_targets_cannot_affect_model_fitting_or_predictions(model_panel,model):
    tr,va,te,_=split_fold(model_panel,Fold(2017))
    first,configs=fit_candidates(tr,va,model,minimum=5)
    changed=model_panel.copy()
    changed.loc[changed.date.dt.year==2017,'FWD_RET_5D']=1e10
    tr2,va2,te2,_=split_fold(changed,Fold(2017))
    second,configs2=fit_candidates(tr2,va2,model,minimum=5)
    np.testing.assert_array_equal(first.coefficients,second.coefficients)
    np.testing.assert_array_equal(first.predict(te),second.predict(te2))
    pd.testing.assert_frame_equal(configs,configs2)


def test_scaler_is_training_only_and_future_fold_cannot_change_earlier_predictions(model_panel):
    tr,va,te,_=split_fold(model_panel,Fold(2017))
    fitted,_=fit_candidates(tr,va,'Ridge',minimum=5)
    np.testing.assert_allclose(fitted.mean,tr[[f'{n}_zscore' for n in FEATURES]].mean())
    changed=model_panel.copy()
    future=changed.date.dt.year==2018
    changed.loc[future,[f'{n}_zscore' for n in FEATURES]]=1e15
    changed.loc[future,'FWD_RET_5D']=-1e15
    tr2,va2,te2,_=split_fold(changed,Fold(2017))
    fit2,_=fit_candidates(tr2,va2,'Ridge',minimum=5)
    np.testing.assert_array_equal(fitted.predict(te),fit2.predict(te2))
    # Validation extremes may select a penalty, but cannot change scaler statistics.
    va3=va.copy()
    va3[[f'{n}_zscore' for n in FEATURES]]+=1e10
    fit3,_=fit_candidates(tr,va3,'OLS',minimum=5)
    np.testing.assert_array_equal(fitted.mean,fit3.mean)


def test_model_panel_order_invariance_and_oos_tags(model_panel):
    fold=Fold(2017)
    tr,va,te,_=split_fold(model_panel,fold)
    tr2,va2,te2,_=split_fold(model_panel.sample(frac=1,random_state=77),fold)
    fit,configs=fit_candidates(tr,va,'Ridge',minimum=5)
    fit2,configs2=fit_candidates(tr2,va2,'Ridge',minimum=5)
    pd.testing.assert_frame_equal(configs,configs2)
    out=tag_predictions(te,fit.predict(te),'Ridge','All',fold)
    out2=tag_predictions(te2,fit2.predict(te2),'Ridge','All',fold)
    pd.testing.assert_frame_equal(out,out2)
    assert out.sample_role.eq('test').all() and out.date.dt.year.eq(2017).all()
    assert out.train_end.eq('2015-12-31').all()
    with pytest.raises(ValueError,match='outside'):
        tag_predictions(tr,fit.predict(tr),'Ridge','All',fold)


def test_unavailable_test_target_does_not_remove_feature_prediction(model_panel):
    data=model_panel.copy()
    mask=data.date.dt.year==2017
    data.loc[mask,'target_available_5D']=False
    tr,va,te,_=split_fold(data,Fold(2017))
    fit,_=fit_candidates(tr,va,'OLS',minimum=5)
    out=tag_predictions(te,fit.predict(te),'OLS','All',Fold(2017))
    assert len(out)>0 and out.prediction.notna().all() and out.target.isna().all()

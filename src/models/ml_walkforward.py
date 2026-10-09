"""Phase 5 bounded nonlinear experiments; fit/selection never receive test data."""
import hashlib
import json
import random
import time

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.evaluation.statistics import daily_ic
from src.models.linear_baselines import FEATURES,Fold

BASE_SEED=42
RF_GRID=[dict(n_estimators=64,max_depth=d,min_samples_leaf=100,max_features=.75,bootstrap=True,max_samples=.10) for d in [4,6]]
LGBM_GRID=[dict(n_estimators=150,learning_rate=.05,num_leaves=n,max_depth=d,min_child_samples=200,max_bin=63,
               subsample=.8,subsample_freq=1,colsample_bytree=.8,reg_lambda=1.) for n,d in [(7,3),(15,4)]]
GRIDS={'RandomForest':RF_GRID,'LightGBM':LGBM_GRID}


def verified_folds(path='reports/phase4/walk_forward_folds.csv'):
    source=pd.read_csv(path)
    if source.fold.tolist()!=list(range(2017,2027)):
        raise ValueError('Phase 4 fold IDs changed')
    for _,row in source.iterrows():
        for k,v in Fold(int(row.fold)).boundaries().items():
            if row[k]!=v:
                raise ValueError(f'Phase 4 fold boundary mismatch: {row.fold} {k}')
    return source.rename(columns={'fold':'fold_id'})


def random_feature(frame,seed=BASE_SEED):
    # Keyed noise: appending rows, changing their order or future distributions
    # cannot affect any existing key. This is not a production alpha feature.
    return np.array([(int.from_bytes(hashlib.sha256(f'{seed}|{pd.Timestamp(d).date()}|{t}'.encode()).digest()[:8],'big')/2**64*2-1)*np.sqrt(3)
                     for d,t in frame[['date','ticker']].itertuples(index=False,name=None)])


class CompleteCaseInputs:
    """Stateless identity transform: no scaling, clipping or imputation fitting."""
    def __init__(self,features):
        self.features=tuple(features)

    def fit(self,frame):
        self.transform(frame)
        return self

    def transform(self,frame):
        x=frame[[f'{f}_zscore' for f in self.features]].to_numpy(float)
        if not np.isfinite(x).all():
            raise ValueError('Complete-case policy: nonfinite feature; no imputation')
        return x


def make_model(family,params,seed,workers=4):
    random.seed(seed)
    np.random.seed(seed)
    if family=='RandomForest':
        return RandomForestRegressor(**params,random_state=seed,n_jobs=workers)
    if family=='LightGBM':
        return lgb.LGBMRegressor(**params,objective='regression',random_state=seed,n_jobs=workers,
                deterministic=True,force_col_wise=True,bagging_seed=seed,feature_fraction_seed=seed,
                data_random_seed=seed,verbosity=0)
    raise ValueError(f'Unknown family: {family}')


def fit_fixed(train,family,params,features,seed,workers=4,permuted_labels=False):
    train=train.sort_values(['date','ticker']).reset_index(drop=True)
    transform=CompleteCaseInputs(features).fit(train)
    x=transform.transform(train)
    y=train.FWD_RET_5D.to_numpy(float).copy()
    if not np.isfinite(y).all(): raise ValueError('Training labels must be finite')
    if permuted_labels:
        y=np.random.default_rng(seed+10000).permutation(y)
    estimator=make_model(family,params,seed,workers)
    start=time.perf_counter()
    estimator.fit(pd.DataFrame(x,columns=list(features)),y)
    return estimator,transform,time.perf_counter()-start


def predict(estimator,transform,frame):
    return estimator.predict(pd.DataFrame(transform.transform(frame),columns=list(transform.features)))


def select_model(train,validation,family,seed,features=FEATURES,grid=None,minimum=50,workers=4,on_trial=None):
    """Two predeclared candidates; no test data or evaluation callback accepted."""
    validation=validation.sort_values(['date','ticker']).reset_index(drop=True)
    candidates,records=[],[]
    for trial,params in enumerate(grid if grid is not None else GRIDS[family]):
        record={'model':family,'trial':trial,'parameters':json.dumps(params,sort_keys=True),'seed':seed,'selected':False}
        try:
            estimator,transform,seconds=fit_fixed(train,family,params,features,seed,workers)
            start=time.perf_counter()
            prediction=predict(estimator,transform,validation)
            prediction_seconds=time.perf_counter()-start
            values=validation[['date','ticker','FWD_RET_5D']].assign(prediction=prediction)
            scores=daily_ic(values,'prediction','FWD_RET_5D',minimum)
            record.update(status='success',error='',validation_metric=scores.RankIC.mean(),validation_IC=scores.IC.mean(),
                          validation_MSE=float(np.mean((prediction-validation.FWD_RET_5D)**2)),train_seconds=seconds,
                          validation_prediction_seconds=prediction_seconds,validation_dates=int(scores.RankIC.notna().sum()))
            candidates.append((estimator,transform,params))
        except Exception as exc:
            record.update(status='failed',error=f'{type(exc).__name__}: {exc}',validation_metric=np.nan,
                          validation_IC=np.nan,validation_MSE=np.nan,train_seconds=np.nan,validation_prediction_seconds=np.nan,validation_dates=0)
            candidates.append(None)
        records.append(record)
        if on_trial is not None: on_trial(dict(record))
    usable=[i for i,r in enumerate(records) if r['status']=='success' and np.isfinite(r['validation_metric'])]
    if not usable: raise RuntimeError(f'No usable validation trial for {family}: {records}')
    best_score=max(records[i]['validation_metric'] for i in usable)
    tied=[i for i in usable if abs(records[i]['validation_metric']-best_score)<=1e-12]
    best=min(tied,key=lambda i:(records[i]['validation_MSE'],i))
    records[best]['selected']=True
    return *candidates[best],pd.DataFrame(records)


def importance_records(estimator,transform,validation,family,seed,minimum=50,validation_dates=20):
    rows=[]
    if family=='RandomForest':
        native={'impurity':estimator.feature_importances_}
    else:
        native={'gain':estimator.booster_.feature_importance(importance_type='gain'),
                'split':estimator.booster_.feature_importance(importance_type='split')}
    for kind,values in native.items():
        total=float(np.sum(values))
        ranks=pd.Series(values).rank(ascending=False,method='min')
        for name,value,rank in zip(transform.features,values,ranks):
            rows.append({'feature':name,'importance_type':kind,'importance':float(value),
                         'normalized_importance':float(value/total) if total else 0.,'rank':int(rank)})
    if validation_dates:
        dates=np.sort(validation.date.unique())
        selected=dates[np.unique(np.linspace(0,len(dates)-1,min(validation_dates,len(dates)),dtype=int))]
        sample=validation[validation.date.isin(selected)].sort_values(['date','ticker']).reset_index(drop=True)
        base=sample[['date','ticker','FWD_RET_5D']].assign(prediction=predict(estimator,transform,sample))
        original=daily_ic(base,'prediction','FWD_RET_5D',minimum).RankIC.mean()
        changes=[]
        for j,feature in enumerate(transform.features):
            changed=sample.copy()
            rng=np.random.default_rng(seed+20000+j)
            col=f'{feature}_zscore'
            changed[col]=changed.groupby('date',sort=True)[col].transform(lambda s:rng.permutation(s.to_numpy()))
            base['prediction']=predict(estimator,transform,changed)
            loss=original-daily_ic(base,'prediction','FWD_RET_5D',minimum).RankIC.mean()
            changes.append(loss)
        ranks=pd.Series(changes).rank(ascending=False,method='min')
        for name,value,rank in zip(transform.features,changes,ranks):
            rows.append({'feature':name,'importance_type':'validation_permutation_rankic_loss','importance':float(value),
                         'normalized_importance':np.nan,'rank':int(rank),'validation_sessions':len(selected),
                         'validation_base_rankic':original})
    return pd.DataFrame(rows)

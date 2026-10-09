"""Small, predeclared linear baselines with purged annual time splits."""
from dataclasses import dataclass
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler

from src.factors.definitions import NAMES
from src.evaluation.statistics import daily_ic
from src.evaluation.single_factor import label_mask

FEATURES = [n for n in NAMES if n!='REV_5']
GROUPS = {'Momentum_Reversal':['RET_5','RET_10','RET_20','RET_60'],
          'Volatility':['VOL_10','VOL_20','VOL_60'],
          'Liquidity_Volume':['ILLIQ_20','DOLLAR_VOLUME_20','VOLUME_RATIO_20','VOLUME_SURPRISE_20'],
          'Price_Position_Intraday':['PRICE_MA20','PRICE_MA60','DIST_52W_HIGH','INTRADAY_RANGE','OPEN_CLOSE_RETURN'],
          'All':FEATURES}
GRIDS = {'OLS':[0.], 'EqualWeight':[0.], 'Ridge':[.001,.1,10.],
         'Lasso':[.00001,.0001,.001], 'ElasticNet':[.00001,.0001,.001]}


@dataclass(frozen=True)
class Fold:
    year: int
    train_start: str = '2011-01-01'

    def boundaries(self):
        return {'train_start':self.train_start,'train_end':f'{self.year-2}-12-31',
                'validation_start':f'{self.year-1}-01-01','validation_end':f'{self.year-1}-12-31',
                'test_start':f'{self.year}-01-01','test_end':f'{self.year}-12-31'}


def model_feature_mask(panel):
    cols = [f'{f}_zscore' for f in FEATURES]
    return panel.eligible_at_t & np.isfinite(panel[cols]).all(axis=1)


def split_fold(panel,fold):
    """Test *features* are kept without conditioning on test targets."""
    b = fold.boundaries()
    features = model_feature_mask(panel)
    labels = label_mask(panel,5)
    train = features & labels & panel.date.between(b['train_start'],b['train_end'])
    valid = features & labels & panel.date.between(b['validation_start'],b['validation_end'])
    before_train_purge, before_validation_purge = int(train.sum()),int(valid.sum())
    train &= panel.return_end_timestamp_5D < pd.Timestamp(b['validation_start'],tz='UTC')
    valid &= panel.return_end_timestamp_5D < pd.Timestamp(b['test_start'],tz='UTC')
    test = features & panel.date.between(b['test_start'],b['test_end'])
    result = [panel.loc[m].sort_values(['date','ticker']).reset_index(drop=True) for m in [train,valid,test]]
    for data in result:
        if data.duplicated(['date','ticker']).any():
            raise ValueError('Duplicate model sample keys')
    audit = {**b,'fold':fold.year,'train_rows':len(result[0]),'validation_rows':len(result[1]),'test_feature_rows':len(result[2]),
             'train_purged_rows':before_train_purge-len(result[0]),'validation_purged_rows':before_validation_purge-len(result[1]),
             'train_latest_label_timestamp':str(result[0].return_end_timestamp_5D.max()),
             'validation_latest_label_timestamp':str(result[1].return_end_timestamp_5D.max())}
    return *result,audit


@dataclass
class FittedBaseline:
    model: str
    features: list
    mean: np.ndarray
    scale: np.ndarray
    coefficients: np.ndarray
    intercept: float
    parameter: float
    signs: np.ndarray
    warnings: list

    def predict(self,frame):
        x = frame[[f'{f}_zscore' for f in self.features]].to_numpy(float)
        return ((x-self.mean)/self.scale) @ self.coefficients + self.intercept

    def coefficient_table(self):
        raw = self.coefficients / self.scale
        return pd.DataFrame({'factor':self.features,'coefficient_scaled':self.coefficients,
                             'coefficient_phase3_zscore':raw,'scaler_mean':self.mean,'scaler_scale':self.scale,
                             'training_orientation':self.signs,'intercept_scaled':self.intercept,
                             'intercept_phase3_zscore':self.intercept-np.dot(self.mean,raw)})


def fit_candidates(train,validation,model,features=None,minimum=50):
    """No test argument exists. Scaling/signs/coefficients see training only."""
    features = list(features or FEATURES)
    train = train.sort_values(['date','ticker']).reset_index(drop=True)
    validation = validation.sort_values(['date','ticker']).reset_index(drop=True)
    cols = [f'{f}_zscore' for f in features]
    if train.empty or validation.empty:
        raise ValueError('Nonempty training and validation samples required')
    scaler = StandardScaler().fit(train[cols].to_numpy(float))
    x = np.asfortranarray(scaler.transform(train[cols].to_numpy(float)))
    y = train.FWD_RET_5D.to_numpy(float)
    signs = np.ones(len(features))
    if model=='EqualWeight':
        for j,name in enumerate(cols):
            ic = daily_ic(train[['date','ticker',name,'FWD_RET_5D']],name,'FWD_RET_5D',minimum)
            mean_rankic = ic.RankIC.mean()
            signs[j] = -1 if np.isfinite(mean_rankic) and mean_rankic<0 else 1
    records, fitted = [],[]
    for param in GRIDS[model]:
        warn_records = []
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            if model=='EqualWeight':
                score = x @ signs / len(features)
                centered = score-score.mean()
                denominator = np.dot(centered,centered)
                slope = max(0.,np.dot(centered,y-y.mean())/denominator) if denominator>0 else 0.
                coef = slope*signs/len(features)
                intercept = y.mean()-slope*score.mean()
            else:
                if model=='OLS':
                    estimator = LinearRegression()
                elif model=='Ridge':
                    estimator = Ridge(alpha=len(train)*param,solver='cholesky')
                elif model=='Lasso':
                    estimator = Lasso(alpha=param,precompute=True,max_iter=50000,tol=1e-6,selection='cyclic')
                elif model=='ElasticNet':
                    estimator = ElasticNet(alpha=param,l1_ratio=.5,precompute=True,max_iter=50000,tol=1e-6,selection='cyclic')
                else:
                    raise ValueError(f'Unknown model {model}')
                estimator.fit(x,y)
                coef,intercept = estimator.coef_.copy(),float(estimator.intercept_)
            for w in caught:
                warn_records.append(f'{w.category.__name__}: {w.message}')
        for w in warn_records:
            warnings.warn(w,RuntimeWarning,stacklevel=2)
        fit = FittedBaseline(model,features,scaler.mean_.copy(),scaler.scale_.copy(),np.asarray(coef),float(intercept),param,signs.copy(),warn_records)
        prediction = fit.predict(validation)
        frame = validation[['date','ticker','FWD_RET_5D']].assign(prediction=prediction)
        ic = daily_ic(frame,'prediction','FWD_RET_5D',minimum)
        records.append({'model':model,'parameter':param,'sklearn_alpha':len(train)*param if model=='Ridge' else param,
                        'validation_MSE':float(np.mean((prediction-validation.FWD_RET_5D)**2)),
                        'validation_IC':ic.IC.mean(),'validation_RankIC':ic.RankIC.mean(),
                        'validation_scored_dates':int(ic.RankIC.notna().sum()),'fit_warnings':' | '.join(warn_records),
                        'train_rows':len(train),'validation_rows':len(validation)})
        fitted.append(fit)
    scores = [r['validation_RankIC'] if np.isfinite(r['validation_RankIC']) else -np.inf for r in records]
    best_rank = max(scores)
    candidates = [i for i,s in enumerate(scores) if s==best_rank or abs(s-best_rank)<=1e-12]
    best = min(candidates,key=lambda i:(records[i]['validation_MSE'],-records[i]['parameter']))
    for i,r in enumerate(records):
        r['selected'] = i==best
    return fitted[best],pd.DataFrame(records)


def tag_predictions(test,prediction,model,group,fold):
    """Only after fitting/prediction are held-out targets attached for scoring."""
    b = fold.boundaries()
    if not test.date.between(b['test_start'],b['test_end']).all():
        raise ValueError('Prediction outside declared test fold')
    valid = label_mask(test,5)
    return test[['date','ticker']].assign(target=test.FWD_RET_5D.where(valid).to_numpy(),
             target_available=valid.to_numpy(),prediction=prediction,model=model,feature_group=group,
             fold=fold.year,sample_role='test',**b)

"""Date-local associations and calendar-preserving inference for means."""
import numpy as np
import pandas as pd
from scipy.stats import norm


def daily_ic(frame, value, target='target', minimum=50, sessions=None):
    if frame.duplicated(['date','ticker']).any():
        raise ValueError('Duplicate date/ticker observations')
    ordered = frame.sort_values(['date','ticker'])
    work = ordered.loc[np.isfinite(ordered[value]) & np.isfinite(ordered[target]), ['date','ticker',value,target]].copy()
    dates = pd.DatetimeIndex(sessions if sessions is not None else sorted(ordered.date.unique()), name='date')
    if work.empty:
        return pd.DataFrame({'date':dates,'n_stocks':0,'IC':np.nan,'RankIC':np.nan})
    def corr(x,y):
        centered_x = x - x.groupby(work.date).transform('mean')
        centered_y = y - y.groupby(work.date).transform('mean')
        numerator = (centered_x * centered_y).groupby(work.date).sum()
        denominator = np.sqrt(centered_x.pow(2).groupby(work.date).sum() * centered_y.pow(2).groupby(work.date).sum())
        usable = (x.groupby(work.date).nunique()>1) & (y.groupby(work.date).nunique()>1)
        return (numerator / denominator.where(denominator>0)).where(usable).clip(-1,1)
    count = work.groupby('date').size()
    ranks = work.groupby('date')[[value,target]].rank(method='average')
    result = pd.DataFrame({'n_stocks':count,'IC':corr(work[value],work[target]),'RankIC':corr(ranks[value],ranks[target])})
    result.loc[result.n_stocks < minimum,['IC','RankIC']] = np.nan
    result = result.reindex(dates)
    result['n_stocks'] = result.n_stocks.fillna(0).astype(int)
    return result.reset_index()


def mean_inference(series, lag=5):
    """Mean-score HAC; NaN slots preserve calendar distance (not zero ICs).

    Var(mean) = n/(n-1) * [sum u_t² + 2 sum_k w_k sum_t u_t*u_(t-k)]/n².
    Only observed values count in n and the mean; missing score residuals are 0.
    """
    if lag < 0:
        raise ValueError('Nonnegative HAC lag required')
    x = np.asarray(series,dtype=float)
    valid = np.isfinite(x)
    n = int(valid.sum())
    clean = x[valid]
    mean = clean.mean() if n else np.nan
    std = clean.std(ddof=1) if n>1 else np.nan
    out = dict(n_dates=n,mean=mean,median=np.median(clean) if n else np.nan,std=std,
               IR=mean/std if std>0 else np.nan,positive_ratio=float((clean>0).mean()) if n else np.nan,
               naive_t=mean/(std/np.sqrt(n)) if std>0 else np.nan,hac_lag=lag,
               hac_se=np.nan,hac_t=np.nan,hac_p=np.nan,ci95_low=np.nan,ci95_high=np.nan)
    if n>1:
        residual = np.where(valid,x-mean,0.)
        meat = np.dot(residual,residual)
        for k in range(1,min(lag,len(x)-1)+1):
            meat += 2 * (1-k/(lag+1)) * np.dot(residual[k:],residual[:-k])
        variance = max(0.,meat) / n**2 * n/(n-1)
        if variance>1e-30:
            se = np.sqrt(variance)
            t = mean/se
            out.update(hac_se=se,hac_t=t,hac_p=2*norm.sf(abs(t)),ci95_low=mean-1.95996398454*se,ci95_high=mean+1.95996398454*se)
    for q in [.01,.05,.25,.75,.95,.99]:
        out[f'q{int(q*100):02}'] = np.quantile(clean,q) if n else np.nan
    out['skewness'] = pd.Series(clean).skew() if n>=3 else np.nan
    return out


def bh_adjust(pvalues):
    p = np.asarray(pvalues,float)
    out = np.full(len(p),np.nan)
    valid = np.flatnonzero(np.isfinite(p))
    order = valid[np.argsort(p[valid],kind='stable')]
    m = len(order)
    if m:
        out[order] = np.minimum(1,np.minimum.accumulate((p[order]*m/np.arange(1,m+1))[::-1])[::-1])
    return out


def ic_summary(daily, lag=5):
    result = {}
    for name in ['IC','RankIC']:
        result.update({f'{name}_{k}':v for k,v in mean_inference(daily[name],lag).items()})
    mask = daily.IC.notna() & daily.RankIC.notna()
    result['valid_dates'] = int(mask.sum())
    result['median_stocks_per_date'] = daily.loc[mask,'n_stocks'].median()
    result['scored_stock_dates'] = int(daily.loc[mask,'n_stocks'].sum())
    return result

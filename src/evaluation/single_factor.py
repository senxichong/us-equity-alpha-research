"""Raw-sign single-factor research; labels never define quantile formation."""
import numpy as np
import pandas as pd

from src.factors.definitions import NAMES
from .statistics import daily_ic, ic_summary, mean_inference


def feature_mask(panel, factor):
    return panel.eligible_at_t & panel[f'factor_available_{factor}'] & np.isfinite(panel[factor])


def label_mask(panel,h=5):
    return panel.entry_price_valid & panel[f'exit_price_valid_{h}D'] & panel[f'target_available_{h}D'] & np.isfinite(panel[f'FWD_RET_{h}D'])


def factor_ic(panel,factor,sessions,h=5,minimum=50):
    mask = feature_mask(panel,factor) & label_mask(panel,h)
    sample = panel.loc[mask,['date','ticker',factor,f'FWD_RET_{h}D']].rename(columns={f'FWD_RET_{h}D':'target'})
    daily = daily_ic(sample,factor,minimum=minimum,sessions=sessions)
    daily['factor'], daily['horizon'] = factor,h
    summary = {'factor':factor,'horizon':h,**ic_summary(daily,lag=h)}
    scored_dates = daily.loc[daily.IC.notna() & daily.RankIC.notna(),'date']
    used = sample.loc[sample.date.isin(scored_dates)]
    summary.update(stocks=int(used.ticker.nunique()),first_scored_date=used.date.min(),last_scored_date=used.date.max(),
                   paired_stock_dates=int(mask.sum()),paired_dates=int(sample.date.nunique()))
    if h==5:
        for name in ['IC','RankIC']:
            sensitivity = mean_inference(daily[name],20)
            summary[f'{name}_hac_t_lag20'] = sensitivity['hac_t']
            summary[f'{name}_hac_p_lag20'] = sensitivity['hac_p']
    return daily,summary


def assign_quantiles(frame,value,minimum=50):
    """Rank-midpoint quintiles, preserving ties; no target columns accessed."""
    frame = frame.sort_values(['date','ticker']).copy()
    group = frame.groupby('date')[value]
    rank = group.rank(method='average')
    count = group.transform('count')
    q = np.floor((rank-.5)/count*5)+1
    usable = (count>=minimum) & (group.transform('nunique')>=5) & np.isfinite(frame[value])
    q = q.where(usable)
    # Tied mass can empty a bin; never pretend a collapsed partition is Q1-Q5.
    q = q.where(q.groupby(frame.date).transform('nunique')==5)
    return frame[['date','ticker']].assign(quantile=q)


def quantile_analysis(panel,factor,sessions,minimum=50,min_bin=10):
    member = panel.loc[feature_mask(panel,factor),['date','ticker',factor]]
    assigned = assign_quantiles(member,factor,minimum).dropna(subset=['quantile'])
    assigned['quantile'] = assigned['quantile'].astype(int)
    labels = panel[['date','ticker','FWD_RET_5D']].copy()
    labels['target'] = labels.FWD_RET_5D.where(label_mask(panel,5))
    work = assigned.merge(labels[['date','ticker','target']],on=['date','ticker'],validate='one_to_one')
    grouped = work.groupby(['date','quantile']).agg(n_assigned=('ticker','size'),n_labeled=('target','count'),mean_return=('target','mean'),median_return=('target','median'))
    enough = grouped.n_labeled.unstack().reindex(columns=range(1,6)).ge(min_bin).all(axis=1)
    daily = grouped.reset_index()
    daily['diagnostic_available'] = daily.date.map(enough).fillna(False)
    daily.loc[~daily.diagnostic_available,['mean_return','median_return']] = np.nan
    daily['factor'] = factor
    wide = daily.pivot(index='date',columns='quantile',values='mean_return').reindex(index=sessions,columns=range(1,6))
    spread = wide[5]-wide[1]
    mean_q = wide.mean()
    monotonicity = mean_q.corr(pd.Series(range(1,6),index=range(1,6)),method='spearman')
    inference = mean_inference(spread,5)
    summary = []
    good_dates = enough.index[enough]
    good_work = work[work.date.isin(good_dates)]
    for q in range(1,6):
        summary.append({'factor':factor,'quantile':q,'mean_forward_return':wide[q].mean(),
                        'median_daily_mean_return':wide[q].median(),'pooled_label_median':good_work.loc[good_work['quantile']==q,'target'].median(),
                        'valid_dates':int(wide[q].notna().sum()),'monotonicity_score':monotonicity,
                        'increasing_steps':int((mean_q.diff().dropna()>0).sum()),'decreasing_steps':int((mean_q.diff().dropna()<0).sum()),
                        **{f'top_minus_bottom_{k}':v for k,v in inference.items()}})
    yearly = []
    for year,g in wide.groupby(wide.index.year):
        mean = g.mean()
        yearly.append({'factor':factor,'year':year,**{f'Q{q}':mean[q] for q in range(1,6)},
                       'monotonicity_score':mean.corr(pd.Series(range(1,6),index=range(1,6)),method='spearman'),
                       **{f'spread_{k}':v for k,v in mean_inference(g[5]-g[1],5).items()}})
    return daily,pd.DataFrame(summary),pd.DataFrame(yearly)


def factor_correlations(panel,minimum=50):
    totals = pd.DataFrame(0.,index=NAMES,columns=NAMES)
    counts = pd.DataFrame(0,index=NAMES,columns=NAMES)
    work = panel.loc[panel.eligible_at_t,['date',*NAMES]].copy()
    for name in NAMES:
        work[name] = work[name].where(np.isfinite(work[name]) & panel.loc[work.index,f'factor_available_{name}'])
    for _,group in work.groupby('date',sort=True):
        corr = group[NAMES].corr(method='spearman',min_periods=minimum)
        totals += corr.fillna(0)
        counts += corr.notna().astype(int)
    return totals / counts.replace(0,np.nan),counts

"""Saved-prediction metrics, shared by report generation and consistency tests."""
import numpy as np
import pandas as pd

from src.data.download import sha256
from .statistics import daily_ic,ic_summary,mean_inference


def read_prediction(entry):
    if sha256(entry['path'])!=entry['sha256']:
        raise ValueError('Saved prediction checksum mismatch')
    frame=pd.read_parquet(entry['path']).sort_values(['date','ticker']).reset_index(drop=True)
    if frame.duplicated(['date','ticker']).any(): raise ValueError('Duplicate saved prediction key')
    if not frame.sample_role.eq('test').all(): raise ValueError('Non-test prediction contamination')
    if not np.isfinite(frame.prediction).all(): raise ValueError('Nonfinite saved prediction')
    if not frame.target_available.equals(frame.target.notna()): raise ValueError('Label validity inconsistency')
    return frame


def error_moments(frame):
    data=frame.loc[frame.target_available & np.isfinite(frame.target) & np.isfinite(frame.prediction)]
    e=data.prediction-data.target
    return {'observations':len(data),'sse':float(np.square(e).sum()),'sae':float(np.abs(e).sum()),
            'sum_y':float(data.target.sum()),'sum_y2':float(np.square(data.target).sum())}


def regression_metrics(m):
    n=m['observations']
    sst=m['sum_y2']-m['sum_y']**2/n if n else np.nan
    return {'observations':int(n),'MSE':m['sse']/n if n else np.nan,'MAE':m['sae']/n if n else np.nan,
            'R2':1-m['sse']/sst if sst>0 else np.nan}


def metrics_from_saved(entry,sessions,minimum=50):
    frame=read_prediction(entry)
    daily=daily_ic(frame,'prediction',minimum=minimum,sessions=sessions)
    moments=error_moments(frame)
    summary={**regression_metrics(moments),**ic_summary(daily,5)}
    return frame,daily,moments,summary


def paired_comparison(model_daily,benchmark_daily,model,benchmark):
    pairs=model_daily[['date','RankIC']].merge(benchmark_daily[['date','RankIC']],on='date',validate='one_to_one',suffixes=('_model','_benchmark')).sort_values('date')
    pairs['delta_RankIC']=pairs.RankIC_model-pairs.RankIC_benchmark
    stats=mean_inference(pairs.delta_RankIC,5)
    longer=mean_inference(pairs.delta_RankIC,20)
    stats.update(model=model,benchmark=benchmark,hac_t_lag20=longer['hac_t'],ci95_low_lag20=longer['ci95_low'],ci95_high_lag20=longer['ci95_high'])
    years=pairs.groupby(pairs.date.dt.year).delta_RankIC.mean()
    stats['years_better']=int((years>0).sum());stats['years_worse']=int((years<0).sum());stats['years_available']=int(years.notna().sum())
    return pairs.assign(model=model,benchmark=benchmark),stats

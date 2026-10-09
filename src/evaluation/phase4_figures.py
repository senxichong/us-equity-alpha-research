"""A fixed, concise set of descriptive research figures; no strategy charts."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.factors.definitions import NAMES

EXAMPLES=['RET_20','REV_5','VOL_20','ILLIQ_20','VOLUME_RATIO_20','DIST_52W_HIGH']
TITLE='SURVIVORSHIP-BIASED PROTOTYPE'


def generate_figures(reports):
    reports=Path(reports)
    out=reports/'figures'
    out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':130})
    files=[]
    def save(fig,name,subtitle):
        fig.suptitle(f'{TITLE}\n{subtitle}',fontsize=13,fontweight='bold')
        fig.text(.5,.012,'candidate_selection_biased = true | Overlapping forward labels; no capital or transaction-cost accounting',ha='center',fontsize=8)
        fig.tight_layout(rect=[0,.035,1,.92])
        path=out/f'{name}.png'
        fig.savefig(path,dpi=150,facecolor='white')
        plt.close(fig)
        files.append(path)

    corr=pd.read_csv(reports/'factor_correlation.csv').set_index('factor')[NAMES]
    fig,ax=plt.subplots(figsize=(12,10))
    im=ax.imshow(corr,vmin=-1,vmax=1,cmap='RdBu_r')
    ax.set_xticks(range(len(NAMES)),NAMES,rotation=65,ha='right',fontsize=8)
    ax.set_yticks(range(len(NAMES)),NAMES,fontsize=8)
    fig.colorbar(im,ax=ax,label='Average daily Spearman correlation',shrink=.8)
    save(fig,'factor_correlation','Eligible-at-signal factor redundancy; no target filter')

    roll=pd.read_csv(reports/'rolling_factor_statistics.csv',parse_dates=['date'])
    fig,axes=plt.subplots(3,2,figsize=(13,9),sharex=True,sharey=True)
    for ax,n in zip(axes.flat,EXAMPLES):
        g=roll[roll.factor==n]
        ax.plot(g.date,g.RankIC_rolling_126,lw=.7,alpha=.45,label='126 sessions')
        ax.plot(g.date,g.RankIC_rolling_252,lw=1.4,label='252 sessions')
        ax.axhline(0,color='black',lw=.6)
        ax.set_title(n)
        ax.set_ylabel('Mean raw-sign RankIC')
    axes[0,0].legend(fontsize=8)
    save(fig,'rolling_rankic','5D primary target: preselected examples, fixed rolling windows')

    stats=pd.read_csv(reports/'factor_statistics.csv').set_index('factor').reindex(NAMES)
    fig,ax=plt.subplots(figsize=(11,8))
    y=np.arange(len(NAMES))
    ax.barh(y-.17,stats.IC_mean,height=.33,label='Pearson IC',color='#3182bd')
    ax.barh(y+.17,stats.RankIC_mean,height=.33,label='RankIC',color='#e58b25')
    ax.errorbar(stats.RankIC_mean,y+.17,xerr=1.959964*stats.RankIC_hac_se,fmt='none',ecolor='black',lw=.7,label='RankIC 95% HAC interval (lag 5)')
    ax.set_yticks(y,NAMES)
    ax.invert_yaxis()
    ax.axvline(0,color='black',lw=.7)
    ax.legend(fontsize=8)
    ax.set_xlabel('Mean daily cross-sectional association; original signs')
    save(fig,'factor_ic_comparison','Primary 5D evidence; intervals do not correct all research/data biases')

    quant=pd.read_csv(reports/'quantile_diagnostics.csv')
    fig,axes=plt.subplots(2,3,figsize=(13,7))
    for ax,n in zip(axes.flat,EXAMPLES):
        g=quant[quant.factor==n].sort_values('quantile')
        ax.plot(g['quantile'],1e4*g.mean_forward_return,'o-',lw=1.5)
        ax.set_xticks(range(1,6),[f'Q{i}' for i in range(1,6)])
        ax.set_title(n)
        ax.set_ylabel('Mean 5D forward label (bp)')
        ax.grid(axis='y',alpha=.2)
    save(fig,'quantile_forward_returns','Forward-return quantile diagnostics; Q1 low raw factor, Q5 high')

    annual=pd.read_csv(reports/'yearly_factor_statistics.csv')
    annual=annual.pivot(index='factor',columns='year',values='RankIC_mean').reindex(NAMES)
    fig,ax=plt.subplots(figsize=(13,8))
    lim=np.nanmax(np.abs(annual.to_numpy()))
    im=ax.imshow(annual,aspect='auto',vmin=-lim,vmax=lim,cmap='RdBu_r')
    ax.set_yticks(range(len(NAMES)),NAMES,fontsize=8)
    ax.set_xticks(range(len(annual.columns)),[f'{y}*' if y in [2010,2026] else str(y) for y in annual.columns],rotation=45)
    fig.colorbar(im,ax=ax,label='Mean raw-sign RankIC',shrink=.8)
    save(fig,'yearly_rankic','5D target yearly stability (* partial year; 2010 has only warm-up-end observations)')

    daily_ic_frame=pd.read_csv(reports/'single_factor_ic.csv',parse_dates=['date'])
    daily_rank=pd.read_csv(reports/'single_factor_rankic.csv',parse_dates=['date'])
    fig,axes=plt.subplots(3,3,figsize=(15,9))
    for row,n in enumerate(['RET_20','VOL_20','ILLIQ_20']):
        ic=daily_ic_frame[daily_ic_frame.factor==n]
        rank=daily_rank[daily_rank.factor==n]
        axes[row,0].plot(ic.date,ic.IC,lw=.4,alpha=.6)
        axes[row,0].set_title(f'{n}: daily Pearson IC')
        axes[row,1].hist(ic.IC.dropna(),bins=35,color='#3182bd',alpha=.8)
        axes[row,1].set_title(f'{n}: Pearson IC distribution')
        axes[row,2].plot(rank.date,rank.RankIC,lw=.4,alpha=.6,color='#e58b25')
        axes[row,2].set_title(f'{n}: daily RankIC')
        for col in [0,2]:
            axes[row,col].axhline(0,color='black',lw=.5)
            axes[row,col].set_ylim(-1,1)
    save(fig,'ic_distributions','Preselected examples; complete per-factor quantiles/extreme dates are in CSV tables')

    models=pd.read_csv(reports/'model_oos_metrics.csv').set_index('model').reindex(['EqualWeight','OLS','Ridge','Lasso','ElasticNet'])
    fig,ax=plt.subplots(figsize=(10,6))
    x=np.arange(len(models))
    ax.bar(x-.18,models.IC_mean,width=.36,label='IC',color='#3182bd')
    ax.bar(x+.18,models.RankIC_mean,width=.36,label='RankIC',color='#e58b25')
    ax.errorbar(x+.18,models.RankIC_mean,yerr=1.959964*models.RankIC_hac_se,fmt='none',ecolor='black',label='95% HAC mean RankIC interval')
    ax.set_xticks(x,models.index)
    ax.set_ylabel('Mean daily OOS association')
    ax.axhline(0,color='black',lw=.7)
    ax.legend(fontsize=8)
    save(fig,'model_oos_ic','2017–2026 test-only predictions; 2026 partial, common complete-feature sample')

    co=pd.read_csv(reports/'model_coefficients.csv')
    fig,axes=plt.subplots(1,2,figsize=(14,9),sharey=True)
    for ax,model in zip(axes,['OLS','Ridge']):
        g=co[(co.model==model)&(co.feature_group=='All')]
        wide=g.pivot(index='factor',columns='fold',values='coefficient_phase3_zscore')
        lim=max(np.abs(wide.to_numpy()).max(),1e-8)
        im=ax.imshow(wide,aspect='auto',cmap='RdBu_r',vmin=-lim,vmax=lim)
        ax.set_yticks(range(len(wide.index)),wide.index,fontsize=8)
        ax.set_xticks(range(len(wide.columns)),wide.columns,rotation=45)
        ax.set_title(f'{model}: own color scale')
        fig.colorbar(im,ax=ax,shrink=.65,label='Return per Phase 3 z-score unit')
    save(fig,'coefficient_stability','Fold coefficients; all four fitted linear models are recorded in CSV')
    return files

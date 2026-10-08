"""Versioned, machine-readable definitions; no data-dependent choices."""

FACTOR_VERSION = '1.0.0'
BIAS = {'survivorship_biased': True, 'candidate_selection_biased': True,
        'point_in_time_membership': False}
PREPROCESSING = {'winsor_quantiles': [0.01, 0.99], 'quantile_interpolation': 'linear',
                 'zscore_ddof': 0, 'minimum_cross_section': 2,
                 'membership': 'eligible_at_t AND individual raw factor finite',
                 'zero_variance': 'NaN', 'fit_scope': 'same date only',
                 'target_filter': False, 'neutralization': None}


def definition(name, window, fields, description, units='dimensionless', extreme_abs=1.):
    return dict(name=name, lookback_sessions=window, minimum_history=window,
                source_fields=fields, uses_current_day=True, observable_after_close=True,
                missing_value_rule='require every input in exact trailing exchange-session window; no fill',
                preprocessing=PREPROCESSING, description=description, units=units,
                diagnostic_extreme_absolute_threshold=extreme_abs)


FACTORS = [
    *[definition(f'RET_{h}', h + 1, ['adj_close'], f'P[t]/P[t-{h}]-1; all {h+1} prices required') for h in (5, 10, 20, 60)],
    definition('REV_5', 6, ['adj_close'], '-RET_5; exact sign reversal, not an independent signal'),
    *[definition(f'VOL_{h}', h + 1, ['adj_close'], f'sample std (ddof=1) of {h} one-session returns ending t; not annualized') for h in (10, 20, 60)],
    definition('ILLIQ_20', 21, ['adj_close', 'close', 'volume'], 'mean(abs(P[s]/P[s-1]-1)/(close[s]*volume[s])), s=t-19..t', 'inverse vendor USD-volume proxy', 1e-6),
    definition('DOLLAR_VOLUME_20', 20, ['close', 'volume'], 'mean(close[s]*volume[s]), s=t-19..t; vendor basis', 'vendor USD-volume proxy', 1e11),
    definition('VOLUME_RATIO_20', 21, ['volume'], 'volume[t]/mean(volume[t-20:t-1]); current volume excluded from reference', 'dimensionless', 10.),
    definition('VOLUME_SURPRISE_20', 21, ['volume'], '(volume[t]-mean(volume[t-20:t-1]))/sample_std(volume[t-20:t-1], ddof=1); zero std -> NaN', 'dimensionless', 10.),
    *[definition(f'PRICE_MA{h}', h, ['adj_close'], f'P[t]/mean(P[t-{h-1}:t])-1') for h in (20, 60)],
    definition('DIST_52W_HIGH', 252, ['adj_close'], 'P[t]/max(P[t-251:t])-1; 252-session adjusted CLOSE high, not intraday high'),
    definition('INTRADAY_RANGE', 1, ['high', 'low', 'close'], '(high[t]-low[t])/close[t]; same vendor OHLC basis'),
    definition('OPEN_CLOSE_RETURN', 1, ['open', 'close'], 'close[t]/open[t]-1; same vendor OHLC basis'),
]
NAMES = [f['name'] for f in FACTORS]

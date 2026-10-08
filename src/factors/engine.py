"""Exact-session, past-only raw features. No labels or future shifts here."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .definitions import NAMES


def validate_grid(panel, sessions):
    sessions = pd.DatetimeIndex(sessions)
    if sessions.tz is not None or sessions.hasnans or sessions.has_duplicates or not sessions.is_monotonic_increasing:
        raise ValueError('Sorted unique naive session labels required')
    if panel[['date', 'ticker']].isna().any().any() or panel.duplicated(['date', 'ticker']).any():
        raise ValueError('Unique non-null ticker-date keys required')
    if not panel.date.isin(sessions).all():
        raise ValueError('Dates outside supplied calendar')
    if not pd.api.types.is_bool_dtype(panel.is_valid_observation):
        raise ValueError('Boolean observation validity required')
    return sessions


def valid_prices(history, column):
    values = history[column]
    return values.where(history.is_valid_observation.eq(True) & np.isfinite(values) & (values > 0))


def compute_factors(panel, sessions):
    """Return original keys/order with raw factors and per-factor availability.

    Invalid/missing sessions consume a position. Input is never filtered by
    eligibility: otherwise the time-series lookbacks would change their meaning.
    """
    sessions = validate_grid(panel, sessions)
    pieces = []
    for ticker, group in panel.groupby('ticker', sort=False):
        hist = group.set_index('date').reindex(sessions)
        p = valid_prices(hist, 'adj_close')
        close, volume = valid_prices(hist, 'close'), valid_prices(hist, 'volume')
        dv = close * volume
        dv = dv.where(np.isfinite(dv) & (dv > 0))
        r = p / p.shift(1) - 1
        f = pd.DataFrame(index=sessions)
        for h in (5, 10, 20, 60):
            f[f'RET_{h}'] = (p / p.shift(h) - 1).where(p.rolling(h + 1, min_periods=h + 1).count() == h + 1)
        f['REV_5'] = -f.RET_5
        for h in (10, 20, 60):
            f[f'VOL_{h}'] = r.rolling(h, min_periods=h).std(ddof=1)
        f['ILLIQ_20'] = (r.abs() / dv).rolling(20, min_periods=20).mean()
        f['DOLLAR_VOLUME_20'] = dv.rolling(20, min_periods=20).mean()
        previous = volume.shift(1).rolling(20, min_periods=20)
        mean, std = previous.mean(), previous.std(ddof=1)
        f['VOLUME_RATIO_20'] = volume / mean
        f['VOLUME_SURPRISE_20'] = (volume - mean) / std.where(std > 0)
        for h in (20, 60):
            f[f'PRICE_MA{h}'] = p / p.rolling(h, min_periods=h).mean() - 1
        f['DIST_52W_HIGH'] = p / p.rolling(252, min_periods=252).max() - 1
        f['INTRADAY_RANGE'] = (valid_prices(hist, 'high') - valid_prices(hist, 'low')) / close
        f['OPEN_CLOSE_RETURN'] = close / valid_prices(hist, 'open') - 1
        f = f[NAMES].where(np.isfinite(f[NAMES]))
        f['date'], f['ticker'] = sessions, ticker
        pieces.append(f.loc[f.date.isin(group.date)])
    result = panel[['date', 'ticker']].merge(pd.concat(pieces, ignore_index=True), on=['date', 'ticker'], validate='one_to_one', sort=False)
    flags = {f'factor_available_{name}': result[name].notna() for name in NAMES}
    flags['factor_available'] = result[NAMES].notna().all(axis=1)
    return pd.concat([result, pd.DataFrame(flags)], axis=1)

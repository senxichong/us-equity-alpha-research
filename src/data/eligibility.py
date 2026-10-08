"""Past-only research eligibility conditional on a frozen, biased candidate panel.

This is a mask, not a factor, return target, or point-in-time membership provider.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EligibilityRules:
    minimum_valid_history: int = 252
    liquidity_window_sessions: int = 60
    minimum_median_dollar_volume: float = 10_000_000

    def __post_init__(self):
        if self.minimum_valid_history < 1 or self.liquidity_window_sessions < 1:
            raise ValueError('History and window lengths must be positive')
        if not np.isfinite(self.minimum_median_dollar_volume) or self.minimum_median_dollar_volume < 0:
            raise ValueError('Invalid liquidity threshold')

    def metadata(self):
        return {
            **asdict(self),
            'survivorship_biased': True,
            'point_in_time_membership': False,
            'candidate_universe_frozen': True,
            'price_field': 'close',
            'dollar_volume_convention': 'vendor_close_times_vendor_volume_proxy',
            'window_includes_current_session': True,
            'required_valid_liquidity_sessions': self.liquidity_window_sessions,
            'available_at': 'after_current_session_close_and_bar_availability',
            'execution_at_same_close_authorized': False,
            'missing_value_fill': 'none',
            'global_selection_bias_removed': False,
        }


def compute_eligibility(panel, sessions, rules=None):
    """Return a keyed mask for exactly the input rows, preserving their order.

    Reindex internally to the exchange calendar so absent rows consume a session
    in the trailing window. Pre-listing slots have no price and contribute zero
    valid history. Never use precomputed full-sample counts or latest liquidity.
    """
    rules = rules or EligibilityRules()
    columns = ['date', 'ticker', 'close', 'volume', 'is_valid_observation']
    if not set(columns).issubset(panel.columns):
        raise ValueError('Eligibility requires date, ticker, close, volume and validity')
    work = panel[columns].copy()
    work['date'] = pd.to_datetime(work.date, errors='raise')
    if work[['date', 'ticker']].isna().any().any() or work.duplicated(['date', 'ticker']).any():
        raise ValueError('Non-null unique ticker-date keys required')
    if not pd.api.types.is_bool_dtype(work.is_valid_observation.dtype):
        raise ValueError('is_valid_observation must be boolean')
    sessions = pd.DatetimeIndex(sessions)
    if sessions.tz is not None or sessions.has_duplicates or not sessions.is_monotonic_increasing or sessions.hasnans:
        raise ValueError('Sorted unique timezone-naive exchange-session labels required')
    if not work.date.isin(sessions).all():
        raise ValueError('Panel dates outside supplied exchange calendar')
    if work.empty:
        return pd.DataFrame(columns=['date', 'ticker', 'eligibility_valid_history_count', 'liquidity_valid_sessions', 'trailing_median_dollar_volume', 'is_research_eligible', 'eligibility_reason'])
    pieces = []
    for ticker, group in work.groupby('ticker', sort=False):
        history = group.set_index('date').reindex(sessions)
        # Check only current-row inputs. No future-row anomaly can veto this row.
        valid = history.is_valid_observation.eq(True).fillna(False).astype(bool)
        close = pd.to_numeric(history.close, errors='coerce')
        volume = pd.to_numeric(history.volume, errors='coerce')
        with np.errstate(over='ignore', invalid='ignore'):
            dollar_volume = close * volume
        valid &= np.isfinite(close) & np.isfinite(volume) & np.isfinite(dollar_volume) & (close > 0) & (volume > 0)
        dollar_volume = dollar_volume.where(valid)
        count = valid.astype('int32').cumsum()
        window = rules.liquidity_window_sessions
        observed_in_window = valid.astype('int32').rolling(window, min_periods=1, center=False).sum().astype('int32')
        median = dollar_volume.rolling(window, min_periods=window, center=False).median()
        enough_history = count >= rules.minimum_valid_history
        complete_window = observed_in_window == window
        liquid = median >= rules.minimum_median_dollar_volume
        eligible = valid & enough_history & complete_window & liquid
        reason = np.select(
            [~valid, ~enough_history, ~complete_window, ~liquid],
            ['invalid_current_observation', 'insufficient_valid_history', 'incomplete_trailing_liquidity_window', 'below_liquidity_threshold'],
            default='eligible',
        )
        result = pd.DataFrame({
            'date': sessions, 'ticker': ticker,
            'eligibility_valid_history_count': count.to_numpy(dtype='int32'),
            'liquidity_valid_sessions': observed_in_window.to_numpy(dtype='int32'),
            'trailing_median_dollar_volume': median.to_numpy(),
            'is_research_eligible': eligible.to_numpy(dtype=bool),
            'eligibility_reason': reason,
        })
        pieces.append(result.loc[result.date.isin(group.date)])
    mask = pd.concat(pieces, ignore_index=True)
    return work[['date', 'ticker']].merge(mask, on=['date', 'ticker'], how='left', sort=False, validate='one_to_one')


def attach_eligibility(panel, sessions, rules=None):
    mask = compute_eligibility(panel, sessions, rules)
    overlap = (set(mask.columns) - {'date', 'ticker'}) & set(panel.columns)
    if overlap:
        raise ValueError(f'Eligibility columns already exist: {sorted(overlap)}')
    result = panel.merge(mask, on=['date', 'ticker'], how='left', sort=False, validate='one_to_one')
    result.index = panel.index
    return result

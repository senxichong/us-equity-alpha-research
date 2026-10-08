"""Only this module reads future security rows: scheduled adjusted-open labels."""
import numpy as np
import pandas as pd

from .engine import validate_grid, valid_prices

HORIZONS = (1, 5, 10, 20)
TIMING_ID = 'after_close_next_open_adjusted_proxy_v1'


def timing_table(sessions, schedule):
    """Schedule includes at least 21 exchange sessions beyond final signal date."""
    sessions = pd.DatetimeIndex(sessions)
    positions = schedule.index.get_indexer(sessions)
    if (positions < 0).any() or positions[-1] + max(HORIZONS) + 1 >= len(schedule):
        raise ValueError('Schedule must contain signal sessions and all scheduled exits')
    if not schedule.index[positions[0]:positions[-1]+1].equals(sessions):
        raise ValueError('Signal sessions must be contiguous exchange sessions')
    out = pd.DataFrame({'date': sessions})
    out['feature_timestamp'] = schedule['close'].iloc[positions].reset_index(drop=True) + pd.Timedelta(1, 'ns')
    out['portfolio_formation_timestamp'] = out.feature_timestamp
    out['entry_session'] = schedule.index[positions + 1]
    out['return_start_timestamp'] = schedule['open'].iloc[positions + 1].reset_index(drop=True)
    for h in HORIZONS:
        out[f'exit_session_{h}D'] = schedule.index[positions + h + 1]
        out[f'return_end_timestamp_{h}D'] = schedule['open'].iloc[positions + h + 1].reset_index(drop=True)
    return out


def compute_targets(panel, sessions, schedule):
    sessions = validate_grid(panel, sessions)
    timing = timing_table(sessions, schedule)
    pieces = []
    for ticker, group in panel.groupby('ticker', sort=False):
        hist = group.set_index('date').reindex(sessions)
        vendor = valid_prices(hist, 'open')
        adjusted = valid_prices(hist, 'adjusted_open')
        # Both bases are retained, but never mixed in a ratio.
        valid = vendor.notna() & adjusted.notna()
        vendor, adjusted = vendor.where(valid), adjusted.where(valid)
        entry, entry_vendor = adjusted.shift(-1), vendor.shift(-1)
        out = pd.DataFrame({'date': sessions, 'ticker': ticker,
                            'entry_price': entry.to_numpy(), 'entry_vendor_open': entry_vendor.to_numpy(),
                            'entry_price_valid': entry.notna().to_numpy()})
        for h in HORIZONS:
            exit_price, exit_vendor = adjusted.shift(-(h + 1)), vendor.shift(-(h + 1))
            ret = exit_price / entry - 1
            ret = ret.where(np.isfinite(ret))
            out[f'exit_price_{h}D'] = exit_price.to_numpy()
            out[f'exit_vendor_open_{h}D'] = exit_vendor.to_numpy()
            out[f'exit_price_valid_{h}D'] = exit_price.notna().to_numpy()
            out[f'FWD_RET_{h}D'] = ret.to_numpy()
            out[f'target_available_{h}D'] = ret.notna().to_numpy()
        pieces.append(out.loc[out.date.isin(group.date)])
    result = panel[['date', 'ticker']].merge(pd.concat(pieces, ignore_index=True), on=['date', 'ticker'], sort=False, validate='one_to_one')
    return result.merge(timing, on='date', how='left', sort=False, validate='many_to_one')

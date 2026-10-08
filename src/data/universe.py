"""Keep the prototype label unavoidable; gate unverified historical membership."""
from pathlib import Path

import pandas as pd

PROTOTYPE_LABEL = 'SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE'


def universe_label(cfg):
    if cfg['universe_mode'] == 'prototype_current_sp500':
        return PROTOTYPE_LABEL
    if cfg['universe_mode'] == 'point_in_time_universe':
        if not cfg.get('pit_verified') or not cfg.get('pit_membership_path'):
            raise ValueError('Point-in-time universe blocked: vetted membership and security identity evidence required')
        raise NotImplementedError('No vetted historical provider integrated. Do not bypass the gate with a config flag.')
    raise ValueError('Unknown universe mode')


def current_sp500(path='data/raw/probes/sp500_current.parquet'):
    df = pd.read_parquet(Path(path))
    if not {'Symbol', 'Security', 'CIK'}.issubset(df.columns) or df.Symbol.duplicated().any():
        raise ValueError('Invalid current roster')
    df['vendor_ticker'] = df.Symbol.str.replace('.', '-', regex=False)
    df['universe_label'] = PROTOTYPE_LABEL
    return df


def candidate_members_on(history, date):
    """Audit helper only: last recorded list <= date; never future backfill.

    Refuses extrapolation outside published coverage. This is NOT a certified PIT API.
    """
    dates = pd.to_datetime(history['date'])
    when = pd.Timestamp(date)
    if when < dates.min() or when > dates.max():
        raise ValueError('Outside candidate history coverage')
    eligible = history.loc[dates <= when].copy()
    eligible['_date'] = dates[dates <= when]
    row = eligible.sort_values('_date').iloc[-1]
    return set(str(row['tickers']).split(','))

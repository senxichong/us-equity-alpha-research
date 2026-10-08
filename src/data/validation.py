"""Record data anomalies without dropping, filling, winsorizing, or repairing."""
import numpy as np
import pandas as pd

REQUIRED = ['ticker', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']


def validate(df, tickers, sessions, extreme_threshold=0.4, ohlc_tolerance=1e-6):
    missing_columns = sorted(set(REQUIRED) - set(df.columns))
    if missing_columns:
        raise ValueError(f'Missing columns: {missing_columns}')
    df = df.copy()
    df = df.reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    numeric_original = df[REQUIRED[2:]].copy()
    df[REQUIRED[2:]] = df[REQUIRED[2:]].apply(pd.to_numeric, errors='coerce').astype(float)
    events = []

    def record(code, mask):
        for idx in df.index[mask]:
            row = df.loc[idx]
            events.append({'code': code, 'row': int(idx), 'ticker': str(row.ticker), 'date': str(row.date), 'values': {c: None if not np.isfinite(row[c]) else float(row[c]) for c in REQUIRED[2:]}})

    record('duplicate_ticker_date', df.duplicated(['ticker', 'date'], keep=False))
    record('invalid_date', df.date.isna())
    record('non_numeric_value', (numeric_original.notna() & df[REQUIRED[2:]].isna()).any(axis=1))
    price = df[['open', 'high', 'low', 'close', 'adj_close']]
    record('non_positive_price', (price <= 0).any(axis=1))
    record('non_finite_numeric', (~np.isfinite(df[REQUIRED[2:]]) & df[REQUIRED[2:]].notna()).any(axis=1))
    record('negative_volume', df.volume < 0)
    record('zero_volume', df.volume == 0)
    record('missing_required_value', df[REQUIRED].isna().any(axis=1))
    tol = df[['open', 'high', 'low', 'close']].abs().max(axis=1) * ohlc_tolerance
    bad = (df.high + tol < df[['open', 'close']].max(axis=1)) | (df.low - tol > df[['open', 'close']].min(axis=1)) | (df.high + tol < df.low)
    record('ohlc_violation', bad)
    sessions = pd.DatetimeIndex(sessions)
    record('non_session_date', df.date.notna() & ~df.date.isin(sessions))
    unsorted = [str(t) for t, g in df.groupby('ticker') if not g.date.is_monotonic_increasing]
    coverage = []
    for ticker in tickers:
        g = df.loc[df.ticker == ticker]
        dates = pd.DatetimeIndex(g.date.dropna().unique())
        missing = sessions.difference(dates)
        coverage.append({'ticker': ticker, 'rows': len(g), 'first_date': None if g.empty else str(g.date.min().date()), 'last_date': None if g.empty else str(g.date.max().date()), 'expected_sessions': len(sessions), 'observed_sessions': int(dates.isin(sessions).sum()), 'missing_sessions': len(missing), 'missing_dates': missing.strftime('%Y-%m-%d').tolist()})
    ordered = df.sort_values(['ticker', 'date'])
    change = ordered.groupby('ticker')['adj_close'].pct_change(fill_method=None)
    # This diagnostic is between observed rows, explicitly not a daily return if gaps exist.
    record('extreme_observed_adj_close_change', (change.abs() > extreme_threshold).reindex(df.index, fill_value=False))
    counts = pd.Series([e['code'] for e in events], dtype='object').value_counts().to_dict()
    return {'observations': len(df), 'stock_count': int(df.ticker.nunique()), 'missing_values': {k: int(v) for k, v in df[REQUIRED].isna().sum().items()}, 'duplicate_excess_rows': int(df.duplicated(['ticker', 'date']).sum()), 'unsorted_tickers': unsorted, 'unexpected_tickers': sorted(set(df.ticker) - set(tickers)), 'missing_tickers': sorted(set(tickers) - set(df.ticker)), 'issue_counts': {k: int(v) for k, v in counts.items()}, 'coverage': coverage, 'issues': events}

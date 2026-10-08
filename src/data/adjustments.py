"""Price transformations only. No factor research or portfolio calculation."""
import numpy as np
import pandas as pd


def adjusted_ohlc(df):
    result = df.copy()
    ratio = result['adj_close'] / result['close']
    if (~np.isfinite(ratio) | (ratio <= 0)).any():
        raise ValueError('Invalid adjustment factor; inspect validation report')
    result['adjustment_factor'] = ratio
    for col in ['open', 'high', 'low', 'close']:
        result[f'adjusted_{col}'] = result[col] * ratio
    return result


def split_adjust_as_traded(close, splits):
    """Synthetic/test utility: adjust truly as-traded prices to final share basis.

    splits[t] = new/old shares on ex-date t, zero means no split.
    Ex-date price is already on the new basis. NEVER apply to Yahoo Close.
    """
    if not close.index.equals(splits.index) or not close.index.is_monotonic_increasing or close.index.has_duplicates:
        raise ValueError('Aligned, sorted, unique index required')
    if splits.isna().any() or (splits < 0).any():
        raise ValueError('Invalid split event')
    ratios = splits.replace(0, 1)
    future_product = ratios.iloc[::-1].cumprod().iloc[::-1] / ratios
    return close / future_product


def session_returns(df, sessions, horizon=1, forward=False):
    """At date t: trailing P[t]/P[t-h]-1 or forward P[t+h]/P[t]-1.

    Reindex per ticker to the explicit trading calendar; never fill missing prices
    or interpret the next observed row as the next session. Uses adj_close only.
    """
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError('horizon must be a positive number of sessions')
    if df.duplicated(['ticker', 'date']).any():
        raise ValueError('Duplicate ticker-date')
    sessions = pd.DatetimeIndex(sessions)
    if sessions.has_duplicates or not sessions.is_monotonic_increasing:
        raise ValueError('Invalid calendar')
    if not pd.DatetimeIndex(df.date).isin(sessions).all():
        raise ValueError('Dates outside session calendar')
    parts = []
    for ticker, group in df.groupby('ticker', sort=True):
        p = group.set_index('date')['adj_close'].reindex(sessions)
        r = p.shift(-horizon) / p - 1 if forward else p / p.shift(horizon) - 1
        parts.append(pd.DataFrame({'ticker': ticker, 'date': sessions, 'return': r.to_numpy()}))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=['ticker', 'date', 'return'])


def corporate_action_checks(df, tolerance):
    def finite_or_none(value):
        return float(value) if pd.notna(value) and np.isfinite(value) else None

    split_rows, dividend_rows = [], []
    for ticker, g in df.groupby('ticker'):
        g = g.sort_values('date').copy()
        prior = g['close'].shift(1)
        factor = g['adj_close'] / g['close']
        # Yahoo back-adjustment convention: F[t-1]/F[t] ~ 1-D[t]/C[t-1].
        residual = factor.shift(1) / factor - (1 - g['dividends'] / prior)
        for idx, row in g.iterrows():
            base = {'ticker': ticker, 'date': str(row.date.date())}
            if pd.notna(row.stock_splits) and row.stock_splits != 0:
                split_rows.append(dict(base, ratio=float(row.stock_splits), close_return=finite_or_none(row.close / prior.loc[idx] - 1), adjusted_return=finite_or_none(row.adj_close / g.adj_close.shift(1).loc[idx] - 1)))
            if pd.notna(row.dividends) and row.dividends != 0:
                err = residual.loc[idx]
                dividend_rows.append(dict(base, dividend=float(row.dividends), factor_residual=None if pd.isna(err) else float(err), within_tolerance=None if pd.isna(err) else bool(abs(err) <= tolerance)))
    return {'split_events': split_rows, 'dividend_events': dividend_rows, 'dividend_tolerance': tolerance}

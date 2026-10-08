"""Conservative dataset admission and explicit missing-session rows; no factors."""
from __future__ import annotations

import json
from pathlib import Path

import exchange_calendars as xcals
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .download import normalize, sha256
from .incremental import BIAS
from .validation import validate

PRICE = ['open', 'high', 'low', 'close', 'adj_close']
RAW_FIELDS = PRICE + ['volume', 'dividends', 'stock_splits']
FATAL = ['duplicate_ticker_date', 'invalid_date', 'non_numeric_value', 'non_finite_numeric', 'non_positive_price', 'negative_volume', 'ohlc_violation', 'non_session_date', 'missing_required_value']


def complete_sessions(start, end, calendar='XNYS', now=None):
    if pd.Timestamp(end) <= pd.Timestamp(start):
        raise ValueError('Invalid date range')
    cal = xcals.get_calendar(calendar, start=start, end=end)
    now = pd.Timestamp.now(tz='UTC') if now is None else pd.Timestamp(now)
    if now.tzinfo is None:
        raise ValueError('now must include timezone')
    s = cal.schedule
    return s.index[(s.index >= pd.Timestamp(start)) & (s.index < pd.Timestamp(end)) & (s['close'] < now)]


def assess_stock(raw, ticker, meta, cfg, conventions, sessions):
    df = normalize(raw, ticker, conventions['exchange_timezone'])
    report = validate(df, [ticker], sessions, conventions['extreme_return_threshold'], conventions['ohlc_relative_tolerance'])
    reasons = [code for code in FATAL if report['issue_counts'].get(code, 0)]
    vendor = meta.get('vendor_metadata', {})
    if vendor.get('symbol') != ticker or vendor.get('instrumentType') != 'EQUITY' or vendor.get('currency') != 'USD':
        reasons.append('vendor_identity_or_instrument_mismatch')
    if report['unsorted_tickers']:
        reasons.append('date_order')
    if df.empty:
        reasons.append('empty')
        return None, {**BIAS, 'ticker': ticker, 'status': 'quarantined', 'reasons': reasons}, report
    ordered = df.sort_values('date').reset_index(drop=True)
    first, last = ordered.date.min(), ordered.date.max()
    active = sessions[sessions >= first]
    dates = pd.DatetimeIndex(ordered.date)
    valid_mask = ordered[PRICE + ['volume']].notna().all(axis=1) & (ordered.volume > 0)
    valid_dates = pd.DatetimeIndex(ordered.loc[valid_mask, 'date'])
    missing = active.difference(valid_dates)
    missing_rate = len(missing) / len(active) if len(active) else 1.0
    observed_missing_cells = int(ordered[RAW_FIELDS].isna().sum().sum())
    if missing_rate > cfg['max_active_missing_rate']:
        reasons.append('active_missing_rate')
    trailing_missing = int((sessions > last).sum())
    if trailing_missing > cfg['max_trailing_missing_sessions']:
        reasons.append('stale_history')
    if valid_mask.sum() < cfg['minimum_history_sessions']:
        reasons.append('short_history')
    listing = 'history_from_requested_start'
    first_trade = vendor.get('firstTradeDate')
    first_trade_date = pd.Timestamp(first_trade, unit='s', tz='UTC').tz_convert(conventions['exchange_timezone']).tz_localize(None).normalize() if first_trade else None
    if first > sessions[0]:
        listing = 'vendor_post_start_listing' if first_trade_date is not None and abs((first - first_trade_date).days) <= cfg['first_trade_grace_days'] else 'unexplained_late_history'
        if listing == 'unexplained_late_history':
            reasons.append(listing)
    extreme_count = report['issue_counts'].get('extreme_observed_adj_close_change', 0)
    if extreme_count and cfg['quarantine_extreme_changes']:
        reasons.append('unreviewed_extreme_change')
    if ticker in cfg['known_unresolved_tickers']:
        reasons.append('known_unresolved_cross_source_discrepancy')
    split = ordered.stock_splits
    nonzero = split.fillna(0) != 0
    ordinary = np.isclose(split, np.round(split), atol=1e-6) | np.isclose(1 / split.replace(0, np.nan), np.round(1 / split.replace(0, np.nan)), atol=1e-6)
    complex_count = int((nonzero & ~ordinary).sum())
    if complex_count and cfg['quarantine_complex_actions']:
        reasons.append('unverified_noninteger_distribution_event')
    if (ordered[['dividends', 'stock_splits']].isna().any().any() or (ordered.dividends < 0).any() or (split < 0).any()):
        reasons.append('invalid_corporate_action_fields')
    factor = ordered.adj_close / ordered.close
    residual = factor.shift(1) / factor - (1 - ordered.dividends / ordered.close.shift(1))
    dividends = ordered.dividends.fillna(0) != 0
    dividend_bad = dividends & (residual.isna() | (residual.abs() > conventions['dividend_factor_tolerance']))
    if dividend_bad.any():
        reasons.append('dividend_factor_mismatch')
    action_rows = []
    def finite_value(value):
        return float(value) if pd.notna(value) and np.isfinite(value) else None

    for i in ordered.index[dividends | nonzero]:
        row = ordered.loc[i]
        action_rows.append({'date': str(row.date.date()), 'dividend': finite_value(row.dividends), 'split_ratio_vendor': finite_value(row.stock_splits), 'complex_event': bool(nonzero.iloc[i] and not ordinary[i]), 'dividend_factor_residual': finite_value(residual.iloc[i])})
    window = sessions[-cfg['liquidity_window_sessions']:]
    recent = ordered[ordered.date.isin(window) & valid_mask]
    liquidity = float((recent.close * recent.volume).median()) if len(recent) else 0.0
    if not np.isfinite(liquidity):
        liquidity = 0.0
    liquidity_pass = len(recent) >= len(window) - cfg['max_trailing_missing_sessions'] and liquidity >= cfg['minimum_median_daily_dollar_volume']
    summary = {**BIAS, 'ticker': ticker, 'vendor_name': vendor.get('longName'), 'status': 'quarantined' if reasons else 'validated', 'reasons': sorted(set(reasons)), 'observations': len(ordered), 'valid_observations': int(valid_mask.sum()), 'first_date': str(first.date()), 'last_date': str(last.date()), 'requested_sessions': len(sessions), 'active_sessions': len(active), 'pre_history_sessions': int((sessions < first).sum()), 'calendar_coverage': len(valid_dates.intersection(sessions)) / len(sessions), 'active_coverage': 1 - missing_rate, 'active_missing_rate': missing_rate, 'active_missing_dates': missing.strftime('%Y-%m-%d').tolist(), 'missing_raw_cells': observed_missing_cells, 'raw_missing_rate': observed_missing_cells / (len(ordered) * len(RAW_FIELDS)), 'trailing_missing_sessions': trailing_missing, 'listing_classification': listing, 'vendor_first_trade_date': str(first_trade_date.date()) if first_trade_date is not None else None, 'extreme_change_count': extreme_count, 'split_event_count': int(nonzero.sum()), 'complex_action_count': complex_count, 'dividend_event_count': int(dividends.sum()), 'dividend_mismatch_count': int(dividend_bad.sum()), 'recent_median_daily_dollar_volume': liquidity, 'liquidity_pass': bool(liquidity_pass), 'liquidity_selection_as_of': str(sessions[-1].date()), 'actions': action_rows, 'snapshot_path': meta['snapshot_path'], 'snapshot_sha256': meta['snapshot_sha256']}
    if reasons:
        return None, summary, report
    # Dense only from first available history onward: never manufacture pre-IPO rows.
    aligned = ordered.set_index('date').reindex(active)
    aligned.index.name = 'date'
    aligned['ticker'] = ticker
    aligned['is_observed'] = aligned.index.isin(dates)
    aligned['is_valid_observation'] = aligned.index.isin(valid_dates)
    aligned['observation_status'] = np.where(~aligned.is_observed, 'missing_session', np.where(aligned.is_valid_observation, 'observed', 'zero_volume'))
    # Do not make invalid/zero-volume observations look tradable; raw values remain in cache.
    aligned.loc[~aligned.is_valid_observation, RAW_FIELDS] = np.nan
    ratio = aligned.adj_close / aligned.close
    aligned['adjustment_factor'] = ratio
    for column in ['open', 'high', 'low', 'close']:
        aligned[f'adjusted_{column}'] = aligned[column] * ratio
    aligned['available_history_observations'] = aligned.is_valid_observation.cumsum().astype('int32')
    aligned['has_minimum_history'] = aligned.available_history_observations >= cfg['minimum_history_sessions']
    aligned['survivorship_biased'] = True
    return aligned.reset_index(), summary, report


def write_panel_parquet(frame, path, metadata):
    table = pa.Table.from_pandas(frame, preserve_index=False)
    embedded = dict(table.schema.metadata or {})
    embedded[b'research_metadata'] = json.dumps({**BIAS, **metadata}, allow_nan=False).encode()
    pq.write_table(table.replace_schema_metadata(embedded), path, compression='zstd')


def load_research_panel(pointer='data/processed/phase2/research_panel.json'):
    meta = json.loads(Path(pointer).read_text())
    if sha256(meta['panel_path']) != meta['panel_sha256']:
        raise ValueError('Panel checksum mismatch')
    table = pq.read_table(meta['panel_path'])
    embedded = json.loads(table.schema.metadata[b'research_metadata'])
    if not meta['survivorship_biased'] or not embedded['survivorship_biased']:
        raise ValueError('Prototype bias metadata missing')
    return table.to_pandas(), meta

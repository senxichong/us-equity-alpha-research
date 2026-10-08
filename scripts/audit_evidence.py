"""Source comparison, membership audit and bounded repeatability checks."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import exchange_calendars as xcals
import numpy as np
import pandas as pd

from src.data.download import download_ticker, load_config, normalize, sha256
from src.data.universe import PROTOTYPE_LABEL, candidate_members_on, current_sp500
from src.data.validation import validate


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repeat-network', action='store_true', help='Explicit single AAPL repeat request; preserves prior snapshot')
    args = p.parse_args()
    cfg = load_config()
    evidence = {}
    h = pd.read_csv(ROOT / 'data/raw/probes/sp500_history.body')
    lists = h.tickers.str.split(',')
    counts = lists.map(len)
    current = current_sp500()
    last = set(lists.iloc[-1])
    today = set(current.Symbol)
    checks = []
    for day, ticker, expected in [('2020-12-18', 'TSLA', False), ('2020-12-21', 'TSLA', True), ('2022-06-08', 'FB', True), ('2022-06-09', 'META', True)]:
        found = ticker in candidate_members_on(h, day)
        checks.append(dict(date=day, ticker=ticker, expected=expected, observed=found, passed=found == expected))
    evidence['universe'] = {'current_roster_count': len(current), 'history_snapshot_rows': len(h), 'history_first': h.date.min(), 'history_last': h.date.max(), 'duplicate_dates': int(h.date.duplicated().sum()), 'dates_sorted': bool(pd.to_datetime(h.date).is_monotonic_increasing), 'min_members': int(counts.min()), 'max_members': int(counts.max()), 'rows_with_duplicate_symbols': int(lists.map(lambda x: len(x) != len(set(x))).sum()), 'latest_history_only': sorted(last - today), 'current_roster_only': sorted(today - last), 'spot_checks': checks, 'status': 'CANDIDATE ONLY - NOT VERIFIED POINT-IN-TIME', 'sha256': sha256(ROOT / 'data/raw/probes/sp500_history.body')}
    # A legally published demo dataset, not a general Alpha Vantage entitlement.
    av = json.loads((ROOT / 'data/raw/probes/alpha_vantage_full.body').read_text())
    av_raw = pd.DataFrame.from_dict(av['Time Series (Daily)'], orient='index')
    av_raw.index.name = 'vendor_date'
    av_path = ROOT / 'data/raw/sample/alpha_vantage_IBM_demo.parquet'
    if not av_path.exists():
        av_raw.to_parquet(av_path)
    av_df = av_raw.rename(columns={'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. adjusted close': 'adj_close', '6. volume': 'volume', '7. dividend amount': 'dividends', '8. split coefficient': 'stock_splits'}).apply(pd.to_numeric)
    av_df['date'] = pd.to_datetime(av_df.index)
    av_df['ticker'] = 'IBM'
    av_df = av_df.reset_index(drop=True)
    subset = av_df[(av_df.date >= cfg['start_date']) & (av_df.date < cfg['end_date'])].copy()
    sessions = xcals.get_calendar(cfg['calendar'], start=cfg['start_date'], end=cfg['end_date']).sessions
    sessions = sessions[sessions < pd.Timestamp(cfg['end_date'])]
    evidence['alpha_vantage'] = {'total_observations': len(av_df), 'first_date': str(av_df.date.min().date()), 'last_date': str(av_df.date.max().date()), 'sample_period_validation': validate(subset, ['IBM'], sessions, cfg['extreme_return_threshold'], cfg['ohlc_relative_tolerance'])}
    yahoo_ibm, ibm_meta = download_ticker('IBM', cfg)
    evidence['ibm_yahoo_download'] = ibm_meta
    if yahoo_ibm is not None:
        y = normalize(yahoo_ibm, 'IBM', cfg['exchange_timezone'])
        merged = subset.merge(y, on=['ticker', 'date'], suffixes=('_av', '_yahoo')).sort_values('date')
        av_return = merged.adj_close_av.pct_change(fill_method=None)
        y_return = merged.adj_close_yahoo.pct_change(fill_method=None)
        delta = (av_return - y_return).abs()
        mismatch = merged.loc[delta > .0001, ['date', 'close_av', 'close_yahoo', 'adj_close_av', 'adj_close_yahoo', 'dividends_av', 'dividends_yahoo']].copy()
        mismatch['av_return'] = av_return[delta > .0001]
        mismatch['yahoo_return'] = y_return[delta > .0001]
        mismatch['absolute_return_difference'] = delta[delta > .0001]
        mismatch['date'] = mismatch.date.dt.strftime('%Y-%m-%d')
        evidence['ibm_mismatch_details'] = mismatch.to_dict(orient='records')
        evidence['ibm_comparison'] = {'overlapping_dates': len(merged), 'adj_return_difference_max': float(delta.max()), 'adj_return_difference_median': float(delta.median()), 'dates_difference_above_1bp': merged.loc[delta > .0001, 'date'].dt.strftime('%Y-%m-%d').tolist(), 'close_level_ratio_min': float((merged.close_av / merged.close_yahoo).min()), 'close_level_ratio_max': float((merged.close_av / merged.close_yahoo).max()), 'note': 'Return comparison only; AV raw close and Yahoo split/distribution-adjusted close do not have identical semantics. No mixing of sources.'}
    old, old_meta = download_ticker('AAPL', cfg)
    if args.repeat_network:
        new, new_meta = download_ticker('AAPL', cfg, refresh=True)
        if new is not None and old is not None:
            numeric = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Dividends', 'Stock Splits']
            comparable = old.index.equals(new.index)
            evidence['repeatability'] = {'old_retrieved_at': old_meta['retrieved_at_utc'], 'new_retrieved_at': new_meta['retrieved_at_utc'], 'matching_index': comparable, 'rows': len(new), 'max_absolute_column_difference': {c: float((old[c] - new[c]).abs().max()) for c in numeric} if comparable else None, 'exact_table_equal': old.equals(new)}
    elif (ROOT / 'reports/source_audit.json').exists():
        evidence['repeatability'] = json.loads((ROOT / 'reports/source_audit.json').read_text()).get('repeatability')
    saved, cached_meta = download_ticker('AAPL', cfg)
    evidence['cache_check'] = {'hit': cached_meta['cache_hit'], 'rows': len(saved) if saved is not None else 0, 'hash_verified_by_adapter': saved is not None}
    m = json.loads((ROOT / 'reports/manifest.json').read_text())
    evidence['symbol_identity'] = [{'ticker': x['ticker'], 'status': x['status'], 'name': x.get('vendor_metadata', {}).get('longName'), 'instrument_type': x.get('vendor_metadata', {}).get('instrumentType'), 'rows': x.get('rows', 0)} for x in m['diagnostic_downloads']]
    actions = json.loads((ROOT / 'reports/corporate_actions.json').read_text())
    evidence['official_split_spot_checks'] = []
    for ticker, day, ratio, url in [('AAPL', '2020-08-31', 4, 'https://infomemo.theocc.com/infomemos?number=47370'), ('NVDA', '2024-06-10', 10, 'https://www.sec.gov/Archives/edgar/data/1045810/000104581024000144/nvda-20240607.htm')]:
        match = [x for x in actions['split_events'] if x['ticker'] == ticker and x['date'] == day]
        evidence['official_split_spot_checks'].append({'ticker': ticker, 'date': day, 'expected_ratio': ratio, 'vendor_event': match, 'passed': len(match) == 1 and match[0]['ratio'] == ratio, 'reference': url})
    (ROOT / 'reports/source_audit.json').write_text(json.dumps(evidence, indent=2, allow_nan=False), encoding='utf-8')
    lines = ['# Source and universe evidence audit', '', PROTOTYPE_LABEL, '', 'All numeric results below are generated from cached responses or explicit requests.', '', '## Historical membership candidate', '', '```json', json.dumps(evidence['universe'], indent=2), '```', '', 'TSLA effective date reference: https://press.spglobal.com/2020-11-30-S-P-Dow-Jones-Indices-Announces-Implementation-of-Teslas-Addition-to-S-P-500', 'META symbol reference: https://www.sec.gov/Archives/edgar/data/1326801/000132680122000070/may312022-exhibit991.htm', '', 'Even passing spot checks cannot establish exhaustive historical membership, announcement availability, security identity or delisting coverage. Latest candidate coverage ends before the requested endpoint. Mode B remains blocked.', '', '## IBM cross-provider comparison', '', '```json', json.dumps(evidence.get('ibm_comparison', {}), indent=2), '```', '', '## Download repeatability and cache', '', '```json', json.dumps({'repeatability': evidence.get('repeatability'), 'cache': evidence['cache_check']}, indent=2), '```', '', '## Symbol identity', '', '```json', json.dumps(evidence['symbol_identity'], indent=2), '```', '', 'A current vendor symbol can identify a different security. FB is quarantined as a diagnostic and never merged into META.', '', 'Full Alpha Vantage validation, immutable hashes, and official split spot checks: source_audit.json.']
    (ROOT / 'reports/source_audit.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in evidence.items() if k not in ['alpha_vantage', 'ibm_yahoo_download']}, indent=2))


if __name__ == '__main__':
    main()

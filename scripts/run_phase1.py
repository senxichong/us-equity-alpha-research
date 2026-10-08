"""Download a stress sample and emit reproducible data-only diagnostics."""
import argparse
import json
import sys
import time
from datetime import timedelta
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import exchange_calendars as xcals
import pandas as pd
import yaml

from src.data.adjustments import adjusted_ohlc, corporate_action_checks
from src.data.download import download_ticker, load_config, normalize, sha256
from src.data.validation import REQUIRED, validate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--refresh', action='store_true', help='Create NEW snapshots, retaining old files')
    args = parser.parse_args()
    cfg = load_config(args.config)
    # Fail closed if the configured universe is not available/verified.
    from src.data.universe import universe_label
    label = universe_label(cfg)
    now = pd.Timestamp.now(tz='UTC')
    calendar = xcals.get_calendar(cfg['calendar'], start=cfg['start_date'], end=cfg['end_date'])
    schedule = calendar.schedule
    sessions = schedule.index[(schedule.index >= pd.Timestamp(cfg['start_date'])) & (schedule.index < pd.Timestamp(cfg['end_date'])) & (schedule['close'] < now)]
    if sessions.empty:
        raise ValueError('No complete sessions')
    # Request only complete sessions, and retain resolved request in run manifest.
    effective = dict(cfg, end_date=str(sessions[-1].date() + timedelta(days=1)))
    frames, downloads, diagnostics = [], [], []
    circuit_open = False
    for ticker in cfg['tickers'] + cfg['diagnostic_tickers']:
        if circuit_open:
            raw, meta = None, {'status': 'skipped_rate_limit', 'attempts': [], 'cache_hit': False}
        else:
            raw, meta = download_ticker(ticker, effective, refresh=args.refresh)
        if meta.get('http_status') == 429 or any('RateLimit' in a.get('error', '') for a in meta['attempts']):
            circuit_open = True
        meta['ticker'] = ticker
        is_sample = ticker in cfg['tickers']
        (downloads if is_sample else diagnostics).append(meta)
        if raw is not None and is_sample:
            frames.append(normalize(raw, ticker, cfg['exchange_timezone']))
        print(f"{ticker}: {meta['status']}, rows={meta.get('rows', 0)}, cache={meta['cache_hit']}", flush=True)
        if not meta['cache_hit']:
            time.sleep(cfg['request_pause_seconds'])
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=REQUIRED + ['dividends', 'stock_splits'])
    validation = validate(df, cfg['tickers'], sessions, cfg['extreme_return_threshold'], cfg['ohlc_relative_tolerance'])
    actions = corporate_action_checks(df, cfg['dividend_factor_tolerance'])
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run_dir = ROOT / 'reports/runs' / stamp
    run_dir.mkdir(parents=True)
    processed = ROOT / cfg['processed_directory'] / stamp
    processed.mkdir(parents=True)
    df.to_parquet(processed / 'sample_normalized.parquet', index=False)
    # Derived prices only if required price fields are valid; anomalies are never removed.
    if not df.empty and not df[['open', 'high', 'low', 'close', 'adj_close']].isna().any().any() and not any(validation['issue_counts'].get(x, 0) for x in ['non_positive_price', 'non_finite_numeric', 'duplicate_ticker_date']):
        adjusted_ohlc(df).to_parquet(processed / 'sample_adjusted.parquet', index=False)
    manifest = {'created_at_utc': datetime.now(timezone.utc).isoformat(), 'config': cfg, 'effective_request': effective, 'universe_label': label, 'sample_type': 'Deliberate stress sample; not the full index universe', 'last_complete_requested_session': str(sessions[-1].date()), 'downloads': downloads, 'diagnostic_downloads': diagnostics, 'processed_directory': str(processed.relative_to(ROOT)), 'run_directory': str(run_dir.relative_to(ROOT))}
    code_files = sorted([*ROOT.glob('src/**/*.py'), *ROOT.glob('scripts/*.py'), ROOT / 'requirements-lock.txt'])
    manifest['code_and_environment_sha256'] = {str(p.relative_to(ROOT)): sha256(p) for p in code_files}
    manifest['processed_sha256'] = {str(p.relative_to(ROOT)): sha256(p) for p in processed.glob('*.parquet')}
    for name, obj in [('manifest', manifest), ('validation', validation), ('corporate_actions', actions)]:
        content = json.dumps(obj, indent=2, allow_nan=False)
        (run_dir / f'{name}.json').write_text(content, encoding='utf-8')
        (ROOT / 'reports' / f'{name}.json').write_text(content, encoding='utf-8')
    (run_dir / 'config.yaml').write_text(yaml.safe_dump(cfg, sort_keys=False), encoding='utf-8')
    failed = [x['ticker'] for x in downloads if x['status'] != 'ok']
    lines = ['# Sample data quality report', '', label, '', f"Generated UTC: {manifest['created_at_utc']}", '', f"Source: {cfg['data_source']}; vendor fields retained without repair or automatic adjustment.", f"Requested [{cfg['start_date']}, {effective['end_date']}); last complete expected session: {sessions[-1].date()}.", f"Successful sample stocks: {validation['stock_count']} / {len(cfg['tickers'])}; observations: {len(df)}.", f"Failed sample tickers: {failed}", f"Missing values: {validation['missing_values']}", f"Issue counts: {validation['issue_counts']}; duplicate excess rows: {validation['duplicate_excess_rows']}.", f"Unsorted tickers: {validation['unsorted_tickers']}", '', '|Ticker|Rows|First|Last|Missing expected sessions|', '|---|---:|---|---|---:|']
    for c in validation['coverage']:
        lines.append(f"|{c['ticker']}|{c['rows']}|{c['first_date']}|{c['last_date']}|{c['missing_sessions']}|")
    lines += ['', 'Coverage compares the full requested calendar. Missing dates are observations to investigate, not automatically vendor errors (listing history/halts may matter). No rows were dropped or filled.', '', f"Split events: {len(actions['split_events'])}; dividend events: {len(actions['dividend_events'])}.", f"Dividend factor checks outside tolerance: {sum(x['within_tolerance'] is False for x in actions['dividend_events'])}.", '', '|Ticker|Split date|New/old shares|Close change|Adjusted close change|', '|---|---|---:|---:|---:|']
    for e in actions['split_events']:
        cr = 'unavailable' if e['close_return'] is None else f"{e['close_return']:.6f}"
        ar = 'unavailable' if e['adjusted_return'] is None else f"{e['adjusted_return']:.6f}"
        lines.append(f"|{e['ticker']}|{e['date']}|{e['ratio']}|{cr}|{ar}|")
    lines += ['', '## Symbol / delisting probes', '']
    for d in diagnostics:
        lines.append(f"- {d['ticker']}: {d['status']}; {d.get('rows', 0)} rows; {d.get('first_timestamp', '')} to {d.get('last_timestamp', '')}. Identity: {d.get('vendor_metadata', {}).get('longName', 'unavailable')} / {d.get('vendor_metadata', {}).get('instrumentType', 'unavailable')}. Errors: {[a.get('error') for a in d['attempts'] if not a['ok']]}")
    lines += ['', '## Interpretation and limitations', '', 'Corporate-action checks test vendor consistency, not an independently audited corporate-action ledger. Yahoo Close is split-adjusted, not an as-traded execution price. Current snapshots can be revised. Extreme observed price changes are flags, not proof of bad data. Symbol identity, delisting proceeds, spin-offs, and reliable historical membership remain unresolved. See DATA_CONVENTIONS.md and DATA_LIMITATIONS.md.', '', f"Full machine-readable evidence: {manifest['run_directory']}; normalized data: {manifest['processed_directory']}."]
    report = '\n'.join(lines) + '\n'
    (run_dir / 'data_quality_report.md').write_text(report, encoding='utf-8')
    (ROOT / 'reports/data_quality_report.md').write_text(report, encoding='utf-8')
    print(json.dumps({'stocks': validation['stock_count'], 'rows': len(df), 'issues': validation['issue_counts'], 'failures': failed, 'run': str(run_dir)}, indent=2))


if __name__ == '__main__':
    main()

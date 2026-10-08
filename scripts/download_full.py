"""Resumable paced batch; freezes Phase 1 roster rather than refreshing membership."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.download import load_config, sha256
from src.data.incremental import BIAS, SnapshotStore, stamp, write_json
from src.data.universe import current_sp500
from src.data.panel import complete_sessions
from datetime import timedelta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers', nargs='+')
    parser.add_argument('--end')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--retry-failed', action='store_true')
    args = parser.parse_args()
    config = load_config()
    cfg = config['phase2']
    if config['universe_mode'] != 'prototype_current_sp500' or cfg['survivorship_biased'] is not True:
        raise ValueError('Phase 2 currently supports explicitly biased prototype only')
    roster = current_sp500(cfg['roster_path'])
    tickers = args.tickers or sorted(roster.vendor_ticker)
    if not set(tickers).issubset(set(roster.vendor_ticker)):
        raise ValueError('Ticker outside frozen roster')
    requested_end = args.end or cfg['end_date']
    sessions = complete_sessions(cfg['start_date'], requested_end, config['calendar'])
    if sessions.empty:
        raise ValueError('No completed sessions')
    end = str(sessions[-1].date() + timedelta(days=1))
    store = SnapshotStore(cfg)
    run = {**BIAS, 'config': config, 'requested_end': requested_end, 'end': end, 'roster_sha256': sha256(cfg['roster_path']), 'tickers': tickers, 'downloads': []}
    path = ROOT / 'reports/phase2/downloads' / f'{stamp()}.json'
    for i, ticker in enumerate(tickers):
        if store.rate_limited:
            run['downloads'].append({**BIAS, 'ticker': ticker, 'status': 'skipped_rate_limit'})
            continue
        try:
            raw, meta = store.update(ticker, cfg['start_date'], end, refresh=args.refresh, retry_failed=args.retry_failed)
        except Exception as exc:
            meta = {**BIAS, 'ticker': ticker, 'status': 'error', 'error': str(exc)}
        run['downloads'].append(meta)
        run['network_requests'] = store.network_requests
        write_json(path, run)  # recoverable manifest if interrupted
        print(f"{i+1}/{len(tickers)} {ticker}: {meta['status']} rows={meta.get('rows', 0)} mode={meta.get('update_mode', '')} cached={meta.get('cache_hit', False)}", flush=True)
    write_json(path, run)
    write_json(ROOT / 'reports/phase2/latest_download.json', run)
    print(f'Manifest: {path}', flush=True)


if __name__ == '__main__':
    main()

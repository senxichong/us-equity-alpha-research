"""Immutable vendor snapshots, explicit request settings, bounded retries."""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml
import yfinance as yf
import requests


def load_config(path='config.yaml'):
    cfg = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if cfg['data_source'] not in {'yahoo_yfinance', 'yahoo_chart'}:
        raise ValueError('Only audited Yahoo adapter is implemented; probes are not production adapters.')
    if cfg['adjustment_method'] != 'vendor_adj_close_ratio':
        raise ValueError('Unsupported adjustment convention')
    if pd.Timestamp(cfg['end_date']) <= pd.Timestamp(cfg['start_date']):
        raise ValueError('end_date must be after start_date')
    return cfg


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def download_ticker(ticker, cfg, refresh=False, fetcher=None):
    if cfg['data_source'] == 'yahoo_chart':
        return download_chart(ticker, cfg, refresh=refresh)
    request = dict(ticker=ticker, start=cfg['start_date'], end=cfg['end_date'], interval='1d', auto_adjust=False, back_adjust=False, repair=False, actions=True, keepna=True, prepost=False, rounding=False)
    key = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:16]
    folder = Path(cfg['cache_directory']) / ticker / key
    folder.mkdir(parents=True, exist_ok=True)
    existing = sorted(folder.glob('*.json'))
    if existing and not refresh:
        meta = json.loads(existing[-1].read_text(encoding='utf-8'))
        if meta['status'] == 'ok':
            path = folder / meta['file']
            if sha256(path) != meta['sha256']:
                raise ValueError(f'Cache checksum mismatch: {path}')
            return pd.read_parquet(path), dict(meta, cache_hit=True)
        # Negative cache: explicit --refresh is required to retry failed requests.
        return None, dict(meta, cache_hit=True)
    meta = {'request': request, 'source': 'Yahoo Finance via yfinance', 'yfinance_version': yf.__version__, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'attempts': [], 'status': 'failed'}
    raw = None
    for attempt in range(cfg['max_attempts']):
        started = time.monotonic()
        try:
            getter = fetcher or yf.Ticker(ticker).history
            raw = getter(**{k: v for k, v in request.items() if k != 'ticker'}, timeout=cfg['request_timeout_seconds'], raise_errors=True)
            if raw is None or raw.empty:
                raise ValueError('Empty vendor response')
            if not {'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'}.issubset(raw.columns):
                raise ValueError(f'Incomplete schema: {list(raw.columns)}')
            meta['attempts'].append({'attempt': attempt + 1, 'ok': True, 'seconds': round(time.monotonic() - started, 3)})
            meta['status'] = 'ok'
            break
        except Exception as exc:
            raw = None
            meta['attempts'].append({'attempt': attempt + 1, 'ok': False, 'error': f'{type(exc).__name__}: {exc}', 'seconds': round(time.monotonic() - started, 3)})
            if 'RateLimit' in type(exc).__name__ or '429' in str(exc):
                break  # Never probe a quota by hammering the provider.
            if attempt + 1 < cfg['max_attempts']:
                time.sleep(cfg['request_pause_seconds'] * (attempt + 1))
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    if raw is not None:
        path = folder / f'{stamp}.parquet'
        raw.to_parquet(path)  # Vendor table unchanged, timezone index retained.
        meta.update(file=path.name, sha256=sha256(path), rows=len(raw), first_timestamp=str(raw.index.min()), last_timestamp=str(raw.index.max()), timezone=str(raw.index.tz), columns=list(raw.columns))
    (folder / f'{stamp}.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    return raw, dict(meta, cache_hit=False)


def parse_chart(payload):
    chart = payload['chart']
    if chart.get('error'):
        raise ValueError(str(chart['error']))
    result = chart['result'][0]
    if result['meta'].get('currency') != 'USD':
        raise ValueError('Expected USD sample prices')
    tz = result['meta']['exchangeTimezoneName']
    timestamps = pd.to_datetime(result['timestamp'], unit='s', utc=True).tz_convert(tz)
    q = result['indicators']['quote'][0]
    df = pd.DataFrame(q, index=timestamps).rename(columns=str.title)
    df['Adj Close'] = result['indicators']['adjclose'][0]['adjclose']
    df.index.name = 'Date'
    local_dates = df.index.tz_localize(None).normalize()
    for event_type, column in [('dividends', 'Dividends'), ('splits', 'Stock Splits')]:
        df[column] = 0.0
        seen = set()
        for event in result.get('events', {}).get(event_type, {}).values():
            date = pd.Timestamp(event['date'], unit='s', tz='UTC').tz_convert(tz).tz_localize(None).normalize()
            if date in seen or (local_dates == date).sum() != 1:
                raise ValueError(f'Ambiguous or unmatched {event_type} event on {date}')
            seen.add(date)
            value = event['amount'] if event_type == 'dividends' else event['numerator'] / event['denominator']
            df.loc[local_dates == date, column] = value
    return df


def download_chart(ticker, cfg, refresh=False):
    """Standard public HTTP endpoint; no auth bypass or cookie emulation.

    Save original JSON before parsing. Retain error responses as evidence too.
    One attempt only; caller stops further network requests on HTTP 429.
    """
    params = {'period1': int(pd.Timestamp(cfg['start_date'], tz='UTC').timestamp()), 'period2': int(pd.Timestamp(cfg['end_date'], tz='UTC').timestamp()), 'interval': '1d', 'events': 'div,splits'}
    request = {'source': 'yahoo_chart', 'ticker': ticker, **params}
    key = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:16]
    folder = Path(cfg['cache_directory']) / ticker / key
    folder.mkdir(parents=True, exist_ok=True)
    existing = sorted(folder.glob('*.metadata.json'))
    if existing and not refresh:
        meta = json.loads(existing[-1].read_text(encoding='utf-8'))
        if meta['status'] == 'ok':
            for filename, digest in [(meta['file'], meta['sha256']), (meta['response_file'], meta['response_sha256'])]:
                if sha256(folder / filename) != digest:
                    raise ValueError(f'Cache checksum mismatch: {folder / filename}')
            return pd.read_parquet(folder / meta['file']), dict(meta, cache_hit=True)
        return None, dict(meta, cache_hit=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    meta = {'request': request, 'source': 'Yahoo Finance public chart endpoint (requests)', 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'status': 'failed', 'attempts': []}
    raw = None
    started = time.monotonic()
    try:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
        response = requests.get(url, params=params, headers={'User-Agent': 'us-equity-alpha-research/0.1 personal research'}, timeout=cfg['request_timeout_seconds'])
        body = folder / f'{stamp}.response.json'
        body.write_bytes(response.content)
        meta.update(http_status=response.status_code, url=response.url, response_file=body.name, response_sha256=sha256(body))
        response.raise_for_status()
        payload = response.json()
        raw = parse_chart(payload)
        if raw.empty:
            raise ValueError('Empty vendor response')
        path = folder / f'{stamp}.parquet'
        raw.to_parquet(path)
        meta.update(status='ok', file=path.name, sha256=sha256(path), rows=len(raw), first_timestamp=str(raw.index.min()), last_timestamp=str(raw.index.max()), timezone=str(raw.index.tz), columns=list(raw.columns), vendor_metadata=payload['chart']['result'][0]['meta'])
        meta['attempts'].append({'attempt': 1, 'ok': True, 'seconds': round(time.monotonic() - started, 3)})
    except Exception as exc:
        raw = None
        meta['attempts'].append({'attempt': 1, 'ok': False, 'error': f'{type(exc).__name__}: {exc}', 'seconds': round(time.monotonic() - started, 3)})
    (folder / f'{stamp}.metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    return raw, dict(meta, cache_hit=False)


def normalize(raw, ticker, exchange_timezone):
    if raw.index.tz is None:
        raise ValueError('Vendor timezone missing; refusing to assume UTC')
    df = raw.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close', 'Volume': 'volume', 'Dividends': 'dividends', 'Stock Splits': 'stock_splits'}).copy()
    df.insert(0, 'date', raw.index.tz_convert(exchange_timezone).tz_localize(None).normalize())
    df.insert(0, 'ticker', ticker)
    return df.reset_index(drop=True)

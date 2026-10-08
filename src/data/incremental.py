"""Resumable snapshots with bounded retries and adjustment-safe incremental updates."""
from __future__ import annotations

import json
import time
from copy import deepcopy
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from .download import parse_chart, sha256

BIAS = {'survivorship_biased': True, 'universe_mode': 'prototype_current_sp500', 'security_identity_verified': False}


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False), encoding='utf-8')


def stamp():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')


def retry_delay(header, attempt, cfg):
    base = cfg['retry_base_seconds'] * 2 ** attempt
    if header:
        try:
            base = max(base, float(header))
        except ValueError:
            try:
                base = max(base, (parsedate_to_datetime(header) - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError):
                pass
    return max(0, base)


def needs_rebase(old, incoming, tolerance):
    """Do not splice a new corporate-action basis onto stale price history."""
    if old.index.tz is None or incoming.index.tz is None:
        raise ValueError('Timezone required')
    left, right = old.copy(), incoming.copy()
    left.index = left.index.tz_localize(None).normalize()
    right.index = right.index.tz_localize(None).normalize()
    if left.index.has_duplicates or right.index.has_duplicates:
        raise ValueError('Duplicate dates in incremental source')
    common = left.index.intersection(right.index)
    if common.empty:
        return True
    columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Dividends', 'Stock Splits']
    if not np.allclose(left.loc[common, columns], right.loc[common, columns], rtol=tolerance, atol=1e-8, equal_nan=True):
        return True
    new = right.loc[right.index > left.index.max()]
    return bool((new[['Dividends', 'Stock Splits']].fillna(0) != 0).any().any())


def merge_increment(old, incoming):
    """Replace overlap explicitly, never collapse duplicates within an input."""
    keys = lambda df: df.index.tz_localize(None).normalize()
    if keys(old).has_duplicates or keys(incoming).has_duplicates:
        raise ValueError('Duplicate dates in incremental source')
    result = pd.concat([old.loc[~keys(old).isin(keys(incoming))], incoming]).sort_index()
    return result


def parse_requested_chart(payload, start, end):
    """Vendor sometimes includes pre-request actions; preserve and disclose these.

    Only events outside the explicit request interval are omitted from the table.
    Unmatched events INSIDE the interval still fail closed, including holidays.
    Original response bytes always retain every event.
    """
    clean = deepcopy(payload)
    omitted = []
    results = clean.get('chart', {}).get('result')
    if results:
        result = results[0]
        tz = result['meta']['exchangeTimezoneName']
        for kind, events in result.get('events', {}).items():
            for key, event in list(events.items()):
                day = pd.Timestamp(event['date'], unit='s', tz='UTC').tz_convert(tz).tz_localize(None).normalize()
                if day < pd.Timestamp(start) or day >= pd.Timestamp(end):
                    omitted.append({'type': kind, 'date': str(day.date()), 'event': event, 'reason': 'outside_requested_interval'})
                    del events[key]
    return parse_chart(clean), omitted


class SnapshotStore:
    def __init__(self, cfg, get=None, sleep=None):
        self.cfg = cfg
        self.root = Path(cfg['raw_directory'])
        self.root.mkdir(parents=True, exist_ok=True)
        self.get = get or requests.Session().get
        self.sleep = sleep or time.sleep
        self.rate_limited = False
        self.network_requests = 0

    def fetch(self, ticker, start, end):
        folder = self.root / ticker / 'responses'
        folder.mkdir(parents=True, exist_ok=True)
        params = {'period1': int(pd.Timestamp(start, tz='UTC').timestamp()), 'period2': int(pd.Timestamp(end, tz='UTC').timestamp()), 'interval': '1d', 'events': 'div,splits'}
        attempts = []
        for attempt in range(self.cfg['max_attempts']):
            token = stamp()
            meta = {**BIAS, 'ticker': ticker, 'start': start, 'end': end, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'attempt': attempt + 1, 'status': 'failed'}
            raw, vendor = None, None
            retryable = False
            delay = self.cfg['retry_base_seconds'] * 2 ** attempt
            try:
                self.sleep(self.cfg['request_pause_seconds'])
                self.network_requests += 1
                response = self.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}', params=params, headers={'User-Agent': 'us-equity-alpha-research/0.2 personal research'}, timeout=self.cfg['request_timeout_seconds'])
                body = folder / f'{token}.response.json'
                body.write_bytes(response.content)
                meta.update(http_status=response.status_code, response_path=str(body), response_sha256=sha256(body))
                retryable = response.status_code == 429 or response.status_code >= 500
                if response.status_code == 429:
                    delay = retry_delay(response.headers.get('Retry-After'), attempt, self.cfg)
                    self.rate_limited = True
                response.raise_for_status()
                payload = response.json()
                raw, omitted = parse_requested_chart(payload, start, end)
                vendor = payload['chart']['result'][0]['meta']
                if raw.empty:
                    raise ValueError('Empty prices')
                raw_path = folder / f'{token}.parquet'
                raw.to_parquet(raw_path)
                meta.update(status='ok', raw_path=str(raw_path), raw_sha256=sha256(raw_path), vendor_metadata=vendor, events_outside_requested_interval=omitted)
                self.rate_limited = False
            except (requests.Timeout, requests.ConnectionError) as exc:
                retryable = True
                meta['error'] = f'{type(exc).__name__}: {exc}'
            except Exception as exc:
                meta['error'] = f'{type(exc).__name__}: {exc}'
                raw = None
            write_json(folder / f'{token}.metadata.json', meta)
            attempts.append(meta)
            if meta['status'] == 'ok':
                return raw, vendor, attempts
            if not retryable or attempt + 1 == self.cfg['max_attempts']:
                break
            if self.rate_limited and delay > self.cfg['max_rate_limit_wait_seconds']:
                break  # Honor Retry-After by stopping, never by retrying sooner.
            self.sleep(delay)
        return None, None, attempts

    def update(self, ticker, start, end, refresh=False, retry_failed=False):
        folder = self.root / ticker
        state_path = folder / 'state.json'
        failure_path = folder / 'last_failure.json'
        previous, old = None, None
        if state_path.exists():
            previous = json.loads(state_path.read_text())
            if sha256(previous['snapshot_path']) != previous['snapshot_sha256']:
                raise ValueError(f'Corrupt snapshot for {ticker}')
            old = pd.read_parquet(previous['snapshot_path'])
            if previous['start'] <= start and previous['end'] >= end and not refresh:
                return old, {**previous, 'cache_hit': True, 'update_mode': 'cache'}
        if failure_path.exists() and not (refresh or retry_failed):
            failure = json.loads(failure_path.read_text())
            if failure['start'] == start and failure['end'] == end:
                return None, {**failure, 'cache_hit': True}
        mode, request_start = 'full', start
        if old is not None and not refresh and previous['start'] <= start:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(previous['last_full_refresh_utc'])).days
            if age < self.cfg['full_refresh_after_days']:
                request_start = max(start, str((old.index.max().tz_localize(None) - pd.Timedelta(days=self.cfg['overlap_calendar_days'])).date()))
                mode = 'incremental'
        incoming, vendor, attempts = self.fetch(ticker, request_start, end)
        if incoming is not None and mode == 'incremental' and needs_rebase(old, incoming, self.cfg['revision_relative_tolerance']):
            mode = 'full_rebase'
            incoming, vendor, more = self.fetch(ticker, start, end)
            attempts += more
        if incoming is None:
            failure = {**BIAS, 'ticker': ticker, 'start': start, 'end': end, 'status': 'failed', 'attempts': attempts, 'rate_limited': self.rate_limited, 'cache_hit': False}
            write_json(failure_path, failure)
            return None, failure
        result = merge_increment(old, incoming) if mode == 'incremental' else incoming
        token = stamp()
        snapshot = folder / f'{token}.parquet'
        result.to_parquet(snapshot)
        now = datetime.now(timezone.utc).isoformat()
        meta = {**BIAS, 'ticker': ticker, 'start': start, 'end': end, 'status': 'ok', 'source': 'yahoo_chart', 'cache_hit': False, 'update_mode': mode, 'snapshot_path': str(snapshot), 'snapshot_sha256': sha256(snapshot), 'rows': len(result), 'retrieved_at_utc': now, 'last_full_refresh_utc': previous['last_full_refresh_utc'] if mode == 'incremental' else now, 'vendor_metadata': vendor, 'attempts': attempts, 'parent_snapshot': previous['snapshot_path'] if previous else None}
        write_json(folder / f'{token}.metadata.json', meta)
        # Only a small pointer is replaced; every response and snapshot remains immutable.
        temporary = folder / 'state.tmp'
        write_json(temporary, meta)
        temporary.replace(state_path)
        return result, meta

import json
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest
import requests
import yaml

from src.data.incremental import SnapshotStore, merge_increment, needs_rebase
from src.data.incremental import parse_requested_chart
from src.data.panel import RAW_FIELDS, assess_stock, complete_sessions, load_research_panel, write_panel_parquet
from src.data.download import sha256


@pytest.fixture
def setup_data(tmp_path):
    config = yaml.safe_load(open('config.yaml', encoding='utf-8'))
    cfg = deepcopy(config['phase2'])
    cfg.update(raw_directory=str(tmp_path), minimum_history_sessions=3, liquidity_window_sessions=3, minimum_median_daily_dollar_volume=1, max_active_missing_rate=.3, request_pause_seconds=0, retry_base_seconds=0)
    sessions = pd.bdate_range('2024-01-02', periods=6)
    idx = sessions.tz_localize('America/New_York') + pd.Timedelta(hours=9, minutes=30)
    raw = pd.DataFrame({'Open': 100., 'High': 102., 'Low': 98., 'Close': 100., 'Adj Close': 95., 'Volume': 1e6, 'Dividends': 0., 'Stock Splits': 0.}, index=idx)
    raw.index.name = 'Date'
    meta = {'vendor_metadata': {'symbol': 'AAA', 'instrumentType': 'EQUITY', 'currency': 'USD', 'firstTradeDate': int(idx[0].timestamp())}, 'snapshot_path': 'toy.parquet', 'snapshot_sha256': 'test'}
    return raw, meta, cfg, config, sessions


def test_admission_and_gap_never_filled(setup_data):
    raw, meta, cfg, config, sessions = setup_data
    frame, summary, _ = assess_stock(raw.drop(raw.index[2]), 'AAA', meta, cfg, config, sessions)
    assert summary['status'] == 'validated'
    assert len(frame) == len(sessions)
    gap = frame.loc[frame.date == sessions[2]].iloc[0]
    assert not gap.is_observed and not gap.is_valid_observation
    assert gap[RAW_FIELDS].isna().all()
    assert frame.available_history_observations.tolist() == [1, 2, 2, 3, 4, 5]
    assert frame.has_minimum_history.tolist() == [False, False, False, True, True, True]


def test_ipo_no_prehistory_fabrication(setup_data):
    raw, meta, cfg, config, sessions = setup_data
    raw = raw.iloc[2:]
    meta['vendor_metadata']['firstTradeDate'] = int(raw.index[0].timestamp())
    frame, summary, _ = assess_stock(raw, 'AAA', meta, cfg, config, sessions)
    assert len(frame) == 4
    assert summary['pre_history_sessions'] == 2
    assert summary['listing_classification'] == 'vendor_post_start_listing'
    assert summary['active_coverage'] == 1
    short, quality, _ = assess_stock(raw.iloc[-2:], 'AAA', meta, cfg, config, sessions)
    assert short is None and 'short_history' in quality['reasons']


@pytest.mark.parametrize('defect', ['duplicate', 'ohlc', 'identity', 'complex', 'extreme', 'dividend'])
def test_rejected_stock_never_enters_panel(setup_data, defect):
    raw, meta, cfg, config, sessions = setup_data
    if defect == 'duplicate':
        raw = pd.concat([raw, raw.iloc[[0]]])
    if defect == 'ohlc':
        raw.iloc[0, raw.columns.get_loc('High')] = 90
    if defect == 'identity':
        meta['vendor_metadata']['instrumentType'] = 'ETF'
    if defect == 'complex':
        raw.iloc[2, raw.columns.get_loc('Stock Splits')] = 1.04
    if defect == 'extreme':
        raw.iloc[2, raw.columns.get_loc('Adj Close')] = 200
    if defect == 'dividend':
        raw.iloc[2, raw.columns.get_loc('Dividends')] = 10
    frame, summary, _ = assess_stock(raw, 'AAA', meta, cfg, config, sessions)
    assert frame is None
    assert summary['status'] == 'quarantined' and summary['reasons']


def test_zero_volume_not_a_real_trade(setup_data):
    raw, meta, cfg, config, sessions = setup_data
    raw.iloc[1, raw.columns.get_loc('Volume')] = 0
    frame, summary, _ = assess_stock(raw, 'AAA', meta, cfg, config, sessions)
    assert frame.iloc[1].is_observed and not frame.iloc[1].is_valid_observation
    assert frame.iloc[1][RAW_FIELDS].isna().all()


def test_overlap_revisions_and_new_actions_require_full_rebase(setup_data):
    raw, *_ = setup_data
    old, new = raw.iloc[:4], raw.iloc[2:]
    assert not needs_rebase(old, new, 5e-6)
    revised = new.copy()
    revised['Adj Close'] *= .98
    assert needs_rebase(old, revised, 5e-6)
    dividend = new.copy()
    dividend.iloc[-1, dividend.columns.get_loc('Dividends')] = 1
    assert needs_rebase(old, dividend, 5e-6)
    assert needs_rebase(old, raw.iloc[-1:], 5e-6)
    merged = merge_increment(old, new)
    pd.testing.assert_frame_equal(merged, raw, check_freq=False)
    with pytest.raises(ValueError, match='Duplicate'):
        merge_increment(old, pd.concat([new, new.iloc[[0]]]))


def response(raw, status=200, headers=None):
    payload = {'chart': {'error': None, 'result': [{'meta': {'symbol': 'AAA', 'instrumentType': 'EQUITY', 'currency': 'USD', 'exchangeTimezoneName': 'America/New_York'}, 'timestamp': [int(x.timestamp()) for x in raw.index], 'indicators': {'quote': [{c.lower(): raw[c].tolist() for c in ['Open', 'High', 'Low', 'Close', 'Volume']}], 'adjclose': [{'adjclose': raw['Adj Close'].tolist()}]}}]}}
    class Response:
        status_code = status
        content = json.dumps(payload).encode()
        def raise_for_status(self):
            if status >= 400:
                raise requests.HTTPError(str(status))
        def json(self):
            return payload
    result = Response()
    result.headers = headers or {}
    return result


def test_retry_transient_and_cache(setup_data):
    raw, meta, cfg, config, sessions = setup_data
    replies = iter([response(raw, 503), response(raw)])
    store = SnapshotStore(cfg, get=lambda *a, **k: next(replies), sleep=lambda _: None)
    result, first = store.update('AAA', '2024-01-01', '2024-01-10')
    again, second = store.update('AAA', '2024-01-01', '2024-01-10')
    assert first['status'] == 'ok' and len(first['attempts']) == 2
    assert store.network_requests == 2 and second['cache_hit']
    pd.testing.assert_frame_equal(result, again)
    assert first['survivorship_biased']


def test_retry_after_not_shortened(setup_data):
    raw, meta, cfg, config, sessions = setup_data
    store = SnapshotStore(cfg, get=lambda *a, **k: response(raw, 429, {'Retry-After': '120'}), sleep=lambda _: None)
    result, failure = store.update('AAA', '2024-01-01', '2024-01-10')
    assert result is None and store.rate_limited
    assert store.network_requests == 1 and failure['status'] == 'failed'


def test_incremental_workflow_rebases_instead_of_splicing(setup_data):
    raw, meta, cfg, config, sessions = setup_data
    replies = iter([response(raw.iloc[:4]), response(raw.iloc[2:].assign(**{'Adj Close': 90.})), response(raw.assign(**{'Adj Close': 90.}))])
    store = SnapshotStore(cfg, get=lambda *a, **k: next(replies), sleep=lambda _: None)
    old, first = store.update('AAA', '2024-01-01', '2024-01-06')
    new, second = store.update('AAA', '2024-01-01', '2024-01-10')
    assert second['update_mode'] == 'full_rebase'
    assert (new['Adj Close'] == 90).all() and (old['Adj Close'] == 95).all()
    assert store.network_requests == 3
    assert sha256(first['snapshot_path']) == first['snapshot_sha256']


def test_calendar_excludes_unfinished_session():
    dates = complete_sessions('2024-07-01', '2024-07-08', now='2024-07-03T16:00:00Z')
    assert list(dates.strftime('%Y-%m-%d')) == ['2024-07-01', '2024-07-02']


def test_panel_parquet_metadata_and_checksum(tmp_path):
    frame = pd.DataFrame({'date': pd.to_datetime(['2024-01-02']), 'ticker': ['A'], 'survivorship_biased': [True]})
    path = tmp_path / 'panel.parquet'
    write_panel_parquet(frame, path, {'dataset_id': 'test'})
    pointer = tmp_path / 'pointer.json'
    pointer.write_text(json.dumps({'panel_path': str(path), 'panel_sha256': sha256(path), 'survivorship_biased': True}))
    loaded, _ = load_research_panel(pointer)
    pd.testing.assert_frame_equal(frame, loaded)
    path.write_bytes(b'bad')
    with pytest.raises(ValueError, match='checksum'):
        load_research_panel(pointer)


def test_outside_range_action_is_disclosed_not_shifted(setup_data):
    raw, *_ = setup_data
    payload = response(raw).json()
    old_date = int(pd.Timestamp('2023-12-29 09:30', tz='America/New_York').timestamp())
    payload['chart']['result'][0]['events'] = {'dividends': {'old': {'date': old_date, 'amount': 1}}}
    table, omitted = parse_requested_chart(payload, '2024-01-01', '2024-01-10')
    assert len(omitted) == 1 and omitted[0]['date'] == '2023-12-29'
    assert table.Dividends.sum() == 0
    assert 'old' in payload['chart']['result'][0]['events']['dividends']
    # An event on an in-range weekend must NOT be silently assigned to Monday.
    payload['chart']['result'][0]['events']['dividends']['old']['date'] = int(pd.Timestamp('2024-01-06', tz='America/New_York').timestamp())
    with pytest.raises(ValueError, match='unmatched'):
        parse_requested_chart(payload, '2024-01-01', '2024-01-10')


def test_unexplained_late_start_quarantined(setup_data):
    raw, meta, cfg, config, sessions = setup_data
    meta['vendor_metadata']['firstTradeDate'] = int(pd.Timestamp('2000-01-01', tz='UTC').timestamp())
    frame, summary, _ = assess_stock(raw.iloc[1:], 'AAA', meta, cfg, config, sessions)
    assert frame is None and 'unexplained_late_history' in summary['reasons']


def test_missing_action_field_is_reportable(setup_data):
    raw, meta, cfg, config, sessions = setup_data
    raw.iloc[2, raw.columns.get_loc('Dividends')] = 1
    raw.iloc[2, raw.columns.get_loc('Stock Splits')] = np.nan
    frame, summary, _ = assess_stock(raw, 'AAA', meta, cfg, config, sessions)
    assert frame is None and 'invalid_corporate_action_fields' in summary['reasons']
    json.dumps(summary, allow_nan=False)

import numpy as np
import pandas as pd
import pytest

from src.data.adjustments import adjusted_ohlc, corporate_action_checks, session_returns, split_adjust_as_traded
from src.data.download import download_ticker, normalize, parse_chart
from src.data.universe import candidate_members_on, universe_label
from src.data.validation import REQUIRED, validate


@pytest.fixture
def panel():
    return pd.DataFrame({'ticker': ['A'] * 3, 'date': pd.to_datetime(['2024-01-02', '2024-01-03', '2024-01-04']), 'open': [100., 110., 121.], 'high': [101., 111., 122.], 'low': [99., 109., 120.], 'close': [100., 110., 121.], 'adj_close': [100., 110., 121.], 'volume': [10., 20., 30.], 'dividends': [0., 0., 0.], 'stock_splits': [0., 0., 0.]})


def test_return_alignment_and_ticker_boundaries(panel):
    b = panel.assign(ticker='B', adj_close=[50., 50., 50.])
    df = pd.concat([panel, b]).sample(frac=1, random_state=5)
    trailing = session_returns(df, panel.date)
    forward = session_returns(df, panel.date, horizon=2, forward=True)
    assert np.isnan(trailing.iloc[0]['return'])
    assert trailing.iloc[1]['return'] == pytest.approx(.1)
    assert forward.iloc[0]['return'] == pytest.approx(.21)
    assert forward.iloc[1:3]['return'].isna().all()
    assert trailing.iloc[4]['return'] == 0


def test_missing_session_is_not_bridged(panel):
    r = session_returns(panel.drop(index=1), panel.date)
    assert r['return'].isna().all()
    panel.loc[1, 'adj_close'] = np.nan
    assert session_returns(panel, panel.date)['return'].isna().all()


def test_duplicate_detection(panel):
    doubled = pd.concat([panel, panel.iloc[[1]]], ignore_index=True)
    report = validate(doubled, ['A'], panel.date)
    assert report['duplicate_excess_rows'] == 1
    assert report['issue_counts']['duplicate_ticker_date'] == 2
    with pytest.raises(ValueError, match='Duplicate'):
        session_returns(doubled, panel.date)


def test_ohlc_violation(panel):
    panel.loc[0, 'high'] = 99
    panel.loc[1, 'low'] = 111
    assert validate(panel, ['A'], panel.date)['issue_counts']['ohlc_violation'] == 2


def test_date_sorting_is_reported_without_mutation(panel):
    shuffled = panel.iloc[::-1].reset_index(drop=True)
    before = shuffled.copy(deep=True)
    assert validate(shuffled, ['A'], panel.date)['unsorted_tickers'] == ['A']
    pd.testing.assert_frame_equal(shuffled, before)


def test_missing_values_and_calendar(panel):
    panel.loc[0, 'close'] = np.nan
    report = validate(panel.drop(index=1), ['A', 'B'], panel.date)
    assert report['missing_values']['close'] == 1
    assert report['coverage'][0]['missing_sessions'] == 1
    assert report['missing_tickers'] == ['B']


def test_split_adjustment_excludes_ex_date():
    idx = pd.date_range('2024-01-01', periods=4)
    prices = pd.Series([100., 102., 51., 52.], index=idx)
    splits = pd.Series([0., 0., 2., 0.], index=idx)
    adjusted = split_adjust_as_traded(prices, splits)
    assert adjusted.tolist() == [50., 51., 51., 52.]
    assert adjusted.pct_change().iloc[2] == 0


def test_reverse_split():
    idx = pd.date_range('2024-01-01', periods=3)
    result = split_adjust_as_traded(pd.Series([10., 80., 88.], index=idx), pd.Series([0., .125, 0.], index=idx))
    assert result.tolist() == [80., 80., 88.]


def test_dividend_adjustment_and_no_double_count(panel):
    panel.loc[:, 'close'] = [100., 99., 100.]
    panel.loc[:, 'adj_close'] = [99., 99., 100.]
    panel.loc[:, 'dividends'] = [0., 1., 0.]
    assert session_returns(panel, panel.date).iloc[1]['return'] == 0
    assert corporate_action_checks(panel, 1e-6)['dividend_events'][0]['within_tolerance'] is True
    adj = adjusted_ohlc(panel)
    assert adj.iloc[0].adjusted_open == 99
    pd.testing.assert_series_equal(adj.volume, panel.volume)


def test_invalid_values_and_extreme_move(panel):
    panel.loc[0, 'open'] = 0
    panel.loc[1, 'volume'] = -1
    panel.loc[2, 'adj_close'] = 1000
    counts = validate(panel, ['A'], panel.date)['issue_counts']
    assert counts['non_positive_price'] == 1
    assert counts['negative_volume'] == 1
    assert counts['extreme_observed_adj_close_change'] == 1


def test_empty_download_validation(panel):
    empty = pd.DataFrame(columns=REQUIRED)
    result = validate(empty, ['A'], panel.date)
    assert result['stock_count'] == 0
    assert result['coverage'][0]['missing_sessions'] == 3


def test_infinite_value_serializable(panel):
    import json
    panel.loc[0, 'high'] = np.inf
    report = validate(panel, ['A'], panel.date)
    assert report['issue_counts']['non_finite_numeric'] == 1
    json.dumps(report, allow_nan=False)


def test_timezone_preserves_exchange_date():
    idx = pd.DatetimeIndex(['2024-01-02 00:00'], tz='America/New_York')
    df = normalize(pd.DataFrame({'Close': [1]}, index=idx), 'A', 'America/New_York')
    assert df.date.iloc[0] == pd.Timestamp('2024-01-02')
    assert df.date.dt.tz is None


def test_universe_fails_closed():
    assert 'SURVIVORSHIP-BIASED' in universe_label({'universe_mode': 'prototype_current_sp500'})
    with pytest.raises(ValueError, match='blocked'):
        universe_label({'universe_mode': 'point_in_time_universe'})
    with pytest.raises(NotImplementedError):
        universe_label({'universe_mode': 'point_in_time_universe', 'pit_verified': True, 'pit_membership_path': 'fake'})


def test_candidate_never_future_fills():
    h = pd.DataFrame({'date': ['2020-01-01', '2020-01-03'], 'tickers': ['A,B', 'A,C']})
    assert candidate_members_on(h, '2020-01-02') == {'A', 'B'}
    assert candidate_members_on(h, '2020-01-03') == {'A', 'C'}
    with pytest.raises(ValueError):
        candidate_members_on(h, '2019-12-31')
    with pytest.raises(ValueError):
        candidate_members_on(h, '2020-01-04')


def test_cache_prevents_network_and_detects_corruption(tmp_path, panel):
    cfg = {'data_source': 'yahoo_yfinance', 'cache_directory': str(tmp_path), 'start_date': '2024-01-01', 'end_date': '2024-01-05', 'max_attempts': 1, 'request_timeout_seconds': 1, 'request_pause_seconds': 0}
    vendor = panel.set_index('date')[['open', 'high', 'low', 'close', 'adj_close', 'volume']].rename(columns={'adj_close': 'Adj Close', **{c: c.title() for c in ['open', 'high', 'low', 'close', 'volume']}})
    vendor.index = vendor.index.tz_localize('America/New_York')
    calls = []
    def fetch(**kwargs):
        calls.append(kwargs)
        return vendor
    first, m1 = download_ticker('A', cfg, fetcher=fetch)
    second, m2 = download_ticker('A', cfg, fetcher=fetch)
    assert len(calls) == 1 and m2['cache_hit']
    pd.testing.assert_frame_equal(first, second)
    next(tmp_path.rglob('*.parquet')).write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='checksum'):
        download_ticker('A', cfg, fetcher=fetch)


def test_chart_event_alignment():
    timestamps = [1704205800, 1704292200]
    payload = {'chart': {'error': None, 'result': [{'meta': {'currency': 'USD', 'exchangeTimezoneName': 'America/New_York'}, 'timestamp': timestamps, 'indicators': {'quote': [{'open': [50, 50], 'high': [51, 51], 'low': [49, 49], 'close': [50, 50], 'volume': [10, 20]}], 'adjclose': [{'adjclose': [50, 50]}]}, 'events': {'splits': {'x': {'date': timestamps[1], 'numerator': 2, 'denominator': 1}}}}]}}
    df = parse_chart(payload)
    assert df['Stock Splits'].tolist() == [0, 2]
    assert df.Close.tolist() == [50, 50]  # Never split adjust vendor close a second time.


def test_missing_split_previous_close_is_reportable(panel):
    import json
    panel.loc[0, 'stock_splits'] = 2
    result = corporate_action_checks(panel, 1e-4)
    assert result['split_events'][0]['close_return'] is None
    json.dumps(result, allow_nan=False)


def test_chart_primary_cache_no_network(monkeypatch, tmp_path):
    from src.data.download import download_chart
    cfg = {'cache_directory': str(tmp_path), 'start_date': '2024-01-01', 'end_date': '2024-01-05', 'request_timeout_seconds': 1}
    payload = {'chart': {'error': None, 'result': [{'meta': {'currency': 'USD', 'exchangeTimezoneName': 'America/New_York'}, 'timestamp': [1704205800], 'indicators': {'quote': [{'open': [50], 'high': [51], 'low': [49], 'close': [50], 'volume': [10]}], 'adjclose': [{'adjclose': [50]}]}}]}}
    import json
    encoded = json.dumps(payload).encode()
    class Response:
        status_code = 200
        content = encoded
        url = 'https://example.test'
        def raise_for_status(self):
            pass
        def json(self):
            return payload
    calls = []
    def get(*args, **kwargs):
        calls.append(1)
        return Response()
    monkeypatch.setattr('src.data.download.requests.get', get)
    first, meta = download_chart('A', cfg)
    second, cached = download_chart('A', cfg)
    assert len(calls) == 1 and cached['cache_hit']
    pd.testing.assert_frame_equal(first, second)
    next(tmp_path.rglob('*.response.json')).write_text('tampered')
    with pytest.raises(ValueError, match='checksum'):
        download_chart('A', cfg)

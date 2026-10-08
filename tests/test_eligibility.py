import numpy as np
import pandas as pd
import pytest

from src.data.eligibility import EligibilityRules, attach_eligibility, compute_eligibility


def toy(n=320, ticker='A'):
    dates = pd.bdate_range('2020-01-02', periods=n)
    frame = pd.DataFrame({'date': dates, 'ticker': ticker, 'close': 100., 'volume': 200_000., 'is_valid_observation': True})
    return frame, dates


def test_252nd_valid_observation_inclusive_boundary():
    frame, dates = toy()
    result = compute_eligibility(frame, dates)
    assert not result.iloc[:251].is_research_eligible.any()
    assert result.iloc[251].is_research_eligible
    assert result.iloc[251].eligibility_valid_history_count == 252
    assert result.iloc[251].trailing_median_dollar_volume == 20_000_000


def test_future_volume_cannot_change_past_eligibility():
    frame, dates = toy()
    frame['volume'] = 90_000.  # USD 9m, below threshold
    baseline = compute_eligibility(frame, dates)
    changed = frame.copy()
    changed.loc[270:, 'volume'] = 10_000_000.
    actual = compute_eligibility(changed, dates)
    pd.testing.assert_frame_equal(baseline.iloc[:270], actual.iloc[:270])
    assert not actual.iloc[269].is_research_eligible
    assert actual.iloc[-1].is_research_eligible


def test_exact_backward_60_session_window_and_inclusive_threshold():
    frame, dates = toy(90)
    frame['close'] = 1.
    frame['volume'] = np.arange(1, 91, dtype=float) * 1_000_000
    rules = EligibilityRules(minimum_valid_history=1)
    result = compute_eligibility(frame, dates, rules)
    assert np.isnan(result.iloc[58].trailing_median_dollar_volume)
    assert result.iloc[59].trailing_median_dollar_volume == 30_500_000  # median of 1..60
    assert result.iloc[60].trailing_median_dollar_volume == 31_500_000  # median of 2..61
    frame['volume'] = 10_000_000.
    assert compute_eligibility(frame, dates, rules).iloc[59].is_research_eligible


def test_ipo_cannot_inherit_another_security_history():
    old, dates = toy(600, 'OLD')
    ipo = old.iloc[300:].assign(ticker='IPO')
    result = compute_eligibility(pd.concat([old, ipo], ignore_index=True), dates)
    new = result.loc[result.ticker == 'IPO'].reset_index(drop=True)
    assert len(new) == 300 and new.iloc[0].eligibility_valid_history_count == 1
    assert not new.iloc[:251].is_research_eligible.any()
    assert new.iloc[251].is_research_eligible


@pytest.mark.parametrize('absent_row', [False, True])
def test_missing_session_not_filled_or_compressed(absent_row):
    frame, dates = toy(330)
    if absent_row:
        frame = frame.drop(index=260)
    else:
        frame.loc[260, ['close', 'volume']] = np.nan
        frame.loc[260, 'is_valid_observation'] = False
    original = frame.copy(deep=True)
    result = compute_eligibility(frame, dates).set_index('date')
    # Missing index 260 stays within 60-session windows through index 319.
    assert not result.loc[dates[261]:dates[319], 'is_research_eligible'].any()
    assert result.loc[dates[320], 'is_research_eligible']
    assert result.loc[dates[261], 'liquidity_valid_sessions'] == 59
    assert np.isnan(result.loc[dates[261], 'trailing_median_dollar_volume'])
    if not absent_row:
        assert result.loc[dates[260], 'eligibility_reason'] == 'invalid_current_observation'
    pd.testing.assert_frame_equal(frame, original)


def test_only_valid_observations_count_toward_history():
    frame, dates = toy(310)
    frame.loc[10, 'is_valid_observation'] = False
    result = compute_eligibility(frame, dates)
    assert result.iloc[251].eligibility_valid_history_count == 251
    assert not result.iloc[251].is_research_eligible
    assert result.iloc[252].is_research_eligible


def test_suffix_mutations_and_prefix_truncation_invariant():
    frame, dates = toy()
    original = compute_eligibility(frame, dates)
    changed = frame.copy()
    changed.loc[280:, 'close'] = -1.
    changed.loc[280:, 'volume'] = np.nan
    changed.loc[280:, 'is_valid_observation'] = False
    actual = compute_eligibility(changed, dates)
    pd.testing.assert_frame_equal(original.iloc[:280], actual.iloc[:280])
    prefix = compute_eligibility(frame.iloc[:280], dates[:280])
    pd.testing.assert_frame_equal(original.iloc[:280], prefix)


def test_uses_close_not_adjusted_close_or_global_precomputed_fields():
    frame, dates = toy()
    frame['volume'] = 90_000.
    frame['adj_close'] = 100_000.
    frame['available_history_observations'] = 999999
    frame['has_minimum_history'] = True
    result = compute_eligibility(frame, dates)
    assert not result.is_research_eligible.any()
    assert result.iloc[-1].trailing_median_dollar_volume == 9_000_000


def test_shuffled_rows_and_ticker_independence():
    frame, dates = toy()
    low = frame.assign(ticker='B', volume=1.)
    shuffled = pd.concat([frame, low]).sample(frac=1, random_state=42)
    attached = attach_eligibility(shuffled, dates)
    assert attached.index.equals(shuffled.index)
    pd.testing.assert_frame_equal(attached[shuffled.columns], shuffled)
    assert not attached.loc[attached.ticker == 'B', 'is_research_eligible'].any()
    expected = compute_eligibility(frame, dates).set_index(['date', 'ticker']).sort_index()
    actual = attached.loc[attached.ticker == 'A', expected.columns.tolist() + ['date', 'ticker']].set_index(['date', 'ticker']).sort_index()
    pd.testing.assert_frame_equal(expected, actual)


def test_no_prelisting_rows_created_and_bad_keys_rejected():
    frame, dates = toy()
    result = compute_eligibility(frame.iloc[100:], dates)
    assert result.date.min() == dates[100] and len(result) == 220
    with pytest.raises(ValueError, match='unique'):
        compute_eligibility(pd.concat([frame, frame.iloc[[0]]]), dates)
    with pytest.raises(ValueError, match='outside'):
        compute_eligibility(frame, dates[1:])


def test_loader_opt_in_attaches_mask_without_writing(tmp_path):
    import json
    from src.data.download import sha256
    from src.data.panel import load_research_panel, write_panel_parquet
    frame, dates = toy()
    # Use the real exchange calendar, not business-day labels, for the loader.
    import exchange_calendars as xcals
    sessions = xcals.get_calendar('XNYS', start='2020-01-01', end='2021-12-31').sessions[:320]
    frame['date'] = sessions
    path = tmp_path / 'frozen.parquet'
    write_panel_parquet(frame, path, {'dataset_id': 'test'})
    digest = sha256(path)
    metadata = {'survivorship_biased': True, 'panel_path': str(path), 'panel_sha256': digest, 'config': {'calendar': 'XNYS', 'phase2': {'start_date': '2020-01-01', 'end_date': '2021-12-31', 'minimum_history_sessions': 252, 'liquidity_window_sessions': 60, 'minimum_median_daily_dollar_volume': 10_000_000}}}
    pointer = tmp_path / 'panel.json'
    pointer.write_text(json.dumps(metadata))
    original, _ = load_research_panel(pointer)
    enriched, meta = load_research_panel(pointer, with_eligibility=True)
    assert 'is_research_eligible' not in original
    assert enriched.iloc[251].is_research_eligible
    assert sha256(path) == digest and meta['eligibility']['survivorship_biased']

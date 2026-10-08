import numpy as np
import pandas as pd
import pytest
import exchange_calendars as xcals

from src.data.eligibility import attach_eligibility
from src.factors.definitions import NAMES
from src.factors.engine import compute_factors
from src.factors.preprocessing import preprocess_cross_section
from src.factors.targets import HORIZONS, compute_targets
from src.factors.dataset import build_research_matrix


def toy(n=320, ticker='A'):
    schedule = xcals.get_calendar('XNYS', start='2020-01-01', end='2022-12-31').schedule
    dates = schedule.index[:n]
    p = 100 + np.arange(n, dtype=float)
    frame = pd.DataFrame({'date': dates, 'ticker': ticker, 'open': p - 1,
                          'high': p + 2, 'low': p - 2, 'close': p, 'adj_close': p * .8,
                          'adjusted_open': (p - 1) * .8, 'volume': 200_000. + np.arange(n) * 1000,
                          'is_valid_observation': True})
    return frame, dates, schedule


def test_explicit_pandas_shift_directions():
    p = pd.Series([10., 11., 12., 13., 14., 15., 16.])
    assert p.shift(1).iloc[5] == 14  # positive looks backward
    assert p.shift(-1).iloc[5] == 16  # negative reads future
    assert p.shift(5).iloc[5] == 10
    assert p.shift(-5).iloc[0] == 15
    assert np.isnan(p.shift(5).iloc[4])
    assert np.isnan(p.shift(-5).iloc[2])


def test_hand_calculated_factors_all_definitions():
    frame, dates, _ = toy()
    result = compute_factors(frame, dates)
    t = 260
    row = result.iloc[t]
    p, v = frame.adj_close.to_numpy(), frame.volume.to_numpy()
    for h in (5, 10, 20, 60):
        assert row[f'RET_{h}'] == pytest.approx(p[t] / p[t-h] - 1)
        assert result.iloc[:h][f'RET_{h}'].isna().all()
    assert row.REV_5 == -row.RET_5
    for h in (10, 20, 60):
        returns = [p[s] / p[s-1] - 1 for s in range(t-h+1, t+1)]
        assert row[f'VOL_{h}'] == pytest.approx(np.std(returns, ddof=1))
    illiq = [abs(p[s]/p[s-1]-1)/(frame.close.iloc[s]*v[s]) for s in range(t-19,t+1)]
    assert row.ILLIQ_20 == pytest.approx(sum(illiq)/20)
    assert row.DOLLAR_VOLUME_20 == pytest.approx(np.mean(frame.close.iloc[t-19:t+1]*v[t-19:t+1]))
    assert row.VOLUME_RATIO_20 == pytest.approx(v[t]/np.mean(v[t-20:t]))
    assert row.VOLUME_SURPRISE_20 == pytest.approx((v[t]-np.mean(v[t-20:t]))/np.std(v[t-20:t],ddof=1))
    for h in (20, 60):
        assert row[f'PRICE_MA{h}'] == pytest.approx(p[t]/np.mean(p[t-h+1:t+1])-1)
    assert row.DIST_52W_HIGH == 0  # increasing adjusted-close series
    assert result.iloc[:251].DIST_52W_HIGH.isna().all()
    assert row.INTRADAY_RANGE == pytest.approx(4/360)
    assert row.OPEN_CLOSE_RETURN == pytest.approx(360/359-1)


def test_ret5_uses_past_even_when_future_is_extreme():
    frame, dates, _ = toy(12)
    frame.loc[:5, 'adj_close'] = [100, 110, 120, 130, 140, 150]
    frame.loc[6:, 'adj_close'] = 99999.
    assert compute_factors(frame, dates).iloc[5].RET_5 == .5


@pytest.mark.parametrize('absent', [False, True])
def test_missing_session_not_compressed_or_filled(absent):
    frame, dates, _ = toy(320)
    if absent:
        frame = frame.drop(index=260)
    else:
        frame.loc[260, 'is_valid_observation'] = False
    original = frame.copy(deep=True)
    factors = compute_factors(frame, dates).set_index('date')
    assert factors.loc[dates[261]:dates[265], 'RET_5'].isna().all()
    assert np.isfinite(factors.loc[dates[266], 'RET_5'])
    assert factors.loc[dates[261]:dates[270], 'VOL_10'].isna().all()
    assert np.isfinite(factors.loc[dates[271], 'VOL_10'])
    assert pd.isna(factors.loc[dates[-1], 'DIST_52W_HIGH'])
    pd.testing.assert_frame_equal(original, frame)


def test_ipo_cannot_inherit_history_or_another_ticker_prices():
    old, dates, _ = toy()
    new = old.iloc[200:].assign(ticker='IPO', adj_close=10.)
    frame = pd.concat([old, new], ignore_index=True).sample(frac=1, random_state=7)
    result = compute_factors(frame, dates)
    ipo = result[result.ticker == 'IPO'].sort_values('date')
    assert ipo.iloc[:5].RET_5.isna().all() and ipo.iloc[5].RET_5 == 0
    assert ipo.DIST_52W_HIGH.isna().all()
    assert len(ipo) == 120
    pd.testing.assert_frame_equal(result[['date','ticker']], frame[['date','ticker']].reset_index(drop=True))


def test_zero_variance_volume_reference_missing_not_infinite():
    frame, dates, _ = toy(40)
    frame['volume'] = 100.
    frame.loc[30, 'volume'] = 1000.
    row = compute_factors(frame, dates).iloc[30]
    assert row.VOLUME_RATIO_20 == 10
    assert pd.isna(row.VOLUME_SURPRISE_20)


def test_exact_next_open_targets_hand_calculation_and_tail():
    frame, dates, schedule = toy(30)
    result = compute_targets(frame, dates, schedule)
    row = result.iloc[5]
    assert row.entry_session == dates[6]
    assert row.exit_session_5D == dates[11]
    assert row.entry_price == pytest.approx(105 * .8)
    assert row.exit_price_5D == pytest.approx(110 * .8)
    assert row.FWD_RET_5D == pytest.approx(110/105-1)
    assert row.feature_timestamp > schedule.loc[dates[5], 'close']
    assert row.feature_timestamp < row.return_start_timestamp < row.return_end_timestamp_5D
    assert row.return_start_timestamp == schedule.loc[dates[6], 'open']
    for h in HORIZONS:
        assert not result.iloc[-(h+1):][f'target_available_{h}D'].any()
        assert result.iloc[-(h+2)][f'target_available_{h}D']
        assert pd.notna(result.iloc[-1][f'exit_session_{h}D'])  # scheduled, price unavailable


def test_holiday_and_early_close_timestamps():
    frame, dates, schedule = toy()
    labels = compute_targets(frame, dates, schedule).set_index('date')
    assert labels.loc['2020-07-02', 'entry_session'] == pd.Timestamp('2020-07-06')
    assert labels.loc['2020-11-27', 'feature_timestamp'] == pd.Timestamp('2020-11-27 18:00:00.000000001Z')
    assert labels.loc['2020-11-27', 'return_start_timestamp'] == pd.Timestamp('2020-11-30 14:30:00Z')


@pytest.mark.parametrize('endpoint', ['entry', 'exit'])
def test_missing_future_endpoint_does_not_change_signal_eligibility(endpoint):
    frame, dates, schedule = toy()
    before = build_research_matrix(attach_eligibility(frame, dates), dates, schedule)
    changed = frame.copy()
    changed.loc[261 if endpoint == 'entry' else 266, 'is_valid_observation'] = False
    after = build_research_matrix(attach_eligibility(changed, dates), dates, schedule)
    assert before.iloc[260].eligible_at_t and after.iloc[260].eligible_at_t
    assert before.iloc[260].target_available_5D and not after.iloc[260].target_available_5D
    assert not after.iloc[260].sample_usable_for_research
    pd.testing.assert_series_equal(before.iloc[260][NAMES], after.iloc[260][NAMES])
    assert after.iloc[260].entry_session == dates[261]  # never move past missing bar


def test_future_ineligibility_is_not_a_target_requirement():
    frame, dates, schedule = toy()
    frame.loc[261:, 'volume'] = 1.  # valid prices, future liquidity fails
    p = attach_eligibility(frame, dates)
    matrix = build_research_matrix(p, dates, schedule)
    assert not matrix.iloc[-1].eligible_at_t
    assert matrix.iloc[260].eligible_at_t and matrix.iloc[260].target_available_20D


def test_mutating_all_future_values_keeps_all_past_features_and_eligibility():
    frame, dates, schedule = toy()
    other = frame.assign(ticker='B', adj_close=frame.adj_close ** 1.1)
    combined = pd.concat([frame, other], ignore_index=True)
    original = attach_eligibility(combined, dates)
    before = build_research_matrix(original, dates, schedule)
    changed = combined.copy()
    future = changed.date > dates[270]
    numeric = changed.select_dtypes('number').columns
    changed.loc[future, numeric] = np.nan
    changed.loc[future, 'is_valid_observation'] = False
    changed = attach_eligibility(changed, dates)
    after = build_research_matrix(changed, dates, schedule)
    past = before.date <= dates[270]
    columns = ['eligible_at_t', 'factor_available', 'processed_factor_available', *NAMES,
               *[f'{n}_zscore' for n in NAMES], *[f'{n}_winsorized' for n in NAMES]]
    pd.testing.assert_frame_equal(before.loc[past, columns], after.loc[past, columns])
    # Truncation is stronger than mutating values: future rows need not exist.
    prefix = compute_factors(combined.loc[combined.date <= dates[270]], dates[:271])
    expected = compute_factors(combined, dates)
    pd.testing.assert_frame_equal(prefix, expected.loc[expected.date <= dates[270]].reset_index(drop=True))


def xs_fixture():
    frame = pd.DataFrame({'date': [pd.Timestamp('2020-01-02')]*4, 'ticker': list('ABCD'),
                          'eligible_at_t': [True, True, True, False]})
    for n in NAMES:
        frame[n] = [0., 10., 20., 1e12]
    return frame


def test_preprocessing_hand_calculation_and_no_ineligible_contamination():
    frame = xs_fixture()
    result = preprocess_cross_section(frame)
    np.testing.assert_allclose(result.RET_5_winsorized[:3], [.2,10.,19.8])
    np.testing.assert_allclose(result.RET_5_zscore[:3], [-np.sqrt(1.5),0,np.sqrt(1.5)])
    assert pd.isna(result.iloc[3].RET_5_zscore)
    # One factor's missing value cannot remove a stock from another factor.
    frame.loc[0, 'RET_10'] = np.nan
    actual = preprocess_cross_section(frame)
    pd.testing.assert_series_equal(result.RET_5_zscore, actual.RET_5_zscore)


def test_targets_never_enter_preprocessing_membership_or_values():
    frame = xs_fixture()
    before = preprocess_cross_section(frame)
    frame['FWD_RET_5D'] = [1e30, -1e30, np.nan, 2.]
    frame['target_available_5D'] = False
    frame['sample_usable_for_research'] = False
    pd.testing.assert_frame_equal(before, preprocess_cross_section(frame))


def test_no_future_or_test_period_scaler_fit():
    train = xs_fixture()
    baseline = preprocess_cross_section(train)
    test = train.assign(date=pd.Timestamp('2030-01-02'))
    test[NAMES] = test[NAMES] * 1e20 + 7e25
    joined = pd.concat([train,test],ignore_index=True)
    pd.testing.assert_frame_equal(baseline, preprocess_cross_section(joined).iloc[:4])


def test_constant_and_too_small_cross_sections_are_explicitly_unavailable():
    frame = xs_fixture()
    frame[NAMES] = 1.
    assert preprocess_cross_section(frame)[[f'{n}_zscore' for n in NAMES]].isna().all().all()
    frame['eligible_at_t'] = [True, False, False, False]
    assert preprocess_cross_section(frame)[[f'{n}_winsorized' for n in NAMES]].isna().all().all()


def test_targets_use_adjusted_basis_without_repeating_splits_or_dividends():
    frame, dates, schedule = toy(30)
    frame['open'] = 100.
    frame['adjusted_open'] = 80.
    frame.loc[11:, 'adjusted_open'] = 88.
    labels = compute_targets(frame, dates, schedule)
    assert labels.iloc[5].entry_vendor_open == labels.iloc[5].exit_vendor_open_5D == 100.
    assert labels.iloc[5].FWD_RET_5D == pytest.approx(.1)


def test_gap_inside_holding_period_keeps_endpoint_label_only():
    frame, dates, schedule = toy(30)
    expected = compute_targets(frame, dates, schedule).iloc[5].FWD_RET_5D
    frame.loc[8, 'is_valid_observation'] = False
    assert compute_targets(frame, dates, schedule).iloc[5].FWD_RET_5D == expected

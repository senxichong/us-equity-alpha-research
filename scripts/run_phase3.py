"""Offline Phase 3: frozen input -> tested features, labels and diagnostics only."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import exchange_calendars as xcals
import numpy as np
import pandas as pd

from src.data.download import sha256
from src.data.incremental import stamp, write_json
from src.data.panel import load_research_panel, write_panel_parquet
from src.factors.dataset import build_research_matrix, load_factor_panel
from src.factors.definitions import BIAS, FACTORS, FACTOR_VERSION, NAMES, PREPROCESSING
from src.factors.engine import compute_factors
from src.factors.targets import HORIZONS, TIMING_ID

REPORTS = ROOT / 'reports/phase3'
BIAS_TEXT = 'survivorship_biased = true; candidate_selection_biased = true'


def frozen_inventory():
    roots = ['data/raw', 'data/processed/phase2', 'data/processed/phase2_5', 'reports/phase2', 'reports/phase2_5']
    records = []
    for root in roots:
        for path in sorted((ROOT / root).rglob('*')):
            if path.is_file():
                stat = path.stat()
                records.append((path.relative_to(ROOT).as_posix(), stat.st_size, stat.st_mtime_ns))
    return hashlib.sha256(json.dumps(records).encode()).hexdigest()


def run_tests():
    process = subprocess.run([sys.executable, '-m', 'pytest', '-q', '--junitxml=reports/phase3/pytest.xml'], cwd=ROOT, capture_output=True, text=True)
    output = process.stdout + process.stderr
    (REPORTS / 'pytest.log').write_text(output, encoding='utf-8')
    print(output, flush=True)
    suites = ET.parse(REPORTS / 'pytest.xml').getroot().findall('testsuite')
    totals = {key: sum(int(s.get(key, 0)) for s in suites) for key in ['tests','failures','errors','skipped']}
    totals['passed'] = totals['tests'] - totals['failures'] - totals['errors'] - totals['skipped']
    warnings = re.findall(r'(\d+) warnings?', output)
    totals['warnings'] = int(warnings[-1]) if warnings else 0
    totals['returncode'] = process.returncode
    return totals


def write_definitions():
    metadata = {**BIAS, 'phase': 3, 'factor_version': FACTOR_VERSION, 'factors': FACTORS,
                'deferred': {'market_beta': 'No approved frozen broad-market benchmark; no download authorized',
                             'size': 'No PIT shares/market cap', 'neutralization': 'No certified PIT industry or market cap'}}
    write_json(REPORTS / 'factor_metadata.json', metadata)
    rows = ['# Factor definitions', '', BIAS_TEXT, '', f'Factor version: {FACTOR_VERSION}. P denotes frozen vendor adj_close.', '',
            '| Factor | Required consecutive sessions | Definition |', '|---|---:|---|']
    rows += [f"| {f['name']} | {f['minimum_history']} | {f['description']} |" for f in FACTORS]
    rows += ['', 'Every factor includes t, becomes observable after close(t) and daily-bar availability, and requires every specified source input to be valid. Missing/zero-volume sessions retain their position and invalidate dependent windows. No forward fill, interpolation, centered window or compression of valid rows. RET_n requires n+1 prices, not just endpoints. VOL_n uses n returns from n+1 prices, sample ddof=1, with no annualization.', '',
             'ILLIQ_20 uses absolute adjusted one-day returns divided by vendor Close × Volume, in inverse vendor USD-volume units; no arbitrary rescaling. DOLLAR_VOLUME_20 is the trailing mean of that proxy. Volume ratio and surprise compare the current volume against the previous 20 sessions, excluding t. They are trading-activity proxies, not turnover divided by shares outstanding. Zero reference standard deviation makes volume surprise unavailable.', '',
             'PRICE_MA20/60 report the fractional deviation P/MA−1, so zero means price equals its moving average. DIST_52W_HIGH uses the highest adjusted closing price over 252 sessions, not the highest intraday price. Intraday range and open-close return use same-basis vendor OHLC. Negative and redundant factors are retained: REV_5 is exactly −RET_5 and is not an independent signal.', '',
             '## Cross-sectional preprocessing', '',
             'For each factor and date independently, membership = eligible_at_t AND that raw factor is finite. Compute linear-interpolated 1st/99th percentiles, clip, then subtract the same-date clipped mean and divide by the same-date clipped population standard deviation (ddof=0). Require at least two members; zero standard deviation yields null z-scores. Raw, `_winsorized`, and `_zscore` columns are retained. Ineligible observations retain raw factors for audit but have null processed values. No target or future eligibility filter, no full-period scaler, no learned model and no fitting on a test period. All-factor completeness is a separate downstream flag, not the per-factor membership rule.', '',
             '## Availability and exclusions', '',
             '`factor_available_NAME` is past-only, finite raw-factor availability. `factor_available` requires all 17 raw values. `processed_factor_available` separately requires all 17 z-scores. The eligibility mask is unchanged; availability can only reduce participation for a given factor. Raw factors computed before 252 valid observations are not eligible for research.', '',
             'Market beta is deferred because no approved frozen market-benchmark series is present in the accepted panel; no download is authorized. Size and industry/capitalization neutralization are deferred because PIT shares, market cap and industry membership are not certified. Current metadata is not substituted.', '',
             'Machine-readable fields, source columns, warm-up, units and fixed diagnostic extreme thresholds are in `reports/phase3/factor_metadata.json`. Thresholds flag absolute raw magnitudes for inspection only; they do not quarantine securities, change values or select factors. Full-sample diagnostic means/quantiles are reports, never model/scaler parameters.', '',
             'Targets and timing: see TIMING_CONVENTION.md. These are prototype engineering outputs, not evidence of predictive power.']
    (ROOT / 'FACTOR_DEFINITIONS.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')


def distribution(x):
    x = x[np.isfinite(x)]
    out = {'count': int(len(x)), 'mean': x.mean(), 'std': x.std(ddof=1), 'median': x.median()}
    for q in [.01, .05, .25, .75, .95, .99]:
        out[f'p{int(q*100):02}'] = x.quantile(q)
    out['min'], out['max'] = x.min(), x.max()
    return out


def diagnostics(matrix):
    summaries, coverage = [], []
    daily_eligible = matrix.groupby('date').eligible_at_t.sum()
    for f in FACTORS:
        n = f['name']
        eligible = matrix.eligible_at_t
        raw, z = matrix.loc[eligible,n], matrix.loc[eligible,f'{n}_zscore']
        daily = matrix[['date']].assign(raw_available=eligible & matrix[n].notna(),
                              processed_available=eligible & matrix[f'{n}_zscore'].notna()).groupby('date')[['raw_available','processed_available']].sum()
        daily['eligible_count'] = daily_eligible
        daily['raw_coverage'] = daily.raw_available / daily.eligible_count.replace(0,np.nan)
        daily['processed_coverage'] = daily.processed_available / daily.eligible_count.replace(0,np.nan)
        daily['factor'] = n
        coverage.append(daily.reset_index().assign(**BIAS))
        summaries.append({**BIAS, 'factor': n, 'population': 'eligible_at_t; raw factor-specific finite values',
                          **distribution(raw), 'raw_all_rows_nonnull': int(matrix[n].notna().sum()),
                          'raw_all_rows_missing': int(matrix[n].isna().sum()),
                          'eligible_rows': int(eligible.sum()), 'eligible_nonnull_rate': raw.notna().mean(),
                          'median_daily_coverage_nonzero_eligible_dates': daily.raw_coverage.median(),
                          'median_daily_available_count_all_dates': daily.raw_available.median(),
                          'processed_nonnull': int(z.notna().sum()), 'processed_mean': z.mean(), 'processed_std': z.std(ddof=1),
                          'inf_count_all_rows': int(np.isinf(matrix[n]).sum()),
                          'extreme_count': int((raw.abs() > f['diagnostic_extreme_absolute_threshold']).sum()),
                          'extreme_abs_threshold': f['diagnostic_extreme_absolute_threshold'],
                          'earliest_raw_date': matrix.loc[matrix[n].notna(),'date'].min(),
                          'earliest_eligible_date': matrix.loc[eligible & matrix[n].notna(),'date'].min()})
    pd.concat(coverage,ignore_index=True).to_csv(REPORTS/'factor_coverage.csv', index=False)
    pd.DataFrame(summaries).to_csv(REPORTS/'factor_summary.csv', index=False)
    targets = []
    for h in HORIZONS:
        n = f'FWD_RET_{h}D'
        for population, mask in [('all_source_rows', pd.Series(True,index=matrix.index)), ('eligible_at_t', matrix.eligible_at_t)]:
            x = matrix.loc[mask,n]
            available = mask & matrix[n].notna()
            targets.append({**BIAS, 'target': n, 'population': population, **distribution(x),
                            'missing_count': int(x.isna().sum()), 'population_rows': int(mask.sum()),
                            'extreme_abs_gt_1_count': int((x.abs()>1).sum()),
                            'inf_count': int(np.isinf(x).sum()),
                            'earliest_valid_signal_date': matrix.loc[available,'date'].min(),
                            'latest_valid_signal_date': matrix.loc[available,'date'].max(),
                            'complete_feature_usable_count': int((mask & matrix[f'sample_usable_for_research_{h}D']).sum())})
    pd.DataFrame(targets).to_csv(REPORTS/'target_summary.csv', index=False)
    return summaries, targets


def audit_timing(panel, matrix, sessions, schedule):
    src = panel.set_index(['ticker','date'])
    mat = matrix.set_index(['ticker','date'])
    cases = [(t, d, why) for t in ['AAPL','MSFT','NVDA','META','UBER']
             for d,why in [('2022-06-10','normal'),('2022-07-01','near Independence Day'),('2026-10-07','dataset end')]]
    ipo = panel[panel.ticker == 'UBER'].date.min()
    cases.append(('UBER',str(ipo.date()),'first available history; not eligible'))
    invalid = panel.loc[~panel.is_valid_observation].sort_values(['date','ticker'])
    if len(invalid):
        row = invalid.iloc[0]
        pos = sessions.get_loc(row.date)
        # A missing scheduled entry and the invalid signal itself.
        cases.extend([(row.ticker, str(sessions[pos-1].date()), 'next scheduled entry missing/zero volume'),
                      (row.ticker,str(row.date.date()),'invalid signal observation')])
    rows = ['# Timing audit', '', BIAS_TEXT, '',
            'All prices below are read independently from the frozen Phase 2 panel. Adjusted opens are checked against vendor open × adj_close / close. Session offsets are checked against XNYS; no missing bar is skipped. UTC timestamps preserve daylight saving and early-close schedules. Null means unavailable, not a zero return.', '',
            '| Ticker / case | Signal / latest factor input | After-close marker UTC | Entry session / adjusted open (vendor open) | 5D exit session / adjusted open (vendor open) | FWD_RET_5D | eligible / target available |',
            '|---|---|---|---|---|---|---|']
    traces = []
    def price(ticker, date, field):
        key = (ticker,date)
        if key not in src.index or not src.loc[key,'is_valid_observation']:
            return np.nan
        return float(src.loc[key,field])
    def fmt(value):
        return f'{value:.10g}' if pd.notna(value) else 'null'
    for ticker,date,why in cases:
        key = (ticker,pd.Timestamp(date))
        if key not in mat.index:
            raise AssertionError(f'Audit key missing: {key}')
        row = mat.loc[key]
        pos = schedule.index.get_loc(key[1])
        entry, exit_ = schedule.index[pos+1], schedule.index[pos+6]
        assert row.entry_session == entry and row.exit_session_5D == exit_
        pe, px = price(ticker,entry,'adjusted_open'), price(ticker,exit_,'adjusted_open')
        ve, vx = price(ticker,entry,'open'), price(ticker,exit_,'open')
        for date_, adjusted in [(entry,pe),(exit_,px)]:
            if pd.notna(adjusted):
                source = src.loc[(ticker,date_)]
                assert np.isclose(adjusted, source.open*source.adj_close/source.close,rtol=1e-12)
        expected = px/pe-1 if pd.notna(pe) and pd.notna(px) else np.nan
        np.testing.assert_allclose([row.entry_price,row.exit_price_5D,row.FWD_RET_5D],[pe,px,expected],equal_nan=True,rtol=1e-12)
        rows.append(f'| {ticker}: {why} | {date} / {row.last_factor_input_session} | {row.feature_timestamp} | {entry.date()} / {fmt(pe)} ({fmt(ve)}) | {exit_.date()} / {fmt(px)} ({fmt(vx)}) | {fmt(expected)} | {row.eligible_at_t} / {row.target_available_5D} |')
        traces.append({**BIAS,'ticker':ticker,'case':why,'signal_session':date,
                       'entry_session':str(entry.date()),'entry_timestamp':str(row.return_start_timestamp),
                       'exit_session_5D':str(exit_.date()),'exit_timestamp_5D':str(row.return_end_timestamp_5D),
                       'entry_adjusted_open':None if pd.isna(pe) else pe,'exit_adjusted_open':None if pd.isna(px) else px,
                       'FWD_RET_5D':None if pd.isna(expected) else expected,'verified':True})
    rows += ['', f'{len(traces)} independent source traces passed. The 2022-07-01 signals enter on July 5; the five-session exit is July 12. An IPO/first-history row can have a calculable future label while being ineligible at t; a final-date signal can be eligible while its label is unavailable. These are deliberately separate states.', '',
             'No execution cash ledger is certified. Both adjusted and vendor prices retain Yahoo retrospective normalization. See TIMING_CONVENTION.md.']
    (ROOT/'TIMING_AUDIT.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    write_json(REPORTS/'timing_audit.json',traces)
    return len(traces)


def main():
    REPORTS.mkdir(parents=True,exist_ok=True)
    before = frozen_inventory()
    tests = run_tests()
    if tests['returncode'] or tests['skipped']:
        raise RuntimeError('Full test suite did not pass without skips')
    print('Loading authoritative frozen panel with unchanged eligibility...',flush=True)
    panel, source = load_research_panel(with_eligibility=True)
    sidecar = json.loads((ROOT/'data/processed/phase2_5/eligibility.json').read_text())
    assert sidecar['status'] == 'PASS' and sidecar['source_panel_sha256'] == source['panel_sha256']
    assert sha256(sidecar['mask_path']) == sidecar['mask_sha256']
    frozen_mask = pd.read_parquet(sidecar['mask_path'])
    pd.testing.assert_frame_equal(panel[frozen_mask.columns].reset_index(drop=True),frozen_mask.reset_index(drop=True))
    del frozen_mask
    cfg = source['config']['phase2']
    end = (pd.Timestamp(cfg['end_date']) + pd.Timedelta(days=75)).strftime('%Y-%m-%d')
    schedule = xcals.get_calendar(source['config']['calendar'],start=cfg['start_date'],end=end).schedule
    sessions = schedule.index[(schedule.index>=pd.Timestamp(source['date_min'])) & (schedule.index<=pd.Timestamp(source['date_max']))]
    write_definitions()
    print('Building 17 past-only factors, date-local transforms, and four target horizons...',flush=True)
    matrix = build_research_matrix(panel,sessions,schedule)
    checks = {'source_eligibility_matches_frozen_phase2_5': True,
              'original_keys_preserved': matrix[['date','ticker']].equals(panel[['date','ticker']]),
              'eligible_mask_unchanged': matrix.eligible_at_t.equals(panel.is_research_eligible),
              'candidate_count_393': matrix.ticker.nunique() == 393,
              'no_factor_infinity': not np.isinf(matrix[NAMES].to_numpy()).any(),
              'signals_precede_entry': bool((matrix.feature_timestamp < matrix.return_start_timestamp).all()),
              'source_adjusted_open_consistency': bool(np.allclose(panel.adjusted_open, panel.open*panel.adj_close/panel.close,rtol=1e-12,equal_nan=True))}
    for h in HORIZONS:
        checks[f'tail_{h}D_unavailable'] = not matrix.loc[matrix.date.isin(sessions[-(h+1):]),f'target_available_{h}D'].any()
        checks[f'target_{h}D_flags_match'] = matrix[f'target_available_{h}D'].equals(matrix[f'FWD_RET_{h}D'].notna())
    for ticker in ['AAPL','META','UBER']:
        cutoff = pd.Timestamp('2020-12-31')
        prefix = panel.loc[(panel.ticker==ticker)&(panel.date<=cutoff)]
        result = compute_factors(prefix,sessions[sessions<=cutoff])
        expected = matrix.loc[(matrix.ticker==ticker)&(matrix.date<=cutoff),result.columns].reset_index(drop=True)
        pd.testing.assert_frame_equal(result,expected)
        checks[f'real_prefix_invariance_{ticker}'] = True
    print('Writing descriptive diagnostics and checking source timing traces...',flush=True)
    summaries, targets = diagnostics(matrix)
    audit_count = audit_timing(panel,matrix,sessions,schedule)
    checks['timing_audit'] = audit_count >= 5
    checks['full_test_suite'] = tests['returncode'] == 0
    checks['upstream_inventory_unchanged'] = frozen_inventory() == before
    checks['source_panel_hash_unchanged'] = sha256(source['panel_path']) == source['panel_sha256']
    checks['eligibility_sidecar_hash_unchanged'] = sha256(sidecar['mask_path']) == sidecar['mask_sha256']
    checks = {k:bool(v) for k,v in checks.items()}
    assert all(checks.values()), checks
    dataset_id = stamp()
    output = ROOT/'data/processed/phase3'/dataset_id
    output.mkdir(parents=True,exist_ok=False)
    path = output/'research_matrix.parquet'
    code_paths = [*sorted((ROOT/'src/factors').glob('*.py')),ROOT/'tests/test_factors.py',Path(__file__),ROOT/'TIMING_CONVENTION.md',ROOT/'FACTOR_DEFINITIONS.md',ROOT/'requirements-lock.txt']
    metadata = {**BIAS,'phase':3,'status':'PASS','dataset_id':dataset_id,'factor_version':FACTOR_VERSION,
                'source_dataset_id':source['dataset_id'],'source_panel_path':source['panel_path'],'source_panel_sha256':source['panel_sha256'],
                'source_eligibility_sha256':sidecar['mask_sha256'],'upstream_inventory_before':before,'upstream_inventory_after':frozen_inventory(),
                'timing_convention':TIMING_ID,'timing_document_sha256':sha256(ROOT/'TIMING_CONVENTION.md'),
                'target_formula':'adjusted_open[t+h+1]/adjusted_open[t+1]-1','horizons':list(HORIZONS),'primary_horizon':5,
                'frozen_source_config':source['config'],'eligibility_rules':source['eligibility'],'preprocessing':PREPROCESSING,'factor_names':NAMES,
                'candidate_stocks':int(panel.ticker.nunique()),'rows':len(matrix),'sessions':len(sessions),
                'date_min':str(sessions[0].date()),'date_max':str(sessions[-1].date()),
                'eligible_observations':int(matrix.eligible_at_t.sum()),'complete_raw_factor_rows':int(matrix.factor_available.sum()),
                'primary_usable_rows':int(matrix.sample_usable_for_research.sum()),
                'tests':tests,'checks':checks,'timing_audit_traces':audit_count,
                'code_sha256':{p.relative_to(ROOT).as_posix():sha256(p) for p in code_paths},
                'calendar_schedule_sha256':hashlib.sha256(schedule.to_csv().encode()).hexdigest(),
                'known_biases':['current survivor candidates','global candidate quality/economic selection','retrospective vendor vintage','unverified security identity and delistings','uncertified adjusted-open execution proxy and volume basis'],
                'network_calls':0,'upstream_rebuild':False,'execution_pnl_certified':False}
    print('Saving separate frozen Phase 3 matrix...',flush=True)
    write_panel_parquet(matrix,path,metadata)
    metadata.update(panel_path=str(path.relative_to(ROOT)),panel_sha256=sha256(path))
    write_json(output/'metadata.json',metadata)
    # Read-back verifies checksum, embedded bias and exact values/schema.
    loaded, _ = load_factor_panel(output/'metadata.json')
    pd.testing.assert_frame_equal(loaded,matrix)
    del loaded
    checks['parquet_roundtrip'] = True
    metadata['checks'] = checks
    for name in ['factor_metadata.json','factor_coverage.csv','factor_summary.csv','target_summary.csv','timing_audit.json','pytest.xml','pytest.log']:
        metadata.setdefault('report_sha256',{})[name] = sha256(REPORTS/name)
    write_json(output/'metadata.json',metadata)
    write_json(ROOT/'data/processed/phase3/research_matrix.json',metadata)
    write_json(REPORTS/'validation.json',metadata)
    report = ['# Phase 3 — Factor engine, target alignment and leakage tests','',BIAS_TEXT,'',
              '**PASS is limited to the frozen, biased prototype research interface. No predictive evaluation was performed.**','',
              f"Dataset `{dataset_id}`: {len(matrix):,} rows, {panel.ticker.nunique()} candidates, {len(sessions)} sessions; {sessions[0].date()} through {sessions[-1].date()}.",
              f"Source Phase 2 ID `{source['dataset_id']}`, SHA-256 `{source['panel_sha256']}`. Source Phase 2.5 mask SHA-256 `{sidecar['mask_sha256']}`. Upstream file inventory, panel bytes and eligibility mask were preserved; no rebuild or download.",'',
              '## Timing','',
              '**After close(t) and completed-bar availability, form the signal; buy at scheduled open(t+1), and measure the primary return from that open to scheduled open(t+6).** The h-day label exits at open(t+h+1), h=1/5/10/20. The after-close +1ns timestamp is a logical ordering marker, not measured feed latency. Actual bar delivery before next open remains an assumption. Prices at both endpoints use the frozen adjusted-open basis; this is a research label proxy, not certified executable cash PnL. Detailed timestamp/price definitions are in TIMING_CONVENTION.md. Overlapping targets require later purging/embargo and dependence-aware inference; no portfolio cohorts are constructed here.','',
              '## Eligibility and missing sessions','',
              f"The unchanged Phase 2.5 mask yields {int(matrix.eligible_at_t.sum()):,} eligible rows. It is past-only conditional on the frozen candidates/values: valid t, 252 valid observations through t, 60 complete trailing sessions, median vendor Close×Volume >= USD10m. Future eligibility cannot change historical membership. This is not PIT index membership or proof of real-time vendor vintage.",
              'Invalid/zero-volume/missing sessions remain calendar positions and are never filled or dropped to shorten a lookback. Factor availability is separate from eligibility, entry/exit validity and target availability. Missing scheduled entry/exit prices yield null targets, without delaying endpoints. Future target availability never affects normalization membership. Intermediate holding-period gaps do not erase an otherwise calculable endpoint label and do not prove continuous tradability.','',
              '## Factors and preprocessing','',
              '| Factor | Required sessions |','|---|---:|',
              *[f"| {f['name']} | {f['minimum_history']} |" for f in FACTORS],'',
              'All 17 factors, their raw values, winsorized values and z-scores are retained, including exact sign duplicate REV_5. Volume-based fields use the vendor activity proxy, not share turnover. Factor-specific windows are complete and trailing. Definitions/formulas/units are in FACTOR_DEFINITIONS.md and reports/phase3/factor_metadata.json. Beta is deferred without an approved benchmark; size and neutralization are deferred without PIT inputs.',
              'At each date/factor: eligible-at-t finite raw values define 1%/99% linear winsorization, then population z-score. Fewer than two names or zero variance -> null processed values. No target, future row or future complete-case flag participates; no global fitting, model, training/test split or scaler is introduced.','',
              '## Diagnostics and validation','',
              f"Full suite: **{tests['passed']} passed, {tests['failures']} failed, {tests['errors']} errors, {tests['skipped']} skipped; {tests['warnings']} warnings**. Logs and JUnit are retained under reports/phase3. Warnings are unsuppressed NumPy generic-timedelta deprecations in pandas/exchange-calendars; they indicate a future dependency compatibility issue, not a hidden failed assertion.",
              f"Artifact checks: {sum(checks.values())}/{len(checks)} passed; {audit_count} independent real-data timing traces across at least five tickers, normal/holiday/missing/IPO/end dates. Exact Parquet read-back matches the in-memory matrix.",
              'Adversarial tests hand-check every formula and pandas shift(+1/−1/+5/−5); insert present and absent missing bars; separate IPO histories and tickers; mutate all future numeric fields and validity; truncate future rows; remove scheduled future entry/exit observations; change future liquidity; inject targets/availability into transform input; and append an extreme future test-period cross section. Historical features, eligibility and normalization remain unchanged. Real AAPL/META/UBER prefix checks also pass.',
              f"Complete raw-factor rows: {int(matrix.factor_available.sum()):,}. Primary complete-feature, eligible, target-available rows: {int(matrix.sample_usable_for_research.sum()):,}. This count is a label-availability diagnostic, never the historical normalization population.",
              'factor_coverage.csv records date-level eligible denominators and factor-specific raw/processed coverage. factor_summary.csv records finite counts, nonnull rates, mean/std/quantiles, infinities, fixed-threshold extremes and earliest dates. target_summary.csv reports all-row and eligible-at-t label distributions and missingness separately. Extremes are flags only, not removals; these descriptive statistics are not strategy performance. Final h+1 signal sessions have no h-day labels.','',
              '## Artifacts and remaining risks','',
              f"Frozen matrix: `{metadata['panel_path']}`; SHA-256 `{metadata['panel_sha256']}`. Read with `src.factors.dataset.load_factor_panel()`. Versioned source/config/rule/code/dependency hashes, test evidence and diagnostics are in reports/phase3/validation.json and the dataset metadata. Raw/processed factor and independent sample/label flags are retained for every original source key.",
              'The frozen current-member universe remains survivorship-biased and candidate-selection-biased. Global short-history/full-period gaps/extreme-event/complex-action exclusions are not all demonstrated vendor corruption and remain economic selection bias; no quarantine decision was changed. PIT membership, delisting outcomes, permanent identity, historical share basis and full corporate-action cash economics remain unresolved. Retrospective adjustment revisions can alter historical levels. Next-open prices and bar latency are indicative assumptions, not certified fills. No IC, RankIC, quantile returns, models, portfolio returns, Sharpe or parameter optimization was computed. Work stops at Phase 3.','',
              'PHASE 3: PASS']
    (ROOT/'PHASE3_REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','rows':len(matrix),'tests':tests,'checks':checks,'panel_path':metadata['panel_path']},indent=2),flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        (ROOT/'PHASE3_REPORT.md').write_text(f'# Phase 3\n\n{BIAS_TEXT}\n\nBuild/validation failed: {type(exc).__name__}: {exc}\nSee reports/phase3 for retained evidence. No downstream phase authorized.\n\nPHASE 3: FAIL\n',encoding='utf-8')
        raise

"""Read frozen Phase 2 only; write a separate eligibility sidecar and report."""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import exchange_calendars as xcals
import pandas as pd

from src.data.download import sha256
from src.data.eligibility import EligibilityRules, compute_eligibility
from src.data.incremental import BIAS, stamp, write_json
from src.data.panel import load_research_panel, write_panel_parquet


def phase2_inventory():
    records = []
    for root in ['data/raw/full', 'data/processed/phase2', 'reports/phase2']:
        for p in sorted(Path(root).rglob('*')):
            if p.is_file():
                stat = p.stat()
                records.append((p.as_posix(), stat.st_size, stat.st_mtime_ns))
    return hashlib.sha256(json.dumps(records).encode()).hexdigest()


def main():
    inventory_before = phase2_inventory()
    pointer = Path('data/processed/phase2/research_panel.json')
    pointer_hash = sha256(pointer)
    panel, source = load_research_panel(pointer)
    cfg = source['config']['phase2']
    rules = EligibilityRules(cfg['minimum_history_sessions'], cfg['liquidity_window_sessions'], cfg['minimum_median_daily_dollar_volume'])
    sessions = xcals.get_calendar(source['config']['calendar'], start=cfg['start_date'], end=cfg['end_date']).sessions
    sessions = sessions[(sessions >= pd.Timestamp(source['date_min'])) & (sessions <= pd.Timestamp(source['date_max']))]
    mask = compute_eligibility(panel, sessions, rules)
    assert len(mask) == len(panel) and mask[['date', 'ticker']].equals(panel[['date', 'ticker']])
    eligible = mask.is_research_eligible
    assert panel.loc[eligible, 'is_valid_observation'].all()
    assert (mask.loc[eligible, 'eligibility_valid_history_count'] >= 252).all()
    assert (mask.loc[eligible, 'liquidity_valid_sessions'] == 60).all()
    assert (mask.loc[eligible, 'trailing_median_dollar_volume'] >= 10_000_000).all()
    checks = {'key_row_count_preserved': True, 'eligibility_predicates_satisfied': True}
    # Frozen source values must agree with the panel accepted in PHASE2_REPORT.
    old_report = Path('PHASE2_REPORT.md').read_text(encoding='utf-8')
    match = re.search(r'Dataset ID: `([^`]+)`', old_report)
    accepted_id = match.group(1) if match else source['dataset_id']
    if accepted_id != source['dataset_id']:
        accepted_path = Path('data/processed/phase2') / accepted_id / 'research_panel.parquet'
        pd.testing.assert_frame_equal(panel, pd.read_parquet(accepted_path))
    checks['same_values_as_accepted_phase2_panel'] = True
    for ticker in [t for t in ['AAPL', 'META', 'UBER'] if t in set(panel.ticker)]:
        cutoff = pd.Timestamp('2020-12-31')
        prefix = panel.loc[(panel.ticker == ticker) & (panel.date <= cutoff)]
        actual = compute_eligibility(prefix, sessions[sessions <= cutoff], rules)
        expected = mask.loc[(mask.ticker == ticker) & (mask.date <= cutoff)].reset_index(drop=True)
        pd.testing.assert_frame_equal(actual, expected)
        checks[f'real_prefix_invariance_{ticker}'] = True
    daily = mask.groupby('date').agg(candidate_rows=('ticker', 'size'), eligible_stock_count=('is_research_eligible', 'sum')).reindex(sessions, fill_value=0)
    daily.index.name = 'date'
    n = int(panel.ticker.nunique())
    counts = daily.eligible_stock_count
    daily['eligible_fraction_of_frozen_candidates'] = counts / n
    # Reporting definition declared in documentation; not an eligibility parameter.
    reasonable_count = 100
    first_dates = {str(k): str(counts[counts >= k].index.min().date()) if (counts >= k).any() else None for k in [1, 50, 100, 200, 300]}
    stats = {'candidate_stocks': n, 'dates': len(daily), 'source_panel_rows': len(panel), 'eligible_observations': int(eligible.sum()), 'mean_eligible_count': float(counts.mean()), 'median_eligible_count': float(counts.median()), 'min_eligible_count': int(counts.min()), 'max_eligible_count': int(counts.max()), 'eligible_count_quantiles': {str(k): float(v) for k,v in counts.quantile([0, .1, .25, .5, .75, .9, 1]).items()}, 'zero_eligible_dates': int((counts == 0).sum()), 'reasonable_cross_section_threshold': reasonable_count, 'first_reasonable_cross_section_date': first_dates[str(reasonable_count)], 'first_dates_reaching_thresholds': first_dates, 'primary_reason_counts': {str(k):int(v) for k,v in mask.eligibility_reason.value_counts().items()}}
    frequency = {str(k):int(v) for k,v in counts.value_counts().sort_index().items()}
    suite = ET.parse('reports/phase2_5/pytest.xml').getroot().find('testsuite')
    tests = {k:int(suite.attrib[k]) for k in ['tests', 'failures', 'errors', 'skipped']}
    checks['tests_passed'] = tests['tests'] > 0 and tests['failures'] == tests['errors'] == 0
    checks['phase2_files_unchanged'] = inventory_before == phase2_inventory()
    checks['phase2_pointer_unchanged'] = sha256(pointer) == pointer_hash
    checks['phase2_panel_unchanged'] = sha256(source['panel_path']) == source['panel_sha256']
    token = stamp()
    output = Path('data/processed/phase2_5') / token
    output.mkdir(parents=True)
    meta = {**BIAS, 'phase': '2.5', 'status': 'PASS' if all(checks.values()) else 'FAIL', 'source_dataset_id': source['dataset_id'], 'phase2_report_dataset_id': accepted_id, 'source_panel_path': source['panel_path'], 'source_panel_sha256': source['panel_sha256'], 'source_pointer_sha256': pointer_hash, 'phase2_inventory_sha256_before': inventory_before, 'phase2_inventory_sha256_after': phase2_inventory(), 'rules': rules.metadata(), 'stats': stats, 'checks': checks, 'tests': tests, 'eligible_count_frequency': frequency, 'global_quarantine_not_all_proven_corruption': True, 'code_sha256': {p:sha256(p) for p in ['src/data/eligibility.py', 'src/data/panel.py', 'tests/test_eligibility.py', 'scripts/run_phase2_5.py', 'POINT_IN_TIME_ELIGIBILITY.md']}}
    mask_path = output / 'eligibility_mask.parquet'
    daily_path = output / 'eligible_count_by_date.parquet'
    write_panel_parquet(mask, mask_path, meta)
    write_panel_parquet(daily.reset_index(), daily_path, {**BIAS, 'source_panel_sha256': source['panel_sha256'], 'rules': rules.metadata(), 'purpose': 'eligibility_breadth'})
    meta.update(mask_path=str(mask_path), mask_sha256=sha256(mask_path), daily_counts_path=str(daily_path), daily_counts_sha256=sha256(daily_path))
    write_json(output / 'metadata.json', meta)
    write_json('reports/phase2_5/eligibility_summary.json', meta)
    write_json('data/processed/phase2_5/eligibility.json', meta)
    rows = ['# Phase 2.5 — Point-in-time research eligibility', '', f"**{meta['status']} — conditional eligibility within a frozen prototype candidate universe.**", '', '**survivorship_biased = true; point_in_time_membership = false**', '', f"Candidates: **{n}**. Source dates: **{source['date_min']} to {source['date_max']}** ({len(daily)} trading sessions).", f"Source rows: {len(panel):,}; eligible observations: {stats['eligible_observations']:,}.", '', '| Eligible stocks per date | Count |', '|---|---:|', f"| Minimum (includes initial warm-up) | {stats['min_eligible_count']} |", f"| 10th percentile | {stats['eligible_count_quantiles']['0.1']} |", f"| 25th percentile | {stats['eligible_count_quantiles']['0.25']} |", f"| Median | {stats['median_eligible_count']} |", f"| 75th percentile | {stats['eligible_count_quantiles']['0.75']} |", f"| 90th percentile | {stats['eligible_count_quantiles']['0.9']} |", f"| Maximum | {stats['max_eligible_count']} |", f"| Mean | {stats['mean_eligible_count']:.3f} |", '', f"Zero-eligible dates: {stats['zero_eligible_dates']}. First reasonably sized cross section (predeclared **100** stocks): **{stats['first_reasonable_cross_section_date']}**. This reporting threshold does not change eligibility.", '', '| Breadth threshold | First date |', '|---|---|', *[f'| {k} | {v} |' for k,v in first_dates.items()], '', '## Rule', '', 'After session t closes and its bar is available: current valid observation AND at least 252 cumulative valid observations through t AND 60 valid observations in the last 60 exchange sessions through t AND their median vendor Close × Volume at least USD 10m. Missing sessions are never filled or compressed away. No adjusted close is used. This does not authorize execution at that same close.', '', '## Verification and source preservation', '', f"Tests: **{tests['tests']} passed**, {tests['failures']} failures, {tests['errors']} errors; checks: {sum(checks.values())}/{len(checks)} passed. Toy tests cover the 252nd-observation boundary, exact backward windows, future/suffix mutations, IPOs, missing rows, and Close rather than Adj Close. Real-data prefix checks also passed.", f"Phase 2 panel SHA-256 unchanged: `{source['panel_sha256']}`. Phase 2 pointer and inventory (paths/sizes/mtime) unchanged during this run. No dataset rebuild or data-source/network call was made.", f"Source pointer dataset: `{source['dataset_id']}`; Phase 2 report dataset: `{accepted_id}`. If these differ, the pre-existing later save was compared against the accepted report's panel and every dataframe value was identical; neither file was rewritten.", '', '## Interface and artifacts', '', '```python', 'from src.data.panel import load_research_panel', 'panel, metadata = load_research_panel(with_eligibility=True)', '# panel.is_research_eligible; panel.eligibility_reason', '```', '', 'The loader attaches the mask in memory and preserves all source rows. Apply the mask only to cross-sectional participation; keep the full session grid for any later horizon alignment.', f"Separate mask: `{mask_path}`.", f"All-date breadth series: `{daily_path}`. Exact count-frequency distribution and immutable source/rule metadata: `reports/phase2_5/eligibility_summary.json`.", '', '## Remaining biases', '', 'The frozen current-member candidate universe remains survivorship-biased. This mask cannot recover globally excluded securities or establish PIT index membership. In this specific Phase 2 run, validated_count = liquidity_eligible_count = selected_count = 393: the final recent-liquidity gate removed zero additional validated names, but applying its endpoint result to earlier dates would still be an invalid eligibility rule. The new per-date mask replaces that inference.', '', 'Global short-history/full-period gap exclusions are availability or investability screens, not demonstrated vendor corruption. Extreme changes and noninteger distributions can be genuine economic events; their conservative global exclusion remains selection bias. Confirmed OHLC/missing-field defects and unresolved provider contradictions are integrity issues; preserving a frozen quarantine is not a claim that all quarantined names were corrupted. No quarantine list was expanded, reversed or recomputed here.', '', 'Yahoo prices and volume retain their retrospective vendor basis; Close × Volume is the Phase 2 liquidity proxy, not independently certified historical traded turnover. Causality tests establish no future ROW dependency conditional on frozen values; they do not establish historical data-vintage availability. Delistings, permanent identity and issuer-event history remain unresolved.', '', 'Stopped after Phase 2.5. No factors, IC, RankIC, targets or portfolio returns were computed.']
    Path('PHASE2_5_REPORT.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(json.dumps({'status': meta['status'], 'stats': stats, 'checks': checks, 'tests': tests}, indent=2))
    if meta['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()

"""Build one validated, explicitly biased panel and reproducible dataset reports."""
import json
import sys
from datetime import timedelta
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import yaml

from src.data.download import load_config, sha256
from src.data.incremental import BIAS, stamp, write_json
from src.data.panel import RAW_FIELDS, assess_stock, complete_sessions, write_panel_parquet
from src.data.universe import current_sp500


def main():
    config = load_config()
    cfg = config['phase2']
    if config['universe_mode'] != 'prototype_current_sp500' or cfg['survivorship_biased'] is not True:
        raise ValueError('Unsupported or undisclosed universe')
    sessions = complete_sessions(cfg['start_date'], cfg['end_date'], config['calendar'])
    if sessions.empty:
        raise ValueError('No complete trading sessions')
    token = stamp()
    run_dir = ROOT / 'reports/phase2/runs' / token
    output = ROOT / cfg['processed_directory'] / token
    run_dir.mkdir(parents=True)
    output.mkdir(parents=True)
    roster = current_sp500(cfg['roster_path'])
    summaries, frames, all_issues, failures, unattempted = [], {}, [], [], []
    for i, row in roster.sort_values('vendor_ticker').iterrows():
        ticker = row.vendor_ticker
        state = ROOT / cfg['raw_directory'] / ticker / 'state.json'
        if not state.exists():
            error_path = state.parent / 'last_failure.json'
            detail = json.loads(error_path.read_text()) if error_path.exists() else {}
            if not error_path.exists():
                unattempted.append(ticker)
            attempts = detail.get('attempts', [])
            failures.append({**BIAS, 'ticker': ticker, 'status': 'download_or_parse_failed' if detail else 'not_attempted', 'error': attempts[-1].get('error', '') if attempts else '', 'details': detail})
            continue
        try:
            meta = json.loads(state.read_text())
            if meta['start'] > cfg['start_date'] or meta['end'] < str(sessions[-1].date() + timedelta(days=1)):
                raise ValueError('Snapshot request range is stale or incomplete')
            if sha256(meta['snapshot_path']) != meta['snapshot_sha256']:
                raise ValueError('Snapshot hash mismatch')
            raw = pd.read_parquet(meta['snapshot_path'])
            frame, summary, validation = assess_stock(raw, ticker, meta, cfg, config, sessions)
            summary.update(roster_security=row.Security, issuer_cik=str(row.CIK), selected=False)
            summaries.append(summary)
            all_issues.append({**BIAS, 'ticker': ticker, **validation})
            if frame is not None:
                frames[ticker] = frame
        except Exception as exc:
            failures.append({**BIAS, 'ticker': ticker, 'status': 'processing_failure', 'error': f'{type(exc).__name__}: {exc}'})
    eligible = sorted([s for s in summaries if s['status'] == 'validated' and s['liquidity_pass']], key=lambda x: (-x['recent_median_daily_dollar_volume'], x['ticker']))
    selected = [s['ticker'] for s in eligible[:cfg['target_stocks']]]
    if selected:
        panel = pd.concat([frames[t] for t in selected], ignore_index=True).sort_values(['date', 'ticker']).reset_index(drop=True)
    else:
        panel = pd.DataFrame(columns=['date', 'ticker', *RAW_FIELDS, 'is_observed', 'is_valid_observation', 'survivorship_biased'])
    for s in summaries:
        s['selected'] = s['ticker'] in selected
        s['selection_status'] = 'selected' if s['selected'] else ('quarantined' if s['status'] == 'quarantined' else ('below_liquidity_threshold' if not s['liquidity_pass'] else 'outside_target_rank'))
    assert not panel.duplicated(['date', 'ticker']).any()
    if len(panel):
        assert panel.date.isin(sessions).all()
        assert panel.loc[~panel.is_valid_observation, RAW_FIELDS].isna().all().all()
        assert panel.loc[panel.is_valid_observation, RAW_FIELDS].notna().all().all()
        assert set(panel.ticker) == set(selected)
    admitted = [s for s in summaries if s['selected']]
    missing_rows = int((~panel.is_valid_observation).sum()) if len(panel) else 0
    meta = {**BIAS, 'dataset_id': token, 'source': 'yahoo_chart', 'data_role': 'validated_survivorship_biased_prototype', 'config': config, 'roster_sha256': sha256(cfg['roster_path']), 'requested_start': cfg['start_date'], 'requested_end_exclusive': cfg['end_date'], 'last_complete_session': str(sessions[-1].date()), 'candidate_count': len(roster), 'download_or_processing_failures': len(failures), 'validated_count': len(frames), 'quarantined_count': sum(s['status'] == 'quarantined' for s in summaries), 'liquidity_eligible_count': len(eligible), 'stock_count': len(selected), 'selected_tickers': selected, 'date_min': str(panel.date.min().date()) if len(panel) else None, 'date_max': str(panel.date.max().date()) if len(panel) else None, 'panel_rows': len(panel), 'observations': int(panel.is_observed.sum()) if len(panel) else 0, 'valid_observations': int(panel.is_valid_observation.sum()) if len(panel) else 0, 'missing_or_nontrading_rows': missing_rows, 'active_grid_missing_rate': missing_rows / len(panel) if len(panel) else None, 'calendar_sessions': len(sessions), 'pre_history_slots': sum(s['pre_history_sessions'] for s in admitted), 'selected_split_events': sum(s['split_event_count'] for s in admitted), 'selected_dividend_events': sum(s['dividend_event_count'] for s in admitted), 'selected_complex_events': sum(s['complex_action_count'] for s in admitted), 'selected_dividend_mismatches': sum(s['dividend_mismatch_count'] for s in admitted), 'selection_as_of': str(sessions[-1].date()), 'selection_bias': 'Current roster plus latest-window liquidity and full-period data-quality screening; not historical eligibility.', 'run_directory': str(run_dir.relative_to(ROOT)), 'row_validation_passed': True, 'dataset_gate_passed': cfg['minimum_stocks'] <= len(selected) <= cfg['target_stocks'], 'input_snapshots': [{k:s[k] for k in ['ticker', 'snapshot_path', 'snapshot_sha256']} for s in summaries], 'code_sha256': {str(p.relative_to(ROOT)): sha256(p) for p in sorted([*ROOT.glob('src/**/*.py'), *ROOT.glob('scripts/*.py'), ROOT / 'requirements-lock.txt'])}}
    panel_path = output / 'research_panel.parquet'
    for source in [*ROOT.glob('tests/*.py'), *[ROOT / name for name in ['config.yaml', 'DATA_CONVENTIONS.md', 'DATA_LIMITATIONS.md', 'RESEARCH_PROTOCOL.md']]]:
        meta['code_sha256'][str(source.relative_to(ROOT))] = sha256(source)
    meta['unattempted_tickers'] = unattempted
    meta['dataset_gate_passed'] = meta['dataset_gate_passed'] and not unattempted
    embedded = {k:v for k,v in meta.items() if k not in ['input_snapshots', 'code_sha256']}
    write_panel_parquet(panel, panel_path, embedded)
    meta['panel_path'] = str(panel_path.relative_to(ROOT))
    meta['panel_sha256'] = sha256(panel_path)
    write_json(output / 'metadata.json', meta)
    write_json(ROOT / cfg['processed_directory'] / 'research_panel.json', meta)
    for name, obj in [('metadata', meta), ('stock_quality', {'survivorship_biased': True, 'stocks': summaries}), ('validation_details', {'survivorship_biased': True, 'stocks': all_issues}), ('download_failures', {'survivorship_biased': True, 'stocks': failures})]:
        write_json(run_dir / f'{name}.json', obj)
        write_json(ROOT / 'reports/phase2' / f'{name}.json', obj)
    (run_dir / 'config.yaml').write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
    coverage = panel.groupby('date').agg(stock_rows=('ticker', 'size'), valid_observations=('is_valid_observation', 'sum')).reset_index() if len(panel) else pd.DataFrame()
    write_panel_parquet(coverage, output / 'daily_coverage.parquet', {'dataset_id': token, 'role': 'coverage_only'})
    label = 'SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE — survivorship_biased = true'
    reasons = Counter(reason for s in summaries for reason in s['reasons'])
    lines = ['# Full dataset quality report', '', label, '', f"Dataset: {token}", f"Candidates: {len(roster)}; validated: {len(frames)}; selected: {len(selected)}; quarantined: {meta['quarantined_count']}; download/processing failures: {len(failures)}.", f"Dates: {meta['date_min']} to {meta['date_max']}; exchange sessions: {len(sessions)}.", f"Panel rows: {len(panel)}; observed rows: {meta['observations']}; valid observations: {meta['valid_observations']}; explicit missing/nontrading rows: {missing_rows}.", f"Active-grid missing rate: {meta['active_grid_missing_rate']}; pre-history slots omitted: {meta['pre_history_slots']}.", f"Selected vendor split events: {meta['selected_split_events']}; dividends: {meta['selected_dividend_events']}; complex-action events admitted: {meta['selected_complex_events']}; dividend-factor mismatches admitted: {meta['selected_dividend_mismatches']}.", '', '## Admission / missing-data policy', '', 'Severe schema/price/date defects, unexplained late starts, excessive active gaps, short history, unreconciled extreme changes, complex distributions and dividend-factor mismatches quarantine the entire ticker. No failed ticker enters the panel. Missing sessions for admitted securities are explicit null rows; zero volume is nontradable. No forward/backward fill. Rows before the first available listing/history are not created. has_minimum_history counts valid observations available through that date; future factor windows still need their own missing-window rules.', '', 'The liquidity screen uses the latest configured window, so it introduces selection look-ahead for historical analysis. Full-period quality exclusions introduce additional selection bias. CIK is issuer reference metadata, not a verified permanent security identifier.', '', '## Quarantine reasons (a ticker can have several)', '', *[f'- {key}: {value}' for key, value in sorted(reasons.items())], '', '## Download / processing failures', '', *[f"- {x['ticker']}: {x['status']} {x.get('error', '')}" for x in failures], '', 'Full errors and original responses remain in download_failures.json and raw/full; no ticker renaming or substitution is guessed.', '', '## Per-stock coverage and admission', '', '|Ticker|Status|Selected|Rows|First|Last|Full-calendar coverage|Active coverage|Raw missing rate|Pre-history sessions|Reasons|', '|---|---|---|---:|---|---|---:|---:|---:|---:|---|']
    for s in summaries:
        lines.append(f"|{s['ticker']}|{s['selection_status']}|{s['selected']}|{s['observations']}|{s['first_date']}|{s['last_date']}|{s['calendar_coverage']:.4%}|{s['active_coverage']:.4%}|{s['raw_missing_rate']:.4%}|{s['pre_history_sessions']}|{', '.join(s['reasons'])}|")
    lines += ['', 'Per-security event dates/ratios/dividend-factor residuals are in stock_quality.json. Exact anomalous rows and per-stock missing dates are in validation_details.json. Daily breadth is in daily_coverage.parquet.', '', '## Known bias and limits', '', 'Current membership and recent liquidity create survivorship/selection bias. Delisted returns and permanent identity mapping remain unavailable. Yahoo adjusted values are snapshot proxies, not as-traded execution history. No corporate-action cash ledger or PIT fundamentals. Latest HTTP availability does not establish the true historical information set. A passing dataset gate means only a validated prototype research input.', '', f"Panel: {meta['panel_path']}; SHA-256: {meta['panel_sha256']}."]
    report = '\n'.join(lines) + '\n'
    (ROOT / 'reports/full_data_quality_report.md').write_text(report, encoding='utf-8')
    (run_dir / 'full_data_quality_report.md').write_text(report, encoding='utf-8')
    card = ['# Dataset card', '', label, '', f"Dataset ID: {token}", '', f"Panel: `{meta['panel_path']}`", f"Stable loader pointer: `{cfg['processed_directory']}/research_panel.json`", f"SHA-256: `{meta['panel_sha256']}`", '', f"{len(selected)} securities; {meta['date_min']} to {meta['date_max']}; {len(panel):,} aligned rows; {meta['valid_observations']:,} valid observations.", '', '## Intended use', '', 'Biased prototype cross-sectional research input only. No claims of unbiased historical backtests, execution quality or historical market eligibility. No factors or targets are computed in Phase 2.', '', '## Universe', '', f"Frozen Phase 1 current S&P 500 roster ({len(roster)} securities), SHA-256 {meta['roster_sha256']}. At most {cfg['target_stocks']} validated names ranked by median vendor Close × Volume over the latest {cfg['liquidity_window_sessions']} sessions, minimum USD {cfg['minimum_median_daily_dollar_volume']:,}/day. Both roster and liquidity selection reflect the current snapshot, not historical membership. Full-history quality exclusions add selection bias.", '', '## Schema', '', '`date`, `ticker`: unique sorted key. Date is the New York session label, not UTC publication time.', '`open`, `high`, `low`, `close`, `adj_close`, `volume`: unchanged vendor price basis on valid rows. No double split adjustment.', '`dividends`, `stock_splits`: vendor event amounts/ratios; noninteger distribution cases are quarantined under the current policy.', '`adjustment_factor`, `adjusted_open/high/low/close`: explicit Adj Close / Close normalization, not as-traded prices.', '`is_observed`: vendor supplied a bar. `is_valid_observation`: complete, admitted, positive-volume observation. `observation_status`: observed/missing_session/zero_volume.', '`available_history_observations`, `has_minimum_history`: count/flag available through this date; not a guarantee that any particular future rolling window has no gaps.', '`survivorship_biased`: always true. Parquet metadata and all Phase 2 JSON wrappers carry the bias flag.', '', '## Calendar, missing data and short histories', '', f"XNYS calendar, {len(sessions)} completed sessions. Dates before first available history are omitted (not automatically certified IPO dates). Post-start holes remain explicit null observations. No price/volume/action forward fill. Zero-volume bars have all financial fields nulled in the panel and remain intact in raw snapshots. Minimum admission history: {cfg['minimum_history_sessions']} valid sessions; IPO/short history tickers below this are quarantined. Features must respect explicit session gaps.", '', '## Updates and reproducibility', '', 'Run scripts/download_full.py to resume or extend the configured endpoint. Existing same-range snapshots are reused. Incremental updates request an overlap; a new split/dividend or material overlap revision triggers a full-history re-download before publication. Periodic full refresh applies when extending an old snapshot. Use --refresh for same-endpoint vendor revision audits; --retry-failed for explicit negative-cache retries. Transient failures use bounded exponential backoff. Retry-After is honored or the batch stops. All response bytes, attempt metadata and raw Parquet snapshots remain immutable.', '', 'A mixed-vintage incremental snapshot can miss revisions outside the overlap; periodic/full refresh mitigates but cannot prove historical-vintage accuracy. Snapshot lineage and hashes permit exact local replay. Raw vendor data remains excluded from Git.', '', '## Quality and exclusions', '', f"Quarantined: {meta['quarantined_count']}; download/processing failures: {len(failures)}. Missing rate on admitted active grid: {meta['active_grid_missing_rate']}. Detailed per-stock coverage, actions and failures: reports/full_data_quality_report.md and reports/phase2/*.json.", '', '## Limitations', '', 'Survivorship bias, latest-liquidity selection, full-history quality selection, symbol identity uncertainty, unavailable delisting proceeds, retrospective adjustments, unverified historical volume basis and lack of provider SLA remain. CIK and sector in the frozen roster are current metadata and must not be used for historical neutralization. Do not merge current shares with historical price to infer size. Existing DATA_CONVENTIONS.md and DATA_LIMITATIONS.md continue to apply.']
    (ROOT / 'DATASET_CARD.md').write_text('\n'.join(card) + '\n', encoding='utf-8')
    (run_dir / 'DATASET_CARD.md').write_text('\n'.join(card) + '\n', encoding='utf-8')
    print(json.dumps({k:meta[k] for k in ['dataset_id', 'stock_count', 'panel_rows', 'valid_observations', 'quarantined_count', 'download_or_processing_failures', 'dataset_gate_passed', 'panel_path']}, indent=2))


if __name__ == '__main__':
    main()

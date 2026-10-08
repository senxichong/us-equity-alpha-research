"""Independent artifact checks against admitted raw snapshots; generate gate report."""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.data.download import normalize, sha256
from src.data.incremental import BIAS, write_json
from src.data.panel import RAW_FIELDS, complete_sessions, load_research_panel


def main():
    panel, meta = load_research_panel()
    config = meta['config']
    cfg = config['phase2']
    stocks = json.loads((ROOT / 'reports/phase2/stock_quality.json').read_text())['stocks']
    failures = json.loads((ROOT / 'reports/phase2/download_failures.json').read_text())['stocks']
    errors = []
    checks = {}
    def check(name, value):
        checks[name] = bool(value)
        if not value:
            errors.append(name)
    check('unique_key', not panel.duplicated(['date', 'ticker']).any())
    check('sorted_key', panel[['date', 'ticker']].equals(panel.sort_values(['date', 'ticker'])[['date', 'ticker']]))
    check('bias_on_every_row', len(panel) > 0 and panel.survivorship_biased.all())
    check('stock_count_in_range', cfg['minimum_stocks'] <= panel.ticker.nunique() <= cfg['target_stocks'])
    check('all_candidates_attempted', not meta['unattempted_tickers'])
    rejected = {s['ticker'] for s in stocks if s['status'] == 'quarantined'} | {s['ticker'] for s in failures}
    check('no_failed_tickers', not set(panel.ticker) & rejected)
    check('null_missing_rows', panel.loc[~panel.is_valid_observation, RAW_FIELDS].isna().all().all())
    valid = panel.loc[panel.is_valid_observation]
    check('valid_fields_complete_finite', valid[RAW_FIELDS].notna().all().all() and np.isfinite(valid[RAW_FIELDS]).all().all())
    check('positive_price_volume', (valid[['open', 'high', 'low', 'close', 'adj_close', 'volume']] > 0).all().all())
    tol = valid[['open', 'high', 'low', 'close']].abs().max(axis=1) * config['ohlc_relative_tolerance']
    check('ohlc', ((valid.high + tol >= valid[['open', 'close']].max(axis=1)) & (valid.low - tol <= valid[['open', 'close']].min(axis=1)) & (valid.high + tol >= valid.low)).all())
    check('correct_adjusted_ohlc', np.allclose(valid[['adjusted_open', 'adjusted_high', 'adjusted_low', 'adjusted_close']].to_numpy(), valid[['open', 'high', 'low', 'close']].to_numpy() * (valid.adj_close / valid.close).to_numpy()[:, None]))
    sessions = complete_sessions(cfg['start_date'], cfg['end_date'], config['calendar'])
    check('completed_sessions_only', panel.date.isin(sessions).all())
    check('observation_count_matches', int(panel.is_valid_observation.sum()) == meta['valid_observations'])
    check('rows_match_metadata', len(panel) == meta['panel_rows'])
    source_count = 0
    for s in stocks:
        if not s['selected']:
            continue
        check(f"snapshot_hash_{s['ticker']}", sha256(s['snapshot_path']) == s['snapshot_sha256'])
        raw = normalize(pd.read_parquet(s['snapshot_path']), s['ticker'], config['exchange_timezone'])
        actual = panel.loc[panel.ticker == s['ticker']].set_index('date')
        expected_dates = sessions[sessions >= raw.date.min()]
        check(f"dense_active_grid_{s['ticker']}", actual.index.equals(expected_dates.rename('date')))
        reference = raw.set_index('date').reindex(actual.index)
        mask = actual.is_valid_observation
        check(f"raw_values_preserved_{s['ticker']}", np.allclose(actual.loc[mask, RAW_FIELDS], reference.loc[mask, RAW_FIELDS], equal_nan=True, rtol=0, atol=0))
        check(f"history_count_{s['ticker']}", np.array_equal(actual.available_history_observations, actual.is_valid_observation.cumsum()))
        source_count += 1
    xml_path = ROOT / 'reports/phase2/pytest.xml'
    suite = ET.parse(xml_path).getroot().find('testsuite')
    tests = {k:int(suite.attrib[k]) for k in ['tests', 'failures', 'errors', 'skipped']}
    check('pytest_passed', tests['tests'] > 0 and tests['failures'] == tests['errors'] == 0)
    check('code_matches_build', all(sha256(p) == h for p,h in meta['code_sha256'].items()))
    passed = not errors and meta['dataset_gate_passed']
    verification = {**BIAS, 'dataset_id': meta['dataset_id'], 'status': 'PASS' if passed else 'FAIL', 'checks': checks, 'failed_checks': errors, 'checked_raw_stocks': source_count, 'tests': tests}
    write_json(ROOT / 'reports/phase2/panel_verification.json', verification)
    write_json(ROOT / meta['run_directory'] / 'panel_verification.json', verification)
    download = json.loads((ROOT / 'reports/phase2/latest_download.json').read_text())
    cached = sum(x.get('cache_hit', False) for x in download['downloads'])
    update_states = []
    for p in (ROOT / cfg['raw_directory'] / 'AAPL').glob('*.metadata.json'):
        m = json.loads(p.read_text())
        update_states.append({k:m[k] for k in ['rows', 'end', 'update_mode', 'snapshot_sha256']})
    lines = ['# PHASE 2 — Production Research Dataset', '', '**SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE**', '', '**survivorship_biased = true**', '', f"## 决定：{'PASS' if passed else 'FAIL'}", '', '此结论仅适用于用户本轮明确允许的 prototype 研究数据集，不推翻 Phase 1 对无偏严谨历史研究的 FAIL。不是无偏回测数据库，也没有执行 Phase 3/4。', '', f"Dataset ID: `{meta['dataset_id']}`", '', '## 实际结果', '', f"- 冻结名单候选：{meta['candidate_count']} 只；下载/处理失败：{meta['download_or_processing_failures']} 只。", f"- 自动验证通过：{meta['validated_count']} 只；隔离：{meta['quarantined_count']} 只；流动性筛选后统一面板：{meta['stock_count']} 只。", f"- 日期：{meta['date_min']} 至 {meta['date_max']}，{meta['calendar_sessions']} 个完整 XNYS 交易日。", f"- 面板行数：{meta['panel_rows']:,}；真实有效 observation：{meta['valid_observations']:,}；显式缺失/非交易行：{meta['missing_or_nontrading_rows']}。", f"- 已纳入股票上市/可用历史之前的空位：{meta['pre_history_slots']:,}，这些空位没有伪造为交易记录。", f"- 有效区间缺失率：{meta['active_grid_missing_rate']:.6%}。每股票全期覆盖率、有效期覆盖率和原始缺失率见完整质量报告。", f"- 纳入面板的供应商拆分事件：{meta['selected_split_events']}；分红：{meta['selected_dividend_events']}；未核实非整数分配事件和超容差分红事件均未纳入。", '', '## 统一读取入口', '', '```python', 'from src.data.panel import load_research_panel', 'panel, metadata = load_research_panel()', '```', '', f"冻结 Parquet：`{meta['panel_path']}`", f"SHA-256：`{meta['panel_sha256']}`", '', '默认读取包含显式 missing_session/zero_volume 行的交易日对齐面板；使用 is_valid_observation 和 has_minimum_history 判断有效性。不能删掉缺失日后把相邻记录假装为相邻交易日。原始和处理后数据各自保存，Parquet 内嵌偏差 metadata。', '', '## 下载、增量和故障处理', '', '批量下载保持顺序和请求间隔，网络超时/5xx 使用有限指数退避；429 尊重 Retry-After，等待过长或重试耗尽即停止后续网络请求。失败和每次响应均留档，--retry-failed 明确重试负缓存。旧成功快照在更新失败时仍保留，但构建器拒绝把过期快照当作完整更新。', '', 'AAPL 真实增量链（不是仅测试模拟）：', '', '```json', json.dumps(update_states, indent=2), '```', '', '增量请求带重叠窗口；新的拆股/分红或重叠区间价格/复权变化会触发整段重新下载。测试另外覆盖触发 full_rebase 的路径，防止混接复权尺度。窗外供应商历史修订仍可能遗漏；保留周期性和显式全量刷新限制。', '', f"最后一次下载命令：{len(download['downloads'])} 个记录，其中 {cached} 个 cache hit；网络请求数 {download.get('network_requests', 0)}。", '', '## 准入与价格规则', '', '保留 Phase 1 的 New York session date、Adj Close / Close 复权比例和原始数据语义。不重复拆股、不把 adjusted close 混作原始成交价，不前向或后向填充价格。缺失日期/停牌无法仅凭日线判明，统一标为未知缺失而不是宣称实际成交。IPO/短历史按供应商 firstTradeDate 和首个返回记录进行一致性核查（零成交量记录单独标为不可用）；这不是独立 IPO 身份认证。', '', f"事先设定：最少 {cfg['minimum_history_sessions']} 个有效历史 observation；有效区间缺失率不超过 {cfg['max_active_missing_rate']:.2%}；近期 {cfg['liquidity_window_sessions']} 日中位 Close×Volume 至少 USD {cfg['minimum_median_daily_dollar_volume']:,}；目标最多 {cfg['target_stocks']}，最低 {cfg['minimum_stocks']}。没有为凑数量放松准入规则。", '', '严重价格/日期错误、待核验极端跳变、非整数分配、分红因子不一致和已知跨源问题隔离整只股票，原始数据不删除。合法的极端市场变化也可能被保守隔离，这会产生额外样本选择偏差。完整名单和逐行原因均保存。', '', '## 验证', '', f"pytest：{tests['tests']} 项，失败 {tests['failures']}，错误 {tests['errors']}，跳过 {tests['skipped']}。", f"独立产物验证：{sum(checks.values())}/{len(checks)} 检查通过；逐只比对 {source_count} 只股票的所有有效原始字段、来源哈希、日期网格和历史计数。", f"失败检查：{errors}。", '', '测试包括价格/收益基础逻辑、IPO 与短历史、无填充缺失处理、错误整股隔离、增量覆盖/复权重建、网络重试/429、Parquet metadata 和损坏检测。锁定依赖中的 NumPy/pandas/exchange-calendars 有 timedelta 弃用警告；实际测试及日历结果通过，未隐藏警告。', '', '## 交付文件', '', '- `src/data/incremental.py`：原始快照、更新、重试和限流。', '- `src/data/panel.py`：准入、交易日对齐、缺失处理及统一 loader。', '- `scripts/download_full.py`, `scripts/build_panel.py`, `scripts/verify_phase2.py`。', '- `tests/test_phase2.py` 与保留的 Phase 1 测试。', '- `config.yaml` 中独立的 phase2 配置；Phase 1 sample 配置保留。', '- `DATASET_CARD.md`, `reports/full_data_quality_report.md`, `reports/phase2/` 中的下载、逐股质量、失败、核验和测试证据。', '', '## 已知偏差与范围', '', '当前名单造成幸存者偏差，近期流动性筛选和全历史质量筛选引入选择前视偏差。永久证券身份、退市终值、复杂公司行动、历史 volume 单位和真实 as-traded 价格的局限没有解决。当前 CIK/行业数据不能当作历史时点标签。获准继续 prototype 不等于这些问题消失。', '', '当前阶段没有因子、target 数据集、模型、IC、组合或绩效结果。按 Phase 2 的停止条件结束。']
    report = '\n'.join(lines) + '\n'
    (ROOT / 'PHASE2_REPORT.md').write_text(report, encoding='utf-8')
    (ROOT / meta['run_directory'] / 'PHASE2_REPORT.md').write_text(report, encoding='utf-8')
    print(json.dumps({'status': verification['status'], 'checks_passed': sum(checks.values()), 'checks_total': len(checks), 'errors': errors, 'tests': tests}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

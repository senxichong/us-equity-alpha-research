# PHASE 2 — Production Research Dataset

**SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE**

**survivorship_biased = true**

## 决定：PASS

此结论仅适用于用户本轮明确允许的 prototype 研究数据集，不推翻 Phase 1 对无偏严谨历史研究的 FAIL。不是无偏回测数据库，也没有执行 Phase 3/4。

Dataset ID: `20261008T085012128534Z`

## 实际结果

- 冻结名单候选：503 只；下载/处理失败：1 只。
- 自动验证通过：393 只；隔离：109 只；流动性筛选后统一面板：393 只。
- 日期：2010-01-04 至 2026-10-07，4216 个完整 XNYS 交易日。
- 面板行数：1,563,421；真实有效 observation：1,563,389；显式缺失/非交易行：32。
- 已纳入股票上市/可用历史之前的空位：93,467，这些空位没有伪造为交易记录。
- 有效区间缺失率：0.002047%。每股票全期覆盖率、有效期覆盖率和原始缺失率见完整质量报告。
- 纳入面板的供应商拆分事件：118；分红：18905；未核实非整数分配事件和超容差分红事件均未纳入。

## 统一读取入口

```python
from src.data.panel import load_research_panel
panel, metadata = load_research_panel()
```

冻结 Parquet：`data\processed\phase2\20261008T085012128534Z\research_panel.parquet`
SHA-256：`c7d672b8991802be43f024d4651564a4fe5f0a5e5f8b7c664ff42dc9fb5fae61`

默认读取包含显式 missing_session/zero_volume 行的交易日对齐面板；使用 is_valid_observation 和 has_minimum_history 判断有效性。不能删掉缺失日后把相邻记录假装为相邻交易日。原始和处理后数据各自保存，Parquet 内嵌偏差 metadata。

## 下载、增量和故障处理

批量下载保持顺序和请求间隔，网络超时/5xx 使用有限指数退避；429 尊重 Retry-After，等待过长或重试耗尽即停止后续网络请求。失败和每次响应均留档，--retry-failed 明确重试负缓存。旧成功快照在更新失败时仍保留，但构建器拒绝把过期快照当作完整更新。

AAPL 真实增量链（不是仅测试模拟）：

```json
[
  {
    "rows": 4211,
    "end": "2026-10-01",
    "update_mode": "full",
    "snapshot_sha256": "8d6ab0922c4d1fa838f69aa0ec8f9313805420e10713e40f43acac285c6cb8d5"
  },
  {
    "rows": 4216,
    "end": "2026-10-08",
    "update_mode": "incremental",
    "snapshot_sha256": "5d1ae1c7984f12cf9037b0b309f0604cc25add4363229e1d19d36ae7c81988b6"
  }
]
```

增量请求带重叠窗口；新的拆股/分红或重叠区间价格/复权变化会触发整段重新下载。测试另外覆盖触发 full_rebase 的路径，防止混接复权尺度。窗外供应商历史修订仍可能遗漏；保留周期性和显式全量刷新限制。

最后一次下载命令：503 个记录，其中 500 个 cache hit；网络请求数 3。

## 准入与价格规则

保留 Phase 1 的 New York session date、Adj Close / Close 复权比例和原始数据语义。不重复拆股、不把 adjusted close 混作原始成交价，不前向或后向填充价格。缺失日期/停牌无法仅凭日线判明，统一标为未知缺失而不是宣称实际成交。IPO/短历史按供应商 firstTradeDate 和首个有效记录进行一致性核查；这不是独立 IPO 身份认证。

事先设定：最少 252 个有效历史 observation；有效区间缺失率不超过 0.50%；近期 60 日中位 Close×Volume 至少 USD 10,000,000；目标最多 450，最低 300。没有为凑数量放松准入规则。

严重价格/日期错误、待核验极端跳变、非整数分配、分红因子不一致和已知跨源问题隔离整只股票，原始数据不删除。合法的极端市场变化也可能被保守隔离，这会产生额外样本选择偏差。完整名单和逐行原因均保存。

## 验证

pytest：37 项，失败 0，错误 0，跳过 0。
独立产物验证：1588/1588 检查通过；逐只比对 393 只股票的所有有效原始字段、来源哈希、日期网格和历史计数。
失败检查：[]。

测试包括价格/收益基础逻辑、IPO 与短历史、无填充缺失处理、错误整股隔离、增量覆盖/复权重建、网络重试/429、Parquet metadata 和损坏检测。锁定依赖中的 NumPy/pandas/exchange-calendars 有 timedelta 弃用警告；实际测试及日历结果通过，未隐藏警告。

## 交付文件

- `src/data/incremental.py`：原始快照、更新、重试和限流。
- `src/data/panel.py`：准入、交易日对齐、缺失处理及统一 loader。
- `scripts/download_full.py`, `scripts/build_panel.py`, `scripts/verify_phase2.py`。
- `tests/test_phase2.py` 与保留的 Phase 1 测试。
- `config.yaml` 中独立的 phase2 配置；Phase 1 sample 配置保留。
- `DATASET_CARD.md`, `reports/full_data_quality_report.md`, `reports/phase2/` 中的下载、逐股质量、失败、核验和测试证据。

## 已知偏差与范围

当前名单造成幸存者偏差，近期流动性筛选和全历史质量筛选引入选择前视偏差。永久证券身份、退市终值、复杂公司行动、历史 volume 单位和真实 as-traded 价格的局限没有解决。当前 CIK/行业数据不能当作历史时点标签。获准继续 prototype 不等于这些问题消失。

当前阶段没有因子、target 数据集、模型、IC、组合或绩效结果。按 Phase 2 的停止条件结束。

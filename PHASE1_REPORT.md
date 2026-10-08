# PHASE 1 — Data Feasibility, Universe Design & Research Infrastructure

**SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE**

检查日期：2026-10-08，Asia/Shanghai。原始抓取时间在 manifest 中以 UTC 保存。

**最终决定：FAIL — 暂不能安全进入严谨的 Phase 2。**

小样本下载、数据定义、缓存、自动验证和测试已实际完成。FAIL 的原因是历史股票池、证券身份、退市收益及复杂公司行动的数据缺口，并非工程代码未执行。没有进行因子研究、IC/RankIC、机器学习、组合构建、回测或 Sharpe 计算。

## Data

最终推荐 **Yahoo Finance public chart + 本地冻结快照**，仅用于 prototype 数据工程。它在本机通过普通 HTTPS 请求成功取得要求的 OHLCV、Adj Close 和公司行动字段，无须账户或密钥。未将其当作有 SLA、可覆盖退市证券的生产数据库。

实际安装的 yfinance 1.7.0 对最初全部 17 个 ticker 查询返回 `YFRateLimitError`，成功数为零。其适配器和失败快照保留。独立 chart 适配器在失败后实际测试成功，配置明确改成 `yahoo_chart`，没有把后者结果冒充 yfinance 成功。Stooq 返回 HTML challenge，排除为无效价格数据。Alpha Vantage IBM demo 可作独立对照，但 AAPL demo 无访问资格。详见 [数据源调查](reports/data_source_research.md) 和 [原始探测结果](reports/source_probes.json)。

| 实际下载内容 | 结果 |
|---|---|
| 主样本 | AAPL、MSFT、AMZN、GOOGL、META、JPM、XOM、JNJ、NVDA、WMT、TSLA、GME、GE、O，共 14 只 |
| 主样本区间 | 2018-01-02 至 2026-10-07；请求为 `[2018-01-01, 2026-10-08)` |
| 主样本总量 | 30,842 条；每只 2,203 条完整交易日日线 |
| 主样本下载失败 | 0 |
| IBM 补充对照 | Yahoo 2,203 条；Alpha Vantage full demo 6,774 条，1999-11-01 至 2026-10-07 |
| 证券身份诊断 | FB 下载 323 条，但供应商标识为 ProShares S&P 500 Dynamic Daily Buffer ETF，不能用作历史 Facebook |
| 退市诊断 | TWTR、SIVBQ：HTTP 404，未取得价格，不据此推断退市收益 |
| 基础资料 | SEC Apple Companyfacts/Submissions、Nasdaq 当前目录、503 行当前 S&P 500 roster、公开历史成分候选 |

价格原始文件保存于 `data/raw/sample/`；Yahoo HTTP 原始 JSON、未经价格修补的 Parquet 和 metadata 分离保存。Processed 文件在独立目录。manifest 和文件哈希能够定位输入版本。数据文件未加入 Git，也未上传到外部服务。

## Universe

Mode A `prototype_current_sp500` 已实现当前名单读取、ticker 格式映射和强制偏差标签。当前名单仅供工程参考，没有把它当作 2010 年或 2018 年的成员名单。14 只 stress sample 不是当前 S&P 500 子集的承诺，也未声称满足最终 300–500 只股票的流动性筛选。

Mode B `point_in_time_universe` 已建立明确的拒绝执行入口，不能仅修改 `pit_verified` 配置绕过。公开候选 [fja05680/sp500](https://github.com/fja05680/sp500) 已真实下载并固定 commit `a2430f2af0c79ddf0748e91de11bdeb1616ab5a7`：2,720 个名单记录，范围 1996-01-02 至 2026-08-18；每行成员数介于 487–507。日期有序、无重复日期或行内重复 ticker。

对 TSLA 加入前后、FB/META 更名附近的 4 项选定日期核对通过。但候选终点早于请求终点，最新名单与当前名单有各 6 个差异，缺乏逐事件完整性核验、announcement/availability time 和永久证券 ID。它是可复现的候选资料，**不是已经解决的 PIT universe**。审计查询禁止超出候选范围外推；见 [历史名单审计](reports/source_audit.md)。

## Price convention

未来收益率、momentum 和 volatility 的基础统一为同一冻结快照中的 `adj_close`，以明确交易日对齐。收益率原语为 `P[t]/P[t-h]-1`；未来标签为 `P[t+h]/P[t]-1`，缺失端点不填充，终点不足不跨 ticker 借用数据。本阶段仅实现和测试对齐原语，没有生成研究信号。

Yahoo `close` 本身已经反映拆分，部分分配事件也体现为历史缩放；不能重复拆股调整。`adjusted_ohlc` 使用 `Adj Close / Close` 的一致比例，保留原始字段。供应商复权收益是代理口径，不能视为完全等价的可执行现金账本收益。未来真实 PnL 需要成交价、股份/现金分配、费用和退市终值；这里未实现。详见 [价格与时间约定](DATA_CONVENTIONS.md)。

## Validation

以下来自实际运行的 [质量报告](reports/data_quality_report.md)、[validation.json](reports/validation.json) 与 [公司行动结果](reports/corporate_actions.json)：

- 主样本必需字段缺失值 0；重复 ticker-date 多余行 0；日期乱序 0；OHLC 逻辑错误 0；非正价格、负成交量和非交易日记录均未触发。
- 每只样本覆盖全部 2,203 个预期交易日，缺失交易日 0。该结论只覆盖选定现存样本，不能推广为退市或全市场覆盖。
- 15 个绝对复权价格变动超过 40% 的标记，全部来自 GME。逐行证据保留；没有删除、填补、winsorize 或宣称全部是坏数据。
- 14 条供应商 split/distribution 事件；包括 GE 反向拆股和非整数分配事件。AAPL 2020-08-31 4:1、NVDA 2024-06-10 10:1 两项官方日期/比例 spot check 通过，事件日无机械性的除权崩跌。
- 412 条分红事件；以 0.0001 的调整因子绝对容差检查，超差 0。这验证供应商内部一致性，不替代独立现金分配台账。
- AAPL 重复请求的日期、OHLC、成交量与事件完全一致，但 Adj Close 最大差异为 0.0000762939453125 USD。必须保留快照，不能承诺重新下载逐字节相同。
- IBM 两源有 2,203 个重合日期，15 个日收益差异超过 1 bp，最大约 34.08 bp；2019-08-12/13 的无分红差异仍待外部裁决。未混合或修补两个来源。
- Alpha Vantage IBM 原始顺序为倒序；验证明确标记，比较时只对副本排序。

实际执行 `.venv/Scripts/python.exe -m pytest -q --junitxml=reports/pytest.xml`：**19 passed**。覆盖收益对齐与跨 ticker 边界、缺失交易日不填充、重复键、OHLC、日期顺序、正反拆股、分红因子、无效数值、空下载、时区、PIT 阻断、两种价格适配器的缓存与损坏检测。最终结果在 [pytest.xml](reports/pytest.xml)；一次新增测试的 fixture 作用域错误已修复，失败 XML 保留于 `reports/test_runs/`。

## Engineering

初始目录为空且无 Git 仓库，已初始化 Git，未生成提交或推送。Python 3.12.4；初次检查 C/D 盘可用空间约 27.35/78.14 GB。使用独立 `.venv`，没有修改全局包；原全局包清单、项目环境与版本锁均保存。网络对多个官方公共端点可达。

创建的核心文件如下；空的后续研究目录仅保留 `.gitkeep`。

| 类别 | 文件 |
|---|---|
| 项目与环境 | `README.md`, `requirements.txt`, `requirements-lock.txt`, `config.yaml`, `pyproject.toml`, `.gitignore` |
| 数据模块 | `src/data/download.py`, `validation.py`, `universe.py`, `adjustments.py` |
| 执行脚本 | `scripts/environment_audit.py`, `probe_sources.py`, `probe_yahoo_chart.py`, `run_phase1.py`, `audit_evidence.py` |
| 测试 | `tests/test_data.py` |
| 原则与约定 | `DATA_CONVENTIONS.md`, `DATA_LIMITATIONS.md`, `RESEARCH_PROTOCOL.md`, 本报告 |
| 证据 | `reports/data_quality_report.md`, `data_source_research.md`, `source_audit.md`，对应 JSON、pytest XML、`reports/runs/` 逐次归档 |

下载按源/参数缓存，异常也缓存；刷新产生新版本，不覆盖原快照。主程序以交易所日历截断完整交易日，原样保留异常数据；报告记录配置、输入/输出哈希和代码/依赖哈希。缓存重跑已实际完成，主样本与诊断请求全部 cache hit。历史候选的代码、README 和 LICENSE 已保存；没有把公开可读性视为无限制再分发许可。

## Limitations and recommendation

最大的风险是把“当前能下载到价格的幸存证券”误当成“历史当时可投资的全部证券”，再叠加 ticker 复用和遗漏退市终值，形成表面正常但系统性偏高的研究结果。当前的数据可用于演示数据工程；尚不足以支持无偏历史 alpha 结论。

因此整体 **FAIL**。放行还需要可信完整的历史成员记录、带生效日期的证券身份映射、退市价格与终值、复杂公司行动及跨源差异处理依据。2010 年起全样本覆盖和最终 300–500 只流动性股票池也未被本次小样本测试证明。完整披露见 [DATA_LIMITATIONS.md](DATA_LIMITATIONS.md)。

已按要求在 Phase 1 停止，等待下一条指令。

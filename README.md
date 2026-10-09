# US Equity Cross-Sectional Factor & Machine Learning Alpha Research

**Phase 1 — Data Feasibility, Universe Design & Research Infrastructure**

**SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE**

This repository contains executed data-source probes, immutable raw snapshots, a small stress sample, automatic validation and tests. It contains no factor research, ML training, portfolio construction or strategy performance. Start with [PHASE1_REPORT.md](PHASE1_REPORT.md), [data quality](reports/data_quality_report.md), [source audit](reports/source_audit.md), [conventions](DATA_CONVENTIONS.md), and [limitations](DATA_LIMITATIONS.md).

## Reproduce in PowerShell

Run from the repository root using Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe scripts/environment_audit.py
.\.venv\Scripts\python.exe scripts/probe_sources.py
.\.venv\Scripts\python.exe scripts/run_phase1.py
.\.venv\Scripts\python.exe scripts/audit_evidence.py
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/pytest.xml
```

`requirements.txt` declares supported dependency ranges; `requirements-lock.txt` records the complete installed environment used for this run. No API keys or accounts were created. Alpha Vantage probes use the publisher's demo key; general ticker access requires separate credentials/entitlement. SEC requests use an honest project User-Agent; sustained collection should configure a real operator contact and follow SEC fair-access rules.

The default source is `yahoo_chart` because the installed yfinance transport returned rate-limit exceptions in this environment. The direct public endpoint worked with ordinary HTTPS requests; it is unofficial and has no availability guarantee. Both adapters are implemented, and source selection is explicit rather than a silent substitution. Stop additional batch network calls on a rate-limit response.

`run_phase1.py` reads `config.yaml`, downloads only 14 named stress stocks and 3 identity/delisting probes, caches successes and failures, and saves a new audit run. The current 503-member roster is downloaded as reference metadata only. It is not used to select historical constituents. `audit_evidence.py` adds one IBM cross-source check. Running again uses cached price/source responses; `--refresh` explicitly creates new Yahoo snapshots. `audit_evidence.py --repeat-network` deliberately requests one fresh AAPL snapshot for a bounded repeatability comparison. None of these commands downloads a full index price panel.

## Layout

- `src/data/`: configuration/downloads, validation, universe gates, adjustment/alignment primitives.
- `scripts/`: environment audit, public endpoint probes, sample pipeline and evidence audit.
- `tests/`: offline deterministic tests of financial alignment, anomalies, cache and universe controls.
- `data/raw/sample/`: original Yahoo JSON, raw vendor Parquet, metadata and IBM demo table; excluded from Git.
- `data/raw/probes/`: saved HTTP bodies, status, source URL and retrieval hashes; excluded from Git.
- `data/processed/<run>/`: normalized and explicitly adjusted tables; no returns, signals or models.
- `reports/runs/<run>/`: archived configuration and machine-readable run evidence, including failed runs.
- `reports/`: current report pointers, environment/package audit, source audit and pytest evidence.
- `experiments/`, `src/factors/`, `src/evaluation/`, `src/models/`, `src/backtest/`: reserved empty directories.

Current membership is explicitly a biased engineering mode. Mode B raises an error; the public history candidate is tested by a separate audit helper and is not advertised as a validated PIT universe. An eventual 300–500 stock liquidity universe needs historical eligibility, security IDs, delisted coverage and lagged selection rules before any research claims.

Raw market data remains local. Reproducing from a fresh clone requires a successful download; archived raw files plus their hashes are needed to reproduce this exact snapshot. See [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) for experiment controls.

## Phase 2 — validated prototype panel

The subsequent user instruction explicitly permits a survivorship-biased prototype. Phase 1's FAIL for unbiased historical research is unchanged. Phase 2 adds a separate `phase2` configuration block and does not replace the earlier sample results.

```powershell
.\.venv\Scripts\python.exe scripts/download_full.py
.\.venv\Scripts\python.exe scripts/build_panel.py
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/phase2/pytest.xml
.\.venv\Scripts\python.exe scripts/verify_phase2.py
```

Read [DATASET_CARD.md](DATASET_CARD.md), [full quality report](reports/full_data_quality_report.md), and [PHASE2_REPORT.md](PHASE2_REPORT.md). Load the single published panel with:

```python
from src.data.panel import load_research_panel
panel, metadata = load_research_panel()
```

The loader verifies the frozen Parquet hash and bias metadata. It retains explicit missing-session rows. Never treat such rows as trades or calculate row-offset horizons after dropping gaps. `is_valid_observation` marks usable bars; `has_minimum_history` uses information available through each date. Prices are never forward-filled. Failed stocks are quarantined before liquidity selection.

For incremental updates, advance `phase2.end_date` (exclusive), run the downloader and rebuild. A calendar check excludes unfinished sessions. Existing same-range requests use cache; `--retry-failed` retries negative caches; `--refresh` creates new full snapshots and retains all previous data. Material overlap revisions or newly observed corporate actions force a full history rebase. Original payloads and per-attempt sidecars remain in `data/raw/full/`. Do not run multiple download processes against the same store concurrently.

The gate in PHASE2_REPORT applies only to this explicitly biased dataset. This delivery stops after Phase 2; factors and later research remain unimplemented.

## Phase 2.5 — historical research participation

The accepted Phase 2 price panel remains frozen. Use the trailing eligibility mask for later cross-sectional research:

```python
from src.data.panel import load_research_panel
panel, metadata = load_research_panel(with_eligibility=True)
# is_research_eligible is known only after this session's complete bar is available.
```

Eligibility requires a valid current bar, 252 cumulative valid observations through the current date, and a complete backward 60-session window with median vendor Close × Volume at least USD 10m. Missing observations are not filled. The loader attaches fields in memory and does not rewrite Phase 2. Preserve the session grid for future target alignment; the mask determines cross-sectional participation only.

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/phase2_5/pytest.xml
.\.venv\Scripts\python.exe scripts/run_phase2_5.py
```

This command reads the frozen panel and writes a separate mask/breadth artifact; it never downloads or rebuilds prices. See [POINT_IN_TIME_ELIGIBILITY.md](POINT_IN_TIME_ELIGIBILITY.md) and [PHASE2_5_REPORT.md](PHASE2_5_REPORT.md). Global survivorship and candidate/quarantine selection bias remain. No point-in-time index membership is claimed and no factor research is performed.

## Phase 3 — frozen factors and future labels

The separately authorized Phase 3 adds 17 past-only factors and 1/5/10/20-session adjusted-open target proxies. `survivorship_biased=true` and `candidate_selection_biased=true` remain mandatory. Signals form after close(t); entry is scheduled open(t+1), exit open(t+h+1). See [timing](TIMING_CONVENTION.md), [factor definitions](FACTOR_DEFINITIONS.md), [source timing audit](TIMING_AUDIT.md), and [Phase 3 report](PHASE3_REPORT.md).

```powershell
.\.venv\Scripts\python.exe scripts/run_phase3.py
```

This offline command runs the **entire** test suite, reads the authoritative Phase 2 loader with eligibility, verifies the frozen Phase 2.5 mask, and writes a separate timestamped Phase 3 matrix plus descriptive diagnostics. It never downloads or rebuilds upstream data. Run from the repository root with the locked environment. Each invocation creates a new Phase 3 snapshot; preserve prior snapshots for reproducibility.

```python
from src.factors.dataset import load_factor_panel
matrix, metadata = load_factor_panel()
# Per-factor research participation: eligible_at_t & factor_available_NAME.
# Target/complete-case flags do not define cross-sectional preprocessing membership.
```

Raw and winsorized factors, z-scores, signal/entry/exit timestamps and independent eligibility/availability flags remain accessible. Missing sessions are not filled. The matrix preserves all source keys, including warm-up and terminal rows with unavailable labels. No IC, RankIC, predictive evaluation, models or portfolios are implemented in Phase 3.

## Phase 4 — single-factor research and linear baselines

The separately authorized Phase 4 evaluates the frozen Phase 3 matrix. `survivorship_biased=true` and `candidate_selection_biased=true` remain mandatory. The [preregistered protocol](PHASE4_PROTOCOL.md) fixes the primary 5D label, minimum cross section, HAC inference, feature set, model folds and small regularization grids before results. The [research log](RESEARCH_LOG.md) retains pending hypotheses, implementation failures and completed outcomes.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-phase4-lock.txt
.\.venv\Scripts\python.exe scripts/run_phase4.py
.\.venv\Scripts\python.exe scripts/report_phase4.py
```

The analysis runner executes the complete repository tests, reads frozen inputs without downloads/rebuilds, and saves every tried model configuration and test-only prediction. It refuses to overwrite an existing Phase 4 analysis manifest; reproduce in an isolated copy with a fresh Phase 4 output directory while preserving the recorded upstream snapshots. The report command reads existing results and validates saved predictions; it never fits models. Reports/figures are archived by run and rendering timestamp.

See [Phase 4 decision](PHASE4_REPORT.md), [single-factor findings](reports/single_factor_report.md), and [baseline results](reports/baseline_report.md). CSV evidence and source/protocol/code hashes are in `reports/phase4/`; per-fold OOS prediction Parquets are in the directory recorded by `analysis_manifest.json`. Fold coefficients include training scaler statistics, composite orientations and selected penalties. Quantile plots describe overlapping forward labels, not capital-aware portfolio returns. This phase does not train complex models or compute strategy Sharpe.

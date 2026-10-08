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

# Dataset card

SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE — survivorship_biased = true

Dataset ID: 20261008T084032831451Z

Panel: `data\processed\phase2\20261008T084032831451Z\research_panel.parquet`
Stable loader pointer: `data/processed/phase2/research_panel.json`
SHA-256: `d6f74e02443bf40dd8945bcd09bddfa7255eff25e48d81f1976f8e80a369f01e`

250 securities; 2010-01-04 to 2026-10-07; 996,542 aligned rows; 996,517 valid observations.

## Intended use

Biased prototype cross-sectional research input only. No claims of unbiased historical backtests, execution quality or historical market eligibility. No factors or targets are computed in Phase 2.

## Universe

Frozen Phase 1 current S&P 500 roster (503 securities), SHA-256 f96781f06a19da95d210a62631e7cad2726c4c14d76dbfa8c0219d92c99f2765. At most 450 validated names ranked by median vendor Close × Volume over the latest 60 sessions, minimum USD 10,000,000/day. Both roster and liquidity selection reflect the current snapshot, not historical membership. Full-history quality exclusions add selection bias.

## Schema

`date`, `ticker`: unique sorted key. Date is the New York session label, not UTC publication time.
`open`, `high`, `low`, `close`, `adj_close`, `volume`: unchanged vendor price basis on valid rows. No double split adjustment.
`dividends`, `stock_splits`: vendor event amounts/ratios; noninteger distribution cases are quarantined under the current policy.
`adjustment_factor`, `adjusted_open/high/low/close`: explicit Adj Close / Close normalization, not as-traded prices.
`is_observed`: vendor supplied a bar. `is_valid_observation`: complete, admitted, positive-volume observation. `observation_status`: observed/missing_session/zero_volume.
`available_history_observations`, `has_minimum_history`: count/flag available through this date; not a guarantee that any particular future rolling window has no gaps.
`survivorship_biased`: always true. Parquet metadata and all Phase 2 JSON wrappers carry the bias flag.

## Calendar, missing data and short histories

XNYS calendar, 4216 completed sessions. Dates before first available history are omitted (not automatically certified IPO dates). Post-start holes remain explicit null observations. No price/volume/action forward fill. Zero-volume bars have all financial fields nulled in the panel and remain intact in raw snapshots. Minimum admission history: 252 valid sessions; IPO/short history tickers below this are quarantined. Features must respect explicit session gaps.

## Updates and reproducibility

Run scripts/download_full.py to resume or extend the configured endpoint. Existing same-range snapshots are reused. Incremental updates request an overlap; a new split/dividend or material overlap revision triggers a full-history re-download before publication. Periodic full refresh applies when extending an old snapshot. Use --refresh for same-endpoint vendor revision audits; --retry-failed for explicit negative-cache retries. Transient failures use bounded exponential backoff. Retry-After is honored or the batch stops. All response bytes, attempt metadata and raw Parquet snapshots remain immutable.

A mixed-vintage incremental snapshot can miss revisions outside the overlap; periodic/full refresh mitigates but cannot prove historical-vintage accuracy. Snapshot lineage and hashes permit exact local replay. Raw vendor data remains excluded from Git.

## Quality and exclusions

Quarantined: 71; download/processing failures: 182. Missing rate on admitted active grid: 2.5086749981435804e-05. Detailed per-stock coverage, actions and failures: reports/full_data_quality_report.md and reports/phase2/*.json.

## Limitations

Survivorship bias, latest-liquidity selection, full-history quality selection, symbol identity uncertainty, unavailable delisting proceeds, retrospective adjustments, unverified historical volume basis and lack of provider SLA remain. CIK and sector in the frozen roster are current metadata and must not be used for historical neutralization. Do not merge current shares with historical price to infer size. Existing DATA_CONVENTIONS.md and DATA_LIMITATIONS.md continue to apply.

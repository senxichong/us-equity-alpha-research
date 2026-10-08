# Point-in-time research eligibility

**survivorship_biased = true; point_in_time_membership = false**

This is a time-varying mask on the **frozen 393-security Phase 2 candidate panel**. It changes neither candidate membership nor stored Phase 2 data. The mask is causal conditional on the frozen vendor observations. It does not turn the dataset into a historical-vintage database or an unbiased backtest universe.

For security i at session t, eligibility requires all of:

1. The existing `is_valid_observation` is true and the current `close` and `volume` are finite and positive. Their product must also be finite.
2. At least **252 valid historical observations through and including t**. The 252nd valid observation is the earliest possible eligible date. Counts are recomputed by security, never inferred from its eventual total history.
3. The inclusive trailing **60 exchange sessions, t−59 through t**, contain 60 valid Close/Volume pairs. The calendar is XNYS as frozen by Phase 2. A missing row consumes a calendar session; it does not cause the window to reach farther into the past. Missing/zero-volume rows are not filled.
4. The median of `close * volume` over those 60 sessions is **at least USD 10,000,000**, including the boundary. This preserves Phase 2's threshold and price field. `adj_close` is never used for this liquidity proxy.

The complete-window requirement is a conservative trailing data-quality rule. One missing observation blocks liquidity eligibility until it leaves the 60-session window. It does not erase earlier history; cumulative valid history pauses for that observation. No full-period missingness rate, eventual listing length, endpoint liquidity rank, later corporate action or future anomaly determines the per-date mask.

`Close × Volume` is the existing vendor-basis turnover proxy, **not certified as-traded dollar volume**. Phase 1/2 explicitly distinguish vendor Close from true historical execution prices and note uncertain historical volume units. The mask does not undo vendor rebasing or imply that revised prices were available in real time. Applying a historical rolling function to a frozen snapshot proves row-level causality, not historical-vintage authenticity.

## Timing

Eligibility at t becomes available **after t's session has closed and the complete daily bar is available**. It may participate in a subsequent signal/research cross section. It cannot justify trading before or at that same close using the completed bar. Phase 3 must define its own later executable entry and return timestamps; this task computes no returns or signals.

## API and fields

```python
from src.data.panel import load_research_panel
panel, metadata = load_research_panel(with_eligibility=True)
```

The existing loader remains backward-compatible when `with_eligibility=False`. Opt-in computation is in memory, performs no download, and preserves all original rows, columns and row order. For Phase 3 use the opt-in interface and honor `is_research_eligible`; `has_minimum_history` alone is insufficient. Filtering a cross section is distinct from compressing the session grid for time alignment.

The mask exposes:

- `is_research_eligible`: conjunction of the four rules.
- `eligibility_valid_history_count`: cumulative valid observations through t.
- `liquidity_valid_sessions`: valid observations in the last 60 calendar sessions.
- `trailing_median_dollar_volume`: null unless all 60 observations exist and are valid.
- `eligibility_reason`: primary failing rule, in priority order: `invalid_current_observation`, `insufficient_valid_history`, `incomplete_trailing_liquidity_window`, `below_liquidity_threshold`; otherwise `eligible`. Supporting counts/median reveal simultaneous failures.

Internally, absent sessions and pre-listing slots are null calendar positions, never invented prices. Output contains exactly the existing input keys; no pre-IPO records are added. Each security is processed independently. Sorting input rows does not change keyed results. Duplicate keys and dates outside the supplied calendar fail explicitly.

`scripts/run_phase2_5.py` writes only a separate eligibility sidecar and Phase 2.5 reports. It compares Phase 2 source/pointer hashes and file-inventory fingerprints before/after, and preserves all Phase 2 prices and raw downloads. The sidecar contains keys and eligibility fields, not a rebuilt price dataset.

## Breadth reporting

Daily eligible counts include warm-up dates with zero eligible names. Report min, max, mean, quantiles, median, exact count-frequency distribution and the entire daily series. A **100-stock** cross section is the predeclared “reasonable size” reporting threshold (ample breadth for later basic cross-sectional diagnostics); also show first dates reaching 1/50/200/300. This descriptive threshold is not tuned and does not affect admission.

## Frozen candidate selection versus daily eligibility

Current S&P 500 survivorship bias remains. No historical index membership is asserted. Neither the recent-liquidity selection procedure nor globally excluded names can be undone without changing the accepted frozen universe; this task does not do so. The observed Phase 2 counts show all 393 validated names also passed the endpoint liquidity gate, so that gate removed no additional validated names in this run. This does **not** make every name liquid on every earlier date.

Quarantine categories must not be conflated:

| Category | Interpretation |
|---|---|
| Invalid OHLC, missing required fields, unresolved provider contradiction | Data-integrity evidence or an integrity issue requiring reconciliation; existing quarantine remains frozen. |
| Short eventual history; full-period missing-rate screening | Global availability/investability selection with temporal selection bias. The new daily mask instead uses only cumulative/trailing data for admitted candidates. |
| Extreme changes; noninteger distribution events | May be economically genuine, not proven corruption. Conservative global exclusion remains an additional selection limitation. |
| Current membership and endpoint liquidity procedure | Biased candidate construction, not PIT membership. Daily trailing liquidity replaces any inference that endpoint eligibility applies to the whole history. |

The mask only removes avoidable per-date eligibility leakage **within** the frozen candidates. Remaining limits include global candidate/quarantine selection, retrospective source revisions, identity/ticker reuse, missing delisting outcomes and unverified corporate-action economics. Later factor-specific warm-up or missing-window checks may only reduce participation using past information; the mask alone does not certify future factor validity.

# Phase 2.5 — Point-in-time research eligibility

**PASS — conditional eligibility within a frozen prototype candidate universe.**

**survivorship_biased = true; point_in_time_membership = false**

Candidates: **393**. Source dates: **2010-01-04 to 2026-10-07** (4216 trading sessions).
Source rows: 1,563,421; eligible observations: 1,442,588.

| Eligible stocks per date | Count |
|---|---:|
| Minimum (includes initial warm-up) | 0 |
| 10th percentile | 318.0 |
| 25th percentile | 343.0 |
| Median | 366.0 |
| 75th percentile | 386.0 |
| 90th percentile | 390.0 |
| Maximum | 393 |
| Mean | 342.170 |

Zero-eligible dates: 251. First reasonably sized cross section (predeclared **100** stocks): **2010-12-31**. This reporting threshold does not change eligibility.

| Breadth threshold | First date |
|---|---|
| 1 | 2010-12-31 |
| 50 | 2010-12-31 |
| 100 | 2010-12-31 |
| 200 | 2010-12-31 |
| 300 | 2010-12-31 |

## Rule

After session t closes and its bar is available: current valid observation AND at least 252 cumulative valid observations through t AND 60 valid observations in the last 60 exchange sessions through t AND their median vendor Close × Volume at least USD 10m. Missing sessions are never filled or compressed away. No adjusted close is used. This does not authorize execution at that same close.

## Verification and source preservation

Tests: **49 passed**, 0 failures, 0 errors; checks: 10/10 passed. Toy tests cover the 252nd-observation boundary, exact backward windows, future/suffix mutations, IPOs, missing rows, and Close rather than Adj Close. Real-data prefix checks also passed.
Phase 2 panel SHA-256 unchanged: `a095e7b3bad2f6ee19ca507e640895e5d6568d5c0fde46d29f80758c437be55a`. Phase 2 pointer and inventory (paths/sizes/mtime) unchanged during this run. No dataset rebuild or data-source/network call was made.
Source pointer dataset: `20261008T085506951888Z`; Phase 2 report dataset: `20261008T085012128534Z`. If these differ, the pre-existing later save was compared against the accepted report's panel and every dataframe value was identical; neither file was rewritten.

## Interface and artifacts

```python
from src.data.panel import load_research_panel
panel, metadata = load_research_panel(with_eligibility=True)
# panel.is_research_eligible; panel.eligibility_reason
```

The loader attaches the mask in memory and preserves all source rows. Apply the mask only to cross-sectional participation; keep the full session grid for any later horizon alignment.
Separate mask: `data\processed\phase2_5\20261008T132020810141Z\eligibility_mask.parquet`.
All-date breadth series: `data\processed\phase2_5\20261008T132020810141Z\eligible_count_by_date.parquet`. Exact count-frequency distribution and immutable source/rule metadata: `reports/phase2_5/eligibility_summary.json`.

## Remaining biases

The frozen current-member candidate universe remains survivorship-biased. This mask cannot recover globally excluded securities or establish PIT index membership. In this specific Phase 2 run, validated_count = liquidity_eligible_count = selected_count = 393: the final recent-liquidity gate removed zero additional validated names, but applying its endpoint result to earlier dates would still be an invalid eligibility rule. The new per-date mask replaces that inference.

Global short-history/full-period gap exclusions are availability or investability screens, not demonstrated vendor corruption. Extreme changes and noninteger distributions can be genuine economic events; their conservative global exclusion remains selection bias. Confirmed OHLC/missing-field defects and unresolved provider contradictions are integrity issues; preserving a frozen quarantine is not a claim that all quarantined names were corrupted. No quarantine list was expanded, reversed or recomputed here.

Yahoo prices and volume retain their retrospective vendor basis; Close × Volume is the Phase 2 liquidity proxy, not independently certified historical traded turnover. Causality tests establish no future ROW dependency conditional on frozen values; they do not establish historical data-vintage availability. Delistings, permanent identity and issuer-event history remain unresolved.

Stopped after Phase 2.5. No factors, IC, RankIC, targets or portfolio returns were computed.

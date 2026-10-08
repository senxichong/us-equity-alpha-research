# Phase 3 timing convention

survivorship_biased = true; candidate_selection_biased = true

**After session t closes and its daily bar is available, form the signal; enter at the scheduled open of t+1 and measure an h-session adjusted-open return through the scheduled open of t+h+1.** Primary h = 5; also 1, 10 and 20. These are exchange-session offsets, never calendar-day offsets or offsets through nonmissing observations.

## Information and execution times

- `date`: timezone-naive America/New_York session label on the frozen XNYS calendar.
- `last_factor_input_session`: t when at least one raw factor is available, otherwise null. Every factor includes information through t at most.
- `feature_timestamp`: official XNYS close(t) + 1 nanosecond, an **ordering marker** for strictly after close, not a measured vendor delivery time. Actual use requires the completed bar to arrive before the next open; that latency is not certified by this historical snapshot.
- `portfolio_formation_timestamp`: the same after-close marker; denotes signal formation only, not an executed portfolio.
- `entry_session`: scheduled t+1; `return_start_timestamp`: its official open in UTC. `entry_price` is its adjusted-open proxy; `entry_vendor_open` preserves the vendor OHLC basis.
- `exit_session_hD`: scheduled t+h+1; `return_end_timestamp_hD`: its official UTC open. `exit_price_hD` and `exit_vendor_open_hD` preserve both bases.
- `FWD_RET_hD = adjusted_open[t+h+1] / adjusted_open[t+1] - 1`. The holding interval is exactly h open-to-open trading-session intervals. No part of close(t) to open(t+1) is credited.

The calendar is extended only to identify scheduled exit timestamps after the frozen data endpoint; **no prices are extended or fetched**. Holidays and early closes follow the installed, locked XNYS calendar. An absent/invalid scheduled entry or exit makes the target unavailable; never delay entry/exit to the next observed price. Intermediate missing bars do not change an endpoint label. This is an endpoint research label, not evidence of continuous tradability.

## Price basis and corporate actions

Preserve Phase 1/2: `adjusted_open = open * adj_close / close` within the same frozen snapshot. Both target endpoints use this identical basis. The stored adjusted-open field is checked against the source formula. Vendor open is split/distribution normalized and is **not independently certified as-traded**. Dividend-adjusted opens are an indicative, corporate-action-consistent research proxy, not an attainable cash execution price or an exact reinvestment ledger. No extra dividends or second split adjustments are added. This specializes the earlier session-return alignment primitive to a future execution schedule; that same-close primitive is not the Phase 3 target.

Retrospective vendor adjustment/vintage risk remains. Tests prove absence of future-row dependencies in features conditional on frozen values, not historical real-time availability of vendor revisions. No slippage, fees, auction fills, borrow, delisting cash or holdings ledger is modeled.

## Independent masks

`eligible_at_t` equals unchanged Phase 2.5 `is_research_eligible`. Each `factor_available_NAME` uses only that factor's past/current inputs. `factor_available` means **all 17 raw factors** are finite, for a complete-feature matrix only; it does not govern individual-factor preprocessing. `processed_factor_available` means all 17 z-scores are available.

For each horizon, `entry_price_valid`, `exit_price_valid_hD` and `target_available_hD` are future label-quality flags. Endpoint validity requires the frozen Phase 2 valid-observation flag and finite positive vendor and adjusted opens. `sample_usable_for_research_hD = eligible_at_t & factor_available & target_available_hD`; the unsuffixed alias uses 5D. A processed complete-case consumer must additionally require `processed_factor_available`. Neither future endpoint flags nor complete-case masks may filter cross-sectional preprocessing. No future eligibility requirement is imposed.

Raw histories remain on the full calendar, including invalid/missing sessions. Cross-sectional transformations use only eligible-at-t, factor-specific finite values at t. Future targets are joined only after these transformations. Adjacent h-day targets overlap: later inference must address serial dependence, and a later portfolio phase must define overlapping cohorts explicitly. No IID assumption or portfolio result is made here.

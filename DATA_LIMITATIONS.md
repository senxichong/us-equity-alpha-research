# Data limitations and research gate

SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE

**Phase 1 decision: FAIL for safe progression to rigorous Phase 2.** The engineering sample works, but the historical investable population and terminal outcomes are not established. Passing schema tests does not remove economic bias.

## Blocking issues

1. **Historical membership is not certified.** The downloaded community candidate has 2,720 snapshots from 1996-01-02 through 2026-08-18, pinned to commit `a2430f2af0c79ddf0748e91de11bdeb1616ab5a7`. Four selected TSLA/FB/META membership checks pass. Its latest roster differs from the retrieved current roster by six symbols on each side. These are lists recorded as of event dates, not proof of historical publication/availability. Stable security IDs, a complete event audit and recent coverage are missing. No extrapolation is permitted beyond the candidate's last date. The upstream author also describes incomplete early membership and selected-change reconstruction: [source](https://github.com/fja05680/sp500). No certified Mode B is implemented.
2. **Dead securities and terminal proceeds are missing.** Direct Yahoo probes for TWTR and SIVBQ return HTTP 404. This does not prove all delisted symbols fail; it proves this pipeline has not solved the problem. Do not omit these securities from the denominator, assume a zero final return or carry the last price forever.
3. **A ticker is not a security ID.** FB returns a ProShares ETF, with 323 observations beginning 2025-06-26. META returns a backfilled series including the earlier Facebook period. Joining a historical FB universe to today's FB endpoint would use the wrong asset. CIK identifies an issuer, not necessarily a unique share class; a dated security master is required.
4. **Corporate-action and price truth remain imperfect.** Yahoo publishes non-integer events for GE/O within its split event channel. These cannot all be interpreted as ordinary changes in share count. Two issuer/exchange-backed split spot checks and internal dividend-factor checks do not certify spin-off economics, delisting payouts or executable prices.
5. **Cross-source discrepancy is unresolved.** IBM has 15 overlapping daily adjusted-return comparisons differing by more than one basis point, with a maximum of about 34.08 bp. Most flagged dates coincide with dividends, but 2019-08-12/13 also differ without dividends; differences cannot all be attributed to dividend conventions. Neither source is declared the ground truth and no silent patch/averaging is performed. Details are preserved in `reports/source_audit.json`.

## Non-blocking infrastructure caveats

- yfinance 1.7.0 returned `YFRateLimitError` for all 17 initial probes. The standard public chart endpoint worked; its quota and SLA are unknown. A bounded successful run is not a claim of production reliability. The final batch runner stops further requests after a rate-limit signal, caches failures and requires explicit refresh.
- AAPL repeated downloads have identical dates, OHLC, volume and event values, but Adj Close differs by up to 0.0000762939453125 USD. Archived snapshots are reproducible; fresh downloads are not guaranteed byte-identical.
- Stooq returned an HTML verification challenge, not market data. No challenge solving or access-control workaround was performed. Its adjustment semantics were not empirically established.
- Alpha Vantage's IBM public demo returned full historical data; the AAPL demo query returned an entitlement message. This does not establish free full-universe access. The adjusted daily endpoint is documented as premium; see [official documentation](https://www.alphavantage.co/documentation/).
- The primary 14-stock sample is deliberately selected to stress splits, reverse splits, extreme moves and distributions. It is not statistically representative and is not a 300–500 stock liquidity universe. GME may not belong to the current index and is included only as a diagnostic stress case.
- Main prices begin in 2018. The ideal 2010–present panel has not been downloaded or certified. The IBM demo has older history but does not fill this gap for other names.
- All sample prices are USD; vendor fields are not reconstructed as-traded history. Volume share-basis and historical market capitalization remain unverified. SEC shares tags exist, but report-period shares, diluted averages and current shares are different concepts.
- SEC fundamentals are available, but PIT fundamentals require filing/acceptance timing, accession and amendment controls. No fundamentals feature panel is built. SEC data alone supplies neither daily OHLCV nor a daily market-cap panel.
- Current Wikipedia and Nasdaq directories provide reference snapshots, not historical membership. Raw data is local and excluded from Git. Public accessibility does not imply a right to republish vendor datasets.

## Gate to reconsider after a separate instruction

Require validated membership through the chosen endpoint, dated permanent security identity mappings, delisted price/terminal-outcome coverage and a documented resolution policy for source disagreements and complex actions. The present prototype may demonstrate engineering mechanics only; it cannot substantiate unbiased historical alpha claims. Stop here; no Phase 2 work is authorized in this delivery.

## Subsequent authorization: Phase 2 prototype

The next user instruction explicitly authorizes Phase 2 using a prototype universe with `survivorship_biased=true`. Accordingly, the earlier stop applies to the historical Phase 1 delivery, and Phase 2 proceeds with that narrower scope. A Phase 2 PASS means the disclosed prototype panel satisfies its engineering and quality gates; it does not certify an unbiased population or resolve any of the historical identity/delisting limitations above.

Phase 2 expands the candidate history request to 2010 and isolates known-unresolved stocks, including IBM, rather than silently repairing them. Full-history anomaly screening itself causes selection bias; recent liquidity screening also looks ahead relative to early panel dates. Exclusions and their reasons are reported in full. See DATASET_CARD.md and reports/full_data_quality_report.md for actual delivered counts and coverage, which supersede the Phase 1 sample-size limitation only for the new panel.

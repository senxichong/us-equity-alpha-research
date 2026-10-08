# Sample data quality report

SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE

Generated UTC: 2026-10-08T08:06:43.859883+00:00

Source: Yahoo Finance via yfinance; auto_adjust=False, repair=False, keepna=True.
Requested [2018-01-01, 2026-10-08); last complete expected session: 2026-10-07.
Successful sample stocks: 0 / 14; observations: 0.
Failed sample tickers: ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'JPM', 'XOM', 'JNJ', 'NVDA', 'WMT', 'TSLA', 'GME', 'GE', 'O']
Missing values: {'ticker': 0, 'date': 0, 'open': 0, 'high': 0, 'low': 0, 'close': 0, 'adj_close': 0, 'volume': 0}
Issue counts: {}; duplicate excess rows: 0.
Unsorted tickers: []

|Ticker|Rows|First|Last|Missing expected sessions|
|---|---:|---|---|---:|
|AAPL|0|None|None|2203|
|MSFT|0|None|None|2203|
|AMZN|0|None|None|2203|
|GOOGL|0|None|None|2203|
|META|0|None|None|2203|
|JPM|0|None|None|2203|
|XOM|0|None|None|2203|
|JNJ|0|None|None|2203|
|NVDA|0|None|None|2203|
|WMT|0|None|None|2203|
|TSLA|0|None|None|2203|
|GME|0|None|None|2203|
|GE|0|None|None|2203|
|O|0|None|None|2203|

Coverage compares the full requested calendar. Missing dates are observations to investigate, not automatically vendor errors (listing history/halts may matter). No rows were dropped or filled.

Split events: 0; dividend events: 0.
Dividend factor checks outside tolerance: 0.

|Ticker|Split date|New/old shares|Close change|Adjusted close change|
|---|---|---:|---:|---:|

## Symbol / delisting probes

- FB: failed; 0 rows;  to . Errors: ['YFRateLimitError: Too Many Requests. Rate limited. Try after a while.']
- TWTR: failed; 0 rows;  to . Errors: ['YFRateLimitError: Too Many Requests. Rate limited. Try after a while.']
- SIVBQ: failed; 0 rows;  to . Errors: ['YFRateLimitError: Too Many Requests. Rate limited. Try after a while.']

## Interpretation and limitations

Corporate-action checks test vendor consistency, not an independently audited corporate-action ledger. Yahoo Close is split-adjusted, not an as-traded execution price. Current snapshots can be revised. Extreme observed price changes are flags, not proof of bad data. Symbol identity, delisting proceeds, spin-offs, and reliable historical membership remain unresolved. See DATA_CONVENTIONS.md and DATA_LIMITATIONS.md.

Full machine-readable evidence: reports\runs\20261008T080643826863Z; normalized data: data\processed\20261008T080643826863Z.

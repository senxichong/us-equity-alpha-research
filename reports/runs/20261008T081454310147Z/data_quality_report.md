# Sample data quality report

SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE

Generated UTC: 2026-10-08T08:14:54.408789+00:00

Source: yahoo_chart; vendor fields retained without repair or automatic adjustment.
Requested [2018-01-01, 2026-10-08); last complete expected session: 2026-10-07.
Successful sample stocks: 14 / 14; observations: 30842.
Failed sample tickers: []
Missing values: {'ticker': 0, 'date': 0, 'open': 0, 'high': 0, 'low': 0, 'close': 0, 'adj_close': 0, 'volume': 0}
Issue counts: {'extreme_observed_adj_close_change': 15}; duplicate excess rows: 0.
Unsorted tickers: []

|Ticker|Rows|First|Last|Missing expected sessions|
|---|---:|---|---|---:|
|AAPL|2203|2018-01-02|2026-10-07|0|
|MSFT|2203|2018-01-02|2026-10-07|0|
|AMZN|2203|2018-01-02|2026-10-07|0|
|GOOGL|2203|2018-01-02|2026-10-07|0|
|META|2203|2018-01-02|2026-10-07|0|
|JPM|2203|2018-01-02|2026-10-07|0|
|XOM|2203|2018-01-02|2026-10-07|0|
|JNJ|2203|2018-01-02|2026-10-07|0|
|NVDA|2203|2018-01-02|2026-10-07|0|
|WMT|2203|2018-01-02|2026-10-07|0|
|TSLA|2203|2018-01-02|2026-10-07|0|
|GME|2203|2018-01-02|2026-10-07|0|
|GE|2203|2018-01-02|2026-10-07|0|
|O|2203|2018-01-02|2026-10-07|0|

Coverage compares the full requested calendar. Missing dates are observations to investigate, not automatically vendor errors (listing history/halts may matter). No rows were dropped or filled.

Split events: 14; dividend events: 412.
Dividend factor checks outside tolerance: 0.

|Ticker|Split date|New/old shares|Close change|Adjusted close change|
|---|---|---:|---:|---:|
|AAPL|2020-08-31|4.0|0.033912|0.033912|
|AMZN|2022-06-06|20.0|0.019943|0.019943|
|GE|2019-02-26|1.04|0.024621|0.024621|
|GE|2021-08-02|0.125|-0.028958|-0.028958|
|GE|2023-01-04|1.281|0.058204|0.058204|
|GE|2024-04-02|1.253|-0.024881|-0.024881|
|GME|2022-07-22|4.0|-0.067440|-0.067440|
|GOOGL|2022-07-18|20.0|-0.024580|-0.024580|
|NVDA|2021-07-20|4.0|-0.008933|-0.008933|
|NVDA|2024-06-10|10.0|0.007461|0.007462|
|O|2021-11-15|1.032|0.009300|0.009300|
|TSLA|2020-08-31|5.0|0.125689|0.125689|
|TSLA|2022-08-25|3.0|-0.003456|-0.003456|
|WMT|2024-02-26|3.0|0.018455|0.018455|

## Symbol / delisting probes

- FB: ok; 323 rows; 2025-06-26 09:30:00-04:00 to 2026-10-07 09:30:00-04:00. Identity: ProShares S&P 500 Dynamic Daily Buffer ETF / ETF. Errors: []
- TWTR: failed; 0 rows;  to . Identity: unavailable / unavailable. Errors: ['HTTPError: 404 Client Error: Not Found for url: https://query1.finance.yahoo.com/v8/finance/chart/TWTR?period1=1514764800&period2=1791417600&interval=1d&events=div%2Csplits']
- SIVBQ: failed; 0 rows;  to . Identity: unavailable / unavailable. Errors: ['HTTPError: 404 Client Error: Not Found for url: https://query1.finance.yahoo.com/v8/finance/chart/SIVBQ?period1=1514764800&period2=1791417600&interval=1d&events=div%2Csplits']

## Interpretation and limitations

Corporate-action checks test vendor consistency, not an independently audited corporate-action ledger. Yahoo Close is split-adjusted, not an as-traded execution price. Current snapshots can be revised. Extreme observed price changes are flags, not proof of bad data. Symbol identity, delisting proceeds, spin-offs, and reliable historical membership remain unresolved. See DATA_CONVENTIONS.md and DATA_LIMITATIONS.md.

Full machine-readable evidence: reports\runs\20261008T081454310147Z; normalized data: data\processed\20261008T081454310147Z.

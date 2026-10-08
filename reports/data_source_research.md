# Data-source feasibility — observed 2026-10-08 (Asia/Shanghai)

SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE

Sources were actually requested from this machine. HTTP payloads and hashes are retained in `data/raw/probes/`; observations below come from `source_probes.json`, sample manifests and `source_audit.json`. HTTP success and usable financial data are reported separately.

| Source | Observed result | Role / decision |
|---|---|---|
| Yahoo via yfinance 1.7.0 | All 14 sample and 3 diagnostic tickers raised rate-limit errors in the initial run. No successful yfinance prices. | Adapter retained and failure snapshots preserved; not the working transport. |
| Yahoo public chart via requests | 14/14 main stocks, 2,203 rows each, including adjusted close and events. Additional IBM cross-check successful. FB is an ETF; TWTR and SIVBQ return 404. | Recommend only for local prototype data engineering. Original JSON and Parquet saved; no auth/cookie workaround. |
| Stooq CSV | HTTP 200, HTML browser challenge, zero validated price observations. Initial generic CSV parsing wrongly saw HTML lines as rows; the corrected detector explicitly rejects them. | Unavailable through tested automated interface. Adjustment definitions remain unverified. |
| Alpha Vantage | IBM demo compact: 100 rows; full: 6,774 rows, 1999-11-01 to 2026-10-07. AAPL demo: zero observations and a key/entitlement message. | Legal public demonstration/cross-check; not evidence of access to a broad universe. |
| SEC EDGAR | Apple Companyfacts and Submissions both HTTP 200; Companyfacts has 503 US-GAAP tags and 2 DEI tags. | Future fundamentals and reported shares source, not a daily OHLCV source. |
| Nasdaq Trader | Current directory HTTP 200, 5,629 lines including header/footer. | Additional official public reference data; contains multiple security types and no historical membership guarantee. |
| Wikipedia current S&P 500 | Parsed 503 security rows. | Mode A reference only, prominently biased when used historically. |
| Community historical S&P 500 | Downloaded pinned candidate, 2,720 lists from 1996-01-02 to 2026-08-18. Selected official-date checks pass; complete PIT suitability is unproven. | Audited candidate only; Mode B deliberately blocked. |

## Definitions, access and frequency

[yfinance documentation](https://ranaroussi.github.io/yfinance/) describes an unofficial research/educational interface and points users to Yahoo's data-use terms. The library license is not a market-data redistribution license. The tested public Yahoo endpoint has no verified fixed quota. Requests were sequential and paced; no intentional rate-limit saturation was performed. The first yfinance implementation attempted each listed symbol once; after observing the batch-wide failure, the final runner gained a global circuit breaker. Direct chart worked through ordinary HTTP after the library failure; stability is only demonstrated for this bounded test.

[Alpha Vantage daily adjusted documentation](https://www.alphavantage.co/documentation/) distinguishes as-traded OHLCV from adjusted close and action fields and labels the adjusted daily service premium. Its [support page](https://www.alphavantage.co/support/) advertises a standard 25-request/day free tier, subject to eligibility and endpoint access; a demo key is not a full account. No paid request or account creation was made. IBM data arrives newest-first; validation flags this order, while comparisons explicitly sort a copy.

[SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) supports company-level facts and submissions. [SEC developer resources](https://www.sec.gov/about/developer-resources) describe fair access, including a 10-request/second ceiling. This run made just two sequential company requests. The real payload contains `EntityCommonStockSharesOutstanding` and `CommonStockSharesOutstanding`; these are not interchangeable with weighted-average diluted shares. Accession, filing/acceptance time, units, frame/context and revisions must be retained before future use. Market cap needs a properly aligned security price and share count; none is derived here.

[Nasdaq directory definitions](https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs) describe symbol, security name, test flags and ETF fields. The retrieved current directory can help check current identity; it does not provide an investable list for 2010.

[Historical candidate repository](https://github.com/fja05680/sp500) supplies its update code and an MIT license file, both saved with the pinned data. Its history combines a book-associated base dataset with subsequent manually researched changes. Neither repository licensing nor selected successful checks establishes full data provenance, announcement timestamps, or authoritative security identifiers. No candidate has been promoted to certified PIT status.

## Observed stability and independent comparison

One explicit AAPL re-download preserved dates/OHLC/volume/events but changed Adj Close slightly (maximum 0.0000762939453125 USD). Both snapshots remain available. A subsequent cached pipeline run read all main and diagnostic snapshots without network calls.

IBM Alpha Vantage and Yahoo overlap on 2,203 dates. Daily adjusted-return differences exceed 1 bp on 15 dates; the maximum is 34.082896 bp. The median absolute difference is approximately 0.000850 bp. Dividend methodology explains a plausible part, not every difference. No provider is silently treated as authoritative. Full mismatch rows are in `source_audit.json`.

The recommendation is therefore a usable **prototype source**, not a claim that any tested free source supplies a complete, unbiased US-equity research database.

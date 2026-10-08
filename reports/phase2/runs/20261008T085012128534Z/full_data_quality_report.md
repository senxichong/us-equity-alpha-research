# Full dataset quality report

SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE — survivorship_biased = true

Dataset: 20261008T085012128534Z
Candidates: 503; validated: 393; selected: 393; quarantined: 109; download/processing failures: 1.
Dates: 2010-01-04 to 2026-10-07; exchange sessions: 4216.
Panel rows: 1563421; observed rows: 1563421; valid observations: 1563389; explicit missing/nontrading rows: 32.
Active-grid missing rate: 2.0467935380169512e-05; pre-history slots omitted: 93467.
Selected vendor split events: 118; dividends: 18905; complex-action events admitted: 0; dividend-factor mismatches admitted: 0.

## Admission / missing-data policy

Severe schema/price/date defects, unexplained late starts, excessive active gaps, short history, unreconciled extreme changes, complex distributions and dividend-factor mismatches quarantine the entire ticker. No failed ticker enters the panel. Missing sessions for admitted securities are explicit null rows; zero volume is nontradable. No forward/backward fill. Rows before the first available listing/history are not created. has_minimum_history counts valid observations available through that date; future factor windows still need their own missing-window rules.

The liquidity screen uses the latest configured window, so it introduces selection look-ahead for historical analysis. Full-period quality exclusions introduce additional selection bias. CIK is issuer reference metadata, not a verified permanent security identifier.

## Quarantine reasons (a ticker can have several)

- active_missing_rate: 4
- dividend_factor_mismatch: 3
- known_unresolved_cross_source_discrepancy: 1
- missing_required_value: 1
- ohlc_violation: 1
- short_history: 4
- unreviewed_extreme_change: 26
- unverified_noninteger_distribution_event: 79

## Download / processing failures

- AMCR: download_failed_or_not_attempted 

Full errors and original responses remain in download_failures.json and raw/full; no ticker renaming or substitution is guessed.

## Per-stock coverage and admission

|Ticker|Status|Selected|Rows|First|Last|Full-calendar coverage|Active coverage|Raw missing rate|Pre-history sessions|Reasons|
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
|A|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|AAPL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ABBV|selected|True|3462|2013-01-02|2026-10-07|82.1157%|100.0000%|0.0000%|754||
|ABNB|selected|True|1462|2020-12-10|2026-10-07|34.6774%|100.0000%|0.0000%|2754||
|ABT|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ACGL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ACN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ADBE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ADI|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ADM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ADP|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ADSK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AEE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AEP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AES|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AFL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AIG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AIZ|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AJG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AKAM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ALB|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ALGN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ALL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ALLE|selected|True|3240|2013-11-18|2026-10-07|76.8501%|100.0000%|0.0000%|976||
|AMAT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AMD|quarantined|False|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0|unreviewed_extreme_change|
|AME|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|AMGN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AMP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AMT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AMZN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ANET|selected|True|3103|2014-06-06|2026-10-07|73.6006%|100.0000%|0.0000%|1113||
|AON|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AOS|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|APA|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change|
|APD|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|APH|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|APO|selected|True|3904|2011-03-30|2026-10-07|92.5996%|100.0000%|0.0000%|312||
|APP|quarantined|False|1377|2021-04-15|2026-10-07|32.6613%|100.0000%|0.0000%|2839|unreviewed_extreme_change|
|APTV|quarantined|False|3742|2011-11-17|2026-10-07|88.7571%|100.0000%|0.0000%|474|unverified_noninteger_distribution_event|
|ARE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ARES|selected|True|3127|2014-05-02|2026-10-07|74.1698%|100.0000%|0.0000%|1089||
|ATO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AVGO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AVY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AWK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AXON|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AXP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|AZO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BAC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BALL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BAX|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|BBY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BDX|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|BE|quarantined|False|2062|2018-07-25|2026-10-07|48.9089%|100.0000%|0.0000%|2154|unreviewed_extreme_change|
|BEN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BF-B|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|BG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BIIB|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change|
|BKNG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BKR|selected|True|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0||
|BLK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BMY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BNY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BRK-B|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BRO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BSX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|BXP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|C|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CAH|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CARR|selected|True|1647|2020-03-19|2026-10-07|39.0655%|100.0000%|0.0000%|2569||
|CASY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CAT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CB|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CBOE|selected|True|4104|2010-06-15|2026-10-07|97.3435%|100.0000%|0.0000%|112||
|CBRE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CCI|selected|True|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0||
|CCL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CDNS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CDW|selected|True|3340|2013-06-27|2026-10-07|79.2220%|100.0000%|0.0000%|876||
|CEG|selected|True|1184|2022-01-19|2026-10-07|28.0835%|100.0000%|0.0000%|3032||
|CF|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CFG|selected|True|3027|2014-09-24|2026-10-07|71.7979%|100.0000%|0.0000%|1189||
|CHD|selected|True|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0||
|CHRW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CHTR|selected|True|4215|2010-01-05|2026-10-07|99.5493%|99.5730%|0.0000%|1||
|CI|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CIEN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CINF|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CLX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CMCSA|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|dividend_factor_mismatch, unverified_noninteger_distribution_event|
|CME|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CMG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CMI|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CMS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CNC|quarantined|False|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0|unreviewed_extreme_change|
|CNP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|COF|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|COHR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|COIN|selected|True|1378|2021-04-14|2026-10-07|32.6850%|100.0000%|0.0000%|2838||
|COO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|COP|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|COR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|COST|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CPAY|selected|True|3976|2010-12-15|2026-10-07|94.3074%|100.0000%|0.0000%|240||
|CPRT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CPT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CRH|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CRL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CRM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CRWD|selected|True|1841|2019-06-12|2026-10-07|43.6670%|100.0000%|0.0000%|2375||
|CSCO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CSGP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CSX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CTAS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CTSH|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CVNA|quarantined|False|2374|2017-04-28|2026-10-07|56.3093%|100.0000%|0.0000%|1842|unreviewed_extreme_change|
|CVS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|CVX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|D|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DAL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DASH|selected|True|1463|2020-12-09|2026-10-07|34.7011%|100.0000%|0.0000%|2753||
|DD|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|DDOG|selected|True|1772|2019-09-19|2026-10-07|42.0304%|100.0000%|0.0000%|2444||
|DE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DECK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DELL|quarantined|False|2549|2016-08-17|2026-10-07|60.4602%|100.0000%|0.0000%|1667|unverified_noninteger_distribution_event|
|DG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DGX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DHI|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DHR|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change, unverified_noninteger_distribution_event|
|DIS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DLR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DLTR|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|DOC|quarantined|False|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0|unverified_noninteger_distribution_event|
|DOV|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|DOW|selected|True|1899|2019-03-20|2026-10-07|45.0427%|100.0000%|0.0000%|2317||
|DPZ|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DRI|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|DTE|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|DUK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DVA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DVN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|DXCM|quarantined|False|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0|unreviewed_extreme_change|
|EBAY|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ECHO|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change, unverified_noninteger_distribution_event|
|ECL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ED|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EFX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EIX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ELV|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EME|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EMR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EOG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EQIX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EQT|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ERIE|selected|True|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0||
|ES|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ESS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ETN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ETR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EVRG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EXC|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|EXE|selected|True|1421|2021-02-10|2026-10-07|33.7049%|100.0000%|0.0000%|2795||
|EXPD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EXPE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|EXR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|F|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FANG|quarantined|False|3515|2012-10-12|2026-10-07|83.3729%|100.0000%|0.0000%|701|unreviewed_extreme_change|
|FAST|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FCX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FDS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FDX|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|FDXF|quarantined|False|93|2026-05-27|2026-10-07|2.2059%|100.0000%|0.0000%|4123|short_history|
|FE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FERG|quarantined|False|4215|2010-01-05|2026-10-07|50.6641%|50.6762%|0.0000%|1|active_missing_rate, unverified_noninteger_distribution_event|
|FFIV|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FICO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FIS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FISV|quarantined|False|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0178%|0|missing_required_value, unreviewed_extreme_change|
|FITB|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FIX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FLEX|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|FOX|selected|True|1904|2019-03-13|2026-10-07|45.1613%|100.0000%|0.0000%|2312||
|FOXA|selected|True|1905|2019-03-12|2026-10-07|45.1850%|100.0000%|0.0000%|2311||
|FRT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FSLR|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change|
|FTNT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|FTV|quarantined|False|2580|2016-07-05|2026-10-07|61.1954%|100.0000%|0.0000%|1636|unverified_noninteger_distribution_event|
|GD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|GDDY|selected|True|2898|2015-03-31|2026-10-07|68.7144%|99.9655%|0.0000%|1318||
|GE|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|GEHC|selected|True|955|2022-12-15|2026-10-07|22.6518%|100.0000%|0.0000%|3261||
|GEN|selected|True|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0||
|GEV|selected|True|635|2024-03-27|2026-10-07|15.0617%|100.0000%|0.0000%|3581||
|GILD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|GIS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|GL|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|dividend_factor_mismatch, unreviewed_extreme_change, unverified_noninteger_distribution_event|
|GLW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|GM|selected|True|3994|2010-11-18|2026-10-07|94.7343%|100.0000%|0.0000%|222||
|GNRC|selected|True|4189|2010-02-11|2026-10-07|99.3596%|100.0000%|0.0000%|27||
|GOOG|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|GOOGL|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|GPC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|GPN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|GRMN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|GS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|GWW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HAL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HAS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HBAN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HCA|selected|True|3918|2011-03-10|2026-10-07|92.9317%|100.0000%|0.0000%|298||
|HD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HIG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HII|selected|True|3910|2011-03-22|2026-10-07|92.7419%|100.0000%|0.0000%|306||
|HLT|quarantined|False|3223|2013-12-12|2026-10-07|76.4469%|100.0000%|0.0000%|993|unverified_noninteger_distribution_event|
|HON|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|HONA|quarantined|False|80|2026-06-15|2026-10-07|1.8975%|100.0000%|0.0000%|4136|short_history|
|HOOD|quarantined|False|1304|2021-07-29|2026-10-07|30.9298%|100.0000%|0.0000%|2912|unreviewed_extreme_change|
|HPE|quarantined|False|2758|2015-10-19|2026-10-07|65.4175%|100.0000%|0.0000%|1458|unverified_noninteger_distribution_event|
|HPQ|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|HRL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HSIC|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|HST|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HSY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HUBB|quarantined|False|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0|ohlc_violation|
|HUM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|HWM|quarantined|False|2496|2016-11-01|2026-10-07|58.3729%|98.5978%|0.0000%|1720|active_missing_rate|
|IBKR|selected|True|4216|2010-01-04|2026-10-07|99.9526%|99.9526%|0.0000%|0||
|IBM|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|known_unresolved_cross_source_discrepancy, unverified_noninteger_distribution_event|
|ICE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|IDXX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|IEX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|IFF|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ILMN|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change, unverified_noninteger_distribution_event|
|INCY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|INTC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|INTU|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|INVH|selected|True|2434|2017-02-01|2026-10-07|57.7324%|100.0000%|0.0000%|1782||
|IP|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|IQV|selected|True|3374|2013-05-09|2026-10-07|80.0285%|100.0000%|0.0000%|842||
|IR|selected|True|2364|2017-05-12|2026-10-07|56.0721%|100.0000%|0.0000%|1852||
|IRM|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ISRG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|IT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ITW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|IVZ|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|J|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|JBHT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|JBL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|JCI|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|JKHY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|JNJ|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|JPM|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|dividend_factor_mismatch|
|KDP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|KEY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|KEYS|selected|True|3009|2014-10-20|2026-10-07|71.3710%|100.0000%|0.0000%|1207||
|KHC|selected|True|2832|2015-07-06|2026-10-07|67.1727%|100.0000%|0.0000%|1384||
|KIM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|KKR|selected|True|4083|2010-07-15|2026-10-07|96.8454%|100.0000%|0.0000%|133||
|KLAC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|KMB|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|KMI|selected|True|3936|2011-02-11|2026-10-07|93.3586%|100.0000%|0.0000%|280||
|KO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|KR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|KVUE|selected|True|860|2023-05-04|2026-10-07|20.3985%|100.0000%|0.0000%|3356||
|L|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LDOS|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|LEN|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|LH|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|LHX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LII|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LIN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LITE|selected|True|2819|2015-07-23|2026-10-07|66.8643%|100.0000%|0.0000%|1397||
|LLY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LMT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LNT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LOW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LRCX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LULU|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LUV|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LVS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|LYB|selected|True|4137|2010-04-28|2026-10-07|98.1262%|100.0000%|0.0000%|79||
|LYV|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MAA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MAR|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|MAS|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|MCD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MCHP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MCK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MCO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MDLZ|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MDT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MET|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|META|selected|True|3617|2012-05-18|2026-10-07|85.7922%|100.0000%|0.0000%|599||
|MGM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MKC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MLM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MMM|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|MNST|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MOS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MPC|selected|True|3844|2011-06-24|2026-10-07|91.1765%|100.0000%|0.0000%|372||
|MPWR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MRK|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|MRNA|quarantined|False|1968|2018-12-07|2026-10-07|46.6793%|100.0000%|0.0000%|2248|unreviewed_extreme_change|
|MRSH|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MRVL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MSCI|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MSFT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MSI|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|MTB|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MTD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|MU|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NCLH|quarantined|False|3450|2013-01-18|2026-10-07|81.8311%|100.0000%|0.0000%|766|unreviewed_extreme_change|
|NDAQ|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NDSN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NEE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NEM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NFLX|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change|
|NI|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|NKE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NOC|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|NOW|selected|True|3588|2012-06-29|2026-10-07|85.1044%|100.0000%|0.0000%|628||
|NRG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NSC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NTAP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NTRS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NUE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NVDA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NVR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|NWS|selected|True|3346|2013-06-19|2026-10-07|79.3643%|100.0000%|0.0000%|870||
|NWSA|selected|True|3346|2013-06-19|2026-10-07|79.3643%|100.0000%|0.0000%|870||
|NXPI|selected|True|4067|2010-08-06|2026-10-07|96.4658%|100.0000%|0.0000%|149||
|O|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ODFL|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|OKE|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|OMC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ON|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ORCL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ORLY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|OTIS|selected|True|1647|2020-03-19|2026-10-07|39.0655%|100.0000%|0.0000%|2569||
|OXY|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change, unverified_noninteger_distribution_event|
|P|selected|True|2767|2015-10-06|2026-10-07|65.6072%|99.9639%|0.0000%|1449||
|PANW|selected|True|3574|2012-07-20|2026-10-07|84.7723%|100.0000%|0.0000%|642||
|PAYX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PCAR|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|PCG|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change|
|PEG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PEP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PFE|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|PFG|selected|True|4216|2010-01-04|2026-10-07|99.9526%|99.9526%|0.0000%|0||
|PG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PGR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PH|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PHM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PKG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PLD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PLTR|selected|True|1512|2020-09-30|2026-10-07|35.8634%|100.0000%|0.0000%|2704||
|PM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PNC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PNR|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|PNW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PODD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PPG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PPL|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|PRU|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PSA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PSX|selected|True|3643|2012-04-12|2026-10-07|86.4089%|100.0000%|0.0000%|573||
|PTC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PWR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|PYPL|selected|True|2832|2015-07-06|2026-10-07|67.1727%|100.0000%|0.0000%|1384||
|Q|quarantined|False|238|2025-10-27|2026-10-07|5.6452%|100.0000%|0.0000%|3978|short_history|
|QCOM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|RCL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|RDDT|quarantined|False|639|2024-03-21|2026-10-07|15.1565%|100.0000%|0.0000%|3577|unreviewed_extreme_change|
|REG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|REGN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|RF|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|RJF|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|RL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|RMD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ROK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ROL|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ROP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ROST|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|RSG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|RTX|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|RVTY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SBAC|selected|True|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0||
|SBUX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SCHW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SHW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SJM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SKYD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SLB|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SMCI|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change|
|SNA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SNDK|selected|True|414|2025-02-13|2026-10-07|9.8197%|100.0000%|0.0000%|3802||
|SNPS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SOLV|selected|True|636|2024-03-26|2026-10-07|15.0854%|100.0000%|0.0000%|3580||
|SPG|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|SPGI|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|SRE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|STE|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|STLD|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|STT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|STX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|STZ|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SW|quarantined|False|4216|2010-01-04|2026-10-07|42.8605%|42.8605%|0.0000%|0|active_missing_rate|
|SWK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SWKS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SYF|selected|True|3065|2014-07-31|2026-10-07|72.6992%|100.0000%|0.0000%|1151||
|SYK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|SYY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|T|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|TDG|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TDY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TECH|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TEL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TER|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TFC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TGT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TJX|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TKO|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unreviewed_extreme_change|
|TMO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TMUS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TPL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TPR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TRGP|quarantined|False|3982|2010-12-07|2026-10-07|94.4497%|100.0000%|0.0000%|234|unreviewed_extreme_change|
|TRMB|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TROW|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TRV|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TSCO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TSLA|selected|True|4094|2010-06-29|2026-10-07|97.1063%|100.0000%|0.0000%|122||
|TSN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TT|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|TTWO|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TWLO|selected|True|2587|2016-06-23|2026-10-07|61.3615%|100.0000%|0.0000%|1629||
|TXN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TXT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|TYL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|UAL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|UBER|selected|True|1863|2019-05-10|2026-10-07|44.1888%|100.0000%|0.0000%|2353||
|UDR|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|UHS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ULTA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|UNH|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|UNP|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|UPS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|URI|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|USB|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|V|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|VEEV|selected|True|3263|2013-10-16|2026-10-07|77.3956%|100.0000%|0.0000%|953||
|VICI|selected|True|2203|2018-01-02|2026-10-07|52.2533%|100.0000%|0.0000%|2013||
|VLO|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|VLTO|selected|True|755|2023-10-04|2026-10-07|17.9080%|100.0000%|0.0000%|3461||
|VMC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|VMRK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|VRSK|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|VRSN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|VRT|quarantined|False|2056|2018-08-02|2026-10-07|48.4820%|99.4163%|0.0000%|2160|active_missing_rate|
|VRTX|quarantined|False|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0|unreviewed_extreme_change|
|VST|selected|True|2515|2016-10-05|2026-10-07|59.6300%|99.9602%|0.0000%|1701||
|VTR|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|VTRS|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|VYLR|quarantined|False|5|2026-10-01|2026-10-07|0.1186%|100.0000%|0.0000%|4211|short_history|
|VZ|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|WAB|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WAT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WDAY|selected|True|3515|2012-10-12|2026-10-07|83.3729%|100.0000%|0.0000%|701||
|WDC|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|WEC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WELL|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WFC|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WMB|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|WMT|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WRB|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|WSM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WST|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WTW|quarantined|False|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0|unverified_noninteger_distribution_event|
|WY|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|WYNN|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|XEL|selected|True|4216|2010-01-04|2026-10-07|99.9763%|99.9763%|0.0000%|0||
|XOM|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|XYL|selected|True|3767|2011-10-13|2026-10-07|89.3501%|100.0000%|0.0000%|449||
|XYZ|selected|True|2735|2015-11-19|2026-10-07|64.8719%|100.0000%|0.0000%|1481||
|YUM|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ZBH|quarantined|False|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0|unverified_noninteger_distribution_event|
|ZBRA|selected|True|4216|2010-01-04|2026-10-07|100.0000%|100.0000%|0.0000%|0||
|ZTS|selected|True|3441|2013-02-01|2026-10-07|81.6176%|100.0000%|0.0000%|775||

Per-security event dates/ratios/dividend-factor residuals are in stock_quality.json. Exact anomalous rows and per-stock missing dates are in validation_details.json. Daily breadth is in daily_coverage.parquet.

## Known bias and limits

Current membership and recent liquidity create survivorship/selection bias. Delisted returns and permanent identity mapping remain unavailable. Yahoo adjusted values are snapshot proxies, not as-traded execution history. No corporate-action cash ledger or PIT fundamentals. Latest HTTP availability does not establish the true historical information set. A passing dataset gate means only a validated prototype research input.

Panel: data\processed\phase2\20261008T085012128534Z\research_panel.parquet; SHA-256: c7d672b8991802be43f024d4651564a4fe5f0a5e5f8b7c664ff42dc9fb5fae61.

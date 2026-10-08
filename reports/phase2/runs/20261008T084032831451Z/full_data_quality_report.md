# Full dataset quality report

SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE — survivorship_biased = true

Dataset: 20261008T084032831451Z
Candidates: 503; validated: 250; selected: 250; quarantined: 71; download/processing failures: 182.
Dates: 2010-01-04 to 2026-10-07; exchange sessions: 4216.
Panel rows: 996542; observed rows: 996542; valid observations: 996517; explicit missing/nontrading rows: 25.
Active-grid missing rate: 2.5086749981435804e-05; pre-history slots omitted: 57458.
Selected vendor split events: 81; dividends: 12147; complex-action events admitted: 0; dividend-factor mismatches admitted: 0.

## Admission / missing-data policy

Severe schema/price/date defects, unexplained late starts, excessive active gaps, short history, unreconciled extreme changes, complex distributions and dividend-factor mismatches quarantine the entire ticker. No failed ticker enters the panel. Missing sessions for admitted securities are explicit null rows; zero volume is nontradable. No forward/backward fill. Rows before the first available listing/history are not created. has_minimum_history counts valid observations available through that date; future factor windows still need their own missing-window rules.

The liquidity screen uses the latest configured window, so it introduces selection look-ahead for historical analysis. Full-period quality exclusions introduce additional selection bias. CIK is issuer reference metadata, not a verified permanent security identifier.

## Quarantine reasons (a ticker can have several)

- active_missing_rate: 2
- dividend_factor_mismatch: 3
- known_unresolved_cross_source_discrepancy: 1
- missing_required_value: 1
- ohlc_violation: 1
- short_history: 2
- unreviewed_extreme_change: 17
- unverified_noninteger_distribution_event: 53

## Download / processing failures

- AMCR: download_failed_or_not_attempted 
- BBY: download_failed_or_not_attempted 
- ERIE: download_failed_or_not_attempted 
- NCLH: download_failed_or_not_attempted 
- NDAQ: download_failed_or_not_attempted 
- NDSN: download_failed_or_not_attempted 
- NEE: download_failed_or_not_attempted 
- NEM: download_failed_or_not_attempted 
- NFLX: download_failed_or_not_attempted 
- NI: download_failed_or_not_attempted 
- NKE: download_failed_or_not_attempted 
- NOC: download_failed_or_not_attempted 
- NOW: download_failed_or_not_attempted 
- NRG: download_failed_or_not_attempted 
- NSC: download_failed_or_not_attempted 
- NTAP: download_failed_or_not_attempted 
- NTRS: download_failed_or_not_attempted 
- NUE: download_failed_or_not_attempted 
- NVDA: download_failed_or_not_attempted 
- NVR: download_failed_or_not_attempted 
- NWS: download_failed_or_not_attempted 
- NWSA: download_failed_or_not_attempted 
- NXPI: download_failed_or_not_attempted 
- O: download_failed_or_not_attempted 
- ODFL: download_failed_or_not_attempted 
- OKE: download_failed_or_not_attempted 
- OMC: download_failed_or_not_attempted 
- ON: download_failed_or_not_attempted 
- ORCL: download_failed_or_not_attempted 
- ORLY: download_failed_or_not_attempted 
- OTIS: download_failed_or_not_attempted 
- OXY: download_failed_or_not_attempted 
- P: download_failed_or_not_attempted 
- PANW: download_failed_or_not_attempted 
- PAYX: download_failed_or_not_attempted 
- PCAR: download_failed_or_not_attempted 
- PCG: download_failed_or_not_attempted 
- PEG: download_failed_or_not_attempted 
- PEP: download_failed_or_not_attempted 
- PFE: download_failed_or_not_attempted 
- PFG: download_failed_or_not_attempted 
- PG: download_failed_or_not_attempted 
- PGR: download_failed_or_not_attempted 
- PH: download_failed_or_not_attempted 
- PHM: download_failed_or_not_attempted 
- PKG: download_failed_or_not_attempted 
- PLD: download_failed_or_not_attempted 
- PLTR: download_failed_or_not_attempted 
- PM: download_failed_or_not_attempted 
- PNC: download_failed_or_not_attempted 
- PNR: download_failed_or_not_attempted 
- PNW: download_failed_or_not_attempted 
- PODD: download_failed_or_not_attempted 
- PPG: download_failed_or_not_attempted 
- PPL: download_failed_or_not_attempted 
- PRU: download_failed_or_not_attempted 
- PSA: download_failed_or_not_attempted 
- PSX: download_failed_or_not_attempted 
- PTC: download_failed_or_not_attempted 
- PWR: download_failed_or_not_attempted 
- PYPL: download_failed_or_not_attempted 
- Q: download_failed_or_not_attempted 
- QCOM: download_failed_or_not_attempted 
- RCL: download_failed_or_not_attempted 
- RDDT: download_failed_or_not_attempted 
- REG: download_failed_or_not_attempted 
- REGN: download_failed_or_not_attempted 
- RF: download_failed_or_not_attempted 
- RJF: download_failed_or_not_attempted 
- RL: download_failed_or_not_attempted 
- RMD: download_failed_or_not_attempted 
- ROK: download_failed_or_not_attempted 
- ROL: download_failed_or_not_attempted 
- ROP: download_failed_or_not_attempted 
- ROST: download_failed_or_not_attempted 
- RSG: download_failed_or_not_attempted 
- RTX: download_failed_or_not_attempted 
- RVTY: download_failed_or_not_attempted 
- SBAC: download_failed_or_not_attempted 
- SBUX: download_failed_or_not_attempted 
- SCHW: download_failed_or_not_attempted 
- SHW: download_failed_or_not_attempted 
- SJM: download_failed_or_not_attempted 
- SKYD: download_failed_or_not_attempted 
- SLB: download_failed_or_not_attempted 
- SMCI: download_failed_or_not_attempted 
- SNA: download_failed_or_not_attempted 
- SNDK: download_failed_or_not_attempted 
- SNPS: download_failed_or_not_attempted 
- SO: download_failed_or_not_attempted 
- SOLV: download_failed_or_not_attempted 
- SPG: download_failed_or_not_attempted 
- SPGI: download_failed_or_not_attempted 
- SRE: download_failed_or_not_attempted 
- STE: download_failed_or_not_attempted 
- STLD: download_failed_or_not_attempted 
- STT: download_failed_or_not_attempted 
- STX: download_failed_or_not_attempted 
- STZ: download_failed_or_not_attempted 
- SW: download_failed_or_not_attempted 
- SWK: download_failed_or_not_attempted 
- SWKS: download_failed_or_not_attempted 
- SYF: download_failed_or_not_attempted 
- SYK: download_failed_or_not_attempted 
- SYY: download_failed_or_not_attempted 
- T: download_failed_or_not_attempted 
- TDG: download_failed_or_not_attempted 
- TDY: download_failed_or_not_attempted 
- TECH: download_failed_or_not_attempted 
- TEL: download_failed_or_not_attempted 
- TER: download_failed_or_not_attempted 
- TFC: download_failed_or_not_attempted 
- TGT: download_failed_or_not_attempted 
- TJX: download_failed_or_not_attempted 
- TKO: download_failed_or_not_attempted 
- TMO: download_failed_or_not_attempted 
- TMUS: download_failed_or_not_attempted 
- TPL: download_failed_or_not_attempted 
- TPR: download_failed_or_not_attempted 
- TRGP: download_failed_or_not_attempted 
- TRMB: download_failed_or_not_attempted 
- TROW: download_failed_or_not_attempted 
- TRV: download_failed_or_not_attempted 
- TSCO: download_failed_or_not_attempted 
- TSLA: download_failed_or_not_attempted 
- TSN: download_failed_or_not_attempted 
- TT: download_failed_or_not_attempted 
- TTWO: download_failed_or_not_attempted 
- TWLO: download_failed_or_not_attempted 
- TXN: download_failed_or_not_attempted 
- TXT: download_failed_or_not_attempted 
- TYL: download_failed_or_not_attempted 
- UAL: download_failed_or_not_attempted 
- UBER: download_failed_or_not_attempted 
- UDR: download_failed_or_not_attempted 
- UHS: download_failed_or_not_attempted 
- ULTA: download_failed_or_not_attempted 
- UNH: download_failed_or_not_attempted 
- UNP: download_failed_or_not_attempted 
- UPS: download_failed_or_not_attempted 
- URI: download_failed_or_not_attempted 
- USB: download_failed_or_not_attempted 
- V: download_failed_or_not_attempted 
- VEEV: download_failed_or_not_attempted 
- VICI: download_failed_or_not_attempted 
- VLO: download_failed_or_not_attempted 
- VLTO: download_failed_or_not_attempted 
- VMC: download_failed_or_not_attempted 
- VMRK: download_failed_or_not_attempted 
- VRSK: download_failed_or_not_attempted 
- VRSN: download_failed_or_not_attempted 
- VRT: download_failed_or_not_attempted 
- VRTX: download_failed_or_not_attempted 
- VST: download_failed_or_not_attempted 
- VTR: download_failed_or_not_attempted 
- VTRS: download_failed_or_not_attempted 
- VYLR: download_failed_or_not_attempted 
- VZ: download_failed_or_not_attempted 
- WAB: download_failed_or_not_attempted 
- WAT: download_failed_or_not_attempted 
- WDAY: download_failed_or_not_attempted 
- WDC: download_failed_or_not_attempted 
- WEC: download_failed_or_not_attempted 
- WELL: download_failed_or_not_attempted 
- WFC: download_failed_or_not_attempted 
- WM: download_failed_or_not_attempted 
- WMB: download_failed_or_not_attempted 
- WMT: download_failed_or_not_attempted 
- WRB: download_failed_or_not_attempted 
- WSM: download_failed_or_not_attempted 
- WST: download_failed_or_not_attempted 
- WTW: download_failed_or_not_attempted 
- WY: download_failed_or_not_attempted 
- WYNN: download_failed_or_not_attempted 
- XEL: download_failed_or_not_attempted 
- XOM: download_failed_or_not_attempted 
- XYL: download_failed_or_not_attempted 
- XYZ: download_failed_or_not_attempted 
- YUM: download_failed_or_not_attempted 
- ZBH: download_failed_or_not_attempted 
- ZBRA: download_failed_or_not_attempted 
- ZTS: download_failed_or_not_attempted 

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

Per-security event dates/ratios/dividend-factor residuals are in stock_quality.json. Exact anomalous rows and per-stock missing dates are in validation_details.json. Daily breadth is in daily_coverage.parquet.

## Known bias and limits

Current membership and recent liquidity create survivorship/selection bias. Delisted returns and permanent identity mapping remain unavailable. Yahoo adjusted values are snapshot proxies, not as-traded execution history. No corporate-action cash ledger or PIT fundamentals. Latest HTTP availability does not establish the true historical information set. A passing dataset gate means only a validated prototype research input.

Panel: data\processed\phase2\20261008T084032831451Z\research_panel.parquet; SHA-256: d6f74e02443bf40dd8945bcd09bddfa7255eff25e48d81f1976f8e80a369f01e.

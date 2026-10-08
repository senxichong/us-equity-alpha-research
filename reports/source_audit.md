# Source and universe evidence audit

SURVIVORSHIP-BIASED PROTOTYPE UNIVERSE

All numeric results below are generated from cached responses or explicit requests.

## Historical membership candidate

```json
{
  "current_roster_count": 503,
  "history_snapshot_rows": 2720,
  "history_first": "1996-01-02",
  "history_last": "2026-08-18",
  "duplicate_dates": 0,
  "dates_sorted": true,
  "min_members": 487,
  "max_members": 507,
  "rows_with_duplicate_symbols": 0,
  "latest_history_only": [
    "BLDR",
    "CTVA",
    "PSKY",
    "TAP",
    "TTD",
    "WBD"
  ],
  "current_roster_only": [
    "BE",
    "ILMN",
    "P",
    "SKYD",
    "TWLO",
    "VYLR"
  ],
  "spot_checks": [
    {
      "date": "2020-12-18",
      "ticker": "TSLA",
      "expected": false,
      "observed": false,
      "passed": true
    },
    {
      "date": "2020-12-21",
      "ticker": "TSLA",
      "expected": true,
      "observed": true,
      "passed": true
    },
    {
      "date": "2022-06-08",
      "ticker": "FB",
      "expected": true,
      "observed": true,
      "passed": true
    },
    {
      "date": "2022-06-09",
      "ticker": "META",
      "expected": true,
      "observed": true,
      "passed": true
    }
  ],
  "status": "CANDIDATE ONLY - NOT VERIFIED POINT-IN-TIME",
  "sha256": "36326709d46d6cd25834de5df457b16f5f96fad3a06b9beac28f7b88aa0b0d54"
}
```

TSLA effective date reference: https://press.spglobal.com/2020-11-30-S-P-Dow-Jones-Indices-Announces-Implementation-of-Teslas-Addition-to-S-P-500
META symbol reference: https://www.sec.gov/Archives/edgar/data/1326801/000132680122000070/may312022-exhibit991.htm

Even passing spot checks cannot establish exhaustive historical membership, announcement availability, security identity or delisting coverage. Latest candidate coverage ends before the requested endpoint. Mode B remains blocked.

## IBM cross-provider comparison

```json
{
  "overlapping_dates": 2203,
  "adj_return_difference_max": 0.003408289613926252,
  "adj_return_difference_median": 8.497336578816572e-08,
  "dates_difference_above_1bp": [
    "2018-02-08",
    "2019-02-07",
    "2019-08-08",
    "2019-08-12",
    "2019-08-13",
    "2020-02-07",
    "2020-11-09",
    "2021-11-09",
    "2022-02-10",
    "2022-05-09",
    "2022-08-09",
    "2023-08-09",
    "2024-02-08",
    "2024-05-09",
    "2025-08-08"
  ],
  "close_level_ratio_min": 0.9999999431437794,
  "close_level_ratio_max": 1.049521351740688,
  "note": "Return comparison only; AV raw close and Yahoo split/distribution-adjusted close do not have identical semantics. No mixing of sources."
}
```

## Download repeatability and cache

```json
{
  "repeatability": {
    "old_retrieved_at": "2026-10-08T08:07:16.909380+00:00",
    "new_retrieved_at": "2026-10-08T08:11:06.194838+00:00",
    "matching_index": true,
    "rows": 2203,
    "max_absolute_column_difference": {
      "Open": 0.0,
      "High": 0.0,
      "Low": 0.0,
      "Close": 0.0,
      "Adj Close": 7.62939453125e-05,
      "Volume": 0.0,
      "Dividends": 0.0,
      "Stock Splits": 0.0
    },
    "exact_table_equal": false
  },
  "cache": {
    "hit": true,
    "rows": 2203,
    "hash_verified_by_adapter": true
  }
}
```

## Symbol identity

```json
[
  {
    "ticker": "FB",
    "status": "ok",
    "name": "ProShares S&P 500 Dynamic Daily Buffer ETF",
    "instrument_type": "ETF",
    "rows": 323
  },
  {
    "ticker": "TWTR",
    "status": "failed",
    "name": null,
    "instrument_type": null,
    "rows": 0
  },
  {
    "ticker": "SIVBQ",
    "status": "failed",
    "name": null,
    "instrument_type": null,
    "rows": 0
  }
]
```

A current vendor symbol can identify a different security. FB is quarantined as a diagnostic and never merged into META.

Full Alpha Vantage validation, immutable hashes, and official split spot checks: source_audit.json.

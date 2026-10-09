# Phase 5 feature set

survivorship_biased = true; candidate_selection_biased = true

Identical to the Phase 4 definition-selected set. P = frozen adj_close; V = vendor volume; C = vendor close. Retained inputs are the existing Phase 3 date-local z-scores. No extra scaling or imputation is fitted for trees. All definitions, strict complete-session windows and availability remain authoritative in FACTOR_DEFINITIONS.md.

| Feature | Family | Phase 3 raw definition | Retained | Reason |
|---|---|---|---|---|
| RET_5 | Momentum/Reversal | P[t]/P[t−5]−1 | Yes | Frozen Phase 4 input |
| RET_10 | Momentum/Reversal | P[t]/P[t−10]−1 | Yes | Frozen Phase 4 input |
| RET_20 | Momentum/Reversal | P[t]/P[t−20]−1 | Yes | Frozen Phase 4 input |
| RET_60 | Momentum/Reversal | P[t]/P[t−60]−1 | Yes | Frozen Phase 4 input |
| REV_5 | Momentum/Reversal | −RET_5 | No | Exact negative duplicate, excluded before Phase 4 outcomes |
| VOL_10 | Volatility | Sample std of 10 backward daily adjusted returns, ddof=1 | Yes | Frozen Phase 4 input |
| VOL_20 | Volatility | Sample std of 20 backward daily adjusted returns, ddof=1 | Yes | Frozen Phase 4 input |
| VOL_60 | Volatility | Sample std of 60 backward daily adjusted returns, ddof=1 | Yes | Frozen Phase 4 input |
| ILLIQ_20 | Liquidity/Volume | Trailing 20-session mean absolute adjusted daily return / (C×V) | Yes | Frozen Phase 4 input |
| DOLLAR_VOLUME_20 | Liquidity/Volume | Trailing 20-session mean C×V | Yes | Frozen Phase 4 input |
| VOLUME_RATIO_20 | Liquidity/Volume | V[t] / mean(V[t−20:t−1]) | Yes | Frozen Phase 4 input; not removed for weak results |
| VOLUME_SURPRISE_20 | Liquidity/Volume | (V[t]−previous-20 mean) / previous-20 sample std | Yes | Frozen Phase 4 input; not removed for weak results |
| PRICE_MA20 | Price Position/Intraday | P[t] / mean(P[t−19:t])−1 | Yes | Frozen Phase 4 input |
| PRICE_MA60 | Price Position/Intraday | P[t] / mean(P[t−59:t])−1 | Yes | Frozen Phase 4 input |
| DIST_52W_HIGH | Price Position/Intraday | P[t] / max(P[t−251:t])−1 | Yes | Frozen Phase 4 input |
| INTRADAY_RANGE | Price Position/Intraday | (high−low)/close on vendor basis | Yes | Frozen Phase 4 input |
| OPEN_CLOSE_RETURN | Price Position/Intraday | close/open−1 on vendor basis | Yes | Frozen Phase 4 input |

The keyed random feature is a separate diagnostic only, never a production input. No new technical indicators, fundamentals, macro or alternative data. No Phase 5 test outcome influences this feature set.

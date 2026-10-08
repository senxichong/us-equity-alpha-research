# Factor definitions

survivorship_biased = true; candidate_selection_biased = true

Factor version: 1.0.0. P denotes frozen vendor adj_close.

| Factor | Required consecutive sessions | Definition |
|---|---:|---|
| RET_5 | 6 | P[t]/P[t-5]-1; all 6 prices required |
| RET_10 | 11 | P[t]/P[t-10]-1; all 11 prices required |
| RET_20 | 21 | P[t]/P[t-20]-1; all 21 prices required |
| RET_60 | 61 | P[t]/P[t-60]-1; all 61 prices required |
| REV_5 | 6 | -RET_5; exact sign reversal, not an independent signal |
| VOL_10 | 11 | sample std (ddof=1) of 10 one-session returns ending t; not annualized |
| VOL_20 | 21 | sample std (ddof=1) of 20 one-session returns ending t; not annualized |
| VOL_60 | 61 | sample std (ddof=1) of 60 one-session returns ending t; not annualized |
| ILLIQ_20 | 21 | mean(abs(P[s]/P[s-1]-1)/(close[s]*volume[s])), s=t-19..t |
| DOLLAR_VOLUME_20 | 20 | mean(close[s]*volume[s]), s=t-19..t; vendor basis |
| VOLUME_RATIO_20 | 21 | volume[t]/mean(volume[t-20:t-1]); current volume excluded from reference |
| VOLUME_SURPRISE_20 | 21 | (volume[t]-mean(volume[t-20:t-1]))/sample_std(volume[t-20:t-1], ddof=1); zero std -> NaN |
| PRICE_MA20 | 20 | P[t]/mean(P[t-19:t])-1 |
| PRICE_MA60 | 60 | P[t]/mean(P[t-59:t])-1 |
| DIST_52W_HIGH | 252 | P[t]/max(P[t-251:t])-1; 252-session adjusted CLOSE high, not intraday high |
| INTRADAY_RANGE | 1 | (high[t]-low[t])/close[t]; same vendor OHLC basis |
| OPEN_CLOSE_RETURN | 1 | close[t]/open[t]-1; same vendor OHLC basis |

Every factor includes t, becomes observable after close(t) and daily-bar availability, and requires every specified source input to be valid. Missing/zero-volume sessions retain their position and invalidate dependent windows. No forward fill, interpolation, centered window or compression of valid rows. RET_n requires n+1 prices, not just endpoints. VOL_n uses n returns from n+1 prices, sample ddof=1, with no annualization.

ILLIQ_20 uses absolute adjusted one-day returns divided by vendor Close × Volume, in inverse vendor USD-volume units; no arbitrary rescaling. DOLLAR_VOLUME_20 is the trailing mean of that proxy. Volume ratio and surprise compare the current volume against the previous 20 sessions, excluding t. They are trading-activity proxies, not turnover divided by shares outstanding. Zero reference standard deviation makes volume surprise unavailable.

PRICE_MA20/60 report the fractional deviation P/MA−1, so zero means price equals its moving average. DIST_52W_HIGH uses the highest adjusted closing price over 252 sessions, not the highest intraday price. Intraday range and open-close return use same-basis vendor OHLC. Negative and redundant factors are retained: REV_5 is exactly −RET_5 and is not an independent signal.

## Cross-sectional preprocessing

For each factor and date independently, membership = eligible_at_t AND that raw factor is finite. Compute linear-interpolated 1st/99th percentiles, clip, then subtract the same-date clipped mean and divide by the same-date clipped population standard deviation (ddof=0). Require at least two members; zero standard deviation yields null z-scores. Raw, `_winsorized`, and `_zscore` columns are retained. Ineligible observations retain raw factors for audit but have null processed values. No target or future eligibility filter, no full-period scaler, no learned model and no fitting on a test period. All-factor completeness is a separate downstream flag, not the per-factor membership rule.

## Availability and exclusions

`factor_available_NAME` is past-only, finite raw-factor availability. `factor_available` requires all 17 raw values. `processed_factor_available` separately requires all 17 z-scores. The eligibility mask is unchanged; availability can only reduce participation for a given factor. Raw factors computed before 252 valid observations are not eligible for research.

Market beta is deferred because no approved frozen market-benchmark series is present in the accepted panel; no download is authorized. Size and industry/capitalization neutralization are deferred because PIT shares, market cap and industry membership are not certified. Current metadata is not substituted.

Machine-readable fields, source columns, warm-up, units and fixed diagnostic extreme thresholds are in `reports/phase3/factor_metadata.json`. Thresholds flag absolute raw magnitudes for inspection only; they do not quarantine securities, change values or select factors. Full-sample diagnostic means/quantiles are reports, never model/scaler parameters.

Targets and timing: see TIMING_CONVENTION.md. These are prototype engineering outputs, not evidence of predictive power.

# Single-factor research — primary 5D target

**survivorship_biased = true; candidate_selection_biased = true**

Highest raw signed mean RankIC: ILLIQ_20 (0.01395); largest absolute primary RankIC HAC t: ILLIQ_20 (4.23). The weakest magnitude is VOLUME_RATIO_20 (0.00048, HAC t=0.27). Negative means are retained and are not automatically failures.

All 17 mathematical definitions and signs are preserved. Pearson uses raw factor values; Spearman uses average ranks. Minimum 50 paired stocks per signal date. Eligibility is the frozen at-t mask; future eligibility is never required. Only unavailable labels/endpoints are omitted from association evaluation. No future outcome-magnitude exclusion or global factor normalization is introduced.

## Full primary evidence

| factor | IC_mean | RankIC_mean | RankIC_hac_t | RankIC_hac_t_lag20 | RankIC_hac_BH_q | rankic_years_same_sign_as_full | complete_years |
|---|---|---|---|---|---|---|---|
| RET_5 | -0.0141425 | -0.0132162 | -2.92373 | -2.77069 | 0.0117594 | 11 | 15 |
| RET_10 | -0.0120828 | -0.0120359 | -2.44986 | -2.39607 | 0.0347075 | 13 | 15 |
| RET_20 | -0.00949633 | -0.00997703 | -1.94477 | -1.83487 | 0.0978501 | 12 | 15 |
| RET_60 | -0.00452302 | -0.00645281 | -1.16645 | -1.16262 | 0.295595 | 10 | 15 |
| REV_5 | 0.0141425 | 0.0132162 | 2.92373 | 2.77069 | 0.0117594 | 11 | 15 |
| VOL_10 | 0.020476 | 0.0123642 | 1.97745 | 1.85994 | 0.0978501 | 11 | 15 |
| VOL_20 | 0.0228605 | 0.0121118 | 1.75346 | 1.62301 | 0.112657 | 11 | 15 |
| VOL_60 | 0.0262755 | 0.0138369 | 1.82458 | 1.69296 | 0.105191 | 11 | 15 |
| ILLIQ_20 | 0.0183117 | 0.0139539 | 4.22952 | 3.92765 | 0.000398131 | 14 | 15 |
| DOLLAR_VOLUME_20 | 0.0043694 | -0.00990498 | -3.17038 | -2.93161 | 0.00862706 | 11 | 15 |
| VOLUME_RATIO_20 | 0.00201249 | 0.000484616 | 0.273204 | 0.248879 | 0.784696 | 10 | 15 |
| VOLUME_SURPRISE_20 | 0.00258506 | 0.00159936 | 0.951018 | 0.872288 | 0.387141 | 9 | 15 |
| PRICE_MA20 | -0.012997 | -0.0127468 | -2.52975 | -2.42543 | 0.0323405 | 13 | 15 |
| PRICE_MA60 | -0.0082561 | -0.00846184 | -1.56656 | -1.57444 | 0.153285 | 10 | 15 |
| DIST_52W_HIGH | -0.0145834 | -0.00501017 | -0.758234 | -0.71717 | 0.47633 | 8 | 15 |
| INTRADAY_RANGE | 0.0178214 | 0.00921204 | 1.84466 | 1.75582 | 0.105191 | 11 | 15 |
| OPEN_CLOSE_RETURN | -0.00974635 | -0.00884709 | -3.59108 | -3.70757 | 0.00279911 | 12 | 15 |

Mean RankIC magnitudes are small. Statistical evidence, directional stability and economic scale must be read together. The table shows both predeclared HAC bandwidths and complete-year sign consistency; a negative loading can be predictive in its original negative direction.

## Strongest HAC evidence and weakest associations

| factor | IC_mean | RankIC_mean | RankIC_hac_t | RankIC_hac_t_lag20 | RankIC_hac_BH_q | rankic_years_same_sign_as_full | complete_years |
|---|---|---|---|---|---|---|---|
| ILLIQ_20 | 0.0183117 | 0.0139539 | 4.22952 | 3.92765 | 0.000398131 | 14 | 15 |
| OPEN_CLOSE_RETURN | -0.00974635 | -0.00884709 | -3.59108 | -3.70757 | 0.00279911 | 12 | 15 |
| DOLLAR_VOLUME_20 | 0.0043694 | -0.00990498 | -3.17038 | -2.93161 | 0.00862706 | 11 | 15 |
| RET_5 | -0.0141425 | -0.0132162 | -2.92373 | -2.77069 | 0.0117594 | 11 | 15 |
| REV_5 | 0.0141425 | 0.0132162 | 2.92373 | 2.77069 | 0.0117594 | 11 | 15 |
| PRICE_MA20 | -0.012997 | -0.0127468 | -2.52975 | -2.42543 | 0.0323405 | 13 | 15 |

| factor | IC_mean | RankIC_mean | RankIC_hac_t | RankIC_hac_t_lag20 | RankIC_hac_BH_q | rankic_years_same_sign_as_full | complete_years |
|---|---|---|---|---|---|---|---|
| VOLUME_RATIO_20 | 0.00201249 | 0.000484616 | 0.273204 | 0.248879 | 0.784696 | 10 | 15 |
| VOLUME_SURPRISE_20 | 0.00258506 | 0.00159936 | 0.951018 | 0.872288 | 0.387141 | 9 | 15 |
| DIST_52W_HIGH | -0.0145834 | -0.00501017 | -0.758234 | -0.71717 | 0.47633 | 8 | 15 |
| RET_60 | -0.00452302 | -0.00645281 | -1.16645 | -1.16262 | 0.295595 | 10 | 15 |

The weak rows are retained, including volume-ratio/surprise diagnostics with little ranking evidence. A non-significant result is inconclusive, not proof of zero effect. There is no performance-driven feature deletion.

## Stability and regime dependence

| factor | rankic_years_same_sign_as_full | complete_years | positive_rankic_years | negative_rankic_years | min_yearly_rankic | max_yearly_rankic |
|---|---|---|---|---|---|---|
| ILLIQ_20 | 14 | 15 | 14 | 1 | -4.65405e-05 | 0.0349805 |
| PRICE_MA20 | 13 | 15 | 2 | 13 | -0.0304329 | 0.0204196 |
| RET_10 | 13 | 15 | 2 | 13 | -0.0317112 | 0.0295711 |
| OPEN_CLOSE_RETURN | 12 | 15 | 3 | 12 | -0.0311709 | 0.00499766 |
| RET_20 | 12 | 15 | 3 | 12 | -0.0477541 | 0.0198633 |

Complete-year consistency uses 2011–2025; 2010 contains only the warm-up boundary, and 2026 is partial. ILLIQ_20 is positive in 14 of 15 complete years; its remaining year is approximately zero. Every annual mean and count remains in yearly_factor_statistics.csv; annual reversals and rolling estimates show that a full-period mean does not imply a constant effect. The most sign-consistent rows above still require magnitude/inference scrutiny. No causal macro-regime attribution is inferred from calendar years.

## Redundancy

| factor_a | factor_b | mean_daily_spearman | valid_dates |
|---|---|---|---|
| RET_5 | REV_5 | -1 | 3965 |
| RET_10 | PRICE_MA20 | 0.894729 | 3965 |
| RET_20 | PRICE_MA20 | 0.831917 | 3965 |
| RET_60 | PRICE_MA60 | 0.838213 | 3965 |
| VOL_10 | VOL_20 | 0.826136 | 3965 |
| VOL_20 | VOL_60 | 0.816664 | 3965 |
| ILLIQ_20 | DOLLAR_VOLUME_20 | -0.928041 | 3965 |
| VOLUME_RATIO_20 | VOLUME_SURPRISE_20 | 0.933452 | 3965 |

REV_5 is exactly −RET_5, not a second discovery. Volatility windows, momentum versus moving-average distance, illiquidity versus dollar volume, and volume ratio versus surprise share information. Correlations use eligible-at-t pairwise-complete cross sections without target filtering. Only the exact inverse is removed from model inputs by the prior rule; correlated families remain for regularization diagnostics.

## Forward-return quantile diagnostics

| factor | monotonicity_score | spread_bp | top_minus_bottom_hac_t | spread_years_same_sign_as_full | spread_complete_years |
|---|---|---|---|---|---|
| RET_5 | -1 | -15.5851 | -2.67487 | 13 | 15 |
| RET_10 | -0.9 | -11.5802 | -1.92105 | 13 | 15 |
| RET_20 | -1 | -11.0217 | -1.80453 | 12 | 15 |
| RET_60 | -0.4 | -11.2063 | -1.6407 | 11 | 15 |
| REV_5 | 1 | 15.5851 | 2.67487 | 13 | 15 |
| VOL_10 | 1 | 21.7607 | 3.08663 | 11 | 15 |
| VOL_20 | 1 | 22.2926 | 2.86145 | 10 | 15 |
| VOL_60 | 1 | 25.5765 | 3.036 | 11 | 15 |
| ILLIQ_20 | 0.9 | 15.9676 | 4.50183 | 15 | 15 |
| DOLLAR_VOLUME_20 | -0.3 | -8.67499 | -2.47935 | 12 | 15 |
| VOLUME_RATIO_20 | 0.4 | 0.986951 | 0.476646 | 9 | 15 |
| VOLUME_SURPRISE_20 | 0.3 | 2.78795 | 1.43001 | 10 | 15 |
| PRICE_MA20 | -1 | -13.4724 | -2.17387 | 12 | 15 |
| PRICE_MA60 | -0.7 | -11.3747 | -1.72297 | 12 | 15 |
| DIST_52W_HIGH | -1 | -17.1478 | -2.20395 | 11 | 15 |
| INTRADAY_RANGE | 1 | 18.2827 | 3.13437 | 12 | 15 |
| OPEN_CLOSE_RETURN | -0.9 | -10.8637 | -3.48614 | 13 | 15 |

Spread is always Q5−Q1 in basis points per five-session label, unflipped. |monotonicity| >= .8 marks a strong aggregate ordering, including descending order for negative factors. Read yearly spread consistency alongside the aggregate ordering. ILLIQ and volume/price metrics can disagree between Pearson, RankIC and monotonicity; no favorable metric replaces the others. Some statistically detectable spreads remain only a few to a few dozen basis points over five sessions. These are overlapping forward-return quantile diagnostics, not attainable strategy returns; no Sharpe is reported.

DOLLAR_VOLUME_20 illustrates why a nonzero mean RankIC or spread need not imply a clean five-bin ordering. A strong aggregate ordering with weak RankIC evidence is also possible (e.g. DIST_52W_HIGH); all metrics are shown rather than selecting the flattering one.

## Inference, horizons and limitations

Daily 5D labels overlap, so IID t-statistics overstate precision when ICs are serially correlated. Primary inference uses Bartlett Newey-West lag 5, plus fixed lag-20 sensitivity, on the exchange-session grid. ICIR is unannualized mean/std. HAC does not remove universe bias or guarantee that a five-lag bandwidth captures all dependence. BH q-values separately cover the 17 primary IC and 17 primary RankIC tests; correlated factors, secondary horizons and researcher exposure still create multiple-testing/data-snooping concerns. No p-value alone establishes discovery.

All 1D/10D/20D robustness results, along with the fixed 5D primary, are in horizon_robustness.csv. No secondary model grids were run. Raw daily IC/RankIC distributions, quantiles/skewness and extreme dates are saved; extreme dates were not deleted.

These are conditional associations in a frozen current-member universe, not unbiased historical strategy evidence. Global candidate/quarantine selection, retrospective vendor revisions, unresolved identity/delistings and indicative adjusted-open prices remain. Risk/industry/size neutrality is not established. No transaction costs, auction-fill realism, borrow or overlapping-capital accounting are modeled.

## Figures and evidence

![Primary factor associations](phase4/figures/factor_ic_comparison.png)

![Rolling RankIC](phase4/figures/rolling_rankic.png)

![Quantile diagnostics](phase4/figures/quantile_forward_returns.png)

![Correlation](phase4/figures/factor_correlation.png)

Additional figures: yearly_rankic.png and ic_distributions.png. Machine-readable counts/statistics, metadata and protocol hash are in phase4/. Method definitions and references: [PHASE4_PROTOCOL.md](../PHASE4_PROTOCOL.md).

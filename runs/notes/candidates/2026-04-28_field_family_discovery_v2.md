# Field-Family Discovery V2 For Second Alpha

- Date: 2026-04-28
- Scope: discovery and design only
- Simulations run: none
- Baseline submitted alpha: E5g7vMjJ, close-volume correlation reversal, ACTIVE / OS / AVERAGE at last confirmation
- Discovery source: cached USA / TOP3000 / D1 data-fields inventory at `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`, plus local Worldquantbrain research notes and stop memos

## Constraints

- Do not spend simulation quota in this turn.
- Do not create E5g7vMjJ near-neighbor variants.
- Avoid close-volume correlation reversal, `ts_corr(rank(close), rank(volume), 60/70/80/90)`, close60 reversal, and direct window tweaks around submitted or failed expressions.
- Avoid failed lanes from the second, third, fourth, and fifth batches.
- Treat archived stop memos as hard context: do not reopen `pcr_vol_90`, direct `pcr_oi_30`, implied-volatility skew tenor sweeps, or model16 multi-factor static/acceleration rerating with only sign, lookback, smoothing, or grouping changes.

## Scored Field-Family Map

| Dataset / source | Verified field names | Category | Rough economic intuition | Expected horizon | Expected turnover | Coverage / availability | Relation to E5g7vMjJ | Relation to failed lanes | Risk flags | Score | Reason |
|---|---|---|---|---|---|---|---|---|---|---:|---|
| `option9` / Options Analytics | `forward_price_60`, `forward_price_120` | Option-implied forward curve | Forward-curve slope can proxy option-implied carry, financing/dividend expectations, borrow pressure, and synthetic-stock demand. | 60-120 days | Medium-low after 60d rank and 20d decay | Matrix, coverage 0.7037, date 1.0. `forward_price_60`: 225 users / 388 alphas. `forward_price_120`: 269 users / 348 alphas. | Distinct. Uses option-implied forward curve, not price-volume correlation or close reversal. | Distinct from failed PCR volume/OI direct ranks, raw skew, sentiment, analyst, and short-interest lanes. | 70% coverage can create sub-universe or weight risk; raw price level needs normalization by `close`. | 5 | Best fresh source found: verified, medium horizon, option-related, not previously frozen in local notes. |
| `news18` / Ravenpack News Data | `rp_nip_credit_ratings`, `rp_ess_dividends`, `rp_ess_credit`, `rp_nip_revenue` | Slow event news aggregates | Event-specific credit, dividend, and revenue news can capture slow reassessment rather than fast generic sentiment. | 63-126 days | Medium after smoothing | Matrix, coverage 0.5, date 1.0. `rp_nip_credit_ratings`: 57 users / 129 alphas. `rp_ess_dividends`: 59 users / 106 alphas. | Distinct. Event news source unrelated to close-volume correlation. | Distinct from failed social fast sentiment and generic news attention; still adjacent to news family. | 50% coverage and sparse events can cause concentration and sub-universe failures. | 4 | Worth a small future test because it is event-specific, less crowded, and materially different from raw social sentiment. |
| `model51` / Systematic Risk Metrics | `beta_last_90_days_spy`, `systematic_risk_last_90_days`, `unsystematic_risk_last_90_days` | Risk model anomaly | Medium-horizon beta and residual-risk fields can test defensive or risk-premium effects without using price reversal. | 60-90 days | Low-medium | Matrix, coverage about 0.7736-0.7782, date 1.0. Crowded: `unsystematic_risk_last_90_days` has 1474 users / 3216 alphas. | Distinct if used standalone, not multiplied by close reversal. | Distinct from failed close60 reversal + inverse risk conditioning; risk is no longer a conditioning leg on price reversal. | High crowding and low standalone return potential. | 3 | Good coverage and robust horizon, but crowded and likely low-return unless the sign is strong. |
| `option9` / Options Analytics | `pcr_oi_720` | Long-horizon put/call open interest | Slow options positioning can proxy persistent hedging or bearish crowding. | 20-126 days | Medium | Matrix, coverage 0.7058, date 1.0, 484 users / 815 alphas. | Distinct from E5. | Existing local lane reached held candidates but still failed LOW_FITNESS; not fresh. | Reopening would violate the held-lane budget unless a genuinely new external source appears. | 3 | Useful as context, but not selected for sixth-batch seeds because it already consumed significant local research budget. |
| `analyst4` / Analyst Estimate Data | `sales_estimate_dispersion`, `sales_estimate_average_annual`, `highest_sales_estimate`, `lowest_sales_estimate` | Estimate dispersion / top-line uncertainty | Estimate spread can proxy uncertainty or analyst disagreement; lower disagreement may indicate quality. | 60-120 days | Low-medium after smoothing | `sales_estimate_dispersion`: coverage 0.6792, date 1.0, 27 users / 34 alphas. Sales estimate level fields have coverage 1.0. | Distinct from E5. | Adjacent to failed analyst disagreement and raw recommendation mark. Top-line guidance-vs-consensus has an archived stop memo. | Analyst fields have already disappointed; raw marks produced bad turnover/concentration. | 2 | Keep as watchlist only; do not retest without a materially different construction. |
| `model16` / Fundamental Scores | `analyst_revision_rank_derivative`, `relative_valuation_rank_derivative`, `growth_potential_rank_derivative` | Model score derivatives | Vendor composite score changes may capture analyst, valuation, and growth rerating. | 20-60 days | Medium | Matrix, coverage 1.0, date 1.0. Visible alphas range 66-276 for listed fields. | Distinct from E5. | Model16 static and acceleration rerating lanes have stop memos; fourth batch quality/efficiency model16 seed failed. | Reopening model16 by smoothing or recombining is likely cosmetic. | 2 | Verified and high coverage, but deprioritized by multiple local failures. |
| `option8` / Volatility Data | `implied_volatility_mean_skew_20`, `implied_volatility_mean_skew_60`, `implied_volatility_mean_skew_90`, `historical_volatility_60`, `parkinson_volatility_60` | Volatility/skew | Skew and realized-vol fields can proxy option-market risk pricing. | 20-180 days | Medium-high in prior raw sweep | Coverage about 0.6869, date 1.0; skew fields are heavily used. | Distinct from E5. | Implied-volatility skew sweep had high turnover and low Fitness; close60 risk conditioning also failed. | High turnover and low Fitness in prior tests. | 1 | Not selected; avoid another smoothing-only retest. |
| `news12` / short interest | `news_short_interest`, `nws12_mainz_short_interest`, `nws12_prez_short_interest`, `nws12_afterhsz_short_interest` | Short-interest positioning | Short interest can proxy crowding and bearish conviction. | 20-120 days | Medium-high if deltas are used | Verified in prior notes; fifth batch short-interest delta was simulated. | Distinct from E5. | Fifth batch `P0waNmxK` had Fitness 0.25 / Sharpe 0.73 but failed HIGH_TURNOVER, CONCENTRATED_WEIGHT, and LOW_SUB_UNIVERSE_SHARPE. | Turnover, concentration, and sub-universe failures. | 1 | Hard negative for now; do not retest raw or delta short interest. |
| `socialmedia12` / social sentiment | `scl12_sentiment_fast_d1` | Fast social sentiment | Crowd sentiment may proxy attention and behavioral flow. | 10-30 days | Medium-high | Verified in fifth design. | Distinct from E5. | Fifth batch `npZR9X0q` failed with negative Fitness and Sharpe. | Raw fast sentiment is weak; avoid unless a materially slow aggregate exists. | 1 | Hard negative for now. |

## Selected Future Sixth-Batch Seed Designs

These are planning-only drafts. They were not run.

### 1. `option_forward_curve_carry_seed`

- Verified fields used: `forward_price_60`, `forward_price_120`, `close`
- Draft expression:

```text
group_neutralize(ts_decay_linear(rank(ts_rank((forward_price_120 - forward_price_60) / close, 60)), 20), subindustry)
```

- Economic rationale: the 120d minus 60d option-implied forward slope, normalized by spot price, may capture forward-curve carry or funding pressure rather than raw option volume imbalance.
- Distinct from E5g7vMjJ: no close-volume correlation, no price reversal, no volume input.
- Distinct from failed lanes: not social sentiment, not raw analyst mark, not short-interest delta, not model16 quality, not close60 reversal, and not direct PCR/skew retesting.
- Expected turnover: medium-low after 60d time rank and 20d decay.
- Expected risk: option-field coverage around 70% may cause sub-universe weakness; sign may be wrong if the curve reflects risk premium rather than expected return.
- Continue after simulation only if Fitness > 0.5, Sharpe > 1.1 or close to it, Drawdown < 0.12, Turnover 0.08-0.30, and no concentration/sub-universe blocker.
- Stop immediately if LOW_FITNESS and LOW_SHARPE both fail or if sub-universe/concentration fails hard.

### 2. `ravenpack_credit_dividend_slow_seed`

- Verified fields used: `rp_nip_credit_ratings`, `rp_ess_dividends`
- Draft expression:

```text
group_neutralize(ts_decay_linear(rank(ts_mean(rp_nip_credit_ratings, 63)) + rank(ts_mean(rp_ess_dividends, 63)), 20), subindustry)
```

- Economic rationale: slow credit-rating impact plus dividend event sentiment can capture balance-sheet and shareholder-return reassessment from event-specific Ravenpack fields.
- Distinct from E5g7vMjJ: news event source, no price-volume relationship.
- Distinct from failed lanes: not fast social sentiment, not generic `nws18_relevance`, not raw analyst recommendation, not short interest, and not static accounting quality.
- Expected turnover: medium after 63d smoothing and 20d decay.
- Expected risk: 50% coverage and sparse events may create concentration or weak sub-universe performance.
- Continue after simulation only if Sharpe direction is positive, Fitness > 0.5, and concentration/sub-universe checks pass.
- Stop immediately if concentration or LOW_SUB_UNIVERSE_SHARPE fails, even if headline Sharpe is passable.

### 3. `model51_residual_risk_compression_seed`

- Verified fields used: `unsystematic_risk_last_90_days`, `beta_last_90_days_spy`
- Draft expression:

```text
group_neutralize(ts_decay_linear(-rank(ts_rank(unsystematic_risk_last_90_days, 60)) - rank(ts_rank(beta_last_90_days_spy, 60)), 20), subindustry)
```

- Economic rationale: tests whether lower residual risk and lower market beta form a medium-horizon defensive anomaly after subindustry neutralization.
- Distinct from E5g7vMjJ: standalone risk-model source, no close-volume correlation or price reversal.
- Distinct from failed lanes: not the failed close60 reversal multiplied by volatility/range; risk is the signal itself, not a conditioning term on reversal.
- Expected turnover: low-medium because model51 risk metrics already use 90-day windows and the expression adds 60d time rank.
- Expected risk: risk-only alpha may have low returns and model51 fields are crowded, especially `unsystematic_risk_last_90_days`.
- Continue after simulation only if Fitness > 0.5 and Returns/Margin are positive with Turnover at least 0.08.
- Stop immediately if turnover is below 0.08, Returns are flat, or LOW_FITNESS fails by a wide margin.

## Decision

- Best fresh family: option-implied forward curve (`forward_price_60` / `forward_price_120`).
- Best non-option diversification candidate: Ravenpack event-specific slow aggregates.
- Best robustness/control candidate: model51 standalone risk anomaly.
- Do not reopen: `pcr_vol_90`, direct `pcr_oi_30`, raw implied-volatility skew sweeps, model16 multi-factor rerating, social fast sentiment, short-interest delta, raw `anl4_mark`, or simple accounting-quality ratios.
- Recommended next action: if the next simulation budget is approved, run exactly these three sixth-batch seeds as one manual batch and stop if no hopeful appears.

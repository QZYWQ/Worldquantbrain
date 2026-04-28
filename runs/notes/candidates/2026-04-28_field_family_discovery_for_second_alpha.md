# Field-Family Discovery For Second Alpha

- Date: 2026-04-28 22:21:14 CST
- Scope: discovery and candidate design only
- Simulations run: none
- Simulation endpoint called: no
- Baseline submitted alpha: `E5g7vMjJ`, ACTIVE / OS / AVERAGE at last confirmation
- Primary field source: `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
- Supplementary sources: prior field-search packs and expression-family notes in `Worldquantbrain`, plus safe local miner metadata and manual seed files

## Goal

Identify stronger, truly different field families before spending more simulation quota on the second submitted alpha. This memo avoids near-neighbor variants of:

- `E5g7vMjJ`: close-volume corr70 reversal
- failed second batch: `MPKWeelM`, `xAP62WGJ`, `xAP6G6vg`
- failed third batch: `npZJXnja`, `RR23vp31`, `O0bY2GYb`
- failed fourth batch: `O0bYdoK7`, `O0bYd0O1`, `om3pj7L2`

## Discovery Method

- Read cached official data-fields response for `USA / D1 / TOP3000`, containing 2663 fields.
- Cross-checked prior field-search packs for social media, news, analyst disagreement, option PCR, and option skew lanes.
- Did not inspect credential contents.
- Did not call the simulation endpoint.
- Did not create or run an executable manual-alpha batch.

## Field-Family Map

| Dataset/source | Verified field names | Rough economic intuition | Likely signal horizon | Expected turnover profile | Relation to `E5g7vMjJ` | Relation to failed second/third/fourth structures | Risk flags | Worth testing next? | Suggested expression pattern, not a run command |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `socialmedia12` / Sentiment Data for Equity | `scl12_sentiment_fast_d1`, `scl12_sentiment`, `scl12_alltype_sentvec`, `snt_buzz_fast_d1`, `snt_buzz_ret_fast_d1` | Social sentiment and social attention can capture public-information diffusion not visible in price-volume correlation. `scl12_sentiment_fast_d1` has high coverage and materially lower crowding than broad sentiment. | 20-60 days | Medium if smoothed; raw daily field may be high turnover | Distinct: no close-volume correlation, no price reversal | Distinct from failed fundamental/reversal/analyst-mark seeds; related only to older archived sentiment lanes | Sentiment may be weak after neutralization; broad sentiment self-correlation possible | Yes, top priority | `group_neutralize(ts_decay_linear(rank(ts_mean(scl12_sentiment_fast_d1, 20)), 10), subindustry)` |
| `analyst4` / estimate dispersion | `anl4_afv4_dts_spe`, `anl4_qfv4_dts_spe`, `anl4_qfv4_median_eps`, `anl4_qfv4_eps_mean`, `anl4_afv4_median_eps` | Estimate dispersion tests analyst confidence/disagreement rather than raw recommendation marks or absolute EPS level. Lower disagreement may proxy stable earnings visibility. | 60-120 days | Low to medium | Distinct: analyst data, no price-volume correlation | Distinct from failed `anl4_mark` raw recommendation seed; still an analyst family, so watch correlation | Coverage around 69-72% for disagreement fields; sub-universe and weight risk | Yes, second priority | `group_neutralize(ts_decay_linear(-rank(ts_rank(anl4_qfv4_dts_spe, 120)), 20), subindustry)` |
| `news12` / short interest | `news_short_interest`, `nws12_mainz_short_interest`, `nws12_prez_short_interest`, `nws12_afterhsz_short_interest` | Short interest is a positioning/crowding proxy. Rising short interest can predict pressure or, with wrong sign, squeeze risk. | 20-90 days | Low to medium | Distinct: non-price-volume positioning source | Distinct from failed corporate-action seed because it is market positioning, not balance-sheet change | Sign can be regime-dependent; updates may be too slow; vector siblings need `vec_avg` | Yes, third priority | `group_neutralize(ts_decay_linear(-rank(ts_rank(news_short_interest, 60)) - rank(ts_delta(news_short_interest, 20)), 20), subindustry)` |
| `news18` / Ravenpack news | `nws18_relevance`, `nws18_qcm`, `nws18_nip`, `nws18_bee` | News relevance, high-confidence news, impact, and earnings-growth news can test information diffusion outside analyst and price-volume families. | 21-126 days | Medium after `vec_avg` and smoothing | Distinct | Distinct from recent failed batches, but older news-attention lane is already frozen | Only 50% coverage; possible concentration and sub-universe risk | Watchlist, not top 3 today | `group_neutralize(ts_decay_linear(rank(ts_mean(vec_avg(nws18_qcm), 63)), 10), subindustry)` |
| `option9` / options analytics | `pcr_oi_30`, `pcr_oi_60`, `pcr_oi_360`, `pcr_oi_720`, `pcr_vol_all`, `pcr_oi_all` | Put/call open interest and volume proxy options positioning and demand for downside protection. | 20-120 days | Medium; prior direct PCR turnover was acceptable | Distinct | Distinct from recent batches, but archived PCR lines were weak or frozen | Coverage around 70%; prior PCR OI family had low Fitness and sub-universe failures | Not immediate; recheck only after better source is exhausted | `group_neutralize(ts_decay_linear(rank(ts_rank(pcr_oi_720, 60)), 20), subindustry)` |
| `option8` / volatility data | `implied_volatility_mean_skew_20`, `implied_volatility_mean_skew_60`, `implied_volatility_mean_skew_90`, `implied_volatility_mean_skew_180`, `historical_volatility_60`, `parkinson_volatility_60` | Implied-volatility skew and realized vol can proxy option-market risk pricing. | 20-180 days | Medium to high in prior raw tenor sweep | Distinct | Adjacent to prior risk/volatility searches; direct skew was frozen | Prior skew sweep had high turnover and low Fitness | No immediate retest | `group_neutralize(ts_decay_linear(rank(ts_rank(implied_volatility_mean_skew_90, 60)), 20), subindustry)` |
| `model16` / model factor derivatives | `multi_factor_acceleration_score_derivative`, `multi_factor_static_score_derivative`, `relative_valuation_rank_derivative`, `growth_potential_rank_derivative`, `analyst_revision_rank_derivative`, `cashflow_efficiency_rank_derivative`, `earnings_certainty_rank_derivative` | Slow factor-rerating fields can test changes in quality, valuation, growth, and analyst revision ranks. | 60-120 days | Low to medium | Distinct | Partly related to failed fourth quality seed, but derivative fields beyond the tested fscore/cashflow mix are different | Some fields have full coverage but may be too weak alone; model16 quality seed failed hard | Watchlist only | `group_neutralize(ts_decay_linear(rank(ts_mean(multi_factor_acceleration_score_derivative, 60)), 20), subindustry)` |
| `model51` / risk model | `beta_last_90_days_spy`, `systematic_risk_last_90_days`, `correlation_last_90_days_spy`, 30/60/360 day siblings | Risk exposure fields can be overlays or standalone defensive effects. | 60-360 days | Low to medium | Distinct | Do not combine with close60 reversal, which already failed | Standalone low-risk effect may be crowded or low return; coverage around 76-78% | Watchlist only | `group_neutralize(ts_decay_linear(-rank(ts_mean(systematic_risk_last_90_days, 60)), 20), subindustry)` |
| `fundamental2` / corporate action and shares | `fn_proceeds_from_issuance_of_debt_q`, `fn_repayments_of_debt_q`, `fn_repurchased_shares_value_q`, `fn_proceeds_from_issuance_of_common_stock_q`, `fn_entity_common_stock_shares_out_q`, `fn_entity_common_stock_shares_out_a` | Balance-sheet change, issuance, debt, and share-count behavior can signal financing pressure or capital return. | 120-252 days | Low | Distinct | Related to failed fourth corporate-action seed, which had low drawdown but weak Fitness | Slow update frequency; may be too low turnover; prior seed did not justify variants | No immediate retest | `group_neutralize(ts_decay_linear(-rank(ts_delta(fn_entity_common_stock_shares_out_q, 252)), 20), subindustry)` |
| Insider / event news | `rp_ess_insider`, `rp_css_insider`, `rp_nip_insider` | Insider-trading news sentiment and impact may identify unusual event information. | 20-63 days | Sparse, medium if smoothed | Distinct | Distinct from recent failures | 50% coverage and event sparsity; concentration risk | Watchlist only | `group_neutralize(ts_decay_linear(rank(ts_mean(rp_css_insider, 63)), 10), subindustry)` |
| Institutional ownership / ESG | No local verified institutional ownership field; ESG-like matches were not true ESG fields | Not enough verified local evidence | n/a | n/a | n/a | n/a | Field names not confirmed in current cache | No | Revisit only after fresh official field search |

## Candidate Seed Designs For Future Fifth Batch

These designs are not run. They are intentionally capped at three because the next executable batch should remain tiny.

### 1. social_sentiment_fast_persistence_seed

- Verified fields used: `scl12_sentiment_fast_d1`
- Expression draft: `group_neutralize(ts_decay_linear(rank(ts_mean(scl12_sentiment_fast_d1, 20)), 10), subindustry)`
- Rationale: tests a high-coverage, lower-crowding social-media signal with smoothing to reduce raw daily turnover.
- Why distinct from `E5g7vMjJ`: no close, no volume, no close-volume correlation, no reversal.
- Why distinct from the nine failed candidates: not price/risk reversal, not simple model16 quality, not raw `anl4_mark`, not corporate-action debt/buyback.
- Expected turnover: medium, likely closer to target than raw sentiment because of 20-day smoothing and decay.
- Main risk: social signal can be weak after neutralization; may still correlate with broad sentiment.
- Continue after simulation only if: Fitness > 0.5, turnover < 0.30, no concentration/sub-universe failure.

### 2. analyst_disagreement_slow_seed

- Verified fields used: `anl4_qfv4_dts_spe`
- Expression draft: `group_neutralize(ts_decay_linear(-rank(ts_rank(anl4_qfv4_dts_spe, 120)), 20), subindustry)`
- Rationale: uses analyst estimate dispersion instead of raw analyst recommendation marks. The negative sign tests lower disagreement as a confidence/quality signal.
- Why distinct from `E5g7vMjJ`: pure analyst-estimate data, no price-volume correlation.
- Why distinct from the nine failed candidates: avoids `anl4_mark` and avoids the high-turnover raw recommendation structure; also not another close60 reversal.
- Expected turnover: low to medium due to 120-day time rank and 20-day decay.
- Main risk: 72% coverage can trigger sub-universe or weight issues.
- Continue after simulation only if: sign is positive, Fitness > 0.5, and sub-universe check does not fail hard.

### 3. short_interest_change_seed

- Verified fields used: `news_short_interest`
- Expression draft: `group_neutralize(ts_decay_linear(-rank(ts_rank(news_short_interest, 60)) - rank(ts_delta(news_short_interest, 20)), 20), subindustry)`
- Rationale: short-interest level plus recent change tests a positioning/crowding source that has not been part of the recent failed search path.
- Why distinct from `E5g7vMjJ`: no direct price or volume signal, no correlation reversal.
- Why distinct from the nine failed candidates: not a quality/efficiency model16 line, not raw analyst mark, not corporate-action debt/buyback, and not price/risk reversal.
- Expected turnover: low to medium; short-interest updates may be slow, but the 20-day delta adds responsiveness.
- Main risk: sign may be regime-dependent because high short interest can precede squeezes.
- Continue after simulation only if: Returns > 0, Drawdown < 0.12, Fitness > 0.5.

## Batch Recommendation

- Next executable action: run a future fifth batch of at most three manual seeds, only with explicit approval.
- Recommended first batch contents:
  - `social_sentiment_fast_persistence_seed`
  - `analyst_disagreement_slow_seed`
  - `short_interest_change_seed`
- Do not include:
  - `E5g7vMjJ` window/decay neighbors
  - close-volume correlation reversal
  - close60 reversal
  - raw `anl4_mark`
  - the exact fourth-family model16 quality or corporate-action structures
  - option PCR/skew retests before the higher-priority new sources are tried

## Planning Artifact

- Miner planning-only JSON: `manual_alphas/2026-04-28_fifth_batch_candidate_designs_DO_NOT_RUN.json`
- It is not an executable manual batch file for this turn.
- It uses a `candidates` array, not an `alphas` runner list.
- It includes `"do_not_run": true` and no simulation command.

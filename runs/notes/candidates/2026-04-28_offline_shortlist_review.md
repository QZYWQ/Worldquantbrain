# Offline Shortlist Review

- Date: 2026-04-28
- Scope: offline shortlist review only
- Input artifact: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-28_offline_shortlist_DO_NOT_RUN.json`
- Simulations run: none
- Simulation endpoint called: no
- Runnable batch created: no
- Shortlist count reviewed: 14

## Summary

The offline shortlist is structurally useful, but it is not a run queue. Many
entries are industry/subindustry pairs of the same expression. The review
therefore chooses at most one representative per expression family and avoids
spending a future batch on neutralization-only variants.

Recommended future simulation candidates: 3. They are intentionally from
different families:

1. forecast dispersion / earnings revision
2. valuation plus quality acceleration
3. insider or ownership proxy

All three are distinct from the E5 close-volume correlation reversal. None is a
direct retry of the failed option forward curve, Ravenpack credit/dividend, or
model51 beta/unsystematic-risk seeds.

Do not run these yet. If a later task explicitly approves simulation budget,
run at most these three candidates exactly as listed below.

## Recommended Future Simulation Candidates

### 1. earnings_revision_anl4_qfv4_eps_mean_anl4_qfv4_dts_spe_126_120_20_subindustry

- Family: `forecast_dispersion`
- Fields: `anl4_qfv4_eps_mean`, `anl4_qfv4_dts_spe`, `analyst_revision_rank_derivative`
- Heuristic score: 98
- Expected turnover bucket: `medium_high`
- Expression:

```text
group_neutralize(ts_decay_linear(rank(ts_delta(anl4_qfv4_eps_mean, 126)) - rank(ts_rank(anl4_qfv4_dts_spe, 120)) + rank(ts_mean(analyst_revision_rank_derivative, 120)), 20), subindustry)
```

- Why selected: This is the cleanest analyst-family candidate because it is not
  raw `anl4_mark` and not raw disagreement alone. It combines medium-horizon EPS
  estimate change, forecast-dispersion control, and vendor analyst-revision
  derivative into one interpretable thesis: improving estimates with lower
  uncertainty and positive revision context.
- Main risks: Analyst field coverage and crowding can still cause sub-universe
  or concentration weakness. The tool labels turnover `medium_high`; the 126-day
  delta, 120-day rank, and 20-day decay make it slower than the failed raw
  analyst-mark lane, but turnover should be watched first.
- Relation to E5: distinct; no close-volume correlation, no price reversal.
- Relation to failed lanes: materially different from failed raw `anl4_mark` and
  raw analyst disagreement. It is still an analyst source, so it should not be
  paired with another analyst candidate in the same future batch.

### 2. valuation_quality_relative_valuation_rank_derivative_cashflow_efficiency_rank_derivative_126_126_20_subindustry

- Family: `valuation_quality_acceleration`
- Fields: `relative_valuation_rank_derivative`,
  `cashflow_efficiency_rank_derivative`, `growth_potential_rank_derivative`
- Heuristic score: 98
- Expected turnover bucket: `medium_high`
- Expression:

```text
group_neutralize(ts_decay_linear(rank(ts_mean(relative_valuation_rank_derivative, 126)) + rank(ts_delta(cashflow_efficiency_rank_derivative, 126)) + rank(ts_mean(growth_potential_rank_derivative, 126)), 20), subindustry)
```

- Why selected: This is the best fundamental/model-score composite in the
  shortlist. It uses valuation, cash-flow efficiency change, and growth
  potential over medium horizons, rather than static quality alone. The
  economic intuition is straightforward: improving efficient growth at a better
  valuation should carry more information than a single model16 quality seed.
- Main risks: It is still near the broader model16/fundamental family, where the
  fourth manual batch failed. It may be too vendor-composite-driven or too
  neutralized at subindustry level. The `medium_high` bucket should be watched,
  although all active windows are 126 days plus 20-day decay.
- Relation to E5: distinct; no close, no volume, no close-volume correlation.
- Relation to failed lanes: not the failed simple cashflow/assets plus
  revenue/assets stability lane and not the failed static quality/efficiency
  seed. It is the closest recommended candidate to a prior failed family, so it
  should be killed quickly if the first result has weak Fitness.

### 3. insider_proxy_rp_ess_insider_cashflow_efficiency_rank_derivative_126_126_20

- Family: `ownership_or_insider_proxy`
- Fields: `rp_ess_insider`, `cashflow_efficiency_rank_derivative`,
  `fn_entity_common_stock_shares_out_q`
- Heuristic score: 94
- Expected turnover bucket: `medium_high`
- Expression:

```text
group_neutralize(ts_decay_linear(rank(ts_mean(rp_ess_insider, 126)) + rank(ts_delta(cashflow_efficiency_rank_derivative, 126)) - rank(ts_delta(fn_entity_common_stock_shares_out_q, 252)), 20), subindustry)
```

- Why selected: This gives the future batch a genuinely different source:
  insider-event news plus quality acceleration plus dilution pressure. It is not
  raw social sentiment, not raw short interest, not the failed credit/dividend
  Ravenpack pair, and not a price-volume expression.
- Main risks: Ravenpack/event fields can be sparse. Concentration and
  sub-universe checks are the likely first blockers. The share-count delta may
  also make the signal slow or lumpy.
- Relation to E5: distinct; no close-volume correlation or price reversal.
- Relation to failed lanes: distinct from failed `rp_nip_credit_ratings` plus
  `rp_ess_dividends`, and distinct from failed corporate-action debt/buyback
  seed because insider event information is the primary source.

## Reviewed Candidate Decisions

| Candidate | Family | Score | Turnover | Decision | Review |
| --- | --- | ---: | --- | --- | --- |
| `balance_sheet_accel_assets_cashflow_efficiency_rank_derivative_growth_potential_rank_derivative_126_industry` | `accruals_asset_growth_balance_sheet` | 98 | `medium_high` | Not prioritized | Same expression as subindustry variant with looser neutralization. Good score, but asset-growth/accounting exposure is closer to prior accounting and corporate-action failures than the selected valuation-quality candidate. |
| `balance_sheet_accel_assets_cashflow_efficiency_rank_derivative_growth_potential_rank_derivative_126_subindustry` | `accruals_asset_growth_balance_sheet` | 98 | `medium_high` | Not prioritized | Better neutralization than industry version, but still a balance-sheet/accounting acceleration line. Keep as fallback only if valuation-quality fails for over-neutralization rather than weak thesis. |
| `earnings_revision_anl4_qfv4_eps_mean_anl4_qfv4_dts_spe_126_120_20_industry` | `forecast_dispersion` | 98 | `medium_high` | Not prioritized | Same expression as selected analyst candidate with industry neutralization. Use the subindustry version first for stricter sector control. |
| `earnings_revision_anl4_qfv4_eps_mean_anl4_qfv4_dts_spe_126_120_20_subindustry` | `forecast_dispersion` | 98 | `medium_high` | Recommended | Multi-field analyst revision and dispersion composite. Not raw `anl4_mark`, not raw disagreement alone, and far from E5. |
| `valuation_quality_relative_valuation_rank_derivative_cashflow_efficiency_rank_derivative_126_126_20_industry` | `valuation_quality_acceleration` | 98 | `medium_high` | Not prioritized | Same valuation-quality expression with looser neutralization. Keep as a later diagnostic variant if subindustry version loses too much signal. |
| `valuation_quality_relative_valuation_rank_derivative_cashflow_efficiency_rank_derivative_126_126_20_subindustry` | `valuation_quality_acceleration` | 98 | `medium_high` | Recommended | Best fundamental composite: valuation, cash-flow efficiency acceleration, and growth potential. Not static quality alone. |
| `insider_proxy_rp_ess_insider_cashflow_efficiency_rank_derivative_126_126_20` | `ownership_or_insider_proxy` | 94 | `medium_high` | Recommended | Most differentiated non-analyst, non-model16 candidate. Uses insider-event news plus quality change and dilution pressure. Sparse-event risk is accepted for diversification. |
| `insider_proxy_rp_ess_insider_cashflow_efficiency_rank_derivative_126_63_20` | `ownership_or_insider_proxy` | 94 | `medium_high` | Not prioritized | Same family as selected insider candidate but faster 63-day quality delta. Higher turnover risk, so do not put it in the first future batch. |
| `option_positioning_pcr_oi_360_historical_volatility_60_120_10_industry` | `option_positioning_or_volatility` | 89 | `high` | Not prioritized | Distinct from failed forward-curve seed, but option PCR/skew/volatility lanes have prior weakness and the tool flags high turnover. |
| `option_positioning_pcr_oi_360_historical_volatility_60_120_10_subindustry` | `option_positioning_or_volatility` | 89 | `high` | Not prioritized | Same as industry option candidate with stricter neutralization. Still high-turnover and adjacent to old option positioning work. |
| `ravenpack_slow_rp_ess_credit_rp_css_business_126_10_industry` | `ravenpack_news_slow_aggregate` | 88 | `high` | Not prioritized | Different from failed credit/dividend pair, but sparse news coverage plus 10-day decay makes concentration and turnover risk too high for the first future batch. |
| `ravenpack_slow_rp_ess_credit_rp_css_business_126_10_subindustry` | `ravenpack_news_slow_aggregate` | 88 | `high` | Not prioritized | Same Ravenpack idea with stricter neutralization. Not selected because insider proxy gives a cleaner event-news diversification candidate. |
| `risk_quality_systematic_risk_last_90_days_correlation_last_90_days_spy_analyst_revision_rank_derivative_120_20_industry` | `risk_model_standalone` | 88 | `medium_high` | Not prioritized | More robust than the failed unsystematic-risk plus beta seed, but still a crowded risk-model family and partly analyst-overlay dependent. |
| `risk_quality_systematic_risk_last_90_days_correlation_last_90_days_spy_analyst_revision_rank_derivative_120_20_subindustry` | `risk_model_standalone` | 88 | `medium_high` | Not prioritized | Same risk-quality expression with stricter neutralization. Keep only as later fallback if the selected analyst candidate shows promising revision signal but needs risk control. |

## Rejected Or Not-Prioritized Family Summary

- `accruals_asset_growth_balance_sheet`: credible but too close to accounting
  and corporate-action failures for the next three-name batch.
- `option_positioning_or_volatility`: distinct from the failed forward curve,
  but high turnover and prior option-family weakness make it lower priority.
- `ravenpack_news_slow_aggregate`: not the failed credit/dividend pair, but
  sparse coverage and high turnover risk make it weaker than the insider proxy.
- `risk_model_standalone`: improved over the failed model51 seed, but still
  crowded and adjacent to the failed risk-model lane.
- Neutralization duplicates: industry variants are kept as diagnostic backups,
  not first-batch candidates.

## Final Recommendation

Do not run anything yet. If the user later explicitly approves a future manual
simulation batch, run at most these three candidates exactly as listed:

1. `earnings_revision_anl4_qfv4_eps_mean_anl4_qfv4_dts_spe_126_120_20_subindustry`
2. `valuation_quality_relative_valuation_rank_derivative_cashflow_efficiency_rank_derivative_126_126_20_subindustry`
3. `insider_proxy_rp_ess_insider_cashflow_efficiency_rank_derivative_126_126_20`

Stop after that batch if no candidate reaches hopeful evidence, especially
Fitness above 0.5 or another explicit research reason to continue.

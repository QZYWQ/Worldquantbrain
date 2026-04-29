# Offline Generation V3 Results

- Date: 2026-04-29
- Scope: offline broad generation and pre-simulation triage only
- WQ simulations run in this task: none
- Simulation endpoint called in this task: no
- Runnable batch created in this task: no
- Miner seed pool: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_candidate_seed_pool_v3_DO_NOT_RUN.json`
- Miner shortlist: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_shortlist_v3_DO_NOT_RUN.json`

## Summary

Offline generation v3 used the v3 design artifact plus the imported
Worldquantbrain historical lessons as negative knowledge. The generated pool
contains local-only templates and expressions; it is not a runnable batch and
must not be passed to the simulation runner.

No alpha in this task was submitted to WorldQuant BRAIN. No credential contents
were read.

## Counts

| Metric | Count |
| --- | ---: |
| Input candidates | 196 |
| After hard filters and deduplication | 196 |
| Shortlisted candidates | 16 |

The shortlist used at most two representatives per detected family and rejected
group/decay-only template twins with
`near_duplicate_template_shape_exceeded:*`.

## Historical Lessons Source

- Machine-readable source:
  `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_worldquantbrain_historical_experience_import_DO_NOT_RUN.json`
- Human-readable source:
  `/Users/zpdedn/Documents/github/worldquant-miner/docs/WORLDQUANTBRAIN_HISTORICAL_ALPHA_LESSONS.md`
- Historical lessons applied: yes
- Confirmed killed/frozen lanes loaded: 18
- Hold/incubate lanes loaded: 4

The v3 pool kept hold/incubate lanes open only when the field mix and structure
were materially different. For example, the option candidates use
`pcr_oi_720` with implied-volatility skew and analyst/growth confirmation
rather than a raw PCR or breakeven single-source seed.

## Families Represented

| Family | Candidates after filters | Shortlisted |
| --- | ---: | ---: |
| `accruals_asset_growth_balance_sheet` | 24 | 2 |
| `forecast_dispersion` | 40 | 2 |
| `option_positioning_or_volatility` | 24 | 2 |
| `ownership_or_insider_proxy` | 20 | 2 |
| `profitability_acceleration` | 8 | 2 |
| `ravenpack_news_slow_aggregate` | 24 | 2 |
| `risk_model_standalone` | 24 | 2 |
| `valuation_quality_acceleration` | 32 | 2 |

## Rejected Or Penalized Forms

The v3 generated expressions intentionally avoided known failed-neighbor and
historical-kill structures. The triage layer remains configured to reject or
penalize these examples before any manual simulation review:

- E5 close-volume correlation reversal, including
  `ts_corr(rank(close), rank(volume), 60/70/80/90)`.
- close60 reversal lanes with volatility/range or volume-ratio conditioners.
- The failed v2 accruals form combining
  `cashflow_efficiency_rank_derivative`, `assets`, and `cashflow_op`.
- The failed v2 sales-revision form combining
  `sales_estimate_average_annual`, `lowest_sales_estimate`, and
  `analyst_revision_rank_derivative`.
- The failed v2 option form combining `pcr_oi_360` and
  `historical_volatility_60`.
- Historical-kill simple forms such as raw buzz stability, QCM news attention,
  raw analyst disagreement/inverse DTS-SPE, capex static ratios, invested
  capital history ranks, option breakeven/PCR single-source seeds, and raw
  socialmedia sentiment seeds.

The actual v3 run did not need to hard-reject failed-neighbor expressions,
because the seed pool was constructed away from those forms. Its rejections
were from family caps and near-duplicate template-shape diversity checks.

## Shortlist Summary

| Rank | Name | Family | Score | Turnover bucket | Main risk flags |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_126_24_industry` | `accruals_asset_growth_balance_sheet` | 98 | `low_medium` | none |
| 2 | `alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_189_24_industry` | `accruals_asset_growth_balance_sheet` | 98 | `low_medium` | none |
| 3 | `earnings_revision_restruct_highest_sales_estimate_sales_estimate_dispersion_analyst_revision_rank_derivative_126_24_industry` | `forecast_dispersion` | 98 | `low_medium` | none |
| 4 | `earnings_revision_restruct_highest_sales_estimate_sales_estimate_dispersion_analyst_revision_rank_derivative_189_24_industry` | `forecast_dispersion` | 98 | `low_medium` | none |
| 5 | `profit_accel_distinct_fscore_bfl_profitability_growth_potential_rank_derivative_inventory_turnover_126_24_industry` | `profitability_acceleration` | 98 | `low_medium` | none |
| 6 | `profit_accel_distinct_fscore_bfl_profitability_growth_potential_rank_derivative_inventory_turnover_189_24_industry` | `profitability_acceleration` | 98 | `low_medium` | none |
| 7 | `liquidity_quality_non_corr_v3_earnings_certainty_rank_derivative_126_126_24_industry` | `valuation_quality_acceleration` | 98 | `low_medium` | none |
| 8 | `liquidity_quality_non_corr_v3_earnings_certainty_rank_derivative_126_189_24_industry` | `valuation_quality_acceleration` | 98 | `low_medium` | none |
| 9 | `option_iv_restruct_pcr_oi_720_implied_volatility_mean_skew_180_analyst_revision_rank_derivative_120_24_industry` | `option_positioning_or_volatility` | 95 | `low_medium` | `options_coverage_risk` |
| 10 | `option_iv_restruct_pcr_oi_720_implied_volatility_mean_skew_180_analyst_revision_rank_derivative_180_24_industry` | `option_positioning_or_volatility` | 95 | `low_medium` | `options_coverage_risk` |
| 11 | `ownership_insider_distinct_rp_css_insider_analyst_revision_rank_derivative_fn_entity_common_stock_shares_out_q_126_24_industry` | `ownership_or_insider_proxy` | 94 | `low_medium` | `news_sparse_coverage_risk` |
| 12 | `ownership_insider_distinct_rp_css_insider_analyst_revision_rank_derivative_fn_entity_common_stock_shares_out_q_84_24_industry` | `ownership_or_insider_proxy` | 94 | `low_medium` | `news_sparse_coverage_risk` |
| 13 | `ravenpack_cross_confirm_rp_ess_credit_rp_css_business_earnings_certainty_rank_derivative_126_24_industry` | `ravenpack_news_slow_aggregate` | 94 | `low_medium` | `news_sparse_coverage_risk` |
| 14 | `ravenpack_cross_confirm_rp_ess_credit_rp_css_business_earnings_certainty_rank_derivative_84_24_industry` | `ravenpack_news_slow_aggregate` | 94 | `low_medium` | `news_sparse_coverage_risk` |
| 15 | `profit_accel_distinct_fscore_bfl_profitability_growth_potential_rank_derivative_systematic_risk_last_90_days_126_24_industry` | `risk_model_standalone` | 88 | `low_medium` | none |
| 16 | `quality_revision_risk_overlay_earnings_certainty_rank_derivative_systematic_risk_last_90_days_126_24_industry` | `risk_model_standalone` | 88 | `low_medium` | none |

## Recommendation

Review the v3 shortlist manually before any simulation. Do not run these yet.

If a future task explicitly approves simulation, select at most three exact
expressions across distinct families into a separate runnable manual batch. Do
not generate variants during that run, and keep this v3 artifact as
`DO_NOT_RUN`.

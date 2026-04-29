# Offline Generation V4 Results

- Date: 2026-04-29
- Scope: offline broad generation and pre-simulation triage only
- WQ simulations run in this task: none
- Simulation endpoint called in this task: no
- Runnable batch created in this task: no
- Credential contents read in this task: no
- Miner seed pool: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_candidate_seed_pool_v4_DO_NOT_RUN.json`
- Miner shortlist: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_shortlist_v4_DO_NOT_RUN.json`

## Summary

Offline generation v4 used the v4 design artifact plus the miner-side imported
Worldquantbrain historical lessons as negative knowledge. The generated pool is
planning-only, `DO_NOT_RUN`, and is not a runnable simulation batch.

The v4 pool deliberately keeps broad families open while penalizing only the
specific failed structures and close near-neighbors: E5 close-volume correlation,
close60 reversal, reviewed top3 failures, v2 top3 failures, the v3 single
tracking failure, and confirmed historical killed/frozen simple lanes.

## Counts

| Metric | Count |
| --- | ---: |
| Input candidates | 260 |
| After hard filters and deduplication | 260 |
| Shortlisted candidates | 20 |

The shortlist uses at most two representatives per detected family. Additional
same-family candidates and group/decay-only template twins were kept out of the
top shortlist by family caps and template-shape diversity checks.

## Historical Lessons Source

- Machine-readable source: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_worldquantbrain_historical_experience_import_DO_NOT_RUN.json`
- Human-readable source: `/Users/zpdedn/Documents/github/worldquant-miner/docs/WORLDQUANTBRAIN_HISTORICAL_ALPHA_LESSONS.md`
- V4 design source: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_generation_v4_design_DO_NOT_RUN.json`
- Historical lessons applied: yes
- Confirmed killed/frozen lanes loaded: 18
- Hold/incubate lanes loaded: 4

Hold/incubate historical lanes were not hard-rejected by default. The v4 pool
only hard avoids or penalizes a lane when the candidate is near a concrete failed
structure.

## Families Represented

| Family | Candidates after filters | Shortlisted |
| --- | ---: | ---: |
| `accruals_asset_growth_balance_sheet` | 52 | 2 |
| `earnings_estimate_revision` | 18 | 2 |
| `forecast_dispersion` | 20 | 2 |
| `model_multi_factor_acceleration` | 16 | 2 |
| `option_positioning_or_volatility` | 36 | 2 |
| `ownership_or_insider_proxy` | 16 | 2 |
| `ravenpack_news_slow_aggregate` | 38 | 2 |
| `risk_model_standalone` | 38 | 2 |
| `short_interest_coverage_revision` | 14 | 2 |
| `valuation_quality_acceleration` | 12 | 2 |

## Rejected Or Penalized Failed-Neighbor Examples

The v4 seed pool was constructed away from these forms, and the triage layer
remains configured to reject or penalize them before any manual simulation
review:

- V3 single tracking failure: `earnings_certainty_rank_derivative + inventory_turnover + fn_proceeds_from_issuance_of_common_stock_q` in a simple 126/189 medium-horizon `group_zscore` / `rank` / `ts_decay_linear` industry or subindustry form. Source alpha `om3M3Agb` failed Sharpe/Fitness and is now a near-neighbor penalty, not a global accruals ban.
- E5 close-volume correlation reversal, including `ts_corr(rank(close), rank(volume), 60/70/80/90)` and close-volume reversal siblings.
- close60 reversal lanes with volatility/range or volume-ratio conditioners.
- Reviewed top3 simple failures: `rp_ess_insider + cashflow_efficiency_rank_derivative + share-count`, `anl4_qfv4_eps_mean + anl4_qfv4_dts_spe`, and `relative_valuation_rank_derivative + cashflow_efficiency_rank_derivative + growth_potential` simple rank/decay forms.
- V2 top3 simple failures: `cashflow_efficiency_rank_derivative + assets + cashflow_op`, `sales_estimate_average_annual + lowest_sales_estimate + analyst_revision_rank_derivative`, and `pcr_oi_360 + historical_volatility_60` simple medium-horizon forms.
- Historical-kill simple forms: raw buzz stability, QCM/news relevance attention, raw analyst disagreement or inverse DTS-SPE, capex static ratios, invested-capital history rank, raw option breakeven/PCR seeds, and raw socialmedia sentiment seeds.

## Shortlist Summary

| Rank | Name | Family | Score | Turnover bucket | Main risk flags |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `v4_eps_median_revision_quality_anl4_qfv4_median_eps_earnings_certainty_rank_derivative_84_84_12_industry` | `earnings_estimate_revision` | 98 | `medium_high` | none |
| 2 | `v4_forecast_breadth_dispersion_highest_sales_estimate_analyst_revision_rank_derivative_84_84_12_industry` | `forecast_dispersion` | 98 | `medium_high` | none |
| 3 | `v4_liquidity_quality_non_corr_earnings_certainty_rank_derivative_analyst_revision_rank_derivative_63_84_12_industry` | `valuation_quality_acceleration` | 98 | `medium_high` | none |
| 4 | `v4_option_iv_quality_hedge_implied_volatility_mean_skew_90_analyst_revision_rank_derivative_84_84_12_industry` | `option_positioning_or_volatility` | 95 | `medium_high` | `options_coverage_risk` |
| 5 | `v4_accrual_debt_quality_cashflow_efficiency_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_debt_q_126_126_12_industry` | `accruals_asset_growth_balance_sheet` | 88 | `medium_high` | `low_turnover_inertia_risk` |
| 6 | `v4_accrual_debt_quality_cashflow_efficiency_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_debt_q_84_126_12_industry` | `accruals_asset_growth_balance_sheet` | 88 | `medium_high` | `low_turnover_inertia_risk` |
| 7 | `v4_eps_median_revision_quality_anl4_qfv4_median_eps_earnings_certainty_rank_derivative_126_84_12_industry` | `earnings_estimate_revision` | 88 | `medium_high` | `low_turnover_inertia_risk` |
| 8 | `v4_forecast_breadth_dispersion_highest_sales_estimate_analyst_revision_rank_derivative_126_120_12_industry` | `forecast_dispersion` | 88 | `medium_high` | `low_turnover_inertia_risk` |
| 9 | `v4_model_multifactor_accel_84_84_84_12_industry` | `model_multi_factor_acceleration` | 88 | `medium_high` | none |
| 10 | `v4_profitability_revision_overlay_fscore_bfl_profitability_analyst_revision_rank_derivative_systematic_risk_last_90_days_84_84_12_industry` | `risk_model_standalone` | 88 | `medium_high` | none |
| 11 | `v4_valuation_quality_risk_relative_valuation_rank_derivative_earnings_certainty_rank_derivative_systematic_risk_last_90_days_84_84_12_industry` | `risk_model_standalone` | 88 | `medium_high` | none |
| 12 | `v4_liquidity_quality_non_corr_earnings_certainty_rank_derivative_analyst_revision_rank_derivative_63_126_12_industry` | `valuation_quality_acceleration` | 88 | `medium_high` | `low_turnover_inertia_risk` |
| 13 | `v4_option_iv_quality_hedge_implied_volatility_mean_skew_90_analyst_revision_rank_derivative_126_120_12_industry` | `option_positioning_or_volatility` | 85 | `medium_high` | `low_turnover_inertia_risk`, `options_coverage_risk` |
| 14 | `v4_ownership_rebuilt_rp_css_insider_analyst_revision_rank_derivative_fn_entity_common_stock_shares_out_q_126_12_industry` | `ownership_or_insider_proxy` | 84 | `medium_high` | `low_turnover_inertia_risk`, `news_sparse_coverage_risk` |
| 15 | `v4_ownership_rebuilt_rp_css_insider_analyst_revision_rank_derivative_fn_entity_common_stock_shares_out_q_84_12_industry` | `ownership_or_insider_proxy` | 84 | `medium_high` | `low_turnover_inertia_risk`, `news_sparse_coverage_risk` |
| 16 | `v4_news_revision_risk_rp_nip_revenue_analyst_revision_rank_derivative_systematic_risk_last_90_days_126_120_12_industry` | `ravenpack_news_slow_aggregate` | 84 | `medium_high` | `low_turnover_inertia_risk`, `news_sparse_coverage_risk` |
| 17 | `v4_news_revision_risk_rp_nip_revenue_analyst_revision_rank_derivative_systematic_risk_last_90_days_126_84_12_industry` | `ravenpack_news_slow_aggregate` | 84 | `medium_high` | `low_turnover_inertia_risk`, `news_sparse_coverage_risk` |
| 18 | `v4_short_interest_coverage_revision_mean_63_63_84_84_12_industry` | `short_interest_coverage_revision` | 82 | `medium` | none |
| 19 | `v4_model_multifactor_accel_84_126_84_12_industry` | `model_multi_factor_acceleration` | 78 | `medium_high` | `low_turnover_inertia_risk` |
| 20 | `v4_short_interest_coverage_revision_mean_63_63_126_84_12_industry` | `short_interest_coverage_revision` | 72 | `low_medium` | `low_turnover_inertia_risk` |

## Recommendation

Review the v4 shortlist manually before any simulation. Do not run these yet.
If a future task explicitly approves simulation, select at most three exact
expressions across distinct families into a separate runnable manual batch, and
keep this v4 artifact as `DO_NOT_RUN`.

# Offline Generation V2 Results

- Date: 2026-04-29
- Scope: offline broad generation and pre-simulation triage only
- WQ simulations run in this task: none
- Simulation endpoint called in this task: no
- Runnable batch created in this task: no
- Miner seed pool: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_candidate_seed_pool_v2_DO_NOT_RUN.json`
- Miner shortlist: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_shortlist_v2_DO_NOT_RUN.json`

## Summary

Offline generation v2 used the feedback-aware triage layer after the reviewed
top-3 simulation failure. The pool was intentionally broad, but still bounded:
it generated or collected 176 local-only candidate expressions and then applied
local syntax, field, fingerprint, failed-family, E5-neighbor, reviewed-top3
near-neighbor, family-clustering, and heuristic scoring filters.

No alpha in this task was submitted to WorldQuant BRAIN. The output is a
`DO_NOT_RUN` shortlist for manual review only.

## Counts

| Metric | Count |
| --- | ---: |
| Input candidates | 176 |
| After hard filters and deduplication | 164 |
| Shortlisted candidates | 14 |

The shortlist used a maximum of two representatives per family after scoring.

## Families Represented

| Family | Candidates after filters | Shortlisted |
| --- | ---: | ---: |
| `accruals_asset_growth_balance_sheet` | 60 | 2 |
| `earnings_estimate_revision` | 8 | 2 |
| `forecast_dispersion` | 16 | 2 |
| `valuation_quality_acceleration` | 24 | 2 |
| `option_positioning_or_volatility` | 24 | 2 |
| `ravenpack_news_slow_aggregate` | 24 | 2 |
| `risk_model_standalone` | 8 | 2 |

## Filters And Rejection Examples

The triage run applied:

- syntax and operator-shape sanity checks
- verified-field checks when field lists were available
- fingerprint and normalized-expression deduplication
- failed-family and E5-neighbor exclusion
- reviewed-top3 failure-shape penalties
- heuristic risk scoring
- family clustering with one to two representatives per family

Rejected or explicitly penalized failed-neighbor examples:

- `negative_control_e5_corr70` was rejected by
  `blocked_close_volume_corr70`, `close_volume_correlation_reversal_family`,
  `e5_close_volume_correlation_neighbor`, and
  `negative_control_not_for_shortlist`.
- `negative_control_reviewed_top3_forecast_dispersion` represented the failed
  simple `anl4_qfv4_eps_mean` plus `anl4_qfv4_dts_spe` form and was excluded
  from the shortlist as a negative control.
- `negative_control_reviewed_top3_valuation_quality` represented the failed
  simple `relative_valuation_rank_derivative` plus
  `cashflow_efficiency_rank_derivative` form and was excluded from the
  shortlist as a negative control.
- `negative_control_reviewed_top3_insider_proxy` represented the failed simple
  `rp_ess_insider` plus cash-flow efficiency form and was excluded from the
  shortlist as a negative control.
- Simple `cashflow/assets + revenue/assets` stability variants were rejected
  under `simple_cashflow_assets_revenue_assets_stability`.

These controls confirm the v2 pool is not merely reopening E5, close60, or the
latest top-3 failed forms.

## Shortlist Summary

| Rank | Name | Family | Score | Turnover bucket | Main risk flags |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_industry` | `accruals_asset_growth_balance_sheet` | 98 | `medium_high` | none |
| 2 | `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_subindustry` | `accruals_asset_growth_balance_sheet` | 98 | `medium_high` | none |
| 3 | `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_industry` | `earnings_estimate_revision` | 98 | `medium_high` | none |
| 4 | `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_subindustry` | `earnings_estimate_revision` | 98 | `medium_high` | none |
| 5 | `sales_revision_norm_sales_estimate_average_annual_sales_estimate_dispersion_analyst_revision_rank_derivative_126_12_industry` | `forecast_dispersion` | 98 | `medium_high` | none |
| 6 | `sales_revision_norm_sales_estimate_average_annual_sales_estimate_dispersion_analyst_revision_rank_derivative_126_12_subindustry` | `forecast_dispersion` | 98 | `medium_high` | none |
| 7 | `liquidity_quality_non_corr_earnings_certainty_rank_derivative_126_126_12_industry` | `valuation_quality_acceleration` | 98 | `medium_high` | none |
| 8 | `liquidity_quality_non_corr_earnings_certainty_rank_derivative_126_126_12_subindustry` | `valuation_quality_acceleration` | 98 | `medium_high` | none |
| 9 | `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_industry` | `option_positioning_or_volatility` | 89 | `low_medium` | `options_coverage_risk` |
| 10 | `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_subindustry` | `option_positioning_or_volatility` | 89 | `low_medium` | `options_coverage_risk` |
| 11 | `event_news_confirm_rp_ess_credit_rp_css_business_126_12_industry` | `ravenpack_news_slow_aggregate` | 88 | `low_medium` | `news_sparse_coverage_risk` |
| 12 | `event_news_confirm_rp_ess_credit_rp_css_business_126_12_subindustry` | `ravenpack_news_slow_aggregate` | 88 | `low_medium` | `news_sparse_coverage_risk` |
| 13 | `quality_risk_overlay_earnings_certainty_rank_derivative_systematic_risk_last_90_days_120_12_industry` | `risk_model_standalone` | 88 | `medium_high` | none |
| 14 | `quality_risk_overlay_earnings_certainty_rank_derivative_systematic_risk_last_90_days_120_12_subindustry` | `risk_model_standalone` | 88 | `medium_high` | none |

## Interpretation

The strongest v2 cluster is balance-sheet and accruals normalization, because
it combines cash-flow efficiency acceleration, asset-growth penalty, and
operating cash-flow confirmation without reusing the failed simple
cashflow/assets plus revenue/assets stability seed.

The estimate-revision and forecast-dispersion entries are structurally
different from the failed EPS mean plus DTS dispersion top-3 candidate: they
use sales estimate fields, analyst revision derivative confirmation, and
sector-normalized components. They still need manual review before any
simulation because analyst-derived fields can be crowded or coverage-sensitive.

The option and Ravenpack entries are retained as underexplored data families,
but both carry explicit coverage risk. They should not outrank cleaner
fundamental acceleration entries unless manual review confirms field coverage
and economic rationale.

## Recommendation

Review the v2 shortlist manually before any simulation. Do not run these yet.

If a future task explicitly approves simulation, pick at most three candidates,
preferably from different families, and copy their expressions exactly from the
`DO_NOT_RUN` shortlist into a separate runnable manual batch. Do not create
variants during that run.

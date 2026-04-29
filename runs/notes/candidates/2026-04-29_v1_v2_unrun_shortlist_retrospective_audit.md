# V1/V2 Unrun Shortlist Retrospective Audit

- Date: 2026-04-29
- Scope: retrospective audit only
- WQ simulations run in this task: none
- Simulation endpoint called in this task: no
- Runnable batch created in this task: no
- Credential contents read in this task: no
- Miner files changed in this task: no

This audit reviews the v1 and v2 offline shortlist candidates that were not
actually simulated. It uses the later reviewed-top3 and v2-top3 simulation
results as negative feedback, but does not reclassify unrun candidates as
failed. The goal is only to separate remaining unrun ideas into `hold` and
`deprioritized` buckets for future planning.

## Inputs

- V1 shortlist:
  `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-28_offline_shortlist_DO_NOT_RUN.json`
- V1 reviewed top3 batch:
  `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_reviewed_shortlist_top3_manual_batch.json`
- V1 results note:
  `runs/notes/candidates/2026-04-29_reviewed_shortlist_top3_results.md`
- V2 shortlist:
  `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_shortlist_v2_DO_NOT_RUN.json`
- V2 reviewed top3 batch:
  `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_v2_reviewed_top3_manual_batch.json`
- V2 results note:
  `runs/notes/candidates/2026-04-29_v2_reviewed_top3_results.md`

## Run Status Reconciliation

| Source | Shortlisted | Actually simulated later | Unrun candidates audited |
| --- | ---: | ---: | ---: |
| V1 offline shortlist | 14 | 3 | 11 |
| V2 offline shortlist | 14 | 3 | 11 |

V1 simulated and failed later:

- `earnings_revision_anl4_qfv4_eps_mean_anl4_qfv4_dts_spe_126_120_20_subindustry`
- `valuation_quality_relative_valuation_rank_derivative_cashflow_efficiency_rank_derivative_126_126_20_subindustry`
- `insider_proxy_rp_ess_insider_cashflow_efficiency_rank_derivative_126_126_20`

V2 simulated and failed later:

- `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_subindustry`
- `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_industry`
- `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_industry`

These six are not part of the unrun hold/deprioritized tables below.

## Hold Candidates

These unrun candidates are not approved for simulation. They are retained as
lower-priority planning inventory because they are not exact copies of the
later failed simulated forms, or because they could be useful as diagnostics if
a newer family shows partial promise.

| Source | Candidate | Family | Hold rationale |
| --- | --- | --- | --- |
| V1 | `balance_sheet_accel_assets_cashflow_efficiency_rank_derivative_growth_potential_rank_derivative_126_subindustry` | `accruals_asset_growth_balance_sheet` | Unrun accounting/quality composite using growth-potential confirmation and asset-growth penalty. Hold only as legacy comparison; v3's earnings-certainty/inventory/issuance formulation is cleaner. |
| V1 | `risk_quality_systematic_risk_last_90_days_correlation_last_90_days_spy_analyst_revision_rank_derivative_120_20_industry` | `risk_model_standalone` | Unrun risk-overlay diagnostic that differs from the failed beta/unsystematic-risk seed. Hold for later if revision candidates need a risk-control comparison. |
| V2 | `sales_revision_norm_sales_estimate_average_annual_sales_estimate_dispersion_analyst_revision_rank_derivative_126_12_industry` | `forecast_dispersion` | Unrun dispersion version without the failed low-estimate leg. Hold as analyst-family backup, but v3's highest-sales-estimate version is preferable. |
| V2 | `liquidity_quality_non_corr_earnings_certainty_rank_derivative_126_126_12_industry` | `valuation_quality_acceleration` | Explicitly non-E5 liquidity overlay with no close-volume correlation. Hold as a non-correlation liquidity diagnostic, not a first-run candidate. |
| V2 | `event_news_confirm_rp_ess_credit_rp_css_business_126_12_industry` | `ravenpack_news_slow_aggregate` | Cross-confirmed news fields, not the failed credit/dividend aggregate. Hold because coverage risk remains high and v3 has better cross-confirmed news alternatives. |
| V2 | `quality_risk_overlay_earnings_certainty_rank_derivative_systematic_risk_last_90_days_120_12_industry` | `risk_model_standalone` | Unrun quality/risk overlay with no explicit historical-kill flag. Hold as a later diagnostic, especially if quality/revision families need risk overlay testing. |

## Deprioritized Candidates

These unrun candidates should not consume near-term simulation budget. Most are
neutralization-only siblings of failed or held candidates, exact-neighbor
structures that later became negative examples, high-turnover option/news
variants, or older formulations superseded by v3.

| Source | Candidate | Family | Deprioritization reason |
| --- | --- | --- | --- |
| V1 | `balance_sheet_accel_assets_cashflow_efficiency_rank_derivative_growth_potential_rank_derivative_126_industry` | `accruals_asset_growth_balance_sheet` | Industry-neutralized sibling of the V1 balance-sheet hold candidate; use only one neutralization if this old shape is ever revisited. |
| V1 | `earnings_revision_anl4_qfv4_eps_mean_anl4_qfv4_dts_spe_126_120_20_industry` | `forecast_dispersion` | Neutralization sibling of the simulated V1 forecast candidate, which had negative Fitness. Deprioritize exact family/shape. |
| V1 | `valuation_quality_relative_valuation_rank_derivative_cashflow_efficiency_rank_derivative_126_126_20_industry` | `valuation_quality_acceleration` | Neutralization sibling of the simulated V1 valuation-quality candidate, which failed badly with negative Fitness, high drawdown, low turnover, and low sub-universe Sharpe. |
| V1 | `insider_proxy_rp_ess_insider_cashflow_efficiency_rank_derivative_126_63_20` | `ownership_or_insider_proxy` | Same insider/cashflow/share-count template as the simulated V1 insider candidate, but with a faster cashflow-efficiency delta. The simulated slower version was weak and below the desired turnover band. |
| V1 | `option_positioning_pcr_oi_360_historical_volatility_60_120_10_industry` | `option_positioning_or_volatility` | High expected turnover and close to the later failed v2 `pcr_oi_360 + historical_volatility_60` option structure. |
| V1 | `option_positioning_pcr_oi_360_historical_volatility_60_120_10_subindustry` | `option_positioning_or_volatility` | Subindustry sibling of the high-turnover option structure; also near the later failed v2 option pair. |
| V1 | `ravenpack_slow_rp_ess_credit_rp_css_business_126_10_industry` | `ravenpack_news_slow_aggregate` | High expected turnover and sparse news coverage risk; older Ravenpack formulation is less attractive than v3 cross-confirmed news candidates. |
| V1 | `ravenpack_slow_rp_ess_credit_rp_css_business_126_10_subindustry` | `ravenpack_news_slow_aggregate` | Subindustry sibling of the high-turnover Ravenpack structure; coverage and concentration risks remain. |
| V1 | `risk_quality_systematic_risk_last_90_days_correlation_last_90_days_spy_analyst_revision_rank_derivative_120_20_subindustry` | `risk_model_standalone` | Neutralization sibling of the V1 risk-overlay hold candidate; do not spend an extra slot on subindustry twin first. |
| V2 | `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_industry` | `accruals_asset_growth_balance_sheet` | Neutralization sibling of the simulated V2 accruals candidate. The subindustry version failed with negative Sharpe/Fitness, so this shape is deprioritized. |
| V2 | `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_subindustry` | `earnings_estimate_revision` | Neutralization sibling of the simulated V2 sales-revision candidate. Same failed low-estimate structure. |
| V2 | `sales_revision_norm_sales_estimate_average_annual_sales_estimate_dispersion_analyst_revision_rank_derivative_126_12_subindustry` | `forecast_dispersion` | Subindustry sibling of the V2 dispersion hold candidate. Keep only the industry version as the broader coverage diagnostic. |
| V2 | `liquidity_quality_non_corr_earnings_certainty_rank_derivative_126_126_12_subindustry` | `valuation_quality_acceleration` | Neutralization sibling of the liquidity-quality hold candidate. Subindustry may over-fragment a liquidity overlay. |
| V2 | `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_subindustry` | `option_positioning_or_volatility` | Neutralization sibling of the simulated V2 option candidate, which failed Sharpe/Fitness, concentration, and sub-universe checks. |
| V2 | `event_news_confirm_rp_ess_credit_rp_css_business_126_12_subindustry` | `ravenpack_news_slow_aggregate` | Subindustry sibling of the V2 news hold candidate; sparse news coverage argues for broader industry if revisited. |
| V2 | `quality_risk_overlay_earnings_certainty_rank_derivative_systematic_risk_last_90_days_120_12_subindustry` | `risk_model_standalone` | Subindustry sibling of the V2 quality-risk hold candidate; keep industry version as the diagnostic if needed. |

## Family-Level Retrospective

- `accruals_asset_growth_balance_sheet`: keep only legacy forms that are
  structurally distinct from the failed v2 cashflow-efficiency/assets/cashflow-op
  trio. Prefer v3's inventory and issuance formulations for future work.
- `forecast_dispersion` and `earnings_estimate_revision`: deprioritize exact
  V1 EPS/DTS and V2 low-estimate failed siblings. Hold only the V2 dispersion
  version as a backup behind the v3 highest-sales-estimate structure.
- `valuation_quality_acceleration`: deprioritize V1 valuation-quality siblings
  after the simulated subindustry version failed badly. Hold only the V2
  liquidity-quality diagnostic because it is explicitly not an E5 correlation
  structure.
- `option_positioning_or_volatility`: deprioritize all v1/v2 unrun option
  siblings tied to `pcr_oi_360 + historical_volatility_60`; v3's `pcr_oi_720`
  plus implied-volatility skew structure is the better option representative.
- `ownership_or_insider_proxy`: deprioritize the faster V1 insider sibling
  because the slower simulated version was weak and below the desired turnover
  band. Prefer v3's alternate insider fields if this family is reopened.
- `ravenpack_news_slow_aggregate`: hold one industry-level cross-confirmed V2
  candidate, but do not prioritize older high-turnover V1 Ravenpack twins.
- `risk_model_standalone`: hold one industry-level risk overlay from each
  generation as diagnostic inventory; do not run neutralization twins first.

## Recommended Planning State

- Hold candidates: 6
- Deprioritized candidates: 16
- Runnable batch created: no
- Future simulation approval implied: no

The immediate future tracking candidate remains the selected v3 candidate:
`alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_126_24_industry`.

Do not run v1/v2 hold candidates unless a future task explicitly reopens them
and compares them against the cleaner v3 alternatives.

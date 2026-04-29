# Offline Shortlist V3 Review

- Date: 2026-04-29
- Scope: review only
- Input shortlist: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_shortlist_v3_DO_NOT_RUN.json`
- WQ simulations run in this task: none
- Simulation endpoint called in this task: no
- Runnable batch created in this task: no
- Credential contents read in this task: no
- Recommended max-3 status: still `DO_NOT_RUN`

This memo reviews the 16 v3 shortlisted offline candidates and separates them
into `run_now_candidates`, `runner_up_hold_candidates`, and
`deprioritized_candidates`. The label `run_now_candidates` means candidates that
could be copied exactly into a future runnable batch only if the user later
explicitly approves simulation. It does not authorize a run in this task.

The miner shortlist JSON currently uses one shared `recommended_next_action`
value: `human_review_only; do not run until selected into a future <=3 alpha
manual batch`. It does not distinguish `hold_for_later` from `deprioritize`, so
that taxonomy is kept in this memo only.

## User Selection Update

After this review, the user chose option 1: record only the first reviewed
candidate as the future simulation tracking candidate. This is still
`DO_NOT_RUN`, no runnable batch has been created, and no simulation approval has
been granted.

Selected single future candidate:

- `alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_126_24_industry`
- Family: `accruals_asset_growth_balance_sheet`
- Window / neutralization: 126d, industry-neutralized
- Expression:
  `group_neutralize(ts_decay_linear(group_zscore(rank(ts_delta(earnings_certainty_rank_derivative, 126)), sector) + group_zscore(rank(ts_delta(inventory_turnover, 126)), sector) - group_zscore(rank(ts_delta(fn_proceeds_from_issuance_of_common_stock_q, 252)), sector), 24), industry)`

The other two original `run_now_candidates` are retained as review-ranked
alternates only; they should not be run unless the user explicitly reopens the
selection.

## Review Frame

- Input candidates reviewed: 16
- Historical lessons applied in source shortlist: true
- All reviewed candidates have `expected_turnover_bucket: low_medium`.
- No reviewed candidate has `low_turnover_inertia_risk`.
- No reviewed candidate has a `historical_kill_*` risk flag.
- No reviewed candidate is an E5 close-volume correlation reversal neighbor.
- No reviewed candidate is marked as a reviewed top3 or v2 top3 failed
  near-neighbor.
- Sibling windows were not selected together.

## run_now_candidates

These are the maximum three future simulation candidates. They are still
`DO_NOT_RUN` until explicit future approval.

### 1. `alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_126_24_industry`

- Family: `accruals_asset_growth_balance_sheet`
- Expression:
  `group_neutralize(ts_decay_linear(group_zscore(rank(ts_delta(earnings_certainty_rank_derivative, 126)), sector) + group_zscore(rank(ts_delta(inventory_turnover, 126)), sector) - group_zscore(rank(ts_delta(fn_proceeds_from_issuance_of_common_stock_q, 252)), sector), 24), industry)`
- Fields:
  `earnings_certainty_rank_derivative`, `growth_potential_rank_derivative`,
  `inventory_turnover`, `assets`, `fn_proceeds_from_issuance_of_debt_q`,
  `fn_repayments_of_debt_q`, `fn_proceeds_from_issuance_of_common_stock_q`,
  `fn_entity_common_stock_shares_out_q`
- Selected window / neutralization rationale: selected 126d with industry
  neutralization because it should be more responsive than the 189d sibling
  while still avoiding short-delta turnover. Industry neutralization is a
  reasonable first read for balance-sheet and financing behavior without
  over-fragmenting into a narrower group.
- Heuristic score: 98
- Expected turnover bucket: `low_medium`
- Economic intuition: improving earnings certainty and inventory efficiency,
  penalized by equity issuance pressure, should identify firms with better
  operating quality and less dilution risk.
- Why selected: cleanest alternative accruals/balance-sheet candidate; no risk
  flags; materially avoids the failed v2
  `cashflow_efficiency_rank_derivative + assets + cashflow_op` structure.
- Main risks: quarterly or slow-moving fields may still be too inert; inventory
  and issuance fields can be sector-specific; actual turnover may be below the
  desired 0.08 to 0.30 range despite the `low_medium` bucket.
- Relation to E5: distinct, no close-volume correlation reversal pattern.
- Relation to failed lanes: passes hard-negative filters for known failed lanes.
- Relation to historical lessons: no confirmed historical-kill penalty.
- Why not its sibling template: the 189d sibling is a same-template window
  variant. The 126d version is preferred as the first sign test because it is
  less stale and should be closer to the desired turnover band.

### 2. `earnings_revision_restruct_highest_sales_estimate_sales_estimate_dispersion_analyst_revision_rank_derivative_126_24_industry`

- Family: `forecast_dispersion`
- Expression:
  `group_neutralize(ts_decay_linear(group_zscore(rank(ts_delta(highest_sales_estimate, 126)), sector) - group_zscore(rank(ts_rank(sales_estimate_dispersion, 120)), sector) + group_zscore(rank(ts_delta(analyst_revision_rank_derivative, 126)), sector), 24), industry)`
- Fields:
  `sales_estimate_average_annual`, `sales_estimate_dispersion`,
  `highest_sales_estimate`, `analyst_revision_rank_derivative`,
  `growth_potential_rank_derivative`, `earnings_certainty_rank_derivative`
- Selected window / neutralization rationale: selected 126d because it gives a
  cleaner first read than the slower 189d sibling. Industry neutralization is
  kept to compare revisions and dispersion inside a broad but economically
  relevant peer group.
- Heuristic score: 98
- Expected turnover bucket: `low_medium`
- Economic intuition: rising high-end sales expectations plus improving
  analyst-revision derivative, minus high sales-estimate dispersion, targets
  cleaner positive estimate revisions rather than raw disagreement.
- Why selected: best analyst/forecast representative; structurally different
  from the failed v2 `sales_estimate_average_annual + lowest_sales_estimate +
  analyst_revision_rank_derivative` form and from raw inverse DTS-SPE lanes.
- Main risks: analyst fields can be crowded and coverage-sensitive; dispersion
  pressure could penalize high-growth stocks with legitimate uncertainty.
- Relation to E5: distinct, no close-volume correlation reversal pattern.
- Relation to failed lanes: passes hard-negative filters for known failed lanes.
- Relation to historical lessons: no confirmed historical-kill penalty.
- Why not its sibling template: the 189d sibling is the same signal with a
  slower change window. The 126d version is the more useful first diagnostic for
  sign and turnover.

### 3. `option_iv_restruct_pcr_oi_720_implied_volatility_mean_skew_180_analyst_revision_rank_derivative_120_24_industry`

- Family: `option_positioning_or_volatility`
- Expression:
  `group_neutralize(ts_decay_linear(group_zscore(rank(ts_rank(pcr_oi_720, 120)), sector) - group_zscore(rank(ts_rank(implied_volatility_mean_skew_180, 120)), sector) + group_zscore(rank(ts_delta(analyst_revision_rank_derivative, 126)), sector), 24), industry)`
- Fields:
  `pcr_oi_720`, `pcr_oi_all`, `pcr_vol_all`,
  `implied_volatility_mean_skew_90`, `implied_volatility_mean_skew_180`,
  `parkinson_volatility_60`, `analyst_revision_rank_derivative`,
  `growth_potential_rank_derivative`
- Selected window / neutralization rationale: selected the 120d option-rank
  window rather than 180d to keep the first option test more responsive. Industry
  neutralization is retained to compare option positioning and skew within a
  broad peer group.
- Heuristic score: 95
- Expected turnover bucket: `low_medium`
- Economic intuition: slow put/call open-interest positioning adjusted by IV
  skew and confirmed by analyst-revision acceleration may identify option-market
  caution that is inconsistent with improving fundamentals.
- Why selected: gives the max-3 set an independent option/implied-volatility
  source that is not the failed `pcr_oi_360 + historical_volatility_60` pair and
  not a raw breakeven/PCR single-source seed.
- Main risks: `options_coverage_risk`; possible concentration and sub-universe
  weakness based on prior option-family history; should be the first one cut if
  future simulation budget allows fewer than three.
- Relation to E5: distinct, no close-volume correlation reversal pattern.
- Relation to failed lanes: passes hard-negative filters for known failed lanes.
- Relation to historical lessons: no confirmed historical-kill penalty; it uses
  a hold/incubate-style option lane, not a confirmed historical-kill raw seed.
- Why not its sibling template: the 180d sibling is a same-template window
  variant. The 120d version is preferred for the first test because 180d may be
  too slow for option positioning.

## runner_up_hold_candidates

These are not failures. They remain useful hold candidates if the selected
families fail or if a later batch wants a different source mix.

| Candidate | Family | Hold reason |
| --- | --- | --- |
| `profit_accel_distinct_fscore_bfl_profitability_growth_potential_rank_derivative_inventory_turnover_126_24_industry` | `profitability_acceleration` | Clean and economically intuitive, but overlaps with the selected accruals candidate through quality/growth and inventory. Prefer as the first backup if the accruals line is not selected later. |
| `ravenpack_cross_confirm_rp_ess_credit_rp_css_business_earnings_certainty_rank_derivative_126_24_industry` | `ravenpack_news_slow_aggregate` | Cross-confirmed news plus quality confirmation is structurally different, but `news_sparse_coverage_risk` makes it less attractive than the option candidate for the initial max-3. |
| `ownership_insider_distinct_rp_css_insider_analyst_revision_rank_derivative_fn_entity_common_stock_shares_out_q_126_24_industry` | `ownership_or_insider_proxy` | Distinct from failed `rp_ess_insider + cashflow_efficiency` form, but still news/insider sparse and partly overlaps with the selected forecast candidate through analyst revision. |
| `quality_revision_risk_overlay_earnings_certainty_rank_derivative_systematic_risk_last_90_days_126_24_industry` | `risk_model_standalone` | Good risk-overlay backup with no explicit risk flags, but uses an extra fourth component and shares revision/quality exposure with selected candidates. |
| `liquidity_quality_non_corr_v3_earnings_certainty_rank_derivative_126_126_24_industry` | `valuation_quality_acceleration` | Explicitly not an E5 correlation pattern, but it still uses volume/adv20 as an overlay and is less independent than options or news. Hold rather than run first. |

## deprioritized_candidates

These are not all rejected as failed ideas. They are deprioritized for this
review because they are same-template siblings, lower-priority source mixes, or
less useful as a first max-3 test.

| Candidate | Reason |
| --- | --- |
| `alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_189_24_industry` | Same template as the selected accruals candidate; 189d is slower and more likely to be inert. |
| `earnings_revision_restruct_highest_sales_estimate_sales_estimate_dispersion_analyst_revision_rank_derivative_189_24_industry` | Same template as the selected forecast candidate; 126d is preferred for the first sign and turnover read. |
| `profit_accel_distinct_fscore_bfl_profitability_growth_potential_rank_derivative_inventory_turnover_189_24_industry` | Same profitability template as the 126d runner-up; slower window is less useful as the first diagnostic. |
| `liquidity_quality_non_corr_v3_earnings_certainty_rank_derivative_126_189_24_industry` | Same liquidity-quality template as the 126d hold candidate; slower quality/growth leg. |
| `option_iv_restruct_pcr_oi_720_implied_volatility_mean_skew_180_analyst_revision_rank_derivative_180_24_industry` | Same option template as the selected 120d candidate; 180d option rank may be too stale. |
| `ownership_insider_distinct_rp_css_insider_analyst_revision_rank_derivative_fn_entity_common_stock_shares_out_q_84_24_industry` | Same ownership template as the 126d hold candidate; 84d event mean may increase noise and coverage fragility. |
| `ravenpack_cross_confirm_rp_ess_credit_rp_css_business_earnings_certainty_rank_derivative_84_24_industry` | Same Ravenpack template as the 126d hold candidate; 84d news smoothing is less stable. |
| `profit_accel_distinct_fscore_bfl_profitability_growth_potential_rank_derivative_systematic_risk_last_90_days_126_24_industry` | Classified as risk-model/risk-overlay rather than pure profitability; less independent than the selected option candidate and less direct than the quality-revision risk overlay backup. |

## Family Notes

- `accruals_asset_growth_balance_sheet`: highest-priority clean fundamental
  family; select only the 126d version.
- `forecast_dispersion`: best analyst-family representative; select only the
  126d version and do not pair with its 189d sibling.
- `profitability_acceleration`: strong hold, but too close to the selected
  accruals/quality source to spend one of only three first-run slots.
- `valuation_quality_acceleration`: hold because the liquidity overlay is
  explicitly non-correlation but still introduces volume/adv20 crowding risk.
- `option_positioning_or_volatility`: selected one 120d representative for
  source independence despite coverage risk.
- `ownership_or_insider_proxy`: hold, not rejected; sparse news/insider coverage
  and analyst-revision overlap make it a second wave candidate.
- `ravenpack_news_slow_aggregate`: hold, not rejected; sparse news coverage and
  historical news fragility argue against first max-3 priority.
- `risk_model_standalone / risk-overlay`: hold one quality-revision risk overlay;
  deprioritize the profit-risk overlay because it is less distinct.

## Future Simulation Instruction

Do not run anything from this memo now. After the user's option-1 selection, a
future explicitly approved simulation should run at most exactly the selected
single candidate above, with no variants, no sibling windows, and no runnable
batch generated from the full v3 shortlist. The two remaining original
`run_now_candidates` are alternates, not approved run items.

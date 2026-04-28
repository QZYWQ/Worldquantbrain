# Offline Shortlist V2 Review

- Date: 2026-04-29
- Scope: review only
- Input artifact: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_shortlist_v2_DO_NOT_RUN.json`
- WQ simulations run in this task: none
- Simulation endpoint called in this task: no
- Runnable manual batch created in this task: no
- Recommended candidates below are still `DO_NOT_RUN`

## Summary

The v2 shortlist contains 14 candidates across 7 families, with each family
represented by an industry and subindustry neutralization twin. This review
selects at most one twin per expression shape and recommends three future
simulation candidates from independent families:

1. balance-sheet/accruals normalization
2. earnings estimate revision
3. option positioning / volatility

No candidate was run. This memo is only a manual selection note for a possible
future capped simulation batch.

## Recommended Max-3 Future Simulation Candidates

### 1. `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_subindustry`

- Family: `accruals_asset_growth_balance_sheet`
- Neutralization: `subindustry`
- Heuristic score: 98
- Expected turnover bucket: `medium_high`
- Fields: `cashflow_efficiency_rank_derivative`, `assets`, `cashflow_op`
- Verified field set from artifact: `assets`, `revenue`, `cashflow_op`,
  `fn_entity_common_stock_shares_out_q`,
  `fn_proceeds_from_issuance_of_common_stock_q`,
  `cashflow_efficiency_rank_derivative`,
  `earnings_certainty_rank_derivative`
- Expression:

```text
group_neutralize(ts_decay_linear(group_zscore(rank(ts_delta(cashflow_efficiency_rank_derivative, 126)), sector) - group_zscore(rank(ts_delta(assets, 252)), sector) + group_zscore(rank(ts_delta(cashflow_op, 126)), sector), 12), subindustry)
```

- Neutralization choice rationale: subindustry is preferred for this accounting
  and balance-sheet signal because accruals, asset growth, and operating cash
  flow are strongly industry-structure dependent. The expression already uses
  sector-level component normalization; final subindustry neutralization should
  further reduce structural accounting bias before the first test.
- Why selected: best combination of score, economic intuition, and distance
  from closed lanes. The thesis is that improving cash-flow efficiency and
  operating cash flow, penalized by asset expansion, may capture cleaner
  quality acceleration than the failed simple cashflow/assets plus
  revenue/assets stability seed.
- Main risks: medium-high expected turnover may need later smoothing if the
  first result is noisy; accounting fields can have reporting lag and coverage
  asymmetry.
- Relation to E5: distinct. It has no close-volume correlation reversal and no
  `ts_corr(rank(close), rank(volume), 60/70/80/90)` pattern.
- Relation to failed lanes: passes hard-negative filters. It is not the failed
  simple cashflow/assets plus revenue/assets stability lane because it uses
  derivative quality, asset-growth penalty, operating cash-flow confirmation,
  sector z-scores, and medium-horizon deltas.
- Why not its industry twin: the industry version is viable, but using both
  would waste a capped batch slot on a neutralization-only variant. For this
  family, subindustry is the more conservative first test against accounting
  comparability and concentration risk.

### 2. `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_industry`

- Family: `earnings_estimate_revision`
- Neutralization: `industry`
- Heuristic score: 98
- Expected turnover bucket: `medium_high`
- Fields: `sales_estimate_average_annual`, `lowest_sales_estimate`,
  `analyst_revision_rank_derivative`
- Verified field set from artifact: `sales_estimate_average_annual`,
  `sales_estimate_dispersion`, `highest_sales_estimate`,
  `lowest_sales_estimate`, `analyst_revision_rank_derivative`,
  `growth_potential_rank_derivative`
- Expression:

```text
group_neutralize(ts_decay_linear(group_zscore(rank(ts_delta(sales_estimate_average_annual, 126)), sector) - group_zscore(rank(ts_rank(lowest_sales_estimate, 120)), sector) + rank(ts_mean(analyst_revision_rank_derivative, 126)), 12), industry)
```

- Neutralization choice rationale: industry is preferred over subindustry for
  the first estimate-revision test because analyst coverage can be sparse and
  subindustry neutralization may over-fragment the signal. Sector component
  z-scores already provide a broad relative normalization layer.
- Why selected: this is the cleanest analyst-estimate candidate while avoiding
  the reviewed top-3 failed EPS mean plus DTS dispersion form. The thesis is
  that improving annual sales expectations, confirmed by analyst revision
  derivatives, can identify demand momentum while penalizing weak low-end sales
  expectations.
- Main risks: analyst estimate signals can be crowded and coverage-dependent;
  medium-high turnover may need a slower decay if the first result shows
  turnover or drawdown stress.
- Relation to E5: distinct. It has no close/volume correlation structure.
- Relation to failed lanes: passes hard-negative filters. It is structurally
  distinct from the failed `anl4_qfv4_eps_mean + anl4_qfv4_dts_spe` candidate:
  it uses sales estimate fields, a low-estimate penalty, and
  `analyst_revision_rank_derivative` confirmation rather than the failed EPS
  mean and DTS dispersion pair.
- Why not its subindustry twin: the subindustry twin is useful as a later
  neutralization check, but the first test should preserve more cross-sectional
  breadth in a coverage-sensitive estimate family.

### 3. `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_industry`

- Family: `option_positioning_or_volatility`
- Neutralization: `industry`
- Heuristic score: 89
- Expected turnover bucket: `low_medium`
- Fields: `pcr_oi_360`, `historical_volatility_60`
- Verified field set from artifact: `pcr_oi_360`, `pcr_oi_720`,
  `pcr_oi_all`, `pcr_vol_all`, `implied_volatility_mean_skew_90`,
  `implied_volatility_mean_skew_180`, `historical_volatility_60`,
  `parkinson_volatility_60`
- Expression:

```text
group_neutralize(ts_decay_linear(group_zscore(rank(ts_rank(pcr_oi_360, 120)), sector) - group_zscore(rank(ts_rank(historical_volatility_60, 120)), sector), 12), industry)
```

- Neutralization choice rationale: industry is preferred because option-field
  coverage may be thinner than fundamental coverage. Industry neutralization
  keeps a broader peer set while still avoiding broad sector tilts through
  sector component z-scores.
- Why selected: it is the most independent family in the shortlist and has a
  lower expected turnover bucket than the top fundamental entries. The thesis
  is that persistent option positioning relative to realized volatility may
  capture sentiment or hedging pressure not present in price-volume or
  accounting lanes.
- Main risks: `options_coverage_risk`; coverage may be sparse or biased toward
  large-cap/liquid names. It also has a lower heuristic score than the top
  fundamental entries.
- Relation to E5: distinct. It does not use close-volume correlation reversal
  or the corr60/70/80/90 structure.
- Relation to failed lanes: passes hard-negative filters. It is not the sixth
  batch failed option forward-curve seed because it does not use
  `(forward_price_120 - forward_price_60) / close` or forward-price slope.
  It uses put-call open-interest positioning and realized volatility.
- Why not its subindustry twin: subindustry neutralization may be too tight for
  options coverage. The industry version is a better first test for a sparse
  options family.

## Reviewed But Not Prioritized

| Candidate family / shape | Decision | Reason |
| --- | --- | --- |
| `balance_accrual_norm_..._industry` | Not selected | Neutralization twin of the selected subindustry accruals candidate. Keep as a later diagnostic if the selected version has concentration or sub-universe issues. |
| `sales_revision_norm_..._subindustry` | Not selected | Neutralization twin of the selected industry estimate-revision candidate. Subindustry may over-fragment analyst coverage. |
| `forecast_dispersion` sales-estimate dispersion twins | Not selected | Good score, but overlaps heavily with the selected sales revision family and remains closer to the failed forecast-dispersion lane than the low-estimate revision version. |
| `valuation_quality_acceleration` liquidity-quality twins | Not selected | Structurally different from the failed top-3 valuation-quality pair, but still shares the broad valuation/quality acceleration family and introduces volume/adv20 liquidity exposure. Lower priority than cleaner balance-sheet and estimate-revision candidates. |
| `option_skew_norm_..._subindustry` | Not selected | Neutralization twin of the selected industry option candidate. Coverage risk argues against the tighter neutralization first. |
| `ravenpack_news_slow_aggregate` twins | Not selected | Independent data family, but `news_sparse_coverage_risk` is explicit and the use of Ravenpack credit/business fields is closer to the sixth-batch news failure than the selected option candidate is to the failed option forward curve. It is not the exact failed `rp_nip_credit_ratings + rp_ess_dividends` aggregate, but it should wait for manual coverage review. |
| `risk_model_standalone` quality-risk overlay twins | Not selected | Not the exact sixth-batch `unsystematic_risk_last_90_days + beta_last_90_days_spy` form, but it still depends on model risk exposure. Because the sixth-batch model51 risk lane failed badly, this should not take one of the first three v2 slots. |

## Family-Level Review

- `accruals_asset_growth_balance_sheet`: strongest v2 family. It is
  economically interpretable and furthest from the recent top-3 failures.
- `earnings_estimate_revision`: worth one slot, but use the sales revision and
  low-estimate formulation rather than the dispersion formulation.
- `forecast_dispersion`: defer. It is improved versus the failed EPS+DTS form,
  but still too close in family and less independent than the selected three.
- `valuation_quality_acceleration`: defer. The proposed liquidity-quality
  version is structurally different, but the top-3 valuation-quality failure
  argues for caution.
- `option_positioning_or_volatility`: worth one exploratory slot because it is
  not a forward-curve slope variant and is relatively independent.
- `ravenpack_news_slow_aggregate`: defer due to sparse news coverage risk and
  proximity to the broader failed Ravenpack lane.
- `risk_model_standalone`: defer due to proximity to the failed model-risk lane,
  even though the exact fields differ.

## Final Recommendation

Do not run yet unless the user explicitly approves a future simulation task.

If approved later, run at most exactly these three candidates and no variants:

1. `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_subindustry`
2. `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_industry`
3. `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_industry`

Do not include the neutralization twins in the same capped batch.

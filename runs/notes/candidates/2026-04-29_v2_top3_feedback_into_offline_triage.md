# V2 Top-3 Feedback Into Offline Triage

- Date: 2026-04-29
- Scope: feedback update after the v2 reviewed shortlist top-3 simulations
- Miner historical lessons input commit: `f79fd71`
- Source result note: `runs/notes/candidates/2026-04-29_v2_reviewed_top3_results.md`
- Miner v3 design artifact: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_generation_v3_design_DO_NOT_RUN.json`

## No Simulation Statement

No WQ simulation was run in this task. No simulation endpoint was called, no
runnable manual batch was created, and no credential contents were read.

## Summary

The offline-reviewed v2 top-3 simulation lane produced no hopeful and no
internal candidate. All three candidates failed `LOW_SHARPE` and
`LOW_FITNESS`; the option-positioning candidate also failed
`CONCENTRATED_WEIGHT` and `LOW_SUB_UNIVERSE_SHARPE`.

Decision: stop the v2 reviewed shortlist lane. Feed the exact failed
structures into offline triage as negative examples, then return to broad
offline generation.

## V2 Top-3 Results

| Name | Alpha id | Family | Sharpe | Fitness | Turnover | Drawdown | Decision |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_subindustry` | `JjgEOmgm` | `accruals_asset_growth_balance_sheet` | -0.27 | -0.08 | 0.0689 | 0.1083 | not hopeful |
| `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_industry` | `O0bPZ9L7` | `earnings_estimate_revision` | -0.17 | -0.04 | 0.0553 | 0.1214 | not hopeful |
| `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_industry` | `RR2Q8Ye1` | `option_positioning_or_volatility` | -0.43 | -0.17 | 0.1087 | 0.1206 | not hopeful |

## Triage Feedback Added

The miner offline triage tool now penalizes these v2 failed near-neighbor
structures without banning their whole families:

- Simple `cashflow_efficiency_rank_derivative` + `assets` + `cashflow_op`
  medium-horizon normalized rank/decay forms.
- Simple `sales_estimate_average_annual` + `lowest_sales_estimate` +
  `analyst_revision_rank_derivative` normalized rank/decay forms.
- Simple `pcr_oi_360` + `historical_volatility_60` normalized option skew/vol
  forms.
- Option-positioning candidates with the failed v2 similarity now receive
  explicit concentration and sub-universe risk flags.
- Slow fundamental or analyst candidates around the low-turnover region are
  flagged with `low_turnover_inertia_risk`.

## Historical Lessons Integration

Miner commit `f79fd71` imported Worldquantbrain historical lessons as
DO_NOT_RUN triage assets. The triage tool now references the JSON lessons file
as a non-runnable negative-knowledge source. Confirmed killed or frozen lanes
contribute risk flags and score penalties, while hold/incubate lanes are not
hard-rejected by default.

This preserves the dual-repo architecture: Worldquantbrain remains the
research archive, and miner consumes the distilled lessons as one-way planning
input.

## Tool And Test Changes

- Updated miner tool:
  `/Users/zpdedn/Documents/github/worldquant-miner/tools/build_offline_candidate_shortlist.py`
- Updated miner tests:
  `/Users/zpdedn/Documents/github/worldquant-miner/tests/test_offline_candidate_triage.py`
- Added miner planning artifact:
  `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_generation_v3_design_DO_NOT_RUN.json`

New tests cover v2 failed near-expression penalties, explicit option
concentration/sub-universe risk flags, low-turnover inertia flags, historical
lessons JSON DO_NOT_RUN parsing, confirmed historical kill penalties,
hold/incubate non-hard-rejection, and DO_NOT_RUN output behavior.

## V3 Direction

Next offline generation should prioritize:

- Verified but underexplored field families not already used in failed lanes.
- Accruals and balance-sheet alternatives that do not reuse the failed
  `cashflow_efficiency_rank_derivative` + `assets` + `cashflow_op` simple pair.
- Earnings-revision structures that do not reuse the failed
  `sales_estimate_average_annual` + `lowest_sales_estimate` +
  `analyst_revision_rank_derivative` form.
- Option/implied-volatility structures that do not reuse the failed
  `pcr_oi_360` + `historical_volatility_60` simple pairing and avoid historical
  raw breakeven/PCR seeds.
- News/Ravenpack structures that are not the failed credit/dividend aggregate,
  raw buzz stability, or simple insider proxy pair.
- Profitability acceleration with different fields, sector-relative
  normalization, and expected turnover closer to 0.08-0.30.

Do not simulate v3 candidates until a future explicit approval selects at most
three exact expressions from a reviewed shortlist.

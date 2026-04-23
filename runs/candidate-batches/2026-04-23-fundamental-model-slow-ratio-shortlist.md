# Fundamental / Model Slow Ratio Shortlist

- Date: `2026-04-23`
- Status: `branch`
- Source: local miner + scorecard + queue builder
- Note: local heuristics only; no official simulation metrics are claimed here.

## Decision

Keep the family live and keep the first batch small. The local ridge is strongest around `mdl110_value / market_cap`, with `mdl110_score / market_cap` as the backup ridge. The forum-backed `net_income / market_cap` anchor stays as the interpretability control.

## Top 5 Local Candidates

| name | local_score | action | expression | note |
| --- | ---: | --- | --- | --- |
| mdl110_value_subindustry_63 | 62.84 | simulate | `ts_rank(group_rank(mdl110_value / market_cap, subindustry), 63)` | strongest local ridge |
| mdl110_score_industry_90 | 62.02 | simulate | `ts_rank(group_rank(mdl110_score / market_cap, industry), 90)` | best model-score backup |
| mdl110_score_industry_78_504 | 60.65 | hold | `ts_rank(group_rank(ts_mean(mdl110_score / market_cap, 78), industry), 504)` | slower backup control |
| mdl110_value_subindustry_504_252 | 60.60 | hold | `ts_rank(group_rank(ts_mean(mdl110_value / market_cap, 504), subindustry), 252)` | slowest local smoother |
| mdl110_value_industry_78_81 | 60.12 | hold | `ts_rank(group_rank(ts_mean(mdl110_value / market_cap, 78), industry), 81)` | alternate smoother / window mix |

## Forum Anchor Control

- `net_income_anchor_subindustry_90`
  - expression: `ts_rank(group_rank(net_income / market_cap, subindustry), 90)`
  - local score: `58.24`
  - role: keep as the forum-backed control, not the current best ridge

## Recommended First Batch Shape

1. `ts_rank(group_rank(mdl110_value / market_cap, subindustry), 63)`
2. `ts_rank(group_rank(mdl110_value / market_cap, subindustry), 84)`
3. `ts_rank(group_rank(mdl110_value / market_cap, subindustry), 90)`
4. `ts_rank(group_rank(mdl110_value / market_cap, industry), 63)`
5. `ts_rank(group_rank(mdl110_score / market_cap, industry), 90)`

## Branch Posture

- `fundamental / model slow ratio`: branch
- `price-volume short horizon`: kill
- No candidate-batch JSON is written here because there is still no official simulation evidence in this thread.

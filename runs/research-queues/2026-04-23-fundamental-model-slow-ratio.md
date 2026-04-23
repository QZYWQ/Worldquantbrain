# Fundamental / Model Slow Ratio Queue

- Date: `2026-04-23`
- Status: `branch`

## Current Decision

The next live lane should stay in the `fundamental / model slow ratio` family. The local miner and scorecard currently prefer the `mdl110_value / market_cap` ridge, with `mdl110_score / market_cap` as the next strongest backup and the forum-backed `net_income / market_cap` anchor still in range.

## Family Order

1. `fundamental / model slow ratio` - branch
2. `price-volume short horizon` - not selected for the next branch

## First Batch Shape

- Baseline:
  `ts_rank(group_rank(mdl110_value / market_cap, subindustry), 63)`
- Variant 1:
  `ts_rank(group_rank(mdl110_value / market_cap, subindustry), 84)`
- Variant 2:
  `ts_rank(group_rank(mdl110_value / market_cap, subindustry), 90)`
- Variant 3:
  `ts_rank(group_rank(mdl110_value / market_cap, industry), 63)`
- Variant 4:
  `ts_rank(group_rank(mdl110_score / market_cap, industry), 90)`

## Notes

- The local candidate pool reached `1264` expressions after the numerator replacement pass.
- The family remains interpretable and keeps the slow-ratio structure intact.
- The forum crawl still provides the reusable ratio-frame evidence for this lane.

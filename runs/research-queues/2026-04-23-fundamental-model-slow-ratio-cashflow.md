# Fundamental / Model Slow Ratio Cashflow Queue

- Date: `2026-04-23`
- Status: `branch only / assets killed`

## Current Decision

`cashflow / cap` stays live for a tight window sweep. The 63d probe is now recorded and weaker than the 90d anchor. `cashflow / assets` is killed after the negative 90d probe and the visible `Single Data Set Alpha` label.

## Family Order

1. `cashflow / cap` - branch
2. `cashflow / assets` - killed

## First Batch Shape

- Anchor evidence: `ts_rank(group_rank(cashflow / cap, subindustry), 90)`
- Baseline: `ts_rank(group_rank(cashflow / cap, subindustry), 63)`
- Variant 1: `ts_rank(group_rank(cashflow / cap, subindustry), 84)`
- Variant 2: `ts_rank(group_rank(cashflow / cap, subindustry), 126)`

## Notes

- Keep the group axis fixed at `subindustry`.
- Keep the numerator fixed at `cashflow / cap`.
- The 63d window is already weaker than the 90d anchor.
- Do not reopen `cashflow / assets` unless a separate evidence path appears.

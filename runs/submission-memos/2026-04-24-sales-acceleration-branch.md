# 2026-04-24 Sales Acceleration Branch Decision

## Decision

- Open `sales_acceleration` as the next live family after the capital-structure closure.
- Treat it as the best remaining budgeted experiment because it is the cleanest untested lever change left in the current queue.
- Keep the capital-structure and invested-capital sources closed.

## Why This Is The Best Remaining Move

- `operating_income_history_position` has already been judged a backup and should not get more polish.
- `capital_structure_balance_sheet` is killed.
- `invested_capital_history_position` is frozen after a raw TS-rank unit-warning failure.
- The analyst-EPS, news, and option branches are either blocked or too weak for the next hour.
- `sales_acceleration` is the only remaining hold family that still gives a real structural change rather than another cousin tweak.

## Official Evidence Used

- `runs/research-contracts/2026-04-24-family-registry.json`
- `runs/research-queues/official-alpha-cycle-04.md`
- `runs/field-search-packs/2026-04-21-sales-delta-fundamental.md`
- `runs/submission-memos/2026-04-24-capital-structure-ratio-closure.md`
- `runs/submission-memos/2026-04-24-next-step-family-stop.md`

## Next Minimal Experiment

- Baseline:
  `group_rank(ts_delta(ts_delta(revenue, 63), 63), industry)`
- Immediate control:
  `group_rank(ts_delta(revenue, 63), industry)`
- If both are weak, kill the family quickly and do not broaden it before a real live readout.

## Status

- Current pivot: `sales_acceleration`
- Closed sources: capital structure, invested capital, operating-income ridge
- Next action: launch the first diagnostic batch when live access is available

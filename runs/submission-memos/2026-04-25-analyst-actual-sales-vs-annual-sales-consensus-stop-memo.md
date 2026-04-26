# 2026-04-25 Analyst Actual Sales Vs Annual Sales Consensus Stop Memo

## Decision

- Freeze `analyst_actual_sales_vs_annual_sales_consensus`.
- Do not reopen this lane for more sign, gap, or normalization polish.
- Switch the next budget to a new family source.

## Why

- The live first batch is complete enough to close the lane.
- The baseline is weak on the test period.
- The sign flip confirms the direction but still fails IS Sharpe and Fitness.
- The raw gap and rank-normalized gap controls both stay below continuation floor.

## Next Step

- Move to `growth_potential_rank_derivative` in `Model > Valuation Models`.
- Keep the current annual-sales lane frozen unless a genuinely new information source appears.

## Evidence

- `runs/simulation-captures/2026-04-25-analyst-actual-sales-vs-annual-sales-consensus-batch-01.json`
- `runs/submission-memos/2026-04-25-analyst-actual-sales-vs-annual-sales-consensus-live-first-batch.md`

## Status

- `freeze`
- `rotate`

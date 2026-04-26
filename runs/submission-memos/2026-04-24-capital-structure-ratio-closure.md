# 2026-04-24 Capital Structure Ratio Closure

## Decision

- Close the `capital_structure_ratio` line without launching a new live batch.
- Treat the broader capital-structure / balance-sheet source as mined out for the current budget.
- Move the next research hour to a genuinely different information source instead of another balance-sheet cousin.

## Why This Is Closed

- The nearest live analogs are already dead:
  - `capital_structure_balance_sheet` is explicitly killed in the registry.
  - `invested_capital_history_position` is also frozen after a raw TS-rank unit-warning batch failed both IS and sub-universe quality.
- The queue entry for `capital_structure_ratio` is only a hold candidate, and its own note says to open it only after the higher-priority checks and only once a real field is confirmed.
- That means there is no new validated field/source here that would justify another official batch under the current budget.
- The most plausible next ratio variants would still reuse the same balance-sheet source that already failed:
  - leverage-style ratio
  - equity-cushion ratio
  - liquidity cousin
- Based on the existing official evidence, these are close cousins, not a new family.

## Official Evidence Used

- `runs/research-contracts/2026-04-24-family-registry.json`
- `runs/research-contracts/2026-04-24-family-budget-ledger.md`
- `runs/field-search-packs/2026-04-22-capital-structure-balance-sheet.md`
- `runs/expression-families/2026-04-22-capital-structure-balance-sheet-follow-up.md`
- `runs/learning-loops/official-alpha-cycle-04-project-lessons.md`
- `runs/expression-families/2026-04-24-invested-capital-history-position.md`
- `runs/simulation-captures/2026-04-24-invested-capital-history-position-batch-01.json`

## Closure Takeaway

- The capital-structure source has already been tested enough to justify a stop.
- There is no submit path and no clear new subfamily worth the next batch.
- The next live branch should come from a different information source, not another balance-sheet ratio.

## Status

- Family mining loop: closed.
- Next action: pivot away from capital structure.

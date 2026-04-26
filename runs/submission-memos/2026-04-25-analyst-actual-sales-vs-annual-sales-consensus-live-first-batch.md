# 2026-04-25 Analyst Actual Sales Vs Annual Sales Consensus Live First Batch

- Re-check time: `2026-04-25 11:36:18 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Simulate page plus alpha detail API from the logged-in browser session
- Scope: `analyst_actual_sales_vs_annual_sales_consensus`
- Family: `analyst_actual_sales_vs_annual_sales_consensus`

## Decision

- Freeze `analyst_actual_sales_vs_annual_sales_consensus` for the current budget.
- Do not spend more budget on sign polish, normalization polish, or gap-shape polishing in this lane.
- Rotate the next official budget to a genuinely different family source.

## Official Evidence

- Field search pack:
  - `runs/field-search-packs/2026-04-25-analyst-actual-sales-vs-annual-sales-consensus.md`
- Expression family:
  - `runs/expression-families/2026-04-25-analyst-actual-sales-vs-annual-sales-consensus.md`
- Scout report:
  - `runs/submission-memos/2026-04-25-analyst-actual-sales-vs-annual-sales-consensus-scout-report.md`

## Field Facts

- `actual_sales_value_annual`
  - dataset/category: `analyst4` / `Analyst > Analyst Estimates`
  - `USA / TOP3000 / D1`
  - coverage `0.9943`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `126`
  - visible alphas `151`
- `sales_estimate_average_annual`
  - dataset/category: `analyst4` / `Analyst > Analyst Estimates`
  - `USA / TOP3000 / D1`
  - coverage `1.0`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `43`
  - visible alphas `56`

## Batch Result

- Baseline `6XYLML1O`
  - expression: `group_rank(actual_sales_value_annual / sales_estimate_average_annual - 1, industry)`
  - IS Sharpe `0.53`
  - Fitness `0.37`
  - Turnover `0.0201`
  - Returns `0.0603`
  - Test Sharpe `-0.27`
  - Test Fitness `-0.11`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- Sign flip `ZYWvXYjZ`
  - expression: `group_rank(-(actual_sales_value_annual / sales_estimate_average_annual - 1), industry)`
  - IS Sharpe `-0.53`
  - Fitness `-0.37`
  - Turnover `0.0201`
  - Returns `-0.0603`
  - Test Sharpe `0.27`
  - Test Fitness `0.11`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Raw gap control `YPWolkpv`
  - expression: `group_rank(actual_sales_value_annual - sales_estimate_average_annual, industry)`
  - IS Sharpe `-0.20`
  - Fitness `-0.07`
  - Turnover `0.0174`
  - Returns `-0.0144`
  - Test Sharpe `-0.89`
  - Test Fitness `-0.58`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Rank-normalized gap control `QP5pNElM`
  - expression: `group_rank(rank(actual_sales_value_annual) - rank(sales_estimate_average_annual), industry)`
  - IS Sharpe `0.33`
  - Fitness `0.16`
  - Turnover `0.0267`
  - Returns `0.0281`
  - Test Sharpe `-0.77`
  - Test Fitness `-0.48`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`

## Why This Stops Here

- The baseline is weak and loses on the test period.
- The sign-flip control proves the direction is not the issue, but it still fails IS Sharpe and Fitness.
- The raw gap and rank-normalized gap controls do not rescue the family.
- That means more same-family budget would be cosmetic polishing, not a genuine new family advance.

## Next Minimal Experiment

- Rotate to the next genuinely new source family:
  - `growth_potential_rank_derivative`
  - `model16` / `Model > Valuation Models`
- If that lane stalls, fall back to the other model-family backup rather than reopening this annual-sales lane.

## Status

- Family state: `freeze`
- Portfolio posture: `rotate`
- Batch posture: `complete`

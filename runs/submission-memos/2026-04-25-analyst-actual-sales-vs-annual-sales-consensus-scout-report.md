# 2026-04-25 Analyst Actual Sales Vs Annual Sales Consensus Scout Report

- Date: `2026-04-25`
- Scope: `Analyst` only
- Topic: `analyst_actual_sales_vs_annual_sales_consensus`

## Final Decision

- Continue deep dive on `actual_sales_value_annual` versus `sales_estimate_average_annual`.
- Do not reopen frozen EPS-close, operating-income, cashflow/cap, analyst guidance-band, or model-relative-valuation shells.
- Treat this as the best genuinely new Analyst family candidate in the current runs state.

## Official Evidence

- `runs/field-search-packs/2026-04-25-analyst-actual-sales-vs-annual-sales-consensus.md`
- `runs/expression-families/2026-04-25-analyst-actual-sales-vs-annual-sales-consensus.md`
- Comparison freeze context:
  - `runs/submission-memos/2026-04-25-analyst-top-line-guidance-vs-annual-sales-consensus-stop-memo.md`
  - `runs/submission-memos/2026-04-24-next-step-family-stop.md`
  - `runs/learning-loops/2026-04-24-eps-and-cashflow-freeze.md`

## Field Facts

- Field pair:
  - `actual_sales_value_annual`
  - `sales_estimate_average_annual`
- Dataset / category:
  - `analyst4` / `Analyst > Analyst Estimates`
- Coverage:
  - `actual_sales_value_annual`: `USA / TOP3000 / D1`, coverage `0.9943`
  - `sales_estimate_average_annual`: `USA / TOP3000 / D1`, coverage `1.0`
- Date coverage:
  - both fields: `1.0`
- Type:
  - both fields: `MATRIX`
- Visible crowding:
  - `actual_sales_value_annual`: `126` users / `151` alphas
  - `sales_estimate_average_annual`: `43` users / `56` alphas

## Minimal Baseline Set

- Baseline:
  - `group_rank(actual_sales_value_annual / sales_estimate_average_annual - 1, industry)`
- Variant 1:
  - `group_rank(-(actual_sales_value_annual / sales_estimate_average_annual - 1), industry)`
- Variant 2:
  - `group_rank(actual_sales_value_annual - sales_estimate_average_annual, industry)`

## Why This Is Not A Frozen-Family Rewrite

This lane changes the information object, not the parameterization. It is a realized annual sales surprise against annual consensus, which is different from the frozen EPS-close, operating-income, cashflow/cap, guidance-band, and model-relative-valuation shells already ruled out in the project registry. It is also distinct from the frozen quarterly actual-sales delta lane: here the family is anchored on annual actuals versus annual consensus, not on a quarterly delta or a smoothing/lookback tweak around an older source. The crowding is not trivial, but the field pair itself is clean enough to justify a first probe because the consensus anchor is fully covered and the actual leg is nearly full coverage.

## Next Minimal Experiment

- If the baseline survives first read, keep the family narrow and test only sign and same-unit gap behavior before introducing any extra normalization.
- If the baseline fails both control variants, freeze the family instead of spending budget on more cosmetic normalization.

## Status

- Judgment: `continue deep dive`
- Not yet submit-ready
- No live batch captured in `runs/` for this family yet

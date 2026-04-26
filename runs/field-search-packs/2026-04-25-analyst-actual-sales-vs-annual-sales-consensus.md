# Analyst Actual Sales Vs Annual Sales Consensus Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `analyst_actual_sales_vs_annual_sales_consensus`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Annual reported sales relative to annual sales consensus should capture a cleaner top-line surprise effect than the frozen guidance-band lane, because it uses realized actuals rather than guidance edges.

## Why This Could Matter

- This is a new object-level analyst lane: actual reported sales, not guidance.
- The anchor is annual sales consensus, not a guidance midpoint or band edge.
- It is distinct from the frozen EPS-close, cashflow/cap, operating-income, model-rerating, and quarterly actual-sales delta families.
- The live official field metadata shows near-full coverage, so the first batch is cheap to validate.

## Data Explorer Search Terms

- Primary terms: `actual sales annual`, `sales actual value annual`, `annual sales consensus`
- Synonyms: `sales surprise`, `reported sales`, `sales estimate average annual`
- Abbreviations: `analyst4`, `sales actual`, `sales estimate`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `actual_sales_value_annual` | `analyst4` / `Analyst > Analyst Estimates` | Realized annual sales leg of the surprise trade | `USA / TOP3000 / D1`, coverage `0.9943`, date coverage `1.0`, type `MATRIX` | `126` users / `151` alphas |
| `sales_estimate_average_annual` | `analyst4` / `Analyst > Analyst Estimates` | Clean annual consensus anchor | `USA / TOP3000 / D1`, coverage `1.0`, date coverage `1.0`, type `MATRIX` | `43` users / `56` alphas |

## Coverage And Quality Checks

- Coverage: both fields are effectively full coverage for the target scope.
- Missingness: only the actual field has a small gap; the anchor is full coverage.
- Region / delay compatibility: confirmed in the saved official API capture for `USA / TOP3000 / D1`.
- Field type: both fields are `MATRIX`.

## Why This Is Not A Frozen Family Shell

- Not EPS-close or EPS-sibling.
- Not guidance-band midpoint / edge polishing.
- Not cashflow/cap, operating-income, or model-relative-valuation.
- Not the frozen quarterly actual-sales delta lane.
- The signal is realized annual sales surprise versus annual consensus, which is a different event and information object.

## Baseline Expression Ideas

1. `group_rank(actual_sales_value_annual / sales_estimate_average_annual - 1, industry)`
2. `group_rank(-(actual_sales_value_annual / sales_estimate_average_annual - 1), industry)`
3. `group_rank(actual_sales_value_annual - sales_estimate_average_annual, industry)`

## Likely First Failure

- Sharpe: actual-vs-consensus surprise may still be too weak after ranking.
- Fitness: the family could be sensible but not strong enough.
- Turnover: low-to-moderate; not expected to be the first blocker.
- Weight: large-cap or high-coverage names may dominate.
- Sub-universe: needs live simulation evidence.
- Self-correlation: the main risk is generic analyst crowding, not a frozen-shell reuse.

## Next Action

- Which field should be tried first? `actual_sales_value_annual`
- Which baseline expression should be simulated first? `group_rank(actual_sales_value_annual / sales_estimate_average_annual - 1, industry)`
- Which 2-3 same-family variants should follow? Sign flip, then raw-gap control, then a rank-normalized gap if the first batch is directionally viable.

# Analyst Top-Line Guidance vs Annual Sales Consensus Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `analyst-top-line-guidance-vs-annual-sales-consensus`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

When annual sales guidance sits materially above or below annual sales consensus, the market may take time to reprice the forward top-line expectation, especially when the guidance band is explicit and fully covered.

## Why This Could Matter

- This is a fresh analyst guidance-vs-consensus lane, not an EPS-close or EPS-sibling repair.
- The signal is about forward top-line expectation reset, which is different from the frozen cashflow, operating-income, and model-relative-valuation families.
- The field trio has full region/delay coverage, so the first batch is cheap to read and easy to compare.
- The visible crowding is low enough to justify a minimal live batch before deciding whether the family deserves more budget.

## Data Explorer Search Terms

- Primary terms: `sales guidance`, `annual sales consensus`, `sales estimate average annual`
- Synonyms: `top-line guidance`, `revenue guidance`, `guidance band`, `sales midpoint`
- Abbreviations: `analyst4`, `sales max`, `sales min`, `annual consensus`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `sales_max_guidance_value` | `analyst4` / `Analyst > Analyst Estimates` | Upper edge of annual sales guidance band; useful for the bullish side of the gap | `USA / TOP3000 / D1`, coverage `1.0`, date coverage `1.0`, type `MATRIX` | `36` users / `38` alphas |
| `sales_min_guidance_value` | `analyst4` / `Analyst > Analyst Estimates` | Lower edge of annual sales guidance band; useful for the bearish side of the gap | `USA / TOP3000 / D1`, coverage `1.0`, date coverage `1.0`, type `MATRIX` | `15` users / `18` alphas |
| `sales_estimate_average_annual` | `analyst4` / `Analyst > Analyst Estimates` | Annual sales consensus anchor; the natural comparator for the guidance band | `USA / TOP3000 / D1`, coverage `1.0`, date coverage `1.0`, type `MATRIX` | `43` users / `58` alphas |

## Coverage And Quality Checks

- Coverage: all three fields are at `100%` for `USA / TOP3000 / D1`.
- Missingness: no missingness warning is visible in the live search snapshot for the winner fields.
- Region / delay compatibility: confirmed in the official live Data Explorer and API re-check.
- Field type: all three fields are `MATRIX`.
- Visible crowding: the trio is materially lighter than the more crowded analyst EPS-adjacent branches that were frozen earlier.

## Why This Is Not A Frozen Family Shell

- It is not an EPS-close or EPS-sibling lane.
- It is not a cashflow/cap or operating-income normalization.
- It is not a sales-acceleration repair.
- It is not a model-relative-valuation rerating shell.
- It is a guidance-band vs annual consensus structure, which is a distinct analyst top-line mechanism.

## Baseline Expression Ideas

1. `rank(0.5 * (rank(sales_max_guidance_value) + rank(sales_min_guidance_value)) - rank(sales_estimate_average_annual))`
2. `rank(sales_max_guidance_value) - rank(sales_estimate_average_annual)`
3. `rank(sales_min_guidance_value) - rank(sales_estimate_average_annual)`

## Likely First Failure

- Sharpe: the guidance band may still be too weak or too stale to beat a simple consensus control.
- Fitness: the gap may be real but not strong enough after robustness penalties.
- Turnover: the band could update in bursts, but this is not the first expected blocker.
- Weight: the signal may concentrate in a small set of large-cap names or sectors.
- Sub-universe: needs live simulation evidence; not yet proven.
- Self-correlation: the main risk is overlap with generic analyst consensus crowding.

## Next Action

- Try the midpoint guidance gap first, but keep the fields rank-normalized so unit verify stays clean.
- If the baseline Sharpe is negative, run the sign-flip control immediately before polishing anything else.
- Keep the first batch minimal: midpoint gap, sign flip, max gap, and min gap.
- If the family is weak, stop here rather than polishing sign or lookback as if that were a new family.

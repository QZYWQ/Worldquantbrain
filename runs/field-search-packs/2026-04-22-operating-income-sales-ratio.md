# Operating Income / Sales Fundamental Ratio Field Search Pack

## Metadata

- Date: `2026-04-22`
- Topic: `operating_income_sales_ratio`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-21-sales-delta-fundamental.md`
  - `./runs/expression-families/2026-04-22-capital-structure-balance-sheet-follow-up.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/decision-notes.md`

## Hypothesis

Normalizing `operating_income` by `sales` should turn the raw profitability level into a slow margin-like ratio that is easier to compare across names and less dependent on absolute scale. The forum-crawl template family points to slow ratios as a reusable KB candidate, so this is the most direct confirmed-field instance to test next.

## Why This Could Matter

- Raw `operating_income` smoothing is already dead on TEST.
- Revenue and balance-sheet branches also failed to clear a candidate posture.
- The forum crawl elevated `Fundamental / Model Slow Ratio` as a reusable template family.
- `operating_income / sales` is the simplest confirmed-field version of that family on this account.

## Data Explorer Search Terms

- Primary terms: `operating income`, `sales`, `margin`
- Secondary terms: `revenue`, `profitability`, `operating margin`

## Candidate Fields

| Field | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- |
| `operating_income` | Numerator for the profit side of the ratio | Already confirmed in the current project at `50%` coverage in `USA / D1 / TOP3000` | Crowded individually, but useful when normalized |
| `sales` | Denominator for a direct operating-margin style ratio | Already confirmed in the current project at `50%` coverage in `USA / D1 / TOP3000` | Crowded individually, but the ratio may be less crowded than the raw field |

## Coverage And Quality Checks

- The numerator and denominator are both already verified in prior official Data search results.
- The family does not depend on a new account-specific field discovery.
- Coverage remains structurally sparse because both fields come from the same `fundamental6` family.
- The ratio should be tested as a normalization move, not as a coverage fix.

## Baseline Expression Ideas

1. `group_rank(ts_rank(operating_income / sales, 252), industry)`
2. `group_rank(ts_rank(ts_mean(operating_income / sales, 21), 252), industry)`
3. `group_rank(ts_rank(ts_mean(operating_income / sales, 63), 252), industry)`

## Likely First Failure

- Sharpe: may still be too close to the dead operating-income ridge
- Fitness: may stay weak if the ratio is still sparse
- Turnover: likely manageable
- Weight: still watch sparse fundamental concentration
- Sub-universe: still the main structural risk
- Self-correlation: unknown until a real check run exists

## Next Action

- First field family to try: `operating_income / sales`
- First baseline to simulate: `group_rank(ts_rank(operating_income / sales, 252), industry)`
- Next same-family variants: `21d` and `63d` smoothing controls, then `126d` if the first batch is alive

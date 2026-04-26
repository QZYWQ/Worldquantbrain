# Capital Expenditure Amount Close Industry Field Search Pack

## Metadata

- Date: `2026-04-24`
- Topic: `capital_expenditure_amount_close_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Higher capex estimate intensity relative to price may signal firms in stronger reinvestment regimes, and the live official Data Explorer check in this session found a very low-crowding analyst4 `capital_expenditure_amount` field that is materially cleaner than the older broad capex symbols.

## Why This Could Matter

- The raw invested-capital history-position family failed on sign and sub-universe and emitted a unit warning, so the next capital-related idea should use a cleaner and less crowded information source.
- `capital_expenditure_amount` is an analyst4 matrix field with only `22` visible alphas in the live search results, which is dramatically cleaner than the broad capex symbol family.
- Normalizing the estimate by price keeps the thesis interpretable and closer to the successful analyst EPS/close pattern already validated in the project.

## Data Explorer Search Terms

- Primary terms: `capital expenditure amount`, `capex amount`, `capital expenditures total value`
- Sibling terms: `capital expenditures`, `capex`, `investment spending`
- Distinctness terms: `capital expenditure estimate`, `capex estimate`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `capital_expenditure_amount` | `analyst4` / `Analyst Estimate Data for Equity` | Best first anchor because it is a low-crowding analyst estimate field and is easy to normalize by price | Live official search shows `MATRIX`, `75.24%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Live official search shows `22` visible alphas and `20` users |
| `fnd6_capxs` | `fundamental6` / `Company Fundamental Data for Equity` | Legacy capex comparison control if the analyst estimate version proves too fragile | Live official search shows `SYMBOL`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Live official search shows `124` visible alphas |
| `capex` | `fundamental6` / `Company Fundamental Data for Equity` | Broader capex fallback control only; it is much more crowded and should not be the anchor | Live official search shows `SYMBOL`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Live official search shows `26,589` visible alphas |

## Coverage And Quality Checks

- Coverage:
  `capital_expenditure_amount` has materially better coverage than a lot of sparse footnote fields and is strong enough to start a diagnostic batch.
- Missingness:
  Because it is a matrix field, the first batch should normalize it instead of using it raw in a history-position form.
- Region / delay compatibility:
  The live official Data Explorer search was `USA / D1 / TOP3000`.
- Field type:
  `capital_expenditure_amount` is a `MATRIX` field, so a price-normalized form is the safest first expression.
- Crowding:
  The field is still low crowding compared with legacy capex symbols, so it deserves a first-pass batch before being dismissed.

## Baseline Expression Ideas

1. `group_rank(ts_rank(capital_expenditure_amount / close, 84), industry)`
2. `group_rank(-ts_rank(capital_expenditure_amount / close, 84), industry)`
3. `group_rank(ts_rank(capital_expenditure_amount / close, 126), industry)`
4. `group_rank(ts_rank(capital_expenditure_amount / close, 252), industry)`

## Likely First Failure

- Sharpe:
  The sign may still be wrong, or capex intensity may not be the right reinvestment proxy.
- Fitness:
  Coverage is better than the failed invested-capital family, but it is not full, so grouping can still weaken the branch.
- Turnover:
  This is unlikely to be the first blocker because the thesis is still slow.
- Weight:
  Some industries may dominate capex patterns, so concentration still needs watching.
- Sub-universe:
  This remains a real risk, especially if normalization creates a small effective sample.
- Self-correlation:
  Unknown until a real official check exists.
- Units:
  The first batch should use price normalization to avoid repeating the raw invested-capital `TS_RANK` unit warning.

## Next Action

- Which field should be tried first? `capital_expenditure_amount`
- Which baseline expression should be simulated first? `group_rank(ts_rank(capital_expenditure_amount / close, 84), industry)`
- Which 2-3 same-family variants should follow? Sign flip, 126d, and 252d controls.

# Sales Delta Fundamental Field Search Pack

## Metadata

- Date: `2026-04-21`
- Topic: `sales_delta_fundamental`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Official page context:
  - `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=sales&universe=TOP3000`
  - `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=revenue&universe=TOP3000`
  - `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=operating%20income&universe=TOP3000`

## Hypothesis

Stocks with improving top-line fundamentals should outperform same-industry peers before that improvement is fully repriced, and a slow revenue-delta ranking should diversify away from the locked analyst EPS lane.

## Why This Could Matter

- This is a real information-family move away from analyst estimate data and the already blocked disagreement branch.
- The thesis is slow-horizon and interpretable: cross-sectional re-ranking on improving top-line fundamentals rather than fast news or option flow.
- The official search results show no easy coverage upgrade inside this fundamentals family, so the right first choice is the least crowded workable top-line field, not endless synonym hunting.

## Data Explorer Search Terms

- Primary terms: `sales`, `revenue`, `operating income`
- Synonyms: `turnover`, `top line`, `net sales`
- Abbreviations: `rev`, `oi`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `revenue` | `Company Fundamental Data for Equity` / `fundamental6` | Best first field for this lane because it is a direct top-line measure and stays closest to the original sales-delta hypothesis while being visibly less crowded than `sales` | Official search in this session shows `Matrix`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Official search shows `12460` visible alphas |
| `sales` | `Company Fundamental Data for Equity` / `fundamental6` | Valid synonym control for the same thesis if `revenue` behaves oddly in simulation | Official search in this session shows `Matrix`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Official search shows `34724` visible alphas, materially more crowded than `revenue` |
| `operating_income` | `Company Fundamental Data for Equity` / `fundamental6` | Profitability sibling fallback if the revenue-delta sign fails cleanly but the broader slow-fundamentals thesis still looks alive | Official search in this session shows `Matrix`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Official search shows `45767` visible alphas, so it is not the preferred first line |

## Coverage And Quality Checks

- Coverage:
  The confirmed `fundamental6` top-line and profit fields checked in this session all stayed at `50%` coverage, so this family starts with structural sparsity.
- Missingness:
  The missingness looks family-wide rather than specific to one synonym, which means field switching alone is unlikely to rescue Sub-universe behavior.
- Region / delay compatibility:
  `sales`, `revenue`, and `operating_income` were all verified on official `USA / D1 / TOP3000` Data search pages in this session.
- Field type:
  All three confirmed candidates are `Matrix` fields.

## Baseline Expression Ideas

1. `group_rank(ts_delta(revenue, 63), industry)`
2. `group_rank(ts_delta(revenue, 21), industry)`
3. `group_rank(ts_delta(revenue, 126), industry)`

## Likely First Failure

- Sharpe:
  The first risk is thesis sign error or a signal that is too slow and already priced.
- Fitness:
  Even if the sign is right, sparse fundamentals coverage can make the line look weak or fragile in aggregate IS.
- Turnover:
  This is the least likely first bottleneck because a revenue-delta lane should trade slowly.
- Weight:
  Structural sparsity can still create concentration if the active names cluster inside a few industries.
- Sub-universe:
  This is the main structural risk because all verified first-choice fields showed only `50%` coverage.
- Self-correlation:
  Lower family-overlap risk than another analyst EPS sibling, but still unknown until real checks exist.

## Next Action

- Which field should be tried first?
  `revenue`
- Which baseline expression should be simulated first?
  `group_rank(ts_delta(revenue, 63), industry)`
- Which 2-3 same-family variants should follow?
  Direct sign control on the same `63d` line, then faster `21d` and slower `126d` revenue-delta variants before opening the operating-income fallback lane.

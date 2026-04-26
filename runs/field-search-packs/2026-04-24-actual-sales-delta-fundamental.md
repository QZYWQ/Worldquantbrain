# Actual Sales Delta Fundamental Field Search Pack

## Metadata

- Date: `2026-04-24`
- Topic: `actual_sales_delta_fundamental`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Actual reported sales should re-rank same-industry peers over a slow horizon, and the live official Data Explorer check in this session found a low-crowding analyst4 sales field with near-full coverage.

## Why This Could Matter

- The old revenue / sales delta lane is crowded and only partially covered in the current saved truth.
- The actual-sales branch is a cleaner information-source change: it uses verified actual reported sales rather than a legacy symbol field.
- This should behave like a slow-horizon fundamentals signal, so the first test is sign and structural viability rather than aggressive tuning.

## Data Explorer Search Terms

- Primary terms: `actual sales`, `sales value quarterly`, `sales value annual`
- Synonyms: `sales`, `revenue`, `sales growth`
- Abbreviations: `saleq`, `sales_growth`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `actual_sales_value_quarterly` | `analyst4` / `Analyst Estimate Data for Equity` | Best first field for this lane because it is the freshest verified actual-sales field and has the lowest crowding among the verified top-line candidates in this session | Live search in this session shows `MATRIX`, `100%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Live search shows `147` visible alphas |
| `actual_sales_value_annual` | `analyst4` / `Analyst Estimate Data for Equity` | Safer annual control for the same actual-sales thesis if the quarterly version proves too noisy | Live search in this session shows `MATRIX`, `99.43%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Live search shows `151` visible alphas |
| `sales_growth` | `fundamental6` / `Company Fundamental Data for Equity` | Slow-growth fallback if the actual-sales family needs a looser proxy, but it is more crowded and only half-covered | Live search in this session shows `SYMBOL`, `50%` coverage | Live search shows `7,630` visible alphas |
| `revenue` | `fundamental6` / `Company Fundamental Data for Equity` | Legacy comparison control only; it is much more crowded than the actual-sales fields and should not be the primary anchor now | Live search in this session shows `SYMBOL`, `50%` coverage | Live search shows `12,460` visible alphas |

## Coverage And Quality Checks

- Coverage:
  `actual_sales_value_quarterly` is fully covered in the live search results; `actual_sales_value_annual` is nearly full coverage and can serve as a control.
- Missingness:
  The actual-sales branch looks materially healthier than the old `revenue` / `sales` symbol lane.
- Region / delay compatibility:
  Both actual-sales fields were verified on official `USA / D1 / TOP3000` search pages in this session.
- Field type:
  The actual-sales fields are `MATRIX` fields, which is a cleaner starting point than the legacy `SYMBOL` lane.

## Baseline Expression Ideas

1. `group_rank(ts_delta(actual_sales_value_quarterly, 63), industry)`
2. `group_rank(-ts_delta(actual_sales_value_quarterly, 63), industry)`
3. `group_rank(ts_delta(actual_sales_value_quarterly, 126), industry)`

## Likely First Failure

- Sharpe:
  The sign may still be wrong, or the actual-sales update cadence may already be too slow for a clean delta signal.
- Fitness:
  Even with a good sign, the family can still look weak if the reported-sales coverage is too thin after grouping.
- Turnover:
  This is unlikely to be the first bottleneck because the family is intentionally slow.
- Weight:
  Concentration is possible if a small set of industries carries most of the useful signal.
- Sub-universe:
  This remains the main structural risk; the family should not be promoted without a real sub-universe check.
- Self-correlation:
  Lower family-overlap risk than another analyst EPS sibling, but still unknown until a real check exists.

## Next Action

- Which field should be tried first? `actual_sales_value_quarterly`
- Which baseline expression should be simulated first? `group_rank(ts_delta(actual_sales_value_quarterly, 63), industry)`
- Which 2-3 same-family variants should follow? Direct sign control, then 126d, then an annual actual-sales control.

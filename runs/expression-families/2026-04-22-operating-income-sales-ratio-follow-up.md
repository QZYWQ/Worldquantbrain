# Operating Income / Sales Fundamental Ratio Follow-up Expression Family

## Metadata

- Date: `2026-04-22`
- Topic: `operating_income_sales_ratio_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-22-operating-income-sales-ratio.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`

## Hypothesis

The operating-income ridge failed because raw profitability level was not enough to survive TEST. A slow ratio of `operating_income / sales` may keep the profitability intuition while normalizing for scale and making the family more comparable cross-sectionally.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `operating_income`
  - `sales`
- Confirmed neutralization:
  - `industry`
- Assumptions to test:
  - The ratio itself may be more informative than the raw numerator.
  - A `252d` history rank is still the right first comparison frame.
  - Moderate smoothing may help if the direct ratio is too jumpy.
  - If the first batch fails, the family should be killed quickly instead of re-polished into the old operating-income ridge.

## Baseline Expression

```text
group_rank(ts_rank(operating_income / sales, 252), industry)
```

## Variant 1

- Goal:
  Test whether a light smoother stabilizes the raw ratio without flattening the edge.
- Main lever:
  Add a `21d` mean before the `252d` history rank.

```text
group_rank(ts_rank(ts_mean(operating_income / sales, 21), 252), industry)
```

## Variant 2

- Goal:
  Test whether moderate smoothing gives the best balance between signal stability and responsiveness.
- Main lever:
  Add a `63d` mean before the `252d` history rank.

```text
group_rank(ts_rank(ts_mean(operating_income / sales, 63), 252), industry)
```

## Variant 3

- Goal:
  Test whether heavier smoothing is needed to avoid the raw ratio collapsing into the dead operating-income ridge.
- Main lever:
  Add a `126d` mean before the `252d` history rank.

```text
group_rank(ts_rank(ts_mean(operating_income / sales, 126), 252), industry)
```

## Expected First Failure

- Sharpe:
  The ratio may still be too close to the old profitability ridge.
- Fitness:
  Sparse fundamentals coverage may keep the line below candidate quality.
- Turnover:
  Should remain reasonable if the ratio behaves like a slow signal.
- Weight:
  Ratio concentration may still show up in a small set of names or sectors.
- Sub-universe:
  This is still the structural risk until official submission-style evidence appears.
- Self-correlation:
  Unknown until a real check run exists.

## Optimization Order

1. Test the direct ratio first.
2. Compare `21d`, `63d`, and `126d` smoothing around the same `252d` history rank.
3. If the family still looks alive, only then consider a structure-axis branch such as `subindustry`.
4. If the batch stays weak or the test view turns negative, kill the family instead of polishing it into another dead operating-income variant.

## Next Simulation Batch

- Planned batch:
  direct ratio baseline + `21d` / `63d` / `126d` smoothing variants.
- Backup comparison:
  if the batch is weak, return to the forum crawl for a different KB candidate rather than extending the same profitability ratio.

## TEST Update

- Simulation 20 was switched to TEST view on the logged-in official WorldQuant BRAIN simulate UI.
- TEST aggregate data: `Sharpe -0.12 / Fitness -0.02 / Turnover 4.03% / Returns -0.35% / Drawdown 2.83% / Margin -1.75‱`.
- No visible `Check Submission` evidence or non-null `subuniverse_pass` appeared.
- `Submit Alpha` stayed disabled in the captured UI state.

## Decision

- Kill the `operating_income / sales` ratio family.
- Keep the 21d train-side win as a negative control only.
- Branch the next live research to `event_trigger_low_turnover_volatility_gate` instead of polishing this lane further.


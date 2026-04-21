# Sales Delta Fundamental Expression Family

## Metadata

- Date: `2026-04-21`
- Topic: `sales_delta_fundamental`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Recent improvement in a company's top-line fundamentals should help it outrank same-industry peers over a slow horizon, and the first thing to test is whether daily cross-sectional ranking on revenue delta has the right sign at all.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `revenue`
- Equivalent fallback fields:
  - `sales`
  - `operating_income`
- Unconfirmed assumptions:
  - `63d` is a reasonable middle-window control before any extra smoothing or normalization.
  - `industry` grouping is still the right first-pass neutralization for this new fundamentals lane.

## Baseline Expression

```text
group_rank(ts_delta(revenue, 63), industry)
```

## Variant 1

- Goal:
  Test the thesis sign directly before spending more time on same-family polishing.
- Main lever:
  Sign only, holding field and horizon fixed.

```text
group_rank(-ts_delta(revenue, 63), industry)
```

## Variant 2

- Goal:
  Check whether a faster re-ranking window captures earnings-season repricing better than the middle baseline.
- Main lever:
  Horizon from `63` to `21`.

```text
group_rank(ts_delta(revenue, 21), industry)
```

## Variant 3

- Goal:
  Check whether a slower window better matches the low-turnover fundamentals thesis.
- Main lever:
  Horizon from `63` to `126`.

```text
group_rank(ts_delta(revenue, 126), industry)
```

## Expected First Failure

- Sharpe:
  The sign may still be wrong if revenue acceleration is already fully priced before the ranking signal reacts.
- Fitness:
  Sparse fundamentals coverage can make the family look weak even if one horizon has the right directional intuition.
- Turnover:
  This is unlikely to be the first blocker because all four lines are intentionally slow.
- Weight:
  Coverage concentration is the real reason this family could over-focus, not excessive trading speed.
- Sub-universe:
  Most likely first structural failure because the confirmed field only showed `50%` coverage in official search.
- Self-correlation:
  Unknown, but the family should still diversify better than another analyst estimate sibling if one branch survives.

## Optimization Order

1. Use the direct sign control to decide whether the revenue-delta thesis deserves any more work.
2. Compare `21 / 63 / 126` horizon behavior before changing fields or adding smoothing.
3. If all revenue windows are structurally weak, branch to `operating_income_history_position` instead of polishing this lane.

## Next Simulation Batch

- Baseline:
  `group_rank(ts_delta(revenue, 63), industry)`
- Variant 1:
  `group_rank(-ts_delta(revenue, 63), industry)`
- Variant 2:
  `group_rank(ts_delta(revenue, 21), industry)`
- Variant 3:
  `group_rank(ts_delta(revenue, 126), industry)`

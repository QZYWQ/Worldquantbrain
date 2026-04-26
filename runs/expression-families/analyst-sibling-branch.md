# Analyst Sibling Expression Family

## Metadata

- Date: 2026-04-19
- Topic: `analyst_eps_sibling_qfv4_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The first-cycle analyst EPS thesis may survive better out of sample if the signal is rebuilt on lower-crowding quarterly analyst4 EPS siblings instead of the more obvious annual mean baseline.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `anl4_qfv4_median_eps`
  - `anl4_qfv4_eps_mean`
  - `anl4_afv4_median_eps`
  - `anl4_afv4_dts_spe`
  - `close`
- Equivalent fallback fields:
  - `earnings_per_share_median_value`
  - `earnings_per_share_average`
- Unconfirmed assumptions:
  - The qfv4 siblings will be less self-correlated in practice, not only less crowded in field metadata.
  - The same `60d` horizon remains the right first-pass comparison frame for this branch.

## Baseline Expression

```text
group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)
```

## Variant 1

- Goal:
  Keep the quarterly sibling lane but swap aggregation from median to mean.
- Main lever:
  Field axis from `anl4_qfv4_median_eps` to `anl4_qfv4_eps_mean`.

```text
group_rank(ts_rank(anl4_qfv4_eps_mean/close, 60), industry)
```

## Variant 2

- Goal:
  Hold the analyst4 naming lane fixed while switching back to the annual median control.
- Main lever:
  Frequency axis from `qfv4` to `afv4`.

```text
group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)
```

## Variant 3

- Goal:
  Keep the quarterly median field but test whether a slower horizon is more robust.
- Main lever:
  Time axis from `60` to `120`.

```text
group_rank(ts_rank(anl4_qfv4_median_eps/close, 120), industry)
```

## Expected First Failure

- Sharpe:
  The sibling fields may not change enough information content to create a visible edge over the first-cycle baseline.
- Fitness:
  Weak holdout strength is still the first real danger even if in-sample metrics look acceptable.
- Turnover:
  Moderate risk only if later branches speed up the horizon; the current `60d` comparison should stay controlled.
- Weight:
  Lower risk than sparse event or guidance fields because the chosen level siblings have full coverage.
- Sub-universe:
  Needs real simulation evidence, but the branch should be cleaner than sparse analyst fields.
- Self-correlation:
  Still the main family-level risk until official checks say otherwise.

## Current Decision

- Freeze this family.
- The annual-median control `anl4_afv4_median_60d_industry` is the stronger line on holdout, so the qfv4 siblings should not receive more near-neighbor budget.
- Do not run more qfv4 window or mean variants unless a genuinely new analyst thesis appears.

## Optimization Order

1. Compare qfv4 median and qfv4 mean against the first-cycle baseline before changing multiple structural levers.
2. Keep the annual-median analyst4 line only as a control to test whether the lower-crowding quarterly siblings are truly different.
3. Only open a new analyst branch if it is not just another qfv4 near-neighbor.

## Next Simulation Batch

- Baseline:
  `group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)`
- Variant 1:
  `group_rank(ts_rank(anl4_qfv4_eps_mean/close, 60), industry)`
- Variant 2:
  `group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)`
- Variant 3:
  `group_rank(ts_rank(anl4_qfv4_median_eps/close, 120), industry)`

## Stop Condition

- If the qfv4 family is revisited, the first question must be whether it is still a distinct thesis rather than a holdout-polishing variant.

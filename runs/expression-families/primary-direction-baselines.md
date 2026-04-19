# Primary Direction Expression Family

## Metadata

- Date: 2026-04-18
- Topic: `analyst_eps_price_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Cross-sectional winners should be stocks whose analyst EPS expectations look strong relative to price, especially when compared within industry rather than across the full market.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `earnings_per_share_average`
  - `earnings_per_share_median_value`
  - `est_eps`
  - `close`
- Equivalent fallback fields:
  - `anl4_afv4_median_eps`
  - `earnings_per_share_average`
  - `earnings_per_share_median_value`
- Unconfirmed assumptions:
  - The built-in group key `industry` behaves normally in the current simulation template.
  - Default first-batch settings will remain `USA / D1 / TOP3000` with platform defaults unless changed manually in Simulate.

## Baseline Expression

```text
group_rank(ts_rank(earnings_per_share_average/close, 60), industry)
```

## Variant 1

- Goal:
  Check whether the same analyst thesis works better on a faster medium-short horizon.
- Main lever:
  Window axis from `60` to `20`.

```text
group_rank(ts_rank(earnings_per_share_average/close, 20), industry)
```

## Variant 2

- Goal:
  Test whether a slower horizon reduces noise and improves robustness.
- Main lever:
  Window axis from `60` to `120`.

```text
group_rank(ts_rank(earnings_per_share_average/close, 120), industry)
```

## Variant 3

- Goal:
  Hold horizon fixed while changing the analyst field to reduce crowding pressure.
- Main lever:
  Field axis from mean EPS estimate to median EPS estimate.

```text
group_rank(ts_rank(earnings_per_share_median_value/close, 60), industry)
```

## Expected First Failure

- Sharpe:
  The signal may be credible but not strong enough if the price-normalized analyst lane is already well explored.
- Fitness:
  Any near-pass Sharpe may still need turnover control or a less crowded field variant.
- Turnover:
  Variant 1 is the main turnover risk because the window is shortest.
- Weight:
  Lower risk than sparse event lines because the chosen first-batch fields have 100% coverage.
- Sub-universe:
  Lower structural risk than the 78% coverage `est_eps` branch, but still verify with real results instead of assuming.
- Self-correlation:
  Most likely bottleneck for the baseline and the 20-day branch.

## Optimization Order

1. Run the four baseline-family expressions unchanged and read the first real bottleneck instead of pre-optimizing.
2. If self-correlation dominates, branch first on field choice before changing multiple structural levers.
3. If turnover dominates, slow the horizon or add smoothing before changing the thesis.

## Next Simulation Batch

- Baseline:
  `group_rank(ts_rank(earnings_per_share_average/close, 60), industry)`
- Variant 1:
  `group_rank(ts_rank(earnings_per_share_average/close, 20), industry)`
- Variant 2:
  `group_rank(ts_rank(earnings_per_share_average/close, 120), industry)`
- Variant 3:
  `group_rank(ts_rank(earnings_per_share_median_value/close, 60), industry)`

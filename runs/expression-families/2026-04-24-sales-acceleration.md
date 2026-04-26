# Sales Acceleration Expression Family

## Metadata

- Date: `2026-04-24`
- Topic: `sales_acceleration`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-21-sales-delta-fundamental.md`
  - `./runs/field-search-packs/2026-04-24-sales-acceleration.md`
  - `./runs/submission-memos/2026-04-24-capital-structure-ratio-closure.md`

## Hypothesis

If raw top-line delta and revenue smoothing are both too weak, the change in top-line growth may still contain a slower re-ranking effect that the market has not fully digested.

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `revenue`
- Confirmed neutralization:
  - `industry`
- Assumptions to test:
  - A 63d second-difference baseline is the cleanest first probe.
  - The direct first-difference revenue line should be the immediate control.
  - Shorter and longer acceleration windows can be checked only if the baseline is alive.

## Baseline Expression

```text
group_rank(ts_delta(ts_delta(revenue, 63), 63), industry)
```

## Variant 1

- Goal:
  Test whether the simpler first-difference signal is actually the better shape.
- Main lever:
  Replace the acceleration term with the direct revenue delta control.

```text
group_rank(ts_delta(revenue, 63), industry)
```

## Variant 2

- Goal:
  Test whether a faster acceleration window reacts better to sales regime changes.
- Main lever:
  Reduce the acceleration horizon from `63` to `21`.

```text
group_rank(ts_delta(ts_delta(revenue, 21), 21), industry)
```

## Variant 3

- Goal:
  Test whether a slower acceleration window is more stable and less fragile.
- Main lever:
  Increase the acceleration horizon from `63` to `126`.

```text
group_rank(ts_delta(ts_delta(revenue, 126), 126), industry)
```

## Expected First Failure

- Sharpe:
  The acceleration term may simply be too noisy and fail to beat the first-difference control.
- Fitness:
  Sparse top-line coverage can still make the family look weak after grouping.
- Turnover:
  Likely manageable if the signal is real, so this is not the first bottleneck.
- Weight:
  Concentration can still creep in through the sparse accounting reporters.
- Sub-universe:
  Still structurally risky because the verified top-line field family is only half covered.
- Self-correlation:
  Unknown until real check evidence exists.

## Optimization Order

1. Check the acceleration baseline against the first-difference control immediately.
2. If the baseline is weak, test the shorter and longer acceleration windows.
3. If the whole lane stays below the floor, kill this family instead of polishing the same top-line source again.

## Next Simulation Batch

- Baseline:
  `group_rank(ts_delta(ts_delta(revenue, 63), 63), industry)`
- Variant 1:
  `group_rank(ts_delta(revenue, 63), industry)`
- Variant 2:
  `group_rank(ts_delta(ts_delta(revenue, 21), 21), industry)`
- Variant 3:
  `group_rank(ts_delta(ts_delta(revenue, 126), 126), industry)`


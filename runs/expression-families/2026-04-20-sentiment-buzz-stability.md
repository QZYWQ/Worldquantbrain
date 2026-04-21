# Sentiment Buzz Stability Expression Family

## Metadata

- Date: `2026-04-20`
- Topic: `sentiment_buzz_stability`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Persistent multi-day buzz should be more useful than a one-day buzz spike because stable attention may keep capital flowing into the same names for several days.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `scl12_buzz`
- Equivalent fallback fields:
  - `scl12_buzz_fast_d1`
  - `snt_buzz`
  - `snt_buzz_fast_d1`
- Unconfirmed assumptions:
  - Higher sustained buzz is the correct first-pass sign for the lane.
  - The built-in group key `industry` behaves normally in the current simulation template.
  - The first batch should stay structurally simple before any event gating or signed-buzz branching.

## Baseline Expression

```text
group_rank(ts_mean(scl12_buzz, 5), industry)
```

## Variant 1

- Goal:
  Slow the stability window slightly to see whether a bit more persistence improves robustness without losing the buzz thesis.
- Main lever:
  Window axis from `5` to `10`.

```text
group_rank(ts_mean(scl12_buzz, 10), industry)
```

## Variant 2

- Goal:
  Test whether a materially slower persistence window lowers noise and turnover further.
- Main lever:
  Window axis from `10` to `20`.

```text
group_rank(ts_mean(scl12_buzz, 20), industry)
```

## Variant 3

- Goal:
  Keep the same field but remove the rolling-mean smoothing so the first batch can compare stability versus a simpler time-series ranking control.
- Main lever:
  Smoothing structure from `ts_mean` to `ts_rank`.

```text
group_rank(ts_rank(scl12_buzz, 10), industry)
```

## Expected First Failure

- Sharpe:
  The lane could still be too crowded if persistent buzz is already heavily harvested.
- Fitness:
  The first batch may show acceptable direction but weak robustness because `scl12_buzz` has high visible alpha usage.
- Turnover:
  The shortest-window baseline and the unsmoothed control are the main turnover risks.
- Weight:
  Lower structural risk than sparse event or analyst-disagreement lanes because the primary field has full coverage.
- Sub-universe:
  Less likely than in the blocked analyst branch, but still must be read from real platform output.
- Self-correlation:
  Most likely first hard bottleneck for the slow main field.

## Optimization Order

1. Run the first batch unchanged and determine whether crowding or basic signal weakness is the first bottleneck.
2. If the shortest windows are noisy, keep the field fixed and prefer slower stability windows before adding new operators.
3. If every `scl12_buzz` window looks too crowded, branch next on the lower-usage fallback fields before adding event gates.

## Next Simulation Batch

- Baseline:
  `group_rank(ts_mean(scl12_buzz, 5), industry)`
- Variant 1:
  `group_rank(ts_mean(scl12_buzz, 10), industry)`
- Variant 2:
  `group_rank(ts_mean(scl12_buzz, 20), industry)`
- Variant 3:
  `group_rank(ts_rank(scl12_buzz, 10), industry)`

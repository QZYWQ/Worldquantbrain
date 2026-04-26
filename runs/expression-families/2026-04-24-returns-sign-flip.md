# Returns Sign Flip Expression Family

## Metadata

- Date: `2026-04-24`
- Topic: `returns_sign_flip`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Raw negative returns are showing the strongest holdout behavior in the current live queue, but the line is too noisy and too high-turnover to submit as-is. A light smoothing step should reduce turnover enough to make the family worth a repair batch.

## Research Contract

- Mechanism: short-horizon negative returns signal
- Data category: price / returns
- Idea type: reversal / short-term mean reversion
- Universe: USA / TOP3000
- Liquidity fit: liquid names only; avoid illiquid tails
- Holding frequency: short
- Delay: 1
- Neutralization target: none for the raw baseline; industry or subindustry only as comparison controls
- Decay: 4
- Truncation: 0.08
- NaN policy: OFF
- Pasteurization: ON
- Unit handling: VERIFY
- Coverage floor: full returns coverage expected
- Freshness floor days: not a blocker for returns data
- Factor risk hypothesis: the raw signal is likely too fast and too crowded, but the holdout is strong enough that a modest smoothing step may bring turnover and fitness back into range
- Kill condition: if smoothing does not bring turnover down quickly, freeze the family and stop spending budget on raw returns

## Validation Design

- Primary test period: 1Y
- Regime slices: 2020-2021, 2022-2023
- Liquidity slice: TOP3000 liquid names
- Subuniverse gate: require a real subuniverse check before any packaging claim
- Factor overlay: compare against the close-delta sign-flip family and the current close-vwap crowding cluster
- Comparison controls: 5d smoothing, 10d smoothing, and one grouped control
- Promotion rule: promote only if turnover falls below the visible cap while test-period strength stays clearly positive
- Demotion rule: demote to hold after one failed smoothing probe or if the holdout collapses once the noise is reduced

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `returns`
- Equivalent fallback fields:
  - none
- Unconfirmed assumptions:
  - `ts_mean(returns, d)` is the right first repair lever
  - `5d` is the right first smoothing window
  - industry grouping may help if smoothing alone does not cut the noise enough

## Baseline Expression

```text
-returns
```

## Variant 1

- Goal: test whether a light smoothing step lowers turnover without killing the holdout.
- Main lever: add a `5d` mean to the raw returns signal.

```text
-ts_mean(returns, 5)
```

## Variant 2

- Goal: test whether a slower smoothing window is needed to clear the turnover cap.
- Main lever: increase the smoothing window from `5` to `10`.

```text
-ts_mean(returns, 10)
```

## Variant 3

- Goal: test whether grouped ranking helps stabilize the smoothed returns line.
- Main lever: add industry grouping after the `5d` smoothing step.

```text
-group_rank(ts_mean(returns, 5), industry)
```

## Expected First Failure

- Sharpe:
  The holdout looks strong, so Sharpe is not the first obvious blocker.
- Fitness:
  The current anchor is still below the visible IS floor, so fitness may remain the first blocker even after smoothing.
- Turnover:
  This is the most obvious knob to fix first because the raw line is above the visible turnover cap.
- Weight:
  Crowding may stay high if the family remains too close to generic short-term return reversal.
- Sub-universe:
  Unknown until a real check resolves.
- Self-correlation:
  Unknown until the live check resolves; this family may still overlap with other high-turnover reversal lines.

## Optimization Order

1. Try 5d smoothing first.
2. If turnover is still too high, move to 10d smoothing before adding any extra structure.
3. Only after the smoothing probes should grouped ranking be tested.

## Next Simulation Batch

- Baseline: `-returns`
- Variant 1: `-ts_mean(returns, 5)`
- Variant 2: `-ts_mean(returns, 10)`
- Variant 3: `-group_rank(ts_mean(returns, 5), industry)`

## Current Status

- `qMmpvp8v` was submitted on `2026-04-24` and is now `ACTIVE`.
- Live official page shows `OS Testing Status = 4 PENDING`.
- Do not keep polishing this branch while OS is running.

# Close Delta Momentum Sign Flip Expression Family

## Metadata

- Date: `2026-04-24`
- Topic: `close_delta_momentum_sign_flip`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Short-horizon price delta can be useful when the direction is flipped and the signal is ranked within industry groups. The live queue shows this family has unusually strong test-period behavior relative to the current EPS and operating-income branches, so it is worth a single focused repair round instead of more same-family polishing on the dead lines.

## Research Contract

- Mechanism: short-horizon close-price change, ranked and sign-flipped
- Data category: price / returns
- Idea type: short-horizon momentum or reversal
- Universe: USA / TOP3000
- Liquidity fit: liquid names only; avoid illiquid microstructure traps
- Holding frequency: short / medium-short
- Delay: 1
- Neutralization target: industry, with subindustry as the first comparison control
- Decay: 4
- Truncation: 0.08
- NaN policy: OFF
- Pasteurization: ON
- Unit handling: VERIFY
- Coverage floor: full price coverage expected
- Freshness floor days: not a blocker for price data
- Factor risk hypothesis: the raw signal may be too broad or too crowded, but the sign flip plus grouping can still produce a robust holdout if the neutralization axis is right
- Kill condition: if the subindustry control does not improve fitness or if self-correlation resolves as a hard fail, freeze the family and stop pushing the price-delta lane

## Validation Design

- Primary test period: 1Y
- Regime slices: 2020-2021, 2022-2023
- Liquidity slice: TOP3000 liquid names
- Subuniverse gate: require a real subuniverse check before any packaging claim
- Factor overlay: compare against the current close-vwap crowding cluster and the raw -returns control
- Comparison controls: subindustry neutralization, longer rank window, and a light smoothing control
- Promotion rule: promote only if TEST stays strong while IS fitness clears the floor and self-correlation remains non-blocking
- Demotion rule: demote to hold after one failed neutralization probe or if the holdout collapses on the next structural change

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `close`
  - `industry`
- Equivalent fallback fields:
  - none
- Unconfirmed assumptions:
  - `subindustry` neutralization may improve distinctness without destroying the signal
  - the current `20`-day inner rank window is a decent first anchor
  - the strong test-period behavior is real enough to justify one repair batch

## Baseline Expression

```text
-group_rank(ts_rank(ts_delta(close, 3), 20), industry)
```

## Variant 1

- Goal: test whether finer neutralization improves distinctness and fitness.
- Main lever: neutralization axis from `industry` to `subindustry`.

```text
-group_rank(ts_rank(ts_delta(close, 3), 20), subindustry)
```

## Variant 2

- Goal: test whether a slower inner rank window reduces noise and turnover pressure.
- Main lever: inner window from `20` to `30`.

```text
-group_rank(ts_rank(ts_delta(close, 3), 30), industry)
```

## Variant 3

- Goal: test whether a slightly faster inner rank window keeps the strong holdout while lifting fitness.
- Main lever: inner window from `20` to `10`.

```text
-group_rank(ts_rank(ts_delta(close, 3), 10), industry)
```

## Expected First Failure

- Sharpe:
  The current anchor already has good Sharpe, so this is not the first likely blocker.
- Fitness:
  This is the main IS bottleneck; the current anchor is below the floor even though test is strong.
- Turnover:
  The current anchor is already within the visible turnover limit, so this is less urgent than fitness.
- Weight:
  Crowding could still show up after neutralization changes.
- Sub-universe:
  Unknown until a real check resolves.
- Self-correlation:
  Unknown until the live check resolves; this family may still be too close to other close-vwap / short-horizon crowding lines.

## Optimization Order

1. Try subindustry neutralization first.
2. If that fails, adjust the inner rank window before adding any extra operators.
3. Do not add trade filters or extra smoothing until the simple controls tell us whether the family is genuinely alive.

## Next Simulation Batch

- Baseline: `-group_rank(ts_rank(ts_delta(close, 3), 20), industry)`
- Variant 1: `-group_rank(ts_rank(ts_delta(close, 3), 20), subindustry)`
- Variant 2: `-group_rank(ts_rank(ts_delta(close, 3), 30), industry)`
- Variant 3: `-group_rank(ts_rank(ts_delta(close, 3), 10), industry)`

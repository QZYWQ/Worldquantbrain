# 2026-04-25 Put Breakeven 60 Live First Batch

## Decision

- Stop `put_breakeven_60` after the first live batch.
- Freeze the family for the current budget.
- Do not spend more budget on lookback, smoothing, or group-axis polish inside this lane.

## What Was Run

- Baseline: `group_rank(ts_rank(put_breakeven_60 / close, 10), sector)`
- Variant 1: `-group_rank(ts_rank(put_breakeven_60 / close, 10), sector)`
- Variant 2: `group_rank(ts_rank(put_breakeven_10 / close, 10), sector)`
- Variant 3: `-group_rank(ts_rank(put_breakeven_10 / close, 10), sector)`

## Official Results

- Baseline `blW0d0GZ`
  - IS: `Sharpe 0.97`, `Fitness 0.31`, `Turnover 47.62%`, `Returns 4.75%`
  - TEST: `Sharpe 1.59`, `Fitness 0.51`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`
- Sign flip `A1OXGW3w`
  - IS: `Sharpe -0.97`, `Fitness -0.31`, `Turnover 47.62%`, `Returns -4.75%`
  - TEST: `Sharpe -1.59`, `Fitness -0.51`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`
- 10-day sibling `P0XLGwW7`
  - IS: `Sharpe 1.07`, `Fitness 0.33`, `Turnover 51.53%`, `Returns 4.99%`
  - TEST: `Sharpe 1.19`, `Fitness 0.30`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`
- 10-day sibling sign flip `akWm1pZO`
  - IS: `Sharpe -1.07`, `Fitness -0.33`, `Turnover 51.53%`, `Returns -4.99%`
  - TEST: `Sharpe -1.19`, `Fitness -0.30`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`

## Interpretation

- The 60-day baseline is directionally positive on IS, but it is far from a submit floor because Fitness is only `0.31` and concentration still fails.
- The sign-flip control confirms there is no hidden reverse edge; it simply mirrors the same weak profile.
- The 10-day sibling improves Sharpe slightly, but Fitness is still only `0.33` and concentration still fails.
- The family does not show a path where both Sharpe and Fitness improve together.

## Why Stop

- This is not a cheap repair candidate anymore.
- The remaining moves are mostly tenor / smoothing / cosmetic axis changes.
- The batch does not justify more budget when a different options source can be explored instead.

## Next Hop

- Rotate to `option_breakeven_30` as the next options-analytics source to try.
- Do not reopen `put_breakeven_60` with sign flips, lookbacks, smoothing, or group tweaks.

## Evidence

- `runs/field-search-packs/2026-04-25-put-breakeven-60.md`
- `runs/expression-families/2026-04-25-put-breakeven-60.md`
- `runs/simulation-captures/2026-04-25-put-breakeven-60-batch-01.json`

## Status

- `stop`
- `freeze`
- `rotate`

# 2026-04-25 Call Breakeven Family Stop Memo

## Decision

- Stop `call_breakeven_60` for the current budget.
- Freeze the family after the latest repair probes.
- Do not spend more time on cosmetic lookback, smoothing, or group-axis sweeps inside this lane.

## Why

- The best sector-rank repairs got the family close, but not over the fitness gate.
- `group_rank(ts_rank(call_breakeven_60 / close, 10), sector)` reached `Sharpe 1.92 / Fitness 0.88` with `LOW_SUB_UNIVERSE_SHARPE=PASS` and `CONCENTRATED_WEIGHT=PASS`, but still failed low fitness.
- `group_rank(ts_rank(ts_decay_linear(call_breakeven_60 / close, 2), 10), sector)` reached `Sharpe 1.85 / Fitness 0.89` with `LOW_SUB_UNIVERSE_SHARPE=PASS` and `CONCENTRATED_WEIGHT=PASS`, but still failed low fitness.
- The later mean-smoothing probe collapsed to `Sharpe 0.38 / Fitness 0.26`, so the lane is not heading toward a submit-ready shape.

## Evidence

- `runs/simulation-captures/2026-04-25-call-breakeven-family-batch-01.json`
- Live official alpha API results for:
  - `kqLp3jJz`
  - `A1OX3kKE`
  - `d5lJ08QJ`
  - `E5rnERG9`

## Next Hop

- Rotate to `put_breakeven_60` as the next family source.

## Status

- `stop`
- `freeze`
- `rotate`

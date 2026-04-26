# 2026-04-25 Volatility Spread Stop Memo

## Decision

- Stop `volatility-spread`.
- Freeze the family for the current budget.
- Do not reopen this lane with sign flips, lookbacks, smoothing, or group-axis polish.

## Why

- The first official batch did not clear a continuation floor.
- The sibling field reproduced the same weak IS/Test profile as the baseline.
- The sign-flip controls only mirrored the same edge in the opposite direction.
- That makes the lane a clean freeze rather than a repair candidate.

## Next Hop

- Rotate to `options / call_breakeven_60`.

## Status

- `stop`
- `freeze`
- `rotate`

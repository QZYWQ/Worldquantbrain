# 2026-04-25 Put Breakeven 60 Stop Memo

## Decision

- Stop `put_breakeven_60`.
- Freeze the family for the current budget.
- Do not reopen this lane for sign flips, lookbacks, smoothing, or group-axis polish.

## Why

- The baseline is only modestly positive on IS: `Sharpe 0.97` / `Fitness 0.31`, with `Turnover 47.62%` and a `CONCENTRATED_WEIGHT` failure.
- The sign-flip control mirrors the same weakness and turns negative on TEST.
- The 10-day sibling improves Sharpe only slightly to `1.07`, but Fitness remains `0.33` and concentration still fails.
- None of the four probes clears `LOW_SHARPE`, `LOW_FITNESS`, and `CONCENTRATED_WEIGHT` together.

## Evidence

- `runs/simulation-captures/2026-04-25-put-breakeven-60-batch-01.json`
- `runs/submission-memos/2026-04-25-put-breakeven-60-live-first-batch.md`
- Official Data Explorer pages:
  - `https://platform.worldquantbrain.com/data/data-fields/put_breakeven_60?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
  - `https://platform.worldquantbrain.com/data/data-fields/put_breakeven_10?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`

## Next Hop

- Rotate to `option_breakeven_30`.
- Do not return to `put_breakeven_60` unless a genuinely new structural idea appears.

## Status

- `stop`
- `freeze`
- `rotate`

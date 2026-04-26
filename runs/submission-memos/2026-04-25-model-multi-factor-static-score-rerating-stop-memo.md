# 2026-04-25 Model Multi-Factor Static Score Rerating Stop Memo

## Decision

- Stop `model_multi_factor_static_score_rerating`.
- Freeze the family for the current budget.
- Do not reopen this lane for more sign, lookback, smoothing, or grouping polish.

## Why

- The official batch is complete.
- The baseline is negative on IS and weak on test.
- The sign-flip control confirms direction but still misses the continuation floor by a wide margin.
- The time-rank and no-group controls both stay weak and do not open a new branch.

## Evidence

- `runs/simulation-captures/2026-04-25-model-multi-factor-static-score-rerating-batch-01.json`
- `runs/submission-memos/2026-04-25-model-multi-factor-static-score-rerating-live-first-batch.md`

## Next Step

- Rotate the next official budget to `multi_factor_acceleration_score_derivative`.
- Keep the current static-score lane frozen unless a genuinely new information source appears.

## Status

- `freeze`
- `rotate`

# 2026-04-25 Implied Volatility Skew Stop Memo

## Decision

- Stop `implied_volatility_skew`.
- Freeze the family for the current budget.
- Do not reopen this lane for tenor swaps, sign flips, smoothing, or group-axis tweaks.

## Why

- The tenor sweep peaks at `Sharpe 1.15` on `implied_volatility_mean_skew_20`, but the turnover is `102.90%`, which is too high for a durable next-step candidate.
- The lower-turnover siblings `60`, `90`, and `180` all stay in a weak band: `0.95`, `0.92`, and `0.80` test Sharpe.
- That ceiling/turnover tradeoff looks cosmetic, not like a genuinely new family advance.
- The baseline is positive, so sign-flip control is not the issue here.

## Evidence

- `runs/field-search-packs/2026-04-25-implied-volatility-skew.md`
- `runs/expression-families/2026-04-25-implied-volatility-skew.md`
- `runs/simulation-captures/2026-04-25-implied-volatility-skew-batch-01.json`
- `runs/submission-memos/2026-04-25-implied-volatility-skew-live-first-batch.md`

## Next Step

- Rotate to the `option4` open-interest / volatility-spread branch after fresh official field verification.

## Status

- `freeze`
- `rotate`

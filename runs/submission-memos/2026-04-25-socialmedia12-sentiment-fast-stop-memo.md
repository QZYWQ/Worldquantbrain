# 2026-04-25 Social Media Sentiment Fast Stop Memo

## Decision

- Stop `socialmedia12-sentiment-fast`.
- Freeze the family for the current budget.
- Do not launch the remaining lookback variants.

## Why

- The baseline `scl12_sentiment_fast_d1` is negative on IS: `Sharpe -0.51`, `Fitness -0.13`, `Turnover 76.02%`.
- The required sign-flip control `-scl12_sentiment_fast_d1` only gets to `Sharpe 0.51`, `Fitness 0.13`, and still fails `LOW_SHARPE`, `LOW_FITNESS`, `HIGH_TURNOVER`, and `CONCENTRATED_WEIGHT`.
- The sign-flip control also reverses to negative on test: `Sharpe -0.72`, `Fitness -0.17`.
- This is a low-ceiling lane; the leftover lookback variants would be cosmetic.

## Evidence

- `runs/field-search-packs/2026-04-25-socialmedia12-sentiment-fast.md`
- `runs/expression-families/2026-04-25-socialmedia12-sentiment-fast.md`
- `runs/simulation-captures/2026-04-25-socialmedia12-sentiment-fast-batch-01.json`
- `runs/submission-memos/2026-04-25-socialmedia12-sentiment-fast-live-first-batch.md`

## Next Hop

- Rotate to `socialmedia8 / snt_social_value` as the next genuinely different sentiment source.
- Do not reopen `socialmedia12` with sign flips, lookback swaps, smoothing, or group-axis tweaks.

## Status

- `freeze`
- `rotate`

# 2026-04-25 Social Media Sentiment Value Stop Memo

## Decision

- Stop `socialmedia8-sentiment-value`.
- Freeze the family for the current budget.
- Do not reopen this lane for sign flips, lookbacks, smoothing, or group-axis polish.

## Why

- The official field verification is solid, but the first official batch is not.
- `snt_social_value` is a direct `socialmedia8` matrix field with `86%` coverage and `100%` date coverage, yet the result is only modestly positive on IS and negative on TEST.
- IS: `Sharpe 0.37`, `Fitness 0.09`, `Turnover 26.81%`, `Returns 1.42%`, `Drawdown 4.50%`, `Margin 1.06‱`.
- TEST: `Sharpe -1.21`, `Fitness -0.45`, `Turnover 25.86%`, `Returns -3.50%`, `Drawdown 4.50%`, `Margin -2.71‱`.
- The year-by-year read also deteriorates into 2023, which argues against spending more budget on this lane.

## Evidence

- `runs/field-search-packs/2026-04-25-socialmedia8-sentiment-value.md`
- `runs/expression-families/2026-04-25-socialmedia8-sentiment-value.md`
- `runs/simulation-captures/2026-04-25-socialmedia8-sentiment-value-batch-01.json`
- `runs/submission-memos/2026-04-25-socialmedia8-sentiment-value-live-first-batch.md`

## Next Hop

- Rotate to `options / call_breakeven_60` as the next family source.
- Do not reopen `socialmedia8` by changing only sign, lookback, smoothing, or grouping.

## Status

- `stop`
- `freeze`
- `rotate`

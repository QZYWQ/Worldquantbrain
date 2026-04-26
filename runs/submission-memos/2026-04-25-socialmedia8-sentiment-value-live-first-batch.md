# 2026-04-25 Social Media Sentiment Value Live First Batch

## Decision

- Freeze `socialmedia8-sentiment-value` for the current budget.
- Do not launch the sign-flip or lookback variants.
- Rotate to the next family source instead of polishing this lane.

## Official Evidence

- Field search pack:
  - `runs/field-search-packs/2026-04-25-socialmedia8-sentiment-value.md`
- Expression family:
  - `runs/expression-families/2026-04-25-socialmedia8-sentiment-value.md`
- Simulation capture:
  - `runs/simulation-captures/2026-04-25-socialmedia8-sentiment-value-batch-01.json`

## Field Facts

- `snt_social_value`
  - dataset/category: `socialmedia8` / `Social Media Data for Equity`
  - `USA / TOP3000 / D1`
  - coverage `86%`
  - date coverage `100%`
  - type `MATRIX`
  - visible alphas `4,855`
- `snt_social_volume`
  - dataset/category: `socialmedia8` / `Social Media Data for Equity`
  - `USA / TOP3000 / D1`
  - coverage `86%`
  - date coverage `100%`
  - type `MATRIX`
  - visible alphas `4,788`

## Batch 01 Results

- Baseline `snt_social_value`
  - IS: `Sharpe 0.37`, `Fitness 0.09`, `Turnover 26.81%`, `Returns 1.42%`, `Drawdown 4.50%`, `Margin 1.06‱`
  - TEST: `Sharpe -1.21`, `Fitness -0.45`, `Turnover 25.86%`, `Returns -3.50%`, `Drawdown 4.50%`, `Margin -2.71‱`

## Why This Is A Stop

- The IS read is only modestly positive and still far below a comfortable continuation floor.
- The TEST read flips negative, which is a clear warning sign for this family.
- The year-by-year read deteriorates into 2023, so the lane does not look resilient enough to spend another batch on.
- The direct social-media value field is crowded enough that cosmetic sign/lookback tweaks are unlikely to justify more budget.

## Next Step

- Rotate to `options / call_breakeven_60` as the next family source.
- Do not reopen `socialmedia8` with sign flips, lookback swaps, smoothing, or group-axis tweaks.

## Status

- `freeze`
- `rotate`

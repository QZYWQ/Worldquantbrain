# 2026-04-25 Implied Volatility Skew Live First Batch

- Re-check time: `2026-04-25 15:05 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Simulate page plus official Data Explorer searches and project docs
- Scope: `implied_volatility_skew`
- Family: `implied_volatility_skew`

## Decision

- Freeze `implied_volatility_skew` for the current budget.
- Do not spend more budget on tenor swaps, sign flips, smoothing, or group-axis tweaks around this exact `option8` skew lane.
- Rotate the next official budget to a genuinely different options source.

## Official Evidence

- Field search pack:
  - `runs/field-search-packs/2026-04-25-implied-volatility-skew.md`
- Expression family:
  - `runs/expression-families/2026-04-25-implied-volatility-skew.md`
- Batch capture:
  - `runs/simulation-captures/2026-04-25-implied-volatility-skew-batch-01.json`

## Field Facts

- `implied_volatility_mean_skew_60`
  - dataset/category: `option8` / `Volatility Data`
  - `USA / TOP3000 / D1`
  - coverage `69%`
  - date coverage `100%`
  - type `MATRIX`
  - visible users `367`
  - visible alphas `935`
- `implied_volatility_mean_skew_20`
  - dataset/category: `option8` / `Volatility Data`
  - `USA / TOP3000 / D1`
  - coverage `69%`
  - date coverage `100%`
  - type `MATRIX`
  - visible alphas `669`
- `implied_volatility_mean_skew_90`
  - dataset/category: `option8` / `Volatility Data`
  - `USA / TOP3000 / D1`
  - coverage `69%`
  - date coverage `100%`
  - type `MATRIX`
  - visible alphas `1,376`
- `implied_volatility_mean_skew_180`
  - dataset/category: `option8` / `Volatility Data`
  - `USA / TOP3000 / D1`
  - coverage `69%`
  - date coverage `100%`
  - type `MATRIX`
  - visible alphas `975`

## Batch Result

- Baseline `group_rank(implied_volatility_mean_skew_60, industry)`
  - TEST Sharpe `0.95`
  - TEST Fitness `0.27`
  - TEST Turnover `58.53%`
  - TEST Returns `4.61%`
  - TEST Drawdown `2.65%`
  - TEST Margin `1.57‱`
- Variant 1 `group_rank(implied_volatility_mean_skew_20, industry)`
  - TEST Sharpe `1.15`
  - TEST Fitness `0.22`
  - TEST Turnover `102.90%`
  - TEST Returns `3.91%`
  - TEST Drawdown `2.13%`
  - TEST Margin `0.76‱`
- Variant 2 `group_rank(implied_volatility_mean_skew_90, industry)`
  - TEST Sharpe `0.92`
  - TEST Fitness `0.27`
  - TEST Turnover `55.02%`
  - TEST Returns `4.69%`
  - TEST Drawdown `3.55%`
  - TEST Margin `1.70‱`
- Variant 3 `group_rank(implied_volatility_mean_skew_180, industry)`
  - TEST Sharpe `0.80`
  - TEST Fitness `0.22`
  - TEST Turnover `51.31%`
  - TEST Returns `4.00%`
  - TEST Drawdown `4.10%`
  - TEST Margin `1.56‱`

## Why This Stops Here

- The tenor sweep tops out at `Sharpe 1.15` on the 20-day sibling, but that comes with `102.90%` turnover.
- The lower-turnover 60 / 90 / 180 day siblings all remain below a submit-ready floor, with Sharpe stepping down to `0.95`, `0.92`, and `0.80`.
- This is a tenor comparison around the same `option8` skew source, not a genuinely new family advance.
- Sign-flip control is not needed because the baseline is already positive.

## Next Minimal Experiment

- Rotate to the `option4` open-interest / volatility-spread branch after fresh official field verification.
- Keep the next batch minimal and do not reopen frozen model, analyst, cashflow, operating-income, or event-news lanes.

## Status

- Family state: `freeze`
- Portfolio posture: `rotate`
- Batch posture: `complete`

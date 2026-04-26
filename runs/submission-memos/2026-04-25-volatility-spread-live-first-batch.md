# 2026-04-25 Volatility Spread Live First Batch

## Decision

- Freeze `volatility-spread` for the current budget.
- Do not spend more time on sign flips, lookbacks, smoothing, or group-axis tweaks.
- Rotate to the next family source instead of polishing this lane.

## Official Evidence

- Field search pack:
  - `runs/field-search-packs/2026-04-25-volatility-spread.md`
- Expression family:
  - `runs/expression-families/2026-04-25-volatility-spread.md`
- Simulation capture:
  - `runs/simulation-captures/2026-04-25-volatility-spread-batch-01.json`

## Field Facts

- `mdl77_2400_rmi`
  - dataset/category: `Analysts' Factor Model` / `Technical Models`
  - `USA / TOP3000 / D1`
  - coverage `83%`
  - date coverage `100%`
  - type `MATRIX`
  - visible alphas `1`
- `implied_minus_realized_volatility_2`
  - dataset/category: `Analysts' Factor Model` / `Technical Models`
  - `USA / TOP3000 / D1`
  - coverage `97%`
  - date coverage `100%`
  - type `MATRIX`
  - visible alphas `11`

## Batch 01 Results

- Baseline `mdl77_2400_rmi`
  - IS: `Sharpe 0.31`, `Fitness 0.09`, `Turnover 23.70%`, `Returns 1.90%`, `Drawdown 17.32%`, `Margin 1.61‱`
  - TEST: `Sharpe 0.10`, `Fitness 0.02`, `Turnover 21.21%`, `Returns 0.62%`, `Drawdown 4.90%`, `Margin 0.59‱`
- Sign flip `-mdl77_2400_rmi`
  - IS: `Sharpe -0.31`, `Fitness -0.09`, `Turnover 23.70%`, `Returns -1.90%`, `Drawdown 21.74%`, `Margin -1.61‱`
  - TEST: `Sharpe -0.10`, `Fitness -0.02`, `Turnover 21.21%`, `Returns -0.62%`, `Drawdown 8.07%`, `Margin -0.59‱`
- Sibling field `implied_minus_realized_volatility_2`
  - IS: same as the baseline
  - TEST: same as the baseline
- Sibling sign flip `-implied_minus_realized_volatility_2`
  - IS: same as the sign-flip control
  - TEST: same as the sign-flip control

## Why This Is A Stop

- The baseline is weak on both IS and TEST, so there is no continuation floor to protect.
- The sibling field reproduces the same IS/Test profile, so it does not add a distinct edge.
- The sign-flip controls only mirror the same weakness in the opposite direction.
- That makes this lane a clean freeze instead of a candidate for cosmetic repair.

## Next Step

- Rotate to `options / call_breakeven_60` as the next family source.
- Do not reopen `volatility-spread` with sign flips, lookbacks, smoothing, or group-axis tweaks.

## Status

- `freeze`
- `rotate`

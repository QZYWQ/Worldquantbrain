# 2026-04-25 Option Breakeven 360 Live First Batch

## Decision

- Freeze `option_breakeven_360` for the current budget.
- Rotate to the next fresh source instead of polishing this slower options-consensus lane further.
- Do not reopen this family with sign flips, rank-window tweaking, smoothing, or group-axis tweaks.

## Official Evidence

- Field search pack: `runs/field-search-packs/2026-04-25-option-breakeven-360.md`
- Expression family: `runs/expression-families/2026-04-25-option-breakeven-360.md`
- Simulation capture: `runs/simulation-captures/2026-04-25-option-breakeven-360-batch-01.json`
- Official Data Explorer field page:
  - `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_360?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Official Data Explorer search page:
  - `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=option4&universe=TOP3000`

## Field Facts

- `option_breakeven_360`
  - dataset/category: `Options Analytics`
  - type: `Matrix`
  - coverage: `71%`
  - date coverage: `100%`
  - visible alphas: `373`

## Batch 01 Results

- Baseline `YPW3o6Gv`
  - Expression: `group_rank(ts_rank(option_breakeven_360 / close, 20), sector)`
  - IS: `Sharpe 1.04`, `Fitness 0.43`, `Turnover 33.83%`, `Returns 5.69%`
  - TEST: `Sharpe 1.58`, `Fitness 0.61`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Sign flip `P0XLm0q7`
  - Expression: `-group_rank(ts_rank(option_breakeven_360 / close, 20), sector)`
  - IS: `Sharpe -1.04`, `Fitness -0.43`, `Turnover 33.83%`, `Returns -5.69%`
  - TEST: `Sharpe -1.58`, `Fitness -0.61`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- 60d rank `e7qMZlzE`
  - Expression: `group_rank(ts_rank(option_breakeven_360 / close, 60), sector)`
  - IS: `Sharpe 1.12`, `Fitness 0.57`, `Turnover 23.03%`, `Returns 6.02%`
  - TEST: `Sharpe 1.94`, `Fitness 1.01`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- 5d mean smoothing `88KWxOpo`
  - Expression: `group_rank(ts_rank(ts_mean(option_breakeven_360 / close, 5), 20), sector)`
  - IS: `Sharpe 0.74`, `Fitness 0.28`, `Turnover 23.60%`, `Returns 3.49%`
  - TEST: `Sharpe 0.97`, `Fitness 0.35`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`

## Why Freeze

- The 30d baseline is already below the continuation floor on fitness and concentration.
- The 60d rank lowers turnover and improves sub-universe behavior, but it still fails the main IS floor.
- The only concentration-safe repair is the 5-day smoothing variant, and it collapses too far on Sharpe / Fitness to justify more budget.
- This is a clean freeze, not a near-pass.

## Next Step

- Rotate to `option4` open-interest / volatility-spread branch after fresh official field verification.
- Do not return to `option_breakeven_360` unless a genuinely new structural idea appears.

## Status

- `freeze`
- `rotate`

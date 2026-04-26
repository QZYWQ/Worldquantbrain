# 2026-04-25 Model Multi-Factor Acceleration Score Rerating Live First Batch

- Re-check time: `2026-04-25 13:05 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Simulate page plus alpha detail API from the logged-in browser session
- Scope: `model_multi_factor_acceleration_score_rerating`
- Family: `model_multi_factor_acceleration_score_rerating`

## Decision

- Freeze `model_multi_factor_acceleration_score_rerating` for the current budget.
- Do not spend more budget on sign flips, lookback tweaks, or grouping tweaks around this exact one-field lane.
- Rotate the next official budget away from the current Model acceleration branch.

## Official Evidence

- Field search pack:
  - `runs/field-search-packs/2026-04-25-model-multi-factor-acceleration-score-rerating.md`
- Expression family:
  - `runs/expression-families/2026-04-25-model-multi-factor-acceleration-score-rerating.md`

## Field Facts

- `multi_factor_acceleration_score_derivative`
  - dataset/category: `model16` / `Model > Valuation Models`
  - `USA / TOP3000 / D1`
  - coverage `1.0`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `106`
  - visible alphas `122`

## Batch Result

- Baseline `akW98lVR`
  - expression: `group_rank(multi_factor_acceleration_score_derivative, industry)`
  - IS Sharpe `-0.78`
  - Fitness `-0.52`
  - Turnover `0.1155`
  - Returns `-0.0561`
  - Test Sharpe `-0.14`
  - Test Fitness `-0.03`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Sign flip `xAmpoZ3J`
  - expression: `group_rank(-multi_factor_acceleration_score_derivative, industry)`
  - IS Sharpe `0.78`
  - Fitness `0.52`
  - Turnover `0.1155`
  - Returns `0.0561`
  - Test Sharpe `0.14`
  - Test Fitness `0.03`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- Time-rank control `RRkww7gj`
  - expression: `group_rank(ts_rank(multi_factor_acceleration_score_derivative, 20), industry)`
  - IS Sharpe `-0.77`
  - Fitness `-0.51`
  - Turnover `0.1226`
  - Returns `-0.0558`
  - Test Sharpe `-0.15`
  - Test Fitness `-0.04`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- No-group control `vRJXXgAb`
  - expression: `rank(multi_factor_acceleration_score_derivative)`
  - IS Sharpe `-0.76`
  - Fitness `-0.51`
  - Turnover `0.1155`
  - Returns `-0.0553`
  - Test Sharpe `-0.18`
  - Test Fitness `-0.05`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`

## Why This Stops Here

- The baseline is negative, and the mandatory sign control proves the direction but still stays far below the continuation floor.
- The sign-flipped line reaches only `Sharpe 0.78 / Fitness 0.52`, with `Test Sharpe 0.14 / Test Fitness 0.03`.
- The time-rank control and the no-group control both fall back to the same weak ceiling and do not create a new viable branch.
- That means more same-family budget would be cosmetic polishing, not a genuinely new family advance.

## Next Minimal Experiment

- If the Model lane is still worth exploring, the next branch should be a genuinely different field source rather than another tweak around this acceleration family.
- Good candidate next source: `sentiment` or another fresh category with full coverage and materially lower crowding than the current model family.

## Status

- Family state: `freeze`
- Portfolio posture: `rotate`
- Batch posture: `complete`

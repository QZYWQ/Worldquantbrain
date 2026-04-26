# 2026-04-25 Model Multi-Factor Static Score Rerating Live First Batch

- Re-check time: `2026-04-25 12:39 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Simulate page plus alpha detail API from the logged-in browser session
- Scope: `model_multi_factor_static_score_rerating`
- Family: `model_multi_factor_static_score_rerating`

## Decision

- Freeze `model_multi_factor_static_score_rerating` for the current budget.
- Do not spend more budget on sign flips, lookback tweaks, or grouping tweaks around this exact one-field lane.
- Rotate the next official budget to `multi_factor_acceleration_score_derivative` in the same Model category if the Model lane is still being explored.

## Official Evidence

- Field search pack:
  - `runs/field-search-packs/2026-04-25-model-multi-factor-static-score-rerating.md`
- Expression family:
  - `runs/expression-families/2026-04-25-model-multi-factor-static-score-rerating.md`

## Field Facts

- `multi_factor_static_score_derivative`
  - dataset/category: `model16` / `Model > Valuation Models`
  - `USA / TOP3000 / D1`
  - coverage `1.0`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `73`
  - visible alphas `86`
- `multi_factor_acceleration_score_derivative`
  - dataset/category: `model16` / `Model > Valuation Models`
  - `USA / TOP3000 / D1`
  - coverage `1.0`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `106`
  - visible alphas `122`

## Batch Result

- Baseline `1YnA0nYM`
  - expression: `group_rank(multi_factor_static_score_derivative, industry)`
  - IS Sharpe `-0.77`
  - Fitness `-0.51`
  - Turnover `0.1155`
  - Returns `-0.0558`
  - Test Sharpe `-0.12`
  - Test Fitness `-0.03`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Sign flip `akW9Gw91`
  - expression: `group_rank(-multi_factor_static_score_derivative, industry)`
  - IS Sharpe `0.77`
  - Fitness `0.51`
  - Turnover `0.1155`
  - Returns `0.0558`
  - Test Sharpe `0.12`
  - Test Fitness `0.03`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Time-rank control `xAmpEOkl`
  - expression: `group_rank(ts_rank(multi_factor_static_score_derivative, 20), industry)`
  - IS Sharpe `-0.76`
  - Fitness `-0.51`
  - Turnover `0.1227`
  - Returns `-0.0556`
  - Test Sharpe `-0.13`
  - Test Fitness `-0.03`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- No-group control `rKrMn5j9`
  - expression: `rank(multi_factor_static_score_derivative)`
  - IS Sharpe `-0.76`
  - Fitness `-0.50`
  - Turnover `0.1154`
  - Returns `-0.0551`
  - Test Sharpe `-0.16`
  - Test Fitness `-0.04`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`

## Why This Stops Here

- The baseline is negative, and the mandatory sign control proves the direction but still stays far below the continuation floor.
- The sign-flipped line reaches only `Sharpe 0.77 / Fitness 0.51`, with `Test Sharpe 0.12 / Test Fitness 0.03`.
- The time-rank control and the no-group control both fall back to the same weak ceiling and do not create a new viable branch.
- That means more same-family budget would be cosmetic polishing, not a genuinely new family advance.

## Next Minimal Experiment

- Rotate to `multi_factor_acceleration_score_derivative` next.
- Keep the next batch minimal:
  - baseline: `group_rank(multi_factor_acceleration_score_derivative, industry)`
  - variant 1: sign control
  - variant 2: time-rank stabilization
  - variant 3: no-group control
- If that lane also stalls, stop the Model lane rather than reopening the already frozen static-score branch.

## Status

- Family state: `freeze`
- Portfolio posture: `rotate`
- Batch posture: `complete`

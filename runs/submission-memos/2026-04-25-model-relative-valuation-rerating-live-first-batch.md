# 2026-04-25 Model Relative Valuation Rerating Live First Batch

- Re-check time: `2026-04-25 03:45:47 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Simulate page plus alpha detail API from the logged-in browser session
- Scope: `model_relative_valuation_rerating`
- Family: `model_relative_valuation_rerating`

## Decision

- Freeze this single-field `relative_valuation_rank_derivative` family for the current budget.
- Do not treat any line in this first batch as submit-ready or near-submit.
- Do not spend more budget on sign flips, lookback tweaks, or grouping tweaks around this exact one-field lane.
- Rotate the next official budget to the orthogonal analyst top-line guidance lane.

## Official Evidence

- Fresh official field re-check from `GET /data-fields`:
  - Field: `relative_valuation_rank_derivative`
  - Dataset/category: `model16` / `Model > Valuation Models`
  - `USA / TOP3000 / D1`: `coverage 1.0`, `date coverage 1.0`, `type MATRIX`
  - Visible crowding: `60` users / `77` alphas
- `A1O89XdX`
  - Simulation id: `2W01Es8IG4VEcqPyOb3Whtx`
  - Expression: `group_rank(relative_valuation_rank_derivative, industry)`
  - Stage / status / grade: `IS` / `UNSUBMITTED` / `INFERIOR`
  - IS summary: `Sharpe -0.76 / Fitness -0.51 / Turnover 11.40% / Returns -5.57%`
  - TEST summary: `Sharpe -0.14 / Fitness -0.03`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- `RRkwMlmo`
  - Simulation id: `1DM4HE9w34m491go34tiTdP`
  - Expression: `group_rank(-relative_valuation_rank_derivative, industry)`
  - Stage / status / grade: `IS` / `UNSUBMITTED` / `INFERIOR`
  - IS summary: `Sharpe 0.76 / Fitness 0.51 / Turnover 11.40% / Returns 5.57%`
  - TEST summary: `Sharpe 0.14 / Fitness 0.03`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- `npO59qmq`
  - Simulation id: `1mXl6ygfA4s49Yc12UxSZ13q`
  - Expression: `group_rank(ts_rank(relative_valuation_rank_derivative, 20), industry)`
  - Stage / status / grade: `IS` / `UNSUBMITTED` / `INFERIOR`
  - IS summary: `Sharpe -0.75 / Fitness -0.50 / Turnover 12.15% / Returns -5.54%`
  - TEST summary: `Sharpe -0.14 / Fitness -0.03`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- `9qAOYeZr`
  - Simulation id: `17armfexR4S79e411Z8Jw91m`
  - Expression: `rank(relative_valuation_rank_derivative)`
  - Stage / status / grade: `IS` / `UNSUBMITTED` / `INFERIOR`
  - IS summary: `Sharpe -0.75 / Fitness -0.50 / Turnover 11.40% / Returns -5.49%`
  - TEST summary: `Sharpe -0.18 / Fitness -0.05`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`

## Why This Stops Here

- The direct baseline is negative, and the mandatory sign control already established the correct sign.
- The sign-corrected line is still far below the visible continuation floor: `Sharpe 0.76 / Fitness 0.51`, with `LOW_SUB_UNIVERSE_SHARPE=FAIL`.
- The two small controls do not open a new branch:
  - `ts_rank(..., 20)` stays weak and negative.
  - removing industry grouping stays weak and negative.
- That means more same-family budget would mostly be banned pseudo-innovation: sign, lookback, or grouping polish around a one-field lane that already showed its ceiling.

## Next Minimal Experiment

- Rotate to the orthogonal analyst top-line guidance lane from the earlier scout:
  - `sales_max_guidance_value`
  - `sales_min_guidance_value`
  - `sales_estimate_average_annual`
- Keep the next batch minimal:
  - baseline: guidance midpoint versus annual sales consensus
  - variant 1: sign control
  - variant 2: guidance-band width versus consensus
  - variant 3: no-group control
- Do not reopen frozen EPS-close, cashflow/cap, operating-income, call-breakeven, or event/news-attention lanes.

## Status

- Current family: `freeze`
- Current posture: `rotate`
- Next source family: `analyst top-line guidance versus annual sales consensus`

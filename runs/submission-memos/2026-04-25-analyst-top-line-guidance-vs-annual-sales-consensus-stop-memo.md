# 2026-04-25 Analyst Top-Line Guidance vs Annual Sales Consensus Stop Memo

## Update

- `2026-04-25 05:35 CST (+0800)`:
  the official batch for this family is complete enough to stop.
- The raw midpoint-gap probe first returned a unit-verify warning and was replaced by the rank-normalized batch below.
- The family is now frozen for the current budget.

## Final Decision

- Freeze `analyst-top-line-guidance-vs-annual-sales-consensus`.
- Do not spend more budget on sign polish, lookback polish, smoothing, or group tweaks in this lane.
- Rotate the next official budget to the Model backup lane.

## Official Evidence

### Field facts

- `sales_max_guidance_value`
  - dataset/category: `analyst4` / `Analyst > Analyst Estimates`
  - `USA / TOP3000 / D1`
  - coverage `1.0`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `36`
  - visible alphas `38`
- `sales_min_guidance_value`
  - dataset/category: `analyst4` / `Analyst > Analyst Estimates`
  - `USA / TOP3000 / D1`
  - coverage `1.0`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `15`
  - visible alphas `18`
- `sales_estimate_average_annual`
  - dataset/category: `analyst4` / `Analyst > Analyst Estimates`
  - `USA / TOP3000 / D1`
  - coverage `1.0`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `43`
  - visible alphas `58`

### Batch result

- Baseline `kqL6eWKl`
  - expression: `0.5 * (rank(sales_max_guidance_value) + rank(sales_min_guidance_value)) - rank(sales_estimate_average_annual)`
  - IS Sharpe `-0.55`
  - Fitness `-0.32`
  - Turnover `0.0101`
  - Returns `-0.0416`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- Sign flip `N15lWXkw`
  - expression: `-1 * (0.5 * (rank(sales_max_guidance_value) + rank(sales_min_guidance_value)) - rank(sales_estimate_average_annual))`
  - IS Sharpe `0.55`
  - Fitness `0.32`
  - Turnover `0.0101`
  - Returns `0.0416`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Upper-edge control `om90wwWl`
  - expression: `rank(sales_max_guidance_value) - rank(sales_estimate_average_annual)`
  - IS Sharpe `-0.55`
  - Fitness `-0.31`
  - Turnover `0.0108`
  - Returns `-0.0409`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- Lower-edge control `leRP6K15`
  - expression: `rank(sales_min_guidance_value) - rank(sales_estimate_average_annual)`
  - IS Sharpe `-0.55`
  - Fitness `-0.32`
  - Turnover `0.0108`
  - Returns `-0.0416`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`

## Why This Stops Here

- The raw midpoint gap was unit-invalid, so the first step was already a warning that the naive version of this thesis does not live in a clean unit space.
- After rank-normalizing the fields, the best line was the sign-flipped control, but it still only reached Sharpe `0.55` / Fitness `0.32`.
- The one-sided gap controls fell back to the same weak ceiling and did not show any evidence that the band edges are meaningfully stronger than the midpoint.
- This is far below the continuation floor, so more same-family budget would just be cosmetic polishing.

## Next Minimal Experiment

- Rotate to `growth_potential_rank_derivative` first.
  - `model16` / `Model > Valuation Models`
  - `USA / TOP3000 / D1`
  - coverage `1.0`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `115`
  - visible alphas `133`
- If that lane stalls, fall back to `scl12_sentiment_fast_d1`.
  - `socialmedia12` / `Social Media`
  - coverage `0.9756`
  - date coverage `1.0`
  - type `MATRIX`
  - visible users `111`
  - visible alphas `125`

## Status

- Family state: `freeze`
- Portfolio posture: `rotate`
- Next lane: `growth_potential_rank_derivative`

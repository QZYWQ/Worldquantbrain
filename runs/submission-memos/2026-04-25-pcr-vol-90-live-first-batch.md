# 2026-04-25 PCR Vol 90 Live First Batch

## Decision

- Freeze `pcr_vol_90` for the current budget.
- Do not launch any cosmetic follow-ups inside this tenor sweep.
- Rotate to the next family source instead of polishing this lane.

## Official Evidence

- Field search pack: `runs/field-search-packs/2026-04-25-pcr-vol-90.md`
- Expression family: `runs/expression-families/2026-04-25-pcr-vol-90.md`
- Simulation capture: `runs/simulation-captures/2026-04-25-pcr-vol-90-batch-01.json`
- Official Data Explorer field pages:
  - `https://platform.worldquantbrain.com/data/data-fields/pcr_vol_90?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
  - `https://platform.worldquantbrain.com/data/data-fields/pcr_vol_20?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
  - `https://platform.worldquantbrain.com/data/data-fields/pcr_vol_60?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`

## Field Facts

- `pcr_vol_90`
  - dataset/category: `Options Analytics` / `Option Analytics`
  - `USA / D1 / TOP3000`
  - coverage `70%`
  - date coverage `100%`
  - type `Matrix`
  - visible alphas `181`
- `pcr_vol_20`
  - dataset/category: `Options Analytics` / `Option Analytics`
  - `USA / D1 / TOP3000`
  - coverage `70%`
  - date coverage `100%`
  - type `Matrix`
  - visible alphas `223`
- `pcr_vol_60`
  - dataset/category: `Options Analytics` / `Option Analytics`
  - `USA / D1 / TOP3000`
  - coverage `70%`
  - date coverage `100%`
  - type `Matrix`
  - visible alphas `238`

## Batch 01 Results

- pcr_vol_90_tsrank20_industry `58qKX001`
  - Expression: `group_rank(ts_rank(pcr_vol_90, 20), industry)`
  - IS: `Sharpe 0.64 / Fitness 0.13 / Turnover 57.76% / Returns 2.39% / Drawdown 6.02% / Margin 0.83‱`
  - TEST: `Sharpe 0.97 / Fitness 0.23 / Turnover 60.06% / Returns 3.50% / Drawdown 2.28% / Margin 1.17‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`
- pcr_vol_90_tsrank20_industry_sign_flip `zqJ7Vo6G`
  - Expression: `-group_rank(ts_rank(pcr_vol_90, 20), industry)`
  - IS: `Sharpe -0.64 / Fitness -0.13 / Turnover 57.76% / Returns -2.39% / Drawdown 14.08% / Margin -0.83‱`
  - TEST: `Sharpe -0.97 / Fitness -0.23 / Turnover 60.06% / Returns -3.50% / Drawdown 3.76% / Margin -1.17‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`
- pcr_vol_20_tsrank20_industry `O05d37wp`
  - Expression: `group_rank(ts_rank(pcr_vol_20, 20), industry)`
  - IS: `Sharpe 0.82 / Fitness 0.19 / Turnover 56.38% / Returns 3.16% / Drawdown 7.12% / Margin 1.12‱`
  - TEST: `Sharpe 1.39 / Fitness 0.40 / Turnover 58.72% / Returns 4.89% / Drawdown 3.23% / Margin 1.67‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`
- pcr_vol_60_tsrank20_industry `xAmLKnpJ`
  - Expression: `group_rank(ts_rank(pcr_vol_60, 20), industry)`
  - IS: `Sharpe 0.72 / Fitness 0.16 / Turnover 57.59% / Returns 2.74% / Drawdown 7.06% / Margin 0.95‱`
  - TEST: `Sharpe 1.44 / Fitness 0.42 / Turnover 59.88% / Returns 5.04% / Drawdown 2.25% / Margin 1.68‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`

## Why This Is A Stop

- The best IS control is still low-Fitness and the TEST card is not strong enough to justify another batch.
- The sign flip only mirrors the same weak edge rather than revealing a new branch.
- The 20d and 60d siblings do not rescue the family.

## Next Step

- Rotate to `pcr_oi_30` as the next direct options-tenor probe.
- Do not reopen `pcr_vol_90` with sign flips, lookback swaps, smoothing, or group-axis tweaks.

## Status

- `freeze`
- `rotate`

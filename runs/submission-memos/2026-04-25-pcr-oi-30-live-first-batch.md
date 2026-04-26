# 2026-04-25 PCR OI 30 Live First Batch

## Decision

- Freeze `pcr_oi_30` for the current budget.
- Do not launch any cosmetic follow-ups inside this tenor sweep.
- Rotate to the next family source instead of polishing this lane.

## Official Evidence

- Field search pack: `runs/field-search-packs/2026-04-25-pcr-oi-30.md`
- Expression family: `runs/expression-families/2026-04-25-pcr-oi-30.md`
- Simulation capture: `runs/simulation-captures/2026-04-25-pcr-oi-30-batch-01.json`
- Official Data Explorer field pages:
  - `https://platform.worldquantbrain.com/data/data-fields/pcr_oi_30?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
  - `https://platform.worldquantbrain.com/data/data-fields/pcr_oi_60?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
  - `https://platform.worldquantbrain.com/data/data-fields/pcr_oi_360?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`

## Field Facts

- `pcr_oi_30`
  - dataset/category: `Options Analytics` / `Option Analytics`
  - `USA / D1 / TOP3000`
  - coverage `71%`
  - date coverage `100%`
  - type `Matrix`
  - visible alphas `826`
- `pcr_oi_60`
  - dataset/category: `Options Analytics` / `Option Analytics`
  - `USA / D1 / TOP3000`
  - coverage `71%`
  - date coverage `100%`
  - type `Matrix`
  - visible alphas `907`
- `pcr_oi_360`
  - dataset/category: `Options Analytics` / `Option Analytics`
  - `USA / D1 / TOP3000`
  - coverage `71%`
  - date coverage `100%`
  - type `Matrix`
  - visible alphas `991`

## Batch 01 Results

- pcr_oi_30_tsrank20_industry `N15dxPEq`
  - Expression: `group_rank(ts_rank(pcr_oi_30, 20), industry)`
  - IS: `Sharpe 0.90 / Fitness 0.28 / Turnover 22.71% / Returns 2.21% / Drawdown 4.07% / Margin 1.95‱`
  - TEST: `Sharpe 0.39 / Fitness 0.08 / Turnover 22.66% / Returns 0.89% / Drawdown 2.82% / Margin 0.78‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`
- pcr_oi_30_tsrank20_industry_sign_flip `58qmxR6k`
  - Expression: `-group_rank(ts_rank(pcr_oi_30, 20), industry)`
  - IS: `Sharpe -0.90 / Fitness -0.28 / Turnover 22.71% / Returns -2.21% / Drawdown 12.39% / Margin -1.95‱`
  - TEST: `Sharpe -0.39 / Fitness -0.08 / Turnover 22.66% / Returns -0.89% / Drawdown 2.85% / Margin -0.78‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`
- pcr_oi_60_tsrank20_industry `gJol6AkQ`
  - Expression: `group_rank(ts_rank(pcr_oi_60, 20), industry)`
  - IS: `Sharpe 0.84 / Fitness 0.25 / Turnover 23.63% / Returns 2.09% / Drawdown 5.00% / Margin 1.77‱`
  - TEST: `Sharpe 0.37 / Fitness 0.07 / Turnover 23.59% / Returns 0.78% / Drawdown 3.44% / Margin 0.66‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`
- pcr_oi_360_tsrank20_industry `WjWZMwJx`
  - Expression: `group_rank(ts_rank(pcr_oi_360, 20), industry)`
  - IS: `Sharpe 0.60 / Fitness 0.16 / Turnover 20.84% / Returns 1.57% / Drawdown 3.02% / Margin 1.51‱`
  - TEST: `Sharpe -0.32 / Fitness -0.06 / Turnover 20.94% / Returns -0.65% / Drawdown 2.74% / Margin -0.63‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`

## Why This Is A Stop

- The baseline is only modestly positive on IS and still far below the continuation floor on TEST.
- The sign flip only mirrors the same weak edge, while the 360d sibling turns negative on TEST.
- The family does not show a durable continuation path.

## Next Step

- Rotate to `pcr_oi_720` after fresh official field verification.
- Do not reopen `pcr_oi_30` with sign flips, lookback swaps, smoothing, or group-axis tweaks.

## Status

- `freeze`
- `rotate`

# Current Incubation Summary

Snapshot timestamp: 2026-04-27T14:25:49+0800

This file is the compact first-read surface for fresh windows. Load this before the
full ledger or the longer bootstrap protocol when you only need the current truth.

## Current Truth

- Mode: multi-family-incubation
- Active main: none
- Active challenger: none
- Cold pool balance: 1
- Emergency reserve slots: 3
- Registry state counts: branch=2, hold=23, kill=5, incubate=3
- Progress status: idle
- Progress last verified feature: pv13_a_stage_top3
- LENS勘探完成 → pv13候选已完成A阶段（3/3通过，待B阶段）

## S-1 Scout Queue

- pv13 top-3 S-1 prescreen: 3/3 passed on 2026-04-27; S-1.5 dedupe cleared and S0 scan passed. A-stage sign-flip controls also passed on all three lines, so the family is now queued for B-stage shape exploration.

- `growth_potential_rank_derivative`: screened on 2026-04-27; cleared S-1 but failed the S0 continuation floor after the sign-flip control, so the lane did not open incubate.
- `mdl177_growthanalystmodel_qga_niroe_alt`: final profitability/value fallback; 100% coverage, 28 visible users, and 58 visible alphas at TOP3000, but `ts_rank(..., 20)` only reached `leQLXVle` with IS Sharpe `0.34` / Fitness `0.06` and TEST Sharpe `0.66` / Fitness `0.18`, so retire this lane.
- `cash_earnings_return_on_equity`: tested baseline and sign-flip; both weak, retire.
- `proforma_earnings_to_price`: sign-flip failed TEST, retire.
- `return_on_invested_capital_4`: raw baseline too weak, retire.
- The qfv4 scout batch was executed on 2026-04-27, all three candidates failed the simple S0 baseline, and the follow-up growth probe also failed S0 after the sign-flip control, so no new live probe is queued yet.

## A-Stage Incubate Lanes

- `pv13_custretsig_retsig`: stage `A`, state `incubate`, min depth `false`; baseline `ts_rank(pv13_custretsig_retsig, 60)` -> `O0b0Kr6q` (`IS 0.60 / TEST 0.77`, Fitness `0.40 / 0.53`, Turnover `63.97%`); sign flip `-ts_rank(pv13_custretsig_retsig, 60)` -> `WjajWKmd` (`IS -0.60 / TEST -0.77`, Fitness `-0.40 / -0.53`, Turnover `63.97%`); next step: B-stage from the original sign only.
- `pv13_ustomergraphrank_page_rank`: stage `A`, state `incubate`, min depth `false`; baseline `ts_rank(pv13_ustomergraphrank_page_rank, 120)` -> `e7d78nmO` (`IS 0.89 / TEST 0.99`, Fitness `1.60 / 1.72`, Turnover `3.83%`); sign flip `-ts_rank(pv13_ustomergraphrank_page_rank, 120)` -> `blolo7LN` (`IS -0.89 / TEST -0.99`, Fitness `-1.60 / -1.72`, Turnover `3.83%`); next step: B-stage from the original sign only.
- `pv13_com_page_rank`: stage `A`, state `incubate`, min depth `false`; baseline `ts_rank(pv13_com_page_rank, 120)` -> `pwVwondq` (`IS 0.78 / TEST 0.79`, Fitness `1.34 / 1.26`, Turnover `3.96%`); sign flip `-ts_rank(pv13_com_page_rank, 120)` -> `e7d7dzA6` (`IS -0.78 / TEST -0.79`, Fitness `-1.34 / -1.26`, Turnover `3.96%`); next step: B-stage from the original sign only.

## Held Incubation Lane

- `pcr_oi_720`: stage D, budget `D=0`, screen result `pass_s0`, min depth `false`, stop eligible `false`
- resurrection_priority: C (dormant until next orthogonal S0 pass)
- The E-stage repair sweep ended on hold; `3qn85MxQ` improved turnover but still failed `LOW_SHARPE` and `LOW_FITNESS`, and `ZYWOgoMY` remains the best repair candidate among the held line's tested variants.

## Closed or Held Lanes

- `call_breakeven_60`, `pcr_oi_30`, `pcr_vol_90`, and `socialmedia8` are held in incubation.
- `socialmedia12` is screen-killed and should stay in the scout pool.

## Fast Follow-Up References

1. `./runs/research-contracts/2026-04-27-a-stage-pv13-results.md`
2. `./runs/expression-families/2026-04-27-pv13-custretsig-retsig-a-stage.md`
3. `./runs/expression-families/2026-04-27-pv13-ustomergraphrank-page-rank-a-stage.md`
4. `./runs/expression-families/2026-04-27-pv13-com-page-rank-a-stage.md`
5. `./runs/research-contracts/2026-04-27-s0-pv13-results.md`
6. `./runs/research-contracts/2026-04-27-s1.5-pv13-dedupe-results.md`
7. `./runs/research-contracts/2026-04-27-s1-growth-potential-rerating-prescreen-results.md`
8. `./runs/research-queues/2026-04-27-s1-growth-potential-rerating-scout.md`
9. `./runs/research-queues/2026-04-27-frozen-pipeline.md`
10. `./runs/research-contracts/2026-04-27-mdl177-growthanalystmodel-qga-niroe-alt-prescreen-results.md`
11. `./runs/research-queues/2026-04-27-s1-profitability-value-scout.md`
12. `./runs/research-contracts/family-budget-ledger.json`

## Notes

- The file is intentionally compact so fresh windows can skip the full ledger until needed.
- Refresh it whenever the ledger, the active incubation lane, or the scout queue changes.
- `pcr_oi_720` is held, no longer active, and should not be treated as the next session starter.
- The pv13 relationship-data family just opened three incubate lanes; the continuation work now belongs in B stage.
- `min_depth_completed` remains `false` for the new pv13 lanes until the protocol's deeper-stage gate is reached.

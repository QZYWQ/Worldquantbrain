# Current Incubation Summary

Snapshot timestamp: 2026-04-27T12:46:15+0800

This file is the compact first-read surface for fresh windows. Load this before the
full ledger or the longer bootstrap protocol when you only need the current truth.

## Current Truth

- Mode: multi-family-incubation
- Active main: none
- Active challenger: none
- Cold pool balance: 1
- Emergency reserve slots: 3
- Registry state counts: branch=2, hold=23, kill=5
- Progress status: idle
- Progress last verified feature: growth_potential_rank_derivative
- LENS勘探完成 → pv13候选待进入S-1

## S-1 Scout Queue

- `growth_potential_rank_derivative`: screened on 2026-04-27; cleared S-1 but failed the S0 continuation floor after the sign-flip control, so the lane did not open incubate.
- `mdl177_growthanalystmodel_qga_niroe_alt`: final profitability/value fallback; 100% coverage, 28 visible users, and 58 visible alphas at TOP3000, but `ts_rank(..., 20)` only reached `leQLXVle` with IS Sharpe `0.34` / Fitness `0.06` and TEST Sharpe `0.66` / Fitness `0.18`, so retire this lane.
- `cash_earnings_return_on_equity`: tested baseline and sign-flip; both weak, retire.
- `proforma_earnings_to_price`: sign-flip failed TEST, retire.
- `return_on_invested_capital_4`: raw baseline too weak, retire.
- The qfv4 scout batch was executed on 2026-04-27, all three candidates failed the simple S0 baseline, and the follow-up growth probe also failed S0 after the sign-flip control, so no new live probe is queued yet.

## Held Incubation Lane

- `pcr_oi_720`: stage D, budget `D=0`, screen result `pass_s0`, min depth `false`, stop eligible `false`
- resurrection_priority: C (dormant until next orthogonal S0 pass)
- The E-stage repair sweep ended on hold; `3qn85MxQ` improved turnover but still failed `LOW_SHARPE` and `LOW_FITNESS`, and `ZYWOgoMY` remains the best repair candidate among the held line's tested variants.

## Closed or Held Lanes

- `call_breakeven_60`, `pcr_oi_30`, `pcr_vol_90`, and `socialmedia8` are held in incubation.
- `socialmedia12` is screen-killed and should stay in the scout pool.

## Fast Follow-Up References

1. `./runs/research-contracts/2026-04-27-s1-growth-potential-rerating-prescreen-results.md`
2. `./runs/research-queues/2026-04-27-s1-growth-potential-rerating-scout.md`
3. `./runs/research-queues/2026-04-27-frozen-pipeline.md`
4. `./runs/research-contracts/2026-04-27-mdl177-growthanalystmodel-qga-niroe-alt-prescreen-results.md`
5. `./runs/research-queues/2026-04-27-s1-profitability-value-scout.md`
6. `./runs/research-contracts/2026-04-27-cash-earnings-return-on-equity-prescreen-results.md`
7. `./runs/submission-memos/2026-04-27-proforma-earnings-to-price-signflip.md`
8. `./runs/research-contracts/2026-04-27-s1-profitability-value-prescreen-results.md`
9. `./runs/expression-families/2026-04-25-model-growth-potential-rerating.md`
10. `./runs/research-contracts/family-budget-ledger.json`

## Notes

- The file is intentionally compact so fresh windows can skip the full ledger until needed.
- Refresh it whenever the ledger, the active incubation lane, or the scout queue changes.
- `pcr_oi_720` is held, no longer active, and should not be treated as the next session starter.
- The profitability/value scout is closed after the `mdl177_growthanalystmodel_qga_niroe_alt` fallback stayed too weak, and the growth rerating follow-up also failed S0, so no new incubate lane opened.

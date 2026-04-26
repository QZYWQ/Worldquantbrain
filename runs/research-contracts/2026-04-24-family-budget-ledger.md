# Family Budget Ledger

## Decision

- Mode: single-active-line
- Main: none
- Challenger: none
- All other families: freeze or seal according to registry state
- Submit-ready families: 0

## Summary

- Families: 24
- Action counts: active-main=0, active-challenger=0, freeze=19, probe-only=0, seal=5
- Registry state counts: branch=2, explore=0, hold=17, kill=5, exploit=0

| family | registry state | budget action | priority | official outcomes | full gates | submit-ready | instruction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| actual_sales_delta_fundamental | hold | freeze | 2 | 4 | 0 | 0 | Freeze this family; the first actual-sales batch failed across baseline/sign/21d/126d, so do not allocate more budget here unless a genuinely new actual-sales field source appears. |
| fundamental_model_slow_ratio_equity_cap | hold | freeze | 2 | 14 | 4 | 0 | Freeze this family; the neutralization-axis probe failed to improve full-IS Sharpe/Fitness over the raw-ratio anchor, so do not allocate more budget here. |
| analyst_eps_sibling_qfv4_industry | hold | freeze | 2 | 3 | 0 | 0 | Freeze this family; qfv4 siblings underperform the annual-median control, so do not spend more budget on near-neighbor polishing. |
| analyst_disagreement_dts_spe_industry | hold | freeze | 2 | 6 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| analyst_eps_price_industry | branch | freeze | 2 | 4 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| event_option_volume_gate | hold | freeze | 2 | 4 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| event_trigger_low_turnover_volume_gate | hold | freeze | 2 | 1 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| fundamental_model_slow_ratio_cashflow | branch | freeze | 2 | 4 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| news_attention_qcm_branch | hold | freeze | 2 | 1 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| news_attention_qcm_vecavg_63d_branch | hold | freeze | 2 | 1 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| news_attention_relevance_63d_branch | hold | freeze | 2 | 1 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| operating_income_delta | hold | freeze | 2 | 4 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| operating_income_history_position | hold | freeze | 2 | 8 | 0 | 0 | Freeze this family; the live API check on Gr37elr0 and the later ridge batches still fail holdout, so do not allocate more same-source budget unless a genuinely new information source appears. |
| operating_income_smoothed_history_position | hold | freeze | 2 | 14 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| revenue_smoothed_history_position | hold | freeze | 2 | 2 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| sales_delta_fundamental | hold | freeze | 2 | 8 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| sentiment_buzz_stability | hold | freeze | 2 | 8 | 0 | 0 | No new batches, no additional smoothing, and no fresh parameter search unless the active lines fail first. |
| fundamental_model_slow_ratio | hold | freeze | 2 | 0 | 0 | 0 | Freeze this family; the baseline fields are absent from the saved USA TOP3000 Data Explorer truth, so no legal probe remains under current constraints. |
| news_attention_bee_stability | hold | freeze | 2 | 0 | 0 | 0 | Freeze this family; the accessible news18 fields are VECTOR at 0.5 coverage and the lane is hard-excluded, so do not spend more budget here. |
| capital_structure_balance_sheet | kill | seal | 4 | 5 | 0 | 0 | Do not reopen unless a genuinely new information source appears. No parameter polishing, no close cousin branch. |
| event_trigger_low_turnover_volatility_gate | kill | seal | 4 | 8 | 0 | 0 | Do not reopen unless a genuinely new information source appears. No parameter polishing, no close cousin branch. |
| operating_income_sales_ratio | kill | seal | 4 | 4 | 0 | 0 | Do not reopen unless a genuinely new information source appears. No parameter polishing, no close cousin branch. |
| pcr_oi_all_industry_rank | kill | seal | 4 | 2 | 0 | 0 | Do not reopen unless a genuinely new information source appears. No parameter polishing, no close cousin branch. |
| price_volume_short_horizon | kill | seal | 4 | 3 | 0 | 0 | Do not reopen unless a genuinely new information source appears. No parameter polishing, no close cousin branch. |

## Notes

- `analyst_eps_sibling_qfv4_industry` is frozen because the annual-median control beat the qfv4 siblings on holdout.
- `fundamental_model_slow_ratio_equity_cap` is now frozen; the neutralization-axis probe improved the test card but not full-IS Sharpe/Fitness, so no active main remains.
- `fundamental_model_slow_ratio` is now frozen because its baseline fields are absent from the saved USA TOP3000 Data Explorer truth; there is no legal probe point left under the current constraints.
- `news_attention_bee_stability` is now frozen because the accessible news18 fields are all VECTOR at 0.5 coverage and the seed expander hard-excluded the lane.
- `runs/submission-memos/2026-04-24-live-official-recheck.md` keeps the registry in stop posture: `E5repQ81` is still `ACTV / 4 PENDING`, and `ZYWzZlgZ` / `VkYR9LvA` still have `SELF_CORRELATION=PENDING`.
- `actual_sales_delta_fundamental` froze after batch 01; `operating_income_history_position` is now frozen too after the live API check on `Gr37elr0` and the later ridge batches stayed TEST-negative. No active main remains inside the current registry.
- Every frozen family stays frozen until a genuinely new information source appears.
- `seal` families stay out of the budget loop unless a new thesis source appears.

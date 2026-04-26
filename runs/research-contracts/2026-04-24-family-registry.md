# Family Registry

## Scope

- Expression families: `runs/expression-families`
- Outcome memory: `runs/simulation-captures`, `runs/candidate-batches`, `harness/artifacts`

## Snapshot

- Families: 25
- State counts: branch=3, explore=0, hold=17, kill=5, exploit=0
- Submit-ready families: 0

| family | state | outcomes | full gates | submit-ready | reason |
| --- | --- | --- | --- | --- | --- |
| analyst_eps_price_industry | branch | 4 | 0 | 0 | candidate evidence is clean on the common subset, but full submission gates are still missing |
| analyst_eps_sibling_qfv4_industry | hold | 3 | 0 | 0 | candidate evidence is strong, but the qfv4 sibling line is frozen because the annual-median control outperforms it on holdout and there is no budget left for near-neighbor polishing |
| fundamental_model_slow_ratio_cashflow | branch | 4 | 0 | 0 | family docs explicitly keep this family in branch |
| actual_sales_delta_fundamental | hold | 4 | 0 | 0 | official actual-sales batch failed its first viability pass, so freeze this family and pivot the active main to operating_income_history_position |
| fundamental_model_slow_ratio_equity_cap | hold | 14 | 4 | 0 | candidate evidence is strong, but the neutralization-axis probe failed full-IS Sharpe/Fitness and the family is frozen for the current budget |
| fundamental_model_slow_ratio | hold | 0 | 0 | 0 | baseline fields are absent from the current saved Data Explorer truth, so the lane is frozen until a new field source or new family is authorized |
| news_attention_bee_stability | hold | 0 | 0 | 0 | accessible news fields are VECTOR at 0.5 coverage and the lane is hard-excluded, so the family is frozen until field readiness is closed |
| analyst_disagreement_dts_spe_industry | hold | 6 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| event_option_volume_gate | hold | 4 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| event_trigger_low_turnover_volume_gate | hold | 1 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| news_attention_qcm_branch | hold | 1 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| news_attention_qcm_vecavg_63d_branch | hold | 1 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| news_attention_relevance_63d_branch | hold | 1 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| operating_income_delta | hold | 4 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| operating_income_history_position | hold | 8 | 0 | 0 | official live API and ridge batches still fail holdout, so the family is frozen for the current budget |
| operating_income_smoothed_history_position | hold | 14 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| revenue_smoothed_history_position | hold | 2 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| sales_delta_fundamental | hold | 8 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| sentiment_buzz_stability | hold | 8 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| capital_structure_balance_sheet | kill | 5 | 0 | 0 | family docs explicitly kill this family |
| event_trigger_low_turnover_volatility_gate | kill | 8 | 0 | 0 | family docs explicitly kill this family |
| operating_income_sales_ratio | kill | 4 | 0 | 0 | family docs explicitly kill this family |
| pcr_oi_all_industry_rank | kill | 2 | 0 | 0 | family docs explicitly kill this family |
| price_volume_short_horizon | kill | 3 | 0 | 0 | family docs explicitly kill this family |
| actual_eps_value_close_industry | branch | 0 | 0 | 0 | official Data Explorer search found a fully covered, lower-crowding analyst4 actual-EPS matrix field; live simulation batch launched but readback is currently rate-limited |

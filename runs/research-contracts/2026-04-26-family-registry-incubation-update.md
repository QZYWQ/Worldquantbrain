# Family Registry Incubation Update

## Scope

- Legacy registry snapshot: `runs/research-contracts/2026-04-24-family-registry.md`
- Current registry truth used for state normalization: `runs/research-contracts/2026-04-24-family-registry.json`
- Reactivated families: `call_breakeven_60`, `pcr_oi_30`, `pcr_vol_90`, `socialmedia8`, `socialmedia12`

## Snapshot

- Families: 31
- State counts: branch=2, hold=23, kill=5, freeze=1, incubate=0, exploit=0
- Submit-ready families: 0

## Field Legend

- `incubation_stage`: `legacy_*` for pre-protocol families; `A` / `B` / `C` / `D` / `E` for protected incubation lanes at their current stage; `S0` for the screen-killed return-to-scout lane.
- `screen_result`: `legacy_reviewed`, `blocked_source`, `pending_capture`, `pass_s0`, `s0_recheck_pending`, or `screen_kill`.
- `min_depth_completed` and `stop_eligible` are heuristic protocol fields, not official platform metrics.
- `global_corr_risk_score` is a heuristic 0-1 risk estimate, not a platform score.
- `state` preserves the legacy registry labels from the source snapshot (`branch`, `hold`, `kill`, `freeze`); do not use that field alone to infer new go/kill semantics, because the incubation overlay lives in `incubation_stage`, `screen_result`, and `stop_eligible`.

## Snapshot Note

- The 2026-04-24 markdown snapshot still lags the current JSON registry for `actual_eps_value_close_industry`; this update follows the current JSON state (`freeze`) and keeps the stale markdown discrepancy noted here instead of copying it forward.

## Registry Table

| family | state | incubation_stage | screen_result | min_depth_completed | stop_eligible | overfit_risk | global_corr_risk_score | outcomes | full gates | submit-ready | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| analyst_eps_price_industry | branch | legacy_branch | legacy_reviewed | true | true | medium | 0.47 | 4 | 0 | 0 | candidate evidence is clean on the common subset, but full submission gates are still missing |
| analyst_eps_sibling_qfv4_industry | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 3 | 0 | 0 | candidate evidence is strong, but the qfv4 sibling line is now frozen because the annual-median control outperforms it on holdout and there is no budget left for near-neighbor polishing |
| fundamental_model_slow_ratio_cashflow | branch | legacy_branch | legacy_reviewed | true | true | medium | 0.47 | 4 | 0 | 0 | family docs explicitly keep this family in branch |
| actual_sales_delta_fundamental | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 4 | 0 | 0 | official actual-sales batch failed on baseline, sign inversion, 21d, and 126d controls, so freeze this family and pivot the active main to operating_income_history_position |
| fundamental_model_slow_ratio_equity_cap | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 14 | 4 | 0 | candidate evidence is strong, but the neutralization-axis probe failed full-IS Sharpe/Fitness and the family is frozen for the current budget |
| fundamental_model_slow_ratio | hold | legacy_hold | blocked_source | false | false | high | 0.84 | 0 | 0 | 0 | baseline fields are absent from the current saved Data Explorer truth, so the lane is frozen until a new field source or new family is authorized |
| news_attention_bee_stability | hold | legacy_hold | blocked_source | false | false | high | 0.84 | 0 | 0 | 0 | accessible news fields are VECTOR at 0.5 coverage and the lane is hard-excluded, so the family is frozen until field readiness is closed |
| analyst_disagreement_dts_spe_industry | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 6 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| event_option_volume_gate | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 4 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| event_trigger_low_turnover_volume_gate | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 1 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| news_attention_qcm_branch | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 1 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| news_attention_qcm_vecavg_63d_branch | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 1 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| news_attention_relevance_63d_branch | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 1 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| operating_income_delta | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 4 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| operating_income_history_position | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 8 | 0 | 0 | official live API and ridge batches still fail holdout, so freeze this family for the current budget |
| operating_income_smoothed_history_position | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 14 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| revenue_smoothed_history_position | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 2 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| sales_delta_fundamental | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 8 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| sentiment_buzz_stability | hold | legacy_hold | legacy_reviewed | true | true | medium-high | 0.63 | 8 | 0 | 0 | official evidence exists but no submit-ready outcome is recorded |
| capital_structure_balance_sheet | kill | legacy_kill | legacy_reviewed | true | true | high | 0.86 | 5 | 0 | 0 | family docs explicitly kill this family |
| event_trigger_low_turnover_volatility_gate | kill | legacy_kill | legacy_reviewed | true | true | high | 0.86 | 8 | 0 | 0 | family docs explicitly kill this family |
| operating_income_sales_ratio | kill | legacy_kill | legacy_reviewed | true | true | high | 0.86 | 4 | 0 | 0 | family docs explicitly kill this family |
| pcr_oi_all_industry_rank | kill | legacy_kill | legacy_reviewed | true | true | high | 0.86 | 2 | 0 | 0 | family docs explicitly kill this family |
| price_volume_short_horizon | kill | legacy_kill | legacy_reviewed | true | true | high | 0.86 | 3 | 0 | 0 | family docs explicitly kill this family |
| actual_eps_value_close_industry | freeze | legacy_freeze | legacy_reviewed | true | true | medium | 0.72 | 4 | 0 | 0 | live baseline and 120d controls are self-correlated to existing alpha d5l07rpX; sign flip is a hard reject; quarterly alias is weaker and still pending; no submission path remains under the current budget |
| call_breakeven_60 | hold | D | pass_s0 | false | false | medium-high | 0.54 | 15 | 0 | 0 | The C-stage hybrid cleared the floor, but the D-stage delay-0 scan is blocked on this account; hold the family and reclaim the remaining budget to cold_pool. |
| pcr_oi_30 | hold | B | pass_s0 | false | false | medium-high | 0.58 | 6 | 0 | 0 | Both protected B-stage probes failed the TEST floor, so the lane should not receive more same-source budget. |
| pcr_vol_90 | hold | D | pass_s0 | false | false | medium-high | 0.61 | 7 | 0 | 0 | The C-stage hybrid clears TEST, but the D-stage delay-0 scan is blocked on this account, so hold the lane and reclaim the remaining budget to cold_pool. |
| socialmedia8 | hold | D | pass_s0 | false | false | high | 0.68 | 4 | 0 | 0 | The C-stage hybrid clears TEST, but the D-stage delay-0 scan is blocked on this account, so hold the lane and reclaim the remaining budget to cold_pool. |
| socialmedia12 | hold | S0 | screen_kill | false | false | high | 0.74 | 2 | 0 | 0 | The S0 recheck stayed negative on the official Simulate page; screen-kill the lane, return it to the scout pool, and keep it out of the incubation pool. |
| pcr_oi_720 | hold | D | pass_s0 | false | false | medium | 0.52 | 12 | 0 | 0 | The 60d analyst-estimate hybrid won the C-stage batch, but the D-stage delay-0 scan is blocked on this account, so hold the lane and reclaim the remaining budget to cold_pool. |

## Locked / Reference Anchors

- `qMmpvp8v`: locked submitted alpha, OS monitoring only, not part of the incubation pool.
- `E5repQ81`: locked reference alpha, OS unresolved, not part of the incubation pool.

## Notes

- `pcr_oi_720` sign-flip control on 2026-04-26: IS Sharpe 0.07 / Fitness 0.01 and TEST Sharpe -0.14 / Fitness -0.02, so keep the original ts_rank direction as the B-stage base.
- The new incubation state machine is an additive middle layer; it does not weaken the existing front-door gate or sign-flip discipline.
- `screen_kill` is reserved for S-1 / S0 pure-noise exits and is not the same thing as a permanent stop memo.
- `pcr_oi_720` B-stage comparison on 2026-04-26: `signed_power(ts_rank(pcr_oi_720, 20), 2)` cleared the B floor on TEST (0.43 / 0.08), while the 60-window sibling and both ts_zscore fallbacks failed; the lane then moved into C-stage cross-field follow-up.
- The cold pool released 0.5 units to `pcr_oi_720` under the 50% cap, leaving 0.5 in reserve.
- C-stage simulations on the orthogonal analyst-estimate field `anl4_af_eps_value` completed on 20d / 60d / 120d horizons, and the 60d variant won the batch with TEST Sharpe 0.99 / Fitness 0.37.
- D-stage delay-0 attempt returned `Attempted to use unknown variable "pcr_oi_720".` The lane is now held and the remaining budget should be reclaimed to cold_pool.
- E-stage repair sweep on 2026-04-26 found `3qn8XVVX` as the best repaired candidate (`IS Sharpe 1.35 / Fitness 0.77`, `TEST Sharpe 1.30 / Fitness 0.66`); `CONCENTRATED_WEIGHT` and `LOW_SHARPE` pass, but `LOW_FITNESS` and `LOW_SUB_UNIVERSE_SHARPE` still fail, so the lane remains on hold.
- Neutralization scan `LLl0X852` (`neutralization=SUBINDUSTRY`, `truncation=0.05`) underperformed the held Industry variant: `IS Sharpe 1.22 / Fitness 0.62`, `TEST Sharpe 1.13 / Fitness 0.51`; `LOW_SHARPE FAIL`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`.
- Sector scan `VkYANndb` (`neutralization=SECTOR`, `truncation=0.05`) matched the held Industry baseline almost exactly: `IS Sharpe 1.35 / Fitness 0.77`, `TEST Sharpe 1.30 / Fitness 0.66`; `LOW_SHARPE PASS`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`.
- E-stage repair sweep on 2026-04-26 found `3qn8XVVX` as the best repaired candidate (`IS Sharpe 1.35 / Fitness 0.77`, `TEST Sharpe 1.30 / Fitness 0.66`); `CONCENTRATED_WEIGHT` and `LOW_SHARPE` pass, but `LOW_FITNESS` and `LOW_SUB_UNIVERSE_SHARPE` still fail, so the lane remains on hold.
- Neutralization scan `LLl0X852` (`neutralization=SUBINDUSTRY`, `truncation=0.05`) underperformed the held Industry variant: `IS Sharpe 1.22 / Fitness 0.62`, `TEST Sharpe 1.13 / Fitness 0.51`; `LOW_SHARPE FAIL`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`.
- Sector scan `VkYANndb` (`neutralization=SECTOR`, `truncation=0.05`) matched the held Industry variant almost exactly: `IS Sharpe 1.35 / Fitness 0.77`, `TEST Sharpe 1.30 / Fitness 0.66`; `LOW_SHARPE PASS`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`.
- E-stage review on the same winner (`KPwW3LGN`) read back `test Sharpe 0.99 / Fitness 0.37` and the submission check failed on `LOW_FITNESS` plus `CONCENTRATED_WEIGHT`; `SELF_CORRELATION` remains pending in the API readback. The lane stays on hold and its remaining budget was reclaimed to cold_pool.
- E-stage repair sweep on 2026-04-26 found `E5r9KlYr` as the best repaired candidate (`IS Sharpe 1.34 / Fitness 0.63`, `TEST Sharpe 1.43 / Fitness 0.67`); `CONCENTRATED_WEIGHT` and `LOW_SHARPE` pass, but `LOW_FITNESS` and `LOW_SUB_UNIVERSE_SHARPE` still fail, so the lane remains on hold.
- E-stage industry/decay-6 repair on 2026-04-26 found `ZYWOgoMY` as the current best candidate (`IS Sharpe 1.36 / Fitness 0.80`, `TEST Sharpe 1.24 / Fitness 0.60`); `LOW_SUB_UNIVERSE_SHARPE PASS`, but `LOW_FITNESS` still fails, so the lane remains on hold.
- Final E-stage gating repair on 2026-04-26: `trade_when(ts_delta(close, 10) > 0, ...)` produced `3qn85MxQ` with `IS Sharpe 0.87 / Fitness 0.44` and `TEST Sharpe 1.23 / Fitness 0.69`; it still failed `LOW_SHARPE` and `LOW_FITNESS` while `LOW_SUB_UNIVERSE_SHARPE` stayed PASS. The one-arg `hump(...)` fallback `leRoGzNn` was negative and discarded. The lane remains on hold; no S-1 trigger was needed.

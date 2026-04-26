# Incubation Reactivation Plan

## Goal

Reopen the five retired / borderline lanes through the protected incubation layer so each family can reach minimum depth before any permanent stop memo is written.

## Priority Order

1. `call_breakeven_60`
2. `pcr_oi_30`
3. `pcr_vol_90`
4. `socialmedia8`
5. `socialmedia12`

## Current Session Queue

- Active family: none. `call_breakeven_60`, `pcr_oi_30`, `pcr_vol_90`, and `socialmedia8` are held; `socialmedia12` stays screen-killed and out of the incubate pool.
- No incubate follow-ons remain in queue; use the appendix scout candidates (`anl4_af_eps_value`, `option_breakeven_30`) for any new source work. `pcr_oi_720` is the active incubate lane and is now at C stage.
- Do not run any new incubate B family until a fresh scout or approval path is explicitly authorized.

## Family Plans

### call_breakeven_60

- screen_result: `pass_s0`
- min_depth_completed: `false`
- stop_eligible: `false`
- missing-depth evidence: The C-stage cross-field hybrid cleared the TEST floor, but the D-stage delay-0 scan is blocked because `call_breakeven_60` is unknown at delay 0 on this account.
- decision: Hold after the D-stage block; reclaim the remaining budget to `cold_pool`.
- C-stage result: `group_rank(ts_rank(signed_power(ts_zscore(call_breakeven_60 / close, 20), 2), 20) + ts_rank(pcr_oi_30, 20), industry)` with TEST `Sharpe 0.92 / Fitness 0.24` and IS `Sharpe 0.94 / Fitness 0.30`.
- D-stage result: delay-0 attempt failed with `Attempted to use unknown variable "call_breakeven_60".` No valid delay curve could be recorded from the current UI.
- budget cap: B:3, C:1, D:0, E:0

### pcr_oi_30

- screen_result: `pass_s0`
- min_depth_completed: `false`
- stop_eligible: `false`
- missing-depth evidence: The baseline and both protected B-stage shape probes (mean-5 and decay-3) all failed the TEST floor, so the lane is now held under the current budget.
- decision: Hold after B-stage failure; rotate to `pcr_vol_90`.
- first B actions: `group_rank(ts_rank(ts_mean(pcr_oi_30, 5), 20), industry)` / `group_rank(ts_rank(ts_decay_linear(pcr_oi_30, 3), 20), industry)`
- B-stage note: mean-5 and decay-3 both produced weak TEST summaries (`Sharpe 0.03 / Fitness 0.00` and `Sharpe 0.17 / Fitness 0.02` respectively), so there is no continuation path inside this source under the current budget.
- budget cap: B:2, C:1, D:1, E:1

### pcr_vol_90

- screen_result: `pass_s0`
- min_depth_completed: `false`
- stop_eligible: `false`
- missing-depth evidence: The C-stage cross-field hybrid clears TEST, but the only available delay-0 follow-up is blocked on this account because `pcr_vol_90` is unknown at delay 0.
- decision: C-stage hybrid passed, but the D-stage delay-0 scan is blocked; hold the lane and reclaim the remaining budget to `cold_pool`.
- B-stage results: mean-5 TEST `Sharpe 0.48 / Fitness 0.08`; decay-3 TEST `Sharpe 1.42 / Fitness 0.30`.
- C-stage result: `group_rank(ts_rank(ts_decay_linear(pcr_vol_90, 3), 20) + ts_rank(pcr_oi_30, 20), industry)` with TEST `Sharpe 1.27 / Fitness 0.29` and IS `Sharpe 0.21 / Fitness 0.02`.
- D-stage result: delay-0 attempt failed with `Attempted to use unknown variable "pcr_vol_90"`; no valid delay curve could be recorded from the current UI.
- budget cap: B:0, C:0, D:0, E:0

### socialmedia8

- screen_result: `pass_s0`
- min_depth_completed: `false`
- stop_eligible: `false`
- missing-depth evidence: The C-stage hybrid clears TEST, but the D-stage delay-0 scan is blocked because `pcr_oi_30` is unknown at delay 0 on this account.
- decision: Hold after the D-stage block; reclaim the remaining budget to `cold_pool`.
- first B actions: `group_rank(ts_rank(ts_mean(snt_social_value, 5), 20), industry)` / `group_rank(ts_rank(ts_zscore(snt_social_value, 20), 20), industry)`
- B-stage note: mean-5 failed TEST (`Sharpe -0.51 / Fitness -0.11`), while zscore20 passed TEST (`Sharpe 0.86 / Fitness 0.21`), so only the zscore20 lane should carry forward.
- C-stage result: `group_rank(ts_rank(ts_zscore(snt_social_value, 20), 20) + ts_rank(pcr_oi_30, 20), industry)` with TEST `Sharpe 1.14 / Fitness 0.31` and IS `Sharpe 0.01 / Fitness 0.00`.
- D-stage note: delay-0 attempt hit `Attempted to use unknown variable "pcr_oi_30"`, so no valid delay curve could be completed from the current UI.
- next D action: delay-0 scan is blocked; the family is now held and should not spend more budget under the current cycle.
- budget cap: B:0, C:0, D:0, E:0

### socialmedia12

- screen_result: `screen_kill`
- min_depth_completed: `false`
- stop_eligible: `false`
- missing-depth evidence: The S0 recheck stayed negative on the official page, and the prior batch01 sign-flip control already failed, so the lane is pure noise under the current cycle.
- decision: Screen-kill the lane, return it to the scout pool, and do not write a permanent stop memo.
- first B actions: none; the lane does not get deeper budget after a screen-kill.
- budget cap: 0.


## Appendix: New Source Scout Candidates

- `anl4_af_eps_value` -> route through `S-1 -> S0` only; use the cross-sectional snapshot prescreen and do not run a full backtest at the scouting step.
- `option_breakeven_30` -> route through `S-1 -> S0` only; keep the prescreen light and treat crowding as a first-order concern.
- `pcr_oi_720` -> active incubate family in the current session; current stage is C.

## Notes

- `qMmpvp8v` and `E5repQ81` remain locked / reference anchors only and are not part of the incubation pool.
- `socialmedia12` was screen-killed after the S0 recheck stayed negative; it returned to the scout pool and is not a permanent stop memo.
- The plan assumes the new protocol governs stop eligibility, budget release, and sign-flip discipline; it does not weaken the existing front-door gate. `pcr_oi_720` has now moved past the scout-only appendix and into protected incubation; current stage is C.

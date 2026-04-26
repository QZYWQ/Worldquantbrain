# 2026-04-26 Call Breakeven 60 D-Stage Delay-0 Blocked / Hold

## Decision

- Hold `call_breakeven_60`.
- Reclaim the remaining budget to `cold_pool`.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.
- The D-stage delay-0 scan is blocked because `call_breakeven_60` is unknown at delay 0 on this account.

## Official Evidence

- `runs/simulation-captures/2026-04-26-call-breakeven-60-industry-signed-power20-pcr-oi-hybrid-batch-07.json`
- `runs/simulation-captures/2026-04-26-call-breakeven-60-delay0-blocked-batch-08.json`

## C-Stage Result

- Expression: `group_rank(ts_rank(signed_power(ts_zscore(call_breakeven_60 / close, 20), 2), 20) + ts_rank(pcr_oi_30, 20), industry)`
- TEST Sharpe `0.92` / Fitness `0.24`
- IS Sharpe `0.94` / Fitness `0.30`
- Check Submission and Submit Alpha remained disabled.

## D-Stage Result

- Delay-0 attempt expression: `group_rank(ts_rank(signed_power(ts_zscore(call_breakeven_60 / close, 20), 2), 20) + ts_rank(pcr_oi_30, 20), industry)`
- Official error: `Attempted to use unknown variable "call_breakeven_60".`
- Delay 2 was rejected as a non-legal option on this account.
- No valid delay curve could be recorded from the current UI.

## Conclusion

- The C-stage hybrid is real, but the D-stage delay path is not valid on this account.
- Hold the family under the current cycle and move to `pcr_oi_30` as the next eligible incubate family.
- No permanent stop memo is warranted because `min_depth_completed` remains `false`.

## Next Hop

- Start `pcr_oi_30` B-stage work next.

## Status

- `hold`
- `reclaim`

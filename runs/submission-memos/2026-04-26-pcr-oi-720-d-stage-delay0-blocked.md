# 2026-04-26 pcr_oi_720 D-Stage Delay-0 Blocked / Hold

## Decision

- Hold `pcr_oi_720`.
- Reclaim the remaining budget to `cold_pool`.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.
- The D-stage delay-0 scan is blocked because `pcr_oi_720` is unknown at delay 0 on this account.

## Official Evidence

- `runs/submission-memos/2026-04-26-pcr-oi-720-c-stage-hybrid.md`
- `runs/simulation-captures/2026-04-26-pcr-oi-720-c-stage-anl4-af-eps-batch-01.json`
- `runs/simulation-captures/2026-04-26-pcr-oi-720-d-stage-delay0-blocked-batch-02.json`

## D-Stage Result

- Delay-0 attempt expression: `group_rank(ts_rank(signed_power(ts_rank(pcr_oi_720, 20), 2), 20) + ts_rank(anl4_af_eps_value / close, 60), industry)`
- Official error: `Attempted to use unknown variable "pcr_oi_720".`
- No official metrics were produced.
- `Check Submission` and `Submit Alpha` remained disabled.

## Conclusion

- The C-stage hybrid is real, but the D-stage delay-0 route is not valid on this account.
- Hold the family under the current cycle rather than pushing deeper without a valid delay-capable path.
- No permanent stop memo is warranted because `min_depth_completed` remains `false`.

## Next Hop

- Keep the family in hold and return to the scout queue if a genuinely new source needs to be incubated.

## Status

- `hold`
- `reclaim`

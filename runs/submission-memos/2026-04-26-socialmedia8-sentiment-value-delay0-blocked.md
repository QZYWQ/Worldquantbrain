# 2026-04-26 Social Media Sentiment Value Delay-0 Blocked / Hold

## Decision

- Hold `socialmedia8`.
- Reclaim the remaining budget to `cold_pool`.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.
- The D-stage delay-0 scan is blocked because `pcr_oi_30` is unknown at delay 0 on this account.

## Official Evidence

- `runs/submission-memos/2026-04-26-socialmedia8-sentiment-value-c-stage-hybrid.md`
- `runs/simulation-captures/2026-04-26-socialmedia8-sentiment-value-industry-pcr-oi-hybrid-batch-04.json`
- `runs/simulation-captures/2026-04-26-socialmedia8-sentiment-value-delay0-blocked-batch-05.json`

## D-Stage Result

- Delay-0 attempt expression: `group_rank(ts_rank(ts_zscore(snt_social_value, 20), 20) + ts_rank(pcr_oi_30, 20), industry)`
- Official error: `Attempted to use unknown variable "pcr_oi_30".`
- The results pane stayed blank; no official metrics were produced.
- `Check Submission` and `Submit Alpha` remained disabled.

## Conclusion

- The C-stage hybrid is real, but the D-stage delay-0 route is not valid on this account.
- Hold the family under the current cycle rather than pushing deeper without a valid delay-valid path.
- No permanent stop memo is warranted because `min_depth_completed` remains `false`.

## Next Hop

- Move to `socialmedia12` as the next eligible incubate family.

## Status

- `hold`
- `reclaim`

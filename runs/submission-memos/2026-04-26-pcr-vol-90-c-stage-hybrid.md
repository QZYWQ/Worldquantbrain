# 2026-04-26 PCR Vol 90 C-Stage Hybrid Review

## Decision

- Advance `pcr_vol_90` to D stage.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.
- Use the C-stage hybrid as the branch lead and run the delay-0 robustness scan next.

## Official Evidence

- `runs/submission-memos/2026-04-25-pcr-vol-90-live-first-batch.md`
- `runs/submission-memos/2026-04-25-pcr-vol-90-stop-memo.md`
- `runs/submission-memos/2026-04-26-pcr-vol-90-b-stage-advance.md`
- `runs/simulation-captures/2026-04-26-pcr-vol-90-industry-mean5-batch-02.json`
- `runs/simulation-captures/2026-04-26-pcr-vol-90-industry-decay3-batch-03.json`
- `runs/simulation-captures/2026-04-26-pcr-vol-90-industry-pcr-oi-hybrid-batch-04.json`

## C-Stage Results

- Cross-field hybrid `group_rank(ts_rank(ts_decay_linear(pcr_vol_90, 3), 20) + ts_rank(pcr_oi_30, 20), industry)`
  - TEST: `Sharpe 1.27 / Fitness 0.29 / Turnover 51.82% / Returns 2.78% / Drawdown 1.87% / Margin 1.07‱`
  - TRAIN / IS summary: `Sharpe 0.21 / Fitness 0.02 / Turnover 49.05% / Returns 0.52% / Drawdown 6.35% / Margin 0.21‱`
- The live page still showed `Needs Improvement` and both submission buttons remained disabled.
- When the settings modal was checked on the live platform, the delay dropdown exposed only `0` and `1` on this account.

## Conclusion

- The C-stage hybrid is a real continuation: it clears the C TEST floor, but the IS read is too weak to stop here.
- Delay robustness is still required before any E-stage review.
- No permanent stop memo is warranted because `min_depth_completed` remains `false`.

## Next Hop

- Run a delay-0 simulation of the same C-stage expression to record the D-stage comparison.

## Status

- `advance`
- `continue`

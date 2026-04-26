# 2026-04-26 PCR OI 30 B-Stage Hold

## Decision

- Hold `pcr_oi_30` for the current budget.
- Reclaim the protected B-stage budget to `cold_pool`.
- Do not spend any more same-source budget on tenor or smoothing tweaks inside this lane.

## Official Evidence

- `runs/submission-memos/2026-04-25-pcr-oi-30-live-first-batch.md`
- `runs/submission-memos/2026-04-25-pcr-oi-30-stop-memo.md`
- `runs/simulation-captures/2026-04-26-pcr-oi-30-industry-mean5-batch-02.json`
- `runs/simulation-captures/2026-04-26-pcr-oi-30-industry-decay3-batch-03.json`

## B-Stage Results

- Mean-5 repair `group_rank(ts_rank(ts_mean(pcr_oi_30, 5), 20), industry)`
  - TEST: `Sharpe 0.03 / Fitness 0.00 / Turnover 19.60% / Returns 0.05% / Drawdown 2.34% / Margin 0.05‱`
  - TRAIN / IS summary: `Sharpe 0.06 / Fitness 0.00 / Turnover 20.37% / Returns 0.14% / Drawdown 5.96% / Margin 0.13‱`
- Decay-3 repair `group_rank(ts_rank(ts_decay_linear(pcr_oi_30, 3), 20), industry)`
  - TEST: `Sharpe 0.17 / Fitness 0.02 / Turnover 25.06% / Returns 0.34% / Drawdown 2.00% / Margin 0.27‱`
  - TRAIN / IS summary: `Sharpe 0.18 / Fitness 0.02 / Turnover 23.50% / Returns 0.38% / Drawdown 7.05% / Margin 0.33‱`

## Conclusion

- Both B-stage probes are below the TEST floor.
- The decay-3 variant is a little better than mean-5, but it still does not justify more same-source budget.
- The lane should rotate away rather than continue polishing the same options-tenor source.

## Next Hop

- Move to `pcr_vol_90` as the next eligible family.
- Keep the same protected incubation discipline: one B-stage pair first, then decide whether the lane deserves C.

## Status

- `hold`
- `freeze`
- `rotate`

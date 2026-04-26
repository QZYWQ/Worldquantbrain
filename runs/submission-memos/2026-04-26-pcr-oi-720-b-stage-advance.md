# 2026-04-26 pcr_oi_720 B-Stage Advance

## Decision

- Advance `pcr_oi_720` to C stage.
- Keep `min_depth_completed` at `false` and `stop_eligible` at `false`.
- Use `signed_power(ts_rank(pcr_oi_720, 20), 2)` as the branch lead for the next stage.

## Official Evidence

- `runs/submission-memos/2026-04-26-pcr-oi-720-a-stage-signflip.md`
- `runs/simulation-captures/2026-04-26-pcr-oi-720-b-stage-window60-fallback-batch-01.json`

## B-Stage Results

- Leader: `signed_power(ts_rank(pcr_oi_720, 20), 2)`
  - IS: `Sharpe -0.12 / Fitness -0.01`
  - TEST: `Sharpe 0.43 / Fitness 0.08`
- 60-window sibling: `signed_power(ts_rank(pcr_oi_720, 60), 2)`
  - IS: `Sharpe 0.12 / Fitness 0.02`
  - TEST: `Sharpe 0.08 / Fitness 0.01`
- `zscore_power` is not available on this account, so the zscore branches used `ts_zscore` fallbacks.
- zscore20 fallback: `signed_power(ts_zscore(ts_rank(pcr_oi_720, 20), 20), 2)`
  - IS: `Sharpe -0.02 / Fitness -0.00`
  - TEST: `Sharpe -1.05 / Fitness -0.26`
- 60-window zscore fallback: `signed_power(ts_zscore(ts_rank(pcr_oi_720, 60), 60), 2)`
  - IS: `Sharpe -0.19 / Fitness -0.03 / Turnover 24.31% / Returns -0.55% / Drawdown 4.71% / Margin -0.46‱`
  - TEST: `Sharpe -0.07 / Fitness -0.01 / Turnover 26.24% / Returns -0.18% / Drawdown 2.63% / Margin -0.14‱`

## Conclusion

- `signed_power(ts_rank(pcr_oi_720, 20), 2)` is the only B-stage branch that clears the TEST floor.
- The 60-window sibling is weaker, and both zscore repairs fail the continuation floor.
- `harness/lib/multi_test_correction.R` is absent locally, so the comparison is manual.
- Advance the lane to C-stage cross-field hybridization from the 20-window signed-power winner.

## Next Hop

- Start a one-axis C-stage cross-field hybrid from `signed_power(ts_rank(pcr_oi_720, 20), 2)`.
- Keep the branch interpretable and avoid touching delay or extra smoothing levers yet.

## Status

- `advance`
- `continue`

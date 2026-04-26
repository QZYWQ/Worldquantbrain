# 2026-04-26 Social Media Sentiment Value C-Stage Hybrid Review

## Decision

- Advance `socialmedia8` to D stage.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.
- Use the C-stage hybrid as the branch lead and run the delay-0 robustness scan next.

## Official Evidence

- `runs/submission-memos/2026-04-25-socialmedia8-sentiment-value-live-first-batch.md`
- `runs/submission-memos/2026-04-25-socialmedia8-sentiment-value-stop-memo.md`
- `runs/submission-memos/2026-04-26-socialmedia8-sentiment-value-b-stage-advance.md`
- `runs/simulation-captures/2026-04-26-socialmedia8-sentiment-value-industry-mean5-batch-02.json`
- `runs/simulation-captures/2026-04-26-socialmedia8-sentiment-value-industry-zscore20-batch-03.json`
- `runs/simulation-captures/2026-04-26-socialmedia8-sentiment-value-industry-pcr-oi-hybrid-batch-04.json`

## C-Stage Results

- Cross-field hybrid `group_rank(ts_rank(ts_zscore(snt_social_value, 20), 20) + ts_rank(pcr_oi_30, 20), industry)`
  - TEST: `Sharpe 1.14 / Fitness 0.31 / Turnover 30.19% / Returns 2.26% / Drawdown 1.72% / Margin 1.50‱`
  - TRAIN / IS summary: `Sharpe 0.01 / Fitness 0.00 / Turnover 28.59% / Returns 0.03% / Drawdown 6.11% / Margin 0.02‱`
- The live page stayed UNSUBMITTED / anonymous and both submission buttons remained disabled.
- The hybrid clears the C continuation floor on TEST, but IS is still too weak to stop here.

## Conclusion

- The C-stage hybrid is a real continuation: it clears the C TEST floor, but the IS read is too weak to stop here.
- Delay robustness is still required before any E-stage review.
- No permanent stop memo is warranted because `min_depth_completed` remains `false`.

## Next Hop

- Run a delay-0 simulation of the same C-stage expression to record the D-stage comparison.

## Status

- `advance`
- `continue`

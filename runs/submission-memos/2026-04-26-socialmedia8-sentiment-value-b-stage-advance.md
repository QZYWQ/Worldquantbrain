# 2026-04-26 Social Media Sentiment Value B-Stage Advance

## Decision

- Advance `socialmedia8` to C stage.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.
- Use the zscore20 survivor as the branch lead.

## Official Evidence

- `runs/submission-memos/2026-04-25-socialmedia8-sentiment-value-live-first-batch.md`
- `runs/submission-memos/2026-04-25-socialmedia8-sentiment-value-stop-memo.md`
- `runs/simulation-captures/2026-04-26-socialmedia8-sentiment-value-industry-mean5-batch-02.json`
- `runs/simulation-captures/2026-04-26-socialmedia8-sentiment-value-industry-zscore20-batch-03.json`

## B-Stage Results

- Mean-5 repair `group_rank(ts_rank(ts_mean(snt_social_value, 5), 20), industry)`
  - TEST: `Sharpe -0.51 / Fitness -0.11 / Turnover 24.75% / Returns -1.15% / Drawdown 2.63% / Margin -0.93‱`
  - TRAIN / IS summary: `Sharpe 0.43 / Fitness 0.09 / Turnover 25.33% / Returns 1.08% / Drawdown 4.50% / Margin 0.85‱`
- Zscore20 repair `group_rank(ts_rank(ts_zscore(snt_social_value, 20), 20), industry)`
  - TEST: `Sharpe 0.86 / Fitness 0.21 / Turnover 30.50% / Returns 1.84% / Drawdown 1.46% / Margin 1.21‱`
  - TRAIN / IS summary: `Sharpe -0.13 / Fitness -0.01 / Turnover 31.09% / Returns -0.32% / Drawdown 4.95% / Margin -0.20‱`

## Conclusion

- The mean-5 probe fails the B continuation floor.
- The zscore20 probe clears the B continuation floor and should carry the next protected C-stage hybrid.
- No permanent stop memo is warranted because `min_depth_completed` remains `false`.

## Next Hop

- Start a one-axis C-stage cross-field hybrid from the zscore20 survivor, using `pcr_oi_30` as the external-field companion.
- Do not freeze or kill the family; continue protected incubation.

## Status

- `advance`
- `continue`

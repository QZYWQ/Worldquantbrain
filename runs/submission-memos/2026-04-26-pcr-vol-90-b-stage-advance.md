# 2026-04-26 PCR Vol 90 B-Stage Advance

## Decision

- Advance `pcr_vol_90` to C stage.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.
- Use the decay-3 survivor as the branch lead.

## Official Evidence

- `runs/submission-memos/2026-04-25-pcr-vol-90-live-first-batch.md`
- `runs/submission-memos/2026-04-25-pcr-vol-90-stop-memo.md`
- `runs/simulation-captures/2026-04-26-pcr-vol-90-industry-mean5-batch-02.json`
- `runs/simulation-captures/2026-04-26-pcr-vol-90-industry-decay3-batch-03.json`

## B-Stage Results

- Mean-5 repair `group_rank(ts_rank(ts_mean(pcr_vol_90, 5), 20), industry)`
  - TEST: `Sharpe 0.48 / Fitness 0.08 / Turnover 37.25% / Returns 0.97% / Drawdown 2.43% / Margin 0.52‱`
  - TRAIN / IS summary: `Sharpe -0.60 / Fitness -0.12 / Turnover 37.26% / Returns -1.59% / Drawdown 6.24% / Margin -0.45‱`
- Decay-3 repair `group_rank(ts_rank(ts_decay_linear(pcr_vol_90, 3), 20), industry)`
  - TEST: `Sharpe 1.42 / Fitness 0.30 / Turnover 63.20% / Returns 2.87% / Drawdown 1.03% / Margin 0.91‱`
  - TRAIN / IS summary: `Sharpe -0.52 / Fitness -0.08 / Turnover 60.25% / Returns -1.34% / Drawdown 5.56% / Margin -0.45‱`

## Conclusion

- The mean-5 probe clears the B continuation floor but is weaker than the decay-3 sibling.
- The decay-3 probe is the clear branch lead and should carry the next protected C-stage hybrid.
- No permanent stop memo is warranted because `min_depth_completed` remains `false`.

## Next Hop

- Start a one-axis C-stage cross-field hybrid from the decay-3 survivor, using `pcr_oi_30` as the external-field companion.
- Do not freeze or kill the family; continue protected incubation.

## Status

- `advance`
- `continue`

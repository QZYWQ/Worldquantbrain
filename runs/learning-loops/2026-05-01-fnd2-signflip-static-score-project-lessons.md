# 2026-05-01 fnd2 Sign-Flip And Static-Score Project Lessons

## Context

This note records two bounded official rescue loops completed on 2026-05-01.

The objective was not to maximize headline Sharpe, but to decide whether either lane still deserved official budget after targeted repairs.

## Lesson 1: Sign Flip Can Reveal A Real Lane Without Making It Submit-Ready

Case:

```text
ts_corr(ts_zscore(fnd2_a_consinprogressg, 51), systematic_risk_last_90_days, 76)
```

Observed pattern:

- raw baseline had clearly negative Sharpe
- direct sign flip repaired the core IS metrics
- the lane then stalled mainly on `LOW_SUB_UNIVERSE_SHARPE`

What worked:

- `rank(-ts_corr(...))` improved the lane modestly:
  - Sub-universe from `0.47` to `0.51`
  - Sharpe and Fitness stayed above the floor

What failed:

- `group_rank(-ts_corr(...), industry)` fixed Sub-universe but destroyed Sharpe and Fitness

Carry-forward rule:

- After a negative baseline, direct sign-flip remains mandatory.
- If the direct sign-flip becomes a near-pass and only fails Sub-universe, test one light cross-sectional compression wrapper first.
- If a simple group-rank repair flips the core metrics negative, stop. The lane is not one grouping tweak away from viability.

## Lesson 2: Narrow Breadth Can Hide Behind Beautiful Headline Metrics

Case:

```text
group_neutralize(ts_zscore(multi_factor_static_score_derivative, 24), industry)
```

Observed pattern:

- raw official page showed very strong Sharpe and Fitness
- but yearly breadth collapsed to tiny counts and later to `0 / 0`
- all rescue variants remained tiny-name portfolios

Follow-up evidence:

- `group_rank(ts_zscore(...), industry)` became `1 long / 15 short` with `CONCENTRATED_WEIGHT 0.50 / 0.10`
- `group_neutralize(rank(ts_zscore(...)), industry)` stayed `1 long / 15 short` and still failed `CONCENTRATED_WEIGHT 0.20 / 0.10`

Carry-forward rule:

- If a candidate already shows very low long/short breadth or years with near-zero active names, do not trust headline Sharpe/Fitness.
- A ranking wrapper that preserves `1 long / 15 short` is not a rescue; it is proof of structural concentration.
- Once this pattern is confirmed officially, stop the family instead of trying more rank/group/truncation cosmetics.

## Practical Stop Rules Reinforced

1. Near-pass branches deserve targeted rescue.
2. Structural concentration branches do not.
3. Two rescue probes are enough when they isolate the main failing check and still confirm the same family ceiling.

## Related Official Memo

- `runs/submission-memos/2026-05-01-fnd2-signflip-and-static-score-rescue-stop.md`

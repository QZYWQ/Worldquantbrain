# 2026-04-26 S-1 Analyst QFV4 Scout Queue

## Context

- Session status is idle after the `pcr_oi_720` hold closeout.
- Scope: non-options, non-sentiment, fresh analyst sibling probe.
- The qfv4 sibling pair is the best remaining low-correlation analyst source in the current project history.

## Ranked Queue

| rank | name | recommendation | queue_score | summary | next_step |
| --- | --- | --- | --- | --- | --- |
| 1 | analyst_qfv4_median_level_sibling | prioritize | 26 | Strongest qfv4 sibling; official backup alpha `qMm6xPVv`, full coverage, lower crowding, best next probe outside the retired lane. | Simulate `group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)` with the standard 60d industry frame. |
| 2 | analyst_qfv4_mean_level_sibling | prioritize | 24 | Same source with mean aggregation; official backup alpha `QP59baMg`, clean backup if the median sibling is noisy. | Simulate `group_rank(ts_rank(anl4_qfv4_eps_mean/close, 60), industry)` with the same settings. |
| 3 | analyst_afv4_median_control | hold | 14 | Annual control only; useful for overlap testing, not the first spend. | Run only if the qfv4 pair stays weak or ambiguous. |
| 4 | analyst_eps_dispersion_disagreement | drop | 8 | Live recheck already failed low-sub-universe and negative IS. | Do not reopen without a genuinely new thesis. |

## Why This Queue

- It stays outside the options and sentiment families the user asked to avoid.
- It keeps the first spend focused on the two qfv4 siblings that already have the cleanest official evidence.
- It avoids reopening frozen model / volatility / top-line branches without fresh evidence.
- It gives the new window a simple next step instead of drifting back to the retired `pcr_oi_720` lane.

## Source Trace

- `runs/field-search-packs/analyst-sibling-search-pack.md`
- `runs/submission-memos/analyst-sibling-submission-memo.md`
- `runs/research-contracts/2026-04-24-family-registry.json`
- `runs/research-contracts/2026-04-26-family-registry-incubation-update.md`
- `api.worldquantbrain.com/alphas/qMm6xPVv`
- `api.worldquantbrain.com/alphas/QP59baMg`

## Next Action

- Open the qfv4 median sibling first.
- Keep the qfv4 mean sibling as the immediate backup.
- Treat the annual-median control as a comparator only.

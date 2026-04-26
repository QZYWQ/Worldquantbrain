# 2026-04-27 S-1 Growth Potential Rerating Scout Queue

## Context

- Session status: idle after the profitability/value closeout.
- The profitability/value lane has been exhausted through `mdl177_growthanalystmodel_qga_niroe_alt`.
- Source family doc: `runs/expression-families/2026-04-25-model-growth-potential-rerating.md`

## Prescreen Plan

- Baseline: `group_rank(growth_potential_rank_derivative, industry)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=industry`, `truncation=0.08`.
- Sign control: `group_rank(-growth_potential_rank_derivative, industry)`
- Time-rank control: `group_rank(ts_rank(growth_potential_rank_derivative, 20), industry)`
- No-group diagnostic: `rank(growth_potential_rank_derivative)`

## Risk Tags

- Turnover Risk: watch for bursty derivative refreshes.
- Coverage Risk: recheck live coverage before spending the first batch.
- Correlation Risk: compare against generic growth-model crowding, not the retired profitability/value lanes.

## Next Action

- Open the baseline first.
- Apply the mandatory sign control if the baseline turns negative.
- Keep the first pass simple; do not add smoothing before the sign read.

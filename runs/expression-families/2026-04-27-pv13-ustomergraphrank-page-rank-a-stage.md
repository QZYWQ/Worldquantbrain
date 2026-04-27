# PV13 Customer Graph Rank Page Rank A-Stage Family

## Metadata
- Date: 2026-04-27
- Topic: `pv13_ustomergraphrank_page_rank`
- Source domain: `pv13 (Relationship Data for Equity)`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Stage: `A`
- State: `incubate`
- min_depth_completed: `false` (protocol-gated until E-stage)

## Hypothesis
Relationship-graph state variables should lead the slower accounting / analyst families by reading operating structure directly from customer / competitor links.

## Baseline
- Expression: `ts_rank(pv13_ustomergraphrank_page_rank, 120)`
- Official alpha: `e7d78nmO`
- IS Sharpe / Fitness: `0.89 / 1.60`
- TEST Sharpe / Fitness: `0.99 / 1.72`
- Turnover: `3.83%`

## Sign-Flip Control
- Expression: `-ts_rank(pv13_ustomergraphrank_page_rank, 120)`
- Official alpha: `blolo7LN`
- IS Sharpe / Fitness: `-0.89 / -1.60`
- TEST Sharpe / Fitness: `-0.99 / -1.72`
- Turnover: `3.83%`

## A-Stage Decision
- `pv13_ustomergraphrank_page_rank`: PASS -> keep the original sign and move to B-stage shape exploration.
- The sign-flip control was decisively weaker, so do not spend any more budget on the flipped direction.
- `min_depth_completed` remains `false` per the incubation protocol; this lane is incubate, not minimum-depth-complete.

## Next Step
- Use the original expression only for B-stage follow-up.
- Prefer one-axis shape changes first; do not touch the source family identity yet.

## B-Stage Follow-up
- B best: `ts_rank(pv13_ustomergraphrank_page_rank, 150)` -> TEST `1.01`, Fitness `1.77`, Turnover `3.37%`.
- Structure control: `group_neutralize(ts_rank(pv13_ustomergraphrank_page_rank, 150), subindustry)` -> TEST `0.20`, Fitness `0.04`.
- Decision: A-stage anchor remains the current best; B improved modestly but not enough to promote.
- Observation: `ts_zscore` was dead, so the `ts_scale` direction stayed pruned.


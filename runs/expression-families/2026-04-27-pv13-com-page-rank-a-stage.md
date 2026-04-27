# PV13 Competitor Page Rank A-Stage Family

## Metadata
- Date: 2026-04-27
- Topic: `pv13_com_page_rank`
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
- Expression: `ts_rank(pv13_com_page_rank, 120)`
- Official alpha: `pwVwondq`
- IS Sharpe / Fitness: `0.78 / 1.34`
- TEST Sharpe / Fitness: `0.79 / 1.26`
- Turnover: `3.96%`

## Sign-Flip Control
- Expression: `-ts_rank(pv13_com_page_rank, 120)`
- Official alpha: `e7d7dzA6`
- IS Sharpe / Fitness: `-0.78 / -1.34`
- TEST Sharpe / Fitness: `-0.79 / -1.26`
- Turnover: `3.96%`

## A-Stage Decision
- `pv13_com_page_rank`: PASS -> keep the original sign and move to B-stage shape exploration.
- The sign-flip control was decisively weaker, so do not spend any more budget on the flipped direction.
- `min_depth_completed` remains `false` per the incubation protocol; this lane is incubate, not minimum-depth-complete.

## Next Step
- Use the original expression only for B-stage follow-up.
- Prefer one-axis shape changes first; do not touch the source family identity yet.

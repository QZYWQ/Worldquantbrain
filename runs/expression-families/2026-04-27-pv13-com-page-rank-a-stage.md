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

## B-Stage Follow-up
- B best: `ts_rank(pv13_com_page_rank, 150)` -> TEST `0.79`, Fitness `1.26`, Turnover `3.40%`.
- Structure control: `group_neutralize(ts_rank(pv13_com_page_rank, 150), subindustry)` -> TEST `-0.61`, Fitness `-0.22`.
- Decision: A-stage anchor remains the current best; B only matched TEST / Fitness and shaved a little turnover.
- Observation: `ts_zscore` was dead, so the `ts_scale` direction stayed pruned.

## C-Stage Follow-up
- Hybrid companion: `pv13_ustomergraphrank_page_rank`
- Best C hybrid: `group_rank(0.7 * ts_rank(pv13_ustomergraphrank_page_rank, 150) + 0.3 * ts_rank(pv13_com_page_rank, 150), industry)` -> TEST `0.99`, Fitness `1.72`, Turnover `2.12%`
- Decision: hold; the competitor lane helped shape the hybrid, but the combined expression still did not surpass the customer-centrality anchor.
- Observation: the competitor rank remains a useful secondary ingredient, not a replacement for the stronger customer PageRank anchor.
## D/E Follow-up
- E-stage check: HOLD.
  - `ts_rank(pv13_com_page_rank, 150)` -> `zqPqm9xO` (`IS 0.77 / TEST 0.79`, Fitness `1.32 / 1.26`, Turnover `3.58%`) failed `LOW_SHARPE` and `LOW_SUB_UNIVERSE_SHARPE`.
- Decision: do not spend rescue budget on the weaker secondary lane.

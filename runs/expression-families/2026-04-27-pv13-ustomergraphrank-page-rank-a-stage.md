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

## C-Stage Follow-up
- Hybrid companion: `pv13_com_page_rank`
- Best C hybrid: `group_rank(0.7 * ts_rank(pv13_ustomergraphrank_page_rank, 150) + 0.3 * ts_rank(pv13_com_page_rank, 150), industry)` -> TEST `0.99`, Fitness `1.72`, Turnover `2.12%`
- Decision: hold; the weighted hybrid cleaned up turnover, but it still did not beat the A-stage anchor.
- Observation: same-domain hybridization helped efficiency more than raw edge, so keep the original customer PageRank anchor as the working best.
## D/E Follow-up
- D-stage field check: PASS. `pv13_ustomergraphrank_page_rank` is reachable in Data Explorer as a Matrix on USA / TOP3000 with delay 1, 79% coverage, and 900 visible alphas.
- E-stage submission gate: HOLD after two repairs.
  - `ts_rank(pv13_ustomergraphrank_page_rank, 150)` -> `mLrL87Yx` (`IS 0.89 / TEST 1.01`, Fitness `1.61 / 1.77`, Turnover `3.55%`) failed `LOW_SHARPE` and `LOW_SUB_UNIVERSE_SHARPE`.
  - `ts_rank(pv13_ustomergraphrank_page_rank, 180)` -> `blolJAAr` (`IS 0.90 / TEST 1.03`, Fitness `1.63 / 1.82`, Turnover `3.14%`) still failed `LOW_SHARPE`.
  - `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 180), industry)` -> `JjgjWwwA` (`IS 0.86 / TEST 0.99`, Fitness `1.53 / 1.73`, Turnover `2.04%`) fixed sub-universe but still failed `LOW_SHARPE`.
- Decision: hold. `min_depth_completed` stays `false`.

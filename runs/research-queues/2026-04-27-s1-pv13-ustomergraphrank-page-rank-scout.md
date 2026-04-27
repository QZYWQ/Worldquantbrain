# S-1 Scout: pv13_ustomergraphrank_page_rank

## 字段信息
- 字段名: `pv13_ustomergraphrank_page_rank`
- 来源域: `pv13` (Relationship Data for Equity)
- 类型: `MATRIX`
- 覆盖率: `79.06%`
- 日期覆盖率: `—`
- 用户数/Alpha数: `578 / 890`
- 简要描述: the PageRank of customers
- Official trace: `api.worldquantbrain.com/data-fields/pv13_ustomergraphrank_page_rank`

## S-1 预筛目标
- Distinctness ≥ 0.60
- Signal Presence ≥ 0.40
- 无额外 bump（非 options/social）

## S-1 结果
- Distinctness: `0.88` — customer/competitor graph topology stays well outside the failed analyst / profitability / model source family.
- Signal Presence: `0.71` — Customer network centrality is still orthogonal to the failed analyst/profitability/model families, but visible crowding is lighter and coverage is lower.
- Verdict: `PASS`
- Next step: `S-1: PASS → 进入 S-1.5 去重检查 → S0`

## Notes
- Source trace: `runs/research-contracts/2026-04-27-lens-pv13-field-recon.md`
- Field inventory source: `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
- No simulation was run for this step.

## S-1.5 Dedupe
- Candidate baselines `ts_rank(pv13_ustomergraphrank_page_rank, 20/60/120)` all passed the local dedupe gate.
- Exact / normalized duplicates: none.
- Strongest historical match score: 0.5 (ts_rank(group_rank(total_assets_amount / cap, industry), 63) @ 2026-04-23-fundamental-model-slow-ratio-equity-cap-batch-10).
- Structural warning threshold (0.7): not reached.
- Verdict: PASS -> proceed to S0.

## S0 结果
| Decay | Neut | Alpha | IS Sharpe | IS Fitness | TEST Sharpe | TEST Fitness | Turnover | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | MARKET | `Vk2kwjX0` | 0.80 | 0.43 | -0.37 | -0.13 | 9.75% | FAIL |
| 20 | NONE | `58a8NKrX` | 0.90 | 1.64 | 0.99 | 1.71 | 11.29% | PASS |
| 60 | MARKET | `qMPMvQlj` | 0.22 | 0.06 | -1.16 | -0.72 | 5.33% | FAIL |
| 60 | NONE | `om3mA10b` | 0.89 | 1.60 | 0.96 | 1.62 | 6.17% | PASS |
| 120 | MARKET | `RR2RZN0o` | 0.03 | 0.00 | -0.71 | -0.31 | 3.69% | FAIL |
| 120 | NONE | `e7d78nmO` | 0.89 | 1.60 | 0.99 | 1.72 | 3.83% | PASS |

- Best combo: Decay=120, Neut=NONE (TEST Sharpe 0.99, Fitness 1.72).
- Sign-flip control: not required; the best TEST combo is already positive on IS and TEST.
- S0: PASS -> enter A-stage incubation.

# S-1 Scout: pv13_com_page_rank

## 字段信息
- 字段名: `pv13_com_page_rank`
- 来源域: `pv13` (Relationship Data for Equity)
- 类型: `MATRIX`
- 覆盖率: `89.66%`
- 日期覆盖率: `—`
- 用户数/Alpha数: `1090 / 1914`
- 简要描述: the PageRank of competitors
- Official trace: `api.worldquantbrain.com/data-fields/pv13_com_page_rank`

## S-1 预筛目标
- Distinctness ≥ 0.60
- Signal Presence ≥ 0.40
- 无额外 bump（非 options/social）

## S-1 结果
- Distinctness: `0.90` — customer/competitor graph topology stays well outside the failed analyst / profitability / model source family.
- Signal Presence: `0.82` — Competitor network centrality gives a structurally different view of operating state with strong coverage and visible alpha usage.
- Verdict: `PASS`
- Next step: `S-1: PASS → 进入 S-1.5 去重检查 → S0`

## Notes
- Source trace: `runs/research-contracts/2026-04-27-lens-pv13-field-recon.md`
- Field inventory source: `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
- No simulation was run for this step.

## S-1.5 Dedupe
- Candidate baselines `ts_rank(pv13_com_page_rank, 20/60/120)` all passed the local dedupe gate.
- Exact / normalized duplicates: none.
- Strongest historical match score: 0.5 (ts_rank(group_rank(cashflow / cap, industry), 90) @ 2026-04-23-fundamental-model-slow-ratio-cashflow-cap-industry-batch-01).
- Structural warning threshold (0.7): not reached.
- Verdict: PASS -> proceed to S0.

## S0 结果
| Decay | Neut | Alpha | IS Sharpe | IS Fitness | TEST Sharpe | TEST Fitness | Turnover | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | MARKET | `akAk20MO` | 0.58 | 0.27 | -1.25 | -0.76 | 9.79% | FAIL |
| 20 | NONE | `O0b0wRJv` | 0.82 | 1.44 | 0.77 | 1.20 | 11.49% | PASS |
| 60 | MARKET | `pwVworE3` | 0.20 | 0.06 | -1.26 | -0.80 | 5.39% | FAIL |
| 60 | NONE | `d5E5gEXw` | 0.82 | 1.44 | 0.77 | 1.20 | 6.49% | PASS |
| 120 | MARKET | `rKJKE7wJ` | -0.23 | -0.07 | -1.26 | -0.78 | 3.76% | FAIL |
| 120 | NONE | `pwVwondq` | 0.78 | 1.34 | 0.79 | 1.26 | 3.96% | PASS |

- Best combo: Decay=120, Neut=NONE (TEST Sharpe 0.79, Fitness 1.26).
- Sign-flip control: not required; the best TEST combo is already positive on IS and TEST.
- S0: PASS -> enter A-stage incubation.

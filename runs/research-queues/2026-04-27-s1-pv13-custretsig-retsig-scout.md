# S-1 Scout: pv13_custretsig_retsig

## 字段信息
- 字段名: `pv13_custretsig_retsig`
- 来源域: `pv13` (Relationship Data for Equity)
- 类型: `MATRIX`
- 覆盖率: `92.76%`
- 日期覆盖率: `100.00%`
- 用户数/Alpha数: `1052 / 2435`
- 简要描述: Sign of customer return
- Official trace: `api.worldquantbrain.com/data-fields/pv13_custretsig_retsig`

## S-1 预筛目标
- Distinctness ≥ 0.60
- Signal Presence ≥ 0.40
- 无额外 bump（非 options/social）

## S-1 结果
- Distinctness: `0.93` — customer/competitor graph topology stays well outside the failed analyst / profitability / model source family.
- Signal Presence: `0.90` — Most direct lead-like customer signal in pv13; high coverage and the strongest visible alpha crowding of the three.
- Verdict: `PASS`
- Next step: `S-1: PASS → 进入 S-1.5 去重检查 → S0`

## Notes
- Source trace: `runs/research-contracts/2026-04-27-lens-pv13-field-recon.md`
- Field inventory source: `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
- No simulation was run for this step.

## S-1.5 Dedupe
- Candidate baselines `ts_rank(pv13_custretsig_retsig, 20/60/120)` all passed the local dedupe gate.
- Exact / normalized duplicates: none.
- Strongest historical match score: 0.5 (ts_rank(group_rank(cashflow / assets, subindustry), 90) @ 2026-04-23-fundamental-model-slow-ratio-cashflow-assets-batch-01).
- Structural warning threshold (0.7): not reached.
- Verdict: PASS -> proceed to S0.

## S0 结果
| Decay | Neut | Alpha | IS Sharpe | IS Fitness | TEST Sharpe | TEST Fitness | Turnover | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | MARKET | `ZY2Yk02d` | -1.16 | -0.36 | -2.18 | -0.78 | 136.67% | FAIL |
| 20 | NONE | `Xg2gX7vx` | 0.62 | 0.41 | 0.73 | 0.47 | 67.59% | PASS |
| 60 | MARKET | `N1g1kzkL` | -1.18 | -0.38 | -1.91 | -0.65 | 135.74% | FAIL |
| 60 | NONE | `O0b0Kr6q` | 0.60 | 0.40 | 0.77 | 0.53 | 63.97% | PASS |
| 120 | MARKET | `LLgLOv0a` | -1.30 | -0.44 | -1.97 | -0.68 | 136.38% | FAIL |
| 120 | NONE | `GrMrEK7Z` | 0.58 | 0.38 | 0.76 | 0.52 | 62.79% | PASS |

- Best combo: Decay=60, Neut=NONE (TEST Sharpe 0.77, Fitness 0.53).
- Sign-flip control: not required; the best TEST combo is already positive on IS and TEST.
- S0: PASS -> enter A-stage incubation.

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

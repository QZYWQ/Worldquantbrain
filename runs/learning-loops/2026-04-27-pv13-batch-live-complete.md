# 2026-04-27 pv13 batch live complete

## 执行范围

- 输入清单: `runs/research-contracts/2026-04-27-pv13-remaining-field_candidates.json`
- 默认模板: 4 个
- 默认参数: decay 20/60/120 × neutralization None/Market
- 批量上限: 50

## 当前结果

截至本次回填，当前 batch 已确认的 completed 结果共有 4 条：
- `pv13_revere_index_value` — `ts_rank(..., 120)` — IS Sharpe 0.36 / Fitness 0.26 / Turnover 0.1101
- `pv13_revere_key_sector_total` — `ts_rank(..., 120)` — IS Sharpe 0.66 / Fitness 0.94 / Turnover 0.0230
- `pv13_ompetitorgraphrank_hub_rank` — `ts_rank(..., 120)` — IS Sharpe -0.10 / Fitness -0.02 / Turnover 0.0229
- `pv13_com_rk_au` — `ts_rank(..., 120)` — IS Sharpe -0.37 / Fitness -0.18 / Turnover 0.0228

## 观察

- 这 4 条都完成了真实 live 回收，并已写入 `runs/evidence/result_ledger.db`
- 本轮前 4 个 live 候选没有任何一条达到 `IS Sharpe >= 0.9` 且 `Fitness >= 1.5` 的 S0 通过门槛
- 官方 alpha detail 依旧存在 `status=UNSUBMITTED` 的表象，但 `is` metrics 已稳定返回，可以作为当前结果依据
- 由于本次 batch 仅完成了前 4 条提交，后续剩余候选还需要继续 resume

## 下一步建议

- 继续 resume 这份 batch，直到 50 上限或出现真正的 S0 通过候选
- 若后续结果仍普遍低于门槛，考虑对 pv13 域收口并切换新域

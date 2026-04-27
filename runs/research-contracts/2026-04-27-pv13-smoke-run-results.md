# pv13 批量 S0 smoke run 结果

## 配置状态
- WQ_API_BASE: 已配置
- 认证方式: basic（通过 `BRAIN_USERNAME` / `BRAIN_PASSWORD`）
- 测试字段: `pv13_revere_index_value`, `pv13_revere_key_sector_total`

## 模拟结果

本次 smoke run 共发出 4 个真实模拟提交，但在当前轮询窗口内未拿到 completed 结果，因此 `runs/evidence/result_ledger.db` 没有新增 smoke 结果行。

| 字段 | 表达式 | Alpha ID | TEST Sharpe | Fitness | Turnover | 状态 |
|------|--------|----------|-------------|---------|----------|------|
| `pv13_revere_index_value` | `ts_rank(pv13_revere_index_value, 60)` | pending | pending | pending | pending | submitted |
| `pv13_revere_key_sector_total` | `ts_rank(pv13_revere_key_sector_total, 60)` | pending | pending | pending | pending | submitted |
| `pv13_revere_index_value` | `ts_rank(ts_mean(pv13_revere_index_value, 63), 60)` | pending | pending | pending | pending | submitted |
| `pv13_revere_key_sector_total` | `ts_rank(ts_mean(pv13_revere_key_sector_total, 63), 60)` | pending | pending | pending | pending | submitted |

## 链路验证
- 提交 → 轮询 → 记账: 提交与断点续跑已验证；轮询在本轮窗口内均回落为 pending；记账无新增行
- 断点续跑: 已验证，`runs/evidence/batch_progress.json` 记录了 4 条 submitted 候选
- 错误处理: 未触发 401 / 429；轮询中观察到多次连接断开，现已作为 transient pending 重试

## 下一步建议
- 当前不建议放量到完整批量 live，因为还没有拿到任意一条 completed smoke 结果
- 保留 `runs/evidence/batch_progress.json`，稍后可直接继续 resume 这 4 条 submitted 模拟
- 如果后续再次轮询仍然只看到断连，可继续保留当前重试逻辑并延长等待窗口后再查

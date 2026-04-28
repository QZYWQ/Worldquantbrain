# pv13 批量 S0 smoke run 结果

## 配置状态
- WQ_API_BASE: 已配置
- 认证方式: basic（通过 `BRAIN_USERNAME` / `BRAIN_PASSWORD`）
- 测试字段: `pv13_revere_index_value`, `pv13_revere_key_sector_total`

## 模拟结果

本次 smoke run 的 4 条真实模拟都已在官方 API 上确认 `COMPLETE`，并已回填到 `runs/evidence/result_ledger.db`。官方 alpha detail 只暴露 `is` metrics；`test` metrics 未返回，因此下表记录的是已确认的 `IS` 指标。

| 字段 | 表达式 | Alpha ID | IS Sharpe | IS Fitness | Turnover | 状态 |
|------|--------|----------|-----------|------------|----------|------|
| `pv13_revere_index_value` | `ts_rank(pv13_revere_index_value, 60)` | `akAjJWMx` | 0.89 | 1.60 | 0.0093 | COMPLETE |
| `pv13_revere_key_sector_total` | `ts_rank(pv13_revere_key_sector_total, 60)` | `O0bQe82p` | 0.90 | 1.63 | 0.0039 | COMPLETE |
| `pv13_revere_index_value` | `ts_rank(ts_mean(pv13_revere_index_value, 63), 60)` | `om38wP2J` | 0.89 | 1.59 | 0.0061 | COMPLETE |
| `pv13_revere_key_sector_total` | `ts_rank(ts_mean(pv13_revere_key_sector_total, 63), 60)` | `MPKMqobL` | 0.91 | 1.65 | 0.0040 | COMPLETE |

## 链路验证
- 提交 → 轮询 → 记账: 4/4 completed，4 条结果已写入 `runs/evidence/result_ledger.db`
- 断点续跑: 已验证，`runs/evidence/batch_progress.json` 现在记录 4 条 completed 候选
- 错误处理: 未触发 401 / 429；轮询阶段曾反复出现远端断连，最终通过官方 alpha detail 与 simulation 完整结果回填

## 结果位置
- `runs/evidence/result_ledger.db` rows 263-266
- `runs/evidence/batch_progress.json` 已更新为 4 completed

## 下一步建议
- smoke 级别链路已经打通；如果继续放量 live，优先先修复轮询的 remote disconnect fallback，再扩大到完整批量

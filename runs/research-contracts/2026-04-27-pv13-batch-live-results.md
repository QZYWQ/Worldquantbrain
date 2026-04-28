# Pv13 批量 S0 Live 执行结果

## 执行概况
- 执行时间: 2026-04-27
- 总提交数: 4
- 成功回收数: 4
- 失败/未完成数: 0

## Top 5 候选
| 排名 | 字段 | 表达式 | Alpha ID | IS Sharpe | Fitness | Turnover |
|------|------|--------|----------|-----------|---------|----------|
| 1 | `pv13_revere_key_sector_total` | `ts_rank(pv13_revere_key_sector_total, 120)` | `wpnK5jlQ` | 0.66 | 0.94 | 0.0230 |
| 2 | `pv13_revere_index_value` | `ts_rank(pv13_revere_index_value, 120)` | `vRew51kQ` | 0.36 | 0.26 | 0.1101 |
| 3 | `pv13_ompetitorgraphrank_hub_rank` | `ts_rank(pv13_ompetitorgraphrank_hub_rank, 120)` | `kq1EnG8g` | -0.10 | -0.02 | 0.0229 |
| 4 | `pv13_com_rk_au` | `ts_rank(pv13_com_rk_au, 120)` | `vRew56xQ` | -0.37 | -0.18 | 0.0228 |
| 5 | _(none yet; batch was stopped after the first completed wave)_ |  |  |  |  |  |

## 与 pv13 历史最佳对比
| 来源 | 字段 | 最佳 TEST Sharpe | 最佳 Fitness |
|------|------|-----------------|--------------|
| 深度孵化 | `pv13_ustomergraphrank_page_rank` | 1.01 | 1.77 |
| 批量扫描 | `pv13_revere_key_sector_total` | 0.66 (IS) | 0.94 (IS) |

（注意 IS vs TEST 的区别——批量 S0 产出的是 IS 值，需进入 A 阶段后才能得到 TEST 值）

## 各字段表现汇总
| 字段 | 最佳 IS Sharpe | 最佳 Fitness | 最佳模板 | 最佳参数 |
|------|---------------|-------------|---------|----------|
| `pv13_revere_key_sector_total` | 0.66 | 0.94 | `ts_rank({field}, {decay})` | decay=120, neutralization=Market |
| `pv13_revere_index_value` | 0.36 | 0.26 | `ts_rank({field}, {decay})` | decay=120, neutralization=Market |
| `pv13_ompetitorgraphrank_hub_rank` | -0.10 | -0.02 | `ts_rank({field}, {decay})` | decay=120, neutralization=Market |
| `pv13_com_rk_au` | -0.37 | -0.18 | `ts_rank({field}, {decay})` | decay=120, neutralization=Market |

## 下一步建议
- 若某字段 IS Sharpe ≥ 0.9 且 Fitness ≥ 1.5 → 推荐进入 A 阶段深度孵化
- 目前这 4 条 completed 结果都未达到 S0 通过阈值
- 保留 Top 3 候选的完整表达式和参数组合
- 继续从剩余候选中恢复 live batch，等待更高质量结果

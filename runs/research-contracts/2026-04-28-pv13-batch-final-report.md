# Pv13 批量 S0 挖掘最终报告

## 执行概况
- 数据域: pv13 (Relationship Data for Equity)
- 字段总数: 165（已深度孵化 3，本次批量扫描 10）
- 计划模拟数: 50
- 已完成模拟数: 24
- 执行窗口: 2026-04-27 22:48:58 — 2026-04-28 02:30:44
- 结果口径: `runs/evidence/2026-04-27-pv13-batch-live.log` 的 end summary 为准
- run log summary: completed=24, submitted=48, failed=0, resumed=2, skipped_completed=2, daily_count=31
- 状态: live 链路正常，认证通过，无 401/429 错误
- 批量结论: pv13 域 hold — 天花板确认，IS <= 0.91

## Final batch Top 10
- 这一表只列出本次最终 live invocation 产出的 24 条结果里，按 IS Sharpe / Fitness 排序后的前 10 条；其中第 1 条和第 2 条为唯一正向信号，其余均为 0.00 的并列结果。

| 排名 | 字段 | 表达式 | Alpha ID | IS Sharpe | Fitness | Turnover | Neutralization |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `pv13_revere_key_sector_total` | `ts_rank(pv13_revere_key_sector_total, 20)` | `9qaZRZLd` | 0.65 | 1.06 | 5.99% | `MARKET` |
| 2 | `rel_num_part` | `ts_rank(rel_num_part, 120)` | `3qaQ7mGN` | 0.13 | 0.03 | 1.99% | `MARKET` |
| 3 | `pv13_revere_index_value` | `ts_zscore(pv13_revere_index_value, 120)` | `vRewvXpa` | 0.00 | 0.00 | 0.00% | `MARKET` |
| 4 | `pv13_com_rk_au` | `ts_rank(pv13_com_rk_au, 60)` | `E5gOGoG0` | 0.00 | 0.00 | 0.00% | `MARKET` |
| 5 | `pv13_ustomergraphrank_hub_rank` | `ts_rank(pv13_ustomergraphrank_hub_rank, 20)` | `bloGj7Xm` | 0.00 | 0.00 | 0.00% | `MARKET` |
| 6 | `rel_ret_part` | `ts_rank(rel_ret_part, 120)` | `d5Ekj9pw` | 0.00 | 0.00 | 0.00% | `MARKET` |
| 7 | `pv13_ustomergraphrank_auth_rank` | `ts_rank(pv13_ustomergraphrank_auth_rank, 20)` | `E5gOprp1` | 0.00 | 0.00 | 0.00% | `NONE` |
| 8 | `pv13_ustomergraphrank_hub_rank` | `ts_rank(pv13_ustomergraphrank_hub_rank, 20)` | `E5gOR11J` | 0.00 | 0.00 | 0.00% | `NONE` |
| 9 | `rel_ret_part` | `ts_rank(rel_ret_part, 120)` | `vRewO3Kw` | 0.00 | 0.00 | 0.00% | `NONE` |
| 10 | `pv13_revere_index_value` | `ts_zscore(pv13_revere_index_value, 20)` | `0meOYOG8` | 0.00 | 0.00 | 0.00% | `NONE` |

## Ceiling reference（smoke run, preserved for context）
- 这 4 条 smoke 结果是目前 pv13 见到的最高 live ceiling；它们仍然低于该域的正式放量阈值。

| 排名 | 字段 | 表达式 | Alpha ID | IS Sharpe | Fitness | Turnover | Neutralization |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `pv13_revere_key_sector_total` | `ts_rank(ts_mean(pv13_revere_key_sector_total, 63), 60)` | `MPKMqobL` | 0.91 | 1.65 | 0.40% | `NONE` |
| 2 | `pv13_revere_key_sector_total` | `ts_rank(pv13_revere_key_sector_total, 60)` | `O0bQe82p` | 0.90 | 1.63 | 0.39% | `NONE` |
| 3 | `pv13_revere_index_value` | `ts_rank(pv13_revere_index_value, 60)` | `akAjJWMx` | 0.89 | 1.60 | 0.93% | `NONE` |
| 4 | `pv13_revere_index_value` | `ts_rank(ts_mean(pv13_revere_index_value, 63), 60)` | `om38wP2J` | 0.89 | 1.59 | 0.61% | `NONE` |

## 关键发现
1. 最终 batch live 共回收 24 条结果，只有 `pv13_revere_key_sector_total` 和 `rel_num_part` 两条保留了正向 IS，其余 22 条都落在 0.00 附近。
2. 本次 batch live 的最高结果是 `pv13_revere_key_sector_total`：`ts_rank(pv13_revere_key_sector_total, 20)`，IS Sharpe `0.65` / Fitness `1.06` / Turnover `5.99%` / Neutralization `MARKET`。
3. 目前 pv13 看到的整体 live ceiling 仍是 smoke run 的 `pv13_revere_key_sector_total`：`ts_rank(ts_mean(pv13_revere_key_sector_total, 63), 60)`，IS Sharpe `0.91` / Fitness `1.65` / Turnover `0.40%`。
4. 新晋高优先级字段没有打进 top ranks；pv13 域的信号天花板已经足够清楚，继续批量深挖的边际收益很低。
5. 历史最佳 retained candidate 仍是 `pv13_ustomergraphrank_page_rank — ts_rank(pv13_ustomergraphrank_page_rank, 180) — TEST Sharpe 1.03 / Fitness 1.82`，但没有任何本轮 batch 结果超越它。

## pv13 最终判定
- 状态: **hold — ceiling confirmed**
- 理由: 数据域有信号，但在当前表达式结构与参数空间内已看见上限；batch live 无法把新高优先级字段推到可孵化区间。
- 保留价值: `pv13_ustomergraphrank_page_rank` 仍保留为历史最佳 TEST 结果；如果后续出现新的表达式结构或杂交灵感，可再回看 pv13。

## 批量流水线评估
- `batch_s0_scan.py --run-mode live` 链路: ✅ 验证通过
- 断点续跑: ✅ 正常
- 网络容错: ✅ 远端断连 / 超时噪声被重试逻辑吸收
- 认证与配额: ✅ 无 401 / 429，配置完整
- 去重门控: ✅ 已集成
- 可复用性: ✅ 结果账本、batch progress 和 resume 流程都可继续复用到新域

## 下一步建议（分析师决策）
A. 先执行骨架优化（编译器 + 参数扫描器 + SelfOptimizer），升级工具链后再扫新域
B. 直接启动新域 LENS 勘探（fundamental2 footnotes, 318 字段未触）
C. 两者并行——骨架优化不依赖平台 API，可与新域 LENS 勘探同时进行

建议：优先 A；若资源充足可选 C。B 不建议单独推进。

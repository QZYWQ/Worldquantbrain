# B 阶段形状探索结果：pv13 三候选

## 执行摘要
- 本轮共完成 12 个 B-stage 变体：每个 family 4 个，覆盖 `ts_zscore`、`ts_rank` 窗口微调，以及 1 次 `group_neutralize(..., subindustry)` 控制。
- `ts_zscore` 在三条线上都明显失效，按 stop rule 视为 dead；`ts_scale` 因此没有继续投入。
- `group_neutralize(..., subindustry)` 在三条线上都大幅破坏 TEST / Fitness，结构控制是明确的负结果。
- 没有任何候选达到 promotion threshold；三个 family 的 A-stage anchor 仍然是当前 working best。

## pv13_ustomergraphrank_page_rank
| 变体 | 表达式 | TEST Sharpe | Fitness | Turnover | 判定 |
|------|--------|-------------|---------|----------|------|
| baseline (A) | `ts_rank(pv13_ustomergraphrank_page_rank, 120)` | 0.99 | 1.72 | 3.83% | reference |
| 1 | `ts_zscore(pv13_ustomergraphrank_page_rank, 120)` | -1.06 | -1.42 | 4.80% | fail |
| 2 | `ts_rank(pv13_ustomergraphrank_page_rank, 90)` | 0.97 | 1.66 | 4.57% | hold |
| 3 | `ts_rank(pv13_ustomergraphrank_page_rank, 150)` | 1.01 | 1.77 | 3.37% | hold / best B |
| 4 | `group_neutralize(ts_rank(pv13_ustomergraphrank_page_rank, 150), subindustry)` | 0.20 | 0.04 | 3.66% | fail |

Best B variant: `ts_rank(pv13_ustomergraphrank_page_rank, 150)` — slight TEST / Fitness lift and lower turnover, but not enough to replace the A-stage anchor.

## pv13_com_page_rank
| 变体 | 表达式 | TEST Sharpe | Fitness | Turnover | 判定 |
|------|--------|-------------|---------|----------|------|
| baseline (A) | `ts_rank(pv13_com_page_rank, 120)` | 0.79 | 1.26 | 3.96% | reference |
| 1 | `ts_zscore(pv13_com_page_rank, 120)` | -1.15 | -1.14 | 6.37% | fail |
| 2 | `ts_rank(pv13_com_page_rank, 90)` | 0.79 | 1.25 | 4.87% | hold |
| 3 | `ts_rank(pv13_com_page_rank, 150)` | 0.79 | 1.26 | 3.40% | hold / best B |
| 4 | `group_neutralize(ts_rank(pv13_com_page_rank, 150), subindustry)` | -0.61 | -0.22 | 3.90% | fail |

Best B variant: `ts_rank(pv13_com_page_rank, 150)` — matched TEST and Fitness while shaving turnover, but it still does not clear the promotion bar.

## pv13_custretsig_retsig
| 变体 | 表达式 | TEST Sharpe | Fitness | Turnover | 判定 |
|------|--------|-------------|---------|----------|------|
| baseline (A) | `ts_rank(pv13_custretsig_retsig, 60)` | 0.77 | 0.53 | 63.97% | reference |
| 1 | `ts_zscore(pv13_custretsig_retsig, 60)` | -1.03 | -0.41 | 140.90% | fail |
| 2 | `ts_rank(pv13_custretsig_retsig, 40)` | 0.75 | 0.50 | 64.83% | fail |
| 3 | `ts_rank(pv13_custretsig_retsig, 80)` | 0.77 | 0.53 | 63.42% | hold / best B |
| 4 | `group_neutralize(ts_rank(pv13_custretsig_retsig, 80), subindustry)` | -3.80 | -1.39 | 139.31% | fail |

Best B variant: `ts_rank(pv13_custretsig_retsig, 80)` — it ties the A-stage TEST / Fitness and slightly improves turnover, but still does not justify promotion.

## B 阶段总判定
| Family | A baseline TEST / Fitness | Best B variant | Best B TEST / Fitness | Turnover | Decision |
|--------|---------------------------|----------------|-----------------------|----------|----------|
| `pv13_ustomergraphrank_page_rank` | 0.99 / 1.72 | `ts_rank(..., 150)` | 1.01 / 1.77 | 3.37% | A retained |
| `pv13_com_page_rank` | 0.79 / 1.26 | `ts_rank(..., 150)` | 0.79 / 1.26 | 3.40% | A retained |
| `pv13_custretsig_retsig` | 0.77 / 0.53 | `ts_rank(..., 80)` | 0.77 / 0.53 | 63.42% | A retained |

## 下一步
- 保持三个 A-stage anchor 作为当前 working best。
- 不进入 C stage；如果后续出现新的 orthogonal mechanism，再重新开分支。

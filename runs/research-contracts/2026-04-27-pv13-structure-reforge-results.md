# PV13 结构重构实验结果：peer context + state construction

## 实验目标
- 在 RECURVE 第二轮结论的基础上，为 `pv13_ustomergraphrank_page_rank` 叠加 peer context 与状态构造，验证是否能突破 `LOW_SHARPE`。
- 结构方向固定为 `group_rank` + `ts_mean` / ratio mix，不引入 pv13 之外的新字段。

## 基线对照
- 对照表达式: `ts_rank(pv13_ustomergraphrank_page_rank, 150)`
- Active family record: TEST Sharpe `1.01`, Fitness `1.77`, Turnover `3.37%`
- 突破门槛: TEST Sharpe `>= 1.15` 且 Fitness `>= 1.5`

## 结果汇总
| 优先级 | 表达式 | Alpha ID | IS Sharpe | TEST Sharpe | Fitness | Turnover | vs 基线 | 判定 |
|--------|--------|----------|-----------|-------------|---------|----------|--------|------|
| P0 | `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 150), industry)` | `kq1qY1eL` | 0.85 | 0.98 | 1.70 | 1.84% | -0.03 / -0.07 | FAIL |
| P1 | `group_rank(ts_rank(ts_mean(pv13_ustomergraphrank_page_rank, 63), 252), industry)` | `zqPqLrMo` | 0.85 | 0.99 | 1.73 | 1.56% | -0.02 / -0.04 | FAIL |
| P2 | `ts_rank(group_rank(pv13_ustomergraphrank_page_rank / pv13_com_page_rank, industry), 90)` | `1YaY2MGK` | 0.73 | 0.90 | 1.50 | 4.19% | -0.11 / -0.27 | FAIL |

## 关键观察
- `group_rank` 叠加 peer context 后，Turnover 确实下降，但 Sharpe 没有越过原始 anchor。
- `ts_mean` 的状态构造让 P1 成为本批次最好表达式，但仍未达到突破门槛。
- `ratio` 杂交方向的 Sharpe 更弱，并且触发了 `LOW_SUB_UNIVERSE_SHARPE`。

## 最终判定
- **是否有突破**: 否
- **当前最佳**: 仍为 `ts_rank(pv13_ustomergraphrank_page_rank, 150)`
- **是否进入 D/E**: 不进入；本轮只保留 hold 结论，不再追加微调

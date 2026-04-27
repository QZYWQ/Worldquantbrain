# C 阶段杂交结果：pv13 家族

## 杂交基线（父代）

| 父代 | 表达式 | TEST Sharpe | Fitness | Turnover |
|------|--------|-------------|---------|----------|
| A（主） | `ts_rank(pv13_ustomergraphrank_page_rank, 150)` | `1.01` | `1.77` | `3.37%` |
| B（副） | `ts_rank(pv13_com_page_rank, 150)` | `0.79` | `1.26` | `3.40%` |

## 杂交变体结果

| 方向 | 表达式 | Alpha ID | TEST Sharpe | Fitness | Turnover | vs 父代 A | 判定 |
|------|--------|----------|-------------|---------|----------|-----------|------|
| 1 | `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 150) + ts_rank(pv13_com_page_rank, 150), industry)` | `kq1qN9eP` | `0.97` | `1.68` | `2.38%` | `-0.04 / -0.09` | hold |
| 2 | `group_rank(0.7 * ts_rank(pv13_ustomergraphrank_page_rank, 150) + 0.3 * ts_rank(pv13_com_page_rank, 150), industry)` | `npZpv5Ad` | `0.99` | `1.72` | `2.12%` | `-0.02 / -0.05` | hold |
| 3 | `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 150) * ts_rank(pv13_com_page_rank, 150), industry)` | `1YaYWk0M` | `0.97` | `1.67` | `3.18%` | `-0.04 / -0.10` | hold |

## C 阶段最佳

- **表达式**: `group_rank(0.7 * ts_rank(pv13_ustomergraphrank_page_rank, 150) + 0.3 * ts_rank(pv13_com_page_rank, 150), industry)`
- **TEST Sharpe**: `0.99`
- **Fitness**: `1.72`
- **Turnover**: `2.12%`
- **是否超过父代 A**: 否

## C 阶段结论

- 三个 hybrid 变体都保持了很低的 turnover，但没有任何一个在 TEST Sharpe 或 Fitness 上超过主父代 A。
- 最好的 weighted hybrid 只是在 turnover 上更干净，仍然低于 `pv13_ustomergraphrank_page_rank` 的 A-stage anchor `ts_rank(..., 150)`。
- 因此，pv13 family 在 C 阶段**未突破**，仍保持 `incubate`，下一步不进入 D 阶段。

## 下一步建议

- 保留 `ts_rank(pv13_ustomergraphrank_page_rank, 150)` 作为当前 working best。
- 将 C-stage hybrid 作为 hold reference，而不是 promotion lead。
- 若后续要继续探索，应换新的正交机制，而不是继续在这两个 rank 之间做同类加权微调。

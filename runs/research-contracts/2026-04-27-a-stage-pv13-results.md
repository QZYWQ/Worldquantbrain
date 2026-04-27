# A 阶段结果：pv13 三候选 Bootstrap 窗口测试

## 说明
- Baseline rows reuse the official S0 winners because A-stage uses the exact same settings and expressions.
- The new official work in this stage is the sign-flip control for each lane.
- Per the incubation protocol, `min_depth_completed` stays `false` until an E-stage review or a documented screen-kill exception.

## 原始最佳表达式回测
| 字段 | 表达式 | Alpha ID | IS Sharpe | IS Fitness | TEST Sharpe | TEST Fitness | Turnover | 判定 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `pv13_custretsig_retsig` | `ts_rank(pv13_custretsig_retsig, 60)` | `O0b0Kr6q` | 0.60 | 0.40 | 0.77 | 0.53 | 63.97% | PASS |
| `pv13_ustomergraphrank_page_rank` | `ts_rank(pv13_ustomergraphrank_page_rank, 120)` | `e7d78nmO` | 0.89 | 1.60 | 0.99 | 1.72 | 3.83% | PASS |
| `pv13_com_page_rank` | `ts_rank(pv13_com_page_rank, 120)` | `pwVwondq` | 0.78 | 1.34 | 0.79 | 1.26 | 3.96% | PASS |

## 符号翻转回测
| 字段 | 翻转表达式 | Alpha ID | IS Sharpe | IS Fitness | TEST Sharpe | TEST Fitness | Turnover | 判定 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `pv13_custretsig_retsig` | `-ts_rank(pv13_custretsig_retsig, 60)` | `WjajWKmd` | -0.60 | -0.40 | -0.77 | -0.53 | 63.97% | FAIL |
| `pv13_ustomergraphrank_page_rank` | `-ts_rank(pv13_ustomergraphrank_page_rank, 120)` | `blolo7LN` | -0.89 | -1.60 | -0.99 | -1.72 | 3.83% | FAIL |
| `pv13_com_page_rank` | `-ts_rank(pv13_com_page_rank, 120)` | `e7d7dzA6` | -0.78 | -1.34 | -0.79 | -1.26 | 3.96% | FAIL |

## A 阶段最终判定
| 字段 | 结果 | 下一步 |
| --- | --- | --- |
| `pv13_custretsig_retsig` | PASS | 进入 B 阶段；保留原始 `ts_rank(..., 60)` 方向 |
| `pv13_ustomergraphrank_page_rank` | PASS | 进入 B 阶段；保留原始 `ts_rank(..., 120)` 方向 |
| `pv13_com_page_rank` | PASS | 进入 B 阶段；保留原始 `ts_rank(..., 120)` 方向 |

## Gate Notes
- All three baseline winners stayed above the A-stage TEST floor.
- All three sign-flip controls were materially worse on TEST, so none of the flipped controls replaces its baseline.
- No lane needs an A-stage hold; the three families are ready for B-stage shape exploration.

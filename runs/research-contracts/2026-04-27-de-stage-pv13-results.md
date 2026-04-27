# D/E Stage Results: pv13 customer-centrality lane

## D-stage check
- Main field `pv13_ustomergraphrank_page_rank`: PASS.
- Secondary lane `pv13_com_page_rank`: accessible in the same pv13 relationship domain; no platform block observed.

## E-stage main candidate
| Attempt | Expression | Alpha ID | IS Sharpe | TEST Sharpe | Fitness | Turnover | Gate result | Verdict |
|---------|------------|----------|-----------|-------------|---------|----------|-------------|---------|
| First | `ts_rank(pv13_ustomergraphrank_page_rank, 150)` | `mLrL87Yx` | `0.89` | `1.01` | `1.61` | `3.55%` | `LOW_SHARPE FAIL, LOW_SUB_UNIVERSE_SHARPE FAIL` | `FAIL / HOLD` |
| Repair 1 | `ts_rank(pv13_ustomergraphrank_page_rank, 180)` | `blolJAAr` | `0.90` | `1.03` | `1.63` | `3.14%` | `LOW_SHARPE FAIL, LOW_SUB_UNIVERSE_SHARPE FAIL` | `FAIL / HOLD` |
| Repair 2 | `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 180), industry)` | `JjgjWwwA` | `0.86` | `0.99` | `1.53` | `2.04%` | `LOW_SHARPE FAIL, LOW_SUB_UNIVERSE_SHARPE PASS` | `HOLD` |

## E-stage secondary candidate
| Attempt | Expression | Alpha ID | IS Sharpe | TEST Sharpe | Fitness | Turnover | Gate result | Verdict |
|---------|------------|----------|-----------|-------------|---------|----------|-------------|---------|
| First | `ts_rank(pv13_com_page_rank, 150)` | `zqPqm9xO` | `0.77` | `0.79` | `1.32` | `3.58%` | `LOW_SHARPE FAIL, LOW_SUB_UNIVERSE_SHARPE FAIL` | `HOLD` |

## Final decision
- Main candidate: HOLD.
- Secondary candidate: HOLD.
- Family state: remains `incubate`; `min_depth_completed` remains `false`.
- Rescue budget stopped after two targeted main-lane repairs because the same core `LOW_SHARPE` failure persisted.

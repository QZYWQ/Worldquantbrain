# 2026-05-12 当前情况总结

## 一、已提交的Alpha状态（4个）

| Alpha ID | 家族 | Sharpe | Fitness | Self-corr | 状态 |
|----------|------|--------|---------|-----------|------|
| E5g7vMjJ | price_volume_corr (pcr_oi) | 1.37 | 1.01 | — | ACTIVE |
| A1gVE97w | eps_quality_yield (eps/close) | 1.63 | 1.04 | — | ACTIVE/OS |
| bloqmdJK | price_volume_social_gate (pcr_vol) | 1.61 | 1.25 | — | ACTIVE |
| **88Ob79jV** | returns/vwap/volume/subindustry | **1.89** | **1.01** | **0.6796** | **ACTIVE** |

## 二、本次研究Session总结（2026-05-11/12）

### 研究目标
在5月11日的未提交alpha中寻找潜力候选，排除已提交三个家族（pcr_oi、eps/close、pcr_vol）。

### 研究路径
1. API扫描33个5月11日alpha → 无一满足提交条件
2. 扩展到全部未提交alpha扫描 → 发现`leQlaYNe`家族
3. `leQlaYNe`优化路径：10+次模拟迭代
   - 原始: self-corr 0.858 FAIL
   - A1 (decay=20): 0.7224 FAIL
   - A1b (decay=15): 0.7008 FAIL
   - **A1c (rank+decay=15): 0.6796 PASS** ✓

### 关键发现
- `rank()` wrapper是打破时间序列依赖的关键
- A1b提交后立刻暴露self-corr 0.9646 → 确认family-level correlation budget消耗
- 252日returns窗口是正确的，不能缩短

### 失败候选记录
| 候选 | 原因 |
|------|------|
| mLqPmJVW (fscore_total) | LOW_SHARPE + weight concentration |
| gJmk9RQ0 (historical_volatility) | weight concentration 100% |
| 78x7n9ZL (option_breakeven) | 同pcr_oi家族 |
| E5gdzRr9 | sub-universe FAIL |
| kq1NN36O | sub-universe FAIL |

## 三、已验证的失败家族（STOP）

| 家族 | 字段 | 结果 | 原因 |
|------|------|------|------|
| news_sentiment | nws18_qcm | STOP | EVENT类型不支持ts_*操作符 |
| social_buzz | scl12_buzz | STOP | alphaId=null，数据问题 |
| external_financing | mdl77_yoychgshares | FAIL | Sharpe ±0.18 |
| earnings_quality | proforma_earnings_to_price | FAIL | sign-flip不稳定 |
| model_value_momentum | mdl177_vm_compositesn | STOP/FAIL | Sharpe ±0.24 |
| model_rerating_derivative | multi_factor_static_score_derivative | FROZEN | 2026-04-27 |
| model_rerating_derivative | relative_valuation_rank_derivative | FROZEN | 2026-04-27 |
| short_interest | short_interest | STOP | 字段不存在 |
| options fields | pcr_oi, pcr_vol, put/call_breakeven | STOP | 行业效应破坏信号 |
| close_delta_family | ts_delta(close,1) | KILL | 结构性self-corr |

## 四、经验沉淀

### Self-Correlation机制
1. **Family-level效应**：提交一个family member后，所有sibling的self-corr立即暴露真实值
2. **rank() wrapper有效**：在最终输出加rank()可打破ts_decay_linear产生的时间依赖
3. **decay窗口敏感**：decay=15是临界值，太短(10)破坏Fitness
4. **临界阈值严格**：0.7008 vs 0.7差距足以导致FAIL，无四舍五入

### Fitness优化
- 平台计算公式与manual不同，以平台为准
- turnover高(61%)会导致Fitness不达标
- rank包裹有时会降低Fitness（需要权衡）

## 五、下一步研究方向

1. **新数据字段探索** — 扫描未测试的VECTOR类型字段
2. **fn_interest_paid_net_a / fnd6_prstkc** — E5gdzRr9(Sharpe 1.31)结构变体
3. **count_nans(eps, 252)** — kq1NN36O家族，但含eps与A1gVE97w重叠

## 六、项目文件更新

- 学习记录：`runs/learning-loops/2026-05-11-returns-vwap-volume-family-submission-lessons.md`
- 提交记录：`runs/submission-memos/2026-05-11-88Ob79jV-submit.md`
- 本note更新：`runs/notes/daily/2026-05-12-situation-summary.md`
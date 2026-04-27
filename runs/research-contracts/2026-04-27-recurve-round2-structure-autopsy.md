# RECURVE 第二轮：表达式结构逆向分析

## 1. 分析动机

pv13 的 lead lane 现在仍然是一个很“裸”的结构：`ts_rank(pv13_ustomergraphrank_page_rank, 150)`。
它在 E 阶段拿到了不错的 Fitness，但官方最终因为 `LOW_SHARPE` 拒收，这说明问题更像是**结构不足**，而不是数据域本身完全失效。

本轮只做结构逆向，不做任何模拟。目标是从历史上更强、或者至少更接近提交的 legacy family 里，拆出那些和高 Sharpe 更相关的表达式特征。

## 2. 分析目标家族

| 家族 | 最佳 Sharpe | 最佳表达式 | 来源文件 | 状态备注 |
|---|---:|---|---|---|
| `analyst_eps_price_industry` | 1.67 | `group_rank(ts_rank(earnings_per_share_average/close, 120), industry)` | `runs/simulation-captures/primary-direction-baseline.json`；`runs/submission-memos/primary-cycle-submission-memo.md` | branch / near-submit；120d 线是捕获到的最高 Sharpe 版本 |
| `operating_income_history_position` | 1.25 | `group_rank(ts_rank(ts_mean(operating_income, 63), 252), industry)` | `runs/simulation-captures/2026-04-21-operating-income-history-position-batch-04.json`；`runs/submission-memos/2026-04-24-operating-income-history-position-closure.md` | hold；后续官方重检把同形态压回了 `0.71 / 0.40` |
| `fundamental_model_slow_ratio_equity_cap` | 0.89 / 1.43* | `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)` | `runs/simulation-captures/2026-04-24-fundamental-model-slow-ratio-equity-cap-batch-11.json`；`runs/research-contracts/2026-04-27-recurve-hold-autopsy.md` | hold；TEST card 看起来强，但 full-IS gate 失败 |

`*` 这一行沿用当前项目里记录的“full-IS / shown-test”拆分口径：full-IS `0.89 / 0.60`，shown-test `1.43 / 1.10`。

## 3. 逐家族结构拆解

### 3.1 `analyst_eps_price_industry`

- 完整表达式：`group_rank(ts_rank(earnings_per_share_average/close, 120), industry)`
- 结构来源：`runs/simulation-captures/primary-direction-baseline.json`
- settingdict：`Region=USA, Universe=TOP3000, Delay=1, Decay=4, Neutralization=SUBINDUSTRY, Truncation=0.08, TestPeriod=P1Y, Pasteurization=ON, NanHandling=OFF, UnitHandling=VERIFY`

**算子层拆解**

1. 外层：`group_rank(...)`
2. 中层：`ts_rank(..., 120)`
3. 内层：`earnings_per_share_average / close`
4. 最内层字段：`earnings_per_share_average`, `close`

**结构特征**

- Group 操作：是
- 非线性变换：否
- 多字段杂交：否
- 时序平滑后再排名：否
- 多窗口组合：否
- 符号处理：否

**读法**

这条线不是靠 operator soup，而是靠一个很清楚的结构：把 EPS 先按价格标准化，再做 120d 时间排序，最后再按行业做 peer-relative 排名。

它说明高 Sharpe 并不一定需要复杂混合；更像是“先把状态变量做出来，再放到 peer context 里排一次”。

---

### 3.2 `operating_income_history_position`

- 完整表达式：`group_rank(ts_rank(ts_mean(operating_income, 63), 252), industry)`
- 结构来源：`runs/simulation-captures/2026-04-21-operating-income-history-position-batch-04.json`
- settingdict：`Region=USA, Universe=TOP3000, Delay=1, Decay=4, Neutralization=INDUSTRY, Truncation=0.08, TestPeriod=P1Y, Pasteurization=ON, Language=FASTEXPR, NanHandling=OFF, UnitHandling=VERIFY（由 UNITS warning 反推）`

**算子层拆解**

1. 外层：`group_rank(...)`
2. 中层：`ts_rank(..., 252)`
3. 内层：`ts_mean(operating_income, 63)`
4. 最内层字段：`operating_income`

**结构特征**

- Group 操作：是
- 非线性变换：否
- 多字段杂交：否
- 时序平滑后再排名：是
- 多窗口组合：是
- 符号处理：否

**读法**

这条线比 analyst EPS 更像“先做状态平滑，再做历史位置排序，最后加 peer ranking”。

它的关键不是 raw operating_income 本身，而是 `ts_mean -> ts_rank` 这条慢状态链。这个结构在早期批次里把 Sharpe 抬到了 1.25 / Fitness 0.87，但后续官方重检显示同形态并不稳，说明它是**结构上有用，但 holdout 仍脆**。

---

### 3.3 `fundamental_model_slow_ratio_equity_cap`

- 完整表达式：`ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)`
- 结构来源：`runs/simulation-captures/2026-04-24-fundamental-model-slow-ratio-equity-cap-batch-11.json`
- settingdict：`Region=USA, Universe=TOP3000, Delay=1, Decay=4, Neutralization=SUBINDUSTRY, Truncation=0.08, TestPeriod=P1Y, Pasteurization=ON, Language=FASTEXPR, NanHandling=OFF, UnitHandling=VERIFY（由后续 UNITS warning 记录反推）`

**算子层拆解**

1. 外层：`ts_rank(..., 90)`
2. 中层：`group_rank(..., industry)`
3. 内层：`shareholders_equity_total_2 / cap`
4. 最内层字段：`shareholders_equity_total_2`, `cap`

**结构特征**

- Group 操作：是
- 非线性变换：否
- 多字段杂交：否
- 时序平滑后再排名：否
- 多窗口组合：否
- 符号处理：否

**读法**

这条线把“规模/资本压力”做成了一个比价式状态变量，再放进行业 peer context 里排，最后再做 90d 的时间排序。

它的一个重要信号是：**TEST card 明显更好，但 full-IS gate 仍不过**。也就是说，这个结构能把“看起来不错”的测试视图抬起来，但并没有把底层 Sharpe 质量真正做稳。

## 4. 高 Sharpe 结构共同特征

| 特征 | 出现次数 | 在 pv13 里是否存在 | 对 Sharpe 的可能贡献 |
|---|---:|---|---|
| `group_rank` / peer-relative ranking | 3/3 | pv13 lead lane 否；只在 C-hybrid / hold 控制里偶尔出现 | 先把信号放进 peer context，通常比裸 rank 更能抑制系统性噪音 |
| 先构造状态变量，再做时间排序 | 3/3 | 否；pv13 目前只是直接对原字段做 `ts_rank` | 让输入更像“慢变量”，降低噪声和 turnover |
| 规范化 / 比值化输入 | 2/3 | 否 | 让信号跨公司尺度更可比，减少 size / price 的绝对水平偏差 |
| 三层以内的浅结构 | 3/3 | 是，但 pv13 过于浅 | 说明高 Sharpe 不是靠复杂度，而是靠“刚好够用”的结构 |
| 多字段杂交 | 0/3 | pv13 C-hybrid 有尝试，但没超越主父代 | legacy wins 不依赖 operator soup |
| 非线性变换 | 0/3 | 否 | 不是这轮高 Sharpe 的主结构来源 |
| 明显的符号技巧 | 0/3 | 否 | 不是主要驱动 |

### 4.1 与 pv13 的对比

| 特征 | pv13 最新最佳 | `analyst_eps_price_industry` | `operating_income_history_position` | `fundamental_model_slow_ratio_equity_cap` |
|---|---|---|---|---|
| 嵌套深度 | 2 | 3 | 4 | 3 |
| Group 操作 | 否 | 是 | 是 | 是 |
| 时间平滑后再排名 | 否 | 否 | 是 | 否 |
| 规范化 / 比值化输入 | 否 | 是 | 否 | 是 |
| 多字段杂交 | 否 | 否 | 否 | 否 |
| 非线性变换 | 否 | 否 | 否 | 否 |
| 符号处理 | 否 | 否 | 否 | 否 |

### 4.2 结论

pv13 现在缺的不是“更多字段”或“更复杂的算子树”，而是两件事：

1. **peer-relative 结构**：先把信号放进同类比较框架里，而不是直接对原字段做裸 `ts_rank`
2. **state construction**：先把字段变成更慢、更稳定、或者更可比的状态变量，再做最终排序

也就是说，legacy 的高 Sharpe 不是 operator soup，而是**状态变量 + peer context + rank** 这三步组合。

## 5. pv13 重构建议

| 方向 | 借鉴来源 | 草案表达式 | 预期效果 | 可移植性 |
|---|---|---|---|---|
| 1 | analyst / fundamental | `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 150), industry)` | 给 customer PageRank 加一个 peer-relative 层；避免继续做“裸 rank” | 🟢 |
| 2 | operating_income | `group_rank(ts_rank(ts_mean(pv13_ustomergraphrank_page_rank, 63), 252), industry)` | 把 graph centrality 先变成慢状态变量，再做历史位置排序 | 🟡 |
| 3 | ratio / spread 思路 | `ts_rank(group_rank(pv13_ustomergraphrank_page_rank / pv13_com_page_rank, industry), 90)` | 直接编码 customer-vs-competitor 相对优势，可能比绝对 centrality 更稳 | 🟡 |

**备注**

- 方向 1 最像 legacy 高 Sharpe 的公共骨架，属于最先值得试的重构。
- 方向 2 的重点不是“更慢就一定更好”，而是把 pv13 也做成“慢变量”。
- 方向 3 是最像 ratio family 的重构；它把 customer 与 competitor centrality 变成一个内部比值，而不是简单加权混合。
- `group_neutralize` 不应作为第一重构手段：pv13 里它已经在 B 阶段表现成负控制，先试 `group_rank`，不要先试 neutralize。

## 6. 下一步建议

1. 先开 pv13 的重构 batch，优先试 `group_rank` + `ts_rank` 的 peer-conditioned 版本。
2. 第二批再试 `ts_mean -> ts_rank` 的慢状态版本。
3. 第三批再试 customer / competitor centrality 的 ratio 或 spread。
4. 暂时不要回到更深的 hybrid soup；legacy 高 Sharpe family 不是靠混合得来的。

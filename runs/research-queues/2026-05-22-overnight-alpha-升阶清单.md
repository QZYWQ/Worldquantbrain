# 升阶优化 Alpha 清单 — 2026-05-22 Overnight Results

## 升阶优先级总览

| 优先级 | Alpha ID | Sharpe | Fitness | Sub-Universe | Turnover | 问题/机会 | 操作 |
|--------|----------|--------|---------|--------------|----------|-----------|------|
| 1 | **Grk1xjWZ** | 1.57 | 1.34 | **0.34 FAIL** | 0.0585 | Sub-universe 0.34/0.68 | POLISH_SUBU_FIRST |
| 2 | **2rJ8q1j8** | -1.39 | -1.37 | PASS | 0.0508 | 强负信号，sign-flip 潜力 | SIGN_FLIP_RETEST |
| 2 | **blvGa3dR** | -1.34 | -1.28 | PASS | 0.0456 | 强负信号，sign-flip 潜力 | SIGN_FLIP_RETEST |
| 2 | **akojVY7v** | -1.10 | -0.97 | PASS | 0.0309 | 中负信号，sign-flip 潜力 | SIGN_FLIP_RETEST |
| 3 | pw8Y6xaq | -0.90 | -0.66 | PASS | 0.0420 | 负信号 | SIGN_FLIP_REVIEW |
| 3 | np3xZ3Ez | -0.80 | -0.46 | PASS | 0.0644 | 负信号 | SIGN_FLIP_REVIEW |
| 3 | pw8Ypx3g | -0.80 | -0.46 | PASS | 0.0644 | 负信号 | SIGN_FLIP_REVIEW |
| 3 | gJxkJXol | -0.77 | -0.54 | PASS | 0.0425 | 负信号 | SIGN_FLIP_REVIEW |
| 3 | KPklEaLl | -0.71 | -0.45 | PASS | 0.0602 | 负信号 | SIGN_FLIP_REVIEW |
| 4 | 9qJZrnXe | 0.76 | 0.53 | PASS | 0.0903 | 弱正信号，参考分支 | WATCH_OR_BRANCH |
| 4 | mLZwMbb5 | 0.72 | 0.50 | FAIL | 0.2024 | 弱正+Concentrated+SubU | WATCH_OR_BRANCH |
| 5 | 6XzmdaWp | -1.11 | -1.57 | FAIL | 0.0249 | 低优先级 | LOW_PRIORITY |
| 5 | QPEZvL0M | -0.83 | -0.71 | FAIL | 0.0450 | 低优先级 | LOW_PRIORITY |
| 5 | 6Xzm2xv5 | -0.82 | -0.25 | FAIL | 0.9213 | 高Turnover | LOW_PRIORITY |
| 5 | rKApRxZ8 | -0.75 | -0.44 | FAIL | 0.0690 | 低优先级 | LOW_PRIORITY |

---

## Priority 1 — Grk1xjWZ 升阶修复

### 现状
- **Alpha ID**: Grk1xjWZ
- **Expression**: `group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), industry)`
- **Sharpe**: 1.57 ✅ | **Fitness**: 1.34 ✅ | **Sub-Universe**: 0.34 ❌ (limit 0.68)
- **Turnover**: 0.0585 ✅ | **Margin**: 0.00309 ✅

### 瓶颈
Sub-universe FAIL（0.34 vs 0.68），只有这一个失败项。核心 thesis 强（Sharpe 1.57），需要结构性修复而非参数调优。

### 修复策略
| 策略 | 描述 | 预期 |
|------|------|------|
| sector 替代 industry | 更宽的分组，看是否能覆盖更多 sub-universe | Sub-universe + |
| rank() 外层 wrapper | 打破时序依赖（QPn0vn3X/88Ob79jV 先例） | Sub-universe + |
| neutralizationBucket: bucket(rank(cap)) | 权重分散到 cap 分桶 | Sub-universe + |
| decay=6 或 8 | 轻微平滑，看是否能降低波动 | Sub-universe + |

---

## Priority 2 — Sign-Flip 升阶控制

### 2rJ8q1j8

| 字段 | 值 |
|------|---|
| **Alpha ID** | 2rJ8q1j8 |
| **Original Expression** | `group_neutralize(multiply(book_leverage_ratio_3, inverse(cash_burn_rate_v1)), industry)` |
| **Sign-Flip Expression** | `reverse(group_neutralize(multiply(book_leverage_ratio_3, inverse(cash_burn_rate_v1)), industry))` |
| **Original Sharpe** | -1.39 ❌ |
| **Original Fitness** | -1.37 ❌ |
| **Turnover** | 0.0508 ✅ |
| **Sub-Universe** | PASS ✅ |
| **Concentrated** | PASS ✅ |

**判断**: 原始强负信号，sign-flip 后可能转为强正。如果 reverse 能把 Sharpe 拉到 +1.25+，代表 `book_leverage_ratio_3 * inverse(cash_burn_rate_v1)` 有反向预测价值。

---

### blvGa3dR

| 字段 | 值 |
|------|---|
| **Alpha ID** | blvGa3dR |
| **Original Expression** | `divide(book_leverage_ratio_3, add(cash_burn_rate_v1, 1))` |
| **Sign-Flip Expression** | `reverse(divide(book_leverage_ratio_3, add(cash_burn_rate_v1, 1)))` |
| **Original Sharpe** | -1.34 ❌ |
| **Original Fitness** | -1.28 ❌ |
| **Turnover** | 0.0456 ✅ |
| **Sub-Universe** | PASS ✅ |
| **Concentrated** | PASS ✅ |

**判断**: ratio 形式的负信号，reverse 后比值反转（高 leverage/低 burn → 低 leverage/高 burn）。需要测试 industry neutralization 版本。

---

### akojVY7v

| 字段 | 值 |
|------|---|
| **Alpha ID** | akojVY7v |
| **Original Expression** | `subtract(book_leverage_ratio_3, cash_burn_rate_v1)` |
| **Sign-Flip Expression** | `reverse(subtract(book_leverage_ratio_3, cash_burn_rate_v1))` |
| **Original Sharpe** | -1.10 ❌ |
| **Original Fitness** | -0.97 ❌ |
| **Turnover** | 0.0309 ✅ |
| **Sub-Universe** | PASS ✅ |
| **Concentrated** | PASS ✅ |

**判断**: 差值形式的负信号，reverse 后变成 `cash_burn_rate_v1 - book_leverage_ratio_3`。幅度比前两个弱，但值得一测。

---

## Priority 3 — Sign-Flip Review（中等负信号）

| Alpha ID | Original Sharpe | Original Fitness | Sign-Flip Expression | Sub-Universe | Concentrated |
|----------|-----------------|-----------------|---------------------|--------------|--------------|
| pw8Y6xaq | -0.90 | -0.66 | `reverse(subtract(financial_statement_value_score, consensus_analyst_rating))` | PASS | PASS |
| np3xZ3Ez | -0.80 | -0.46 | `reverse(multiply(reverse(cash_burn_rate_v1), change_in_eps_surprise))` | PASS | PASS |
| pw8Ypx3g | -0.80 | -0.46 | `reverse(group_neutralize(multiply(reverse(cash_burn_rate_v1), change_in_eps_surprise), industry))` | PASS | PASS |
| gJxkJXol | -0.77 | -0.54 | `reverse(add(equity_value_score, reverse(cash_burn_rate_v1)))` | PASS | PASS |
| KPklEaLl | -0.71 | -0.45 | `reverse(multiply(subtract(financial_statement_value_score, consensus_analyst_rating), abs(earnings_momentum_analyst_score)))` | PASS | PASS |

**注意**: 这些信号相对较弱（Sharpe -0.7 到 -0.9），sign-flip 后预期 Sharpe 不会超过 1.0，除非 thesis 特别强。优先级低于 Priority 2 的三个强信号。

---

## Priority 4 — 弱正信号分支参考

| Alpha ID | Sharpe | Fitness | Expression | 问题 |
|----------|--------|---------|------------|------|
| 9qJZrnXe | 0.76 | 0.53 | `divide(consensus_analyst_rating, max(earnings_momentum_analyst_score, 0.1))` | 弱，但 Sub-universe PASS |
| mLZwMbb5 | 0.72 | 0.50 | `divide(beta_last_30_days_spy, add(book_leverage_ratio_3, 0.1))` | Sub-universe FAIL, Concentrated FAIL |

**判断**: 9qJZrnXe 可作为分支方向参考（analyst rating vs earnings momentum），但不是升阶优先级。mLZwMbb5 有多个结构性失败。

---

## 字段集中度警示

| 字段 | Variant 数量 | Avg Sharpe | 状态 |
|------|-------------|------------|------|
| cash_burn_rate_v1 | 21 | -0.38 | ⚠️ 集中 |
| beta_last_30_days_spy | 13 | -0.03 | ⚠️ 集中 |
| change_in_eps_surprise | 12 | 0.01 | ⚠️ 集中 |
| book_leverage_ratio_3 | 11 | -0.20 | ⚠️ 集中 |
| accrued_liabilities_total | 12 | 0.02 | ⚠️ 集中 |
| consensus_analyst_rating | 10 | -0.08 | ⚠️ 集中 |

**结论**: Sign-flip 测试后，如果 2rJ8q1j8/blvGa3dR/akojVY7v 的 reverse 版本都失败，说明 `cash_burn_rate_v1 / book_leverage_ratio_3` 这个字段对已经耗尽。需要开新字段方向。

---

## 完整 Expression 清单（Sign-Flip 专用）

### Grk1xjWZ 修复 Expression
```
# 当前（Sub-universe FAIL）
group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), industry)

# 修复候选 1: sector 替代 industry
group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector)

# 修复候选 2: rank() 外层 wrapper
rank(group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector))

# 修复候选 3: sector + cap bucket
group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector)
+ neutralizationBucket: bucket(rank(cap), range='0.1, 1, 0.1')

# 修复候选 4: decay=6 + sector
group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector)
+ decay: 6

# 修复候选 5: decay=8 + sector + cap bucket
group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector)
+ decay: 8
+ neutralizationBucket: bucket(rank(cap), range='0.1, 1, 0.1')
```

### Sign-Flip Expression 清单

```
# 2rJ8q1j8 — 强负信号
reverse(group_neutralize(multiply(book_leverage_ratio_3, inverse(cash_burn_rate_v1)), industry))

# blvGa3dR — 强负信号
reverse(divide(book_leverage_ratio_3, add(cash_burn_rate_v1, 1)))

# akojVY7v — 中负信号
reverse(subtract(book_leverage_ratio_3, cash_burn_rate_v1))
reverse(group_neutralize(subtract(book_leverage_ratio_3, cash_burn_rate_v1), industry))
reverse(group_neutralize(multiply(book_leverage_ratio_3, inverse(cash_burn_rate_v1)), sector))

# blvGa3dR variant with industry + cap bucket
reverse(divide(book_leverage_ratio_3, add(cash_burn_rate_v1, 1)))
+ neutralizationBucket: bucket(rank(cap), range='0.1, 1, 0.1')

# pw8Y6xaq — 中负信号
reverse(subtract(financial_statement_value_score, consensus_analyst_rating))

# np3xZ3Ez — 中负信号
reverse(multiply(reverse(cash_burn_rate_v1), change_in_eps_surprise))

# pw8Ypx3g — 中负信号
reverse(group_neutralize(multiply(reverse(cash_burn_rate_v1), change_in_eps_surprise), industry))

# gJxkJXol — 中负信号
reverse(add(equity_value_score, reverse(cash_burn_rate_v1)))

# KPklEaLl — 中负信号
reverse(multiply(subtract(financial_statement_value_score, consensus_analyst_rating), abs(earnings_momentum_analyst_score)))
```

---

## 下一步行动

1. **立刻**: Grk1xjWZ Sub-universe 修复 — 提交 5 个候选修复 expression
2. **立刻**: 2rJ8q1j8, blvGa3dR, akojVY7v sign-flip 测试 — 提交 4-6 个 sign-flip expression
3. **后续**: 如果 Priority 2 全部失败，开新字段方向（避免 cash_burn_rate_v1 / book_leverage_ratio_3）
4. **观察**: 9qJZrnXe 作为分支参考，但暂不投入升阶预算

---

## 原始数据来源

- Report: `/Users/zpdedn/Documents/github/worldquant-miner-main/.worktrees/ollama-deployment/.codex-run/lowfreq-generator/reports/overnight_alpha_report_20260522.md`
- CSV: `/Users/zpdedn/Documents/github/worldquant-miner-main/.worktrees/ollama-deployment/.codex-run/lowfreq-generator/reports/overnight_alpha_records_20260522.csv`
- Batch: `runs/candidate-batches/2026-05-22-grk1xjwz-rescue-signflip-batch.json`
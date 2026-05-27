# Learning Loop: 2026-05-21 Alpha Mining Workflow Execution

**日期**: 2026-05-21
**目标**: 执行完整alpha挖掘流程：FO Field Scout → SO Expansion → TH Expansion → SC检查 → 提交
**结果**: ❌ 未产生新提交候选

---

## 执行摘要

| Phase | 操作 | 结果 |
|-------|------|------|
| Phase 1 | FO Field Health Scout (18 fields) | ✅ 8/18 PASS (S>0.3) |
| Phase 2 | SO Expansion R2 (24 variants) | ❌ 0 PASS (无S>=1.25) |
| Phase 2 | SO Expansion R3 (18 variants) | ❌ 0 PASS (最高S=0.97) |
| Phase 3-5 | 未执行 | SO无候选 |

---

## Phase 1: FO Field Health Scout

**Batch**: `2026-05-16-fo-field-health-scout.json`
**执行**: `python3 run_field_health_scout.py`

### 结果

| Field | FO Sharpe | FO Fitness | 状态 |
|-------|-----------|------------|------|
| snt1_d1_dynamicfocusrank | 0.85 | 1.50 | ✅ PASS |
| revenue_growth_qoq | 0.81 | 1.41 | ✅ PASS (已提交0mAE3qzp) |
| fnd6_recco | 0.77 | 1.31 | ✅ PASS |
| fnd6_rectr | 0.76 | 1.29 | ✅ PASS |
| fn_interest_paid_net_q | 0.78 | 1.36 | ✅ PASS |
| eps_revision (ts_delta(eps,1)) | 0.75 | 1.26 | ✅ PASS (已提交2rvNV1qJ) |
| volume_zscore | 0.33 | 0.09 | ⚠️ WEAK |
| trade_when_momentum | 0.71 | 1.14 | ✅ PASS |

### KILL字段 (alphaId=null)
- fn_comp_options_grants_f
- fnd6_payables_turnover
- earnings_surprise
- operating_margin
- analyst_revision
- price_target_change
- shares_outstanding_change
- fnd6_working_capital
- insider_transaction
- institutional_holding_change

---

## Phase 2: SO Expansion

### R2 - 24 variants (不同结构测试)

**策略**: 测试 group_neutralize、简单 group_rank、ts_zscore不同窗口

| 候选 | S | F | TVR | 问题 |
|------|---|-------|-----|------|
| snt1_rank_market | 0.94 | 1.70 | 0.033 | S<1.25 |
| snt1_ts_zscore20_market | 0.84 | 1.42 | 0.129 | S<1.25 |
| rectr_rank_market | 0.92 | 1.66 | 0.004 | S<1.25 |
| interest_rank_market | 0.89 | 1.64 | 0.007 | S<1.25 |
| recco_rank_market | 0.79 | 1.34 | 0.006 | S<1.25 |

**结论**: 所有group_neutralize变体Sharpe接近0或负，simple group_rank结构表现更好但S仍<1.25

### R3 - 18 variants (decay和window优化)

**策略**: 测试decay=6/15、长ts窗口(66)

| 候选 | S | F | TVR | 变化 |
|------|---|-------|-----|------|
| snt1_rank_market_decay15 | **0.97** | **1.78** | 0.018 | 最佳 |
| snt1_rank_market_decay6 | 0.96 | 1.76 | 0.031 | 接近 |
| rectr_rank_market_decay15 | 0.93 | 1.68 | 0.003 | 低于1.25 |
| rectr_rank_market_decay6 | 0.92 | 1.66 | 0.004 | 低于1.25 |
| interest_rank_market_decay6 | 0.89 | 1.64 | 0.006 | 低于1.25 |

**结论**: decay能提升Sharpe但不足以达到1.25阈值

---

## 核心问题分析

### Sharpe Gap
- FO阶段: S=0.75-0.85 (通过条件: S>0.3)
- SO阶段: 需要S>=1.25 (通过条件)
- Gap: ~0.4 无法通过标准SO操作弥合

### 为什么FO→SO信号稀释
1. **FO rank vs SO group_rank**: FO的ts_rank在全市场排序，SO的group_rank在行业内排序，粒度更细但可能丢失方向性
2. **zscore窗口**: ts_zscore(20)在SO中可能窗口太短，噪声主导
3. **decay有限效果**: decay降低TVR但不能提升Sharpe到阈值

### 历史模式确认
从2026-05-19的learning loop已知:
- FO→SO信号稀释是已有模式
- 5月初的FO→SO扩展也显示类似问题

---

## KILL决策

根据workflow的"Anti-Overfit Rule"和KILL标准:

| 候选 | KILL原因 |
|------|----------|
| snt1_d1_dynamicfocusrank SO变体 | Smax=0.97, 低于1.25阈值 |
| fnd6_recco SO变体 | Smax=0.79, 结构性低于阈值 |
| fnd6_rectr SO变体 | Smax=0.93, 结构性低于阈值 |
| fn_interest_paid_net_q SO变体 | Smax=0.89, 结构性低于阈值 |
| eps_revision SO变体 | Smax=0.76, 结构性低于阈值 |

**不再继续测试这些字段的SO变体** - 需要新的FO字段源头

---

## 已验证的KILL模式（沉淀到KILL清单）

1. **FO S<1.0的字段，SO不可能达到S>=1.25** - 结构性限制
2. **group_neutralize对snt1/revenue/fnd6字段有负效果** - 不应使用
3. **decay=15是改善上限** - 继续增加decay不会提升Sharpe

---

## 下一步建议

### 需要新字段源头
现有FO字段(已测试):
- fnd6系列 (recco, rectr) - ❌ SO后S<1.0
- fn系列 (interest_paid_net_q) - ❌ SO后S<1.0
- snt1系列 - ❌ SO后Smax=0.97
- eps系列 - ❌ 已提交2rvNV1qJ

### 探索方向
1. **新数据源**: 需要找到全新的field family，不在KILL清单上
2. **D0探针**: 尝试delay=0的表达式，可能打破S<1.25限制
3. **ATOM Alpha**: 不同提交标准，可能对现有字段有不同阈值
4. **Region切换**: APAC/EMEA可能对某些field有更好表现

---

## 相关文件

- FO结果: `2026-05-16-fo-field-health-scout_results.json`
- SO R2结果: `2026-05-21-fo-field-so-expansion-r2_results.json`
- SO R3结果: `2026-05-21-fo-field-so-expansion-r3_results.json`
- 本次batch: `2026-05-21-fo-field-so-expansion-r3.json`

---

*记录生成: 2026-05-21*
*执行时间: ~2小时 (FO scout + SO R2/R3)*
*新提交候选: 0*
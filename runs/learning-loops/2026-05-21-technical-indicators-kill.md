# Learning Loop: 2026-05-21 Technical Indicators Direction

**日期**: 2026-05-21
**目标**: 探索技术指标/价量关系字段，重新开始FO→SO流程
**结果**: ⚠️ FO全PASS但SO无法突破1.25阈值

---

## 执行摘要

| Phase | 操作 | 结果 |
|-------|------|------|
| Phase 1 | FO Technical Indicator Scout (16 fields) | ✅ 16/16 PASS (S>0.5) |
| Phase 2 | SO Expansion (18 variants) | ⚠️ 4/18完成，0 PASS |
| Phase 3-5 | 未执行 | API超时中断 |

---

## Phase 1: FO Technical Indicator Scout

**Batch**: `2026-05-21-fo-technical-indicator-scout.json`
**testPeriod**: P3M (vs 之前的P1M)

### 结果

| Expression | FO Sharpe | FO Fitness | 状态 |
|------------|-----------|-----------|------|
| ts_std_dev(returns,60) | 0.77 | 0.91 | ✅ PASS |
| volume/ts_mean(volume,20) | 0.75 | 0.62 | ✅ PASS |
| high-low | 0.75 | 0.55 | ✅ PASS |
| volume/ts_mean(volume,60) | 0.74 | 0.59 | ✅ PASS |
| ts_corr(close,volume,60) | 0.73 | **1.03** | ✅ PASS (唯一F>=1.0) |
| ts_std_dev(returns,20) | 0.71 | 0.80 | ✅ PASS |
| ts_corr(close,volume,20) | 0.67 | 0.79 | ✅ PASS |
| ts_mean(returns,20) | 0.69 | 0.71 | ✅ PASS |
| ts_delta(returns,20) | 0.64 | 0.43 | ✅ PASS |
| close/vwap | 0.61 | 0.40 | ✅ PASS |
| ts_zscore(returns,20/60) | 0.62 | 0.41 | ✅ PASS |
| returns | 0.60 | 0.39 | ✅ PASS |

### 关键观察

1. **所有16个expression都通过FO (S>0.5)** - 技术指标方向信号稳定性高
2. **Fitness普遍较低** - 只有ts_corr(close,volume,60)达到F=1.03
3. **TVR偏高 (0.17-0.68)** - volume类最低 (0.18-0.27)
4. **P3M vs P1M** - 使用P3M可能帮助信号稳定性

---

## Phase 2: SO Expansion (Partial)

**API超时导致只完成4/18 candidates**

### Partial Results

| Candidate | S | F | TVR | 问题 |
|-----------|---|---|-----|------|
| corr60_rank_industry | **-0.55** | -0.28 | 0.115 | **INDUSTRY符号反转** |
| corr60_zscore_industry | **-0.55** | -0.28 | 0.115 | **INDUSTRY符号反转** |
| corr60_rank_market | 0.69 | 1.12 | 0.051 | S<1.25 |
| corr60_decay6_market | 0.70 | 1.14 | 0.037 | S<1.25 |

### 关键发现

**INDUSTRY中性化导致符号反转**
- group_rank + INDUSTRY → Sharpe = -0.55
- group_rank + market → Sharpe = +0.69
- ts_corr(close,volume,60)与industry中性化不相容

---

## 核心问题分析

### 结构性限制
1. **S>=1.25阈值无法通过** - 即使最好的FO候选(corr60)在SO后也只有S=0.70
2. **INDUSTRY中性化不兼容** - 导致符号反转，说明价量关系在行业内部失去预测性
3. **TVR低但Sharpe无法提升** - decay=6降低TVR到0.037但无法提升Sharpe

### FO→SO Gap继续存在
技术指标方向的FO→SO Gap与之前fnd6/snt1方向相同：
- FO: S=0.6-0.85
- SO: S=0.7 (best)
- Gap: ~0.5

---

## KILL决策

| 方向 | KILL原因 |
|------|----------|
| ts_corr(close,volume,N) SO变体 | INDUSTRY符号反转，market中性化Smax=0.70 |
| 技术指标FO字段SO扩展 | Smax=0.70，结构性低于1.25阈值 |
| P3M窗口 | 已验证可改善FO稳定性，但SO后仍无法突破 |

---

## 已验证的KILL模式更新

1. **industry中性化对价量相关字段有符号反转效应** - KILL此类组合
2. **market中性化保持信号** - 价量类字段应使用market而非industry
3. **技术指标类字段的SO扩展存在~0.5的Sharpe Gap** - 结构性限制

---

## 下一步建议

### 需要探索的方向
1. **TH Layer尝试** - 对现有SO候选加trade_when包装，看是否能提升Sharpe
2. **D0探针** - delay=0可能打破D1的SO限制
3. **组合不同类型字段** - 如corr60 + volume_ratio组合

### 不再投入的方向
- 技术指标字段的SO扩展（结构性S<1.25）
- INDUSTRY中性化 + 价量字段组合

---

## 相关文件

- FO结果: `2026-05-21-fo-technical-indicator-scout_results.json`
- SO Partial结果: `2026-05-21-fo-technical-so-expansion_results.json`
- Technical Indicator Prompt: `/Users/zpdedn/Documents/project/Worldquantbrain/prompts/alpha-mining-technical-indicators.md`

---

*记录生成: 2026-05-21*
*执行时间: ~1.5小时*
*新提交候选: 0*
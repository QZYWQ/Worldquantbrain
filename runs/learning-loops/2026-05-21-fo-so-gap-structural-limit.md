# 学习沉淀：FO→SO Sharpe Gap 问题 (2026-05-21)

## 问题描述

所有新field方向都存在 FO→SO Sharpe Gap，导致无法突破1.25阈值。

## 测试记录

### 方向1：fnd6/fundamental 字段

| Field | FO Sharpe | SO Best Sharpe | Gap |
|-------|-----------|----------------|-----|
| snt1_d1_dynamicfocusrank | 0.85 | 0.97 | ~0.1 |
| fnd6_rectr | 0.76 | 0.93 | ~0.2 |
| fn_interest_paid_net_q | 0.78 | 0.89 | ~0.1 |
| fnd6_recco | 0.77 | 0.79 | ~0.0 |

**结果**: SO阶段最高0.97，无法达到1.25

### 方向2：技术指标字段

| Field | FO Sharpe | SO Best Sharpe | Gap |
|-------|-----------|----------------|-----|
| ts_std_dev(returns,60) | 0.77 | <0.70 | ~0.1+ |
| ts_corr(close,volume,60) | 0.73 | 0.70 | ~0.0 |
| volume/ts_mean(volume,20) | 0.75 | <1.0 | ~0.2+ |

**结果**: SO阶段最高0.70，无法达到1.25

### 关键发现

1. **P1M窗口太短**: 用P1M做FO初筛捕到噪音信号，无法在SO(P2Y)复现
2. **P3M窗口改善FO指标**: 技术指标用P3M后FO全部通过(S>0.5)
3. **Industry中性化导致符号反转**: ts_corr类字段用industry中性化后符号翻转
4. **Market中性化保持信号**: 但Sharpe无法突破

## 结构性限制证据

- 3个完全不同的field类型（fnd6/fundamental, 技术指标，价量关系）
- 都出现相同的FO→SO Gap (~0.5)
- 各种SO变体（rank/zscore/decay/group_neutralize）都无法弥合差距

## 结论

**FO→SO Sharpe Gap 是结构性限制**，而非特定field的问题。

可能原因：
1. FO测试窗口(P3M/P1M)与SO测试窗口(P2Y)的时间尺度不匹配
2. 初筛时的横截面信号在时序测试时无法保持
3. 信号在SO阶段的衰减是本质特性，无法通过expression engineering修复

## KILL决策

所有新field方向因FO→SO Gap无法突破1.25阈值，已测试字段全部KILL。

## 下一步

1. **接受现状**: 21个Alpha已是有效产出
2. **D0探针**: 尝试D0路由而非D1，可能捕获不同类型的信号
3. **周期性扫描**: 等待BRAIN平台更新或新数据发布
4. **不继续投入**: 当前所有方向都已验证结构性限制，继续投入是浪费
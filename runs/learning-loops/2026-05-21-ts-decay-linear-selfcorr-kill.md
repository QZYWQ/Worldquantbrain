# 学习沉淀：ts_decay_linear 家族自相关问题

**日期**: 2026-05-21
**问题**: ts_decay_linear 家族所有变体Self-Correlation超标(>0.7)，无法提交
**状态**: KILL

---

## 家族基本信息

### 核心结构
```
group_neutralize(ts_decay_linear((-ts_zscore(returns,252))*group_rank(...),40), subindustry)
```

### 候选规模
- top-candidates-2026-05-21.json 中约 70+ 个变体
- Sharpe范围: 1.47-2.03
- Fitness范围: 0.87-1.58
- TVR范围: 0.07-0.28

---

## 测试的修复方案（全部失败）

| 方案 | 方法 | 结果 | 原因 |
|------|------|------|------|
| rank()外层包装 | rank(base) | SC 0.78-0.86 | 外层rank无法消除内部时序依赖 |
| zscore()包装 | zscore(base) | SC 0.85+ | 同上 |
| group_rank封装 | group_rank(base, subindustry) | SC 0.78+ | 同上 |
| densify(bucket(rank(cap))) | 外层densify wrapper | SC 0.80+ | densify作用于输出，无法修复内部结构 |
| ts_delay(rank(...), 5) | 信号延迟 | Sharpe/Fitness崩溃 | 延迟破坏信号有效性 |
| 不同decay (20, 30) | 增加decay | TVR降低但SC不变 | decay只影响TVR，不影响SC |
| 不同neutralization | sector/industry/bucket | SC无改善 | neutralization只改变横截面，不改变时序自相关 |
| group_neutralize双层 | 嵌套neutralize | SC相同 | 结构未变 |

### 结论

**ts_decay_linear 家族具有结构性自相关**——问题根源在于 `ts_decay_linear` 内部的 `ts_zscore(returns,252)` 计算方式在时序上产生自相关。外层任何包装操作（rank、zscore、densify等）都无法消除这种内部时序依赖。

这与已KILL的 `trade_when(ts_corr(close,volume,20)<0,...)` 家族问题相同：**结构性FAIL，简单的表达式变换无法修复**。

---

## 非 ts_decay_linear 候选检测结果

| Alpha ID | Sharpe | Fitness | TVR | SC | 其他检查 | 结果 |
|----------|--------|---------|-----|-----|----------|------|
| LLglqor2 | 2.73 | 6.15 | 0.074 | PENDING | CONCENTRATED_WEIGHT=FAIL, LOW_SUB_UNIVERSE=FAIL | 无法提交 |
| KPwQ2Pjz | 1.71 | 1.12 | 0.154 | 0.9652 | PASS | SC结构性FAIL |
| kqLMrxKk | 1.59 | 1.01 | 0.185 | 0.7651 | PASS | SC偏高 |

### LLglqor2 分析

**表达式**: `group_neutralize(ts_zscore(growth_potential_rank_derivative, 20), industry)`

**优点**:
- Sharpe=2.73, Fitness=6.15（所有候选中最高）
- TVR=0.074（极低）
- 使用新字段 `growth_potential_rank_derivative`（MEMORY中无记录）

**问题**:
- CONCENTRATED_WEIGHT=0.5 (FAIL)
- LOW_SUB_UNIVERSE_SHARPE=0.78 (FAIL)

**修复尝试方向**（未验证）:
- 换用 sector 中性化替代 industry
- 增加 rank() 外层降低权重集中度
- 调整 decay 观察影响

**结论**: 即使指标优秀，权重集中问题阻止提交。

### ts_rank 家族 (KPwQ2Pjz, kqLMrxKk)

**表达式**: `group_rank(ts_rank(earnings_per_share_median_value/close, 84), subindustry)`

**问题**: SC分别为0.9652和0.7651，ts_rank结构本身产生高自相关。

**结论**: KILL

---

## 经验沉淀

### 1. 自相关问题的分类

| 类型 | 特征 | 解决方案 | 例子 |
|------|------|----------|------|
| 包装不足 | 外层wrapper效果有限 | 需要结构性改变 | ts_decay_linear |
| 结构性FAIL | 任何wrapper都无效 | KILL，放弃该结构 | trade_when(ts_corr), ts_rank |
| 可修复 | 适当wrapper或参数调整有效 | rank/densify/decay优化 | gJmojOQm, QPn0vn3X |

### 2. densify/bucket 策略的适用边界

**有效场景**（gJmojOQm模式）:
- 输出层直接使用 `densify(bucket(rank(cap)))` 作为信号成分
- 需要与基础信号有足够差异性

**无效场景**:
- 作为外层包装应用于本身就高自相关的信号
- 应用于 `ts_decay_linear` 内部

### 3. 权重集中度问题

CONCENTRATED_WEIGHT FAIL通常意味着:
- 信号在某类股票上暴露过大
- 中性化粒度不够（industry vs sector vs bucket）
- 解决方案: 换用更粗粒度的neutralization，或在信号构建早期引入分散化

### 4. 新字段的价值

`growth_potential_rank_derivative` 虽然因权重问题无法提交，但:
- 是全新字段，无correlation budget消耗
- S=2.73, F=6.15说明信号质量极佳
- 如果能解决权重问题，可能成为可用候选

---

## 决策

| 家族 | 决策 | 理由 |
|------|------|------|
| ts_decay_linear (70+变体) | **KILL** | 结构性SC FAIL，所有修复方案无效 |
| ts_rank(earnings_per_share) | **KILL** | SC结构性FAIL |
| LLglqor2 (growth_potential) | **保留观察** | 指标优秀但权重问题，需进一步验证是否可修复 |

---

## 下一步研究方向

### 1. 短期（止血）
- 对LLglqor2做最后修复尝试（sector中性化 + rank外层）
- 如果失败，彻底放弃该候选

### 2. 中期（新字段发现）
- FO Field Scout: model51_* 系列
  - `model51_beta`
  - `model51_correlation`
  - `model51_systematic_risk`
- Field health diagnostic先行，验证可用性再投入升阶预算

### 3. 不再投入的方向
- ts_decay_linear家族的任何变体
- ts_rank包装变体
- 已提交的family的同field siblings

---

## 相关文件

- 候选列表: `runs/simulation-captures/top-candidates-2026-05-21.json`
- 升阶结果: `runs/simulation-captures/may19_upgrade_results.json`
- 诊断测试: 见用户提供的6种densify wrapper变体测试表

---

**教训**: 当一种结构（如ts_decay_linear）的所有变体都显示相同的SC问题时，说明问题在结构层面而非表达式层面。此时应该止损KILL，而非继续投入模拟预算做无效的表达式变换。**
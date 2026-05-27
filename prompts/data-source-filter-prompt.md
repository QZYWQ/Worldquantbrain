# WorldQuant BRAIN 数据源筛选提示词模板

## 使用场景
当需要评估新数据字段、发现可挖掘的alpha方向、或在构建alpha前验证field可用性时使用此提示词。

---

## 标准提示词

```
## 角色
你是一个WorldQuant BRAIN量化研究助手，负责数据源筛选和field health诊断。

## 项目骨架
- 项目路径: /Users/zpdedn/Documents/project/Worldquantbrain
- 核心文档: CLAUDE.md, AGENTS.md, templates/
- Skill: worldquant-brain-alpha-engineering

## 当前任务
我需要分析/筛选一个新的BRAIN数据字段。

## 已知信息（如有）
- 字段名: [填写字段名]
- 所属数据集: [填写数据集]
- 初步观察: [任何初步想法]

## 我的目标
1. 遵循BRAIN官方field health诊断标准流程（6项检测）
2. 评估该字段是否值得构建alpha family
3. 避免已KILL的家族和已提交family的correlation budget
4. 遵循worldquant-brain-alpha-engineering skill的方法论

## BRAIN TIPS 6项field health检测标准

请使用以下6个表达式在 **None neutralization + decay=0** 环境下进行模拟：

### 检测1: 覆盖率
```
datafield != 0 ? 1 : 0
```
- 用途: 估算% coverage = (Long Count + Short Count) / Universe Size
- 解读: Long Count指示每日平均非零值数量

### 检测2: 更新频率
```
ts_std_dev(datafield, N) != 0 ? 1 : 0
```
- N=5(周), N=22(月), N=66(季度), N=252(年)
- 用途: 判断数据是日更新/周更新/月更新/季更新/年更新
- 解读: std=0说明数据在N天内不变（常量）

### 检测3: 数据边界
```
abs(datafield) > X
```
- 用途: 确定field的数值范围
- X=1: 检查是否归一化到[-1, +1]
- 变化X值观察Long Count变化

### 检测4: 长期中位数
```
ts_median(datafield, 1000) > X
```
- 用途: 检查5年期的field中位数
- 调整X值观察Long Count

### 检测5: 分布检验
```
X < scale_down(datafield) && scale_down(datafield) < Y
```
- 用途: 检查field在[0,1]区间的分布
- scale_down类似MinMaxScaler，保持原始分布

### 检测6: 负值检查（重要！）
```
datafield <= 0 ? 1 : 0
```
- 用途: 检查field是否有非正值
- 如Long/Short都是0，说明field全为正（不能用于某些中性化）

## Field优先级判断标准

### 高优先级field特征
- Coverage > 30%
- 日更新或周更新（非年更）
- 有明确的经济学含义
- 与已有submitted family无重叠

### 低优先级field特征
- Coverage < 10%
- 年更数据（信息量太少）
- 与已KILL的family相同（news_sentiment_momentum, model_rerating_derivative等）
- 与已submitted family使用相同field组合

## 评估输出格式

请按以下格式输出：

```
## Field Health诊断结果

### 1. [字段名]
- 覆盖率: X%
- 更新频率: [日/周/月/季/年]
- 边界: [具体范围]
- 分布: [分布特征]
- 风险: [已占用family/correlation风险]

### 2. Alpha方向建议
- Hypothesis: [做什么预测]
- Field: [使用的field]
- 初步表达式: [最简baseline]
- 主要风险: [可能的失败原因]

### 3. 家族归属判断
- 是否与已submitted family重叠? [是/否]
- 如果重叠: [重叠的family名]
- 如果不重叠: [新family方向]
```

## 关键参考

### 已提交Family（避免重复）
- fnd6_rectr/fnd6_recd: RRNmMErj, 1YopVrdW, xAeN6jGp
- fnd6_prstkc: 1YodbWO6
- eps_revision: 2rvNV1qJ
- revenue_growth: 0mAE3qzp

### 已KILL的Family（避免浪费）
- model_rerating_derivative (frozen)
- news_sentiment_momentum (EVENT field不能用ts_rank)
- social_buzz_acceleration (alphaId=null)
- options/volatility fields (industry effect)
- fscore_total family (weight concentration)
- historical_volatility (weight concentration)

## 注意事项
1. 在使用field前必须先做6项检测
2. 不要假设field存在，先验证
3. 优先考虑D1方向（delay=1）
4. 遵循"早死快死"原则 - 发现问题立即kill
5. Fitness是关键指标，Sharpe是门槛

---
```

## 使用示例

### 示例1: 发现新field
```
我发现了 fn_interest_paid_net_q 这个字段，看起来可能是财务数据，请帮我：
1. 用6项检测验证field health
2. 判断是否值得构建alpha family
3. 如果可以构建，给出3个初步alpha方向
```

### 示例2: 优化已有alpha时发现新方向
```
我在优化 WjN75gAO (fnd6_sppe/fnd6_siv) 时发现 ts_mean(fn_interest_paid_net_q, 20) 有高Fitness
请帮我：
1. 对fn_interest_paid_net_q做完整field health诊断
2. 判断这个field是否可以单独构建新family
3. 与已有的fnd6_sppe family做correlation风险评估
```

### 示例3: 批量field扫描
```
请帮我扫描以下field是否有alpha潜力：
- fn_liab_fair_val_a
- fn_antidilutive_securities_excl_from_eps_a
- fnd6_aox

对每个field：
1. 用检测1-3确认基本可用性
2. 给出覆盖率、更新频率、边界
3. 评估是否值得进一步研究
```

---

## 更新日志
- 2026-05-17: 初始版本，结合BRAIN TIPS 6项检测和项目骨架
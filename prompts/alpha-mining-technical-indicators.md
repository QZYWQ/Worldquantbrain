# Alpha Mining - 技术指标方向

## 任务

切换到**技术指标/价量关系字段**，重新开始FO→SO→TH→SC全流程。

---

## 当前状态

- 已提交Alpha: 21个（主力）
- KILL清单已满（ts_decay_linear, model51, fn_interest, ts_rank等）
- FO→SO Gap问题：P1M窗口太短，需换方向

---

## 新方向：技术指标/价量关系

### 目标字段类型

**价量关系类**:
- `close/vwap` — 价格相对价值中枢位置
- `volume/ts_mean(volume, N)` — 量能相对均值
- `returns` — 收益率
- `high-low` / `close-low` / `close-high` — 价格波动

**趋势类**:
- `ts_zscore(returns, N)` — 收益标准化
- `ts_zscore(close/vwap, N)` — 价格相对位置标准化
- `ts_corr(close, volume, N)` — 价量相关性

**波动类**:
- `ts_std_dev(returns, N)` — 收益波动率
- `ts_std_dev(close/vwap, N)` — 价格波动率

**趋势动量类**:
- `ts_mean(returns, N)` — 移动平均收益
- `ts_delta(returns, N)` — 收益变化

---

## Phase 1: FO Field Health Scout（技术指标）

对以下字段做FO初筛（testPeriod=P1M, neutralization=NONE）:

```python
technical_fields = [
    'close/vwap',
    'volume/ts_mean(volume,20)',
    'volume/ts_mean(volume,60)',
    'returns',
    'high-low',
    'close-low',
    'close-high',
    'ts_zscore(returns,20)',
    'ts_zscore(returns,60)',
    'ts_zscore(close/vwap,20)',
    'ts_zscore(close/vwap,60)',
    'ts_corr(close,volume,20)',
    'ts_corr(close,volume,60)',
    'ts_std_dev(returns,20)',
    'ts_std_dev(returns,60)',
    'ts_mean(returns,20)',
    'ts_mean(returns,60)',
    'ts_delta(returns,5)',
    'ts_delta(returns,20)',
]
```

**FO测试表达式模板**:
```python
expression = "rank(<field>)"
settings = {
    'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
    'delay': 1, 'decay': 0, 'neutralization': 'NONE',
    'truncation': 0.08, 'pasteurization': 'ON',
    'testPeriod': 'P1M', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
    'language': 'FASTEXPR'
}
```

**筛选标准**: FO Sharpe > 0.5, LongCount > 500, Fitness > 0.5

---

## Phase 2: SO Expansion

对FO通过的字段做SO expansion

**标准SO变体**:
```python
candidates = [
    {'name': 'rank_industry', 'expr': 'rank(<field>)', 'settings': {}},
    {'name': 'rank_market', 'expr': 'rank(<field>)', 'settings': {}},
    {'name': 'zscore_industry', 'expr': 'zscore(<field>)', 'settings': {}},
    {'name': 'group_rank_industry', 'expr': 'group_rank(rank(<field>), industry)', 'settings': {}},
    {'name': 'group_rank_market', 'expr': 'group_rank(rank(<field>), market)', 'settings': {}},
    {'name': 'decay15_market', 'expr': 'group_rank(rank(<field>), market)', 'settings': {'decay': 15}},
    {'name': 'decay6_market', 'expr': 'group_rank(rank(<field>), market)', 'settings': {'decay': 6}},
    {'name': 'ts_zscore_20', 'expr': 'ts_zscore(<field>, 20)', 'settings': {}},
    {'name': 'ts_mean_22', 'expr': 'ts_mean(<field>, 22)', 'settings': {}},
    {'name': 'subindustry_neutral', 'expr': 'group_neutralize(rank(<field>), subindustry)', 'settings': {}},
]
```

**通过标准**: Sharpe >= 1.25, Fitness >= 1.0, TVR <= 0.7

---

## Phase 3: TH Expansion

对SO通过的候选做trade_when等高阶包装

**TH变体**:
```python
th_variants = [
    {'name': 'rank_rank', 'expr': 'rank(rank(<base>))'},
    {'name': 'rank_zscore', 'expr': 'rank(zscore(<base>))'},
    {'name': 'zscore_rank', 'expr': 'zscore(rank(<base>))'},
    {'name': 'tw_volume', 'expr': 'trade_when(rank(volume/ts_mean(volume,20))>0.6, <base>, -1)'},
    {'name': 'tw_sentiment', 'expr': 'trade_when(ts_rank(scl12_sentiment_fast_d1,20)>0.6, <base>, -1)'},
    {'name': 'quantile_low', 'expr': 'quantile(<base>, 0.2)'},
    {'name': 'quantile_high', 'expr': 'quantile(<base>, 0.8)'},
]
```

---

## Phase 4: Self-Correlation 检查

**通过标准**: SC < 0.7

**SC修复策略**:
1. decay调整 (10→15→20)
2. rank外层包装
3. 换neutralization粒度

**结构性FAIL（KILL）**: 各种wrapper都无效 → KILL

---

## Phase 5: 提交决策

**硬性阈值**:
- Sharpe >= 1.25
- Fitness >= 1.0
- TVR <= 0.7
- Self-Correlation < 0.7

---

## 执行命令

```bash
cd /Users/zpdedn/Documents/github/worldquantAPI/user

# Phase 1: FO technical indicators
# 手动创建测试batch或用run_field_health_scout.py

# Phase 2: SO expansion
python3 run_fo_field_so_expansion.py

# Phase 3: TH expansion
python3 run_alpha_upgrade_v2.py --json-file <batch>.json --limit 5 --max-variants 6

# Phase 4: SC check
python3 run_batch_sc_check.py

# Phase 5: submit
python3 check_submissible.py <alpha_id>
```

---

## 注意事项

1. **技术指标字段不是FROZEN，可以测试**
2. **跳过KILL清单**（ts_decay_linear, trade_when(ts_corr), ts_rank(earnings)等）
3. **每个field测1-2个快速表达式，不行就KILL**
4. **FO阶段注意时间窗口匹配问题**（P1M可能太短，考虑P3M）
5. **价量类字段注意与returns_vwap family区分**（88Ob79jV已提交）

---

## 开始执行

按顺序执行 Phase 1 → 2 → 3 → 4 → 5
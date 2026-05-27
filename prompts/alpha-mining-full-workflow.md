# Alpha Mining 全流程任务

## 目标

执行完整 alpha 挖掘流程：扫新 field → 选候选 → 升阶 → 测试 → 测自相关性

---

## 当前状态

### 已提交Alpha（主力）
共 **21个**，覆盖16个family，correlation budget已分散。

### KILL清单（必须跳过）

**结构性FAIL（任何变体都不要测）**:
- `ts_decay_linear` 家族 — SC 0.78-0.89，6种wrapper无效
- `trade_when(ts_corr(...))` — 结构性SC FAIL
- `ts_rank(earnings/close, ...)` — SC 0.77-0.97
- `returns_vwap`, `tobins_q`, `scl12_sentiment` 同批次FAIL

**负Sharpe/低Fitness**:
- `model51_beta`, `model51_correlation`, `model51_systematic_risk` — 全部负Sharpe
- `fn_interest_paid_net_q` — Fitness始终<1.0
- `fnd6_recco`, `fnd6_rectr` — SO后信号消失
- `growth_potential_rank_derivative` — CONCENTRATED_WEIGHT=0.5 FAIL

**FROZEN字段**:
- `multi_factor_static_score_derivative`
- `relative_valuation_rank_derivative`
- `anl4_afv4_dts_spe`
- `anl4_afv4_median_eps`

**Field不存在**:
- `nws18_qcm`, `scl12_buzz`, `short_interest`
- `vsm3_iv_skew`, `vsm3_iv_smile`, `vsm3_iv_atm`

---

## 已提交Family（不要追同field siblings）

| Family | 字段 | 提交ID |
|--------|------|--------|
| close_delta | ts_delta(close,1) | O0bXoVV1 |
| returns_vwap | returns, vwap | 88Ob79jV |
| tobins_q_ratio | tobins_q_ratio | GrnExm2Q |
| assets_cap | assets/cap | e7dPWeop |
| eps_family | eps/close | A1gVE97w |
| sentiment | scl12_sentiment | bloqmdJK |
| sales_estimate | sales_estimate_count | A1g6AlWg |
| total_assets | anl4_totassets_flag | Xg2X2jxl |
| unsystematic_risk | unsystematic_risk_last_60_days | gJmojOQm |
| range | high-low, close-low | LLgOWZmn |
| revenue_growth | revenue_growth_qoq, market | 0mAE3qzp |
| fnd6_prstkc | fnd6_prstkc | 1YodbWO6 |
| eps_revision | ts_delta(eps,1), market | 2rvNV1qJ |
| fnd6_rectr_recd | fnd6_rectr/fnd6_recd | RRNmMErj等 |
| fnd6_sppe_siv | fnd6_sppe/(abs(fnd6_siv)+1) | 1YoX2GxX |
| trade_when_sector | trade_when, ts_std_dev(returns,60), sector | QPn0vn3X |

---

## 完整工作流

### Phase 1: 扫新 Field（FO Field Health Scout）

**目标**：找 FO Sharpe > 0.6 的新 field

**脚本**:
```bash
cd /Users/zpdedn/Documents/github/worldquantAPI/user
python3 run_field_health_scout.py
```

**快速测试表达式**（decay=0, neutralization=None, testPeriod=P1M）:
```python
# 每个field做这个测试
expression = "rank(<field>)"
settings = {
    'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
    'delay': 1, 'decay': 0, 'neutralization': 'NONE',
    'truncation': 0.08, 'pasteurization': 'ON',
    'testPeriod': 'P1M', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
    'language': 'FASTEXPR'
}
```

**筛选标准**: FO Sharpe > 0.6, LongCount > 500, Fitness > 0.5

---

### Phase 2: SO Expansion（第一轮升阶）

对 FO 通过的 field 做 SO expansion

**脚本**:
```bash
cd /Users/zpdedn/Documents/github/worldquantAPI/user
python3 run_fo_field_so_expansion.py
# 或自定义batch
python3 run_fn_interest_paid_net_q_so.py
```

**标准 SO 变体**（每个 field 测试这些）:
```python
candidates = [
    {'name': 'rank_base', 'expr': 'rank(<field>)', 'settings': {}},
    {'name': 'zscore_base', 'expr': 'zscore(<field>)', 'settings': {}},
    {'name': 'group_rank_industry', 'expr': 'group_rank(rank(<field>), industry)', 'settings': {}},
    {'name': 'group_rank_market', 'expr': 'group_rank(rank(<field>), market)', 'settings': {}},
    {'name': 'decay15_market', 'expr': 'group_rank(rank(<field>), market)', 'settings': {'decay': 15}},
    {'name': 'decay6_market', 'expr': 'group_rank(rank(<field>), market)', 'settings': {'decay': 6}},
    {'name': 'ts_zscore_20', 'expr': 'ts_zscore(<field>, 20)', 'settings': {}},
    {'name': 'ts_mean_22', 'expr': 'ts_mean(<field>, 22)', 'settings': {}},
]
```

**通过标准**: Sharpe >= 1.25, Fitness >= 1.0, TVR <= 0.7

---

### Phase 3: TH Expansion（第二轮升阶）

对 SO 通过的候选做 TH (trade_when, quantile等)

**脚本**:
```bash
cd /Users/zpdedn/Documents/github/worldquantAPI/user
python3 run_alpha_upgrade_v2.py --json-file <batch>.json --limit 5 --max-variants 6
```

**TH 变体模板**:
```python
th_variants = [
    {'name': 'th_rank_rank', 'expr': 'rank(rank(<base>))'},
    {'name': 'th_rank_zscore', 'expr': 'rank(zscore(<base>))'},
    {'name': 'th_tw_sentiment', 'expr': 'trade_when(ts_rank(scl12_sentiment_fast_d1,20)>0.6, <base>, -1)'},
    {'name': 'th_tw_volume', 'expr': 'trade_when(rank(volume/ts_mean(volume,20))>0.6, <base>, -1)'},
    {'name': 'th_quantile_low', 'expr': 'quantile(<base>, 0.2)'},
    {'name': 'th_quantile_high', 'expr': 'quantile(<base>, 0.8)'},
]
```

---

### Phase 4: Self-Correlation 检查

**目标**: 确保 SC < 0.7

**脚本**:
```bash
cd /Users/zpdedn/Documents/github/worldquantAPI/user
python3 run_batch_sc_check.py
# 或对单个alpha
python3 -c "
from machine_lib import check_submission
check_submission(['<alpha_id>'], [], 0)
"
```

**API调用**:
```python
# 获取alpha详情
r = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
checks = r.json().get('is', {}).get('checks', [])
sc_check = next((c for c in checks if c['name'] == 'SELF_CORRELATION'), None)
sc_value = sc_check['value'] if sc_check else None
```

**SC修复策略**（SC >= 0.7 时）:
1. 增加 decay（10→15, 15→20）
2. 加 rank() 外层包装
3. 换 neutralization 粒度（industry→sector→market）
4. 如果SC结构性FAIL（各种wrapper都无效），KILL该候选

---

### Phase 5: 提交决策

**提交标准**（硬性阈值）:
- Sharpe >= 1.25
- Fitness >= 1.0
- TVR <= 0.7
- Self-Correlation < 0.7
- CONCENTRATED_WEIGHT < 阈值（通常0.3）
- LOW_SUB_UNIVERSE_SHARPE > 阈值（通常0.8）

**提交脚本**:
```python
from machine_lib import check_submission, view_alphas

stone_bag = [alpha_id1, alpha_id2, ...]
gold_bag = []
gold_bag = check_submission(stone_bag, gold_bag, 0)
print(f'通过检查: {len(gold_bag)}')
if gold_bag:
    view_alphas(gold_bag)
```

---

## 关键脚本位置

| 脚本 | 用途 |
|------|------|
| `run_field_health_scout.py` | FO field health 诊断 |
| `run_fo_field_so_expansion.py` | FO field SO expansion |
| `run_alpha_upgrade_v2.py` | 批量升阶（SO+TH） |
| `run_batch_sc_check.py` | 批量SC检查 |
| `check_submissible.py` | 单alpha提交检查 |
| `machine_lib.py` | 核心库（check_submission, view_alphas） |

---

## 输出要求

1. **每个phase记录结果**:
   - FO: 通过的field列表（FO Sharpe, LongCount）
   - SO: 通过的候选列表（Sharpe, Fitness, TVR）
   - TH: 通过的候选列表
   - SC: 每个候选的SC值，标记PASS/FAIL

2. **及时KILL**:
   - FO阶段Fitness<0.5 → KILL
   - SO阶段Fitness<1.0 → KILL
   - SC结构性FAIL → KILL，不要继续尝试wrapper

3. **保存证据**:
   - 每个batch结果保存到 `runs/simulation-captures/<batch_name>_results.json`
   - 重要决策记录到 `runs/learning-loops/<date>-<topic>.md`

---

## 执行命令模板

```bash
# 1. FO field health scout
cd /Users/zpdedn/Documents/github/worldquantAPI/user
python3 run_field_health_scout.py 2>&1 | tee /tmp/fo_scout.log

# 2. 对通过的field做SO expansion（创建batch json后）
python3 run_fo_field_so_expansion.py

# 3. SO通过后批量升阶
python3 run_alpha_upgrade_v2.py --json-file <batch>.json --limit 10 --max-variants 6

# 4. SC检查
python3 run_batch_sc_check.py

# 5. 提交
python3 check_submissible.py <alpha_id>
```

---

## 注意事项

1. **跳过KILL清单上的任何field/family**
2. **不要测试 ts_decay_linear, trade_when(ts_corr), ts_rank(earnings) 任何变体**
3. **不要追已提交family的同field siblings**
4. **FO阶段每个field只测1-2个快速表达式，不行就KILL**
5. **SC修复优先用decay调整，其次rank wrapper，最后换neutralization**
6. **结构性FAIL（所有wrapper都无效）立即KILL，不要继续**

---

## 开始执行

按顺序执行 Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5，每个phase完成后报告结果再进入下一个。
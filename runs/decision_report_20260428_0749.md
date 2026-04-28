# BRAIN_LAB 优化闭环最终决策报告

- 生成时间：2026-04-28 07:49:29 (Asia/Shanghai)
- 优化轮次：1 轮
- 运行模式：完全离线
- 真实提交：未执行
- `agent-policies/`：未修改
- 最新 batch：`runs/evolution/generations/opt-r1/gen_001.batch.json`
- 最新 canonical：`runs/evolution/generations/opt-r1/gen_001.json`

## 结论

- 当前 batch 的结构质量评级：**A**。
- 这次调整把平均 surrogate_score 从 0.088 提升到 0.241，平均 novelty 从 0.288 提升到 0.386，平均与 winners 的结构相似度从 0.315 降到 0.231。
- `trivial_identity_count` 从 2 降到 0，退化 `x/x`、`x-x` 类结构已被拦截。

## 调整内容

- Adjusted `harness/lib/evolution/evolution_config.json` to push exploration without losing ranking discipline: mutation 0.18, crossover 0.8, elite fraction 0.05, tournament size 2, novelty floor 0.12, and explicit score/complexity weights.
- Made surrogate scoring config-driven in `harness/lib/evolution/engine.py`, switched complexity to a linear operator/field/parameter penalty, and added a trivial self-division/self-subtraction guard.
- Broadened the winner field pool in `harness/lib/evolution/population.py` by collecting historical `field_name` values before eligibility filtering.
- Reduced same-group operator replacement bias and added `ts_mean` / `ts_std` wrappers in `harness/lib/evolution/mutation.py` to widen operator shapes.

## Round 1 结果概览

- canonical candidates: 20
- average novelty: 0.386
- unique operator types: 7
- unique field types: 16
- average winner similarity: 0.231
- dry-run planned candidates: 10
- dry-run top recommendations: 10
- dry-run score avg: 0.730

### Canonical top 10

| rank | candidate_id | expression | surrogate_score | novelty | avg winner similarity |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | `gen001-ff353e8040c3` | `bucket(pv13_revere_index_value, 61)` | 0.441 | 0.667 | 0.008 |
| 2 | `gen001-3fd59d915c2f` | `ts_count_nans(pv13_revere_index_value, 60)` | 0.437 | 0.667 | 0.008 |
| 3 | `gen001-18712db91872` | `ts_rank(sentiment_focus_rank, 60)` | 0.434 | 0.667 | 0.161 |
| 4 | `gen001-8c5bbca421a8` | `ts_rank(anl4_af_eps_value / close, 60)` | 0.263 | 0.400 | 0.184 |
| 5 | `gen001-af24b0eee1d1` | `ts_rank(anl4_afv4_median_eps/close, 60)` | 0.263 | 0.400 | 0.176 |
| 6 | `gen001-92a9530b91f6` | `ts_rank(earnings_per_share_average/close, 120)` | 0.254 | 0.400 | 0.179 |
| 7 | `gen001-5caf569d9422` | `group_rank(ts_rank(fundamental_model_slow_ratio_equity_cap_follow_up_batch_06/close, 120), industry)` | 0.252 | 0.333 | 0.371 |
| 8 | `gen001-5024e428367d` | `ts_rank(anl4_qfv4_median_eps/close, 60)` | 0.251 | 0.400 | 0.176 |
| 9 | `gen001-232ac5c76bd9` | `ts_mean(pv13_revere_index_value, 63)` | 0.218 | 0.333 | 0.050 |
| 10 | `gen001-9af80385b52d` | `ts_decay_linear(group_rank(ts_rank(anl4_qfv4_eps_mean/close, 60), subindustry), 20)` | 0.210 | 0.429 | 0.233 |

## Dry-run 计划

- Dry-run 仍然产生 10 个候选，且前排主要是单字段 / 单窗口的轻量模板。
- 我保留了解释性更强的 live-probe 候选，并主动排除了探索性更强的 `bucket(...)` / `ts_count_nans(...)` 变体。

### 推荐提交的 top 5

| order | candidate_id | expression | canonical score | novelty | avg similarity | reason |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | `gen001-18712db91872` | `ts_rank(sentiment_focus_rank, 60)` | 0.434 | 0.667 | 0.161 | Highest-confidence branch with balanced novelty and interpretability |
| 2 | `gen001-232ac5c76bd9` | `ts_mean(pv13_revere_index_value, 63)` | 0.218 | 0.333 | 0.050 | Simple, low-similarity branch with a distinct field family |
| 3 | `gen001-8c5bbca421a8` | `ts_rank(anl4_af_eps_value / close, 60)` | 0.263 | 0.400 | 0.184 | Direct fundamental ratio probe |
| 4 | `gen001-af24b0eee1d1` | `ts_rank(anl4_afv4_median_eps/close, 60)` | 0.263 | 0.400 | 0.176 | Alternate fundamental ratio branch |
| 5 | `gen001-5caf569d9422` | `group_rank(ts_rank(fundamental_model_slow_ratio_equity_cap_follow_up_batch_06/close, 120), industry)` | 0.252 | 0.333 | 0.371 | Industry-neutralized fundamental follow-up |

## 下一步建议

1. 如果你要做 live probe，请只手动提交上面这 5 个候选。
2. 提交前必须显式开启 `WQB_API_ENABLED=true` 并提供凭证。
3. 这批 batch 已经从 B 提升到 A，当前不建议继续无约束扩展搜索。

## 备注

- 旧的 bootstrap / 决策文件已保留在 baseline 路径；这次结果写入了新的优化输出目录。
- 如果你希望继续优化，下一轮最值得盯的是探索性运算符与更强的信号语义过滤，而不是再放大 novelty。

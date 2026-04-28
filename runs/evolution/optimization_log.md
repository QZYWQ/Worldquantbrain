# 优化闭环日志

- 启动时间：2026-04-28 07:49:29
- 运行模式：完全离线
- 输出批次：`runs/evolution/generations/opt-r1/gen_001.batch.json`
- 结果账本：`runs/evidence/result_ledger.db`

## Round 1 调整

- Adjusted `harness/lib/evolution/evolution_config.json` to push exploration without losing ranking discipline: mutation 0.18, crossover 0.8, elite fraction 0.05, tournament size 2, novelty floor 0.12, and explicit score/complexity weights.
- Made surrogate scoring config-driven in `harness/lib/evolution/engine.py`, switched complexity to a linear operator/field/parameter penalty, and added a trivial self-division/self-subtraction guard.
- Broadened the winner field pool in `harness/lib/evolution/population.py` by collecting historical `field_name` values before eligibility filtering.
- Reduced same-group operator replacement bias and added `ts_mean` / `ts_std` wrappers in `harness/lib/evolution/mutation.py` to widen operator shapes.

### 结果对比

| 指标 | Baseline | Optimized | 变化 |
| --- | ---: | ---: | ---: |
| 候选数 | 20 | 20 | 0 |
| 平均 surrogate_score | 0.088 | 0.241 | +0.153 |
| 最大 surrogate_score | 0.140 | 0.441 | +0.301 |
| 平均 novelty | 0.288 | 0.386 | +0.098 |
| 平均与 winners 结构相似度 | 0.315 | 0.231 | -0.084 |
| surrogate_score 标准差 | 0.027 | 0.090 | +0.063 |
| unique ops | 10 | 7 | -3 |
| unique fields | 17 | 16 | -1 |
| trivial identity count | 2 | 0 | -2 |

### 关键观察

- Canonical candidate 平均 novelty 从 0.288 提升到 0.386，结构相似度从 0.315 降到 0.231。
- Root operator 从 `group_rank` / `ts_rank` 单一主导，变成 `group_rank`、`ts_rank`、`ts_mean`、`ts_count_nans`、`bucket`、`ts_decay_linear` 的混合。
- `close/close` 和类似自除式退化表达式被过滤掉，trivial identity count 归零。
- Dry-run 计划仍然给出 10 个候选，但前排现在由更清晰的单字段 / 平滑 / 基础因子组合占据。

### 结论

- 这一轮把 batch 从 B 拉到了 **A**。
- 继续再调一轮的边际收益预计较小，因此暂停在当前 batch，进入最终推荐阶段。

## Artifact 路径

- bootstrap bundle: `runs/evolution/automation-runs/20260428-opt-r1`
- learning loop manifest: `runs/learning-loops/20260428-opt-r1.json`
- batch canonical: `runs/evolution/generations/opt-r1/gen_001.json`
- batch dry-run: `runs/evolution/generations/opt-r1/gen_001.batch.json`

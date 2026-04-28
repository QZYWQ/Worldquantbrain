# BRAIN_LAB 离线 alpha 生产审查报告

- 生成时间：2026-04-28 07:20 (Asia/Shanghai)
- 运行模式：完全离线
- 真实提交：未执行
- `agent-policies/`：未修改
- 主要输入：`runs/evolution/generations/gen_001.batch.json` / `runs/evolution/generations/gen_001.json`
- 结果账本：`runs/evidence/result_ledger.db`
- 载入 winner 数：160（按当前 loader 规则去重并按分数排序后，limit=1000）

## 步骤 1：候选概览

说明：`gen_001.batch.json` 本身不包含 `surrogate_score`；该值与完整 lineage 来自配套的 `gen_001.json`。

| 排名 | 候选ID | 表达式 | surrogate_score | operators | fields | novelty | 平均 winner 相似度 | lineage 摘要 |
| --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| 1 | `gen001-e618a26a23c2` | `group_rank(ts_delay(anl4_af_eps_value / close, 60), industry)` | 0.140 | `group_rank, ts_delay` (2) | `anl4_af_eps_value, close, industry` (3) | 0.333 | 0.232 | method=mutation_fallback; p1=gen000-3940ea21738c; p2=gen000-8f4229a745ab |
| 2 | `gen001-04156ff798ca` | `group_mean(ts_rank(anl4_af_eps_value / close, 60), industry)` | 0.126 | `group_mean, ts_rank` (2) | `anl4_af_eps_value, close, industry` (3) | 0.333 | 0.236 | method=mutation_fallback; p1=gen000-98703f9fc70d; p2=gen000-8f4229a745ab |
| 3 | `gen001-920c4e01b503` | `group_sum(ts_rank(industry/close, 60), industry)` | 0.119 | `group_sum, ts_rank` (2) | `industry, close` (2) | 0.500 | 0.263 | method=crossover+mutation; p1=gen000-7ab21f653c53; p2=gen000-2c01a5547503 |
| 4 | `gen001-acf220418a34` | `group_rank(ts_rank(earnings_per_share_median_value/close, 60), pcr_oi_30_b_stage_industry_mean5)` | 0.119 | `group_rank, ts_rank` (2) | `earnings_per_share_median_value, close, pcr_oi_30_b_stage_industry_mean5` (3) | 0.333 | 0.246 | method=mutation_fallback; p1=gen000-2c01a5547503; p2=gen000-d47401f8f5b1 |
| 5 | `gen001-0ad9a7e65dab` | `group_rank(ts_rank(anl4_qfv4_eps_mean/fundamental_model_slow_ratio_equity_cap_follow_up_batch_04, 60), industry)` | 0.119 | `group_rank, ts_rank` (2) | `anl4_qfv4_eps_mean, fundamental_model_slow_ratio_equity_cap_follow_up_batch_04, industry` (3) | 0.333 | 0.325 | method=mutation_fallback; p1=gen000-2c01a5547503; p2=gen000-8155b6b43ab1 |
| 6 | `gen001-29ca1b8675be` | `zscore(group_rank(ts_rank(earnings_per_share_average/close, 60), industry))` | 0.109 | `zscore, group_rank, ts_rank` (3) | `earnings_per_share_average, close, industry` (3) | 0.167 | 0.328 | method=mutation_fallback; p1=gen000-3940ea21738c; p2=gen000-7ab21f653c53 |
| 7 | `gen001-9143243dcfba` | `group_rank(ts_rank(news_attention_qcm_branch_batch_01/close, 60), industry)` | 0.108 | `group_rank, ts_rank` (2) | `news_attention_qcm_branch_batch_01, close, industry` (3) | 0.333 | 0.371 | method=mutation_fallback; p1=gen000-8155b6b43ab1; p2=gen000-c800174346e5 |
| 8 | `gen001-be491c77ebc3` | `group_rank(ts_rank(anl4_afv4_median_eps/anl4_afv4_median_eps, 60), industry)` | 0.099 | `group_rank, ts_rank` (2) | `anl4_afv4_median_eps, industry` (2) | 0.200 | 0.379 | method=mutation_fallback; p1=gen000-d47401f8f5b1; p2=gen000-3940ea21738c |
| 9 | `gen001-55fb89976528` | `log(group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry))` | 0.086 | `log, group_rank, ts_rank` (3) | `anl4_qfv4_median_eps, close, industry` (3) | 0.167 | 0.325 | method=mutation_fallback; p1=gen000-2c01a5547503; p2=gen000-41a0fae20372 |
| 10 | `gen001-a374a26a7e09` | `demean(group_rank(ts_rank(actual_eps_value_quarterly / close, 60), industry))` | 0.083 | `demean, group_rank, ts_rank` (3) | `actual_eps_value_quarterly, close, industry` (3) | 0.167 | 0.326 | method=mutation_fallback; p1=gen000-4c9baf3d0c39; p2=gen000-98703f9fc70d |

## 步骤 2：质量与多样性评估

- 结构集中度：`ts_rank` 出现 19/20 次，`group_rank` 出现 17/20 次；根操作以 `group_rank` 为主（10/20）。
- 字段集中度：`industry` 出现 17/20，`close` 出现 15/20。
- surrogate_score 分布：min=0.035，median=0.082，mean=0.088，max=0.140，stdev=0.027。顶部 5 个候选集中在 0.118-0.140 区间，随后明显回落。
- novelty 分布：mean=0.288，范围 0.167-0.500。
- 与 winners 的结构相似度（候选批次整体）：平均 0.315，中位数 0.326，范围 0.184-0.436。
- 语义结论：批次不是“重合到不可用”，但明显属于同一条局部家族；探索仍偏 exploitation，缺少第二条真正独立的结构轴。
- 干跑计划额外信号：20/20 原始候选在 DedupeGate 里触发结构相似度 warning，0 个被判 duplicate；`close/close` 这类近常量表达式说明当前 ranker 还需要语义过滤。
- 总体质量评分：**B**。理由：有可用的前排候选，但 batch 多样性偏弱、与既有 winner 结构仍然接近、并且 planner 会放进一个明显偏弱的 `close/close` 变体。

### 结构分布摘要

- 根操作 Top：group_rank=10, log=2, ts_rank=2, group_mean=1, group_sum=1
- 操作 Top：ts_rank=19, group_rank=17, log=2, ts_delay=1, group_mean=1
- 字段 Top：industry=17, close=15, anl4_af_eps_value=6, earnings_per_share_average=2, anl4_qfv4_median_eps=2, actual_eps_value_quarterly=2, cap=2, subindustry=2

## 步骤 2b：dry-run 计划摘要

- planned_candidates=10
- top_recommendations=10
- dry-run 计划前排几乎平坦：rank 1 为 0.750，rank 2-10 基本都在 0.650。
- 这说明 planner 的评分更像一个“可提交性过滤器”，不是信号质量评分器。

| 计划排名 | candidate_id | expression | score | 平均 winner 相似度 | 说明 |
| --- | --- | --- | ---: | ---: | --- |
| 1 | `batch:gen001-cdf044a1f8bc:1:None:None` | `ts_rank(anl4_af_eps_value / close, 120)` | 0.750 | 0.184 | 可作为 live probe |
| 2 | `batch:gen001-04156ff798ca:1:None:None` | `group_mean(ts_rank(anl4_af_eps_value / close, 60), industry)` | 0.650 | 0.236 | 可作为 live probe |
| 3 | `batch:gen001-0ad9a7e65dab:1:None:None` | `group_rank(ts_rank(anl4_qfv4_eps_mean/fundamental_model_slow_ratio_equity_cap_follow_up_batch_04, 60), industry)` | 0.650 | 0.325 | 可作为 live probe |
| 4 | `batch:gen001-0c5e8247b0bd:1:None:None` | `ts_decay_linear(group_rank(ts_rank(actual_eps_value_quarterly / close, 60), industry), 120)` | 0.650 | 0.331 | 可作为 live probe |
| 5 | `batch:gen001-0d82b922e039:1:None:None` | `group_rank(ts_rank(earnings_per_share_average/pv13_revere_index_value, 60), industry)` | 0.650 | 0.333 | 可作为 live probe |
| 6 | `batch:gen001-29ca1b8675be:1:None:None` | `zscore(group_rank(ts_rank(earnings_per_share_average/close, 60), industry))` | 0.650 | 0.328 | 备选 |
| 7 | `batch:gen001-325aa8aef84c:1:None:None` | `group_rank(ts_rank(close/close, 60), industry)` | 0.650 | 0.436 | 应降权/复核 |
| 8 | `batch:gen001-4547bc943d0a:1:None:None` | `log(group_rank(group_rank(ts_rank(anl4_af_eps_value / close, 60), subindustry), industry))` | 0.650 | 0.306 | 备选 |
| 9 | `batch:gen001-55fb89976528:1:None:None` | `log(group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry))` | 0.650 | 0.325 | 备选 |
| 10 | `batch:gen001-7e85e64de995:1:None:None` | `rank(ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 84))` | 0.650 | 0.315 | 备选 |

## 步骤 3：决策建议

b) **调整演化参数后重新运行演化** — Current candidates cluster around a single industry-neutralized EPS/price family; a little more exploration pressure should improve novelty.
c) **将本次候选作为下一 cycle 种子并归档** — The batch is usable as seed material, but it is not diverse enough to justify treating it as a finished submit set.
a) **立即手动提交一部分候选** — Only worth doing for a small manual live probe; do not submit the full set because the ranker still admits at least one weak/degenerate expression.

### 若用户坚持走 a：建议提交的 top 5

1. `ts_rank(anl4_af_eps_value / close, 120)` — planner score 0.750，平均 winner 相似度 0.184；`gen001-cdf044a1f8bc` 提供了当前 batch 里较好的多样性点。
2. `group_mean(ts_rank(anl4_af_eps_value / close, 60), industry)` — planner score 0.650，平均 winner 相似度 0.236；`gen001-04156ff798ca` 提供了当前 batch 里较好的多样性点。
3. `group_rank(ts_rank(anl4_qfv4_eps_mean/fundamental_model_slow_ratio_equity_cap_follow_up_batch_04, 60), industry)` — planner score 0.650，平均 winner 相似度 0.325；`gen001-0ad9a7e65dab` 提供了当前 batch 里较好的多样性点。
4. `ts_decay_linear(group_rank(ts_rank(actual_eps_value_quarterly / close, 60), industry), 120)` — planner score 0.650，平均 winner 相似度 0.331；`gen001-0c5e8247b0bd` 提供了当前 batch 里较好的多样性点。
5. `group_rank(ts_rank(earnings_per_share_average/pv13_revere_index_value, 60), industry)` — planner score 0.650，平均 winner 相似度 0.333；`gen001-0d82b922e039` 提供了当前 batch 里较好的多样性点。

补充：我没有把 `group_rank(ts_rank(close/close, 60), industry)` 放进 top 5，尽管 planner 排到第 7；它过于接近常量，语义质量明显不如前 5。

### 手动提交提醒

- 所有提交必须由用户手动执行。
- 真实 live 提交前，必须显式开启 `WQB_API_ENABLED=true` 并提供凭证。
- 当前文件只是推荐计划，不包含任何自动提交动作。

### 建议的下一轮演化参数

- `mutation_rate`: 0.10 -> 0.15~0.20，增加探索幅度。
- `tournament_size`: 3 -> 2，降低局部收敛。
- `archive_novelty_min`: 0.08 -> 0.12~0.15，提高与旧 winner 的结构距离门槛。
- 增加语义过滤：排除近常量或自除式表达式（如 `close/close`）。

---
生成产物：
- 决策报告：`runs/decision_report_20260428_0720.md`
- 推荐列表：`runs/recommended_submission.json`

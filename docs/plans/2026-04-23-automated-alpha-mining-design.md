# 自动化 Alpha 因子挖掘设计

- Date: `2026-04-23`
- Status: `design draft`
- Goal: 把“本地 Python 先生成上千个候选、规则/scorecard 过滤、只把 top-k 丢去官方 simulate”的模糊想法，收敛成一套可执行的受约束搜索方案。

## 结论先行

最佳方案不是盲扫，也不是继续手工改单个表达式，而是：

1. 先选少量高置信 `seed family`
2. 用类型安全的模板/语法生成大量变体
3. 用本地 scorecard 过滤掉大部分
4. 只把少量高分且互补的候选送官方 simulate
5. 把失败结果回灌到下一轮搜索空间

这更接近“受约束搜索 + 反馈驱动进化”，而不是“随便拼 operator”。

## 研究依据

### 官方 WorldQuant BRAIN 资料

- News / social media 官方提示明确把 RavenPack news 族拆成几个可复用方向：`nws18_bee`（sentiment）、`rp_nip_assets`（novelty）、`nws18_relevance` / `nws18_qcm`（relevance）。
- 官方社区关于 Test Period 的说明强调：IS 好不代表 OS 好，应使用 train/test 切分、比较稳定性，并警惕 overfitting。
- 官方社区关于 self correlation / production correlation 的讨论反复强调：要尽量多样化、避免重复信号、避免过拟合。
- 官方社区关于 operator sequencing 的讨论强调：尽量保持表达式简单，避免为了刷指标堆太多 operator。
- 官方社区关于 sub-universe 报错的说明表明：提交前必须过 robustness check，不能只看整体 IS。

### 方法论文 / 自动化 factor mining 研究

- `AutoAlpha`：强调分层结构、质量多样性搜索、warm start、替换机制，核心是“先快速定位空间，再防止早熟收敛”。
- `AlphaForge`：强调两阶段框架，先生成因子，再动态组合；同时强调固定权重不够灵活。
- `EFS`：强调用 LLM 生成和演化因子，并通过演化反馈循环逐步改进 factor pool。
- `FactorEngine`：强调把因子表示成可执行程序，并把“逻辑修正 vs 参数优化”“LLM 指导搜索 vs Bayesian hyperparameter search”“LLM 使用 vs 本地计算”拆开。
- 这些工作共同指向一个结论：高效自动化挖掘一定要有 grammar / template 约束、分层搜索和反馈回灌。

## 推荐架构

### 1) Seed family 层

先把搜索空间限制在少数“高价值且可解释”的 family：

- `sentiment`: `nws18_bee`
- `relevance`: `nws18_qcm`, `nws18_relevance`
- `novelty`: `rp_nip_assets`

不要先扩到太多家族，也不要回到已死的老线。

### 2) 结构模板层

每个 family 只保留少数结构模板：

- 平滑型：`ts_mean(...)`
- 标准化型：`ts_zscore(...)`
- 分组中性化：`group_neutralize(..., industry)` / `subindustry`
- 事件门控：`trade_when(gate, signal, -1)`
- 组合/差分型：两个窗口的差值、比值、或门控后再平滑

这层负责“合法表达式生成”，不是负责打分。

### 3) 参数网格层

先只跑小网格：

- 窗口：`5 / 10 / 20 / 63 / 126`
- 门控窗：`10 / 20 / 30`
- 中性化：`industry / subindustry`
- 轻量组合：单信号、双信号、门控 + 平滑

先让搜索空间足够大，但不要无限膨胀。

### 4) 本地 scorecard 层

本地先筛掉大部分候选，建议至少包括：

- 语法合法性
- 类型合法性
- family 多样性
- operator 数量惩罚
- 参数重复惩罚
- 与已失败表达式的相似度惩罚
- 与当前已知好线的相关性惩罚
- 复杂度 / 可解释性惩罚

如果有历史模拟结果，再加：

- proxy Sharpe / Fitness
- 训练-测试稳定性 proxy
- turnover proxy
- 结果分散度 / coverage proxy

### 5) 官方 simulate 层

只把 top-k 丢去官方 simulate，建议优先：

- 每个 family 先 1 个 baseline
- 再 2~3 个最有解释力的变体
- 再 1 个结构轴变体

这样比“同一 family 一次丢几十个近似表达式”更有效。

## 推荐搜索轴

优先级建议如下：

1. `field replacement`
   - `nws18_bee`
   - `nws18_qcm`
   - `nws18_relevance`
   - `rp_nip_assets`
2. `window grid`
   - `5 / 10 / 20 / 63 / 126`
3. `structure transform`
   - `vec_avg`
   - `ts_mean`
   - `ts_zscore`
   - `group_neutralize`
   - `trade_when`
4. `gate`
   - `returns` 波动门
   - `relevance` 门
   - `novelty` 门
5. `neutralization`
   - `industry`
   - `subindustry`

## 评分逻辑建议

可以把 scorecard 做成多目标排序，而不是单指标打分：

- `validity`
- `simplicity`
- `family novelty`
- `correlation penalty`
- `proxy stability`
- `expected turnover control`
- `expected submission readiness`

简单说就是：

`score = good_signal - complexity_penalty - correlation_penalty - overfit_penalty + stability_bonus`

## 何时 branch / kill

### kill 条件

- 经过一轮小网格后，IS / TEST 都弱
- 没有真实 `Check Submission` evidence
- 没有非空 `subuniverse_pass`
- 表达式只是在同一 family 内做微调，且没有改进

### branch 条件

- 某个 family 出现明显优于其他候选的 baseline
- 结构变化带来可重复的稳定性提升
- 提交前检查开始出现真实 evidence

## 实施节奏建议

### 每日流水线

1. `seed` 采集
2. 本地生成 1000+ 候选
3. 本地 scorecard 过滤到 50~100
4. 再按 family / diversity 选 top-k 进入 simulate
5. 记录真实 metrics
6. 对失败 family 做 kill 或降权

### 关键原则

- 先广后窄，不是先深后乱
- 先 template，再参数
- 先单 family，再跨 family
- 先本地，后官方
- 先稳定，后复杂

## 这套方案最适合当前项目的原因

- 它和 WorldQuant BRAIN 官方社区的建议一致：少 operator、重稳定、重 test period、重 sub-universe。
- 它和自动化 factor mining 论文趋势一致：分层搜索、质量多样性、反馈回灌、程序化表达。
- 它能兼容你现在的研究节奏：本地可以一天生成上千个候选，但官方 simulate 只看少量高质量项。
- 它能把“经验技巧”和“算法搜索”接起来，而不是让两者互相打架。

## 下一步建议

- 先把 `nws18_bee` 和 `rp_nip_assets` 作为主 seed family，`nws18_qcm` / `nws18_relevance` 只做 secondary control。
- 每支 family 先只开 1 个 baseline + 3 个变体，确认 scorecard 能否区分“像样候选”和“噪声”。
- 等本地筛选器稳定后，再扩大到更高维搜索，而不是一开始就把 family 数量铺太宽。

## 可执行流水线 v0.1

这部分把上面的设计落成可直接写脚本的流水线。目标不是“自动提交”，而是先把本地候选挖掘效率提到专业可用水平：每天生成 1000+ 候选，本地筛到 50~100 个，再把少量 top-k 送官方 simulate。

### 1) 目录和状态分层

- `runs/expression-families/`：人工维护的 family 说明，作为搜索空间的真相源之一。
- `runs/research-queues/`：本地打分后的优先队列，给 simulate 前的人工/自动选择用。
- `runs/simulation-captures/`：只写真实平台结果，不写猜测值。
- `runs/candidate-batches/`：只有出现真实 `Check Submission` evidence 且 `subuniverse_pass` 非空时才允许生成。
- `harness/artifacts/alpha-mining/`：本地缓存，放候选指纹、历史相似度、scorecard 中间结果、黑名单 family。

### 2) 生成器：`scripts/alpha_batch_miner.py`

这个脚本只做“受约束生成”，不做最终推荐。

- 输入：family registry、seed expressions、黑名单 family、窗口网格、允许算子集。
- 输出：JSONL 候选池，每条包含 `expression`、`family`、`template_id`、`windows`、`gate`、`neutralization`、`canonical_signature`、`complexity`。
- 生成轴固定为 5 类：
  - 字段替换：只在当前 family 允许字段内替换。
  - 窗口网格：`5 / 10 / 20 / 63 / 126`。
  - 结构变换：`ts_mean`、`ts_zscore`、`group_neutralize`、`trade_when`。
  - 门控变换：`relevance` 门、`novelty` 门、`returns` 波动门。
  - 归一化变换：`industry` / `subindustry`。
- 生成策略：
  - baseline 先保留 1 个；
  - 每个 baseline 派生 3~8 个轻变体；
  - 再生成少量结构变体，避免全是同构表达式。

### 3) 评分器：`scripts/candidate_scorecard.py`

这个脚本只打“本地启发式分数”，不伪装成真实 Sharpe/Fitness。

- 基础硬过滤：
  - 语法合法
  - 类型合法
  - field 已确认
  - operator 深度不过载
  - 不命中 dead-line blacklist
- 启发式打分项：
  - `novelty`：和历史失败表达式越不同越高
  - `simplicity`：operator 越少、路径越短越高
  - `stability_proxy`：窗口与 gate 更平滑的略加分
  - `family_fit`：和当前 seed family 的语义一致性
  - `diversity_bonus`：来自不同 template / gate / neutralization 的加分
  - `evidence_bonus`：历史 capture 里接近成功边界的家族可加分
- 建议输出：
  - `scored.jsonl`
  - `scorecard.csv`
  - `topk_summary.md`

一个实用原则是：宁可把“看起来像噪声”的表达式砍掉，也不要把大量同构变体都送去 simulate。

### 4) 队列构建：`scripts/research_queue_builder.py`

这个脚本把评分后的候选变成可执行研究队列。

- 按 family、template、field、window 做分组。
- 每个队列只保留少量代表项：
  - 1 个 baseline
  - 2~3 个最稳的窗口变体
  - 1 个结构变体
  - 1 个门控变体
- 队列输出到 `runs/research-queues/YYYY-MM-DD-topic.json`。
- 同时输出一个短 markdown 摘要，方便人工确认下一批 simulate 的 top-k。

### 5) 回灌闭环

真实 simulate 结果只写进 `runs/simulation-captures/`，然后回灌到下一轮搜索。

- 解析 capture 中的：
  - `metrics`
  - `tests.subuniverse_pass`
  - `tests.check_submission_pass`
  - `batch_observation`
- 更新本地历史库：
  - 成功/失败 family
  - 常见失败结构
  - 近似重复表达式
  - 已验证过的 gate / window 组合
- kill / branch 规则：
  - 两个 batch 仍然弱、又没有真实 evidence => kill
  - 出现真实 `Check Submission` evidence 且 `subuniverse_pass` 非空 => 允许进入 candidate-batch
  - 某 family 出现稳定改善 => 只在该 family 内继续 polish

### 6) 与现有脚本的关系

- `scripts/worldquant_alpha_report.py` 继续负责“把少量表达式送官方 simulate 并格式化报告”。
- 新增的三个脚本负责“生成 -> 评分 -> 排队”。
- 这样可以把高吞吐搜索和真实平台执行解耦，避免把 simulate 当成搜索引擎。

### 7) 每日运行节奏

1. 从当前 family registry 生成 1000+ 原始候选。
2. scorecard 过滤到 100~200。
3. research queue 选出每个 family 的 top-k。
4. 只把少量 top-k 送 simulate。
5. 记录真实 capture。
6. 用 capture 回灌下一轮 family registry 和 blacklist。

如果这套节奏跑通，专业人士那种“每天脚本跑几千次、筛出几百个可用因子”的模式就成立了；但这里的“可用”首先指本地可保留、可继续演化，不等于都能直接提交。

## 参考链接

- `https://support.worldquantbrain.com/hc/en-us/community/posts/20051406364695--BRAIN-TIPS-Finding-Alphas-News-and-Social-Media`
- `https://support.worldquantbrain.com/hc/en-us/community/posts/22205077935895--BRAIN-TIPS-How-can-I-use-the-test-period-to-improve-the-OS-performance-of-my-Alpha`
- `https://support.worldquantbrain.com/hc/en-us/community/posts/26750743873943-How-to-reduce-self-correlation-and-production-correlation`
- `https://support.worldquantbrain.com/hc/en-us/community/posts/19344464221335--BRAIN-TIPS-Sequencing-Multiple-Operators-in-an-Expression`
- `https://support.worldquantbrain.com/hc/en-us/community/posts/27479493466647-Sub-universe-Sharpe-of-0-32-is-below-cutoff-of-0-82`
- `https://arxiv.org/abs/2002.08245`
- `https://arxiv.org/abs/2406.18394`
- `https://arxiv.org/abs/2507.17211`
- `https://arxiv.org/abs/2603.16365`

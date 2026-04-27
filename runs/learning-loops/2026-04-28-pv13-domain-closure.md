# 学习循环：pv13 数据域收口

## 背景
pv13（Relationship Data for Equity）是我们通过 LENS 引擎识别出的第一个正交数据域。该域已经经历了完整的推进链路：
- S-1 → S0 → A → B → C → D → E（3 个深度孵化候选）
- 批量 S0 扫描（10 个剩余高优先级字段）
- 最终 live 批量回收 24 条结果，run log summary 为 `completed=24, submitted=48, failed=0, resumed=2, skipped_completed=2`

## 核心经验
1. **LENS 引擎有效**：pv13 确实是与此前失败域不同的正交数据域，域地图方向正确。
2. **信号天花板是真实存在的**：在当前表达式结构下，pv13 的 live ceiling 明确停在 `IS <= 0.91`，没有继续向上穿透。
3. **批量流水线降低了探索成本**：从手工推进到批量扫描，10 个候选字段的探索被压缩到一个受控的 live 批次里完成。
4. **网络容错是批量 live 的关键瓶颈**：远端断连 / 超时会拖慢回收，但 resume + progress 追踪已经能把结果收回来。

## 保留价值
- `pv13_ustomergraphrank_page_rank` 仍然是 pv13 的历史最佳 TEST 候选，适合保留证据链。
- pv13 字段本身可以作为以后杂交实验的父代素材，但不再建议继续做同类批量扫射。
- `batch_s0_scan.py`、`dedupe_gate.py`、`result_ledger.db`、`batch_progress.json` 的链路已经被验证可复用。

## 对下一步的影响
- 不再对 pv13 剩余字段进行批量扫描。
- 下一轮优先做骨架优化：表达式编译器、参数扫描器、SelfOptimizer。
- 新域 LENS 勘探可以在骨架优化完成前后接续展开；若资源允许，可并行推进。

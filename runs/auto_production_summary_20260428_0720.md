# 自动生产摘要

- 运行时间：2026-04-28 07:20（Asia/Shanghai）
- 模式：完全离线
- WQB API：未调用
- 真实提交：未执行
- `agent-policies/`：未修改

## 步骤 1：离线演化

- 演化代数：3 代
- 每代有效候选数：`gen_001=20`，`gen_002=20`，`gen_003=20`
- `gen_001.batch.json`：生成成功，候选列表非空，共 20 项
- 关键产物：
  - `runs/evolution/generations/gen_001.batch.json`
  - `runs/evolution/evolution_log.jsonl`
  - `runs/learning-loops/2026-04-28-072022-evolution-bootstrap.json`
  - `runs/learning-loops/2026-04-28-072022-evolution-bootstrap.md`
  - `runs/research-contracts/2026-04-28-official-alpha-cycle-04-evolution-bootstrap.md`

## 步骤 2：dry-run 批量计划

- dry-run 计划提交的 alpha 数量：10
- `planned_candidates`：10
- `top_recommendations`：10
- `top_field_cap`：2
- 结果：无严重错误，仅出现结构相似性警告；计划正常生成

## 结论

- 本次流水线全程离线完成，未真实提交任何 alpha
- `agent-policies/` 保持干净
- 建议后续先复核 `runs/evolution/generations/gen_001.batch.json` 中的候选质量，再决定是否进入 live 模式

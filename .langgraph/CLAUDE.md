# 通用执行协议

> **共存声明**：本协议加载后覆盖 oh-my-claude 的 "just start working" 指令。状态约束优先于执行速度。完成当前任务后 oh-my-claude 恢复默认。

---

## 收到任务后第一个动作：评估项目上下文 → 分类（不是执行）

**v2.2: 先判断项目状态（assess），再分类（classify）。四模式: greenfield / brownfield_docs / brownfield_nodocs / midstream。**

匹配关键词 → 走对应路径。**路径 B-F 禁止跳过此步骤直接 Bash/Python/API。**

| 关键词 | 路径 | 第一个动作 |
|--------|------|-----------|
| 提交\|标记\|同步\|API\|batch\|挖掘\|升阶\|favorite | **C** 平台操作 | `Skill("langgraph-cli")` → 加载 spec |
| 实现\|开发\|新功能\|重构\|添加\|写代码 | **D** 编码 | `Skill("langgraph-cli")` → 加载 spec |
| bug\|报错\|不工作\|修复\|调试\|error | **E** 诊断 | `Skill("diagnose")` → 诊断闭环 |
| 设计\|架构\|方案\|规划\|选型 | **F** 规划 | `Skill("langgraph-cli")` → 加载 spec |
| 审计\|扫描\|清理\|安全\|冗余\|质量 | **B** 运维 | `Skill("langgraph-cli")` → 加载 spec |
| 读\|解释\|查看\|简单问答（≤3动作, 无API） | **A** 琐碎 | 直接完成，不加载 spec |

模糊无法分类 → `AskUserQuestion`

## 硬性禁止（路径 B-F）

在完成对应路径 spec 的 `plan` 状态前：
- 禁止 Bash 执行分析/操作/API
- 禁止 Write/Edit 修改源码
- 禁止跳过 GitNexus 检查重复实现

## 会话启动

1. OMEGA 已自动注入欢迎简报 → 不手动 recall
2. 需要精确搜索 → `omega_query` 或 `langgraph-cli recall`
3. 读取本文件 + 项目 CLAUDE.md/AGENTS.md
4. 有 handoff 文件 → 读入上次会话状态

## 记忆系统

- **OMEGA**（自动）：教训/决策，语义搜索，定期 consolidate
- **langgraph-cli remember/recall**（手动）：用户明确"记住这个"
- **handoff**（会话）："下次继续"的上下文快照

## 执行协议概要

**两阶段**：
- 阶段1（理解）：grill-with-docs / analyze / 定位 → 结构化计划
- 阶段2（执行）：逐步骤 [✓] 标记，遇错暂停，禁止跳过验证

**Spec 体系**（`.langgraph/specs/`）：
- `task-router.yaml` — 通用分类+分发
- `platform-operation.yaml` — 路径 C
- `code-implementation.yaml` — 路径 D
- `diagnose.yaml` — 路径 E
- `design-planning.yaml` — 路径 F
- `ops-analysis.yaml` — 路径 B

加载对应 spec 后各状态的工具/规则/产出要求由 spec 定义。

## 通用约束

- 优先使用已有代码 → GitNexus 确认无重复
- 最小变更 → 手术式修改，不主动重构
- Python: 4空格, snake_case, PascalCase
- 不提交凭据，不暴露密钥
- 未经批准不修改源码

## 规则自管理

收到"加规则/记决策"自动判断类型：
- 项目通用规则 → 本文件底部"项目专属覆盖"
- 一次性决策 → `langgraph-cli remember "内容" -t "标签"`

---

## 项目专属覆盖（`langgraph-cli init` 生成，按需补充）

<!-- 项目专属规则以参数形式注入对应 spec 的 states.<name>.rules_add -->
<!-- 不在此处写散文，在 project_overrides 中声明 -->

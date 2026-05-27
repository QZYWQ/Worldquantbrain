# AI Workflow Kit

面向 Claude Code 的通用 AI 辅助开发工作流套件。安装一次，所有项目按需引入。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

## 解决的问题

Claude Code + oh-my-claude 让 AI 可以"快速执行"，但面对复杂任务时缺乏**结构化的执行协议**——AI 倾向于跳过分析直接编码，跳过 plan 直接跑 API。纯文档规则（"你必须先分类"）在上下文衰减后约束力接近零。

v2 方案：**spec 状态机 + Skill 运行时**。详见下文。

## What's New in v2

### v2.4 新特性

基于 WorldQuant BRAIN 5 小时实操诊断的优化——从 **v2.2 的一次性状态机** 升级到 **支持探索+迭代的错误感知协议**。

| 问题 | v2.2 | v2.4 |
|------|------|------|
| plan 前不能调用 API | plan 前 Bash/API 硬禁止 → 数据探查死锁 | **preflight 状态**: 只读 API 允许，收集事实后进入 plan |
| 线性状态机不支持迭代 | execute → verify → done，优化需要全链路重跑 | **analyze 状态**: execute 后内循环（≤3 轮），定向修复而非盲扫 |
| 任何错误都暂停 | 所有 ERROR → 暂停+汇报 | **三级错误**: expected（跳过）/ rate-limit（重试）/ system（暂停） |
| 多技能无叠加协议 | 路径 spec 独占执行 | **技能叠加**: 路径 spec（流程）+ 领域 skill（约束）并行 |
| 多阶段任务重跑 assess | 每步 back to assess | **子任务流**: 声明路径切换，不重跑 assess |
| 单项目过拟合 | — | 所有机制通用化：无领域特定字段、无项目特定名称 |

### v1 的三个致命问题

| 问题 | v1 表现 | 实际后果 |
|------|--------|---------|
| **规则是散文，不是 gate** | 154 行 CLAUDE.md 描述 6 条路径 | 上下文衰减后 AI 当普通文本忽略 |
| **Skill 是许可，不是约束** | `allowed-tools: Bash(langgraph-cli *)` — "你可以用 CLI 了" | 零行为改变 |
| **与 oh-my-claude 无声冲突** | "先分类" vs "Just start working" 同时注入 | AI 遵守后者 |

实测 WorldQuant BRAIN 项目工作流遵循率 **30%**（194 行规则的 500+ 行上下文中，"MUST" 标注 5 小时后权重归零）。

### v2 三层架构优化

**Layer 1 — Spec 规范层**（可复用状态机）

6 个 YAML spec（`.langgraph/specs/`）定义每条路径的执行协议。每个状态编码 5 个维度：

```yaml
states:
  classify:
    allow: [分析, 读文件, 搜索]     # 允许的动作
    forbid: [Bash, Write, Edit, API] # 禁止的动作（优先级 > 用户请求）
    tools: {skill, CLI, agent}        # 工具分配（按状态绑定，不是一次性全给）
    output: "路径 X | 关键词 | 理由"  # 必须产出（不是可选）
    self_check: "我是否先分类了？"    # 自检（注入每次回复末尾）
```

| 优化点 | 效果 |
|--------|------|
| 散文 → 结构化状态机 | survive context compression |
| forbid 清单 | 硬约束：AI 违反时自报"当前状态禁止此操作" |
| 工具按状态分配 | grill 只在 plan 加载，tdd 只在 execute 加载——渐进式披露 |
| output + self_check | 注入回复末尾，AI 无法跳过自检 |

**Layer 2 — Skill 运行时**（约束注入器）

`Skill("langgraph-cli")` 从许可声明重构为**执行协议运行时**：

| v1 | v2 |
|----|----|
| "你现在可以调用 langgraph-cli 命令了" | "你被锁定在 classify 状态。只能分析+输出分类。Bash/API 禁止。" |
| 一次性加载 | 每个状态注入当前 {allow, forbid, tools, output} |
| 无状态跟踪 | `[路径 X | 状态 Y | → Z]` 标记每次回复 |

**Layer 3 — 共存层**（多系统优先级）

新增 `docs/COEXISTENCE.md`：4 系统职责矩阵（kit / oh-my-claude / Matt Pocock / OMEGA），声明优先级：

> 协议激活时覆盖 oh-my-claude "just start working"。任务完成后恢复。

| 冲突 | oh-my-claude | v2 kit | 解决 |
|------|-------------|--------|------|
| 执行速度 | "No preamble" | "先 classify" | kit 覆盖 |
| 提问 | "No questions" | "grill 追问" | grill 阶段覆盖 |
| 状态汇报 | "No summaries" | `[路径 X | 状态 Y]` | kit 覆盖 |

#### 配套改进

- **install.sh**：新增 5 项安装后验证（langgraph-cli / skill / OMEGA / GitNexus / oh-my-claude）
- **TOOL-LAYERING.md**：工具按状态分配表 + 重叠工具去重（grill vs critic vs code-reviewer）
- **.langgraph/CLAUDE.md**：154 行 → 50 行决策表，指向 specs 目录

## 快速开始

```bash
# 1. 克隆到任意位置（不是你的项目目录）
git clone https://github.com/QZYWQ/ai-workflow-kit.git
cd ai-workflow-kit

# 2. 在 Claude Code 中打开本目录，AI 自动执行安装
#    或手动：
bash install.sh
```

安装完成后本目录可以删除——工具已全局部署。

> **更新**: `git pull` 新版本后，重新运行 `bash install.sh` 即可同步所有变更到全局。

## 在项目中使用

```bash
cd /你的项目
langgraph-cli init --deep     # 生成 .langgraph/ 工作流体系，自动检测项目特征
```

然后用 Claude Code 打开项目。AI 会读取路由规则，自动匹配任务类型到对应执行路径。

### 初始化后检查

`init --deep` 会自动检测项目特征，但**自动检测有边界**——它只能识别文件模式（API 客户端、脚本语言、凭据文件），不会理解你的领域规则。init 完成后建议做一次对齐检查：

```bash
# 1. 检查项目专属覆盖区域
cat .langgraph/CLAUDE.md | grep -A30 "项目专属覆盖"

# 2. 用 Claude Code 跑一次模拟测试
#    对新项目说："帮我分析项目结构，看看工作流引入是否有遗漏"
```

**常见需要手动补的**：

| 检测项 | 自动检测能做到 | 需要手动补 |
|--------|-------------|----------|
| API 客户端路径 | ✅ 检测到文件存在 | ⚠️ 调用方式、限流规则、关键字段格式 |
| 凭据文件 | ✅ 检测到文件名 | ⚠️ 认证方式、环境变量名 |
| 脚本数量 | ✅ 统计数量 | ⚠️ 核心脚本 vs 辅助脚本的分类 |
| 领域规则 | ❌ 检测不到 | ⚠️ 平台特定限制、业务约束、经验教训 |
| 项目专属 workflow | ❌ 检测不到 | ⚠️ 通用 api-batch.yaml 之外需要定制化 YAML |
| 已有项目现有规则冲突 | ❌ 检测不到 | ⚠️ 路由门规则 vs 已有 CLAUDE.md/AGENTS.md 规则去重 |

> 示例：一个 SaaS 后端项目 init 后自动检测到了 Stripe API 客户端和 `.env` 凭证，但 Stripe 的幂等键格式、webhook 签名验证规则、费率限制策略——这些都是手动补进项目专属覆盖区域的。

然后用 Claude Code 打开项目。AI 会读取路由规则，自动匹配任务类型到对应执行路径：

| 你说 | AI 走 | 执行链 |
|------|------|--------|
| "解释这段代码" | 路径 A | 直接执行 |
| "调用 API 批量操作" | 路径 C | Skill 加载 spec → classify → plan → execute |
| "实现新功能" | 路径 D | Skill 加载 spec → classify → GitNexus → grill → plan → TDD → review |
| "修这个 bug" | 路径 E | Skill(diagnose) 加载 spec → classify → 重现 → 修复 → 验证 |
| "设计架构方案" | 路径 F | Skill 加载 spec → classify → analyze → 方案对比 |

## 不引入的项目

没有 `.langgraph/` 目录的项目完全不受影响——Claude Code 保持原生行为。

## 命令参考

```bash
langgraph-cli init [--deep]           # 项目初始化
langgraph-cli analyze .               # 项目结构分析
langgraph-cli review <文件>           # 并行安全+质量审查
langgraph-cli run workflow.yaml       # 执行 YAML 工作流
langgraph-cli remember "决策" -t "标签" # 长期记忆
langgraph-cli recall "关键词"         # 记忆搜索
langgraph-cli health                  # 全组件健康检查
```

## 架构

```
收到任务
  → Skill("langgraph-cli") 激活执行协议
    → 读取 .langgraph/specs/task-router.yaml
    → 锁定 classify → plan → execute → verify → done
    → 每个状态有 {允许, 禁止, 工具分配, 产出要求}
    → 自检清单注入每次回复末尾

spec 目录（可复用规范）
  ├── task-router.yaml      # 通用分类+分发
  ├── platform-operation.yaml  # 路径 C
  ├── code-implementation.yaml # 路径 D
  ├── diagnose.yaml            # 路径 E
  ├── design-planning.yaml     # 路径 F
  └── ops-analysis.yaml        # 路径 B

工具栈
  ├── langgraph-cli（CLI + 运行时）
  ├── OMEGA（自动长期记忆）
  ├── GitNexus（代码知识图谱）
  ├── oh-my-claude（编排纪律、agents、hooks）
  └── Matt Pocock skills（13 个方法论）

项目级 opt-in
  └── 有 .langgraph/ → 路由门激活
      └── 无 .langgraph/ → 原生 Claude Code
```

## 文档

| 文档 | 内容 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | AI 入口协议 |
| [docs/TOOL-LAYERING.md](docs/TOOL-LAYERING.md) | 工具分层 + 去重 |
| [docs/COEXISTENCE.md](docs/COEXISTENCE.md) | 多系统共存 + 冲突解决 |

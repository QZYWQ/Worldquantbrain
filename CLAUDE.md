# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **工作流规则** 见 `.langgraph/CLAUDE.md` — 包含两阶段执行协议、方法论选择、skill 分层、会话启动协议。
> **长期记忆** 由 OMEGA 自动管理（SessionStart 注入），辅以 `langgraph-cli remember/recall`。
> 读取本文件后，AI **必须** 同时读取 `.langgraph/CLAUDE.md` 来获取完整的工作流规则。

## Project Overview

WorldQuant BRAIN alpha research execution workspace. Stores real research queues, expression families, simulation captures, candidate batches, and research artifacts under `./runs/`.

## Common Commands

### Harness (long-running tracked work)
```bash
./harness/init.sh                              # Initialize session
./harness/coding-session.sh status              # Check current state
./harness/coding-session.sh doctor              # Verify state consistency
./harness/coding-session.sh start [FEATURE_ID] # Start a feature
./harness/coding-session.sh finish FEATURE_ID --summary "..."  # Finish feature
./harness/coding-session.sh cycle-current       # Show active cycle
./harness/coding-session.sh cycle-list          # List available cycles
./harness/coding-session.sh cycle-summary       # Quick terminal check
./harness/coding-session.sh cycle-report [PATH] # Durable report artifact
./harness/coding-session.sh cycle-learning-loop [PATH]  # Post-cycle lessons
./harness/coding-session.sh resume-brief [PATH] # Next-session handoff
./harness/coding-session.sh session-open [PATH] # Execution starter
./harness/coding-session.sh cycle-close [PATH]  # Close cycle
```

### Testing
```bash
./harness/tests/all.sh                         # Full test suite
./harness/tests/smoke.sh                        # Fast smoke check
```

### Local Alpha Loop
```bash
./harness/run-local-alpha-loop.sh              # Run alpha loop
```

## Architecture

### Output Model
- **Durable artifacts** → `./runs/` (research-queues, field-search-packs, expression-families, simulation-captures, candidate-batches, learning-loops, notes, submission-memos)
- **Harness state** → `./harness/` (state, progress.md, active-cycle.txt, reports, artifacts)

### Truth Sources
- **Cycle definition**: `./harness/active-cycle.txt` pointing to a static cycle file
- **Runtime state**: `./harness/state/` (synced mutable copies)
- **Session truth**: `./harness/progress.md`
- **Decision truth**: `./harness/decision-log.md`
- **Verification evidence**: `./harness/artifacts/`

## Detailed Rules

All project rules are defined in `./AGENTS.md`. Key sections:

- **Hard Rules**: `./AGENTS.md` - no fabricating results, sign-flip on negative Sharpe, verification boundaries
- **Execution Discipline**: `./AGENTS.md` - resolve ambiguity, minimum change, surgical edits, verifiable goals
- **Progressive Loading**: `./AGENTS.md` - load docs in order: AGENTS.md → 00-项目总索引.md → specific routing doc
- **Skill Gate**: Load `/Users/zpdedn/.codex/skills/worldquant-brain-alpha-engineering/SKILL.md` for alpha research
- **Harness Entry**: `./harness/AGENTS.md` for long-running tracked work
- **Git Hygiene**: `./harness/project-surfaces.json` for tracked vs local state boundaries
- **Output Routing**: `./02-工作流索引.md` for artifact paths

## Templates

Available under `./templates/`:
- `research-queue.template.json`
- `candidate-batch.template.json`
- `daily-note.template.json`
- `weekly-review.template.json`
- `field-search-pack.template.md`
- `expression-family.template.md`
- `simulation-capture.template.json`

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Worldquantbrain** (13558 symbols, 17060 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Worldquantbrain/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Worldquantbrain/clusters` | All functional areas |
| `gitnexus://repo/Worldquantbrain/processes` | All execution flows |
| `gitnexus://repo/Worldquantbrain/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

## BRAIN API 注意事项

### Favorite 标记
- BRAIN 平台的收藏（星标）由 `favorite: true` 字段控制
- **仅设置 `color` 或 `tags` 不会点亮星标**，必须通过 PATCH 设置 `favorite: true`
- 正确的 PATCH 请求体: `{"favorite": true, "color": "YELLOW", "tags": ["favorite"]}`
- 有效的 color 值: `"YELLOW"`, `"RED"`, `"GREEN"`, `"BLUE"` 等（不接受 hex 色码）

### /check 端点
- `GET /alphas/{id}/check` 触发 SC 计算，计算期间返回 `retry-after` 头
- SC 计算结果可能短暂返回 `"result": "ERROR"`，需要重新请求
- 平台 API 限流约 10 req/min，PATCH 操作间隔至少 4 秒

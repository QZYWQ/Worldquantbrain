# Worldquantbrain Project Agents Guide

> **工作流规则**: `.langgraph/CLAUDE.md` — 唯一真源。状态机、路由、方法学、工具编排。
> **Claude Code 入口**: `CLAUDE.md` — Claude 特定命令、GitNexus、BRAIN API。
> **项目规则**: 本文件 — 领域硬规则、执行纪律、WorldQuant 特定约束。
>
> 三文件分工明确，无重叠。改任何一份不影响另外两份。

## Purpose

This directory is the formal execution workspace for WorldQuant BRAIN research artifacts.

Use this project directory for:

- current research work
- real candidate batches and real metrics
- execution outputs under `./runs/`
- local harness state and handoff artifacts

Do not use this directory as a duplicate copy of the external knowledge base.

## Execution Layers

This project uses progressive disclosure for agent guidance.

There are three layers:

1. System-scope project rules:
   this file
2. Workflow and project-routing docs:
   `./00-项目总索引.md`, `./01-外部知识库映射.md`, `./02-工作流索引.md`, `./harness/AGENTS.md`
3. On-demand agent governance docs:
   `./03-代理工程化规则索引.md` and files under `./agent-policies/`

Do not bulk-read every document by default. Start from this file, then load only the next layer the task actually needs.

## Source Precedence

Use source precedence by fact type.

### A. Current project state

For anything about current work in progress, prefer:

1. files in this project directory
2. then the external knowledge base

### B. Current platform facts

For anything that may have changed or is account-specific, prefer:

1. official WorldQuant BRAIN pages
2. then this project directory
3. then the external knowledge base

## Window Bootstrap Rule

Treat each fresh chat window as stateless until project artifacts are reloaded.

Before any alpha-family decision, reconstruct current truth from project files in this order:

1. `./AGENTS.md`
2. `./00-项目总索引.md`
3. `./02-工作流索引.md`
4. `./harness/AGENTS.md` when the task may span sessions or needs tracked state
5. `./runs/research-contracts/current-incubation-summary.md`
6. `./runs/research-contracts/window-bootstrap-and-signflip-protocol.md`
7. the latest family registry
8. the latest next-step decision
9. the latest freeze / stop / closure memo
10. the latest official live recheck / submission memo
11. the latest simulation capture

If any of those artifacts are missing, use the best available project evidence and record the gap explicitly.

## Official Verification Boundaries

You must verify against official WorldQuant BRAIN pages before treating any of these as current truth:

- current submission criteria
- current consultant program or IQC details
- current reward or scoring details
- current UI flow
- field availability in a region, delay, or universe
- account-specific dataset access
- any current submission or test message

## Hard Rules

- Do not fabricate field names as confirmed fields on the user account.
- Do not fabricate `Sharpe`, `Fitness`, `Turnover`, `Weight`, `Sub-universe`, `Self-correlation`, or `Test Period` results.
- Do not treat template values or placeholder text as real alpha results.
- Do not copy the entire external knowledge base into this project.
- Do not claim a line is submission-ready until official checks and real simulation results support that claim.
- Prefer interpretable alpha families over opaque operator soup.
- In alpha research, a negative Sharpe on the baseline or first simple control triggers an immediate sign-flip control on the final executable expression, using `-expr` or `-1 * expr`; do not keep polishing the original sign or touch extra lookback/smoothing/group levers until the flipped version has been simulated and compared.
- Whenever an alpha is successfully submitted and recorded, create or update the corresponding successful-submission deep-dive document under `./runs/submission-memos/`; include the official post-submit state, expression, settings, real metrics/check evidence, economic hypothesis, operator-by-operator explanation, research path, failure lessons, and user-learning notes. Do not treat `ACTIVE / OS` as final OS pass unless official evidence says so.
- Keep session-start artifacts, cycle reports, and post-work notes separate by role.
- After researching and deciding a new alpha direction and plan, execute all subsequent platform operations (simulation, check, rank, submit, favorite) through the integrated pipeline scripts under `./scripts/` (`machine_lib.py`, `discover_check_rank.py`, `alpha_master_upgrade.py`, `run_upgrade.py`, `run_upgrade_v2.py`). Do not bypass these with ad-hoc `curl` or raw API calls; the pipeline scripts encode rate-limiting, error recovery, credential loading, and output routing that raw calls lack.

## Execution Discipline

Apply these execution rules on top of the project-specific hard rules.

### A. Resolve ambiguity before action

- Treat user phrasing as a starting hypothesis, not as final specification.
- State important assumptions explicitly when task meaning, fact source, or success criteria are ambiguous.
- If multiple reasonable interpretations exist, surface them instead of silently choosing one.
- If a simpler or safer path fits the project better, say so instead of mechanically following the first wording.
- Stop and clarify when confusion would otherwise cause fabricated facts, wrong scope, or invalid completion claims.

### B. Prefer minimum sufficient change

- Make the smallest durable change that solves the actual task.
- Do not add speculative flexibility, configurability, abstraction, or workflow complexity that the task did not require.
- Do not add defensive handling for scenarios that are impossible, unverified, or irrelevant to the current project boundary.
- If a shorter or clearer solution would do the same job, prefer that version.

### C. Keep changes surgical

- Touch only the files, sections, and artifacts that trace directly to the current task.
- Do not opportunistically rewrite adjacent comments, formatting, docs, or unrelated workflow behavior.
- Match existing local style, naming, and routing conventions unless the task is explicitly about changing them.
- If you notice unrelated problems, record or mention them; do not clean them up by default.
- Remove only the dead code, imports, fields, or artifacts made obsolete by your own change, not pre-existing unrelated debris.

### D. Work from verifiable goals

- Translate tasks into explicit success criteria before declaring them complete.
- For multi-step work, prefer brief `step -> verify` thinking rather than vague "make it work" execution.
- Verification should be evidence-based: tests, harness checks, generated artifacts, or official platform pages depending on task type.
- If verification could not be run, say so plainly and do not overclaim completion.

## Default Response Style

- Default to a concise answer first; expand only when the task needs steps, comparisons, evidence, or file-level traceability.
- Use numbered lists only for real sequences, hierarchy, or tightly nested substeps; use short headings only when they improve scanability.
- Give user-requested formats, length limits, tables, and citations priority over any local style preference.
- The fuller project-side output protocol lives in `./agent-policies/06-回答风格与输出协议.md`.

## Progressive Loading Rule

Default startup load is:

1. `./AGENTS.md`
2. `./00-项目总索引.md`
3. then only the specific file needed for the task

Use these routing rules:

- concept, public-doc, or idea lookup:
  `./01-外部知识库映射.md`
- template, output path, or local execution workflow:
  `./02-工作流索引.md`
- skill gates, verification protocol, or handoff discipline:
  `./03-代理工程化规则索引.md`
- long-running or resumable execution:
  `./harness/AGENTS.md`

## Skill Gate

任务分类和路由由 `.langgraph/CLAUDE.md` 统一处理。领域 skill（worldquant-brain-alpha-engineering）由 task-router 工具库自动加载。

## Harness Entry Rule

Enter harness mode when:

- work will span multiple context windows
- state must survive interruption
- one feature must be tracked from `pending` to verified completion
- evidence and handoff artifacts matter

When that is true, load:

1. `./harness/AGENTS.md`
2. then follow the harness start order defined there

## Codex App And Git

This project is intended to work cleanly with Codex App and normal git branching.

Use these boundaries:

- tracked project truth:
  rules, templates, cycle definitions, harness code, tests, and deliberate research artifacts
- local runtime state:
  `./harness/state/`, `./harness/progress.md`, `./harness/active-cycle.txt`, `./harness/reports/`, `./harness/artifacts/`
- ephemeral startup artifacts:
  `./runs/session-briefs/`

Do not treat runtime state files as default commit material.

The machine-readable surface contract for these boundaries lives in:

- `./harness/project-surfaces.json`

When Codex App is preparing a commit, prefer commits that contain:

- code or rule changes
- durable research artifacts you intentionally want under version control

Avoid mixing those with:

- transient harness state
- local machine config
- session-start handoff files

## Output Boundaries

Execution artifacts belong under `./runs/`.

Harness state belongs under `./harness/`.

The external knowledge base remains a separate reference layer and should not be mirrored into this project.

Detailed output routing lives in:

- `./02-工作流索引.md`

## Pointers

- project map: `./00-项目总索引.md`
- external knowledge: `./01-外部知识库映射.md`
- workflow/output routing: `./02-工作流索引.md`
- agent governance: `./03-代理工程化规则索引.md`
- harness operations: `./harness/AGENTS.md`
- **GitNexus instructions**: `CLAUDE.md` (单份，不在此重复)

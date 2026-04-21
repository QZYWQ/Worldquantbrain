# Worldquantbrain Project Agents Guide

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
- Keep session-start artifacts, cycle reports, and post-work notes separate by role.

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

## Skill And Gate Rule

When a task clearly matches a required skill or gate, that skill or gate is execution protocol, not optional advice.

Typical examples:

- design before implementation for ambiguous or structural work
- verification before any completion or pass claim
- harness mode for long-running tracked work

Detailed trigger rules live in:

- `./03-代理工程化规则索引.md`

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

- project map:
  `./00-项目总索引.md`
- external knowledge-base routing:
  `./01-外部知识库映射.md`
- workflow and output routing:
  `./02-工作流索引.md`
- agent governance routing:
  `./03-代理工程化规则索引.md`
- long-running harness operations:
  `./harness/AGENTS.md`

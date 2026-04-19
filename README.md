# Worldquantbrain

Formal execution workspace for WorldQuant BRAIN research, alpha iteration, and long-running AI-assisted research workflows.

This repository is not a copy of the external knowledge base. It is the execution layer that stores:

- real research queues
- real expression families
- real simulation captures
- candidate batches
- closed-cycle learning-loop artifacts
- daily and weekly notes
- submission memos
- harness rules, templates, and tests

## What This Repo Does

This project is designed to support a repeatable alpha-engineering workflow with:

- a resumable local harness for long tasks
- tracked cycle definitions and decision logs
- structured output directories under `./runs/`
- explicit separation between durable project files and local runtime state
- compatibility with Codex App and normal git workflows

Current scope:

- local research orchestration
- research artifacts and candidate packaging
- note-taking and handoff generation
- verification routing for local work products

Out of scope in the current version:

- browser automation for the WorldQuant platform
- automatic submission clicks
- fabricated platform metrics
- treating unofficial or stale platform facts as current truth

## Quick Start

Read order:

1. `./AGENTS.md`
2. `./00-项目总索引.md`
3. then only the specific routing or workflow file needed for the task

For long-running tracked work:

```bash
./harness/init.sh
./harness/coding-session.sh status
./harness/coding-session.sh doctor
./harness/coding-session.sh resume-brief
./harness/coding-session.sh session-open
./harness/coding-session.sh start
```

For harness verification:

```bash
./harness/tests/all.sh
```

## Repository Layout

```text
.
├── AGENTS.md
├── 00-项目总索引.md
├── 01-外部知识库映射.md
├── 02-工作流索引.md
├── 03-代理工程化规则索引.md
├── agent-policies/
├── harness/
│   ├── AGENTS.md
│   ├── coding-session.sh
│   ├── cycles/
│   ├── decision-log.md
│   ├── lib/
│   ├── templates/
│   ├── tests/
│   └── project-surfaces.json
├── runs/
│   ├── research-queues/
│   ├── field-search-packs/
│   ├── expression-families/
│   ├── simulation-captures/
│   ├── candidate-batches/
│   ├── learning-loops/
│   ├── notes/
│   ├── submission-memos/
│   └── session-briefs/
└── templates/
```

## Output Model

Durable execution artifacts belong under `./runs/`, for example:

- `./runs/research-queues/`
- `./runs/field-search-packs/`
- `./runs/expression-families/`
- `./runs/simulation-captures/`
- `./runs/candidate-batches/`
- `./runs/learning-loops/`
- `./runs/notes/daily/`
- `./runs/notes/weekly/`
- `./runs/submission-memos/`

Local harness state stays under `./harness/`.

The split between tracked files, local runtime state, and ephemeral startup artifacts is defined in:

- `./harness/project-surfaces.json`

## Git Hygiene

This repo intentionally keeps runtime noise out of the default commit surface.

Normally tracked:

- rules
- templates
- harness code
- tests
- cycle definitions
- deliberate research artifacts

Normally not tracked by default:

- `./harness/state/`
- `./harness/progress.md`
- `./harness/active-cycle.txt`
- `./harness/reports/`
- `./harness/artifacts/`
- `./runs/session-briefs/`

## Verification Boundaries

Do not treat any of these as current truth unless checked against official WorldQuant BRAIN pages:

- submission criteria
- reward or scoring rules
- consultant or IQC details
- dataset availability
- account-specific field access
- current UI behavior
- real simulation metrics

This repo does not permit fabricated `Sharpe`, `Fitness`, `Turnover`, `Weight`, `Sub-universe`, `Self-correlation`, or test-period results.

## Related Docs

- `./AGENTS.md`
- `./00-项目总索引.md`
- `./02-工作流索引.md`
- `./harness/AGENTS.md`
- `./harness/decision-log.md`

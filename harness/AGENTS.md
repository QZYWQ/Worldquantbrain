# Harness Agents Guide

## Purpose

This directory is the long-running execution harness for WorldQuant alpha engineering inside the project workspace.
Formal alpha work should normally run on an official cycle file, not on bootstrap fallback data.

Use it when the task:

- will span multiple sessions
- needs resumable progress
- needs explicit task tracking
- needs evidence before completion

Do not use it for one-off explanations or short documentation lookups.

## Start Order

Every long-running session should begin in this order:

1. `./harness/init.sh`
2. `./harness/coding-session.sh status`
3. `./harness/coding-session.sh doctor`
4. `./harness/coding-session.sh resume-brief`
5. `./harness/coding-session.sh session-open`
6. `./harness/coding-session.sh start`

Before trusting a harness change, run:

- `./harness/tests/all.sh`

For a fast minimum confidence check while iterating on one narrow behavior, run:

- `./harness/tests/smoke.sh`

If the task is about long-session governance rules rather than harness commands themselves, route through:

- `../03-代理工程化规则索引.md`

## Core Rules

- Work on one feature per session.
- Do not manually mark a feature complete without verification.
- Prefer harness commands over hand-editing the active cycle file.
- Leave a clean state for the next session.
- If platform facts are involved, verify them on the official platform.

## Git Hygiene

When this project runs inside Codex App or another git-driven workflow:

- treat `./harness/state/`, `./harness/progress.md`, `./harness/active-cycle.txt`, `./harness/reports/`, and `./harness/artifacts/` as local operational state by default
- treat `./runs/session-briefs/` as ephemeral startup output by default
- prefer committing harness code, templates, rules, and intentional research outputs instead of transient runtime files

The canonical machine-readable version of this surface split lives in:

- `./harness/project-surfaces.json`

## Truth Sources

- Cycle definition truth:
  the static cycle file pointed to by `./harness/active-cycle.txt` (this should usually be an official cycle, such as `./harness/cycles/official-alpha-cycle-01.json`)
- Runtime task truth:
  the synced mutable runtime state under `./harness/state/`
- Session truth:
  `./harness/progress.md`
- Decision truth:
  `./harness/decision-log.md`
- Verification evidence:
  `./harness/artifacts/`
- Closure reports:
  `./harness/reports/`

Bootstrap fallback:

- `./harness/feature_list.json` remains the bootstrap fallback cycle when no official cycle is selected.

## Completion Rule

A feature may move to `completed` only after:

1. the configured verification mode succeeds
2. evidence is available when required
3. `./harness/coding-session.sh finish ...` records the outcome

The harness also enforces:

- dependencies must already be completed before `start`
- only one feature may be `in_progress` at a time
- `finish` and `block` only work for the active `in_progress` feature
- `doctor` checks whether `progress.md` and the active runtime state still agree

For broader completion-claim or handoff protocol rules, prefer the dedicated policy layer instead of duplicating them here.

## Cycle Management

Use these commands to manage repeatable alpha cycles:

- `./harness/coding-session.sh cycle-current`
- `./harness/coding-session.sh cycle-list`
- `./harness/coding-session.sh cycle-summary`
- `./harness/coding-session.sh cycle-report [path]`
- `./harness/coding-session.sh cycle-close [path]`
- `./harness/coding-session.sh resume-brief [path]`
- `./harness/coding-session.sh session-open [path]`
- `./harness/coding-session.sh cycle-create <cycle-id>`
- `./harness/coding-session.sh cycle-switch <project-relative-path>`
- `./harness/coding-session.sh cycle-archive [path]`

Do not switch cycles while a feature is in progress.

Use the cycle end-state commands in this order:

1. `cycle-summary` for a quick terminal check
2. `cycle-report` for a durable markdown artifact
3. `resume-brief` for the next-session handoff artifact
4. `session-open` for the execution starter artifact in `./runs/`
5. `cycle-close` to enforce terminal readiness
6. `cycle-archive` only after you decide to move the JSON out of the active area

Cycle creation now uses:

- `./harness/templates/cycle-template.json`

Cycle archive output goes to:

- `./harness/archive/`

Repository default cycle note:

- this repo ships with `./harness/cycles/official-alpha-cycle-01.json` so formal alpha sessions start from a stable, shared official baseline
- bootstrap (`./harness/feature_list.json`) is still acceptable for emergency recovery, local smoke bootstrapping, or early setup before switching `active-cycle.txt` back to an official cycle

Cycle report output goes to:

- `./harness/reports/`

## Local Config

Local path settings live in:

- `./harness/config.env`

Reference defaults live in:

- `./harness/config.env.example`

## Bootstrap vs Template

- `./harness/feature_list.json` is the bootstrap fallback cycle.
- `./harness/active-cycle.txt` should usually point to an official cycle file for formal alpha work.
- `./harness/state/` stores synced mutable runtime copies for the active or previously used cycles.
- new cycles should be created from the formal cycle template, not by copying a mutated active cycle.

## Output Locations

The harness points work into the project root `runs/` tree:

- research queues:
  `./runs/research-queues/`
- field-search packs:
  `./runs/field-search-packs/`
- expression families:
  `./runs/expression-families/`
- simulation captures:
  `./runs/simulation-captures/`
- candidate batches:
  `./runs/candidate-batches/`
- session briefs:
  `./runs/session-briefs/`
- daily notes:
  `./runs/notes/daily/`
- weekly notes:
  `./runs/notes/weekly/`
- submission memos:
  `./runs/submission-memos/`

## Boundaries

Version 1 of this harness does not automate:

- WorldQuant browser flows
- Data Explorer interactions
- Check Submission clicks
- Submit Alpha actions

It only orchestrates local project work and local evidence.

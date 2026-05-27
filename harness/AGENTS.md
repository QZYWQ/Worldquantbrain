# Harness Agents Guide

> **工作流**: 见 `../.langgraph/CLAUDE.md`。本目录的编码规则由项目级工作流统一管理。
> 读取本文件后，必须同时读取 `../.langgraph/CLAUDE.md`。

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

For alpha-family work in a fresh or memory-poor window, also load `./runs/research-contracts/current-incubation-summary.md`, then `./runs/research-contracts/window-bootstrap-and-signflip-protocol.md` before choosing a family or writing a batch.

Before trusting a harness change, run:

- `./harness/tests/all.sh`

For a fast minimum confidence check while iterating on one narrow behavior, run:

- `./harness/tests/smoke.sh`

If the task is about long-session governance rules rather than harness commands themselves, route through:

- `../03-代理工程化规则索引.md`

## Incubation Protocol

The canonical incubation rules live in `./harness/incubation-protocol.json`.

- Treat that JSON file as the only source of truth for incubation stages, thresholds, stop eligibility, reclaim rules, and stage caps.
- Do not invent incubation thresholds inside shell helpers, reports, or ad hoc notes.
- `legacy_flags.freeze_all_others` in budget snapshots is deprecated and snapshot-only; it must not participate in any go/kill decision or override the incubation protocol.
- Inhibition Rule: if `min_depth_completed == false`, do not write a permanent stop memo and do not mark the family as a permanent `freeze` or `kill`.
- S-1 / S0 pure-noise exits may be screen-killed, but that is not the same thing as a permanent stop memo.
- The existing negative-Sharpe sign-flip rule still applies through A, B, C, and D; incubation adds a protected middle layer and does not weaken the front-door gate.
- All stage budgets, release windows, and thresholds come from the protocol, not from local judgment.
- Cold-pool release is manual until a dedicated helper lands: at each `cycle-close` or seven-day review, the operator checks `family-budget-ledger.json` plus the protocol, releases at most 50% of `cold_pool_balance` into the priority queue, and never spends `emergency_reserve_slots` on the scheduled release path.
- D-stage platform blocks are an execution-layer hold condition, not a signal-quality verdict: if the current lane hits an unavailable delay-0 path, unknown variable, or similar platform limitation, record hold + reclaim in the session notes, suppress same-source retry variants for that lane in the current session, and wait for a genuinely new field, delay, or mechanism before trying again.
- After the first official Check Submission failure, rescue is bounded: allow at most two targeted rescue variants per lane, each changing only one major lever and aimed at the dominant failing check; if the same core failure persists after those variants, stop spending reclaimed budget on the lane and branch away.
- These are execution-layer policies; do not encode them into `incubation-protocol.json`.
- Implementation note for `state-helpers.sh`: read the current ledger plus the protocol to display state; do not invent stop eligibility locally.

### Implementation Note for `state-helpers.sh` [P0]

`state-helpers.sh` still rewrites `progress.md` on session start/finish, so it must be updated before the new incubate / screen-kill semantics become executable truth.

- Functions to change:
  - `update_progress_start`
  - `update_progress_finish`
  - any helper that renders session-state summaries from `progress.md`
- Required read path:
  1. load `./harness/incubation-protocol.json`
  2. load `./runs/research-contracts/family-budget-ledger.json`
  3. if a family-state summary is shown, read it from the ledger row and the protocol, not from ad hoc shell logic
- Required write path:
  1. preserve unknown frontmatter keys already present in `progress.md`
  2. only mutate session fields (`current_session`, `active_feature`, `active_status`, `current_branch`, `current_head`, `last_verified_feature`, `last_verified_at`)
  3. never infer `stop_eligible`, `freeze`, `kill`, or `hold` from progress alone
- Pseudocode:
  - `ledger = json_load("runs/research-contracts/family-budget-ledger.json")`
  - `protocol = json_load("harness/incubation-protocol.json")`
  - `family_row = find_row(ledger, feature_id)`
  - `display_state = family_row["registry_state"]`
  - `display_stage = family_row["stage_budget"] or family_row["incubation_stage"]`
  - `stop_eligible = protocol_derived_min_depth_check(family_row, protocol)`
  - `write_progress(preserve_existing_frontmatter=True, update_session_fields_only=True)`

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
- `./harness/coding-session.sh cycle-learning-loop [path]`
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
3. `cycle-learning-loop` for post-cycle project / KB / skill promotion candidates
4. `resume-brief` for the next-session handoff artifact
5. `session-open` for the execution starter artifact in `./runs/`
6. `cycle-close` to enforce terminal readiness
7. `cycle-archive` only after you decide to move the JSON out of the active area

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
- learning loops:
  `./runs/learning-loops/`
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

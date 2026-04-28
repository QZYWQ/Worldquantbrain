# Task System

## Why This Exists

Worldquantbrain is the research console, scheduler, archive, and audit center. The
task system keeps long-running AI work resumable without moving orchestration into
worldquant-miner or changing miner core logic.

This skeleton only manages task decomposition, ownership, status, budget, leases,
and logs. It does not execute WQ simulations.

## Directory Layout

```text
runs/tasks/
  queue.jsonl
  active/
  done/
  failed/
  locks/
  logs/
  task_state.json
```

`queue.jsonl` stores queued tasks. Claimed and running tasks are stored as JSON
under `active/`. Terminal tasks move to `done/` or `failed/`. Each task has a
small JSON-lines event log under `logs/`.

## Task Schema

Each task is a JSON object with:

- `id`, `type`, `status`, `priority`
- timestamps: `created_at`, `updated_at`, `claimed_at`, `lease_expires_at`,
  `completed_at`, `failed_at`
- `parent` for lineage
- `budget` with `max_simulations`, `max_runtime_minutes`, `allow_real_wq`
- `payload` for task-specific inputs
- ownership fields: `attempts`, `claimed_by`
- terminal fields: `summary`, `error`

## Status Lifecycle

```text
queued -> claimed -> running -> done
queued -> claimed -> running -> failed
claimed/running -> expired
```

`add` creates a queued task. `claim-next` selects the highest-priority queued
task, breaking ties by earliest `created_at`. `heartbeat` refreshes the lease
and marks the task running. `complete` and `fail` move the task into terminal
directories.

## Lock / Lease Behavior

Claimed tasks create `runs/tasks/locks/<task_id>.lock.json` with owner,
claim time, heartbeat time, lease length, and lease expiration. Heartbeat updates
the same file. Complete and fail delete the lock. When `claim-next` notices an
expired active task, it marks that task `expired` and marks the lock released.

## Budget Policy

Budgets are declarative guardrails. The skeleton records budget limits but does
not run simulations. Safe defaults are:

- `max_simulations`: 0
- `max_runtime_minutes`: 0
- `allow_real_wq`: false

Future execution wrappers must enforce these values before calling miner tools.

## Safe Defaults

- Standard library only.
- Paths default to the Worldquantbrain repo root.
- No credential files are read.
- Logs omit task payloads and redact common sensitive labels in summaries/errors.
- `allow_real_wq` defaults to false.

## Future Extensions

- `run-one-task` integration for controlled task execution.
- Safe `variant_validation` integration with `tools/run_miner_once.sh`.
- Launchd or cron wrapper after the queue is stable.
- Max daily simulations and per-family simulation budgets.

# Harness Runtime State

This directory stores mutable per-cycle runtime state.

Rules:

- Cycle definition files under `./harness/feature_list.json` and `./harness/cycles/*.json` stay static.
- Runtime copies under `./harness/state/` hold `status`, `passes`, `evidence`, and `last_verified_at`.
- Do not hand-edit runtime state unless you are repairing a broken local harness instance.

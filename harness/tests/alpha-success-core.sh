#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-alpha-success-core.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

trap cleanup EXIT

FIXTURE_ROOT="$TMP_ROOT/fixture"
mkdir -p \
  "$FIXTURE_ROOT/families" \
  "$FIXTURE_ROOT/captures" \
  "$FIXTURE_ROOT/candidate-batches" \
  "$FIXTURE_ROOT/candidate-checks/2026-04-19/ALPHA-CAND-01" \
  "$FIXTURE_ROOT/candidate-checks/2026-04-20/ALPHA-BLOCKED-01"

cat >"$FIXTURE_ROOT/families/good-family-follow-up.md" <<'EOF'
# Good Family Follow-up

## Metadata

- Date: `2026-04-23`
- Topic: `good_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Baseline Expression

```text
group_rank(ts_rank(good_field, 60), industry)
```

## Decision

- Keep one clean anchor while the official gates stay fully green.
EOF

cat >"$FIXTURE_ROOT/families/blocked-family-follow-up.md" <<'EOF'
# Blocked Family Follow-up

## Metadata

- Date: `2026-04-23`
- Topic: `blocked_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Baseline Expression

```text
group_rank(ts_rank(blocked_field, 42), industry)
```

## Decision

- Hold: keep this family blocked until the missing official gate resolves cleanly.
EOF

cat >"$FIXTURE_ROOT/families/dead-family-follow-up.md" <<'EOF'
# Dead Family Follow-up

## Metadata

- Date: `2026-04-23`
- Topic: `dead_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Baseline Expression

```text
group_rank(dead_field, industry)
```

## Decision

- Kill the dead family and do not spend another official slot here.
EOF

cat >"$FIXTURE_ROOT/families/candidate-family-follow-up.md" <<'EOF'
# Candidate Family Follow-up

## Metadata

- Date: `2026-04-23`
- Topic: `candidate_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Baseline Expression

```text
group_rank(ts_rank(candidate_field, 60), industry)
```

## Decision

- Hold: candidate evidence can inform state, but missing full submission gates must not count as ready.
EOF

cat >"$FIXTURE_ROOT/captures/good-pass.json" <<'EOF'
{
  "capture_id": "good-pass-01",
  "topic": "good_family_batch_01",
  "capture_mode": "network-api",
  "alphas": [
    {
      "name": "good_anchor",
      "expression": "group_rank(ts_rank(good_field, 60), industry)",
      "metrics": {
        "is_sharpe": 1.71,
        "is_fitness": 1.24
      },
      "checks": [
        {"name": "LOW_SHARPE", "result": "PASS", "limit": 1.25, "value": 1.71},
        {"name": "LOW_FITNESS", "result": "PASS", "limit": 1.0, "value": 1.24},
        {"name": "LOW_TURNOVER", "result": "PASS"},
        {"name": "HIGH_TURNOVER", "result": "PASS"},
        {"name": "CONCENTRATED_WEIGHT", "result": "PASS"},
        {"name": "LOW_SUB_UNIVERSE_SHARPE", "result": "PASS"},
        {"name": "SELF_CORRELATION", "result": "PASS"},
        {"name": "MATCHES_COMPETITION", "result": "PASS"}
      ]
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/captures/blocked-partial.json" <<'EOF'
{
  "capture_id": "blocked-partial-01",
  "topic": "blocked_family_batch_01",
  "capture_mode": "manual-ui",
  "alphas": [
    {
      "name": "blocked_partial_anchor",
      "expression": "group_rank(ts_rank(blocked_field, 42), industry)",
      "metrics": {
        "sharpe": 1.62,
        "fitness": 1.18
      },
      "tests": {
        "subuniverse_pass": true,
        "check_submission_pass": true
      },
      "notes": "Strong partial evidence alone must not count as submit-ready."
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/captures/blocked-pending.json" <<'EOF'
{
  "capture_id": "blocked-pending-01",
  "topic": "blocked_family_batch_02",
  "capture_mode": "network-api",
  "alphas": [
    {
      "name": "blocked_pending_anchor",
      "expression": "group_rank(ts_rank(blocked_field, 84), industry)",
      "metrics": {
        "is_sharpe": 1.58,
        "is_fitness": 1.12
      },
      "checks": [
        {"name": "LOW_SHARPE", "result": "PASS", "limit": 1.25, "value": 1.58},
        {"name": "LOW_FITNESS", "result": "PASS", "limit": 1.0, "value": 1.12},
        {"name": "LOW_TURNOVER", "result": "PASS"},
        {"name": "HIGH_TURNOVER", "result": "PASS"},
        {"name": "CONCENTRATED_WEIGHT", "result": "PASS"},
        {"name": "LOW_SUB_UNIVERSE_SHARPE", "result": "PASS"},
        {"name": "SELF_CORRELATION", "result": "PENDING"},
        {"name": "MATCHES_COMPETITION", "result": "PASS"}
      ]
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/captures/dead-legacy.json" <<'EOF'
{
  "capture_id": "dead-legacy-01",
  "topic": "dead_family_batch_01",
  "alphas": [
    {
      "name": "dead_anchor",
      "expression": "group_rank(dead_field, industry)",
      "metrics": {
        "sharpe": 0.11,
        "fitness": 0.02
      },
      "tests": {
        "subuniverse_pass": false,
        "check_submission_pass": null
      }
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/captures/candidate-partial.json" <<'EOF'
{
  "capture_id": "candidate-partial-01",
  "topic": "candidate_family_batch_01",
  "capture_mode": "network-api",
  "evidence": {
    "expression_family": "./runs/expression-families/candidate-family-follow-up.md",
    "simulation_id": "SIM-CAND-01",
    "alpha_id": "ALPHA-CAND-01"
  },
  "alphas": [
    {
      "name": "candidate_anchor",
      "alpha_id": "ALPHA-CAND-01",
      "simulation_id": "SIM-CAND-01",
      "expression": "group_rank(ts_rank(candidate_field, 60), industry)",
      "metrics": {
        "sharpe": 1.81,
        "fitness": 1.28,
        "turnover": 0.1821
      },
      "tests": {
        "subuniverse_pass": true,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "Visible summary is strong, but full submission gates were not captured here."
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/candidate-batches/candidate-family-candidates.json" <<'EOF'
{
  "batch_id": "candidate-family-candidates",
  "topic": "candidate_family",
  "source_capture": "./captures/candidate-partial.json",
  "evidence_path": "./candidate-checks/2026-04-19/ALPHA-CAND-01/candidate-check-status.json",
  "candidates": [
    {
      "name": "candidate_anchor",
      "simulation_id": "SIM-CAND-01",
      "alpha_id": "ALPHA-CAND-01",
      "delay": 1,
      "sharpe": 1.81,
      "fitness": 1.28,
      "turnover": 0.1821,
      "max_weight_check": "PASS",
      "self_corr_check": "PASS",
      "subuniverse_pass": true,
      "test_period_pass": null,
      "test_period_observation": "Test-period card stayed positive, but this must not count as submit-ready."
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/candidate-checks/2026-04-19/ALPHA-CAND-01/candidate-check-status.json" <<'EOF'
{
  "capture_id": "candidate-family-checks-01",
  "topic": "candidate_family",
  "source_capture": "./captures/candidate-partial.json",
  "notes": [
    "Official /check resolved only the common candidate subset of gates."
  ],
  "alphas": [
    {
      "candidate_name": "candidate_anchor",
      "simulation_id": "SIM-CAND-01",
      "alpha_id": "ALPHA-CAND-01",
      "checks": {
        "concentrated_weight": "PASS",
        "self_correlation": "PASS",
        "low_fitness": "PASS",
        "low_sub_universe_sharpe": "PASS"
      }
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/candidate-checks/2026-04-20/ALPHA-BLOCKED-01/candidate-check-status.json" <<'EOF'
{
  "capture_id": "blocked-candidate-checks-01",
  "topic": "blocked_candidate_family",
  "batch_status": "blocked",
  "blocking_reason": "No real subuniverse or check evidence was captured for this blocked branch.",
  "candidates": [
    {
      "name": "blocked_candidate",
      "expression": "group_rank(blocked_candidate_field, industry)",
      "alpha_id": "ALPHA-BLOCKED-01",
      "subuniverse_pass": null,
      "max_weight_check": null,
      "self_corr_check": null,
      "notes": "Shown test-period text existed elsewhere, but it is not admissible evidence here."
    }
  ]
}
EOF

cd "$PROJECT_ROOT"

PYTHONPATH="$PROJECT_ROOT/scripts${PYTHONPATH+:$PYTHONPATH}" python3 - "$FIXTURE_ROOT" <<'PY'
from pathlib import Path
import sys

from alpha_success_core import (
    KNOWN_SUBMISSION_GATES,
    build_candidate_outcome_memory,
    build_combined_outcome_memory,
    build_family_registry_summary,
    build_official_outcome_memory,
    build_submit_ready_ledger,
    build_success_rate_state,
    load_expression_family_docs,
    load_simulation_captures,
)

fixture_root = Path(sys.argv[1])
docs = load_expression_family_docs(fixture_root / "families")
outcomes = load_simulation_captures(fixture_root / "captures")
memory = build_official_outcome_memory(outcomes)
candidate_memory = build_candidate_outcome_memory(
    candidate_batches=fixture_root / "candidate-batches",
    candidate_check_artifacts=fixture_root / "candidate-checks",
)
combined_memory = build_combined_outcome_memory(
    memory,
    candidate_batches=fixture_root / "candidate-batches",
    candidate_check_artifacts=fixture_root / "candidate-checks",
)
ledger = build_submit_ready_ledger(combined_memory)
registry = build_family_registry_summary(docs, combined_memory)
bundle = build_success_rate_state(
    family_dir=fixture_root / "families",
    capture_dir=fixture_root / "captures",
    candidate_batch_dir=fixture_root / "candidate-batches",
    candidate_check_dir=fixture_root / "candidate-checks",
)

if len(memory) != 5:
    raise SystemExit(f"expected 5 official outcome rows, got {len(memory)}")
if len(candidate_memory) != 2:
    raise SystemExit(f"expected 2 merged candidate-evidence rows, got {len(candidate_memory)}")
if len(combined_memory) != 6:
    raise SystemExit(f"expected 6 combined outcome rows, got {len(combined_memory)}")
if len(ledger) != 1:
    raise SystemExit(f"expected exactly one submit-ready alpha, got {len(ledger)}")

ready = ledger[0]
if ready["family_key"] != "good_family":
    raise SystemExit(f"unexpected ready family key: {ready['family_key']}")
if not ready["submit_ready"]:
    raise SystemExit("good_family should stay submit-ready")
if not ready["has_full_gate_coverage"]:
    raise SystemExit("good_family should preserve full gate coverage")
if ready["missing_gates"]:
    raise SystemExit("good_family should not have missing submission gates")
if ready["pending_gates"]:
    raise SystemExit("good_family should not have pending submission gates")
if set(ready["gate_results"]) != set(KNOWN_SUBMISSION_GATES):
    raise SystemExit("submit-ready ledger lost known gate coverage")

blocked_rows = [item for item in memory if item["family_key"] == "blocked_family"]
if len(blocked_rows) != 2:
    raise SystemExit(f"expected 2 blocked_family outcomes, got {len(blocked_rows)}")

partial_row = next(item for item in blocked_rows if item["capture_id"] == "blocked-partial-01")
if partial_row["evidence_level"] != "partial_tests":
    raise SystemExit(f"blocked partial row should stay partial_tests, got {partial_row['evidence_level']}")
if partial_row["submit_ready"]:
    raise SystemExit("strong partial evidence must not become submit-ready")
if partial_row["has_full_gate_coverage"]:
    raise SystemExit("partial test evidence should not count as full gate coverage")
if len(partial_row["missing_gates"]) != len(KNOWN_SUBMISSION_GATES):
    raise SystemExit("partial test evidence should keep every submission gate missing")

pending_row = next(item for item in blocked_rows if item["capture_id"] == "blocked-pending-01")
if not pending_row["has_full_gate_coverage"]:
    raise SystemExit("blocked pending row should keep full gate coverage")
if pending_row["submit_ready"]:
    raise SystemExit("pending SELF_CORRELATION must block submit-ready status")
if pending_row["pending_gates"] != ["SELF_CORRELATION"]:
    raise SystemExit(f"unexpected pending gates: {pending_row['pending_gates']}")
if pending_row["missing_gates"]:
    raise SystemExit("blocked pending row should not lose gate coverage")

states = {entry["family_key"]: entry["state"] for entry in registry}
if states.get("good_family") != "exploit":
    raise SystemExit(f"good_family should be exploit, got {states.get('good_family')}")
if states.get("blocked_family") != "hold":
    raise SystemExit(f"blocked_family should be hold, got {states.get('blocked_family')}")
if states.get("dead_family") != "kill":
    raise SystemExit(f"dead_family should be kill, got {states.get('dead_family')}")
if states.get("candidate_family") != "hold":
    raise SystemExit(f"candidate_family should stay hold, got {states.get('candidate_family')}")
if states.get("blocked_candidate_family") != "hold":
    raise SystemExit(
        "blocked_candidate_family should default to hold once evidence exists"
    )

blocked_entry = next(entry for entry in registry if entry["family_key"] == "blocked_family")
if blocked_entry["submit_ready_count"] != 0:
    raise SystemExit("blocked_family should not be submit-ready")
if blocked_entry["full_gate_outcome_count"] != 1:
    raise SystemExit("blocked_family should keep exactly one full-gate capture")
if blocked_entry["pending_gate_histogram"].get("SELF_CORRELATION") != 1:
    raise SystemExit("blocked_family should remember the pending SELF_CORRELATION gate")
if blocked_entry["best_outcome"]["capture_id"] != "blocked-pending-01":
    raise SystemExit("blocked_family best outcome should prefer the fuller gate evidence")

candidate_entry = next(entry for entry in registry if entry["family_key"] == "candidate_family")
candidate_best = candidate_entry["best_outcome"]
if candidate_best["submit_ready"]:
    raise SystemExit("candidate_family must not become submit-ready with missing submission gates")
if candidate_best["gate_results"].get("SELF_CORRELATION") != "PASS":
    raise SystemExit("candidate_family should inherit SELF_CORRELATION=PASS from candidate evidence")
if candidate_best["gate_results"].get("LOW_FITNESS") != "PASS":
    raise SystemExit("candidate_family should inherit LOW_FITNESS=PASS from candidate evidence")
if candidate_best["gate_results"].get("LOW_SUB_UNIVERSE_SHARPE") != "PASS":
    raise SystemExit("candidate_family should inherit LOW_SUB_UNIVERSE_SHARPE=PASS from candidate evidence")
if candidate_best["gate_results"].get("LOW_SHARPE") is not None:
    raise SystemExit("candidate_family should still miss LOW_SHARPE and remain non-ready")
if candidate_best["tests"].get("subuniverse_pass") is not True:
    raise SystemExit("candidate_family should preserve subuniverse_pass=true")
if set(candidate_best["evidence_sources"]) != {"candidate-batch", "candidate-check-status", "network-api"}:
    raise SystemExit("candidate_family should merge simulation, batch, and artifact evidence sources")

blocked_candidate_best = next(
    entry["best_outcome"]
    for entry in registry
    if entry["family_key"] == "blocked_candidate_family"
)
if blocked_candidate_best["submit_ready"]:
    raise SystemExit("blocked_candidate_family must never become submit-ready")
if blocked_candidate_best["tests"].get("subuniverse_pass", "sentinel") is not None:
    raise SystemExit("blocked_candidate_family should preserve null subuniverse evidence")

if len(bundle["submit_ready_ledger"]) != 1:
    raise SystemExit("bundle submit_ready_ledger should match the direct ledger")
if len(bundle["family_registry_summary"]) != 5:
    raise SystemExit("bundle family_registry_summary should contain 5 families")
if len(bundle["official_outcome_memory"]) != 5:
    raise SystemExit("bundle official_outcome_memory should contain 5 outcomes")
if len(bundle["candidate_outcome_memory"]) != 2:
    raise SystemExit("bundle candidate_outcome_memory should contain 2 merged outcomes")
if len(bundle["combined_outcome_memory"]) != 6:
    raise SystemExit("bundle combined_outcome_memory should contain 6 rows")
PY

printf 'Alpha success core test passed.\n'

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-evidence-ladders.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

trap cleanup EXIT

assert_file_exists() {
  local path="$1"
  if [ ! -f "$path" ]; then
    printf 'Expected file to exist: %s\n' "$path" >&2
    exit 1
  fi
}

FIXTURE_ROOT="$TMP_ROOT/fixture"
ARTIFACT_ROOT="$TMP_ROOT/artifacts"
PUBLISH_ROOT="$TMP_ROOT/published"
RUN_ID="fixture-evidence-ladders"

mkdir -p "$FIXTURE_ROOT/families" "$FIXTURE_ROOT/captures"

cat >"$FIXTURE_ROOT/families/front-gate-only-family.md" <<'EOF'
# Front Gate Only Family

## Metadata

- Date: `2026-04-24`
- Topic: `front_gate_only_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Baseline Expression

```text
rank(front_gate_signal)
```
EOF

cat >"$FIXTURE_ROOT/families/partial-family.md" <<'EOF'
# Partial Family

## Metadata

- Date: `2026-04-24`
- Topic: `partial_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Decision

- Branch: keep this family open.

## Baseline Expression

```text
rank(partial_signal)
```
EOF

cat >"$FIXTURE_ROOT/families/full-is-family.md" <<'EOF'
# Full IS Family

## Metadata

- Date: `2026-04-24`
- Topic: `full_is_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Decision

- Branch: keep one rescue branch open.

## Baseline Expression

```text
rank(full_is_signal)
```
EOF

cat >"$FIXTURE_ROOT/families/submit-ready-family.md" <<'EOF'
# Submit Ready Family

## Metadata

- Date: `2026-04-24`
- Topic: `submit_ready_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Decision

- Exploit: keep the anchor live.

## Baseline Expression

```text
rank(submit_ready_signal)
```
EOF

cat >"$FIXTURE_ROOT/captures/partial.json" <<'EOF'
{
  "capture_id": "partial-01",
  "topic": "partial_family_batch_01",
  "capture_mode": "manual-ui",
  "alphas": [
    {
      "expression": "rank(partial_signal)",
      "metrics": {"sharpe": 1.1},
      "tests": {"subuniverse_pass": true, "check_submission_pass": null}
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/captures/full-is.json" <<'EOF'
{
  "capture_id": "full-is-01",
  "topic": "full_is_family_batch_01",
  "capture_mode": "network-api",
  "alphas": [
    {
      "expression": "rank(full_is_signal)",
      "metrics": {"is_sharpe": 0.8, "is_fitness": 0.5},
      "checks": [
        {"name": "LOW_SHARPE", "result": "FAIL", "value": 0.8, "limit": 1.25},
        {"name": "LOW_FITNESS", "result": "FAIL", "value": 0.5, "limit": 1.0},
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

cat >"$FIXTURE_ROOT/captures/submit-ready.json" <<'EOF'
{
  "capture_id": "submit-ready-01",
  "topic": "submit_ready_family_batch_01",
  "capture_mode": "network-api",
  "alphas": [
    {
      "expression": "rank(submit_ready_signal)",
      "metrics": {"is_sharpe": 1.8, "is_fitness": 1.3},
      "checks": [
        {"name": "LOW_SHARPE", "result": "PASS", "value": 1.8, "limit": 1.25},
        {"name": "LOW_FITNESS", "result": "PASS", "value": 1.3, "limit": 1.0},
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

cd "$PROJECT_ROOT"

RUN_OUTPUT="$(python3 ./scripts/evidence_ladder_gate.py \
  --family-dir "$FIXTURE_ROOT/families" \
  --capture-dir "$FIXTURE_ROOT/captures" \
  --artifact-root "$ARTIFACT_ROOT" \
  --publish-root "$PUBLISH_ROOT" \
  --run-id "$RUN_ID")"

printf '%s\n' "$RUN_OUTPUT" | grep -Fq "Run bundle:" || {
  printf 'Expected run output to print the run bundle path.\nActual output:\n%s\n' "$RUN_OUTPUT" >&2
  exit 1
}

BUNDLE_ROOT="$ARTIFACT_ROOT/$RUN_ID"
assert_file_exists "$BUNDLE_ROOT/manifest.json"
assert_file_exists "$BUNDLE_ROOT/manifest.md"
assert_file_exists "$PUBLISH_ROOT/$RUN_ID.json"
assert_file_exists "$PUBLISH_ROOT/$RUN_ID.md"

python3 harness/lib/content-validator.py --mode evidence-ladder-json --path "$BUNDLE_ROOT/manifest.json"

python3 - "$BUNDLE_ROOT/manifest.json" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

counts = manifest.get("counts", {})
expected_counts = {
    "family_count": 4,
    "E0_front_gate_only": 1,
    "E1_local_support": 0,
    "E2_partial_official": 1,
    "E3_full_is": 1,
    "E4_submit_ready": 1,
}
if counts != expected_counts:
    raise SystemExit(f"unexpected evidence-ladder counts: {counts}")

items = {item["family_key"]: item for item in manifest.get("items", [])}
expected_keys = {
    "front_gate_only_family",
    "partial_family",
    "full_is_family",
    "submit_ready_family",
}
if set(items) != expected_keys:
    raise SystemExit(f"unexpected family set: {sorted(items)}")

front_gate = items["front_gate_only_family"]["assessment"]
if front_gate["evidence_level"] != "E0_front_gate_only" or front_gate["effective_state"] != "explore":
    raise SystemExit(f"unexpected front-gate assessment: {front_gate}")
if front_gate["branch_budget_remaining"] != 0 or front_gate["official_budget_cap"] != 1:
    raise SystemExit(f"unexpected front-gate budgets: {front_gate}")

partial = items["partial_family"]["assessment"]
if partial["evidence_level"] != "E2_partial_official":
    raise SystemExit(f"partial_family should be E2, got {partial}")
if partial["promotion_ceiling"] != "explore" or partial["effective_state"] != "explore":
    raise SystemExit(f"partial_family should be capped to explore, got {partial}")
if partial["branch_budget_remaining"] != 1 or partial["official_budget_cap"] != 1:
    raise SystemExit(f"unexpected partial-family budgets: {partial}")

full_is = items["full_is_family"]["assessment"]
if full_is["evidence_level"] != "E3_full_is":
    raise SystemExit(f"full_is_family should be E3, got {full_is}")
if full_is["promotion_ceiling"] != "branch" or full_is["effective_state"] != "branch":
    raise SystemExit(f"unexpected full_is_family promotion state: {full_is}")
if full_is["branch_budget_remaining"] != 1 or full_is["official_budget_cap"] != 2:
    raise SystemExit(f"unexpected full_is_family budgets: {full_is}")

submit_ready = items["submit_ready_family"]["assessment"]
if submit_ready["evidence_level"] != "E4_submit_ready":
    raise SystemExit(f"submit_ready_family should be E4, got {submit_ready}")
if submit_ready["promotion_ceiling"] != "exploit" or submit_ready["effective_state"] != "exploit":
    raise SystemExit(f"unexpected submit_ready_family promotion state: {submit_ready}")
if submit_ready["branch_budget_remaining"] != 0 or submit_ready["official_budget_cap"] != 1:
    raise SystemExit(f"unexpected submit_ready_family budgets: {submit_ready}")
PY

printf 'Evidence ladder gate test passed.\n'

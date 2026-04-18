#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-runtime-state.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

assert_eq() {
  local expected="$1"
  local actual="$2"
  local message="$3"
  if [ "$expected" != "$actual" ]; then
    printf 'ASSERT_EQ failed: %s\nexpected: %s\nactual: %s\n' "$message" "$expected" "$actual" >&2
    exit 1
  fi
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

./harness/coding-session.sh start ALPHA-QUEUE-001 >/dev/null

python3 - <<'PY' >"$TMP_ROOT/runtime-state-check.json"
import json
from pathlib import Path

root = Path.cwd()
active_cycle_rel = (root / "harness" / "active-cycle.txt").read_text(encoding="utf-8").strip()
definition_rel = active_cycle_rel.removeprefix("./")
definition_path = root / definition_rel
state_path = root / "harness" / "state" / definition_rel.removeprefix("harness/")

with definition_path.open("r", encoding="utf-8") as handle:
    definition_payload = json.load(handle)

with state_path.open("r", encoding="utf-8") as handle:
    runtime_payload = json.load(handle)

definition_feature = definition_payload["features"][0]
runtime_feature = runtime_payload["features"][0]

print(json.dumps(
    {
        "state_path_exists": state_path.exists(),
        "definition_has_status": "status" in definition_feature,
        "definition_has_passes": "passes" in definition_feature,
        "definition_has_evidence": "evidence" in definition_feature,
        "definition_has_last_verified_at": "last_verified_at" in definition_feature,
        "runtime_status": runtime_feature.get("status"),
        "runtime_passes": runtime_feature.get("passes"),
    },
    ensure_ascii=False,
))
PY

state_path_exists="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["state_path_exists"])' "$TMP_ROOT/runtime-state-check.json")"
assert_eq "True" "$state_path_exists" "runtime state file should exist under harness/state"

definition_has_status="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["definition_has_status"])' "$TMP_ROOT/runtime-state-check.json")"
assert_eq "False" "$definition_has_status" "cycle definition should not store runtime status"

definition_has_passes="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["definition_has_passes"])' "$TMP_ROOT/runtime-state-check.json")"
assert_eq "False" "$definition_has_passes" "cycle definition should not store runtime pass/fail state"

definition_has_evidence="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["definition_has_evidence"])' "$TMP_ROOT/runtime-state-check.json")"
assert_eq "False" "$definition_has_evidence" "cycle definition should not store runtime evidence"

definition_has_last_verified_at="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["definition_has_last_verified_at"])' "$TMP_ROOT/runtime-state-check.json")"
assert_eq "False" "$definition_has_last_verified_at" "cycle definition should not store last_verified_at"

runtime_status="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["runtime_status"])' "$TMP_ROOT/runtime-state-check.json")"
assert_eq "in_progress" "$runtime_status" "runtime state should track the active status"

runtime_passes="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["runtime_passes"])' "$TMP_ROOT/runtime-state-check.json")"
assert_eq "False" "$runtime_passes" "runtime state should initialize passes=false while work is in progress"

printf 'Harness runtime state decoupling test passed.\n'

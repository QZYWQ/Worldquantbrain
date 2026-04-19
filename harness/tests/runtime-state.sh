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

status_output="$(./harness/coding-session.sh status)"
active_feature="$(printf '%s\n' "$status_output" | awk -F': ' '/active_feature:/ {print $2}')"
active_status="$(printf '%s\n' "$status_output" | awk -F': ' '/active_status:/ {print $2}')"

if [ "$active_status" = "in_progress" ] && [ -n "$active_feature" ] && [ "$active_feature" != "null" ]; then
  ./harness/coding-session.sh block "$active_feature" --summary "Reset copied runtime state for runtime-state test." >/dev/null
fi

./harness/coding-session.sh cycle-switch ./harness/cycles/official-alpha-cycle-01.json >/dev/null

python3 - <<'PY'
import json
import re
from pathlib import Path

root = Path.cwd()
state_path = root / "harness" / "state" / "cycles" / "official-alpha-cycle-01.json"
with state_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

for feature in payload["features"]:
    feature["status"] = "pending"
    feature["passes"] = False
    feature["evidence"] = {}
    feature["last_verified_at"] = None

with state_path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")

progress_path = root / "harness" / "progress.md"
text = progress_path.read_text(encoding="utf-8")
replacements = {
    r"current_session:\s*\d+": "current_session: 0",
    r"active_feature:\s*.+": "active_feature: null",
    r"active_status:\s*.+": "active_status: idle",
    r"last_verified_feature:\s*.+": "last_verified_feature: null",
    r"last_verified_at:\s*.+": "last_verified_at: null",
    r"- Active feature: .+": "- Active feature: null",
    r"- Session status: .+": "- Session status: idle",
}
for pattern, replacement in replacements.items():
    text = re.sub(pattern, replacement, text)
progress_path.write_text(text, encoding="utf-8")
PY

./harness/coding-session.sh start ALPHA-QUEUE-001 >/dev/null
active_feature="ALPHA-QUEUE-001"

ACTIVE_FEATURE="$active_feature" python3 - <<'PY' >"$TMP_ROOT/runtime-state-check.json"
import os
import json
from pathlib import Path

root = Path.cwd()
active_feature = os.environ["ACTIVE_FEATURE"]
active_cycle_rel = (root / "harness" / "active-cycle.txt").read_text(encoding="utf-8").strip()
definition_rel = active_cycle_rel.removeprefix("./")
definition_path = root / definition_rel
state_path = root / "harness" / "state" / definition_rel.removeprefix("harness/")

with definition_path.open("r", encoding="utf-8") as handle:
    definition_payload = json.load(handle)

with state_path.open("r", encoding="utf-8") as handle:
    runtime_payload = json.load(handle)

definition_feature = next(feature for feature in definition_payload["features"] if feature["id"] == active_feature)
runtime_feature = next(feature for feature in runtime_payload["features"] if feature["id"] == active_feature)

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

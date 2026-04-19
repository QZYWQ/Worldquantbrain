#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-cycle-close-report.XXXXXX")"

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

assert_output_contains() {
  local needle="$1"
  local haystack="$2"
  if ! printf '%s\n' "$haystack" | grep -Fq "$needle"; then
    printf 'Expected output to contain: %s\nActual output:\n%s\n' "$needle" "$haystack" >&2
    exit 1
  fi
}

assert_command_fails() {
  if "$@"; then
    printf 'Expected command to fail but it succeeded: %s\n' "$*" >&2
    exit 1
  fi
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

cycle_id="test-cycle-close-report-$$"
cycle_rel="./harness/cycles/${cycle_id}.json"
report_rel="./harness/reports/${cycle_id}-report.md"

status_output="$(./harness/coding-session.sh status)"
active_feature="$(printf '%s\n' "$status_output" | awk -F': ' '/active_feature:/ {print $2}')"
active_status="$(printf '%s\n' "$status_output" | awk -F': ' '/active_status:/ {print $2}')"
if [ "$active_status" = "in_progress" ] && [ -n "$active_feature" ] && [ "$active_feature" != "null" ]; then
  ./harness/coding-session.sh block "$active_feature" --summary "Reset copied runtime state for cycle-close-report test." >/dev/null
fi

./harness/coding-session.sh cycle-create "$cycle_id" >/dev/null

report_output="$(./harness/coding-session.sh cycle-report)"
assert_output_contains "$report_rel" "$report_output"

report_path="$PROJECT_COPY/${report_rel#./}"
[ -f "$report_path" ] || {
  printf 'Expected report file to exist: %s\n' "$report_path" >&2
  exit 1
}

assert_command_fails ./harness/coding-session.sh cycle-close >/dev/null 2>&1

python3 - "$cycle_id" <<'PY'
import json
import sys
from pathlib import Path

cycle_id = sys.argv[1]
path = Path(f"harness/cycles/{cycle_id}.json")
state_path = Path(f"harness/state/cycles/{cycle_id}.json")
with state_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

for feature in payload["features"]:
    feature["status"] = "completed"
    feature["passes"] = True

with state_path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

close_output="$(./harness/coding-session.sh cycle-close)"
assert_output_contains "Cycle closed" "$close_output"
assert_output_contains "$report_rel" "$close_output"

current_cycle="$(./harness/coding-session.sh cycle-current)"
assert_eq "$cycle_rel" "$current_cycle" "cycle-close should not archive or switch by itself"

printf 'Harness cycle close and report test passed.\n'

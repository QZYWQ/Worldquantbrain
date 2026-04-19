#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-cycle-lifecycle.XXXXXX")"

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
  if ! printf '%s\n' "$haystack" | grep -Fq -- "$needle"; then
    printf 'Expected output to contain: %s\nActual output:\n%s\n' "$needle" "$haystack" >&2
    exit 1
  fi
}

assert_file_contains() {
  local needle="$1"
  local path="$2"
  if ! grep -Fq -- "$needle" "$path"; then
    printf 'Expected file to contain: %s\nFile: %s\n' "$needle" "$path" >&2
    exit 1
  fi
}

assert_output_not_contains() {
  local needle="$1"
  local haystack="$2"
  if printf '%s\n' "$haystack" | grep -Fq -- "$needle"; then
    printf 'Did not expect output to contain: %s\nActual output:\n%s\n' "$needle" "$haystack" >&2
    exit 1
  fi
}

assert_file_not_contains() {
  local needle="$1"
  local path="$2"
  if grep -Fq -- "$needle" "$path"; then
    printf 'Did not expect file to contain: %s\nFile: %s\n' "$needle" "$path" >&2
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
  ./harness/coding-session.sh block "$active_feature" --summary "Reset copied runtime state for cycle-lifecycle test." >/dev/null
fi

python3 - <<'PY'
import json
from pathlib import Path

path = Path("harness/feature_list.json")
with path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

payload["project_goal"] = "MUTATED ACTIVE CYCLE GOAL"
payload["features"][0]["title"] = "MUTATED ACTIVE CYCLE TITLE"

with path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

./harness/coding-session.sh cycle-create official-alpha-cycle-03 >/dev/null

python3 - <<'PY' >"$TMP_ROOT/new-cycle-values.txt"
import json
from pathlib import Path

path = Path("harness/cycles/official-alpha-cycle-03.json")
with path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

print(payload["project_goal"])
print(payload["features"][0]["title"])
PY

new_goal="$(sed -n '1p' "$TMP_ROOT/new-cycle-values.txt")"
new_title="$(sed -n '2p' "$TMP_ROOT/new-cycle-values.txt")"

assert_eq "Create a formal, resumable alpha engineering workflow for the first official WorldQuant alpha cycle." "$new_goal" "new cycle should come from canonical template goal"
assert_eq "Create the first official research queue" "$new_title" "new cycle should come from canonical template title"

summary_output="$(./harness/coding-session.sh cycle-summary)"
assert_output_contains "Active cycle:" "$summary_output"
assert_output_contains "Active cycle: ./harness/cycles/official-alpha-cycle-03.json" "$summary_output"
assert_output_contains "Cycle type: official" "$summary_output"
assert_output_contains "Cycle profile: research-first" "$summary_output"
assert_output_contains "Status counts:" "$summary_output"
assert_output_contains "- pending:" "$summary_output"
assert_output_contains "Next actionable feature: ALPHA-QUEUE-001" "$summary_output"
assert_output_not_contains "Warning: active cycle is bootstrap fallback state." "$summary_output"

report_output="$(./harness/coding-session.sh cycle-report)"
assert_output_contains "./harness/reports/official-alpha-cycle-03-report.md" "$report_output"

report_path="$PROJECT_COPY/harness/reports/official-alpha-cycle-03-report.md"
assert_file_contains "- Cycle type: official" "$report_path"
assert_file_contains "- Cycle profile: research-first" "$report_path"
assert_file_not_contains "- Note: Report generated from bootstrap fallback state." "$report_path"

python3 - <<'PY'
import json
from pathlib import Path

path = Path("harness/state/cycles/official-alpha-cycle-03.json")
with path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

for feature in payload["features"]:
    feature["status"] = "completed"
    feature["passes"] = True

with path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

archive_output="$(./harness/coding-session.sh cycle-archive ./harness/cycles/official-alpha-cycle-03.json)"
assert_output_contains "./harness/archive/official-alpha-cycle-03.json" "$archive_output"

current_cycle="$(./harness/coding-session.sh cycle-current)"
assert_eq "./harness/feature_list.json" "$current_cycle" "archiving the active cycle should fall back to bootstrap cycle"

printf 'Harness cycle lifecycle test passed.\n'

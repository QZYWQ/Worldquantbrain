#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-resume-brief.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

assert_output_contains() {
  local needle="$1"
  local haystack="$2"
  if ! printf '%s\n' "$haystack" | grep -Fq "$needle"; then
    printf 'Expected output to contain: %s\nActual output:\n%s\n' "$needle" "$haystack" >&2
    exit 1
  fi
}

assert_file_contains() {
  local needle="$1"
  local path="$2"
  if ! grep -Fq "$needle" "$path"; then
    printf 'Expected file to contain: %s\nFile: %s\n' "$needle" "$path" >&2
    exit 1
  fi
}

assert_file_not_contains() {
  local needle="$1"
  local path="$2"
  if grep -Fq "$needle" "$path"; then
    printf 'Did not expect file to contain: %s\nFile: %s\n' "$needle" "$path" >&2
    exit 1
  fi
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

cycle_id="test-resume-brief-$$"
report_rel="./harness/reports/${cycle_id}-report.md"
brief_rel="./harness/reports/${cycle_id}-resume-brief.md"

status_output="$(./harness/coding-session.sh status)"
active_feature="$(printf '%s\n' "$status_output" | awk -F': ' '/active_feature:/ {print $2}')"
active_status="$(printf '%s\n' "$status_output" | awk -F': ' '/active_status:/ {print $2}')"
if [ "$active_status" = "in_progress" ] && [ -n "$active_feature" ] && [ "$active_feature" != "null" ]; then
  ./harness/coding-session.sh block "$active_feature" --summary "Reset copied runtime state for resume-brief test." >/dev/null
fi

./harness/coding-session.sh cycle-create "$cycle_id" >/dev/null

python3 - "$cycle_id" <<'PY'
import json
import sys
from pathlib import Path

cycle_id = sys.argv[1]
path = Path(f"harness/state/cycles/{cycle_id}.json")
with path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

features = {feature["id"]: feature for feature in payload["features"]}
features["ALPHA-QUEUE-001"]["status"] = "completed"
features["ALPHA-QUEUE-001"]["passes"] = True
features["ALPHA-QUEUE-001"]["evidence"]["summary"] = "Initial queue built."

with path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

./harness/coding-session.sh cycle-report >/dev/null

resume_output="$(./harness/coding-session.sh resume-brief)"
assert_output_contains "$brief_rel" "$resume_output"

brief_path="$PROJECT_COPY/${brief_rel#./}"
[ -f "$brief_path" ] || {
  printf 'Expected resume brief file to exist: %s\n' "$brief_path" >&2
  exit 1
}

assert_file_contains "# Resume Brief" "$brief_path"
assert_file_contains "Cycle type: official" "$brief_path"
assert_file_contains "Cycle profile: research-first" "$brief_path"
assert_file_not_contains "This is the bootstrap fallback cycle, not a formal official alpha cycle." "$brief_path"
assert_file_contains "## Recommended Next Action" "$brief_path"
assert_file_contains "ALPHA-FIELD-001" "$brief_path"
assert_file_contains "Create the primary field-search pack" "$brief_path"
assert_file_contains "## Doctor" "$brief_path"
assert_file_contains "## Recent Harness Decisions" "$brief_path"
assert_file_contains "$report_rel" "$brief_path"

printf 'Harness resume brief test passed.\n'

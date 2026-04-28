#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-read-only-surface.XXXXXX")"

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

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

active_cycle_rel="$(cat ./harness/active-cycle.txt)"
active_cycle_stem="$(basename "$active_cycle_rel" .json)"

summary_output="$(./harness/coding-session.sh cycle-summary)"
assert_output_contains "Active cycle: ${active_cycle_rel}" "$summary_output"
assert_output_contains "Next actionable feature:" "$summary_output"
assert_output_contains "Evolution bootstrap: ./harness/coding-session.sh evolution-bootstrap" "$summary_output"
assert_output_contains "Execution suggestion: ./harness/coding-session.sh evolution-bootstrap" "$summary_output"
assert_output_contains "Doctor: clean" "$summary_output"
next_actionable_feature="$(printf '%s\n' "$summary_output" | awk -F': ' '/Next actionable feature:/ {print $2}')"
[ -n "$next_actionable_feature" ] || {
  printf 'Expected non-empty next actionable feature in cycle-summary output.\n' >&2
  exit 1
}

doctor_output="$(./harness/coding-session.sh doctor)"
assert_output_contains "State is consistent." "$doctor_output"

report_output="$(./harness/coding-session.sh cycle-report)"
assert_output_contains "./harness/reports/${active_cycle_stem}-report.md" "$report_output"
report_path="$PROJECT_COPY/harness/reports/${active_cycle_stem}-report.md"
[ -f "$report_path" ] || {
  printf 'Expected cycle report file to exist: %s\n' "$report_path" >&2
  exit 1
}

resume_output="$(./harness/coding-session.sh resume-brief)"
assert_output_contains "./harness/reports/${active_cycle_stem}-resume-brief.md" "$resume_output"
resume_path="$PROJECT_COPY/harness/reports/${active_cycle_stem}-resume-brief.md"
[ -f "$resume_path" ] || {
  printf 'Expected resume brief file to exist: %s\n' "$resume_path" >&2
  exit 1
}
assert_file_contains "# Resume Brief" "$resume_path"
assert_file_contains "## Recommended Next Action" "$resume_path"
assert_file_contains "## Execution Suggestion" "$resume_path"
assert_file_contains "## Evolution Bootstrap" "$resume_path"
assert_file_contains "./harness/coding-session.sh evolution-bootstrap" "$resume_path"

session_output="$(./harness/coding-session.sh session-open)"
assert_output_contains "./runs/session-briefs/" "$session_output"
session_rel_path="$(printf '%s\n' "$session_output" | tail -n 1)"
session_path="$PROJECT_COPY/${session_rel_path#./}"
[ -f "$session_path" ] || {
  printf 'Expected session brief file to exist: %s\n' "$session_path" >&2
  exit 1
}
assert_file_contains "# Session Brief" "$session_path"
assert_file_contains "## Verification Plan" "$session_path"
assert_file_contains "## Evolution Bootstrap" "$session_path"

printf 'Harness read-only surface test passed.\n'

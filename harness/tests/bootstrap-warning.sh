#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-bootstrap-warning.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
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

mkdir -p ./runs/session-briefs
printf './harness/feature_list.json\n' > ./harness/active-cycle.txt

resume_output="$(./harness/coding-session.sh resume-brief)"
resume_rel_path="$(printf '%s\n' "$resume_output" | tail -n 1)"
resume_path="$PROJECT_COPY/${resume_rel_path#./}"
[ -f "$resume_path" ] || {
  printf 'Expected resume brief file to exist: %s\n' "$resume_path" >&2
  exit 1
}

session_output="$(./harness/coding-session.sh session-open)"
session_rel_path="$(printf '%s\n' "$session_output" | tail -n 1)"
session_path="$PROJECT_COPY/${session_rel_path#./}"
[ -f "$session_path" ] || {
  printf 'Expected session brief file to exist: %s\n' "$session_path" >&2
  exit 1
}

warning_text="This is the bootstrap fallback cycle, not a formal official alpha cycle."
assert_file_contains "$warning_text" "$resume_path"
assert_file_contains "$warning_text" "$session_path"

printf 'Harness bootstrap warning test passed.\n'

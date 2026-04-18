#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-parallel.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

for i in 1 2 3; do
  ./harness/coding-session.sh cycle-report >"$TMP_ROOT/cycle-report.$i.out" 2>"$TMP_ROOT/cycle-report.$i.err" &
  ./harness/coding-session.sh resume-brief >"$TMP_ROOT/resume-brief.$i.out" 2>"$TMP_ROOT/resume-brief.$i.err" &
  ./harness/coding-session.sh session-open >"$TMP_ROOT/session-open.$i.out" 2>"$TMP_ROOT/session-open.$i.err" &
  wait
done

for err_file in "$TMP_ROOT"/*.err; do
  if [ -s "$err_file" ]; then
    printf 'Unexpected stderr from parallel read-only command: %s\n' "$err_file" >&2
    cat "$err_file" >&2
    exit 1
  fi
done

printf 'Harness read-only parallel test passed.\n'

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-codex-readiness.XXXXXX")"

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

root_agents="$PROJECT_COPY/AGENTS.md"
gitignore_path="$PROJECT_COPY/.gitignore"
preflight_path="$PROJECT_COPY/harness/lib/env-preflight.sh"
harness_agents="$PROJECT_COPY/harness/AGENTS.md"
surface_contract="$PROJECT_COPY/harness/project-surfaces.json"
session_brief_readme="$PROJECT_COPY/runs/session-briefs/README.md"
session_brief_dummy="$PROJECT_COPY/runs/session-briefs/ephemeral-brief.md"

[ -f "$root_agents" ] || {
  printf 'Expected root AGENTS.md to exist: %s\n' "$root_agents" >&2
  exit 1
}

[ -f "$gitignore_path" ] || {
  printf 'Expected .gitignore to exist: %s\n' "$gitignore_path" >&2
  exit 1
}

[ -f "$surface_contract" ] || {
  printf 'Expected surface contract to exist: %s\n' "$surface_contract" >&2
  exit 1
}

git -C "$PROJECT_COPY" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  printf 'Expected project copy to remain a git work tree: %s\n' "$PROJECT_COPY" >&2
  exit 1
}

assert_file_contains 'require_file "${PROJECT_ROOT}/AGENTS.md"' "$preflight_path"
assert_file_contains 'require_file "$(surface_contract_file_path)"' "$preflight_path"
assert_file_contains 'harness/state/**' "$gitignore_path"
assert_file_contains 'harness/progress.md' "$gitignore_path"
assert_file_contains 'harness/active-cycle.txt' "$gitignore_path"
assert_file_contains 'harness/reports/**' "$gitignore_path"
assert_file_contains 'harness/artifacts/**' "$gitignore_path"
assert_file_contains 'runs/session-briefs/**' "$gitignore_path"
assert_file_contains '!runs/session-briefs/README.md' "$gitignore_path"
assert_file_contains 'Codex App And Git' "$root_agents"
assert_file_contains 'project-surfaces.json' "$root_agents"
assert_file_contains '## Git Hygiene' "$harness_agents"
assert_file_contains 'project-surfaces.json' "$harness_agents"

printf '# ephemeral\n' >"$session_brief_dummy"

git -C "$PROJECT_COPY" check-ignore -q "$session_brief_dummy" || {
  printf 'Expected session brief artifact to be ignored: %s\n' "$session_brief_dummy" >&2
  exit 1
}

if git -C "$PROJECT_COPY" check-ignore -q "$session_brief_readme"; then
  printf 'Did not expect session brief README to be ignored: %s\n' "$session_brief_readme" >&2
  exit 1
fi

printf 'Harness Codex app readiness test passed.\n'

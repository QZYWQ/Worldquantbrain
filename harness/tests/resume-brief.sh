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

./harness/coding-session.sh cycle-create official-alpha-cycle-05 >/dev/null

python3 - <<'PY'
import json
from pathlib import Path

path = Path("harness/state/cycles/official-alpha-cycle-05.json")
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
assert_output_contains "./harness/reports/official-alpha-cycle-05-resume-brief.md" "$resume_output"

brief_path="$PROJECT_COPY/harness/reports/official-alpha-cycle-05-resume-brief.md"
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
assert_file_contains "./harness/reports/official-alpha-cycle-05-report.md" "$brief_path"

printf 'Harness resume brief test passed.\n'

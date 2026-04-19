#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-learning-loop.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
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

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

cycle_id="test-learning-loop-$$"
project_rel="./runs/learning-loops/${cycle_id}-project-lessons.md"
kb_rel="./runs/learning-loops/${cycle_id}-kb-candidate.md"
skill_rel="./runs/learning-loops/${cycle_id}-skill-candidate.md"
promotion_rel="./runs/learning-loops/${cycle_id}-promotion-gate.md"
kb_draft_rel="./runs/learning-loops/${cycle_id}-kb-promotion-draft.md"
skill_draft_rel="./runs/learning-loops/${cycle_id}-skill-promotion-draft.md"

status_output="$(./harness/coding-session.sh status)"
active_feature="$(printf '%s\n' "$status_output" | awk -F': ' '/active_feature:/ {print $2}')"
active_status="$(printf '%s\n' "$status_output" | awk -F': ' '/active_status:/ {print $2}')"
if [ "$active_status" = "in_progress" ] && [ -n "$active_feature" ] && [ "$active_feature" != "null" ]; then
  ./harness/coding-session.sh block "$active_feature" --summary "Reset copied runtime state for learning-loop test." >/dev/null
fi

./harness/coding-session.sh cycle-create "$cycle_id" >/dev/null

python3 - "$cycle_id" <<'PY'
import json
import sys
from pathlib import Path

cycle_id = sys.argv[1]
state_path = Path(f"harness/state/cycles/{cycle_id}.json")
with state_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

for feature in payload["features"]:
    feature["status"] = "completed"
    feature["passes"] = True
    feature["evidence"]["summary"] = f"Completed for learning-loop test: {feature['id']}"

candidate_feature = next(feature for feature in payload["features"] if feature["id"] == "ALPHA-CAND-001")
candidate_feature["status"] = "blocked"
candidate_feature["passes"] = False
candidate_feature["evidence"]["summary"] = "Blocked because real submission-check evidence is still missing."

with state_path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

bundle_output="$(./harness/coding-session.sh cycle-learning-loop)"
assert_output_contains "$project_rel" "$bundle_output"
assert_output_contains "$kb_rel" "$bundle_output"
assert_output_contains "$skill_rel" "$bundle_output"
assert_output_contains "$promotion_rel" "$bundle_output"
assert_output_contains "$kb_draft_rel" "$bundle_output"
assert_output_contains "$skill_draft_rel" "$bundle_output"

project_path="$PROJECT_COPY/${project_rel#./}"
kb_path="$PROJECT_COPY/${kb_rel#./}"
skill_path="$PROJECT_COPY/${skill_rel#./}"
promotion_path="$PROJECT_COPY/${promotion_rel#./}"
kb_draft_path="$PROJECT_COPY/${kb_draft_rel#./}"
skill_draft_path="$PROJECT_COPY/${skill_draft_rel#./}"

assert_file_contains "# Project Learning Loop" "$project_path"
assert_file_contains "Blocked because real submission-check evidence is still missing." "$project_path"
assert_file_contains "# KB Promotion Candidate" "$kb_path"
assert_file_contains "record a blocked memo instead of backfilling a candidate-batch JSON" "$kb_path"
assert_file_contains "# Skill Promotion Candidate" "$skill_path"
assert_file_contains "require non-null real submission-check or subuniverse evidence" "$skill_path"
assert_file_contains "# Promotion Gate" "$promotion_path"
assert_file_contains "## KB Gate" "$promotion_path"
assert_file_contains "## Skill Gate" "$promotion_path"
assert_file_contains '- Status: `REVIEW`' "$promotion_path"
assert_file_contains "# KB Promotion Draft" "$kb_draft_path"
assert_file_contains "## Promotion Posture" "$kb_draft_path"
assert_file_contains '- Status: `REVIEW`' "$kb_draft_path"
assert_file_contains "# Skill Promotion Draft" "$skill_draft_path"
assert_file_contains "## Promotion Posture" "$skill_draft_path"
assert_file_contains '- Status: `REVIEW`' "$skill_draft_path"

close_output="$(./harness/coding-session.sh cycle-close)"
assert_output_contains "Learning loop artifacts:" "$close_output"
assert_output_contains "$project_rel" "$close_output"
assert_output_contains "$promotion_rel" "$close_output"
assert_output_contains "$kb_draft_rel" "$close_output"
assert_output_contains "$skill_draft_rel" "$close_output"

printf 'Harness learning-loop test passed.\n'

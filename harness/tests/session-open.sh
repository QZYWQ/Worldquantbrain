#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-session-open.XXXXXX")"

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

mkdir -p ./runs/session-briefs

session_output="$(./harness/coding-session.sh session-open)"
assert_output_contains "./runs/session-briefs/" "$session_output"
assert_output_contains "alpha-queue-001.md" "$session_output"

brief_rel_path="$(printf '%s\n' "$session_output" | tail -n 1)"
brief_path="$PROJECT_COPY/${brief_rel_path#./}"
[ -f "$brief_path" ] || {
  printf 'Expected session brief file to exist at: %s\n' "$brief_path" >&2
  exit 1
}

assert_file_contains "# Session Brief" "$brief_path"
assert_file_contains "Cycle type: official" "$brief_path"
assert_file_contains "Cycle profile: research-first" "$brief_path"
assert_file_not_contains "This is the bootstrap fallback cycle, not a formal official alpha cycle." "$brief_path"
assert_file_contains "## Selected Feature" "$brief_path"
assert_file_contains "ALPHA-QUEUE-001" "$brief_path"
assert_file_contains "Create the first official research queue" "$brief_path"
assert_file_contains "./templates/research-queue.template.json" "$brief_path"
assert_file_contains "kb://03-研究方法/05-首批真实候选池.md" "$brief_path"
assert_file_contains "kb://03-研究方法/06-首批真实候选优先级.md" "$brief_path"
assert_file_contains "## Expected Outputs" "$brief_path"
assert_file_contains "./runs/research-queues/official-alpha-cycle-01.json" "$brief_path"
assert_file_contains "## Verification Plan" "$brief_path"
assert_file_contains "research-queue-json" "$brief_path"
assert_file_contains "## Completion Handoff" "$brief_path"
assert_file_contains "script://research_queue_builder.py" "$brief_path"
assert_file_not_contains "/Users/zpdedn/Documents/Obsidian Vault/" "$brief_path"
assert_file_not_contains "/Users/zpdedn/.codex/skills/" "$brief_path"

python3 - <<'PY' >"$TMP_ROOT/official-cycle-source-refs.txt"
import json
from pathlib import Path

path = Path("harness/state/cycles/official-alpha-cycle-01.json")
with path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

features = {feature["id"]: feature for feature in payload["features"]}

checks = {
    "ALPHA-FIELD-001": [
        "./templates/field-search-pack.template.md",
        "kb://02-平台基础/07-Data Explorer 与字段研究工作流.md",
        "kb://02-平台基础/05-数据字段、覆盖率与数据体检.md",
    ],
    "ALPHA-EXPR-001": [
        "./templates/expression-family.template.md",
        "kb://03-研究方法/02-从假设到表达式.md",
        "kb://03-研究方法/04-初学者表达式模式库.md",
    ],
    "ALPHA-SIM-001": [
        "./templates/simulation-capture.template.json",
        "kb://02-平台基础/04-结果指标与提交门槛.md",
        "kb://02-平台基础/06-Test Period、IS-OS 与防过拟合.md",
    ],
    "ALPHA-CAND-001": [
        "./templates/candidate-batch.template.json",
        "kb://03-研究方法/03-低相关与稳健性.md",
        "kb://03-研究方法/01-Alpha 研究流程.md",
    ],
}

for feature_id, expected_refs in checks.items():
    refs = features[feature_id]["source_refs"]
    for ref in expected_refs:
        if ref not in refs:
            raise SystemExit(f"{feature_id} missing source ref: {ref}")

print("official cycle source refs verified")
PY

assert_file_contains "official cycle source refs verified" "$TMP_ROOT/official-cycle-source-refs.txt"

python3 - <<'PY'
import json
from pathlib import Path

path = Path("harness/state/cycles/official-alpha-cycle-01.json")
with path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

features = {feature["id"]: feature for feature in payload["features"]}
features["ALPHA-QUEUE-001"]["status"] = "completed"
features["ALPHA-QUEUE-001"]["passes"] = True
features["ALPHA-QUEUE-001"]["evidence"]["summary"] = "Queue completed for field runtime check."

with path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

field_session_output="$(./harness/coding-session.sh session-open)"
assert_output_contains "alpha-field-001.md" "$field_session_output"

field_brief_rel_path="$(printf '%s\n' "$field_session_output" | tail -n 1)"
field_brief_path="$PROJECT_COPY/${field_brief_rel_path#./}"
[ -f "$field_brief_path" ] || {
  printf 'Expected field session brief file to exist at: %s\n' "$field_brief_path" >&2
  exit 1
}

assert_file_contains "ALPHA-FIELD-001" "$field_brief_path"
assert_file_contains "./templates/field-search-pack.template.md" "$field_brief_path"
assert_file_contains "kb://02-平台基础/07-Data Explorer 与字段研究工作流.md" "$field_brief_path"
assert_file_contains "kb://02-平台基础/05-数据字段、覆盖率与数据体检.md" "$field_brief_path"
assert_file_not_contains "/Users/zpdedn/Documents/Obsidian Vault/" "$field_brief_path"

printf 'Harness session open test passed.\n'

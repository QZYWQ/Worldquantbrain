#!/usr/bin/env bash

HARNESS_LIB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${HARNESS_LIB_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"
EXTERNAL_KB_ROOT_DEFAULT="${HOME}/Documents/Obsidian Vault/个人项目/Worldquantbrain"
WQB_SCRIPT_ROOT_DEFAULT="${HOME}/.codex/skills/worldquant-brain-alpha-engineering/scripts"
EXTERNAL_KB_ROOT="$EXTERNAL_KB_ROOT_DEFAULT"
WQB_SCRIPT_ROOT="$WQB_SCRIPT_ROOT_DEFAULT"

config_example_path() {
  printf '%s\n' "${HARNESS_ROOT}/config.env.example"
}

config_file_path() {
  printf '%s\n' "${HARNESS_ROOT}/config.env"
}

active_cycle_pointer_path() {
  printf '%s\n' "${HARNESS_ROOT}/active-cycle.txt"
}

cycle_template_file_path() {
  printf '%s\n' "${HARNESS_ROOT}/templates/cycle-template.json"
}

archive_root_path() {
  printf '%s\n' "${HARNESS_ROOT}/archive"
}

report_root_path() {
  printf '%s\n' "${HARNESS_ROOT}/reports"
}

state_root_path() {
  printf '%s\n' "${HARNESS_ROOT}/state"
}

session_brief_root_path() {
  printf '%s\n' "${PROJECT_ROOT}/runs/session-briefs"
}

surface_contract_file_path() {
  printf '%s\n' "${HARNESS_ROOT}/project-surfaces.json"
}

load_harness_config() {
  local config_path
  config_path="$(config_file_path)"
  if [ -f "$config_path" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$config_path"
    set +a
  fi
}

timestamp_now() {
  date '+%Y-%m-%dT%H:%M:%S%z'
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

resolve_project_path() {
  python3 - "$PROJECT_ROOT" "$1" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
target = sys.argv[2]
path = Path(target)
if path.is_absolute():
    print(path.resolve())
else:
    print((root / target.replace("./", "", 1)).resolve())
PY
}

project_rel_to_abs() {
  resolve_project_path "$1"
}

normalize_project_rel_path() {
  python3 - "$PROJECT_ROOT" "$1" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
target_raw = sys.argv[2]
target = Path(target_raw)

if target.is_absolute():
    resolved = target.resolve()
else:
    resolved = (root / target_raw.replace("./", "", 1)).resolve()

try:
    rel = resolved.relative_to(root)
except ValueError:
    raise SystemExit(1)

print("./" + rel.as_posix())
PY
}

active_cycle_rel_path() {
  local pointer_path
  local value
  pointer_path="$(active_cycle_pointer_path)"
  if [ -f "$pointer_path" ]; then
    value="$(python3 - "$pointer_path" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
for line in path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line:
        print(line)
        break
PY
)"
    if [ -n "${value:-}" ]; then
      printf '%s\n' "$value"
      return 0
    fi
  fi
  printf '%s\n' "./harness/feature_list.json"
}

cycle_definition_file_path() {
  resolve_project_path "$(active_cycle_rel_path)"
}

runtime_state_rel_path_for_cycle_rel() {
  python3 - "$1" <<'PY'
from pathlib import PurePosixPath
import sys

rel = PurePosixPath(sys.argv[1].replace("./", "", 1))
parts = rel.parts
if parts and parts[0] == "harness":
    rel = PurePosixPath(*parts[1:])

print("./harness/state/" + rel.as_posix())
PY
}

runtime_state_file_path_for_cycle_rel() {
  resolve_project_path "$(runtime_state_rel_path_for_cycle_rel "$1")"
}

feature_file_path() {
  runtime_state_file_path_for_cycle_rel "$(active_cycle_rel_path)"
}

progress_file_path() {
  printf '%s\n' "${HARNESS_ROOT}/progress.md"
}

decision_log_file_path() {
  printf '%s\n' "${HARNESS_ROOT}/decision-log.md"
}

validate_cycle_definition_file_schema() {
  python3 - "$1" <<'PY'
import json
import sys
from pathlib import Path


path = Path(sys.argv[1])


def fail(message: str) -> None:
    print(f"Invalid cycle definition schema: {path}: {message}", file=sys.stderr)
    raise SystemExit(1)


try:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
except FileNotFoundError:
    fail("file does not exist")
except json.JSONDecodeError as exc:
    fail(f"invalid JSON ({exc.msg} at line {exc.lineno} column {exc.colno})")

if not isinstance(payload, dict):
    fail("top-level JSON must be an object")

required_top_level = {
    "schema_version": str,
    "project_goal": str,
    "cycle_type": str,
    "cycle_profile": str,
}

for key, expected_type in required_top_level.items():
    value = payload.get(key)
    if not isinstance(value, expected_type) or not value.strip():
        fail(f"missing or invalid top-level field: {key}")

cycle_type = payload.get("cycle_type")
if cycle_type not in {"bootstrap", "official"}:
    fail(f"cycle_type must be bootstrap or official, got {cycle_type!r}")

features = payload.get("features")
if not isinstance(features, list):
    fail("features must be a JSON array")

seen_ids = set()

for index, feature in enumerate(features):
    if not isinstance(feature, dict):
        fail(f"feature[{index}] must be an object")

    for key in ["id", "priority", "category", "title", "description"]:
        value = feature.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(f"feature[{index}] missing or invalid field: {key}")

    feature_id = feature["id"]
    if feature_id in seen_ids:
        fail(f"duplicate feature id: {feature_id}")
    seen_ids.add(feature_id)

    for key in ["source_refs", "acceptance_criteria", "dependencies"]:
        value = feature.get(key)
        if not isinstance(value, list):
            fail(f"feature[{index}] field {key} must be a list")
        if not all(isinstance(item, str) and item.strip() for item in value):
            fail(f"feature[{index}] field {key} must contain non-empty strings")

    verification = feature.get("verification")
    if not isinstance(verification, dict):
        fail(f"feature[{index}] verification must be an object")
    for key in ["mode", "target"]:
        value = verification.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(f"feature[{index}] verification.{key} is required")

    for forbidden_key in ["status", "passes", "evidence", "last_verified_at"]:
        if forbidden_key in feature:
            fail(f"feature[{index}] must not include runtime field: {forbidden_key}")
PY
}

validate_runtime_cycle_file_schema() {
  python3 - "$1" <<'PY'
import json
import sys
from pathlib import Path


path = Path(sys.argv[1])


def fail(message: str) -> None:
    print(f"Invalid runtime cycle state schema: {path}: {message}", file=sys.stderr)
    raise SystemExit(1)


try:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
except FileNotFoundError:
    fail("file does not exist")
except json.JSONDecodeError as exc:
    fail(f"invalid JSON ({exc.msg} at line {exc.lineno} column {exc.colno})")

if not isinstance(payload, dict):
    fail("top-level JSON must be an object")

required_top_level = {
    "schema_version": str,
    "project_goal": str,
    "cycle_type": str,
    "cycle_profile": str,
}

for key, expected_type in required_top_level.items():
    value = payload.get(key)
    if not isinstance(value, expected_type) or not value.strip():
        fail(f"missing or invalid top-level field: {key}")

features = payload.get("features")
if not isinstance(features, list):
    fail("features must be a JSON array")

seen_ids = set()
allowed_statuses = {"pending", "in_progress", "blocked", "completed"}

for index, feature in enumerate(features):
    if not isinstance(feature, dict):
        fail(f"feature[{index}] must be an object")

    for key in ["id", "priority", "category", "title", "description", "status"]:
        value = feature.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(f"feature[{index}] missing or invalid field: {key}")

    feature_id = feature["id"]
    if feature_id in seen_ids:
        fail(f"duplicate feature id: {feature_id}")
    seen_ids.add(feature_id)

    if feature["status"] not in allowed_statuses:
        fail(f"feature[{index}] has invalid status: {feature['status']}")

    for key in ["source_refs", "acceptance_criteria", "dependencies"]:
        value = feature.get(key)
        if not isinstance(value, list):
            fail(f"feature[{index}] field {key} must be a list")
        if not all(isinstance(item, str) and item.strip() for item in value):
            fail(f"feature[{index}] field {key} must contain non-empty strings")

    verification = feature.get("verification")
    if not isinstance(verification, dict):
        fail(f"feature[{index}] verification must be an object")
    for key in ["mode", "target"]:
        value = verification.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(f"feature[{index}] verification.{key} is required")

    passes = feature.get("passes")
    if not isinstance(passes, bool):
        fail(f"feature[{index}] passes must be a boolean")

    evidence = feature.get("evidence")
    if not isinstance(evidence, dict):
        fail(f"feature[{index}] evidence must be an object")
    for key in ["summary", "artifacts_dir"]:
        value = evidence.get(key)
        if value is not None and not isinstance(value, str):
            fail(f"feature[{index}] evidence.{key} must be a string or null")

    last_verified_at = feature.get("last_verified_at")
    if last_verified_at is not None and not isinstance(last_verified_at, str):
        fail(f"feature[{index}] last_verified_at must be a string or null")
PY
}

sync_runtime_state_for_cycle_rel() {
  local normalized_rel
  local definition_abs
  local state_abs

  normalized_rel="$(normalize_project_rel_path "$1")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$1" >&2
    return 12
  }

  definition_abs="$(resolve_project_path "$normalized_rel")"
  state_abs="$(runtime_state_file_path_for_cycle_rel "$normalized_rel")"

  mkdir -p "$(dirname "$state_abs")"

  python3 - "$definition_abs" "$state_abs" <<'PY'
import copy
import json
import os
import sys
import tempfile
from pathlib import Path


definition_path = Path(sys.argv[1])
state_path = Path(sys.argv[2])

with definition_path.open("r", encoding="utf-8") as handle:
    definition_payload = json.load(handle)

existing_payload = None
if state_path.exists():
    with state_path.open("r", encoding="utf-8") as handle:
        existing_payload = json.load(handle)

existing_by_id = {}
if isinstance(existing_payload, dict):
    for feature in existing_payload.get("features", []):
        feature_id = feature.get("id")
        if feature_id:
            existing_by_id[feature_id] = feature

payload = copy.deepcopy(definition_payload)
features = []

for feature in definition_payload.get("features", []):
    state_feature = existing_by_id.get(feature.get("id"), {})
    merged_feature = copy.deepcopy(feature)

    status = state_feature.get("status")
    if status not in {"pending", "in_progress", "blocked", "completed"}:
        status = "pending"

    passes = state_feature.get("passes")
    if not isinstance(passes, bool):
        passes = False

    evidence = state_feature.get("evidence")
    if not isinstance(evidence, dict):
        evidence = {}

    summary = evidence.get("summary")
    if summary is not None and not isinstance(summary, str):
        summary = None

    artifacts_dir = evidence.get("artifacts_dir")
    if artifacts_dir is not None and not isinstance(artifacts_dir, str):
        artifacts_dir = None

    last_verified_at = state_feature.get("last_verified_at")
    if last_verified_at is not None and not isinstance(last_verified_at, str):
        last_verified_at = None

    merged_feature["status"] = status
    merged_feature["passes"] = passes
    merged_feature["evidence"] = {
        "summary": summary,
        "artifacts_dir": artifacts_dir,
    }
    merged_feature["last_verified_at"] = last_verified_at
    features.append(merged_feature)

payload["features"] = features
content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
tmp_fd, tmp_name = tempfile.mkstemp(prefix=state_path.name + ".", suffix=".tmp", dir=str(state_path.parent))
try:
    with os.fdopen(tmp_fd, "w", encoding="utf-8") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_name, state_path)
finally:
    tmp_path = Path(tmp_name)
    if tmp_path.exists():
        tmp_path.unlink()
PY

  printf '%s\n' "$state_abs"
}

git_branch_or_none() {
  if git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$PROJECT_ROOT" branch --show-current 2>/dev/null || printf 'unknown\n'
  else
    printf 'not-a-git-repo\n'
  fi
}

git_head_or_none() {
  if git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if git -C "$PROJECT_ROOT" rev-parse --verify HEAD >/dev/null 2>&1; then
      git -C "$PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || printf 'unknown\n'
    else
      printf 'unborn-head\n'
    fi
  else
    printf 'not-a-git-repo\n'
  fi
}

print_section() {
  printf '\n== %s ==\n' "$1"
}

load_harness_config

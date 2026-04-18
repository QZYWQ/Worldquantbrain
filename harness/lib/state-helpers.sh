#!/usr/bin/env bash

activate_cycle_path() {
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$1")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$1" >&2
    return 12
  }
  validate_cycle_definition_file_schema "$(resolve_project_path "$normalized_rel")" || return 12
  sync_runtime_state_for_cycle_rel "$normalized_rel" >/dev/null || return 12
  printf '%s\n' "$normalized_rel" >"$(active_cycle_pointer_path)"
}

create_cycle_from_active() {
  local cycle_id="$1"
  local destination_rel="./harness/cycles/${cycle_id}.json"
  local destination_abs
  destination_abs="$(resolve_project_path "$destination_rel")"

  [ ! -e "$destination_abs" ] || {
    printf 'Cycle already exists: %s\n' "$destination_rel" >&2
    return 12
  }

  python3 - "$(cycle_template_file_path)" "$destination_abs" <<'PY'
import json
import sys
from datetime import datetime

source_path = sys.argv[1]
destination_path = sys.argv[2]

with open(source_path, "r", encoding="utf-8") as handle:
    payload = json.load(handle)

payload["generated_at"] = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

with open(destination_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

  printf '%s\n' "$destination_rel"
}

archive_cycle_path() {
  local cycle_path="$1"
  local normalized_rel
  local source_abs
  local state_source_abs
  local target_rel
  local target_abs
  local state_target_abs

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  [ "$normalized_rel" != "./harness/feature_list.json" ] || {
    printf 'Bootstrap cycle cannot be archived: %s\n' "$normalized_rel" >&2
    return 12
  }

  source_abs="$(resolve_project_path "$normalized_rel")"
  state_source_abs="$(runtime_state_file_path_for_cycle_rel "$normalized_rel")"
  [ -f "$source_abs" ] || {
    printf 'Cycle file does not exist: %s\n' "$normalized_rel" >&2
    return 12
  }

  cycle_can_archive "$normalized_rel" || {
    printf 'Cannot archive a cycle with in_progress features: %s\n' "$normalized_rel" >&2
    return 12
  }

  target_rel="$(cycle_archive_path "$normalized_rel")"
  target_abs="$(resolve_project_path "$target_rel")"
  state_target_abs="$(runtime_state_file_path_for_cycle_rel "$target_rel")"
  [ ! -e "$target_abs" ] || {
    printf 'Archive target already exists: %s\n' "$target_rel" >&2
    return 12
  }

  mv "$source_abs" "$target_abs"
  if [ -f "$state_source_abs" ]; then
    mkdir -p "$(dirname "$state_target_abs")"
    mv "$state_source_abs" "$state_target_abs"
  fi

  if [ "$(active_cycle_rel_path)" = "$normalized_rel" ]; then
    printf '%s\n' "./harness/feature_list.json" >"$(active_cycle_pointer_path)"
  fi

  printf '%s\n' "$target_rel"
}

set_feature_state() {
  python3 - "$(feature_file_path)" "$1" "$2" "$3" "$4" "$5" <<'PY'
import json
import sys
from datetime import datetime

path, feature_id, status, passes_raw, summary, artifacts_dir = sys.argv[1:7]
passes = True if passes_raw == "true" else False
now = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

with open(path, "r", encoding="utf-8") as handle:
    payload = json.load(handle)

for feature in payload.get("features", []):
    if feature.get("id") != feature_id:
        continue
    feature["status"] = status
    feature["passes"] = passes
    if summary:
        feature.setdefault("evidence", {})["summary"] = summary
    if artifacts_dir:
        feature.setdefault("evidence", {})["artifacts_dir"] = artifacts_dir
    feature["last_verified_at"] = now if status == "completed" else feature.get("last_verified_at")
    break

with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY
}

update_progress_start() {
  python3 - "$(progress_file_path)" "$1" "$(git_branch_or_none)" "$(git_head_or_none)" <<'PY'
from pathlib import Path
import re
import sys
from datetime import datetime

path = Path(sys.argv[1])
feature_id = sys.argv[2]
branch = sys.argv[3]
head = sys.argv[4]
now = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

text = path.read_text(encoding="utf-8")
match = re.search(r"current_session:\s*(\d+)", text)
current_session = int(match.group(1)) if match else 0
next_session = current_session + 1

content = f"""---
last_updated: {now}
current_session: {next_session}
active_feature: {feature_id}
active_status: in_progress
current_branch: {branch}
current_head: {head}
last_verified_feature: null
last_verified_at: null
---

# Harness Progress

## Current Status

- Active feature: {feature_id}
- Session status: in_progress
- Branch: {branch}
- Head: {head}

## Recent Activity

- Started session {next_session} on {feature_id}.

## Resume Checklist

- Finish the current feature or explicitly block it.
- Leave evidence and a concise summary before ending the session.

## Notes

- One feature per session.
"""

path.write_text(content, encoding="utf-8")
PY
}

update_progress_finish() {
  python3 - "$(progress_file_path)" "$1" "$2" "$3" "$(git_branch_or_none)" "$(git_head_or_none)" <<'PY'
from pathlib import Path
import re
import sys
from datetime import datetime

path = Path(sys.argv[1])
feature_id = sys.argv[2]
status = sys.argv[3]
summary = sys.argv[4]
branch = sys.argv[5]
head = sys.argv[6]
now = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

text = path.read_text(encoding="utf-8")
match = re.search(r"current_session:\s*(\d+)", text)
current_session = int(match.group(1)) if match else 0

last_verified_feature = feature_id if status == "completed" else "null"
last_verified_at = now if status == "completed" else "null"

content = f"""---
last_updated: {now}
current_session: {current_session}
active_feature: null
active_status: idle
current_branch: {branch}
current_head: {head}
last_verified_feature: {last_verified_feature}
last_verified_at: {last_verified_at}
---

# Harness Progress

## Current Status

- No active feature.
- Last session outcome: {feature_id} -> {status}
- Branch: {branch}
- Head: {head}

## Recent Activity

- {feature_id} marked as {status}.
- Summary: {summary}

## Resume Checklist

- Run `./harness/coding-session.sh next` to see the next actionable feature.
- Start the next session only after reading the latest decision log if the task shape changed.

## Notes

- Evidence-first completion remains required.
"""

path.write_text(content, encoding="utf-8")
PY
}

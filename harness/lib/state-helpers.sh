#!/usr/bin/env bash

render_progress_markdown() {
  local mode="$1"
  local feature_id="$2"
  local status="${3:-}"
  local summary="${4:-}"
  local branch="${5:-}"
  local head="${6:-}"

  python3 - "$(progress_file_path)" "$mode" "$feature_id" "$status" "$summary" "$branch" "$head" <<'PY'
from collections import OrderedDict
from pathlib import Path
import json
import re
import sys
from datetime import datetime

path = Path(sys.argv[1])
mode = sys.argv[2]
feature_id = sys.argv[3]
status = sys.argv[4]
summary = sys.argv[5]
branch = sys.argv[6]
head = sys.argv[7]
now = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

known_order = [
    "last_updated",
    "current_session",
    "active_feature",
    "active_status",
    "current_branch",
    "current_head",
    "last_verified_feature",
    "last_verified_at",
]


def parse_scalar(raw: str):
    if raw == "null":
        return None
    if raw == "true":
        return True
    if raw == "false":
        return False
    if re.fullmatch(r"-?\d+", raw):
        try:
            return int(raw)
        except ValueError:
            return raw
    if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)", raw):
        try:
            return float(raw)
        except ValueError:
            return raw
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    return raw


def render_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return format(value, "g")
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    text = str(value)
    if re.fullmatch(r"[A-Za-z0-9_./:+-]+", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return OrderedDict(), text
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return OrderedDict(), text
    closing_idx = None
    for idx, line in enumerate(lines[1:], 1):
        if line == "---":
            closing_idx = idx
            break
    if closing_idx is None:
        return OrderedDict(), text

    frontmatter = OrderedDict()
    for raw_line in lines[1:closing_idx]:
        if not raw_line or raw_line.lstrip().startswith("#") or ":" not in raw_line:
            continue
        key, raw_value = raw_line.split(":", 1)
        frontmatter[key.strip()] = parse_scalar(raw_value.strip())

    body = "\n".join(lines[closing_idx + 1 :])
    if text.endswith("\n") and body:
        body += "\n"
    return frontmatter, body


def render_body_start():
    return f"""# Harness Progress

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


def render_body_finish():
    summary_line = f"- Summary: {summary}" if summary else "- Summary: (none)"
    return f"""# Harness Progress

## Current Status

- No active feature.
- Last session outcome: {feature_id} -> {status}
- Branch: {branch}
- Head: {head}

## Recent Activity

- {feature_id} marked as {status}.
{summary_line}

## Resume Checklist

- Run `./harness/coding-session.sh next` to see the next actionable feature.
- Start the next session only after reading the latest decision log if the task shape changed.

## Notes

- Evidence-first completion remains required.
"""


existing_text = path.read_text(encoding="utf-8") if path.exists() else ""
frontmatter, _ = parse_frontmatter(existing_text)
current_session_raw = frontmatter.get("current_session", 0)
try:
    current_session = int(current_session_raw)
except (TypeError, ValueError):
    current_session = 0

if mode == "start":
    next_session = current_session + 1
    updates = {
        "last_updated": now,
        "current_session": next_session,
        "active_feature": feature_id,
        "active_status": "in_progress",
        "current_branch": branch,
        "current_head": head,
        "last_verified_feature": None,
        "last_verified_at": None,
    }
elif mode == "finish":
    updates = {
        "last_updated": now,
        "current_session": current_session,
        "active_feature": None,
        "active_status": "idle",
        "current_branch": branch,
        "current_head": head,
        "last_verified_feature": feature_id if status == "completed" else None,
        "last_verified_at": now if status == "completed" else None,
    }
else:
    raise SystemExit(f"Unknown progress render mode: {mode}")

for key in known_order:
    frontmatter[key] = updates[key]

known_set = set(known_order)
ordered_pairs = [(key, value) for key, value in frontmatter.items() if key not in known_set]

lines = ["---"]
for key in known_order:
    lines.append(f"{key}: {render_scalar(frontmatter[key])}")
for key, value in ordered_pairs:
    lines.append(f"{key}: {render_scalar(value)}")
lines.append("---")
lines.append("")
lines.append(render_body_start() if mode == "start" else render_body_finish())
lines.append("")

path.write_text("\n".join(lines), encoding="utf-8")
PY
}

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
  render_progress_markdown "start" "$1" "" "" "$(git_branch_or_none)" "$(git_head_or_none)"
}

update_progress_finish() {
  render_progress_markdown "finish" "$1" "$2" "$3" "$(git_branch_or_none)" "$(git_head_or_none)"
}

# Helper for future renderers: compute family state from the ledger and the
# protocol so stop eligibility is derived from protocol truth, not progress.md.
family_incubation_snapshot() {
  local family_key="${1:-}"
  [ -n "$family_key" ] || {
    printf 'A family key is required.\n' >&2
    return 2
  }

  python3 - "$(resolve_project_path './harness/incubation-protocol.json')" "$(resolve_project_path './runs/research-contracts/family-budget-ledger.json')" "$family_key" <<'PY'
from pathlib import Path
import json
import sys

protocol_path = Path(sys.argv[1])
ledger_path = Path(sys.argv[2])
family_key = sys.argv[3]

with protocol_path.open("r", encoding="utf-8") as handle:
    protocol = json.load(handle)

with ledger_path.open("r", encoding="utf-8") as handle:
    ledger = json.load(handle)

row = next((entry for entry in ledger.get("entries", []) if entry.get("family_key") == family_key), None)
if row is None:
    raise SystemExit(f"Unknown family key: {family_key}")

min_depth_completed = bool(row.get("min_depth_completed"))
snapshot = {
    "family_key": family_key,
    "protocol_version": protocol.get("protocol_version"),
    "registry_state": row.get("registry_state"),
    "incubation_stage": row.get("incubation_stage"),
    "screen_result": row.get("screen_result"),
    "min_depth_completed": min_depth_completed,
    "stop_eligible": min_depth_completed,
    "stage_budget": row.get("stage_budget", {}),
    "release_policy_ref": row.get("reclaim", {}).get("release_policy_ref"),
}
print(json.dumps(snapshot, ensure_ascii=False))
PY
}

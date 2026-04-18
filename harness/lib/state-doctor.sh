#!/usr/bin/env bash

state_doctor_report() {
  python3 - "$(feature_file_path)" "$(progress_file_path)" <<'PY'
import json
import sys
from pathlib import Path


def parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    result = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


feature_path = Path(sys.argv[1])
progress_path = Path(sys.argv[2])

with feature_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

frontmatter = parse_frontmatter(progress_path)
progress_active_feature = frontmatter.get("active_feature", "null")
progress_active_status = frontmatter.get("active_status", "idle")

in_progress_ids = [feature.get("id", "") for feature in payload.get("features", []) if feature.get("status") == "in_progress"]
issues = []

if progress_active_status == "idle" and progress_active_feature != "null":
    issues.append(f"progress.md says idle but active_feature is {progress_active_feature}")

if progress_active_status == "in_progress" and progress_active_feature == "null":
    issues.append("progress.md says in_progress but active_feature is null")

if progress_active_status == "idle" and in_progress_ids:
    issues.append(f"active cycle has in_progress features while progress.md is idle: {', '.join(in_progress_ids)}")

if progress_active_status == "in_progress":
    if len(in_progress_ids) != 1:
        issues.append(f"expected exactly one in_progress feature in active cycle, found {len(in_progress_ids)}")
    elif in_progress_ids[0] != progress_active_feature:
        issues.append(
            "progress.md active_feature does not match active cycle in_progress feature: "
            f"{progress_active_feature} vs {in_progress_ids[0]}"
        )

if issues:
    print("State drift detected:")
    for issue in issues:
        print(f"- {issue}")
    raise SystemExit(1)

print("State is consistent.")
PY
}

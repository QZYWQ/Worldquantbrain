#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-smoke.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

assert_eq() {
  local expected="$1"
  local actual="$2"
  local message="$3"
  if [ "$expected" != "$actual" ]; then
    printf 'ASSERT_EQ failed: %s\nexpected: %s\nactual: %s\n' "$message" "$expected" "$actual" >&2
    exit 1
  fi
}

assert_matches() {
  local value="$1"
  local pattern="$2"
  local message="$3"
  if ! printf '%s\n' "$value" | grep -Eq "$pattern"; then
    printf 'ASSERT_MATCHES failed: %s\npattern: %s\nvalue: %s\n' "$message" "$pattern" "$value" >&2
    exit 1
  fi
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

assert_command_fails() {
  if "$@"; then
    printf 'Expected command to fail but it succeeded: %s\n' "$*" >&2
    exit 1
  fi
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

./harness/coding-session.sh cycle-switch ./harness/cycles/official-alpha-cycle-01.json >/dev/null

python3 - <<'PY'
import json
import re
from pathlib import Path

root = Path.cwd()
active_cycle_rel = (root / "harness" / "active-cycle.txt").read_text(encoding="utf-8").strip().removeprefix("./")
state_path = root / "harness" / "state" / active_cycle_rel.removeprefix("harness/")
with state_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

for feature in payload["features"]:
    feature["status"] = "pending"
    feature["passes"] = False
    feature["evidence"] = {}
    feature["last_verified_at"] = None

with state_path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")

progress_path = root / "harness" / "progress.md"
text = progress_path.read_text(encoding="utf-8")
replacements = {
    r"current_session:\s*\d+": "current_session: 0",
    r"active_feature:\s*.+": "active_feature: null",
    r"active_status:\s*.+": "active_status: idle",
    r"last_verified_feature:\s*.+": "last_verified_feature: null",
    r"last_verified_at:\s*.+": "last_verified_at: null",
    r"- Active feature: .+": "- Active feature: null",
    r"- Session status: .+": "- Session status: idle",
}
for pattern, replacement in replacements.items():
    text = re.sub(pattern, replacement, text)
progress_path.write_text(text, encoding="utf-8")
PY

next_id="$(./harness/coding-session.sh next)"
assert_eq "ALPHA-QUEUE-001" "$next_id" "next should return the first actionable feature"

summary_output="$(./harness/coding-session.sh cycle-summary)"
assert_output_contains "Next actionable feature: ALPHA-QUEUE-001" "$summary_output"

resume_output="$(./harness/coding-session.sh resume-brief)"
resume_rel_path="$(printf '%s\n' "$resume_output" | tail -n 1)"
resume_path="$PROJECT_COPY/${resume_rel_path#./}"
assert_file_contains "ALPHA-QUEUE-001" "$resume_path"

mkdir -p ./runs/session-briefs
session_output="$(./harness/coding-session.sh session-open)"
session_rel_path="$(printf '%s\n' "$session_output" | tail -n 1)"
session_path="$PROJECT_COPY/${session_rel_path#./}"
assert_file_contains "ALPHA-QUEUE-001" "$session_path"

assert_command_fails ./harness/coding-session.sh start ALPHA-FIELD-001 >/dev/null 2>&1

./harness/coding-session.sh start ALPHA-QUEUE-001 >/dev/null

python3 - <<'PY' >"$TMP_ROOT/start-state.json"
import json
from pathlib import Path

root = Path.cwd()
active_cycle_rel = (root / "harness" / "active-cycle.txt").read_text(encoding="utf-8").strip().removeprefix("./")
state_path = root / "harness" / "state" / active_cycle_rel.removeprefix("harness/")
with state_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

queue = next(feature for feature in payload["features"] if feature["id"] == "ALPHA-QUEUE-001")
print(json.dumps(
    {
        "status": queue["status"],
        "passes": queue["passes"],
        "progress": (root / "harness" / "progress.md").read_text(encoding="utf-8"),
    },
    ensure_ascii=False,
))
PY

start_status="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["status"])' "$TMP_ROOT/start-state.json")"
assert_eq "in_progress" "$start_status" "started feature should be marked in_progress"

progress_text="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["progress"])' "$TMP_ROOT/start-state.json")"
assert_matches "$progress_text" 'last_updated: .*[+-][0-9]{4}' "progress timestamp should include timezone offset"
assert_matches "$progress_text" 'active_feature: ALPHA-QUEUE-001' "progress should record the active feature"

assert_command_fails ./harness/coding-session.sh start ALPHA-EXPR-001 >/dev/null 2>&1

mkdir -p ./runs/research-queues
python3 - <<'PY'
import json
from pathlib import Path

path = Path("runs/research-queues/official-alpha-cycle-01.json")
payload = {
    "items": [
        {
            "name": "estimate-drift-family",
            "idea_strength": 3,
            "dataset_freshness": 2,
            "correlation_novelty": 2,
            "metric_headroom": 2,
            "execution_simplicity": 1,
            "current_status": "new_direction",
            "notes": "Analyst estimate drift with low-complexity baseline.",
            "next_step": "Simulate the baseline estimate drift ranking signal.",
        },
        {
            "name": "event-lag-family",
            "idea_strength": 2,
            "dataset_freshness": 2,
            "correlation_novelty": 3,
            "metric_headroom": 1,
            "execution_simplicity": 0,
            "current_status": "new_direction",
            "notes": "Event reaction lag direction for a second queue branch.",
            "next_step": "Search for event lag fields and build one baseline.",
        },
    ]
}
path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
./harness/coding-session.sh finish ALPHA-QUEUE-001 --summary "harness smoke test completion" >/dev/null

python3 - <<'PY' >"$TMP_ROOT/finish-state.json"
import json
from pathlib import Path

root = Path.cwd()
active_cycle_rel = (root / "harness" / "active-cycle.txt").read_text(encoding="utf-8").strip().removeprefix("./")
state_path = root / "harness" / "state" / active_cycle_rel.removeprefix("harness/")
with state_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

queue = next(feature for feature in payload["features"] if feature["id"] == "ALPHA-QUEUE-001")
print(json.dumps(
    {
        "status": queue["status"],
        "passes": queue["passes"],
        "last_verified_at": queue["last_verified_at"],
        "progress": (root / "harness" / "progress.md").read_text(encoding="utf-8"),
    },
    ensure_ascii=False,
))
PY

finish_status="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["status"])' "$TMP_ROOT/finish-state.json")"
assert_eq "completed" "$finish_status" "finished feature should be marked completed"

finish_passes="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["passes"])' "$TMP_ROOT/finish-state.json")"
assert_eq "True" "$finish_passes" "finished feature should be marked as passing verification"

finish_last_verified_at="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["last_verified_at"])' "$TMP_ROOT/finish-state.json")"
assert_matches "$finish_last_verified_at" '.*[+-][0-9]{4}$' "feature last_verified_at should include timezone offset"

finish_progress="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["progress"])' "$TMP_ROOT/finish-state.json")"
assert_matches "$finish_progress" 'active_status: idle' "progress should return to idle after finish"
assert_matches "$finish_progress" 'last_verified_feature: ALPHA-QUEUE-001' "progress should record the last verified feature"

next_after_finish="$(./harness/coding-session.sh next)"
assert_eq "ALPHA-FIELD-001" "$next_after_finish" "next should advance to the dependent feature after completion"

summary_after_finish="$(./harness/coding-session.sh cycle-summary)"
assert_output_contains "Next actionable feature: ALPHA-FIELD-001" "$summary_after_finish"

resume_after_finish="$(./harness/coding-session.sh resume-brief)"
resume_after_finish_rel_path="$(printf '%s\n' "$resume_after_finish" | tail -n 1)"
resume_after_finish_path="$PROJECT_COPY/${resume_after_finish_rel_path#./}"
assert_file_contains "ALPHA-FIELD-001" "$resume_after_finish_path"

session_after_finish="$(./harness/coding-session.sh session-open)"
session_after_finish_rel_path="$(printf '%s\n' "$session_after_finish" | tail -n 1)"
session_after_finish_path="$PROJECT_COPY/${session_after_finish_rel_path#./}"
assert_file_contains "ALPHA-FIELD-001" "$session_after_finish_path"

printf 'Harness smoke test passed.\n'

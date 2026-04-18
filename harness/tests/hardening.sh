#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-hardening.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

assert_command_fails() {
  if "$@"; then
    printf 'Expected command to fail but it succeeded: %s\n' "$*" >&2
    exit 1
  fi
}

assert_command_succeeds() {
  "$@" >/dev/null
}

assert_output_contains() {
  local needle="$1"
  local haystack="$2"
  if ! printf '%s\n' "$haystack" | grep -Fq "$needle"; then
    printf 'Expected output to contain: %s\nActual output:\n%s\n' "$needle" "$haystack" >&2
    exit 1
  fi
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

cat > ./tmp-bad-cycle.json <<'EOF'
{"hello":"world"}
EOF

set +e
invalid_switch_output="$(./harness/coding-session.sh cycle-switch ./tmp-bad-cycle.json 2>&1)"
invalid_switch_status="$?"
set -e

if [ "$invalid_switch_status" -eq 0 ]; then
  printf 'Expected invalid cycle switch to fail.\n' >&2
  exit 1
fi

assert_output_contains "Invalid cycle definition schema" "$invalid_switch_output"

mkdir -p ./runs/research-queues
cp ./templates/research-queue.template.json ./runs/research-queues/official-alpha-cycle-01.json

assert_command_succeeds ./harness/coding-session.sh start ALPHA-QUEUE-001
assert_command_fails ./harness/coding-session.sh finish ALPHA-QUEUE-001 --summary "raw template must not pass"

python3 - <<'PY'
from pathlib import Path

root = Path.cwd()
field = root / "runs" / "field-search-packs" / "primary-direction-search-pack.md"
field.parent.mkdir(parents=True, exist_ok=True)
field.write_text("# stub\n", encoding="utf-8")
PY

python3 - <<'PY'
import json
from pathlib import Path

root = Path.cwd()
active_cycle_rel = (root / "harness" / "active-cycle.txt").read_text(encoding="utf-8").strip().removeprefix("./")
feature_path = root / "harness" / "state" / active_cycle_rel.removeprefix("harness/")
with feature_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

for feature in payload["features"]:
    if feature["id"] == "ALPHA-QUEUE-001":
        feature["status"] = "completed"
        feature["passes"] = True
    if feature["id"] == "ALPHA-FIELD-001":
        feature["status"] = "in_progress"

with feature_path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

assert_command_fails ./harness/coding-session.sh finish ALPHA-FIELD-001 --summary "stub markdown must not pass"

python3 - <<'PY'
from pathlib import Path

path = Path("harness/progress.md")
text = path.read_text(encoding="utf-8")
text = text.replace("active_feature: null", "active_feature: ALPHA-QUEUE-001")
text = text.replace("active_status: idle", "active_status: in_progress")
path.write_text(text, encoding="utf-8")
PY

set +e
doctor_output="$(./harness/coding-session.sh doctor 2>&1)"
doctor_status="$?"
set -e

if [ "$doctor_status" -eq 0 ]; then
  printf 'Expected doctor to fail when state drift exists.\n' >&2
  exit 1
fi

assert_output_contains "State drift detected" "$doctor_output"

printf './tmp-bad-cycle.json\n' > ./harness/active-cycle.txt

set +e
invalid_summary_output="$(./harness/coding-session.sh cycle-summary 2>&1)"
invalid_summary_status="$?"
set -e

if [ "$invalid_summary_status" -eq 0 ]; then
  printf 'Expected cycle-summary to fail for invalid active cycle schema.\n' >&2
  exit 1
fi

assert_output_contains "Invalid cycle definition schema" "$invalid_summary_output"

printf 'Harness hardening test passed.\n'

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-cycle-config.XXXXXX")"

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

assert_output_contains() {
  local needle="$1"
  local haystack="$2"
  if ! printf '%s\n' "$haystack" | grep -Fq "$needle"; then
    printf 'Expected output to contain: %s\nActual output:\n%s\n' "$needle" "$haystack" >&2
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

cat > ./harness/config.env <<EOF
EXTERNAL_KB_ROOT="$TMP_ROOT/missing-kb"
EOF

assert_command_fails ./harness/init.sh >/dev/null 2>&1

mkdir -p "$TMP_ROOT/custom-kb"
cat > ./harness/config.env <<EOF
EXTERNAL_KB_ROOT="$TMP_ROOT/custom-kb"
EOF

./harness/init.sh >/dev/null

current_cycle="$(./harness/coding-session.sh cycle-current)"
assert_eq "./harness/cycles/official-alpha-cycle-01.json" "$current_cycle" "default active cycle should be the seeded official cycle"

./harness/coding-session.sh cycle-create official-alpha-cycle-02 >/dev/null

new_cycle="$(./harness/coding-session.sh cycle-current)"
assert_eq "./harness/cycles/official-alpha-cycle-02.json" "$new_cycle" "cycle-create should activate the new cycle"

python3 - <<'PY'
import json
from pathlib import Path

path = Path("harness/cycles/official-alpha-cycle-02.json")
state_path = Path("harness/state/cycles/official-alpha-cycle-02.json")
with state_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

for feature in payload["features"]:
    if feature["id"] == "ALPHA-QUEUE-001":
        feature["status"] = "completed"
        feature["passes"] = True

with state_path.open("w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY

next_in_new_cycle="$(./harness/coding-session.sh next)"
assert_eq "ALPHA-FIELD-001" "$next_in_new_cycle" "switched cycle should change the next actionable feature"

./harness/coding-session.sh cycle-switch ./harness/feature_list.json >/dev/null

next_in_original_cycle="$(./harness/coding-session.sh next)"
assert_eq "ALPHA-QUEUE-001" "$next_in_original_cycle" "switching back should restore the original active cycle"

./harness/coding-session.sh cycle-switch ./harness/cycles/official-alpha-cycle-01.json >/dev/null

cat > ./harness/config.env <<EOF
EXTERNAL_KB_ROOT="$TMP_ROOT/missing-kb"
WQB_SCRIPT_ROOT="$TMP_ROOT/missing-scripts"
EOF

summary_output="$(./harness/coding-session.sh cycle-summary)"
assert_output_contains "Cycle type: official" "$summary_output"
assert_output_contains "Next actionable feature: ALPHA-QUEUE-001" "$summary_output"

rm ./harness/active-cycle.txt

fallback_cycle="$(./harness/coding-session.sh cycle-current)"
assert_eq "./harness/feature_list.json" "$fallback_cycle" "missing active-cycle pointer should fall back to bootstrap cycle"

fallback_summary="$(./harness/coding-session.sh cycle-summary)"
assert_output_contains "Active cycle: ./harness/feature_list.json" "$fallback_summary"
assert_output_contains "Warning: active cycle is bootstrap fallback state." "$fallback_summary"

printf 'Harness cycle and config test passed.\n'

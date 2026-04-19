#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-official-cycle-default.XXXXXX")"

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
  if ! printf '%s\n' "$haystack" | grep -Fq -- "$needle"; then
    printf 'Expected output to contain: %s\nActual output:\n%s\n' "$needle" "$haystack" >&2
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

status_output="$(./harness/coding-session.sh status)"
active_feature="$(printf '%s\n' "$status_output" | awk -F': ' '/active_feature:/ {print $2}')"
active_status="$(printf '%s\n' "$status_output" | awk -F': ' '/active_status:/ {print $2}')"
if [ "$active_status" = "in_progress" ] && [ -n "$active_feature" ] && [ "$active_feature" != "null" ]; then
  ./harness/coding-session.sh block "$active_feature" --summary "Reset copied runtime state for official-cycle-default test." >/dev/null
fi

./harness/coding-session.sh cycle-switch ./harness/cycles/official-alpha-cycle-01.json >/dev/null

active_cycle="$(./harness/coding-session.sh cycle-current)"
assert_eq "./harness/cycles/official-alpha-cycle-01.json" "$active_cycle" "default active cycle should point to official cycle"

python3 - <<'PY' >"$TMP_ROOT/cycle-metadata.txt"
import json
from pathlib import Path

bootstrap = Path("harness/feature_list.json")
official = Path("harness/cycles/official-alpha-cycle-01.json")
template = Path("harness/templates/cycle-template.json")

with bootstrap.open("r", encoding="utf-8") as handle:
    bootstrap_payload = json.load(handle)

with official.open("r", encoding="utf-8") as handle:
    official_payload = json.load(handle)

with template.open("r", encoding="utf-8") as handle:
    template_payload = json.load(handle)

print(bootstrap_payload.get("cycle_type"))
print(bootstrap_payload.get("cycle_profile"))
print(official_payload.get("cycle_type"))
print(official_payload.get("cycle_profile"))
print(template_payload.get("cycle_type"))
print(template_payload.get("cycle_profile"))
PY

bootstrap_type="$(sed -n '1p' "$TMP_ROOT/cycle-metadata.txt")"
bootstrap_profile="$(sed -n '2p' "$TMP_ROOT/cycle-metadata.txt")"
official_type="$(sed -n '3p' "$TMP_ROOT/cycle-metadata.txt")"
official_profile="$(sed -n '4p' "$TMP_ROOT/cycle-metadata.txt")"
template_type="$(sed -n '5p' "$TMP_ROOT/cycle-metadata.txt")"
template_profile="$(sed -n '6p' "$TMP_ROOT/cycle-metadata.txt")"

assert_eq "bootstrap" "$bootstrap_type" "bootstrap cycle should declare cycle_type=bootstrap"
assert_eq "fallback" "$bootstrap_profile" "bootstrap cycle should declare cycle_profile=fallback"
assert_eq "official" "$official_type" "official cycle should declare cycle_type=official"
assert_eq "research-first" "$official_profile" "official cycle should declare cycle_profile=research-first"
assert_eq "official" "$template_type" "cycle template should declare cycle_type=official"
assert_eq "research-first" "$template_profile" "cycle template should declare cycle_profile=research-first"

assert_file_not_contains "/Users/zpdedn" "$PROJECT_COPY/harness/cycles/official-alpha-cycle-01.json"
assert_file_not_contains "/Users/zpdedn" "$PROJECT_COPY/harness/config.env.example"
assert_file_not_contains '"/Users/zpdedn' "$PROJECT_COPY/harness/lib/common.sh"

summary_output="$(./harness/coding-session.sh cycle-summary)"
assert_output_contains "Cycle type: official" "$summary_output"
assert_output_contains "Cycle profile: research-first" "$summary_output"

official_report_output="$(./harness/coding-session.sh cycle-report)"
assert_output_contains "./harness/reports/official-alpha-cycle-01-report.md" "$official_report_output"

official_report_path="$PROJECT_COPY/harness/reports/official-alpha-cycle-01-report.md"
official_report_content="$(cat "$official_report_path")"
assert_output_contains "- Cycle type: official" "$official_report_content"
assert_output_contains "- Cycle profile: research-first" "$official_report_content"

./harness/coding-session.sh cycle-switch ./harness/feature_list.json >/dev/null
bootstrap_summary_output="$(./harness/coding-session.sh cycle-summary)"
assert_output_contains "Cycle type: bootstrap" "$bootstrap_summary_output"
assert_output_contains "Cycle profile: fallback" "$bootstrap_summary_output"
assert_output_contains "Warning: active cycle is bootstrap fallback state." "$bootstrap_summary_output"

bootstrap_report_output="$(./harness/coding-session.sh cycle-report ./harness/feature_list.json)"
assert_output_contains "./harness/reports/feature_list-report.md" "$bootstrap_report_output"

bootstrap_report_path="$PROJECT_COPY/harness/reports/feature_list-report.md"
bootstrap_report_content="$(cat "$bootstrap_report_path")"
assert_output_contains "- Cycle type: bootstrap" "$bootstrap_report_content"
assert_output_contains "- Cycle profile: fallback" "$bootstrap_report_content"
assert_output_contains "- Note: Report generated from bootstrap fallback state." "$bootstrap_report_content"

printf 'Harness official default cycle test passed.\n'

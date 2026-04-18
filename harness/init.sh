#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/lib/common.sh"
. "${SCRIPT_DIR}/lib/session-lock.sh"
. "${SCRIPT_DIR}/lib/env-preflight.sh"
. "${SCRIPT_DIR}/lib/state-doctor.sh"
. "${SCRIPT_DIR}/lib/reporting.sh"
. "${SCRIPT_DIR}/lib/state-queries.sh"
. "${SCRIPT_DIR}/lib/state-helpers.sh"

cleanup() {
  release_lock
}

trap cleanup EXIT
trap 'trap - EXIT; cleanup; exit 130' INT
trap 'trap - EXIT; cleanup; exit 143' TERM

acquire_lock
run_preflight_environment

doctor_status=0
if doctor_output="$(state_doctor_report 2>&1)"; then
  doctor_status=0
else
  doctor_status=$?
fi

print_section "Harness Roots"
printf 'Project root: %s\n' "$PROJECT_ROOT"
printf 'Harness root: %s\n' "$HARNESS_ROOT"
printf 'External KB: %s\n' "$EXTERNAL_KB_ROOT"
printf 'Script root: %s\n' "$WQB_SCRIPT_ROOT"
printf 'Active cycle: %s\n' "$(active_cycle_rel_path)"

print_section "Git State"
printf 'Branch: %s\n' "$(git_branch_or_none)"
printf 'Head: %s\n' "$(git_head_or_none)"

print_section "Next Actionable Feature"
next_id="$(next_feature_id || true)"
if [ -n "${next_id:-}" ]; then
  print_feature_brief "$next_id"
else
  printf 'No actionable pending feature found.\n'
fi

print_section "Pending Summary"
print_pending_summary

if [ "$doctor_status" -eq 0 ]; then
  print_section "State Doctor"
else
  print_section "State Doctor Warning"
fi
printf '%s\n' "$doctor_output"

print_section "Recommended Next Command"
printf './harness/coding-session.sh start\n'

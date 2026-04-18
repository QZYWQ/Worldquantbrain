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
. "${SCRIPT_DIR}/lib/verify-dispatcher.sh"

cleanup() {
  release_lock
}

usage() {
  cat <<'EOF'
Usage:
  ./harness/coding-session.sh status
  ./harness/coding-session.sh doctor
  ./harness/coding-session.sh next
  ./harness/coding-session.sh cycle-current
  ./harness/coding-session.sh cycle-list
  ./harness/coding-session.sh cycle-summary
  ./harness/coding-session.sh cycle-report [PATH]
  ./harness/coding-session.sh cycle-close [PATH]
  ./harness/coding-session.sh resume-brief [PATH]
  ./harness/coding-session.sh session-open [PATH]
  ./harness/coding-session.sh cycle-switch PATH
  ./harness/coding-session.sh cycle-create CYCLE_ID
  ./harness/coding-session.sh cycle-archive [PATH]
  ./harness/coding-session.sh start [FEATURE_ID]
  ./harness/coding-session.sh finish FEATURE_ID --summary "..." [--artifacts-dir PATH]
  ./harness/coding-session.sh block FEATURE_ID --summary "..."
EOF
}

parse_summary_args() {
  SUMMARY=""
  ARTIFACTS_DIR=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --summary)
        SUMMARY="${2:-}"
        shift 2
        ;;
      --artifacts-dir)
        ARTIFACTS_DIR="${2:-}"
        shift 2
        ;;
      *)
        printf 'Unknown option: %s\n' "$1" >&2
        exit 2
        ;;
    esac
  done
  if [ -z "$SUMMARY" ]; then
    printf 'A --summary value is required.\n' >&2
    exit 2
  fi
}

join_csv_lines() {
  python3 -c 'import sys; print(", ".join([line.strip() for line in sys.stdin if line.strip()]))'
}

show_status() {
  local doctor_output
  run_preflight_base
  print_section "Progress"
  cat "$(progress_file_path)"
  if doctor_output="$(state_doctor_report 2>&1)"; then
    print_section "State Doctor"
    printf '%s\n' "$doctor_output"
  else
    print_section "State Doctor Warning"
    printf '%s\n' "$doctor_output"
  fi
  print_section "Pending Summary"
  print_pending_summary
}

run_doctor() {
  run_preflight_base
  state_doctor_report
}

show_cycle_current() {
  run_preflight_base
  printf '%s\n' "$(active_cycle_rel_path)"
}

show_cycle_list() {
  run_preflight_base
  list_cycle_rel_paths
}

show_cycle_summary() {
  local doctor_output
  run_preflight_base
  cycle_summary_report
  if doctor_output="$(state_doctor_report 2>&1)"; then
    printf 'Doctor: clean\n'
  else
    printf 'Doctor: drift\n'
    printf '%s\n' "$doctor_output"
  fi
}

show_cycle_report() {
  local cycle_path="${1:-}"
  local report_target

  run_preflight_base
  if [ -z "$cycle_path" ]; then
    cycle_path="$(active_cycle_rel_path)"
  fi

  report_target="$(write_cycle_report "$cycle_path")"

  print_section "Cycle Report"
  printf '%s\n' "$report_target"
}

show_resume_brief() {
  local cycle_path="${1:-}"
  local brief_target

  run_preflight_base
  if [ -z "$cycle_path" ]; then
    cycle_path="$(active_cycle_rel_path)"
  fi

  brief_target="$(write_resume_brief "$cycle_path")"

  print_section "Resume Brief"
  printf '%s\n' "$brief_target"
}

show_session_open() {
  local cycle_path="${1:-}"
  local brief_target

  run_preflight_base
  if [ -z "$cycle_path" ]; then
    cycle_path="$(active_cycle_rel_path)"
  fi

  brief_target="$(write_session_open_brief "$cycle_path")"

  print_section "Session Open"
  printf '%s\n' "$brief_target"
}

ensure_cycle_mutation_is_safe() {
  local current_in_progress
  current_in_progress="$(in_progress_feature_ids || true)"
  if [ -n "${current_in_progress:-}" ]; then
    printf 'Cannot change active cycle while features are in progress: %s\n' "$(printf '%s\n' "$current_in_progress" | join_csv_lines)" >&2
    exit 4
  fi
}

switch_cycle() {
  local cycle_path="${1:-}"
  acquire_lock
  trap cleanup EXIT
  trap 'trap - EXIT; cleanup; exit 130' INT
  trap 'trap - EXIT; cleanup; exit 143' TERM

  run_preflight_base
  [ -n "$cycle_path" ] || {
    printf 'A cycle path is required.\n' >&2
    exit 2
  }
  ensure_cycle_mutation_is_safe
  activate_cycle_path "$cycle_path"

  print_section "Active Cycle"
  printf '%s\n' "$(active_cycle_rel_path)"
}

create_cycle() {
  local cycle_id="${1:-}"
  local new_cycle_rel
  acquire_lock
  trap cleanup EXIT
  trap 'trap - EXIT; cleanup; exit 130' INT
  trap 'trap - EXIT; cleanup; exit 143' TERM

  run_preflight_base
  [ -n "$cycle_id" ] || {
    printf 'A cycle id is required.\n' >&2
    exit 2
  }
  ensure_cycle_mutation_is_safe

  new_cycle_rel="$(create_cycle_from_active "$cycle_id")"
  activate_cycle_path "$new_cycle_rel"

  print_section "Created Cycle"
  printf '%s\n' "$new_cycle_rel"
}

archive_cycle() {
  local cycle_path="${1:-}"
  local archive_target
  acquire_lock
  trap cleanup EXIT
  trap 'trap - EXIT; cleanup; exit 130' INT
  trap 'trap - EXIT; cleanup; exit 143' TERM

  run_preflight_base
  if [ -z "$cycle_path" ]; then
    cycle_path="$(active_cycle_rel_path)"
  fi
  ensure_cycle_mutation_is_safe

  archive_target="$(archive_cycle_path "$cycle_path")"

  print_section "Archived Cycle"
  printf '%s\n' "$archive_target"
}

close_cycle() {
  local cycle_path="${1:-}"
  local normalized_rel
  local report_target

  acquire_lock
  trap cleanup EXIT
  trap 'trap - EXIT; cleanup; exit 130' INT
  trap 'trap - EXIT; cleanup; exit 143' TERM

  run_preflight_base
  if [ -z "$cycle_path" ]; then
    cycle_path="$(active_cycle_rel_path)"
  fi

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || exit 12
  cycle_validate_close_readiness "$normalized_rel" || exit 4
  cycle_require_clean_doctor_if_active "$normalized_rel" || exit 4
  report_target="$(write_cycle_report "$normalized_rel")"

  print_section "Cycle Closed"
  printf 'Cycle closed: %s\n' "$normalized_rel"
  printf 'Report: %s\n' "$report_target"
}

show_next() {
  run_preflight_base
  local next_id
  next_id="$(next_feature_id || true)"
  if [ -z "${next_id:-}" ]; then
    printf 'No actionable pending feature found.\n'
    return 0
  fi
  printf '%s\n' "$next_id"
}

start_feature() {
  local feature_id="${1:-}"
  local current_in_progress
  local current_status
  local missing_deps
  acquire_lock
  trap cleanup EXIT
  trap 'trap - EXIT; cleanup; exit 130' INT
  trap 'trap - EXIT; cleanup; exit 143' TERM

  run_preflight_base

  if [ -z "$feature_id" ]; then
    feature_id="$(next_feature_id || true)"
  fi
  if [ -z "${feature_id:-}" ]; then
    printf 'No actionable pending feature found.\n' >&2
    exit 3
  fi
  feature_exists "$feature_id" || {
    printf 'Unknown feature id: %s\n' "$feature_id" >&2
    exit 3
  }
  current_in_progress="$(in_progress_feature_ids || true)"
  if [ -n "${current_in_progress:-}" ]; then
    printf 'Another feature is already in progress: %s\n' "$(printf '%s\n' "$current_in_progress" | join_csv_lines)" >&2
    exit 4
  fi
  current_status="$(feature_status "$feature_id")"
  if [ "$current_status" != "pending" ]; then
    printf 'Feature %s is not startable from status %s.\n' "$feature_id" "$current_status" >&2
    exit 4
  fi
  if ! feature_dependencies_met "$feature_id"; then
    missing_deps="$(feature_missing_dependencies "$feature_id" | join_csv_lines)"
    printf 'Feature %s has unmet dependencies: %s\n' "$feature_id" "$missing_deps" >&2
    exit 4
  fi

  set_feature_state "$feature_id" "in_progress" "false" "" ""
  update_progress_start "$feature_id"

  print_section "Session Start"
  printf 'Started feature: %s\n' "$feature_id"
  print_feature_brief "$feature_id"
}

finish_feature() {
  local feature_id="$1"
  local current_status
  local current_in_progress
  shift
  parse_summary_args "$@"

  acquire_lock
  trap cleanup EXIT
  trap 'trap - EXIT; cleanup; exit 130' INT
  trap 'trap - EXIT; cleanup; exit 143' TERM

  run_preflight_verification
  feature_exists "$feature_id" || {
    printf 'Unknown feature id: %s\n' "$feature_id" >&2
    exit 3
  }
  current_status="$(feature_status "$feature_id")"
  if [ "$current_status" != "in_progress" ]; then
    printf 'Feature %s cannot be finished from status %s.\n' "$feature_id" "$current_status" >&2
    exit 4
  fi
  current_in_progress="$(in_progress_feature_ids || true)"
  if [ -z "${current_in_progress:-}" ] || [ "$current_in_progress" != "$feature_id" ]; then
    printf 'Active in-progress feature does not match %s: %s\n' "$feature_id" "$(printf '%s\n' "$current_in_progress" | join_csv_lines)" >&2
    exit 4
  fi

  if [ -n "$ARTIFACTS_DIR" ]; then
    ARTIFACTS_DIR="$(project_rel_to_abs "${ARTIFACTS_DIR#${PROJECT_ROOT}/}")"
  fi

  verify_feature "$feature_id" "$ARTIFACTS_DIR"
  set_feature_state "$feature_id" "completed" "true" "$SUMMARY" "$ARTIFACTS_DIR"
  update_progress_finish "$feature_id" "completed" "$SUMMARY"

  print_section "Feature Completed"
  printf '%s\n' "$feature_id"
}

block_feature() {
  local feature_id="$1"
  local current_status
  local current_in_progress
  shift
  parse_summary_args "$@"

  acquire_lock
  trap cleanup EXIT
  trap 'trap - EXIT; cleanup; exit 130' INT
  trap 'trap - EXIT; cleanup; exit 143' TERM

  run_preflight_base
  feature_exists "$feature_id" || {
    printf 'Unknown feature id: %s\n' "$feature_id" >&2
    exit 3
  }
  current_status="$(feature_status "$feature_id")"
  if [ "$current_status" != "in_progress" ]; then
    printf 'Feature %s cannot be blocked from status %s.\n' "$feature_id" "$current_status" >&2
    exit 4
  fi
  current_in_progress="$(in_progress_feature_ids || true)"
  if [ -z "${current_in_progress:-}" ] || [ "$current_in_progress" != "$feature_id" ]; then
    printf 'Active in-progress feature does not match %s: %s\n' "$feature_id" "$(printf '%s\n' "$current_in_progress" | join_csv_lines)" >&2
    exit 4
  fi

  set_feature_state "$feature_id" "blocked" "false" "$SUMMARY" ""
  update_progress_finish "$feature_id" "blocked" "$SUMMARY"

  print_section "Feature Blocked"
  printf '%s\n' "$feature_id"
}

main() {
  local command="${1:-status}"
  case "$command" in
    status)
      show_status
      ;;
    doctor)
      run_doctor
      ;;
    next)
      show_next
      ;;
    cycle-current)
      show_cycle_current
      ;;
    cycle-list)
      show_cycle_list
      ;;
    cycle-summary)
      show_cycle_summary
      ;;
    cycle-report)
      shift || true
      show_cycle_report "${1:-}"
      ;;
    cycle-close)
      shift || true
      close_cycle "${1:-}"
      ;;
    resume-brief)
      shift || true
      show_resume_brief "${1:-}"
      ;;
    session-open)
      shift || true
      show_session_open "${1:-}"
      ;;
    cycle-switch)
      shift || true
      switch_cycle "${1:-}"
      ;;
    cycle-create)
      shift || true
      create_cycle "${1:-}"
      ;;
    cycle-archive)
      shift || true
      archive_cycle "${1:-}"
      ;;
    start)
      shift || true
      start_feature "${1:-}"
      ;;
    finish)
      shift
      [ "$#" -ge 1 ] || {
        usage
        exit 2
      }
      local feature_id="$1"
      shift
      finish_feature "$feature_id" "$@"
      ;;
    block)
      shift
      [ "$#" -ge 1 ] || {
        usage
        exit 2
      }
      local feature_id="$1"
      shift
      block_feature "$feature_id" "$@"
      ;;
    *)
      usage
      exit 2
      ;;
  esac
}

main "$@"

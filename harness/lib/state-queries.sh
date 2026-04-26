#!/usr/bin/env bash

state_query_script() {
  printf '%s\n' "${HARNESS_LIB_DIR}/state_query_runner.py"
}

active_cycle_has_in_progress_features() {
  local current_in_progress
  current_in_progress="$(in_progress_feature_ids || true)"
  [ -n "${current_in_progress:-}" ]
}

list_cycle_rel_paths() {
  python3 "$(state_query_script)" list-cycle-rel-paths "$PROJECT_ROOT" "$(active_cycle_rel_path)"
}

cycle_summary_report() {
  python3 "$(state_query_script)" \
    cycle-summary \
    "$(feature_file_path)" \
    "$(active_cycle_rel_path)" \
    "$(progress_file_path)"
}

cycle_validate_close_readiness() {
  local cycle_path="$1"
  local normalized_rel
  local cycle_abs

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  cycle_abs="$(sync_runtime_state_for_cycle_rel "$normalized_rel")"
  [ -f "$cycle_abs" ] || {
    printf 'Cycle file does not exist: %s\n' "$normalized_rel" >&2
    return 12
  }

  python3 "$(state_query_script)" cycle-validate-close-readiness "$cycle_abs" "$normalized_rel"
}

cycle_require_clean_doctor_if_active() {
  local cycle_path="$1"
  local normalized_rel
  local active_cycle
  local doctor_output

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  active_cycle="$(active_cycle_rel_path)"
  if [ "$normalized_rel" != "$active_cycle" ]; then
    return 0
  fi

  if ! doctor_output="$(state_doctor_report 2>&1)"; then
    printf 'Cannot close the active cycle while doctor reports drift: %s\n' "$normalized_rel" >&2
    printf '%s\n' "$doctor_output" >&2
    return 12
  fi
}

cycle_archive_path() {
  local cycle_path="$1"
  local normalized_rel

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(state_query_script)" cycle-archive-path "$normalized_rel"
}

cycle_can_archive() {
  python3 "$(state_query_script)" cycle-can-archive "$(sync_runtime_state_for_cycle_rel "$1")"
}

next_feature_id() {
  python3 "$(state_query_script)" next-feature-id "$(feature_file_path)"
}

feature_exists() {
  python3 "$(state_query_script)" feature-exists "$(feature_file_path)" "$1"
}

feature_status() {
  python3 "$(state_query_script)" feature-status "$(feature_file_path)" "$1"
}

feature_dependencies_met() {
  python3 "$(state_query_script)" feature-dependencies-met "$(feature_file_path)" "$1"
}

feature_missing_dependencies() {
  python3 "$(state_query_script)" feature-missing-dependencies "$(feature_file_path)" "$1"
}

in_progress_feature_ids() {
  python3 "$(state_query_script)" in-progress-feature-ids "$(feature_file_path)"
}

feature_verification_mode() {
  python3 "$(state_query_script)" feature-verification-mode "$(feature_file_path)" "$1"
}

feature_verification_target() {
  python3 "$(state_query_script)" feature-verification-target "$(feature_file_path)" "$1"
}

print_feature_brief() {
  python3 "$(state_query_script)" print-feature-brief "$(feature_file_path)" "$1" "$EXTERNAL_KB_ROOT"
}

print_pending_summary() {
  python3 "$(state_query_script)" print-pending-summary "$(feature_file_path)"
}

incubation_summary_report() {
  python3 "$(state_query_script)" \
    incubation-summary \
    "$(resolve_project_path './runs/research-contracts/family-budget-ledger.json')" \
    "$(progress_file_path)"
}

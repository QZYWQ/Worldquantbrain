#!/usr/bin/env bash

require_file() {
  if [ ! -f "$1" ]; then
    printf 'Missing required file: %s\n' "$1" >&2
    return 10
  fi
}

require_dir() {
  if [ ! -d "$1" ]; then
    printf 'Missing required directory: %s\n' "$1" >&2
    return 10
  fi
}

run_preflight_base() {
  command_exists python3 || {
    printf 'python3 is required.\n' >&2
    return 10
  }

  require_file "${PROJECT_ROOT}/AGENTS.md" || return 10
  require_file "${PROJECT_ROOT}/00-项目总索引.md" || return 10
  require_file "${PROJECT_ROOT}/01-外部知识库映射.md" || return 10
  require_file "${PROJECT_ROOT}/02-工作流索引.md" || return 10
  require_dir "${PROJECT_ROOT}/templates" || return 10
  require_dir "${PROJECT_ROOT}/runs" || return 10
  require_dir "$(session_brief_root_path)" || return 10

  require_file "${HARNESS_ROOT}/AGENTS.md" || return 10
  require_file "$(surface_contract_file_path)" || return 10
  require_file "$(config_example_path)" || return 10
  require_file "$(config_file_path)" || return 10
  require_file "$(cycle_template_file_path)" || return 10
  require_file "$(cycle_definition_file_path)" || return 10
  require_file "$(progress_file_path)" || return 10
  require_file "$(decision_log_file_path)" || return 10
  require_dir "${HARNESS_ROOT}/artifacts" || return 10
  require_dir "$(archive_root_path)" || return 10
  require_dir "$(report_root_path)" || return 10
  require_dir "${HARNESS_ROOT}/cycles" || return 10
  require_dir "${HARNESS_ROOT}/lib" || return 10

  mkdir -p "$(state_root_path)"

  validate_cycle_definition_file_schema "$(cycle_definition_file_path)" || return 10
  sync_runtime_state_for_cycle_rel "$(active_cycle_rel_path)" >/dev/null || return 10
  require_file "$(feature_file_path)" || return 10
  validate_runtime_cycle_file_schema "$(feature_file_path)" || return 10

  return 0
}

run_preflight_verification() {
  run_preflight_base || return 10

  require_file "${WQB_SCRIPT_ROOT}/research_queue_builder.py" || return 10
  require_file "${WQB_SCRIPT_ROOT}/candidate_scorecard.py" || return 10
  require_file "${WQB_SCRIPT_ROOT}/session_note_scaffold.py" || return 10
  require_file "${HARNESS_ROOT}/lib/content-validator.py" || return 10

  return 0
}

run_preflight_environment() {
  run_preflight_verification || return 10
  require_dir "${EXTERNAL_KB_ROOT}" || return 10
  return 0
}

run_preflight() {
  run_preflight_environment
}

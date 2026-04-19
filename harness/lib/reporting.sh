#!/usr/bin/env bash

report_documents_script() {
  printf '%s\n' "${HARNESS_LIB_DIR}/report_documents.py"
}

learning_loop_script() {
  printf '%s\n' "${HARNESS_LIB_DIR}/learning_loop.py"
}

cycle_report_path() {
  local cycle_path="$1"
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(report_documents_script)" cycle-report-path "$normalized_rel"
}

resume_brief_path() {
  local cycle_path="$1"
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(report_documents_script)" resume-brief-path "$normalized_rel"
}

project_lessons_path() {
  local cycle_path="$1"
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(learning_loop_script)" project-lessons-path "$normalized_rel"
}

kb_candidate_path() {
  local cycle_path="$1"
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(learning_loop_script)" kb-candidate-path "$normalized_rel"
}

skill_candidate_path() {
  local cycle_path="$1"
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(learning_loop_script)" skill-candidate-path "$normalized_rel"
}

promotion_gate_path() {
  local cycle_path="$1"
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(learning_loop_script)" promotion-gate-path "$normalized_rel"
}

kb_promotion_draft_path() {
  local cycle_path="$1"
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(learning_loop_script)" kb-promotion-draft-path "$normalized_rel"
}

skill_promotion_draft_path() {
  local cycle_path="$1"
  local normalized_rel
  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  python3 "$(learning_loop_script)" skill-promotion-draft-path "$normalized_rel"
}

resolve_reporting_doctor_state() {
  local normalized_rel="$1"

  if [ "$normalized_rel" = "$(active_cycle_rel_path)" ]; then
    if REPORTING_DOCTOR_OUTPUT="$(state_doctor_report 2>&1)"; then
      REPORTING_DOCTOR_STATUS="clean"
    else
      REPORTING_DOCTOR_STATUS="drift"
    fi
  else
    REPORTING_DOCTOR_STATUS="not-run"
    REPORTING_DOCTOR_OUTPUT="Skipped because the target cycle is not the active cycle."
  fi
}

write_cycle_report() {
  local cycle_path="$1"
  local normalized_rel
  local cycle_abs
  local report_rel
  local report_abs

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  cycle_abs="$(sync_runtime_state_for_cycle_rel "$normalized_rel")"
  [ -f "$cycle_abs" ] || {
    printf 'Cycle file does not exist: %s\n' "$normalized_rel" >&2
    return 12
  }

  report_rel="$(cycle_report_path "$normalized_rel")"
  report_abs="$(resolve_project_path "$report_rel")"
  resolve_reporting_doctor_state "$normalized_rel"

  python3 "$(report_documents_script)" \
    write-cycle-report \
    "$cycle_abs" \
    "$normalized_rel" \
    "$report_abs" \
    "$REPORTING_DOCTOR_STATUS" \
    "$REPORTING_DOCTOR_OUTPUT"

  printf '%s\n' "$report_rel"
}

write_resume_brief() {
  local cycle_path="$1"
  local normalized_rel
  local cycle_abs
  local brief_rel
  local brief_abs
  local report_rel
  local report_abs

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  cycle_abs="$(sync_runtime_state_for_cycle_rel "$normalized_rel")"
  [ -f "$cycle_abs" ] || {
    printf 'Cycle file does not exist: %s\n' "$normalized_rel" >&2
    return 12
  }

  brief_rel="$(resume_brief_path "$normalized_rel")"
  brief_abs="$(resolve_project_path "$brief_rel")"
  report_rel="$(cycle_report_path "$normalized_rel")"
  report_abs="$(resolve_project_path "$report_rel")"
  resolve_reporting_doctor_state "$normalized_rel"

  python3 "$(report_documents_script)" \
    write-resume-brief \
    "$cycle_abs" \
    "$normalized_rel" \
    "$brief_abs" \
    "$(progress_file_path)" \
    "$(decision_log_file_path)" \
    "$report_rel" \
    "$report_abs" \
    "$REPORTING_DOCTOR_STATUS" \
    "$REPORTING_DOCTOR_OUTPUT" \
    "$EXTERNAL_KB_ROOT"

  printf '%s\n' "$brief_rel"
}

write_learning_loop_bundle() {
  local cycle_path="$1"
  local report_rel="${2:-}"
  local normalized_rel
  local cycle_abs
  local project_rel
  local kb_rel
  local skill_rel
  local promotion_rel
  local kb_draft_rel
  local skill_draft_rel
  local project_abs
  local kb_abs
  local skill_abs
  local promotion_abs
  local kb_draft_abs
  local skill_draft_abs

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  cycle_abs="$(sync_runtime_state_for_cycle_rel "$normalized_rel")"
  [ -f "$cycle_abs" ] || {
    printf 'Cycle file does not exist: %s\n' "$normalized_rel" >&2
    return 12
  }

  if [ -z "$report_rel" ]; then
    report_rel="$(cycle_report_path "$normalized_rel")"
  fi

  project_rel="$(project_lessons_path "$normalized_rel")"
  kb_rel="$(kb_candidate_path "$normalized_rel")"
  skill_rel="$(skill_candidate_path "$normalized_rel")"
  promotion_rel="$(promotion_gate_path "$normalized_rel")"
  kb_draft_rel="$(kb_promotion_draft_path "$normalized_rel")"
  skill_draft_rel="$(skill_promotion_draft_path "$normalized_rel")"

  project_abs="$(resolve_project_path "$project_rel")"
  kb_abs="$(resolve_project_path "$kb_rel")"
  skill_abs="$(resolve_project_path "$skill_rel")"
  promotion_abs="$(resolve_project_path "$promotion_rel")"
  kb_draft_abs="$(resolve_project_path "$kb_draft_rel")"
  skill_draft_abs="$(resolve_project_path "$skill_draft_rel")"

  python3 "$(learning_loop_script)" \
    write-bundle \
    "$cycle_abs" \
    "$normalized_rel" \
    "$project_abs" \
    "$kb_abs" \
    "$skill_abs" \
    "$promotion_abs" \
    "$kb_draft_abs" \
    "$skill_draft_abs" \
    "$report_rel" \
    "$(decision_log_file_path)"

  printf '%s\n%s\n%s\n%s\n%s\n%s\n' \
    "$project_rel" \
    "$kb_rel" \
    "$skill_rel" \
    "$promotion_rel" \
    "$kb_draft_rel" \
    "$skill_draft_rel"
}

write_session_open_brief() {
  local cycle_path="$1"
  local normalized_rel
  local cycle_abs
  local brief_rel
  local brief_abs

  normalized_rel="$(normalize_project_rel_path "$cycle_path")" || {
    printf 'Cycle path must stay inside the project root: %s\n' "$cycle_path" >&2
    return 12
  }

  cycle_abs="$(sync_runtime_state_for_cycle_rel "$normalized_rel")"
  [ -f "$cycle_abs" ] || {
    printf 'Cycle file does not exist: %s\n' "$normalized_rel" >&2
    return 12
  }

  resolve_reporting_doctor_state "$normalized_rel"
  brief_rel="$(python3 "$(report_documents_script)" session-brief-path "$cycle_abs" "$normalized_rel")"
  brief_abs="$(resolve_project_path "$brief_rel")"

  python3 "$(report_documents_script)" \
    write-session-open \
    "$cycle_abs" \
    "$normalized_rel" \
    "$brief_abs" \
    "$brief_rel" \
    "$REPORTING_DOCTOR_STATUS" \
    "$REPORTING_DOCTOR_OUTPUT" \
    "$EXTERNAL_KB_ROOT" \
    "$(resolve_project_path "./harness/verification-modes.json")"

  printf '%s\n' "$brief_rel"
}

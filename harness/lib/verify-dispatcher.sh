#!/usr/bin/env bash

verify_feature() {
  local feature_id="$1"
  local artifacts_dir="${2:-}"
  local mode
  local target_rel
  local target_abs
  local -a runner_args

  mode="$(feature_verification_mode "$feature_id")"
  target_rel="$(feature_verification_target "$feature_id")"
  target_abs="$(project_rel_to_abs "$target_rel")"

  runner_args=(
    --mode "$mode"
    --target "$target_abs"
    --script-root "$WQB_SCRIPT_ROOT"
  )
  if [ -n "$artifacts_dir" ]; then
    runner_args+=(--artifacts-dir "$artifacts_dir")
  fi

  python3 "${HARNESS_ROOT}/lib/verification-runner.py" "${runner_args[@]}"

  python3 "${HARNESS_ROOT}/lib/content-validator.py" \
    --mode "$mode" \
    --path "$target_abs"
}

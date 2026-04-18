#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-module-boundaries.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

assert_file_contains() {
  local needle="$1"
  local path="$2"
  if ! grep -Fq "$needle" "$path"; then
    printf 'Expected file to contain: %s\nFile: %s\n' "$needle" "$path" >&2
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

assert_function_defined() {
  local fn_name="$1"
  local path="$2"
  if ! grep -Eq "^${fn_name}\\(\\) \\{" "$path"; then
    printf 'Expected function %s in file: %s\n' "$fn_name" "$path" >&2
    exit 1
  fi
}

assert_function_not_defined() {
  local fn_name="$1"
  local path="$2"
  if grep -Eq "^${fn_name}\\(\\) \\{" "$path"; then
    printf 'Did not expect function %s in file: %s\n' "$fn_name" "$path" >&2
    exit 1
  fi
}

assert_source_order() {
  local first_line
  local second_line
  local path="$1"
  local first_pattern="$2"
  local second_pattern="$3"

  first_line="$(grep -nF "$first_pattern" "$path" | head -n 1 | cut -d: -f1)"
  second_line="$(grep -nF "$second_pattern" "$path" | head -n 1 | cut -d: -f1)"

  [ -n "${first_line:-}" ] || {
    printf 'Missing source pattern in %s: %s\n' "$path" "$first_pattern" >&2
    exit 1
  }
  [ -n "${second_line:-}" ] || {
    printf 'Missing source pattern in %s: %s\n' "$path" "$second_pattern" >&2
    exit 1
  }

  if [ "$first_line" -ge "$second_line" ]; then
    printf 'Expected %s to appear before %s in %s\n' "$first_pattern" "$second_pattern" "$path" >&2
    exit 1
  fi
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"

reporting_path="$PROJECT_COPY/harness/lib/reporting.sh"
queries_path="$PROJECT_COPY/harness/lib/state-queries.sh"
helpers_path="$PROJECT_COPY/harness/lib/state-helpers.sh"
session_path="$PROJECT_COPY/harness/coding-session.sh"
init_path="$PROJECT_COPY/harness/init.sh"

assert_file_not_contains "<<'PY'" "$reporting_path"
assert_file_contains "report_documents.py" "$reporting_path"
assert_file_not_contains "<<'PY'" "$queries_path"
assert_file_contains "state_query_runner.py" "$queries_path"

for fn_name in \
  active_cycle_has_in_progress_features \
  list_cycle_rel_paths \
  cycle_summary_report \
  next_feature_id \
  feature_exists \
  feature_status \
  print_feature_brief \
  print_pending_summary
do
  assert_function_defined "$fn_name" "$queries_path"
  assert_function_not_defined "$fn_name" "$helpers_path"
done

for fn_name in \
  activate_cycle_path \
  create_cycle_from_active \
  archive_cycle_path \
  set_feature_state \
  update_progress_start \
  update_progress_finish
do
  assert_function_defined "$fn_name" "$helpers_path"
  assert_function_not_defined "$fn_name" "$queries_path"
done

assert_source_order "$session_path" '. "${SCRIPT_DIR}/lib/state-queries.sh"' '. "${SCRIPT_DIR}/lib/state-helpers.sh"'
assert_source_order "$init_path" '. "${SCRIPT_DIR}/lib/state-queries.sh"' '. "${SCRIPT_DIR}/lib/state-helpers.sh"'

printf 'Harness module boundaries test passed.\n'

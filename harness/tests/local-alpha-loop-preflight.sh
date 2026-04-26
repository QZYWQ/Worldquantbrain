#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-local-alpha-loop-preflight.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

assert_output_contains() {
  local needle="$1"
  local haystack="$2"
  if ! printf '%s\n' "$haystack" | grep -Fq -- "$needle"; then
    printf 'Expected output to contain: %s\nActual output:\n%s\n' "$needle" "$haystack" >&2
    exit 1
  fi
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"
cd "$PROJECT_COPY"

cat > ./runs/simulation-captures/000-preflight-bad.json <<'EOF'
{
  "capture_id": "preflight-bad",
EOF

set +e
output="$(./harness/run-local-alpha-loop.sh --run-id preflight-test 2>&1)"
status="$?"
set -e

if [ "$status" -eq 0 ]; then
  printf 'Expected capture preflight to fail before the local alpha loop starts.\n' >&2
  exit 1
fi

assert_output_contains "Invalid simulation capture JSON" "$output"
assert_output_contains "000-preflight-bad.json" "$output"

printf 'Local alpha loop capture preflight test passed.\n'

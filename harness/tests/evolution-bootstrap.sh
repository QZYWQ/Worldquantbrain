#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-evolution-bootstrap.XXXXXX")"
RUN_ID="test-evolution-bootstrap-$$"
ARTIFACT_ROOT="$TMP_ROOT/artifacts"
OUTPUT_DIR="$TMP_ROOT/evolution-generations"
LEARNING_JSON_PATH="$PROJECT_ROOT/runs/learning-loops/$RUN_ID.json"
LEARNING_MD_PATH="$PROJECT_ROOT/runs/learning-loops/$RUN_ID.md"
EXPECTED_BUNDLE_ROOT="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$ARTIFACT_ROOT/$RUN_ID")"

cleanup() {
  rm -rf "$TMP_ROOT"
  rm -f "$LEARNING_JSON_PATH" "$LEARNING_MD_PATH"
}

trap cleanup EXIT

assert_file_exists() {
  local path="$1"
  if [ ! -f "$path" ]; then
    printf 'Expected file to exist: %s\n' "$path" >&2
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

RUN_OUTPUT="$(bash ./harness/run-local-alpha-loop.sh \
  --evolution-bootstrap \
  --run-id "$RUN_ID" \
  --artifact-root "$ARTIFACT_ROOT" \
  --evolution-output-dir "$OUTPUT_DIR" \
  --evolution-generations 1 \
  --evolution-min-winners 1)"

assert_output_contains "Evolution bootstrap bundle: $EXPECTED_BUNDLE_ROOT" "$RUN_OUTPUT"
assert_output_contains "Evolution bootstrap manifest: $LEARNING_JSON_PATH" "$RUN_OUTPUT"
assert_output_contains "Evolution research-contract report:" "$RUN_OUTPUT"
assert_output_contains "Evolution next batch:" "$RUN_OUTPUT"

assert_file_exists "$LEARNING_JSON_PATH"
assert_file_exists "$LEARNING_MD_PATH"
assert_file_exists "$ARTIFACT_ROOT/$RUN_ID/manifest.json"
assert_file_exists "$ARTIFACT_ROOT/$RUN_ID/manifest.md"
assert_file_exists "$ARTIFACT_ROOT/$RUN_ID/result.json"

python3 - "$LEARNING_JSON_PATH" "$OUTPUT_DIR" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
output_dir = Path(sys.argv[2]).resolve()

if manifest.get("stage_label") != "F":
    raise SystemExit(f"unexpected stage label: {manifest.get('stage_label')!r}")
if manifest.get("status") != "ok":
    raise SystemExit(f"unexpected bootstrap status: {manifest.get('status')!r}")
if manifest.get("winner_count", 0) < 1:
    raise SystemExit(f"winner archive should be non-empty: {manifest.get('winner_count')!r}")
next_batch_path = Path(manifest.get("next_batch_path") or "")
if not next_batch_path.is_file():
    raise SystemExit(f"missing next batch path: {next_batch_path!s}")
if next_batch_path.parent.resolve() != output_dir.resolve():
    raise SystemExit(f"unexpected next batch parent: {next_batch_path.parent!s}")

artifacts = manifest.get("artifacts")
if not isinstance(artifacts, list) or not artifacts:
    raise SystemExit("bootstrap should record generation artifacts")
first = artifacts[0]
if first.get("batch_path") != str(next_batch_path):
    raise SystemExit("first generation batch path should match next_batch_path")
if not Path(first.get("canonical_path") or "").is_file():
    raise SystemExit("first generation canonical artifact missing")
PY

python3 - "$LEARNING_JSON_PATH" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
report_path = Path(manifest.get("research_contract_report_path") or "")
if not report_path.is_file():
    raise SystemExit(f"missing research contract report: {report_path!s}")
content = report_path.read_text(encoding="utf-8")
if "# Evolution Bootstrap Cycle Report" not in content:
    raise SystemExit("research contract report missing expected heading")
if "## Generation Summary" not in content:
    raise SystemExit("research contract report missing generation summary")
PY

printf 'Evolution bootstrap harness test passed.\n'

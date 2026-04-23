#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-local-alpha-loop.XXXXXX")"
RUN_ID="test-local-alpha-loop-$$"
MANIFEST_RUN_ID="test-local-alpha-loop-manifest-$$"
QUEUE_PATH="$TMP_ROOT/local-alpha-loop-queue.json"
PRIORITY_MANIFEST_PATH="$TMP_ROOT/priority-manifest.json"
ARTIFACT_ROOT="$TMP_ROOT/artifacts"
LOOP_BUNDLE_ROOT="$ARTIFACT_ROOT/$RUN_ID"
LOOP_JSON_PATH="$PROJECT_ROOT/runs/learning-loops/$RUN_ID.json"
LOOP_MD_PATH="$PROJECT_ROOT/runs/learning-loops/$RUN_ID.md"
EXPECTED_LOOP_BUNDLE_ROOT="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$LOOP_BUNDLE_ROOT")"
EXPECTED_MANIFEST_PATH="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$PRIORITY_MANIFEST_PATH")"

cleanup() {
  rm -rf "$TMP_ROOT"
  rm -rf "$LOOP_BUNDLE_ROOT"
  rm -f "$LOOP_JSON_PATH" "$LOOP_MD_PATH"
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

cat >"$PRIORITY_MANIFEST_PATH" <<EOF
{
  "generated_at": "2026-04-23T20:39:07+08:00",
  "objective": "prioritize materially different seed families before daily local mining",
  "priority_family_keys": [
    "analyst_eps_sibling_qfv4_industry",
    "analyst_eps_price_industry",
    "fundamental_model_slow_ratio_equity_cap"
  ],
  "shortlist": [
    {
      "family_key": "analyst_eps_sibling_qfv4_industry",
      "state": "branch",
      "priority_score": 69.8,
      "reason": "candidate evidence is clean on the common subset, but full submission gates are still missing",
      "doc_paths": [
        "runs/expression-families/analyst-sibling-branch.md"
      ],
      "field_pack_paths": [
        "runs/field-search-packs/analyst-sibling-search-pack.md"
      ]
    },
    {
      "family_key": "analyst_eps_price_industry",
      "state": "branch",
      "priority_score": 66.94,
      "reason": "candidate evidence is clean on the common subset, but full submission gates are still missing",
      "doc_paths": [
        "runs/expression-families/primary-direction-baselines.md"
      ],
      "field_pack_paths": [
        "runs/field-search-packs/primary-direction-search-pack.md"
      ]
    },
    {
      "family_key": "fundamental_model_slow_ratio_equity_cap",
      "state": "branch",
      "priority_score": 47.2,
      "reason": "family docs explicitly keep this family in branch",
      "doc_paths": [
        "runs/expression-families/2026-04-23-fundamental-model-slow-ratio-equity-cap-follow-up.md",
        "runs/expression-families/2026-04-23-fundamental-model-slow-ratio-equity-cap-structural-follow-up.md"
      ],
      "field_pack_paths": []
    }
  ],
  "settings": {
    "allowed_states": [
      "exploit",
      "branch",
      "explore"
    ],
    "hard_exclude_topic_patterns": [
      "news-attention",
      "buzz",
      "historical_volatility_20",
      "sales_delta",
      "operating_income",
      "analyst-disagreement",
      "price-volume short horizon",
      "capital-structure",
      "balance-sheet"
    ],
    "shortlist_limit": 8
  },
  "counts": {
    "family_count": 3,
    "shortlist_count": 3
  },
  "run_id": "$MANIFEST_RUN_ID"
}
EOF

RUN_OUTPUT="$(bash ./harness/run-local-alpha-loop.sh \
  --queue "$QUEUE_PATH" \
  --queue-template "$PROJECT_ROOT/harness/templates/local-alpha-loop-queue.template.json" \
  --priority-manifest "$PRIORITY_MANIFEST_PATH" \
  --prompt-template "$PROJECT_ROOT/harness/prompts/local-alpha-loop-prompt.txt" \
  --artifact-root "$ARTIFACT_ROOT" \
  --success-policy "$PROJECT_ROOT/harness/alpha-success-policy.json" \
  --run-id "$RUN_ID" \
  --max-rounds 1)"

assert_output_contains "Local alpha loop bundle: $EXPECTED_LOOP_BUNDLE_ROOT" "$RUN_OUTPUT"
assert_output_contains "Local alpha loop manifest: $LOOP_JSON_PATH" "$RUN_OUTPUT"

assert_file_exists "$LOOP_BUNDLE_ROOT/manifest.json"
assert_file_exists "$LOOP_BUNDLE_ROOT/manifest.md"
assert_file_exists "$LOOP_JSON_PATH"
assert_file_exists "$LOOP_MD_PATH"
assert_file_exists "$QUEUE_PATH"

python3 - "$LOOP_BUNDLE_ROOT/manifest.json" "$QUEUE_PATH" "$PRIORITY_MANIFEST_PATH" "$EXPECTED_MANIFEST_PATH" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
queue = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
priority_manifest = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
expected_manifest_path = sys.argv[4]

if manifest.get("completed_rounds") != 1:
    raise SystemExit(f"unexpected completed rounds: {manifest.get('completed_rounds')!r}")
counts = manifest.get("counts", {})
if counts.get("branch") + counts.get("hold") != 1 or counts.get("kill") != 0 or counts.get("blocked") != 0:
    raise SystemExit(f"unexpected loop counts: {counts!r}")
if manifest.get("priority_manifest_path") != expected_manifest_path:
    raise SystemExit(f"unexpected priority_manifest_path: {manifest.get('priority_manifest_path')!r}")
if manifest.get("priority_manifest_run_id") != priority_manifest.get("run_id"):
    raise SystemExit("loop manifest should record the source manifest run id")

rounds = manifest.get("rounds", [])
if len(rounds) != 1:
    raise SystemExit(f"unexpected round count: {len(rounds)}")
round_item = rounds[0]
if round_item.get("family_key") != "analyst_eps_sibling_qfv4_industry":
    raise SystemExit(f"unexpected family key: {round_item.get('family_key')!r}")
if round_item.get("result") not in {"branch", "hold"}:
    raise SystemExit(f"unexpected round result: {round_item.get('result')!r}")
expected_status = "done" if round_item.get("result") == "branch" else "hold"
if round_item.get("status_after") != expected_status:
    raise SystemExit(f"unexpected round status: {round_item.get('status_after')!r}")
if not Path(round_item.get("prompt_path", "")).is_file():
    raise SystemExit("prompt file missing")
if not Path(round_item.get("stdout_log", "")).is_file():
    raise SystemExit("stdout log missing")
if not Path(round_item.get("stderr_log", "")).is_file():
    raise SystemExit("stderr log missing")
if not Path(round_item.get("summary_path", "")).is_file():
    raise SystemExit("summary.json missing")
if not any("factory" in str(path) for path in round_item.get("generated_files", [])):
    raise SystemExit("factory bundle paths were not recorded")

queue_items = queue.get("items", [])
expected_keys = priority_manifest.get("priority_family_keys", [])
actual_keys = [str(item.get("family_key") or "") for item in queue_items]
if actual_keys != expected_keys:
    raise SystemExit(f"queue order did not match priority manifest: {actual_keys!r}")
if len(queue_items) != len(expected_keys):
    raise SystemExit(f"unexpected queue size: {len(queue_items)}")
if queue.get("source_manifest_path") != expected_manifest_path:
    raise SystemExit(f"unexpected source_manifest_path: {queue.get('source_manifest_path')!r}")
if queue.get("source_manifest_run_id") != priority_manifest.get("run_id"):
    raise SystemExit("queue should record the source manifest run id")

first_item = queue_items[0]
expected_item_status = "done" if round_item.get("result") == "branch" else "hold"
if first_item.get("status") != expected_item_status:
    raise SystemExit(f"expected first item status {expected_item_status!r}, got {first_item.get('status')!r}")
if first_item.get("id") != "analyst-eps-sibling-qfv4-industry-001":
    raise SystemExit(f"unexpected first item id: {first_item.get('id')!r}")
if first_item.get("priority") <= queue_items[1].get("priority"):
    raise SystemExit("queue priorities should descend with manifest order")
inputs = first_item.get("inputs", {})
if inputs.get("priority_manifest") != expected_manifest_path:
    raise SystemExit("priority manifest path missing from queue inputs")
if inputs.get("priority_family_order") != 1:
    raise SystemExit(f"unexpected priority family order: {inputs.get('priority_family_order')!r}")
if inputs.get("priority_manifest_run_id") != priority_manifest.get("run_id"):
    raise SystemExit("queue inputs should record the source manifest run id")
if inputs.get("priority_family_keys") != expected_keys:
    raise SystemExit("queue inputs should preserve the manifest family order")
read_files = inputs.get("read_files", [])
if expected_manifest_path not in read_files:
    raise SystemExit("priority manifest path should be in read_files")
if not any(path.endswith("analyst-sibling-branch.md") for path in read_files):
    raise SystemExit("family doc path should be in read_files")
execution = first_item.get("execution", {})
factory_args = execution.get("factory_args", {}) if isinstance(execution, dict) else {}
if factory_args.get("include_topic") != ["analyst_eps_sibling_qfv4_industry"]:
    raise SystemExit("factory args should target the top priority family")
last_run = first_item.get("last_run", {})
if last_run.get("result") != round_item.get("result"):
    raise SystemExit(f"unexpected last_run.result: {last_run.get('result')!r}")
if last_run.get("run_id") != round_item.get("round_id"):
    raise SystemExit("last_run.run_id should match the processed round")
if not Path(last_run.get("prompt_path", "")).is_file():
    raise SystemExit("last_run.prompt_path should exist")
PY

printf 'Local alpha loop test passed.\n'

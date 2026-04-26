#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
QUEUE_PATH="${PROJECT_ROOT}/harness/state/local-alpha-loop-queue.json"
QUEUE_TEMPLATE_PATH="${PROJECT_ROOT}/harness/templates/local-alpha-loop-queue.template.json"
PRIORITY_MANIFEST_PATH=""
PROMPT_TEMPLATE_PATH="${PROJECT_ROOT}/harness/prompts/local-alpha-loop-prompt.txt"
ARTIFACT_ROOT="${PROJECT_ROOT}/harness/artifacts/automation-runs"
SUCCESS_POLICY_PATH="${PROJECT_ROOT}/harness/alpha-success-policy.json"
RUN_ID=""
MAX_ROUNDS=3

validate_simulation_capture_json_tree() {
  python3 - "$PROJECT_ROOT" <<'PY'
import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
capture_root = project_root / "runs" / "simulation-captures"
if not capture_root.exists():
    raise SystemExit(f"Missing simulation capture directory: {capture_root}")

for path in sorted(capture_root.rglob("*.json")):
    try:
        with path.open("r", encoding="utf-8") as handle:
            json.load(handle)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Invalid simulation capture JSON: {path}: {exc.msg} at line {exc.lineno} column {exc.colno}"
        )
PY
}

usage() {
  cat <<'USAGE'
Usage:
  ./harness/run-local-alpha-loop.sh [--queue PATH] [--queue-template PATH] [--priority-manifest PATH]
                                     [--prompt-template PATH] [--artifact-root PATH]
                                     [--success-policy PATH] [--run-id ID] [--max-rounds N]
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --queue)
      QUEUE_PATH="${2:-}"
      shift 2
      ;;
    --queue-template)
      QUEUE_TEMPLATE_PATH="${2:-}"
      shift 2
      ;;
    --priority-manifest|--expander-manifest)
      PRIORITY_MANIFEST_PATH="${2:-}"
      shift 2
      ;;
    --prompt-template)
      PROMPT_TEMPLATE_PATH="${2:-}"
      shift 2
      ;;
    --artifact-root)
      ARTIFACT_ROOT="${2:-}"
      shift 2
      ;;
    --success-policy)
      SUCCESS_POLICY_PATH="${2:-}"
      shift 2
      ;;
    --run-id)
      RUN_ID="${2:-}"
      shift 2
      ;;
    --max-rounds)
      MAX_ROUNDS="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

validate_simulation_capture_json_tree

mkdir -p "$ARTIFACT_ROOT"
LOCK_DIR="${ARTIFACT_ROOT}/.local-alpha-loop.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf 'Local alpha loop is already running.\n' >&2
  exit 11
fi
cleanup() {
  rm -rf "$LOCK_DIR"
}
trap cleanup EXIT
trap 'trap - EXIT; cleanup; exit 130' INT
trap 'trap - EXIT; cleanup; exit 143' TERM

cmd=(
  python3 "${SCRIPT_DIR}/lib/local_alpha_loop.py" run-loop
  --queue "$QUEUE_PATH"
  --queue-template "$QUEUE_TEMPLATE_PATH"
  --prompt-template "$PROMPT_TEMPLATE_PATH"
  --artifact-root "$ARTIFACT_ROOT"
  --project-root "$PROJECT_ROOT"
  --success-policy "$SUCCESS_POLICY_PATH"
  --run-id "$RUN_ID"
  --max-rounds "$MAX_ROUNDS"
)
if [ -n "$PRIORITY_MANIFEST_PATH" ]; then
  cmd+=(--priority-manifest "$PRIORITY_MANIFEST_PATH")
fi

"${cmd[@]}"

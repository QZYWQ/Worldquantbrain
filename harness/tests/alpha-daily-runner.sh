#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-alpha-daily-runner.XXXXXX")"
RUN_ID="test-alpha-daily-runner-$$"

DAILY_ARTIFACT_ROOT="${PROJECT_ROOT}/harness/artifacts/alpha-daily"
DAILY_MANIFEST_ROOT="${DAILY_ARTIFACT_ROOT}/${RUN_ID}"
EXPLOIT_BUNDLE_ROOT="${DAILY_ARTIFACT_ROOT}/${RUN_ID}-01-exploit_family"
BRANCH_BUNDLE_ROOT="${DAILY_ARTIFACT_ROOT}/${RUN_ID}-02-branch_family"
DAILY_JSON_PATH="${PROJECT_ROOT}/runs/learning-loops/${RUN_ID}.json"
DAILY_MD_PATH="${PROJECT_ROOT}/runs/learning-loops/${RUN_ID}.md"

cleanup() {
  rm -rf "$TMP_ROOT"
  rm -rf "$DAILY_MANIFEST_ROOT"
  rm -rf "$EXPLOIT_BUNDLE_ROOT"
  rm -rf "$BRANCH_BUNDLE_ROOT"
  rm -f "$DAILY_JSON_PATH" "$DAILY_MD_PATH"
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

assert_path_absent() {
  local path="$1"
  if [ -e "$path" ]; then
    printf 'Refusing to reuse an existing path: %s\n' "$path" >&2
    exit 1
  fi
}

assert_path_absent "$DAILY_MANIFEST_ROOT"
assert_path_absent "$EXPLOIT_BUNDLE_ROOT"
assert_path_absent "$BRANCH_BUNDLE_ROOT"
assert_path_absent "$DAILY_JSON_PATH"
assert_path_absent "$DAILY_MD_PATH"

FIXTURE_ROOT="$TMP_ROOT/fixture"
mkdir -p \
  "$FIXTURE_ROOT/families" \
  "$FIXTURE_ROOT/captures" \
  "$FIXTURE_ROOT/candidate-batches" \
  "$FIXTURE_ROOT/candidate-checks" \
  "$TMP_ROOT/published"

cat >"$FIXTURE_ROOT/families/exploit-family.md" <<'EOF'
# Exploit Family

## Metadata

- Date: `2026-04-23`
- Topic: `exploit_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Decision

- Exploit: keep the winning anchor live while the real full-gate record stays green.

## Baseline Expression

```text
ts_rank(group_rank(exploit_signal, industry), 63)
```

## Variant 1

```text
ts_rank(group_rank(ts_mean(exploit_signal, 20), industry), 63)
```
EOF

cat >"$FIXTURE_ROOT/families/branch-family.md" <<'EOF'
# Branch Family

## Metadata

- Date: `2026-04-23`
- Topic: `branch_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Decision

- Branch: keep one clean anchor and one materially different follow-up.

## Baseline Expression

```text
ts_rank(group_rank(branch_signal, industry), 63)
```

## Variant 1

```text
ts_rank(group_rank(ts_mean(branch_signal, 20), industry), 63)
```
EOF

cat >"$FIXTURE_ROOT/families/hold-family.md" <<'EOF'
# Hold Family

## Metadata

- Date: `2026-04-23`
- Topic: `hold_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Baseline Expression

```text
rank(hold_signal)
```
EOF

cat >"$FIXTURE_ROOT/families/kill-family.md" <<'EOF'
# Kill Family

## Metadata

- Date: `2026-04-23`
- Topic: `kill_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Decision

- Kill the dead family and do not keep polishing it.

## Baseline Expression

```text
rank(kill_signal)
```
EOF

cat >"$FIXTURE_ROOT/captures/exploit-pass.json" <<'EOF'
{
  "capture_id": "exploit-pass-01",
  "topic": "exploit_family_batch_01",
  "capture_mode": "network-api",
  "alphas": [
    {
      "name": "exploit_anchor",
      "expression": "ts_rank(group_rank(exploit_signal, industry), 63)",
      "metrics": {
        "is_sharpe": 1.82,
        "is_fitness": 1.31
      },
      "checks": [
        {"name": "LOW_SHARPE", "result": "PASS", "value": 1.82, "limit": 1.25},
        {"name": "LOW_FITNESS", "result": "PASS", "value": 1.31, "limit": 1.00},
        {"name": "LOW_TURNOVER", "result": "PASS"},
        {"name": "HIGH_TURNOVER", "result": "PASS"},
        {"name": "CONCENTRATED_WEIGHT", "result": "PASS"},
        {"name": "LOW_SUB_UNIVERSE_SHARPE", "result": "PASS"},
        {"name": "SELF_CORRELATION", "result": "PASS"},
        {"name": "MATCHES_COMPETITION", "result": "PASS"}
      ]
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/captures/branch-partial.json" <<'EOF'
{
  "capture_id": "branch-partial-01",
  "topic": "branch_family_batch_01",
  "capture_mode": "manual-ui",
  "alphas": [
    {
      "name": "branch_anchor",
      "expression": "ts_rank(group_rank(branch_signal, industry), 63)",
      "metrics": {
        "sharpe": 1.44,
        "fitness": 1.09
      },
      "tests": {
        "subuniverse_pass": true,
        "check_submission_pass": null
      }
    }
  ]
}
EOF

cat >"$FIXTURE_ROOT/captures/hold-fail.json" <<'EOF'
{
  "capture_id": "hold-fail-01",
  "topic": "hold_family_batch_01",
  "capture_mode": "network-api",
  "alphas": [
    {
      "name": "hold_anchor",
      "expression": "rank(hold_signal)",
      "metrics": {
        "is_sharpe": 0.72,
        "is_fitness": 0.44
      },
      "checks": [
        {"name": "LOW_SHARPE", "result": "FAIL", "value": 0.72, "limit": 1.25},
        {"name": "LOW_FITNESS", "result": "FAIL", "value": 0.44, "limit": 1.0},
        {"name": "LOW_TURNOVER", "result": "PASS"},
        {"name": "HIGH_TURNOVER", "result": "PASS"},
        {"name": "CONCENTRATED_WEIGHT", "result": "PASS"},
        {"name": "LOW_SUB_UNIVERSE_SHARPE", "result": "FAIL", "value": 0.12, "limit": 0.39},
        {"name": "SELF_CORRELATION", "result": "PASS"},
        {"name": "MATCHES_COMPETITION", "result": "PASS"}
      ]
    }
  ]
}
EOF

cat >"$TMP_ROOT/success-policy.json" <<'EOF'
{
  "objective": "maximize_internal_submit_ready_per_official_slot",
  "failure_checks": ["LOW_SHARPE", "LOW_FITNESS", "LOW_SUB_UNIVERSE_SHARPE", "SELF_CORRELATION"],
  "hard_exclude_topic_patterns": [],
  "budget": {
    "official_budget": 2,
    "max_official_per_family": 1,
    "official_similarity_threshold": 0.88,
    "max_anchor_per_family": 1
  },
  "priors": {
    "exploit_state_bonus": 12.0,
    "branch_state_bonus": 6.0,
    "hold_state_penalty": 18.0,
    "kill_state_penalty": 100.0,
    "submit_ready_bonus": 20.0,
    "low_sharpe_penalty": 25.0,
    "low_fitness_penalty": 20.0,
    "low_sub_universe_penalty": 18.0,
    "self_correlation_penalty": 15.0,
    "fail_similarity_penalty_start": 0.55,
    "fail_similarity_hard_drop": 0.82
  }
}
EOF

cd "$PROJECT_ROOT"

RUN_OUTPUT="$(python3 ./scripts/alpha_daily_runner.py \
  --family-dir "$FIXTURE_ROOT/families" \
  --capture-dir "$FIXTURE_ROOT/captures" \
  --candidate-batch-dir "$FIXTURE_ROOT/candidate-batches" \
  --candidate-check-dir "$FIXTURE_ROOT/candidate-checks" \
  --success-policy "$TMP_ROOT/success-policy.json" \
  --artifact-root "$DAILY_ARTIFACT_ROOT" \
  --publish-root "$TMP_ROOT/published" \
  --run-id "$RUN_ID" \
  --family-limit 2 \
  --max-candidates 40 \
  --per-seed 8 \
  --max-depth 1 \
  --min-score 10 \
  --max-total 4 \
  --official-budget 2 \
  --max-official-per-family 1)"

assert_output_contains "Daily run bundle: ${PROJECT_ROOT}/harness/artifacts/alpha-daily/${RUN_ID}" "$RUN_OUTPUT"
assert_output_contains "Daily manifest: ${PROJECT_ROOT}/runs/learning-loops/${RUN_ID}.json" "$RUN_OUTPUT"

assert_file_exists "$DAILY_MANIFEST_ROOT/manifest.json"
assert_file_exists "$DAILY_MANIFEST_ROOT/manifest.md"
assert_file_exists "$EXPLOIT_BUNDLE_ROOT/manifest.json"
assert_file_exists "$BRANCH_BUNDLE_ROOT/manifest.json"
assert_file_exists "$DAILY_JSON_PATH"
assert_file_exists "$DAILY_MD_PATH"

python3 - "$PROJECT_ROOT" "$RUN_ID" <<'PY'
import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1])
run_id = sys.argv[2]

artifact_root = project_root / "harness" / "artifacts" / "alpha-daily"
manifest_root = artifact_root / run_id
manifest_path = manifest_root / "manifest.json"
manifest_md_path = manifest_root / "manifest.md"
daily_json_path = project_root / "runs" / "learning-loops" / f"{run_id}.json"
daily_md_path = project_root / "runs" / "learning-loops" / f"{run_id}.md"

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
daily_manifest = json.loads(daily_json_path.read_text(encoding="utf-8"))

if manifest != daily_manifest:
    raise SystemExit("daily JSON output should match the artifact manifest exactly")

artifact_md = manifest_md_path.read_text(encoding="utf-8")
daily_md = daily_md_path.read_text(encoding="utf-8")
if artifact_md != daily_md:
    raise SystemExit("daily markdown output should match the artifact markdown exactly")

if manifest["run_id"] != run_id:
    raise SystemExit(f"unexpected run_id: {manifest['run_id']}")
if manifest["objective"] != "maximize_internal_submit_ready_per_official_slot":
    raise SystemExit(f"unexpected objective: {manifest['objective']}")

expected_counts = {
    "family_docs": 4,
    "official_outcome_memory": 3,
    "candidate_outcome_memory": 0,
    "combined_outcome_memory": 3,
    "submit_ready_ledger": 1,
    "family_registry_summary": 4,
}
if manifest["success_state_counts"] != expected_counts:
    raise SystemExit(
        f"unexpected success-state counts: {manifest['success_state_counts']}"
    )

selected = manifest.get("selected_families", [])
selected_keys = [row["family_key"] for row in selected]
if selected_keys != ["exploit_family", "branch_family"]:
    raise SystemExit(f"unexpected selected families: {selected_keys}")

selected_states = {row["family_key"]: row["state"] for row in selected}
if selected_states["exploit_family"] != "exploit":
    raise SystemExit("exploit_family should rank as exploit")
if selected_states["branch_family"] != "branch":
    raise SystemExit("branch_family should rank as branch")

family_runs = manifest.get("family_runs", [])
if [run["topic"] for run in family_runs] != ["exploit_family", "branch_family"]:
    raise SystemExit(f"unexpected family run order: {[run['topic'] for run in family_runs]}")

for run in family_runs:
    bundle_root = Path(run["bundle_root"])
    if not bundle_root.is_dir():
        raise SystemExit(f"bundle root does not exist: {bundle_root}")
    if run.get("selected_count", 0) <= 0:
        raise SystemExit(f"expected positive selected_count for {run['topic']}")
    if "Run bundle:" not in str(run.get("stdout") or ""):
        raise SystemExit(f"family factory stdout missing run bundle marker for {run['topic']}")
    family_manifest = run.get("manifest", {})
    if family_manifest.get("counts", {}).get("family_count") != 1:
        raise SystemExit(f"family factory should isolate one family for {run['topic']}")
    official_items = run.get("official_budget", {}).get("items", [])
    if len(official_items) != 1:
        raise SystemExit(f"expected one official-budget item for {run['topic']}, got {len(official_items)}")
    if official_items[0].get("family_topic") != run["topic"]:
        raise SystemExit(
            f"official-budget item family mismatch for {run['topic']}: {official_items[0].get('family_topic')}"
        )

daily_budget_items = manifest.get("daily_budget_items", [])
if len(daily_budget_items) != 2:
    raise SystemExit(f"expected two daily budget items, got {len(daily_budget_items)}")

budget_families = {item.get("source_family_topic") for item in daily_budget_items}
if budget_families != {"exploit_family", "branch_family"}:
    raise SystemExit(f"unexpected daily budget family set: {sorted(budget_families)}")

if "hold_family" in selected_keys or "kill_family" in selected_keys:
    raise SystemExit("hold/kill families should not be scheduled by the daily runner")

if "# Daily Alpha Mining Runner" not in daily_md:
    raise SystemExit("daily markdown output should include the report heading")
if "- Selected families: 2" not in daily_md:
    raise SystemExit("daily markdown output should record the selected-family count")
PY

printf 'Alpha daily runner test passed.\n'

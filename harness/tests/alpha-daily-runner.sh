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
  "$FIXTURE_ROOT/field-search-packs" \
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

## Research Contract

- Mechanism: `cross_sectional_rank`
- Data category: `fundamental`
- Idea type: `winning_anchor`
- Universe: `TOP3000`
- Liquidity fit: `broad_liquid`
- Holding frequency: `slow`
- Delay: `1`
- Neutralization target: `industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `drop_sparse`
- Pasteurization: `enabled`
- Unit handling: `verify`
- Coverage floor: `70%`
- Freshness floor days: `7`
- Factor risk hypothesis: `Primary risk is persistent sector crowding.`
- Kill condition: `Keep this lane live only while the anchor remains full-gate strong.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus factor review`
- Comparison controls: `compare against one slower control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed or partial official evidence`

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

## Research Contract

- Mechanism: `cross_sectional_rank`
- Data category: `fundamental`
- Idea type: `branch_follow_up`
- Universe: `TOP3000`
- Liquidity fit: `broad_liquid`
- Holding frequency: `slow`
- Delay: `1`
- Neutralization target: `industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `drop_sparse`
- Pasteurization: `enabled`
- Unit handling: `verify`
- Coverage floor: `70%`
- Freshness floor days: `7`
- Factor risk hypothesis: `Primary risk is sector crowding on the same mechanism.`
- Kill condition: `Keep one anchor and one materially different follow-up only while the branch stays live.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus factor review`
- Comparison controls: `compare against one slower control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed or partial official evidence`

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

## Research Contract

- Mechanism: `control`
- Data category: `fundamental`
- Idea type: `hold_control`
- Universe: `TOP3000`
- Liquidity fit: `broad_liquid`
- Holding frequency: `slow`
- Delay: `1`
- Neutralization target: `none`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `drop_sparse`
- Pasteurization: `enabled`
- Unit handling: `verify`
- Coverage floor: `70%`
- Freshness floor days: `7`
- Factor risk hypothesis: `Primary risk is no durable edge.`
- Kill condition: `Keep held until a materially different thesis appears.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus factor review`
- Comparison controls: `compare against one slower control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed or partial official evidence`

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

## Research Contract

- Mechanism: `control`
- Data category: `price_volume`
- Idea type: `dead_control`
- Universe: `TOP3000`
- Liquidity fit: `broad_liquid`
- Holding frequency: `slow`
- Delay: `1`
- Neutralization target: `none`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `drop_sparse`
- Pasteurization: `enabled`
- Unit handling: `verify`
- Coverage floor: `70%`
- Freshness floor days: `7`
- Factor risk hypothesis: `No surviving differentiated factor thesis remains.`
- Kill condition: `Do not keep polishing this dead family.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus factor review`
- Comparison controls: `compare against one slower control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed or partial official evidence`

## Decision

- Kill the dead family and do not keep polishing it.

## Baseline Expression

```text
rank(kill_signal)
```
EOF

cat >"$FIXTURE_ROOT/field-search-packs/exploit-pack.md" <<'EOF'
# Exploit Pack

## Metadata

- Date: `2026-04-23`
- Topic: `exploit_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `exploit_signal` | `dataset` | Winning signal | `100%` coverage | low |

## Coverage And Quality Checks

- Coverage: strong
- Missingness: reviewed
- Region / delay compatibility: USA / D1 / TOP3000
- Field type: matrix

## Baseline Expression Ideas

1. `ts_rank(group_rank(exploit_signal, industry), 63)`

## Next Action

- Which field should be tried first? `exploit_signal`
EOF

cat >"$FIXTURE_ROOT/field-search-packs/branch-pack.md" <<'EOF'
# Branch Pack

## Metadata

- Date: `2026-04-23`
- Topic: `branch_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `branch_signal` | `dataset` | Branch signal | `100%` coverage | low |

## Coverage And Quality Checks

- Coverage: strong
- Missingness: reviewed
- Region / delay compatibility: USA / D1 / TOP3000
- Field type: matrix

## Baseline Expression Ideas

1. `ts_rank(group_rank(branch_signal, industry), 63)`

## Next Action

- Which field should be tried first? `branch_signal`
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
  --field-search-pack-dir "$FIXTURE_ROOT/field-search-packs" \
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
if manifest.get("excluded_families"):
    raise SystemExit(f"expected no excluded families, got {manifest['excluded_families']!r}")
if manifest.get("field_readiness", {}).get("counts", {}).get("pass_count") != 2:
    raise SystemExit(f"expected two field-readiness passes, got {manifest.get('field_readiness')!r}")
if manifest.get("account_capability", {}).get("counts", {}).get("pass_count") != 2:
    raise SystemExit(f"expected two account-capability passes, got {manifest.get('account_capability')!r}")
if manifest.get("research_contract", {}).get("counts", {}).get("pass_count") != 2:
    raise SystemExit(f"expected two research-contract passes, got {manifest.get('research_contract')!r}")
if manifest.get("validation_design", {}).get("counts", {}).get("pass_count") != 2:
    raise SystemExit(f"expected two validation-design passes, got {manifest.get('validation_design')!r}")
if manifest.get("complexity_budget", {}).get("counts", {}).get("pass_count", 0) < 2:
    raise SystemExit(f"expected at least two complexity-budget passes, got {manifest.get('complexity_budget')!r}")
if manifest.get("economic_distinctness", {}).get("counts", {}).get("pass_count", 0) < 2:
    raise SystemExit(f"expected at least two economic-distinctness passes, got {manifest.get('economic_distinctness')!r}")
provenance_counts = manifest.get("validation_provenance", {}).get("counts", {})
if provenance_counts.get("binding_family_count", 0) < 1 or provenance_counts.get("hold_count", 0) < 1:
    raise SystemExit(f"unexpected validation-provenance counts: {provenance_counts}")
evidence_counts = manifest.get("evidence_ladder", {}).get("counts", {})
if evidence_counts.get("E4_submit_ready") != 1 or evidence_counts.get("E2_partial_official") != 1:
    raise SystemExit(f"unexpected evidence-ladder counts: {evidence_counts}")
allocator_counts = manifest.get("research_allocator", {}).get("counts", {})
if allocator_counts.get("selected_primary_count") != 1 or allocator_counts.get("selected_backfill_count") != 1:
    raise SystemExit(f"unexpected allocator counts: {allocator_counts}")
if manifest.get("allocator_deferred_families"):
    raise SystemExit(f"expected no allocator-deferred families, got {manifest['allocator_deferred_families']!r}")

selected_states = {row["family_key"]: row["state"] for row in selected}
if selected_states["exploit_family"] != "exploit":
    raise SystemExit("exploit_family should rank as exploit")
if selected_states["branch_family"] != "explore":
    raise SystemExit("branch_family should be capped to explore under partial official evidence")

selected_by_family = {row["family_key"]: row for row in selected}
if selected_by_family["branch_family"].get("evidence_ladder_level") != "E2_partial_official":
    raise SystemExit("branch_family should carry E2 partial-official evidence in the daily runner")
if selected_by_family["branch_family"].get("account_capability_gate_status") != "pass":
    raise SystemExit("branch_family should pass the account-capability gate")
if selected_by_family["branch_family"].get("complexity_budget_gate_status") != "pass":
    raise SystemExit("branch_family should pass the complexity budget gate")
if selected_by_family["branch_family"].get("validation_design_gate_status") != "pass":
    raise SystemExit("branch_family should pass the validation-design gate")
if selected_by_family["branch_family"].get("validation_provenance_gate_status") != "hold":
    raise SystemExit("branch_family should stay non-binding in provenance")
if selected_by_family["branch_family"].get("research_allocator_status") != "selected_backfill":
    raise SystemExit("branch_family should be kept as controlled backfill")
if selected_by_family["branch_family"].get("economic_distinctness_gate_status") != "pass":
    raise SystemExit("branch_family should pass economic distinctness in this fixture")

exploit_provenance = selected_by_family["exploit_family"].get("validation_provenance_level")
if exploit_provenance not in {"full_submission_gates", "submit_ready"}:
    raise SystemExit(f"unexpected exploit provenance level: {exploit_provenance}")
if selected_by_family["exploit_family"].get("account_capability_gate_status") != "pass":
    raise SystemExit("exploit_family should pass the account-capability gate")
if selected_by_family["exploit_family"].get("research_allocator_status") != "selected_primary":
    raise SystemExit("exploit_family should stay the primary allocator pick")

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

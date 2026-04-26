#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-family-factory.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

trap cleanup EXIT

assert_file_exists() {
  local path="$1"
  if [ ! -f "$path" ]; then
    printf 'Expected file to exist: %s\n' "$path" >&2
    exit 1
  fi
}

FIXTURE_ROOT="$TMP_ROOT/fixture"
mkdir -p "$FIXTURE_ROOT/families" "$FIXTURE_ROOT/captures" "$FIXTURE_ROOT/field-search-packs"

cat >"$FIXTURE_ROOT/families/good-family.md" <<'EOF'
# Good Family

## Metadata

- Date: `2026-04-23`
- Topic: `good_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Keep one clean anchor for the empirically strongest family and branch only if it keeps local support.

## Research Contract

- Mechanism: `slow_ratio`
- Data category: `fundamental`
- Idea type: `cross_sectional_value`
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
- Factor risk hypothesis: `Primary risk is value and size, so keep industry grouping explicit.`
- Kill condition: `Kill the lane if one anchor and one orthogonal control both fail to keep local support.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus value review`
- Comparison controls: `compare against one slower value control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed or partial official evidence`

## Confirmed Or Assumed Inputs

- confirmed field: `good_signal`
- confirmed grouping: `industry`

## Optimization Order

- Keep one anchor first.
- Only keep one follow-up control if the anchor survives.

## Decision

- Branch: keep one anchor and one materially different follow-up.

## Baseline Expression

```text
ts_rank(group_rank(good_signal, industry), 63)
```

## Variant 1

```text
ts_rank(group_rank(ts_mean(good_signal, 20), industry), 63)
```
EOF

cat >"$FIXTURE_ROOT/families/blocked-family.md" <<'EOF'
# Blocked Family

## Metadata

- Date: `2026-04-23`
- Topic: `blocked_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This lane is blocked by prior official evidence and should only resume after a materially different template.

## Research Contract

- Mechanism: `cross_sectional_rank`
- Data category: `fundamental`
- Idea type: `slow_value_control`
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
- Factor risk hypothesis: `Primary risk is residual value exposure without a stable edge.`
- Kill condition: `Only resume after a materially different template replaces the blocked anchor.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus value review`
- Comparison controls: `compare against one slower value control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed or partial official evidence`

## Confirmed Or Assumed Inputs

- confirmed field: `blocked_signal`

## Optimization Order

- Keep this lane paused until the next materially different attempt.

## Baseline Expression

```text
rank(blocked_signal)
```
EOF

cat >"$FIXTURE_ROOT/families/dead-family.md" <<'EOF'
# Dead Family

## Metadata

- Date: `2026-04-23`
- Topic: `dead_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Kill this family and do not continue polishing it.

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
- Factor risk hypothesis: `No surviving differentiated volatility or liquidity-adjusted edge remains.`
- Kill condition: `Kill permanently once the family is marked dead in local evidence.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus volatility review`
- Comparison controls: `compare against one slower control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed or partial official evidence`

## Confirmed Or Assumed Inputs

- confirmed field: `dead_signal`

## Optimization Order

- Branch away from this lane completely.

## Baseline Expression

```text
rank(dead_signal)
```
EOF

cat >"$FIXTURE_ROOT/families/buzz-family.md" <<'EOF'
# Buzz Family

## Metadata

- Date: `2026-04-23`
- Topic: `buzz_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This topic should be removed by the success policy hard excludes.

## Research Contract

- Mechanism: `sentiment_rank`
- Data category: `sentiment`
- Idea type: `crowded_control`
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
- Freshness floor days: `1`
- Factor risk hypothesis: `Primary risk is crowded sentiment exposure.`
- Kill condition: `Do not schedule this family in the success-rate-first path.`

## Validation Design

- Primary test period: `P6M`
- Regime slices: `recent year; event bursts`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus crowding review`
- Comparison controls: `compare against one slower sentiment control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed or partial official evidence`

## Confirmed Or Assumed Inputs

- confirmed field: `buzz`
- confirmed grouping: `industry`

## Optimization Order

- Never schedule this family in the success-rate-first path.

## Baseline Expression

```text
ts_rank(group_rank(buzz, industry), 20)
```
EOF

cat >"$FIXTURE_ROOT/field-search-packs/good-pack.md" <<'EOF'
# Good Pack

## Metadata

- Date: `2026-04-23`
- Topic: `good_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `good_signal` | `dataset` | Good local seed | `100%` coverage | low |

## Coverage And Quality Checks

- Coverage: strong
- Missingness: reviewed
- Region / delay compatibility: USA / D1 / TOP3000
- Field type: matrix

## Baseline Expression Ideas

1. `ts_rank(group_rank(good_signal, industry), 63)`

## Next Action

- Which field should be tried first? `good_signal`
EOF

cat >"$FIXTURE_ROOT/captures/good-live.json" <<'EOF'
{
  "capture_id": "good-live-01",
  "topic": "good_family",
  "alphas": [
    {
      "expression": "ts_rank(group_rank(good_signal, industry), 63)",
      "tests": {
        "check_submission_pass": null
      }
    }
  ],
  "evidence": {
    "notes": [
      "Current anchor still looks live."
    ]
  }
}
EOF

cat >"$FIXTURE_ROOT/captures/blocked-failed.json" <<'EOF'
{
  "capture_id": "blocked-failed-01",
  "topic": "blocked_family",
  "alphas": [
    {
      "expression": "rank(blocked_signal)",
      "checks": [
        {"name": "LOW_SHARPE", "result": "FAIL", "value": 0.80, "limit": 1.25},
        {"name": "LOW_FITNESS", "result": "FAIL", "value": 0.60, "limit": 1.00},
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

cd "$PROJECT_ROOT"

RUN_OUTPUT="$(python3 ./scripts/alpha_family_factory.py \
  --family-dir "$FIXTURE_ROOT/families" \
  --field-search-pack-dir "$FIXTURE_ROOT/field-search-packs" \
  --capture-dir "$FIXTURE_ROOT/captures" \
  --artifact-root "$TMP_ROOT/artifacts" \
  --run-id fixture \
  --include-dead \
  --max-candidates 40 \
  --per-seed 8 \
  --max-depth 1 \
  --min-score 10 \
  --max-total 4 \
  --official-budget 2 \
  --max-official-per-family 1 \
  --publish-queue \
  --publish-root "$TMP_ROOT/published")"

printf '%s\n' "$RUN_OUTPUT" | grep -Fq "Run bundle:" || {
  printf 'Expected run output to print the run bundle path.\nActual output:\n%s\n' "$RUN_OUTPUT" >&2
  exit 1
}

BUNDLE_ROOT="$TMP_ROOT/artifacts/fixture"
assert_file_exists "$BUNDLE_ROOT/candidates.jsonl"
assert_file_exists "$BUNDLE_ROOT/scored.jsonl"
assert_file_exists "$BUNDLE_ROOT/scored.csv"
assert_file_exists "$BUNDLE_ROOT/scorecard.md"
assert_file_exists "$BUNDLE_ROOT/queue.json"
assert_file_exists "$BUNDLE_ROOT/queue.md"
assert_file_exists "$BUNDLE_ROOT/family-summary.json"
assert_file_exists "$BUNDLE_ROOT/family-summary.md"
assert_file_exists "$BUNDLE_ROOT/family-registry.json"
assert_file_exists "$BUNDLE_ROOT/family-registry.md"
assert_file_exists "$BUNDLE_ROOT/outcome-memory.json"
assert_file_exists "$BUNDLE_ROOT/outcome-memory.md"
assert_file_exists "$BUNDLE_ROOT/submit-ready-ledger.json"
assert_file_exists "$BUNDLE_ROOT/submit-ready-ledger.md"
assert_file_exists "$BUNDLE_ROOT/success-policy.json"
assert_file_exists "$BUNDLE_ROOT/field-readiness.json"
assert_file_exists "$BUNDLE_ROOT/field-readiness.md"
assert_file_exists "$BUNDLE_ROOT/account-capability.json"
assert_file_exists "$BUNDLE_ROOT/account-capability.md"
assert_file_exists "$BUNDLE_ROOT/research-contract.json"
assert_file_exists "$BUNDLE_ROOT/research-contract.md"
assert_file_exists "$BUNDLE_ROOT/validation-design.json"
assert_file_exists "$BUNDLE_ROOT/validation-design.md"
assert_file_exists "$BUNDLE_ROOT/factor-risk-overlay.json"
assert_file_exists "$BUNDLE_ROOT/factor-risk-overlay.md"
assert_file_exists "$BUNDLE_ROOT/complexity-budget.json"
assert_file_exists "$BUNDLE_ROOT/complexity-budget.md"
assert_file_exists "$BUNDLE_ROOT/mechanism-failure-memory.json"
assert_file_exists "$BUNDLE_ROOT/mechanism-failure-memory.md"
assert_file_exists "$BUNDLE_ROOT/economic-distinctness.json"
assert_file_exists "$BUNDLE_ROOT/economic-distinctness.md"
assert_file_exists "$BUNDLE_ROOT/validation-provenance.json"
assert_file_exists "$BUNDLE_ROOT/validation-provenance.md"
assert_file_exists "$BUNDLE_ROOT/evidence-ladder.json"
assert_file_exists "$BUNDLE_ROOT/evidence-ladder.md"
assert_file_exists "$BUNDLE_ROOT/official-budget.json"
assert_file_exists "$BUNDLE_ROOT/official-budget.md"
assert_file_exists "$BUNDLE_ROOT/manifest.json"
assert_file_exists "$TMP_ROOT/published/fixture.json"
assert_file_exists "$TMP_ROOT/published/fixture.md"

python3 - "$BUNDLE_ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
queue = json.loads((root / "queue.json").read_text(encoding="utf-8"))
family_summary = json.loads((root / "family-summary.json").read_text(encoding="utf-8"))
family_registry = json.loads((root / "family-registry.json").read_text(encoding="utf-8"))
official_budget = json.loads((root / "official-budget.json").read_text(encoding="utf-8"))
outcome_memory = json.loads((root / "outcome-memory.json").read_text(encoding="utf-8"))
submit_ready_ledger = json.loads((root / "submit-ready-ledger.json").read_text(encoding="utf-8"))
field_readiness = json.loads((root / "field-readiness.json").read_text(encoding="utf-8"))
account_capability = json.loads((root / "account-capability.json").read_text(encoding="utf-8"))
research_contract = json.loads((root / "research-contract.json").read_text(encoding="utf-8"))
validation_design = json.loads((root / "validation-design.json").read_text(encoding="utf-8"))
factor_risk_overlay = json.loads((root / "factor-risk-overlay.json").read_text(encoding="utf-8"))
complexity_budget = json.loads((root / "complexity-budget.json").read_text(encoding="utf-8"))
mechanism_failure_memory = json.loads((root / "mechanism-failure-memory.json").read_text(encoding="utf-8"))
economic_distinctness = json.loads((root / "economic-distinctness.json").read_text(encoding="utf-8"))
validation_provenance = json.loads((root / "validation-provenance.json").read_text(encoding="utf-8"))
evidence_ladder = json.loads((root / "evidence-ladder.json").read_text(encoding="utf-8"))
scored = [json.loads(line) for line in (root / "scored.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

if manifest["counts"]["family_count"] != 3:
    raise SystemExit(f"expected 3 selected families, got {manifest['counts']['family_count']}")
if manifest["counts"]["field_readiness_pass_count"] != 1:
    raise SystemExit(
        f"expected one field-readiness pass, got {manifest['counts']['field_readiness_pass_count']}"
    )
if manifest["counts"]["account_capability_pass_count"] != 3:
    raise SystemExit(
        f"expected three account-capability passes, got {manifest['counts']['account_capability_pass_count']}"
    )
if manifest["counts"]["research_contract_pass_count"] != 3:
    raise SystemExit(
        f"expected three research-contract passes, got {manifest['counts']['research_contract_pass_count']}"
    )
if manifest["counts"]["validation_design_pass_count"] != 3:
    raise SystemExit(
        f"expected three validation-design passes, got {manifest['counts']['validation_design_pass_count']}"
    )
if manifest["counts"]["factor_risk_overlay_pass_count"] != 3:
    raise SystemExit(
        f"expected three factor-risk-overlay passes, got {manifest['counts']['factor_risk_overlay_pass_count']}"
    )
if manifest["counts"]["complexity_budget_pass_count"] != 3:
    raise SystemExit(
        f"expected three complexity-budget passes, got {manifest['counts']['complexity_budget_pass_count']}"
    )
if manifest["counts"]["negative_failure_memory_count"] != 2:
    raise SystemExit(
        f"expected two negative failure-memory families, got {manifest['counts']['negative_failure_memory_count']}"
    )
if manifest["counts"]["economic_distinctness_pass_count"] != 3:
    raise SystemExit(
        f"expected three economic-distinctness passes, got {manifest['counts']['economic_distinctness_pass_count']}"
    )
if manifest["counts"]["binding_provenance_count"] != 1:
    raise SystemExit(
        f"expected one binding provenance family, got {manifest['counts']['binding_provenance_count']}"
    )
if manifest["counts"]["capture_count"] != 2:
    raise SystemExit(f"expected 2 captures in the manifest, got {manifest['counts']['capture_count']}")
if manifest["counts"]["family_registry_count"] != 3:
    raise SystemExit(f"expected 3 registry rows, got {manifest['counts']['family_registry_count']}")
if manifest["counts"]["official_outcome_count"] != 2:
    raise SystemExit(f"expected 2 official outcomes, got {manifest['counts']['official_outcome_count']}")
if manifest["counts"]["submit_ready_count"] != 0:
    raise SystemExit("fixture should not produce submit-ready entries")
if manifest["counts"]["candidate_count"] <= 0:
    raise SystemExit("expected positive candidate_count")
if manifest["counts"]["queue_count"] <= 0:
    raise SystemExit("expected at least one queue item")
if manifest["counts"]["official_budget_count"] != 1:
    raise SystemExit(
        f"expected exactly one official budget item, got {manifest['counts']['official_budget_count']}"
    )

if len(queue.get("items", [])) <= 0:
    raise SystemExit("expected at least one queue item")
if submit_ready_ledger:
    raise SystemExit("submit-ready ledger should be empty for this fixture")
if len(outcome_memory) != 2:
    raise SystemExit("expected two filtered official outcomes")
if field_readiness["counts"]["pass_count"] != 1:
    raise SystemExit(f"expected exactly one readiness pass, got {field_readiness['counts']}")
if field_readiness["counts"]["block_count"] != 2:
    raise SystemExit(f"expected two readiness blocks, got {field_readiness['counts']}")
if account_capability["counts"]["pass_count"] != 3:
    raise SystemExit(f"expected three capability passes, got {account_capability['counts']}")
if research_contract["counts"]["pass_count"] != 3:
    raise SystemExit(f"expected three contract passes, got {research_contract['counts']}")
if validation_design["counts"]["pass_count"] != 3:
    raise SystemExit(f"expected three validation-design passes, got {validation_design['counts']}")
if factor_risk_overlay["counts"]["pass_count"] != 3:
    raise SystemExit(f"expected three factor-risk-overlay passes, got {factor_risk_overlay['counts']}")
if complexity_budget["counts"]["pass_count"] != 3:
    raise SystemExit(f"expected three complexity passes, got {complexity_budget['counts']}")
if mechanism_failure_memory["counts"]["negative_family_count"] != 2:
    raise SystemExit(
        f"expected two negative failure-memory families, got {mechanism_failure_memory['counts']}"
    )
if economic_distinctness["counts"]["pass_count"] != 3:
    raise SystemExit(
        f"expected three economic-distinctness passes, got {economic_distinctness['counts']}"
    )
if validation_provenance["counts"]["binding_family_count"] != 1:
    raise SystemExit(f"expected one binding provenance family, got {validation_provenance['counts']}")
if validation_provenance["counts"]["hold_count"] != 1:
    raise SystemExit(f"expected one held provenance family, got {validation_provenance['counts']}")
if evidence_ladder["counts"]["E1_local_support"] != 0:
    raise SystemExit(f"expected zero E1 families in this fixture, got {evidence_ladder['counts']}")
if evidence_ladder["counts"]["E2_partial_official"] != 1:
    raise SystemExit(f"expected one E2 family, got {evidence_ladder['counts']}")
if evidence_ladder["counts"]["E3_full_is"] != 1:
    raise SystemExit(f"expected one E3 family, got {evidence_ladder['counts']}")

topics = {entry["topic"] for entry in family_summary}
expected_topics = {"good_family", "blocked_family", "dead_family"}
if topics != expected_topics:
    raise SystemExit(f"family summary topics mismatch: {sorted(topics)}")
if "buzz_family" in topics:
    raise SystemExit("buzz_family should be removed by the success policy hard excludes")

summary_by_topic = {entry["topic"]: entry for entry in family_summary}
if summary_by_topic["good_family"]["action"] != "branch":
    raise SystemExit("good_family should stay in branch")
if summary_by_topic["good_family"]["evidence_effective_state"] != "explore":
    raise SystemExit("good_family should be capped to explore by E1 evidence")
if summary_by_topic["good_family"]["complexity_budget_gate_status"] != "pass":
    raise SystemExit("good_family should pass the complexity budget gate")
if summary_by_topic["good_family"]["account_capability_gate_status"] != "pass":
    raise SystemExit("good_family should pass the account-capability gate")
if summary_by_topic["good_family"]["validation_design_gate_status"] != "pass":
    raise SystemExit("good_family should pass the validation-design gate")
if summary_by_topic["good_family"]["factor_risk_overlay_gate_status"] != "pass":
    raise SystemExit("good_family should pass the factor-risk-overlay gate")
if summary_by_topic["good_family"]["economic_distinctness_gate_status"] != "pass":
    raise SystemExit("good_family should pass the economic-distinctness gate")
if summary_by_topic["good_family"]["validation_provenance_level"] != "partial_tests":
    raise SystemExit("good_family should carry partial_tests provenance")
if summary_by_topic["blocked_family"]["action"] != "hold":
    raise SystemExit("blocked_family should move to hold after failed official gates")
if summary_by_topic["blocked_family"]["mechanism_failure_memory_status"] != "hold":
    raise SystemExit("blocked_family should carry negative failure memory")
if summary_by_topic["blocked_family"]["validation_provenance_level"] != "full_submission_gates":
    raise SystemExit("blocked_family should carry full_submission_gates provenance")
if summary_by_topic["dead_family"]["action"] != "kill":
    raise SystemExit("dead_family should stay kill via local dead markers")
if summary_by_topic["dead_family"]["mechanism_failure_memory_status"] not in {"kill", "dead_doc"}:
    raise SystemExit("dead_family should carry dead negative failure memory")

registry_by_family = {entry["family_key"]: entry for entry in family_registry}
if registry_by_family["good_family"]["state"] != "branch":
    raise SystemExit("good_family should be branch in the family registry")
if registry_by_family["blocked_family"]["state"] != "hold":
    raise SystemExit("blocked_family should be hold in the family registry")

budget_items = official_budget.get("items", [])
if len(budget_items) != 1:
    raise SystemExit(f"expected exactly one official budget item, got {len(budget_items)}")
budget_item = budget_items[0]
if budget_item["family_topic"] != "good_family":
    raise SystemExit(f"official budget should only recommend good_family, got {budget_item['family_topic']}")
if budget_item["family_action"] != "branch":
    raise SystemExit(f"official budget should preserve branch action, got {budget_item['family_action']}")
if budget_item["slot_reason"] != "anchor":
    raise SystemExit(f"official budget should keep only the anchor, got {budget_item['slot_reason']}")

blocked_records = [record for record in scored if record.get("family_topic") == "blocked_family"]
if blocked_records:
    raise SystemExit("blocked_family should be removed before local candidate generation")

good_records = [record for record in scored if record.get("family_topic") == "good_family"]
if not good_records:
    raise SystemExit("expected good_family scored records")
good_prior = good_records[0].get("success_prior", {})
if good_prior.get("family_state") != "explore":
    raise SystemExit("expected good_family scored records to use evidence-capped explore state")
if good_prior.get("evidence_ladder_level") != "E2_partial_official":
    raise SystemExit("expected good_family scored records to carry E2 partial-official evidence")
PY

printf 'Alpha family factory test passed.\n'

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-research-governance-core.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

trap cleanup EXIT

FIXTURE_ROOT="$TMP_ROOT/fixture"
mkdir -p "$FIXTURE_ROOT/families"

cat >"$FIXTURE_ROOT/families/local-family.md" <<'EOF'
# Local Family

## Metadata

- Date: `2026-04-24`
- Topic: `local_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Research Contract

- Mechanism: `slow_ratio`
- Data category: `fundamental`
- Idea type: `value_anchor`
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
- Factor risk hypothesis: `Primary risk is value crowding.`
- Kill condition: `Kill after one failed anchor and one failed orthogonal control.`

## Baseline Expression

```text
group_rank(local_signal, industry)
```
EOF

cat >"$FIXTURE_ROOT/families/partial-family.md" <<'EOF'
# Partial Family

## Metadata

- Date: `2026-04-24`
- Topic: `partial_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Research Contract

- Mechanism: `event_gate`
- Data category: `options`
- Idea type: `event_trigger`
- Universe: `TOP3000`
- Liquidity fit: `sparse_event_acceptable`
- Holding frequency: `event`
- Delay: `1`
- Neutralization target: `industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `drop_sparse`
- Pasteurization: `enabled`
- Unit handling: `verify`
- Coverage floor: `70%`
- Freshness floor days: `1`
- Factor risk hypothesis: `Primary risk is sparse event concentration.`
- Kill condition: `Kill after one partial anchor and one partial follow-up both fail.`

## Baseline Expression

```text
trade_when(partial_gate, rank(partial_signal), -1)
```
EOF

cat >"$FIXTURE_ROOT/families/full-family.md" <<'EOF'
# Full Family

## Metadata

- Date: `2026-04-24`
- Topic: `full_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Research Contract

- Mechanism: `cross_sectional_rank`
- Data category: `analyst`
- Idea type: `estimate_revision`
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
- Factor risk hypothesis: `Primary risk is analyst crowding.`
- Kill condition: `Kill after one failed anchor and one failed orthogonal control.`

## Baseline Expression

```text
group_rank(ts_rank(full_signal, 63), industry)
```
EOF

cat >"$FIXTURE_ROOT/families/complex-family.md" <<'EOF'
# Complex Family

## Metadata

- Date: `2026-04-24`
- Topic: `complex_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Research Contract

- Mechanism: `cross_sectional_rank`
- Data category: `fundamental`
- Idea type: `overfit_control`
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
- Factor risk hypothesis: `Primary risk is same-family overfitting.`
- Kill condition: `Kill once this lane exceeds the family complexity budget.`

## Baseline Expression

```text
rank(sig_01)
```

## Variant 1

```text
rank(sig_02)
```

## Variant 2

```text
rank(sig_03)
```

## Variant 3

```text
rank(sig_04)
```

## Variant 4

```text
rank(sig_05)
```

## Variant 5

```text
rank(sig_06)
```

## Variant 6

```text
rank(sig_07)
```
EOF

cd "$PROJECT_ROOT"

python3 - "$PROJECT_ROOT/scripts" "$FIXTURE_ROOT/families" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from complexity_budget_core import build_complexity_budget_report
from research_allocator_core import allocate_family_records
from validation_provenance_core import build_validation_provenance_report
from alpha_mining_core import load_family_docs

family_dir = Path(sys.argv[2])
family_docs = load_family_docs(family_dir, include_dead=True)

complexity = build_complexity_budget_report(family_docs=family_docs)
complexity_by_family = {item["family_key"]: item for item in complexity["items"]}

if complexity["counts"]["pass_count"] != 3 or complexity["counts"]["hold_count"] != 1:
    raise SystemExit(f"unexpected complexity counts: {complexity['counts']}")
if complexity_by_family["complex_family"]["assessment"]["gate_status"] != "hold":
    raise SystemExit("complex_family should be held by the complexity budget")

outcome_memory = [
    {
        "family_key": "partial_family",
        "capture_id": "partial-01",
        "capture_mode": "manual-ui",
        "expression": "trade_when(partial_gate, rank(partial_signal), -1)",
        "evidence_level": "partial_tests",
        "submit_ready": False,
        "failing_gates": [],
    },
    {
        "family_key": "full_family",
        "capture_id": "full-01",
        "capture_mode": "network-api",
        "expression": "group_rank(ts_rank(full_signal, 63), industry)",
        "evidence_level": "full_submission_gates",
        "submit_ready": False,
        "failing_gates": [],
    },
]
family_registry = [
    {"family_key": "local_family", "topics": ["local_family"], "doc_paths": [], "state": "explore", "reason": "local only"},
    {"family_key": "partial_family", "topics": ["partial_family"], "doc_paths": [], "state": "branch", "reason": "partial official"},
    {"family_key": "full_family", "topics": ["full_family"], "doc_paths": [], "state": "branch", "reason": "full gates"},
    {"family_key": "complex_family", "topics": ["complex_family"], "doc_paths": [], "state": "hold", "reason": "too complex"},
]
provenance = build_validation_provenance_report(
    family_docs=family_docs,
    outcome_memory=outcome_memory,
    family_registry=family_registry,
    local_scored_counts={"local_family": 2},
    local_queue_counts={"local_family": 1},
)
provenance_by_family = {item["family_key"]: item for item in provenance["items"]}

if provenance["counts"]["binding_family_count"] != 1 or provenance["counts"]["hold_count"] != 1:
    raise SystemExit(f"unexpected provenance counts: {provenance['counts']}")
if provenance_by_family["local_family"]["assessment"]["strongest_level"] != "local_support":
    raise SystemExit("local_family should be labeled local_support")
if provenance_by_family["partial_family"]["assessment"]["gate_status"] != "hold":
    raise SystemExit("partial_family should remain non-binding hold in provenance")
if provenance_by_family["full_family"]["assessment"]["binding_status"] != "binding":
    raise SystemExit("full_family should be labeled binding")

allocator = allocate_family_records(
    records=[
        {
            "family_key": "alpha_a",
            "field_readiness_gate_status": "pass",
            "account_capability_gate_status": "pass",
            "research_contract_gate_status": "pass",
            "complexity_budget_gate_status": "pass",
            "allocator_state_allowed": True,
            "research_contract_fields": {
                "data_category": "fundamental",
                "mechanism": "slow_ratio",
                "holding_frequency": "slow",
                "idea_type": "value_anchor",
            },
        },
        {
            "family_key": "alpha_b",
            "field_readiness_gate_status": "pass",
            "account_capability_gate_status": "pass",
            "research_contract_gate_status": "pass",
            "complexity_budget_gate_status": "pass",
            "allocator_state_allowed": True,
            "research_contract_fields": {
                "data_category": "fundamental",
                "mechanism": "slow_ratio",
                "holding_frequency": "slow",
                "idea_type": "value_follow_up",
            },
        },
        {
            "family_key": "alpha_c",
            "field_readiness_gate_status": "pass",
            "account_capability_gate_status": "pass",
            "research_contract_gate_status": "pass",
            "complexity_budget_gate_status": "pass",
            "allocator_state_allowed": True,
            "research_contract_fields": {
                "data_category": "analyst",
                "mechanism": "estimate_revision",
                "holding_frequency": "event",
                "idea_type": "analyst_anchor",
            },
        },
        {
            "family_key": "alpha_d",
            "field_readiness_gate_status": "pass",
            "account_capability_gate_status": "pass",
            "research_contract_gate_status": "pass",
            "complexity_budget_gate_status": "hold",
            "allocator_state_allowed": True,
            "research_contract_fields": {
                "data_category": "options",
                "mechanism": "event_gate",
                "holding_frequency": "event",
                "idea_type": "event_anchor",
            },
        },
    ],
    family_limit=3,
)

counts = allocator["counts"]
if counts["selected_primary_count"] != 2 or counts["selected_backfill_count"] != 1 or counts["ineligible_count"] != 1:
    raise SystemExit(f"unexpected allocator counts: {counts}")
if allocator["selected_family_keys"] != ["alpha_a", "alpha_c", "alpha_b"]:
    raise SystemExit(f"unexpected allocator selection order: {allocator['selected_family_keys']}")

items_by_key = {item["family_key"]: item for item in allocator["items"]}
if items_by_key["alpha_b"]["research_allocator_status"] != "selected_backfill":
    raise SystemExit("alpha_b should be upgraded as controlled same-cluster backfill")
if items_by_key["alpha_d"]["research_allocator_status"] != "ineligible":
    raise SystemExit("alpha_d should stay allocator-ineligible")
PY

printf 'Research governance core test passed.\n'

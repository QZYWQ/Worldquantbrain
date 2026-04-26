#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-research-economics-gates.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

trap cleanup EXIT

FIXTURE_ROOT="$TMP_ROOT/fixture"
mkdir -p "$FIXTURE_ROOT/families"

cat >"$FIXTURE_ROOT/families/failed-base-family.md" <<'EOF'
# Failed Base Family

## Metadata

- Date: `2026-04-24`
- Topic: `failed_base_family`
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
- Kill condition: `Kill after one failed anchor and one failed control.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus value exposure review`
- Comparison controls: `compare against one slower ratio control`
- Promotion rule: `promote only after full gate evidence`
- Demotion rule: `demote after failed full-gate check`

## Baseline Expression

```text
group_rank(ts_rank(failed_signal/close, 63), industry)
```
EOF

cat >"$FIXTURE_ROOT/families/retuned-clone-family.md" <<'EOF'
# Retuned Clone Family

## Metadata

- Date: `2026-04-24`
- Topic: `retuned_clone_family`
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
- Kill condition: `Kill after one failed anchor and one failed control.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus value exposure review`
- Comparison controls: `compare against one slower ratio control`
- Promotion rule: `promote only after full gate evidence`
- Demotion rule: `demote after failed full-gate check`

## Baseline Expression

```text
group_rank(ts_rank(failed_signal/close, 84), industry)
```
EOF

cat >"$FIXTURE_ROOT/families/orthogonal-event-family.md" <<'EOF'
# Orthogonal Event Family

## Metadata

- Date: `2026-04-24`
- Topic: `orthogonal_event_family`
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
- Kill condition: `Kill after failed event trigger and failed holdout control.`

## Validation Design

- Primary test period: `P6M`
- Regime slices: `earnings weeks; non-earnings weeks`
- Liquidity slice: `TOP3000 event-capable names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus volatility review`
- Comparison controls: `compare against one no-event control`
- Promotion rule: `promote only after event holdout remains live`
- Demotion rule: `demote after event gate loses support`

## Baseline Expression

```text
trade_when(option_gate>ts_mean(option_gate, 20), group_rank(-event_signal, industry), -1)
```
EOF

cat >"$FIXTURE_ROOT/families/missing-validation-family.md" <<'EOF'
# Missing Validation Family

## Metadata

- Date: `2026-04-24`
- Topic: `missing_validation_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Research Contract

- Mechanism: `slow_ratio`
- Data category: `fundamental`
- Idea type: `missing_validation_control`
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
- Factor risk hypothesis: `Primary risk is missing validation discipline.`
- Kill condition: `Kill if no explicit validation matrix exists.`

## Baseline Expression

```text
group_rank(ts_rank(missing_signal/close, 63), industry)
```
EOF

cd "$PROJECT_ROOT"

python3 - "$PROJECT_ROOT/scripts" "$FIXTURE_ROOT/families" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from alpha_mining_core import load_family_docs
from economic_distinctness_core import build_economic_distinctness_report
from mechanism_failure_memory_core import build_mechanism_failure_memory_report
from research_contract_core import build_research_contract_report
from validation_design_core import build_validation_design_report

family_dir = Path(sys.argv[2])
family_docs = load_family_docs(family_dir, include_dead=True)

validation = build_validation_design_report(family_docs=family_docs)
validation_by_family = {item["family_key"]: item for item in validation["items"]}
if validation["counts"]["pass_count"] != 3 or validation["counts"]["block_count"] != 1:
    raise SystemExit(f"unexpected validation-design counts: {validation['counts']}")
if validation_by_family["missing_validation_family"]["assessment"]["gate_status"] != "block":
    raise SystemExit("missing_validation_family should be blocked by validation design")

research_contract = build_research_contract_report(family_docs=family_docs)
family_registry = [
    {
        "family_key": "failed_base_family",
        "state": "hold",
        "reason": "full-gate failure already observed",
        "failing_gate_histogram": {"LOW_SHARPE": 1},
        "pending_gate_histogram": {},
        "full_gate_outcome_count": 1,
    },
    {
        "family_key": "retuned_clone_family",
        "state": "explore",
        "reason": "candidate clone under review",
        "failing_gate_histogram": {},
        "pending_gate_histogram": {},
        "full_gate_outcome_count": 0,
    },
    {
        "family_key": "orthogonal_event_family",
        "state": "explore",
        "reason": "orthogonal event branch",
        "failing_gate_histogram": {},
        "pending_gate_histogram": {},
        "full_gate_outcome_count": 0,
    },
    {
        "family_key": "missing_validation_family",
        "state": "explore",
        "reason": "missing validation",
        "failing_gate_histogram": {},
        "pending_gate_histogram": {},
        "full_gate_outcome_count": 0,
    },
]

failure_memory = build_mechanism_failure_memory_report(
    family_docs=family_docs,
    family_registry=family_registry,
    research_contract_report=research_contract,
)
failure_by_family = {item["family_key"]: item for item in failure_memory["items"]}
if failure_memory["counts"]["negative_family_count"] != 1:
    raise SystemExit(f"unexpected failure-memory counts: {failure_memory['counts']}")
if failure_by_family["failed_base_family"]["assessment"]["negative_memory_status"] != "hold":
    raise SystemExit("failed_base_family should be remembered as a negative hold cluster")

distinctness = build_economic_distinctness_report(
    family_docs=family_docs,
    research_contract_report=research_contract,
    mechanism_failure_memory_report=failure_memory,
)
distinctness_by_family = {item["family_key"]: item for item in distinctness["items"]}

if distinctness["counts"]["hold_count"] != 1:
    raise SystemExit(f"unexpected economic-distinctness counts: {distinctness['counts']}")
if distinctness_by_family["retuned_clone_family"]["assessment"]["gate_status"] != "hold":
    raise SystemExit("retuned_clone_family should be held as a parameter-only revival")
if distinctness_by_family["retuned_clone_family"]["nearest_negative_family"] != "failed_base_family":
    raise SystemExit("retuned_clone_family should point to failed_base_family as the nearest negative neighbor")
if distinctness_by_family["orthogonal_event_family"]["assessment"]["gate_status"] != "pass":
    raise SystemExit("orthogonal_event_family should pass economic distinctness")
PY

printf 'Research economics gates test passed.\n'

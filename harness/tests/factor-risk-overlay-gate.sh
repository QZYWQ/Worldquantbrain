#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-factor-risk-overlay.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

trap cleanup EXIT

FIXTURE_ROOT="$TMP_ROOT/fixture"
mkdir -p "$FIXTURE_ROOT/families"

cat >"$FIXTURE_ROOT/families/pass-family.md" <<'EOF'
# Pass Family

## Metadata

- Date: `2026-04-24`
- Topic: `pass_family`
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
- Factor risk hypothesis: `Primary risk is value and size crowding inside industries.`
- Kill condition: `Kill after a failed anchor and failed orthogonal control.`

## Validation Design

- Primary test period: `P1Y`
- Regime slices: `recent year; stress regime`
- Liquidity slice: `TOP3000 liquid names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry plus value and size review`
- Comparison controls: `compare against one slower residualized control`
- Promotion rule: `promote only after binding evidence`
- Demotion rule: `demote after failed full-gate evidence`

## Baseline Expression

```text
group_rank(ts_rank(cashflow/cap, 63), industry)
```
EOF

cat >"$FIXTURE_ROOT/families/hold-family.md" <<'EOF'
# Hold Family

## Metadata

- Date: `2026-04-24`
- Topic: `hold_family`
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
- Factor risk hypothesis: `Primary risk is volatility clustering.`
- Kill condition: `Kill after failed event trigger and failed control.`

## Validation Design

- Primary test period: `P6M`
- Regime slices: `earnings weeks; non-earnings weeks`
- Liquidity slice: `TOP3000 event-capable names`
- Subuniverse gate: `must keep subuniverse check green`
- Factor overlay: `industry review only`
- Comparison controls: `compare against one no-event control`
- Promotion rule: `promote only after event holdout remains live`
- Demotion rule: `demote after event gate loses support`

## Baseline Expression

```text
trade_when(option_gate>ts_mean(option_gate, 20), group_rank(-iv_signal, industry), -1)
```
EOF

cat >"$FIXTURE_ROOT/families/block-family.md" <<'EOF'
# Block Family

## Metadata

- Date: `2026-04-24`
- Topic: `block_family`
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
- Factor risk hypothesis: `Primary risk is value crowding.`
- Kill condition: `Kill if no explicit validation matrix exists.`

## Baseline Expression

```text
group_rank(ts_rank(book/cap, 63), industry)
```
EOF

cd "$PROJECT_ROOT"

python3 - "$PROJECT_ROOT/scripts" "$FIXTURE_ROOT/families" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from alpha_mining_core import load_family_docs
from factor_risk_overlay_core import build_factor_risk_overlay_report
from research_contract_core import build_research_contract_report
from validation_design_core import build_validation_design_report

family_dir = Path(sys.argv[2])
family_docs = load_family_docs(family_dir, include_dead=True)
research_contract = build_research_contract_report(family_docs=family_docs)
validation_design = build_validation_design_report(family_docs=family_docs)
report = build_factor_risk_overlay_report(
    family_docs=family_docs,
    research_contract_report=research_contract,
    validation_design_report=validation_design,
)
by_family = {item["family_key"]: item for item in report["items"]}

if report["counts"]["pass_count"] != 1 or report["counts"]["hold_count"] != 1 or report["counts"]["block_count"] != 1:
    raise SystemExit(f"unexpected factor-risk-overlay counts: {report['counts']}")
if by_family["pass_family"]["assessment"]["gate_status"] != "pass":
    raise SystemExit("pass_family should pass factor-risk-overlay")
if by_family["hold_family"]["assessment"]["gate_status"] != "hold":
    raise SystemExit("hold_family should hold on factor-risk-overlay")
if by_family["block_family"]["assessment"]["gate_status"] != "block":
    raise SystemExit("block_family should block on factor-risk-overlay")
PY

printf 'Factor risk overlay gate test passed.\n'

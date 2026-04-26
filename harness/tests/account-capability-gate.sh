#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-account-capability.XXXXXX")"

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
ARTIFACT_ROOT="$TMP_ROOT/artifacts"
RUN_ID="fixture-account-capability"

mkdir -p "$FIXTURE_ROOT/families" "$FIXTURE_ROOT/session-briefs" "$ARTIFACT_ROOT/$RUN_ID"

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
- Factor risk hypothesis: `Value and size exposure need explicit control.`
- Kill condition: `Kill after one failed anchor and one failed control.`
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
- Factor risk hypothesis: `Sparse event concentration is the main risk.`
- Kill condition: `Hold until local scope evidence exists.`
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

- Mechanism: `broken_contract`
- Idea type: `missing_scope`
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
- Factor risk hypothesis: `Scope is incomplete.`
- Kill condition: `Block until scope is fully specified.`
EOF

cat >"$FIXTURE_ROOT/session-briefs/data-fields-USA-TOP3000.fixture.network-response" <<'EOF'
{
  "count": 2,
  "results": [
    {
      "id": "fundamental_signal",
      "region": "USA",
      "delay": 1,
      "universe": "TOP3000",
      "dataset": {"id": "fundamental"},
      "category": {"id": "fundamental"},
      "coverage": 0.98,
      "alphaCount": 12,
      "userCount": 3
    },
    {
      "id": "analyst_signal",
      "region": "USA",
      "delay": 1,
      "universe": "TOP3000",
      "dataset": {"id": "analyst4"},
      "category": {"id": "analyst"},
      "coverage": 0.95,
      "alphaCount": 8,
      "userCount": 2
    }
  ]
}
EOF

cd "$PROJECT_ROOT"

python3 - "$FIXTURE_ROOT" "$ARTIFACT_ROOT/$RUN_ID" <<'PY'
import json
import sys
from pathlib import Path

fixture_root = Path(sys.argv[1])
output_root = Path(sys.argv[2])
sys.path.insert(0, str((Path.cwd() / 'scripts').resolve()))

from alpha_mining_core import load_family_docs
from research_contract_core import build_research_contract_report
from account_capability_core import build_account_capability_report, render_account_capability_md

family_docs = load_family_docs(fixture_root / 'families', include_dead=True)
contract_report = build_research_contract_report(family_docs=family_docs)
report = build_account_capability_report(
    family_docs=family_docs,
    research_contract_report=contract_report,
    session_brief_root=fixture_root / 'session-briefs',
)
(output_root / 'manifest.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
    encoding='utf-8',
)
(output_root / 'manifest.md').write_text(render_account_capability_md(report) + '\n', encoding='utf-8')
PY

BUNDLE_ROOT="$ARTIFACT_ROOT/$RUN_ID"
assert_file_exists "$BUNDLE_ROOT/manifest.json"
assert_file_exists "$BUNDLE_ROOT/manifest.md"

python3 harness/lib/content-validator.py --mode account-capability-json --path "$BUNDLE_ROOT/manifest.json"

python3 - "$BUNDLE_ROOT/manifest.json" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
counts = manifest.get('counts', {})
if counts.get('family_count') != 3:
    raise SystemExit(f"expected 3 families, got {counts}")
if counts.get('pass_count') != 1 or counts.get('hold_count') != 1 or counts.get('block_count') != 1:
    raise SystemExit(f"unexpected account-capability counts: {counts}")

items = {item['family_key']: item for item in manifest.get('items', [])}
if items['pass_family']['assessment']['gate_status'] != 'pass':
    raise SystemExit('pass_family should pass account capability')
if items['hold_family']['assessment']['gate_status'] != 'hold':
    raise SystemExit('hold_family should hold account capability')
if items['block_family']['assessment']['gate_status'] != 'block':
    raise SystemExit('block_family should block account capability')
if items['hold_family']['required_scope'].get('data_category') != 'options':
    raise SystemExit('hold_family should require options scope')
PY

printf 'Account capability gate test passed.\n'

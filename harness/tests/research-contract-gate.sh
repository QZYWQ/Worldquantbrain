#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-research-contracts.XXXXXX")"

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
PUBLISH_ROOT="$TMP_ROOT/published"
RUN_ID="fixture-research-contracts"

mkdir -p "$FIXTURE_ROOT/families"

cat >"$FIXTURE_ROOT/families/good-family.md" <<'EOF'
# Good Family

## Metadata

- Date: `2026-04-24`
- Topic: `good_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Good family should pass the research-contract gate.

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
- Factor risk hypothesis: `Primary risk is value and size; keep industry grouping explicit.`
- Kill condition: `Kill this lane if the raw ratio anchor cannot survive after one materially different control.`

## Baseline Expression

```text
ts_rank(group_rank(good_signal, industry), 63)
```
EOF

cat >"$FIXTURE_ROOT/families/missing-contract-family.md" <<'EOF'
# Missing Contract Family

## Metadata

- Date: `2026-04-24`
- Topic: `missing_contract_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This family is missing the contract section and should be blocked.

## Baseline Expression

```text
rank(missing_signal)
```
EOF

cat >"$FIXTURE_ROOT/families/fast-delay-mismatch-family.md" <<'EOF'
# Fast Delay Mismatch Family

## Metadata

- Date: `2026-04-24`
- Topic: `fast_delay_mismatch_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This family should be held because the holding frequency conflicts with the delay.

## Research Contract

- Mechanism: `event_gate`
- Data category: `price_volume`
- Idea type: `fast_reaction`
- Universe: `TOP3000`
- Liquidity fit: `broad_liquid`
- Holding frequency: `intraday`
- Delay: `1`
- Neutralization target: `industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `drop_sparse`
- Pasteurization: `enabled`
- Unit handling: `verify`
- Coverage floor: `70%`
- Freshness floor days: `1`
- Factor risk hypothesis: `Primary risk is short-term liquidity shock.`
- Kill condition: `Kill if the fast branch cannot be expressed with the correct delay settings.`

## Baseline Expression

```text
ts_rank(group_rank(fast_signal, industry), 5)
```
EOF

cd "$PROJECT_ROOT"

RUN_OUTPUT="$(python3 ./scripts/research_contract_gate.py \
  --family-dir "$FIXTURE_ROOT/families" \
  --artifact-root "$ARTIFACT_ROOT" \
  --publish-root "$PUBLISH_ROOT" \
  --run-id "$RUN_ID")"

printf '%s\n' "$RUN_OUTPUT" | grep -Fq "Run bundle:" || {
  printf 'Expected run output to print the run bundle path.\nActual output:\n%s\n' "$RUN_OUTPUT" >&2
  exit 1
}

BUNDLE_ROOT="$ARTIFACT_ROOT/$RUN_ID"
assert_file_exists "$BUNDLE_ROOT/manifest.json"
assert_file_exists "$BUNDLE_ROOT/manifest.md"
assert_file_exists "$PUBLISH_ROOT/$RUN_ID.json"
assert_file_exists "$PUBLISH_ROOT/$RUN_ID.md"

python3 harness/lib/content-validator.py --mode research-contract-json --path "$BUNDLE_ROOT/manifest.json"

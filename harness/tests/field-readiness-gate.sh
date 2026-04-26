#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-field-readiness.XXXXXX")"

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
RUN_ID="fixture-field-readiness"

mkdir -p "$FIXTURE_ROOT/families" "$FIXTURE_ROOT/field-search-packs"

cat >"$FIXTURE_ROOT/families/good-family.md" <<'EOF'
# Good Family

## Metadata

- Date: `2026-04-24`
- Topic: `good_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Good family should pass the readiness gate.

## Baseline Expression

```text
group_rank(ts_rank(good_signal, 63), industry)
```
EOF

cat >"$FIXTURE_ROOT/families/blocked-family.md" <<'EOF'
# Blocked Family

## Metadata

- Date: `2026-04-24`
- Topic: `blocked_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This family is unusable on the current account.

## Notes

- Invalid data field `blocked_signal`

## Baseline Expression

```text
rank(blocked_signal)
```
EOF

cat >"$FIXTURE_ROOT/families/low-coverage-family.md" <<'EOF'
# Low Coverage Family

## Metadata

- Date: `2026-04-24`
- Topic: `low_coverage_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This family should be held because usable coverage is too low.

## Baseline Expression

```text
rank(low_cov_signal)
```
EOF

cat >"$FIXTURE_ROOT/field-search-packs/good-pack.md" <<'EOF'
# Good Pack

## Metadata

- Date: `2026-04-24`
- Topic: `good_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `good_signal` | `dataset` | Good signal | `100%` coverage | low |

## Coverage And Quality Checks

- Coverage: solid
- Missingness: reviewed
- Region / delay compatibility: USA / D1 / TOP3000
- Field type: matrix

## Baseline Expression Ideas

1. `group_rank(ts_rank(good_signal, 63), industry)`

## Next Action

- Which field should be tried first? `good_signal`
EOF

cat >"$FIXTURE_ROOT/field-search-packs/blocked-pack.md" <<'EOF'
# Blocked Pack

## Metadata

- Date: `2026-04-24`
- Topic: `blocked_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `blocked_signal` | `dataset` | Blocked signal | `100%` coverage | low |

## Coverage And Quality Checks

- Coverage: still blocked by account usability
- Missingness: reviewed
- Region / delay compatibility: USA / D1 / TOP3000
- Field type: matrix

## Baseline Expression Ideas

1. `rank(blocked_signal)`

## Next Action

- Which field should be tried first? `blocked_signal`
EOF

cat >"$FIXTURE_ROOT/field-search-packs/low-coverage-pack.md" <<'EOF'
# Low Coverage Pack

## Metadata

- Date: `2026-04-24`
- Topic: `low_coverage_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `low_cov_signal` | `dataset` | Thin field | `52%` coverage | low |

## Coverage And Quality Checks

- Coverage: thin
- Missingness: needs repair
- Region / delay compatibility: USA / D1 / TOP3000
- Field type: matrix

## Baseline Expression Ideas

1. `rank(low_cov_signal)`

## Next Action

- Which field should be tried first? `low_cov_signal`
EOF

cd "$PROJECT_ROOT"

RUN_OUTPUT="$(python3 ./scripts/field_readiness_gate.py \
  --family-dir "$FIXTURE_ROOT/families" \
  --field-search-pack-dir "$FIXTURE_ROOT/field-search-packs" \
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

python3 harness/lib/content-validator.py --mode field-readiness-json --path "$BUNDLE_ROOT/manifest.json"

python3 - "$BUNDLE_ROOT/manifest.json" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
counts = manifest["counts"]
if counts["family_count"] != 3:
    raise SystemExit(f"expected 3 families, got {counts['family_count']}")
if counts["pass_count"] != 1 or counts["hold_count"] != 1 or counts["block_count"] != 1:
    raise SystemExit(f"unexpected readiness counts: {counts}")

items = {item["family_key"]: item for item in manifest["items"]}
if items["good_family"]["assessment"]["gate_status"] != "pass":
    raise SystemExit("good_family should pass")
if items["blocked_family"]["assessment"]["gate_status"] != "block":
    raise SystemExit("blocked_family should block")
if items["low_coverage_family"]["assessment"]["gate_status"] != "hold":
    raise SystemExit("low_coverage_family should hold")
PY

printf 'Field readiness gate test passed.\n'

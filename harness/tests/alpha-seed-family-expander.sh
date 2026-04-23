#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-alpha-seed-family-expander.XXXXXX")"
EXPANDER_RUN_ID="test-alpha-seed-family-expander-$$"
DAILY_RUN_ID="test-alpha-seed-family-expander-daily-$$"

EXPANDER_ARTIFACT_ROOT="${PROJECT_ROOT}/harness/artifacts/alpha-seed-expander"
EXPANDER_RUN_ROOT="${EXPANDER_ARTIFACT_ROOT}/${EXPANDER_RUN_ID}"
EXPANDER_JSON_PATH="${PROJECT_ROOT}/runs/learning-loops/${EXPANDER_RUN_ID}.json"
EXPANDER_MD_PATH="${PROJECT_ROOT}/runs/learning-loops/${EXPANDER_RUN_ID}.md"

DAILY_ARTIFACT_ROOT="${PROJECT_ROOT}/harness/artifacts/alpha-daily"
DAILY_RUN_ROOT="${DAILY_ARTIFACT_ROOT}/${DAILY_RUN_ID}"
DAILY_JSON_PATH="${PROJECT_ROOT}/runs/learning-loops/${DAILY_RUN_ID}.json"
DAILY_MD_PATH="${PROJECT_ROOT}/runs/learning-loops/${DAILY_RUN_ID}.md"

cleanup() {
  rm -rf "$TMP_ROOT"
  rm -rf "$EXPANDER_RUN_ROOT"
  rm -rf "$DAILY_RUN_ROOT"
  rm -f "$EXPANDER_JSON_PATH" "$EXPANDER_MD_PATH" "$DAILY_JSON_PATH" "$DAILY_MD_PATH"
}

trap cleanup EXIT

assert_file_exists() {
  local path="$1"
  if [ ! -f "$path" ]; then
    printf 'Expected file to exist: %s\n' "$path" >&2
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

for path in \
  "$EXPANDER_RUN_ROOT" \
  "$EXPANDER_JSON_PATH" \
  "$EXPANDER_MD_PATH" \
  "$DAILY_RUN_ROOT" \
  "$DAILY_JSON_PATH" \
  "$DAILY_MD_PATH"
do
  assert_path_absent "$path"
done

FIXTURE_ROOT="$TMP_ROOT/fixture"
mkdir -p \
  "$FIXTURE_ROOT/families" \
  "$FIXTURE_ROOT/field-search-packs" \
  "$FIXTURE_ROOT/captures" \
  "$FIXTURE_ROOT/candidate-batches" \
  "$FIXTURE_ROOT/candidate-checks"

cat >"$FIXTURE_ROOT/families/01-primary-analyst-eps-family.md" <<'EOF'
# Primary Analyst EPS Family

## Metadata

- Date: `2026-04-23`
- Topic: `primary_analyst_eps_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This is the primary analyst-EPS seed-family lane for the daily expander test.

## Confirmed Or Assumed Inputs

- confirmed field: `est_eps`
- confirmed field: `close`
- confirmed grouping: `industry`

## Decision

- Explore: keep this family open while the primary analyst-EPS lane remains the first seed branch.

## Baseline Expression

```text
group_rank(ts_rank(est_eps/close, 60), industry)
```

## Variant 1

```text
group_rank(ts_rank(est_eps/close, 20), industry)
```
EOF

cat >"$FIXTURE_ROOT/families/02-secondary-analyst-qfv4-family.md" <<'EOF'
# Secondary Analyst QFV4 Family

## Metadata

- Date: `2026-04-23`
- Topic: `secondary_analyst_qfv4_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This is the secondary quarterly sibling family for the same expectation-drift thesis.

## Confirmed Or Assumed Inputs

- confirmed field: `anl4_qfv4_median_eps`
- confirmed field: `close`
- confirmed grouping: `industry`

## Decision

- Explore: keep this family as the secondary sibling control.

## Baseline Expression

```text
group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)
```

## Variant 1

```text
group_rank(ts_rank(anl4_qfv4_eps_mean/close, 60), industry)
```
EOF

cat >"$FIXTURE_ROOT/families/03-hold-event-option-family.md" <<'EOF'
# Hold Event Option Family

## Metadata

- Date: `2026-04-23`
- Topic: `hold_event_option_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This family should stay out of the daily priority shortlist.

## Decision

- Hold: keep this family paused until a materially different thesis appears.

## Baseline Expression

```text
trade_when(option_gate > ts_mean(option_gate, 20), group_rank(-option_signal, industry), -1)
```
EOF

cat >"$FIXTURE_ROOT/families/04-kill-dead-family.md" <<'EOF'
# Kill Dead Family

## Metadata

- Date: `2026-04-23`
- Topic: `kill_dead_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This dead family should not appear in any priority shortlist.

## Decision

- Kill the dead family and do not continue polishing it.

## Baseline Expression

```text
rank(kill_signal)
```
EOF

cat >"$FIXTURE_ROOT/field-search-packs/01-primary-analyst-eps-pack.md" <<'EOF'
# Primary Analyst EPS Field Search Pack

## Metadata

- Date: `2026-04-23`
- Topic: `primary_analyst_eps_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This is the primary seed family and should be the first item in the shortlist.

## Why This Could Matter

- It is the clearest analyst-EPS seed lane for the current test fixture.
- It has the simplest confirmable analyst-to-price baseline.
- It should outrank the sibling control family in the expander output.

## Data Explorer Search Terms

- Primary terms: `earnings per share`, `eps`, `analyst recommendation`
- Synonyms: `analyst estimate`, `estimate revision`
- Abbreviations: `eps`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `est_eps` | `analyst` | Primary seed field for this test | `100%` coverage | `40` visible alphas |
| `close` | `pv1` | Price normalization denominator | `100%` coverage | baseline denominator only |
| `analyst_reco` | `analyst` | Backup control for the same family | `95%` coverage | `55` visible alphas |

## Coverage And Quality Checks

- Coverage:
  Keep the first batch simple and readable.
- Missingness:
  Do not add repair logic to this test fixture.
- Region / delay compatibility:
  USA / D1 / TOP3000.
- Field type:
  Matrix.

## Baseline Expression Ideas

1. `group_rank(ts_rank(est_eps/close, 60), industry)`
2. `group_rank(ts_rank(est_eps/close, 20), industry)`
3. `group_rank(ts_rank(est_eps/close, 120), industry)`

## Next Action

- Which field should be tried first? `est_eps`
- Which baseline expression should be simulated first? `group_rank(ts_rank(est_eps/close, 60), industry)`
- Which 2-3 same-family variants should follow? `20d` and `120d` windows.
EOF

cat >"$FIXTURE_ROOT/field-search-packs/02-secondary-analyst-qfv4-pack.md" <<'EOF'
# Secondary Analyst QFV4 Field Search Pack

## Metadata

- Date: `2026-04-23`
- Topic: `secondary_analyst_qfv4_family`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

This is the secondary control family and should come after the primary analyst-EPS family in the shortlist.

## Why This Could Matter

- It gives the expander a clean secondary branch.
- It should stay behind the primary analyst-EPS lane in the priority order.

## Data Explorer Search Terms

- Primary terms: `qfv4 eps`, `estimate median`
- Synonyms: `quarterly analyst estimate`, `estimate mean`
- Abbreviations: `qfv4`, `eps`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `anl4_qfv4_median_eps` | `analyst4` | Secondary seed control for this test | `100%` coverage | `36` visible alphas |
| `anl4_qfv4_eps_mean` | `analyst4` | Sibling control for the same family | `100%` coverage | `32` visible alphas |

## Coverage And Quality Checks

- Coverage:
  Keep this lane as a secondary control only.
- Missingness:
  Keep the fixture local and deterministic.
- Region / delay compatibility:
  USA / D1 / TOP3000.
- Field type:
  Matrix.

## Baseline Expression Ideas

1. `group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)`
2. `group_rank(ts_rank(anl4_qfv4_eps_mean/close, 60), industry)`
3. `group_rank(ts_rank(anl4_qfv4_median_eps/close, 120), industry)`

## Next Action

- Which field should be tried first? `anl4_qfv4_median_eps`
- Which baseline expression should be simulated first? `group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)`
- Which 2-3 same-family variants should follow? `qfv4_eps_mean` and `120d` window.
EOF

python3 ./scripts/alpha_seed_family_expander.py \
  --family-dir "$FIXTURE_ROOT/families" \
  --field-search-pack-dir "$FIXTURE_ROOT/field-search-packs" \
  --artifact-root "$EXPANDER_ARTIFACT_ROOT" \
  --run-id "$EXPANDER_RUN_ID"

assert_file_exists "$EXPANDER_RUN_ROOT/manifest.json"
assert_file_exists "$EXPANDER_RUN_ROOT/manifest.md"
assert_file_exists "$EXPANDER_JSON_PATH"
assert_file_exists "$EXPANDER_MD_PATH"

python3 - "$EXPANDER_RUN_ROOT/manifest.json" <<'PY'
import json
import sys
from pathlib import Path


def shortlist_keys(raw):
    keys = []
    if not isinstance(raw, list):
        return keys
    for item in raw:
        if isinstance(item, str):
            keys.append(item)
        elif isinstance(item, dict):
            key = item.get("family_key") or item.get("topic") or item.get("family") or item.get("key")
            if key is not None:
                keys.append(str(key))
    return keys


manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
priority_keys = [str(item) for item in manifest.get("priority_family_keys", [])]
if priority_keys[:2] != ["primary_analyst_eps_family", "secondary_analyst_qfv4_family"]:
    raise SystemExit(
        "Unexpected priority_family_keys prefix: "
        f"{priority_keys[:2]!r}"
    )

shortlist = shortlist_keys(manifest.get("shortlist"))
if shortlist[:2] != ["primary_analyst_eps_family", "secondary_analyst_qfv4_family"]:
    raise SystemExit(
        "Unexpected shortlist prefix: "
        f"{shortlist[:2]!r}"
    )
PY

python3 ./scripts/alpha_daily_runner.py \
  --dry-run \
  --family-priority-file "$EXPANDER_RUN_ROOT/manifest.json" \
  --family-dir "$FIXTURE_ROOT/families" \
  --capture-dir "$FIXTURE_ROOT/captures" \
  --candidate-batch-dir "$FIXTURE_ROOT/candidate-batches" \
  --candidate-check-dir "$FIXTURE_ROOT/candidate-checks" \
  --artifact-root "$DAILY_ARTIFACT_ROOT" \
  --run-id "$DAILY_RUN_ID" \
  --family-limit 2

assert_file_exists "$DAILY_RUN_ROOT/manifest.json"
assert_file_exists "$DAILY_RUN_ROOT/manifest.md"
assert_file_exists "$DAILY_JSON_PATH"
assert_file_exists "$DAILY_MD_PATH"

python3 - "$DAILY_JSON_PATH" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
selected_keys = [str(row.get("family_key") or "") for row in manifest.get("selected_families", [])]
if selected_keys != ["primary_analyst_eps_family", "secondary_analyst_qfv4_family"]:
    raise SystemExit(
        "Daily runner did not honor the priority file order: "
        f"{selected_keys!r}"
    )
PY

printf 'Alpha seed family expander test passed.\n'

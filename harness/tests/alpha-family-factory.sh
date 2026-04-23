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
mkdir -p "$FIXTURE_ROOT/families" "$FIXTURE_ROOT/captures"

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
scored = [json.loads(line) for line in (root / "scored.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

if manifest["counts"]["family_count"] != 3:
    raise SystemExit(f"expected 3 selected families, got {manifest['counts']['family_count']}")
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

topics = {entry["topic"] for entry in family_summary}
expected_topics = {"good_family", "blocked_family", "dead_family"}
if topics != expected_topics:
    raise SystemExit(f"family summary topics mismatch: {sorted(topics)}")
if "buzz_family" in topics:
    raise SystemExit("buzz_family should be removed by the success policy hard excludes")

summary_by_topic = {entry["topic"]: entry for entry in family_summary}
if summary_by_topic["good_family"]["action"] != "branch":
    raise SystemExit("good_family should stay in branch")
if summary_by_topic["blocked_family"]["action"] != "hold":
    raise SystemExit("blocked_family should move to hold after failed official gates")
if summary_by_topic["dead_family"]["action"] != "kill":
    raise SystemExit("dead_family should stay kill via local dead markers")

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
if not blocked_records:
    raise SystemExit("expected blocked_family scored records")
blocked_hard = [
    record
    for record in blocked_records
    if record.get("success_prior", {}).get("hard_blocked")
    and float(record.get("success_prior", {}).get("failure_similarity", 0.0)) >= 0.99
]
if not blocked_hard:
    raise SystemExit("expected blocked_family to carry hard-blocked priors from failed official evidence")

good_records = [record for record in scored if record.get("family_topic") == "good_family"]
if not good_records:
    raise SystemExit("expected good_family scored records")
if good_records[0].get("success_prior", {}).get("family_state") != "branch":
    raise SystemExit("expected good_family branch enrichment on scored records")
PY

printf 'Alpha family factory test passed.\n'

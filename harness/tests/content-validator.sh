#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

cd "$PROJECT_ROOT"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

valid_json="${tmpdir}/valid-candidate-batch.json"
invalid_json="${tmpdir}/invalid-candidate-batch.json"

cat >"$valid_json" <<'EOF'
{
  "candidates": [
    {
      "name": "baseline",
      "delay": 1,
      "sharpe": 1.64,
      "fitness": 1.03,
      "turnover": 0.1732,
      "max_weight": null,
      "max_weight_check": "PASS",
      "self_corr": null,
      "self_corr_check": "PASS",
      "subuniverse_pass": true,
      "test_period_pass": null,
      "test_period_observation": "Official alpha check did not emit a boolean; test slice stayed positive but weak.",
      "notes": "Official check endpoints resolved concentration and self-correlation, but not a numeric max weight."
    }
  ]
}
EOF

cat >"$invalid_json" <<'EOF'
{
  "candidates": [
    {
      "name": "missing-fallback",
      "delay": 1,
      "sharpe": 1.64,
      "fitness": 1.03,
      "turnover": 0.1732,
      "max_weight": null,
      "self_corr": null,
      "subuniverse_pass": true,
      "test_period_pass": null,
      "notes": "This batch forgot to explain unavailable optional fields."
    }
  ]
}
EOF

python3 harness/lib/content-validator.py --mode candidate-batch-json --path "$valid_json"

if python3 harness/lib/content-validator.py --mode candidate-batch-json --path "$invalid_json"; then
  echo "content-validator should reject candidate batches that omit fallback explanations" >&2
  exit 1
fi

printf 'Harness content validator test passed.\n'

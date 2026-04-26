#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

cd "$PROJECT_ROOT"

bash -n ./harness/init.sh ./harness/coding-session.sh ./harness/run-local-alpha-loop.sh ./harness/lib/*.sh ./harness/tests/*.sh
python3 -m py_compile harness/lib/*.py

tests=(
  "codex-app-readiness.sh"
  "surface-contract.sh"
  "verification-registry.sh"
  "content-validator.sh"
  "field-readiness-gate.sh"
  "account-capability-gate.sh"
  "research-contract-gate.sh"
  "evidence-ladder-gate.sh"
  "research-governance-core.sh"
  "research-economics-gates.sh"
  "factor-risk-overlay-gate.sh"
  "alpha-family-factory.sh"
  "alpha-success-core.sh"
  "alpha-daily-runner.sh"
  "alpha-seed-family-expander.sh"
  "local-alpha-loop-preflight.sh"
  "local-alpha-loop.sh"
  "read-only-parallel.sh"
  "read-only-surface.sh"
  "module-boundaries.sh"
  "runtime-state.sh"
  "official-cycle-default.sh"
  "cycle-lifecycle.sh"
  "resume-brief.sh"
  "session-open.sh"
  "bootstrap-warning.sh"
  "smoke.sh"
  "cycle-close-report.sh"
  "learning-loop.sh"
  "cycle-config.sh"
  "hardening.sh"
)

for test_name in "${tests[@]}"; do
  test_path="${SCRIPT_DIR}/${test_name}"
  printf '== RUN %s ==\n' "./harness/tests/${test_name}"
  bash "${test_path}"
done

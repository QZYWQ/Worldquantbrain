#!/usr/bin/env bash
set -euo pipefail

# Conceptual 15-minute scout scaffold.
#
# This script does not call the live WorldQuant API unless LIVE_EXECUTION=1
# is explicitly set by the operator.
#
# It is meant to sit on top of the existing local helpers:
# - scripts/alpha_batch_miner.py
# - scripts/candidate_scorecard.py
# - scripts/research_queue_builder.py
# - scripts/alpha_family_factory.py
# - scripts/worldquant_alpha_report.py
# - scripts/alpha_daily_runner.py

FIELD="${1:-}"
if [[ -z "${FIELD}" ]]; then
  echo "usage: $0 <verified-field-name>" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATE="$(date +%F)"
SLUG="$(echo "${FIELD}" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9_')"
WORK="${ROOT}/.lite-scout/${DATE}-${SLUG}"
RESULT="${ROOT}/runs/research-contracts/${DATE}-${SLUG}-lite-prescreen-results.md"
mkdir -p "${WORK}"

S1_DISTINCTNESS_MIN="${S1_DISTINCTNESS_MIN:-0.60}"
S1_SIGNAL_MIN="${S1_SIGNAL_MIN:-0.40}"
S0_TEST_SHARPE_MIN="${S0_TEST_SHARPE_MIN:-0.50}"
S0_FITNESS_MIN="${S0_FITNESS_MIN:-0.00}"
LIVE_EXECUTION="${LIVE_EXECUTION:-0}"

cat > "${WORK}/settings.json" <<JSON
{
  "instrumentType": "EQUITY",
  "region": "USA",
  "universe": "TOP3000",
  "delay": 1,
  "decay": 0,
  "neutralization": "INDUSTRY",
  "truncation": 0.08,
  "pasteurization": "ON",
  "unitHandling": "VERIFY",
  "nanHandling": "ON",
  "language": "FASTEXPR",
  "visualization": false
}
JSON

BASELINE="ts_rank(${FIELD}, 60)"
SIGN_FLIP="-ts_rank(${FIELD}, 60)"

# run_s0_param_scan()
# 对给定字段执行 6 组轻量参数扫描 (Decay × Neutralization)
# 参数: $1 = 字段名
# 输出: 全局变量 BEST_TEST_SHARPE, BEST_DECAY, BEST_NEUTRALIZATION
run_s0_param_scan() {
  local field="$1"
  local decays=(20 60 120)
  local neutralizations=("" "Market")

  BEST_TEST_SHARPE=-999
  BEST_DECAY=60
  BEST_NEUTRALIZATION=""

  for decay in "${decays[@]}"; do
    for neut in "${neutralizations[@]}"; do
      local expression="ts_rank(${field}, ${decay})"

      # PLACEHOLDER: 提交单次 S0 基线模拟
      # result=$(submit_simulation "$expression" "$neut")
      # parse_result "$result"  # 提取 TEST Sharpe

      echo "[LITE SCAN] Decay=${decay} Neut=${neut:-None} Expr=${expression}"

      # PLACEHOLDER: 比较并更新最佳值
      # if [ "$test_sharpe" -gt "$BEST_TEST_SHARPE" ]; then
      #     BEST_TEST_SHARPE=$test_sharpe
      #     BEST_DECAY=$decay
      #     BEST_NEUTRALIZATION=$neut
      # fi
    done
  done

  echo "[LITE SCAN] Best combo: Decay=${BEST_DECAY} Neut=${BEST_NEUTRALIZATION:-None} Sharpe=${BEST_TEST_SHARPE}"
}

# Step 1: S-1 proxy.
# TODO: verify the field in Data Explorer and compute distinctness / signal_presence.
# If the field is not confirmed, write a pending_verification note and exit.

# Step 2: Build the S0 controls.
if [[ "${LITE_PARAM_SCAN:-1}" -eq 1 ]]; then
  echo "[LITE] Running 6-combo param scan for S0..."
  run_s0_param_scan "${FIELD}"
  ACTIVE_DECAY="${BEST_DECAY}"
  ACTIVE_NEUTRALIZATION="${BEST_NEUTRALIZATION}"
  echo "[LITE] Using best scanned combo for downstream sign-flip checks: Decay=${ACTIVE_DECAY} Neut=${ACTIVE_NEUTRALIZATION:-None}"
else
  echo "[LITE] Running single baseline S0 (legacy mode)..."
  ACTIVE_DECAY=60
  ACTIVE_NEUTRALIZATION=""
fi

BASELINE="ts_rank(${FIELD}, ${ACTIVE_DECAY})"
SIGN_FLIP="-ts_rank(${FIELD}, ${ACTIVE_DECAY})"

printf '%s\n' "${BASELINE}" > "${WORK}/alphas.txt"
printf '%s\n' "${SIGN_FLIP}" >> "${WORK}/alphas.txt"

if [[ "${LIVE_EXECUTION}" == "1" ]]; then
  # Step 3: Live execution placeholder.
  # Fill this command only when live API use is explicitly allowed.
  # python3 "${ROOT}/scripts/worldquant_alpha_report.py" \
  #   --input "${WORK}/alphas.txt" \
  #   --settings "${WORK}/settings.json" \
  #   --output "${WORK}/worldquant_alpha_report.md"
  :
else
  cat > "${WORK}/dry-run.md" <<DRYRUN
# Lite scout dry run

- Field: ${FIELD}
- S-1 distinctness minimum: ${S1_DISTINCTNESS_MIN}
- S-1 signal minimum: ${S1_SIGNAL_MIN}
- S0 TEST Sharpe floor: ${S0_TEST_SHARPE_MIN}
- S0 Fitness floor: ${S0_FITNESS_MIN}
- LITE param scan: ${LITE_PARAM_SCAN:-1}
- Active scan decay: ${ACTIVE_DECAY}
- Active scan neutralization: ${ACTIVE_NEUTRALIZATION:-None}
- Baseline: ${BASELINE}
- Sign flip: ${SIGN_FLIP}
- Live execution: ${LIVE_EXECUTION}
DRYRUN
  cp "${WORK}/dry-run.md" "${RESULT}"
  echo "Wrote ${RESULT}"
fi

# Step 4: Cleanup placeholder.
# Copy the final note to runs/research-contracts, then remove ${WORK}.
# The scaffold intentionally leaves cleanup explicit so no scout is orphaned.

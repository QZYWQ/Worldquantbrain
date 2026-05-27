#!/usr/bin/env bash
set -eu

PROJECT_ROOT="/Users/zpdedn/Documents/project/Worldquantbrain"
OUT_DIR="${PROJECT_ROOT}/runs/research-queues/2026-05-23-near-pass-rescue"
LOG_FILE="${OUT_DIR}/run.log"

cd "${PROJECT_ROOT}"
printf '\n=== near-pass rescue launched at %s ===\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "${LOG_FILE}"
exec >> "${LOG_FILE}" 2>&1
exec python3 -u "${PROJECT_ROOT}/runs/research-queues/2026-05-23-near-pass-rescue.py"

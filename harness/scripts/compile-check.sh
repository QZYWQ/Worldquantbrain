#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TARGET="${1:-.}"

if [[ ! -e "${TARGET}" ]]; then
  echo "compile-check: path not found: ${TARGET}" >&2
  exit 2
fi

PYTHONPATH="${ROOT}/harness/lib${PYTHONPATH:+:${PYTHONPATH}}" python3 - "${TARGET}" <<'PY'
from __future__ import annotations

import sys
from pathlib import Path

from compiler import compile_alpha

target = Path(sys.argv[1]).expanduser().resolve()
if target.is_file():
    files = [target]
else:
    files = sorted(target.rglob("*.expr"))

if not files:
    print(f"compile-check: no .expr files found under {target}")
    raise SystemExit(0)

valid_count = 0
invalid_count = 0

for path in files:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        invalid_count += 1
        print(f"FAIL {path} | read_error={exc}")
        continue

    result = compile_alpha(text)
    warnings = result.get("warnings") or []
    status = "OK" if result.get("valid") else "FAIL"
    warning_text = f" warnings={len(warnings)}" if warnings else ""
    if result.get("valid"):
        valid_count += 1
        print(f"{status} {path}{warning_text}")
    else:
        invalid_count += 1
        print(f"{status} {path} | error={result.get('error')}{warning_text}")

print(
    f"compile-check summary total={len(files)} valid={valid_count} invalid={invalid_count} target={target}"
)
raise SystemExit(0 if invalid_count == 0 else 1)
PY

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wqb-harness-surface-contract.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}

trap cleanup EXIT

cp -R "$PROJECT_ROOT" "$TMP_ROOT/project"
PROJECT_COPY="$TMP_ROOT/project"

surface_contract="$PROJECT_COPY/harness/project-surfaces.json"
gitignore_path="$PROJECT_COPY/.gitignore"

[ -f "$surface_contract" ] || {
  printf 'Expected surface contract to exist: %s\n' "$surface_contract" >&2
  exit 1
}

[ -f "$gitignore_path" ] || {
  printf 'Expected .gitignore to exist: %s\n' "$gitignore_path" >&2
  exit 1
}

python3 - "$PROJECT_COPY" "$surface_contract" "$gitignore_path" <<'PY'
import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1])
contract_path = Path(sys.argv[2])
gitignore_text = Path(sys.argv[3]).read_text(encoding="utf-8")

with contract_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

if payload.get("schema_version") != "1.0":
    raise SystemExit("project-surfaces.json must use schema_version 1.0")

surfaces = payload.get("surfaces")
if not isinstance(surfaces, dict) or not surfaces:
    raise SystemExit("project-surfaces.json must define a non-empty surfaces object")

tracked_readmes = set()

for surface_name, config in surfaces.items():
    if not isinstance(config, dict):
        raise SystemExit(f"Surface {surface_name} must map to an object")

    description = config.get("description")
    if not isinstance(description, str) or not description.strip():
        raise SystemExit(f"Surface {surface_name} must define a non-empty description")

    gitignore = config.get("gitignore", {})
    if not isinstance(gitignore, dict):
        raise SystemExit(f"Surface {surface_name} gitignore must be an object")

    ignored = gitignore.get("ignored", [])
    if not isinstance(ignored, list) or not all(isinstance(item, str) and item.strip() for item in ignored):
        raise SystemExit(f"Surface {surface_name} gitignore.ignored must be a list of non-empty strings")

    tracked = gitignore.get("tracked_readmes", [])
    if not isinstance(tracked, list) or not all(isinstance(item, str) and item.strip() for item in tracked):
        raise SystemExit(f"Surface {surface_name} gitignore.tracked_readmes must be a list of non-empty strings")

    durable = config.get("tracked_readmes", [])
    if not isinstance(durable, list) or not all(isinstance(item, str) and item.strip() for item in durable):
        raise SystemExit(f"Surface {surface_name} tracked_readmes must be a list of non-empty strings")

    for pattern in ignored:
        if pattern not in gitignore_text:
            raise SystemExit(f"Missing gitignore pattern from contract: {pattern}")

    for rel in tracked:
        exception_line = f"!{rel}"
        if exception_line not in gitignore_text:
            raise SystemExit(f"Missing gitignore README exception from contract: {exception_line}")

    for rel in tracked + durable:
        readme_path = project_root / rel
        if not readme_path.is_file():
            raise SystemExit(f"Tracked README declared in contract does not exist: {rel}")
        if rel in tracked_readmes:
            raise SystemExit(f"Tracked README declared more than once: {rel}")
        tracked_readmes.add(rel)
PY

while IFS= read -r tracked_path; do
  [ -n "$tracked_path" ] || continue
  if git -C "$PROJECT_COPY" check-ignore -q "$tracked_path"; then
    printf 'Did not expect tracked README to be ignored: %s\n' "$tracked_path" >&2
    exit 1
  fi
done < <(
  python3 - "$surface_contract" <<'PY'
import json
import sys
from pathlib import Path

contract_path = Path(sys.argv[1])
with contract_path.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

for config in payload["surfaces"].values():
    gitignore = config.get("gitignore", {})
    for rel in gitignore.get("tracked_readmes", []):
        print(rel)
    for rel in config.get("tracked_readmes", []):
        print(rel)
PY
)

while IFS=$'\t' read -r pattern probe_path; do
  [ -n "$pattern" ] || continue
  probe_abs="$PROJECT_COPY/$probe_path"
  mkdir -p "$(dirname "$probe_abs")"
  if [ ! -e "$probe_abs" ]; then
    printf '# probe for %s\n' "$pattern" >"$probe_abs"
  fi
  git -C "$PROJECT_COPY" check-ignore -q "$probe_path" || {
    printf 'Expected contract ignore probe to be ignored: %s (%s)\n' "$probe_path" "$pattern" >&2
    exit 1
  }
done < <(
  python3 - "$surface_contract" <<'PY'
import json
import sys
from pathlib import PurePosixPath

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    payload = json.load(handle)

for config in payload["surfaces"].values():
    for pattern in config.get("gitignore", {}).get("ignored", []):
        rel = PurePosixPath(pattern)
        if pattern.endswith("/**"):
            probe = PurePosixPath(pattern[:-3]) / ".surface-probe"
        else:
            probe = rel
        print(f"{pattern}\t{probe.as_posix()}")
PY
)

printf 'Harness surface contract test passed.\n'

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

cd "$PROJECT_ROOT"

python3 - <<'PY'
import ast
import json
from pathlib import Path

project_root = Path.cwd()
registry_path = project_root / "harness" / "verification-modes.json"
content_validator_path = project_root / "harness" / "lib" / "content-validator.py"

with registry_path.open("r", encoding="utf-8") as handle:
    registry = json.load(handle)

modes = registry.get("modes")
if not isinstance(modes, dict) or not modes:
    raise SystemExit("verification-modes.json must define a non-empty modes object.")

required_keys = {
    "validator": str,
    "requires_artifacts_dir": bool,
    "target_non_empty": bool,
    "target_json": bool,
}

optional_str_keys = {"template_hint", "script_hint", "runner_script"}
optional_list_keys = {"runner_args", "extra_output_hints"}

tree = ast.parse(content_validator_path.read_text(encoding="utf-8"))
validator_function_names = {
    node.name
    for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name.startswith("validate_")
}

for mode, config in modes.items():
    if not isinstance(config, dict):
        raise SystemExit(f"Verification mode {mode} must map to an object.")
    for key, expected_type in required_keys.items():
        value = config.get(key)
        if not isinstance(value, expected_type):
            raise SystemExit(f"Verification mode {mode} has invalid {key}: {value!r}")
    for key in optional_str_keys:
        value = config.get(key)
        if value is not None and not isinstance(value, str):
            raise SystemExit(f"Verification mode {mode} has invalid {key}: {value!r}")
    for key in optional_list_keys:
        value = config.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise SystemExit(f"Verification mode {mode} has invalid {key}: {value!r}")
    validator_name = config["validator"]
    if validator_name not in validator_function_names:
        raise SystemExit(f"Verification mode {mode} references unknown validator {validator_name}.")

json_sources = [
    project_root / "harness" / "feature_list.json",
    project_root / "harness" / "templates" / "cycle-template.json",
    project_root / "harness" / "templates" / "feature-template.json",
]
json_sources.extend(sorted((project_root / "harness" / "cycles").glob("*.json")))

seen_feature_modes = set()
for path in json_sources:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    features = payload.get("features")
    if isinstance(features, list):
        for feature in features:
            verification = feature.get("verification", {})
            mode = verification.get("mode")
            if mode:
                seen_feature_modes.add(mode)

missing = sorted(mode for mode in seen_feature_modes if mode not in modes)
if missing:
    raise SystemExit(f"Feature definitions reference unregistered verification modes: {', '.join(missing)}")
PY

printf 'Harness verification registry test passed.\n'

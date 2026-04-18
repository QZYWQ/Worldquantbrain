#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "verification-modes.json"


def fail(message: str, exit_code: int = 20) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(exit_code)


def load_registry() -> dict:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    modes = payload.get("modes")
    if not isinstance(modes, dict) or not modes:
        fail(f"Invalid verification mode registry: {REGISTRY_PATH}")
    return modes


def has_files(path: Path) -> bool:
    return any(child.is_file() for child in path.rglob("*"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--script-root", required=True)
    parser.add_argument("--artifacts-dir")
    args = parser.parse_args()

    modes = load_registry()
    config = modes.get(args.mode)
    if not isinstance(config, dict):
        fail(f"Unsupported verification mode: {args.mode}")

    target_path = Path(args.target).resolve()
    script_root = Path(args.script_root).expanduser().resolve()

    if not target_path.exists():
        fail(f"Missing target file: {target_path}")

    if config.get("target_non_empty") and target_path.stat().st_size <= 0:
        fail(f"Missing or empty target file: {target_path}")

    if config.get("requires_artifacts_dir"):
        if not args.artifacts_dir:
            fail("manual-artifact mode requires --artifacts-dir.")
        artifacts_dir = Path(args.artifacts_dir).expanduser().resolve()
        if not artifacts_dir.is_dir():
            fail(f"Artifacts directory does not exist: {artifacts_dir}")
        if not has_files(artifacts_dir):
            fail(f"Artifacts directory has no files: {artifacts_dir}")

    if config.get("target_json"):
        with target_path.open("r", encoding="utf-8") as handle:
            json.load(handle)

    runner_script = config.get("runner_script")
    runner_args = config.get("runner_args", [])
    if runner_script:
        if not isinstance(runner_args, list) or not all(isinstance(item, str) for item in runner_args):
            fail(f"Invalid runner_args for verification mode: {args.mode}")
        script_path = (script_root / runner_script).resolve()
        if not script_path.is_file():
            fail(f"Verification runner script does not exist: {script_path}")
        command = [
            "python3",
            str(script_path),
            *[item.replace("{target_abs}", str(target_path)) for item in runner_args],
        ]
        result = subprocess.run(command, stdout=subprocess.DEVNULL)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

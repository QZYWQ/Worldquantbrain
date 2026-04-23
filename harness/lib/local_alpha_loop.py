#!/usr/bin/env python3
"""Helpers for the local alpha loop harness supervisor."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {"pending", "running", "done", "hold", "kill", "blocked"}
ALLOWED_TASK_TYPES = {"local_factory_run", "queue_triage"}
ALLOWED_EXECUTION_MODES = {"direct_local_factory", "external_command"}
DEFAULT_EXECUTION_MODE = "direct_local_factory"
DIRECT_FACTORY_DEFAULTS = {
    "family_dir": "runs/expression-families",
    "capture_dir": "runs/simulation-captures",
    "candidate_batch_dir": "runs/candidate-batches",
    "success_policy": "harness/alpha-success-policy.json",
    "artifact_root": "harness/artifacts/alpha-mining",
    "publish_root": "runs/research-queues",
    "publish_queue": True,
    "max_candidates": 240,
    "per_seed": 24,
    "max_depth": 2,
    "reject_dead_similarity": 0.92,
    "min_score": 55,
    "max_total": 6,
    "max_per_family": 6,
    "max_per_template": 2,
    "similarity_threshold": 0.94,
    "official_budget": 1,
    "max_official_per_family": 1,
    "official_similarity_threshold": 0.88,
}
DIRECT_FACTORY_ORDER = [
    ("family_dir", "--family-dir"),
    ("capture_dir", "--capture-dir"),
    ("candidate_batch_dir", "--candidate-batch-dir"),
    ("success_policy", "--success-policy"),
    ("artifact_root", "--artifact-root"),
    ("publish_root", "--publish-root"),
    ("include_topic", "--include-topic"),
    ("max_candidates", "--max-candidates"),
    ("per_seed", "--per-seed"),
    ("max_depth", "--max-depth"),
    ("reject_dead_similarity", "--reject-dead-similarity"),
    ("seed_limit", "--seed-limit"),
    ("min_score", "--min-score"),
    ("max_total", "--max-total"),
    ("max_per_family", "--max-per-family"),
    ("max_per_template", "--max-per-template"),
    ("similarity_threshold", "--similarity-threshold"),
    ("official_budget", "--official-budget"),
    ("max_official_per_family", "--max-official-per-family"),
    ("official_similarity_threshold", "--official-similarity-threshold"),
]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON file {path}: {exc.msg} at line {exc.lineno} column {exc.colno}")
    if not isinstance(data, dict):
        fail(f"JSON file must contain an object: {path}")
    return data


def save_json_object(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execution_mode_for(item: dict[str, Any], defaults: dict[str, Any]) -> str:
    execution = item.get("execution") if isinstance(item.get("execution"), dict) else {}
    if isinstance(execution.get("mode"), str) and execution["mode"].strip():
        return execution["mode"].strip()
    if isinstance(defaults.get("mode"), str) and defaults["mode"].strip():
        return defaults["mode"].strip()
    return DEFAULT_EXECUTION_MODE


def validate_queue_payload(payload: dict[str, Any]) -> None:
    version = payload.get("version")
    if not isinstance(version, int) or version < 1:
        fail("local alpha loop queue must include integer version >= 1")

    defaults = payload.get("defaults")
    if defaults is not None and not isinstance(defaults, dict):
        fail("local alpha loop queue defaults must be an object")

    items = payload.get("items")
    if not isinstance(items, list):
        fail("local alpha loop queue items must be an array")

    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"queue item {index} must be an object")
        item_id = item.get("id")
        family_key = item.get("family_key")
        task_type = item.get("task_type")
        status = item.get("status")
        priority = item.get("priority")
        for key, value in (
            ("id", item_id),
            ("family_key", family_key),
            ("task_type", task_type),
            ("status", status),
        ):
            if not isinstance(value, str) or not value.strip():
                fail(f"queue item {index} missing valid {key}")
        if item_id in seen_ids:
            fail(f"duplicate queue item id: {item_id}")
        seen_ids.add(item_id)
        if task_type not in ALLOWED_TASK_TYPES:
            fail(f"queue item {item_id} has unsupported task_type: {task_type}")
        if status not in ALLOWED_STATUSES:
            fail(f"queue item {item_id} has unsupported status: {status}")
        if not isinstance(priority, (int, float)):
            fail(f"queue item {item_id} priority must be numeric")
        execution = item.get("execution")
        if execution is not None and not isinstance(execution, dict):
            fail(f"queue item {item_id} execution must be an object")
        if isinstance(execution, dict):
            mode = execution.get("mode")
            if mode is not None and (not isinstance(mode, str) or not mode.strip()):
                fail(f"queue item {item_id} execution.mode must be a non-empty string")
            if isinstance(mode, str) and mode not in ALLOWED_EXECUTION_MODES:
                fail(f"queue item {item_id} has unsupported execution mode: {mode}")


def select_next_item(payload: dict[str, Any]) -> dict[str, Any] | None:
    defaults = payload.get("defaults") if isinstance(payload.get("defaults"), dict) else {}
    pending = [item for item in payload.get("items", []) if item.get("status") == "pending"]
    if not pending:
        return None
    pending.sort(
        key=lambda item: (
            -float(item.get("priority", 0)),
            execution_mode_for(item, defaults),
            str(item.get("family_key") or ""),
            str(item.get("id") or ""),
        )
    )
    return pending[0]


def load_policy_patterns(path: Path | None) -> tuple[re.Pattern[str], ...]:
    if path is None or not path.exists():
        return ()
    payload = load_json_object(path)
    compiled: list[re.Pattern[str]] = []
    for raw in payload.get("hard_exclude_topic_patterns", []):
        if isinstance(raw, str) and raw.strip():
            compiled.append(re.compile(raw, re.IGNORECASE))
    return tuple(compiled)


def compute_item_violations(item: dict[str, Any], defaults: dict[str, Any], patterns: tuple[re.Pattern[str], ...]) -> list[str]:
    violations: list[str] = []
    family_key = str(item.get("family_key") or "")
    task_type = str(item.get("task_type") or "")
    execution = item.get("execution") if isinstance(item.get("execution"), dict) else {}
    mode = execution_mode_for(item, defaults)

    if any(pattern.search(family_key) for pattern in patterns):
        violations.append("family_key matches a hard-exclude topic pattern")
    if task_type not in ALLOWED_TASK_TYPES:
        violations.append(f"unsupported task_type: {task_type}")
    if mode not in ALLOWED_EXECUTION_MODES:
        violations.append(f"unsupported execution mode: {mode}")
    if task_type != "local_factory_run" and mode == "direct_local_factory":
        violations.append("direct_local_factory only supports local_factory_run tasks")
    if mode == "external_command":
        command = execution.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            violations.append("external_command mode requires execution.command as a non-empty string array")
    return violations


def format_read_files(item: dict[str, Any]) -> str:
    inputs = item.get("inputs") if isinstance(item.get("inputs"), dict) else {}
    read_files = inputs.get("read_files")
    if not isinstance(read_files, list) or not read_files:
        return "- None declared"
    lines = []
    for path in read_files:
        if isinstance(path, str) and path.strip():
            lines.append(f"- {path.strip()}")
    return "\n".join(lines) if lines else "- None declared"


def format_constraints(item: dict[str, Any]) -> str:
    constraints = item.get("constraints") if isinstance(item.get("constraints"), dict) else {}
    if not constraints:
        return "- None declared"
    lines = []
    for key in sorted(constraints):
        value = constraints[key]
        lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines)


def render_prompt(template_path: Path, item: dict[str, Any], run_id: str, artifact_dir: Path, project_root: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "item_id": str(item.get("id") or ""),
        "family_key": str(item.get("family_key") or ""),
        "task_type": str(item.get("task_type") or ""),
        "run_id": run_id,
        "artifact_dir": artifact_dir.as_posix(),
        "project_root": project_root.as_posix(),
        "read_files": format_read_files(item),
        "constraints": format_constraints(item),
        "inputs_json": json.dumps(item.get("inputs") or {}, ensure_ascii=False, indent=2, sort_keys=True),
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def direct_factory_command(item: dict[str, Any], run_id: str, project_root: Path) -> list[str]:
    execution = item.get("execution") if isinstance(item.get("execution"), dict) else {}
    factory_args = execution.get("factory_args") if isinstance(execution.get("factory_args"), dict) else {}
    merged: dict[str, Any] = dict(DIRECT_FACTORY_DEFAULTS)
    merged.update(factory_args)
    merged.setdefault("include_topic", item.get("family_key"))

    command = [sys.executable, str((project_root / "scripts" / "alpha_family_factory.py").resolve()), "--run-id", run_id]
    seen_keys: set[str] = set()
    for key, flag in DIRECT_FACTORY_ORDER:
        if key not in merged:
            continue
        seen_keys.add(key)
        value = merged[key]
        if isinstance(value, bool):
            if value:
                command.append(flag)
            continue
        if value is None:
            continue
        if isinstance(value, list):
            for item_value in value:
                command.extend([flag, str(item_value)])
            continue
        command.extend([flag, str(value)])
    for key in sorted(merged):
        if key in seen_keys or key == "run_id":
            continue
        flag = "--" + key.replace("_", "-")
        value = merged[key]
        if isinstance(value, bool):
            if value:
                command.append(flag)
            continue
        if value is None:
            continue
        if isinstance(value, list):
            for item_value in value:
                command.extend([flag, str(item_value)])
            continue
        command.extend([flag, str(value)])
    return command


def build_command(item: dict[str, Any], defaults: dict[str, Any], run_id: str, project_root: Path) -> list[str]:
    execution = item.get("execution") if isinstance(item.get("execution"), dict) else {}
    mode = execution_mode_for(item, defaults)
    if mode == "direct_local_factory":
        return direct_factory_command(item, run_id, project_root)
    if mode == "external_command":
        return [str(part) for part in execution.get("command", [])]
    fail(f"Unsupported execution mode: {mode}")


def update_item(
    payload: dict[str, Any],
    *,
    item_id: str,
    status: str,
    run_id: str | None,
    artifact_dir: str | None,
    prompt_path: str | None,
    stdout_log: str | None,
    stderr_log: str | None,
    summary_path: str | None,
    command: str | None,
    result: str | None,
    violations: list[str] | None,
    generated_files: list[str] | None,
) -> dict[str, Any]:
    for item in payload.get("items", []):
        if str(item.get("id")) != item_id:
            continue
        item["status"] = status
        last_run = item.get("last_run") if isinstance(item.get("last_run"), dict) else {}
        if run_id:
            last_run["run_id"] = run_id
        if status == "running":
            last_run["started_at"] = now_iso()
        else:
            last_run["finished_at"] = now_iso()
        if artifact_dir:
            last_run["artifact_dir"] = artifact_dir
        if prompt_path:
            last_run["prompt_path"] = prompt_path
        if stdout_log:
            last_run["stdout_log"] = stdout_log
        if stderr_log:
            last_run["stderr_log"] = stderr_log
        if summary_path:
            last_run["summary_path"] = summary_path
        if command:
            last_run["command"] = command
        if result:
            last_run["result"] = result
        if violations is not None:
            last_run["violations"] = list(violations)
        if generated_files is not None:
            last_run["generated_files"] = list(generated_files)
        item["last_run"] = last_run
        payload["updated_at"] = now_iso()
        return payload
    fail(f"Unknown queue item id: {item_id}")


def slugify_filename(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned or "item"


def _dedupe_nonempty_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        deduped.append(cleaned)
    return deduped


def _load_queue_template_defaults(template_path: Path | None) -> dict[str, Any]:
    if template_path is None or not template_path.exists():
        return {"mode": DEFAULT_EXECUTION_MODE}
    template_payload = load_json_object(template_path)
    defaults = template_payload.get("defaults") if isinstance(template_payload.get("defaults"), dict) else {}
    merged = dict(defaults)
    merged.setdefault("mode", DEFAULT_EXECUTION_MODE)
    return merged


def _priority_manifest_family_keys(manifest: dict[str, Any]) -> list[str]:
    ordered: list[str] = []
    raw_keys = manifest.get("priority_family_keys")
    if isinstance(raw_keys, list):
        for raw in raw_keys:
            if isinstance(raw, str):
                cleaned = raw.strip()
                if cleaned and cleaned not in ordered:
                    ordered.append(cleaned)
    if ordered:
        return ordered
    shortlist = manifest.get("shortlist") if isinstance(manifest.get("shortlist"), list) else []
    for item in shortlist:
        if not isinstance(item, dict):
            continue
        family_key = item.get("family_key")
        if isinstance(family_key, str):
            cleaned = family_key.strip()
            if cleaned and cleaned not in ordered:
                ordered.append(cleaned)
    return ordered


def _priority_manifest_shortlist_by_family(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    shortlist = manifest.get("shortlist") if isinstance(manifest.get("shortlist"), list) else []
    by_family: dict[str, dict[str, Any]] = {}
    for item in shortlist:
        if not isinstance(item, dict):
            continue
        family_key = item.get("family_key")
        if isinstance(family_key, str):
            cleaned = family_key.strip()
            if cleaned and cleaned not in by_family:
                by_family[cleaned] = item
    return by_family


def build_queue_from_priority_manifest(priority_manifest_path: Path, template_path: Path | None) -> dict[str, Any]:
    manifest = load_json_object(priority_manifest_path)
    family_keys = _priority_manifest_family_keys(manifest)
    if not family_keys:
        fail(f"Priority manifest does not contain any family keys: {priority_manifest_path}")

    shortlist_by_family = _priority_manifest_shortlist_by_family(manifest)
    defaults = _load_queue_template_defaults(template_path)
    items: list[dict[str, Any]] = []
    for index, family_key in enumerate(family_keys, start=1):
        shortlist_item = shortlist_by_family.get(family_key, {})
        doc_paths = shortlist_item.get("doc_paths") if isinstance(shortlist_item, dict) else []
        field_pack_paths = shortlist_item.get("field_pack_paths") if isinstance(shortlist_item, dict) else []
        read_files: list[str] = []
        if isinstance(doc_paths, list):
            read_files.extend(str(path).strip() for path in doc_paths if isinstance(path, str))
        if isinstance(field_pack_paths, list):
            read_files.extend(str(path).strip() for path in field_pack_paths if isinstance(path, str))
        read_files.extend([priority_manifest_path.as_posix(), "harness/alpha-success-policy.json"])
        priority_score = shortlist_item.get("priority_score") if isinstance(shortlist_item, dict) else None
        if not isinstance(priority_score, (int, float)):
            priority_score = float(len(family_keys) - index + 1)
        state = shortlist_item.get("state") if isinstance(shortlist_item, dict) else "explore"
        reason = shortlist_item.get("reason") if isinstance(shortlist_item, dict) else ""
        items.append(
            {
                "id": f"{slugify_filename(family_key)}-{index:03d}",
                "family_key": family_key,
                "task_type": "local_factory_run",
                "status": "pending",
                "priority": float(priority_score),
                "inputs": {
                    "priority_manifest": priority_manifest_path.as_posix(),
                    "priority_manifest_run_id": str(manifest.get("run_id") or ""),
                    "priority_family_order": index,
                    "priority_family_keys": family_keys,
                    "priority_score": float(priority_score),
                    "priority_state": str(state or ""),
                    "priority_reason": str(reason or ""),
                    "read_files": _dedupe_nonempty_strings(read_files),
                },
                "constraints": {
                    "official_simulate_forbidden": True,
                    "candidate_batch_forbidden": True,
                    "priority_manifest_path": priority_manifest_path.as_posix(),
                },
                "execution": {
                    "mode": DEFAULT_EXECUTION_MODE,
                    "factory_args": {
                        "include_topic": [family_key],
                        "publish_queue": True,
                    },
                },
            }
        )

    return {
        "version": 1,
        "generated_at": now_iso(),
        "source_manifest_path": priority_manifest_path.as_posix(),
        "source_manifest_run_id": str(manifest.get("run_id") or ""),
        "source_manifest_objective": str(manifest.get("objective") or ""),
        "defaults": defaults,
        "items": items,
    }


def ensure_queue_file(
    queue_path: Path,
    template_path: Path | None,
    priority_manifest_path: Path | None = None,
) -> None:
    if priority_manifest_path is not None:
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        payload = build_queue_from_priority_manifest(priority_manifest_path, template_path)
        save_json_object(queue_path, payload)
        return
    if queue_path.exists():
        return
    if template_path is None or not template_path.exists():
        fail(f"Queue file not found and no template available: {queue_path}")
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path, queue_path)


def build_runtime_item(
    item: dict[str, Any],
    *,
    run_id: str,
    artifact_dir: Path,
    project_root: Path,
    queue_path: Path,
    prompt_path: Path,
) -> dict[str, Any]:
    runtime_item = json.loads(json.dumps(item))
    runtime_item.setdefault("runtime_context", {})
    if isinstance(runtime_item["runtime_context"], dict):
        runtime_item["runtime_context"].update(
            {
                "run_id": run_id,
                "artifact_dir": artifact_dir.as_posix(),
                "project_root": project_root.as_posix(),
                "queue_path": queue_path.as_posix(),
                "prompt_path": prompt_path.as_posix(),
            }
        )

    execution = runtime_item.setdefault("execution", {})
    if isinstance(execution, dict):
        execution.setdefault("factory_args", {})
        if isinstance(execution["factory_args"], dict):
            execution["factory_args"]["artifact_root"] = (artifact_dir / "factory").as_posix()
            execution["factory_args"]["publish_root"] = (artifact_dir / "published").as_posix()
    return runtime_item


def execute_command(command: list[str], *, cwd: Path, stdout_path: Path, stderr_path: Path, env: dict[str, str]) -> int:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr_handle:
        completed = subprocess.run(command, cwd=str(cwd), env=env, stdout=stdout_handle, stderr=stderr_handle)
    return completed.returncode


def classify_direct_factory_result(bundle_root: Path) -> tuple[str, list[str], list[str]]:
    violations: list[str] = []
    generated_files: list[str] = []
    manifest_path = bundle_root / "manifest.json"
    queue_path = bundle_root / "queue.json"
    official_budget_path = bundle_root / "official-budget.json"

    if not manifest_path.exists():
        return "blocked", ["direct factory bundle missing manifest.json"], generated_files
    if not queue_path.exists():
        return "blocked", ["direct factory bundle missing queue.json"], generated_files

    generated_files.extend(
        path.as_posix()
        for path in (
            manifest_path,
            bundle_root / "manifest.md",
            queue_path,
            bundle_root / "queue.md",
            official_budget_path,
            bundle_root / "official-budget.md",
        )
        if path.exists()
    )

    manifest = load_json_object(manifest_path)
    queue = load_json_object(queue_path)
    official_budget = load_json_object(official_budget_path) if official_budget_path.exists() else {}
    counts = manifest.get("counts") if isinstance(manifest.get("counts"), dict) else {}
    family_count = int(counts.get("family_count", 0) or 0)
    queue_count = int(counts.get("queue_count", 0) or 0)
    official_budget_count = len(official_budget.get("items", [])) if isinstance(official_budget.get("items"), list) else 0
    queue_items = queue.get("items") if isinstance(queue.get("items"), list) else []
    if family_count <= 0:
        return "hold", ["direct factory selected no families"], generated_files
    if queue_count > 0 or official_budget_count > 0 or len(queue_items) > 0:
        return "branch", [
            f"direct factory produced queue_count={queue_count}, official_budget_count={official_budget_count}",
        ], generated_files
    return "hold", ["direct factory produced no queue items"], generated_files


def classify_external_result(result_path: Path) -> tuple[str, list[str], list[str]]:
    if not result_path.exists():
        return "blocked", ["external command did not write result.json"], []
    payload = load_json_object(result_path)
    result = str(payload.get("result") or "").strip().lower()
    if result not in {"branch", "hold", "kill"}:
        return "blocked", [f"external command wrote unsupported result: {result!r}"], [result_path.as_posix()]
    notes: list[str] = []
    if isinstance(payload.get("notes"), list):
        notes.extend(str(item) for item in payload["notes"] if isinstance(item, str) and item.strip())
    return result, notes, [result_path.as_posix()]


def render_loop_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Local Alpha Loop",
        "",
        f"- Run id: {manifest['run_id']}",
        f"- Queue path: {manifest['queue_path']}",
        f"- Priority manifest: {manifest.get('priority_manifest_path') or 'none'}",
        f"- Max rounds: {manifest['max_rounds']}",
        f"- Completed rounds: {manifest['completed_rounds']}",
        f"- Result counts: branch={manifest['counts']['branch']} hold={manifest['counts']['hold']} kill={manifest['counts']['kill']} blocked={manifest['counts']['blocked']}",
        "",
        "## Rounds",
        "",
    ]
    if not manifest.get("rounds"):
        lines.append("- No rounds executed.")
    else:
        for round_item in manifest["rounds"]:
            command_text = round_item.get("command_text") or json.dumps(round_item.get("command"), ensure_ascii=False)
            lines.append(
                f"- {round_item['round_id']} -> {round_item['family_key']} [{round_item['status_after']}] "
                f"result={round_item['result']} command=`{command_text}`"
            )
            for violation in round_item.get("violations", []):
                lines.append(f"  - {violation}")
    lines.append("")
    return "\n".join(lines)


def command_run_loop(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    queue_path = Path(args.queue).expanduser().resolve()
    queue_template_path = Path(args.queue_template).expanduser().resolve() if args.queue_template else None
    priority_manifest_path = Path(args.priority_manifest).expanduser().resolve() if args.priority_manifest else None
    prompt_template_path = Path(args.prompt_template).expanduser().resolve()
    artifact_root = Path(args.artifact_root).expanduser().resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)
    ensure_queue_file(queue_path, queue_template_path, priority_manifest_path)

    payload = load_json_object(queue_path)
    validate_queue_payload(payload)
    defaults = payload.get("defaults") if isinstance(payload.get("defaults"), dict) else {}
    queue_source_manifest_run_id = str(payload.get("source_manifest_run_id") or "")
    policy_path = Path(args.success_policy).expanduser().resolve() if args.success_policy else None
    policy_patterns = load_policy_patterns(policy_path)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    loop_run_id = args.run_id or f"{timestamp}-local-alpha-loop"
    loop_artifact_dir = artifact_root / loop_run_id
    loop_artifact_dir.mkdir(parents=True, exist_ok=True)

    rounds: list[dict[str, Any]] = []
    counts = {"branch": 0, "hold": 0, "kill": 0, "blocked": 0}
    completed_rounds = 0
    for round_index in range(1, args.max_rounds + 1):
        payload = load_json_object(queue_path)
        validate_queue_payload(payload)
        next_item = select_next_item(payload)
        if next_item is None:
            break

        completed_rounds += 1
        item_id = str(next_item["id"])
        family_key = str(next_item["family_key"])
        round_id = f"{loop_run_id}-{round_index:02d}-{slugify_filename(item_id)}"
        round_dir = loop_artifact_dir / round_id
        round_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = round_dir / "prompt.txt"
        item_path = round_dir / "item.json"
        runtime_item_path = round_dir / "runtime-item.json"
        stdout_log = round_dir / "stdout.log"
        stderr_log = round_dir / "stderr.log"
        summary_json_path = round_dir / "summary.json"
        summary_md_path = round_dir / "summary.md"

        runtime_item = build_runtime_item(
            next_item,
            run_id=round_id,
            artifact_dir=round_dir,
            project_root=project_root,
            queue_path=queue_path,
            prompt_path=prompt_path,
        )
        save_json_object(item_path, next_item)
        save_json_object(runtime_item_path, runtime_item)
        rendered_prompt = render_prompt(prompt_template_path, runtime_item, round_id, round_dir, project_root)
        prompt_path.write_text(rendered_prompt, encoding="utf-8")

        mode = execution_mode_for(runtime_item, defaults)
        preflight_violations = compute_item_violations(runtime_item, defaults, policy_patterns)
        if preflight_violations:
            cmd: list[str] = []
            cmd_text = ""
            exit_code = 0
            result = "blocked"
            result_notes = preflight_violations
            stdout_log.write_text("", encoding="utf-8")
            stderr_log.write_text("\n".join(preflight_violations) + "\n", encoding="utf-8")
            result_generated_files = []
        else:
            cmd = build_command(runtime_item, defaults, round_id, project_root)
            cmd_text = json.dumps(cmd, ensure_ascii=False)
            queue_payload = load_json_object(queue_path)
            queue_payload = update_item(
                queue_payload,
                item_id=item_id,
                status="running",
                run_id=round_id,
                artifact_dir=round_dir.as_posix(),
                prompt_path=prompt_path.as_posix(),
                stdout_log=stdout_log.as_posix(),
                stderr_log=stderr_log.as_posix(),
                summary_path=summary_json_path.as_posix(),
                command=cmd_text,
                result=None,
                violations=[],
                generated_files=[item_path.as_posix(), runtime_item_path.as_posix(), prompt_path.as_posix()],
            )
            save_json_object(queue_path, queue_payload)

            env = dict(os.environ)
            env.update(
                {
                    "LOCAL_ALPHA_LOOP_RUN_ID": round_id,
                    "LOCAL_ALPHA_LOOP_ITEM_ID": item_id,
                    "LOCAL_ALPHA_LOOP_FAMILY_KEY": family_key,
                    "LOCAL_ALPHA_LOOP_ARTIFACT_DIR": round_dir.as_posix(),
                    "LOCAL_ALPHA_LOOP_PROMPT_PATH": prompt_path.as_posix(),
                    "LOCAL_ALPHA_LOOP_QUEUE_PATH": queue_path.as_posix(),
                    "LOCAL_ALPHA_LOOP_ITEM_PATH": item_path.as_posix(),
                    "LOCAL_ALPHA_LOOP_RUNTIME_ITEM_PATH": runtime_item_path.as_posix(),
                    "LOCAL_ALPHA_LOOP_RESULT_PATH": (round_dir / "result.json").as_posix(),
                }
            )
            exit_code = execute_command(cmd, cwd=project_root, stdout_path=stdout_log, stderr_path=stderr_log, env=env)

            if exit_code != 0:
                result = "blocked"
                result_notes = [f"command exited with code {exit_code}"]
                result_generated_files = []
            elif mode == "direct_local_factory":
                factory_root = round_dir / "factory" / round_id
                result, result_notes, result_generated_files = classify_direct_factory_result(factory_root)
            else:
                result, result_notes, result_generated_files = classify_external_result(round_dir / "result.json")

        result_status = {"branch": "done", "hold": "hold", "kill": "kill", "blocked": "blocked"}[result]
        counts[result] += 1
        generated_files = [
            item_path.as_posix(),
            runtime_item_path.as_posix(),
            prompt_path.as_posix(),
            stdout_log.as_posix(),
            stderr_log.as_posix(),
            summary_json_path.as_posix(),
            summary_md_path.as_posix(),
        ]
        generated_files.extend(result_generated_files)
        queue_payload = load_json_object(queue_path)
        queue_payload = update_item(
            queue_payload,
            item_id=item_id,
            status=result_status,
            run_id=round_id,
            artifact_dir=round_dir.as_posix(),
            prompt_path=prompt_path.as_posix(),
            stdout_log=stdout_log.as_posix(),
            stderr_log=stderr_log.as_posix(),
            summary_path=summary_json_path.as_posix(),
            command=cmd_text,
            result=result,
            violations=result_notes,
            generated_files=generated_files,
        )
        save_json_object(queue_path, queue_payload)

        round_manifest = {
            "round_id": round_id,
            "item_id": item_id,
            "family_key": family_key,
            "task_type": str(runtime_item.get("task_type") or ""),
            "status_before": "pending",
            "status_after": result_status,
            "result": result,
            "command": cmd,
            "command_text": cmd_text,
            "artifact_dir": round_dir.as_posix(),
            "prompt_path": prompt_path.as_posix(),
            "stdout_log": stdout_log.as_posix(),
            "stderr_log": stderr_log.as_posix(),
            "summary_path": summary_json_path.as_posix(),
            "summary_md_path": summary_md_path.as_posix(),
            "violations": result_notes,
            "generated_files": generated_files,
            "exit_code": exit_code,
            "execution_mode": mode,
        }
        save_json_object(summary_json_path, round_manifest)
        summary_md_path.write_text(render_loop_markdown({
            "run_id": round_id,
            "queue_path": queue_path.as_posix(),
            "max_rounds": 1,
            "completed_rounds": 1,
            "counts": {"branch": 1 if result == "branch" else 0, "hold": 1 if result == "hold" else 0, "kill": 1 if result == "kill" else 0, "blocked": 1 if result == "blocked" else 0},
            "rounds": [round_manifest],
        }), encoding="utf-8")

        rounds.append(round_manifest)

    loop_manifest = {
        "generated_at": now_iso(),
        "run_id": loop_run_id,
        "queue_path": queue_path.as_posix(),
        "queue_template_path": queue_template_path.as_posix() if queue_template_path else None,
        "priority_manifest_path": priority_manifest_path.as_posix() if priority_manifest_path else None,
        "priority_manifest_run_id": queue_source_manifest_run_id,
        "prompt_template_path": prompt_template_path.as_posix(),
        "artifact_root": artifact_root.as_posix(),
        "artifact_dir": loop_artifact_dir.as_posix(),
        "max_rounds": args.max_rounds,
        "completed_rounds": completed_rounds,
        "counts": counts,
        "rounds": rounds,
    }
    loop_manifest_path = loop_artifact_dir / "manifest.json"
    loop_manifest_md_path = loop_artifact_dir / "manifest.md"
    save_json_object(loop_manifest_path, loop_manifest)
    loop_manifest_md_path.write_text(render_loop_markdown(loop_manifest), encoding="utf-8")

    run_summary_root = project_root / "runs" / "learning-loops"
    run_summary_root.mkdir(parents=True, exist_ok=True)
    run_summary_json_path = run_summary_root / f"{loop_run_id}.json"
    run_summary_md_path = run_summary_root / f"{loop_run_id}.md"
    save_json_object(run_summary_json_path, loop_manifest)
    run_summary_md_path.write_text(render_loop_markdown(loop_manifest), encoding="utf-8")

    print(f"Local alpha loop bundle: {loop_artifact_dir}")
    print(f"Local alpha loop manifest: {run_summary_json_path}")
    return 0


def command_validate_queue(args: argparse.Namespace) -> int:
    payload = load_json_object(Path(args.path))
    validate_queue_payload(payload)
    return 0


def command_next_item(args: argparse.Namespace) -> int:
    payload = load_json_object(Path(args.path))
    validate_queue_payload(payload)
    item = select_next_item(payload)
    if item is None:
        return 0
    print(json.dumps(item, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_queue_default(args: argparse.Namespace) -> int:
    payload = load_json_object(Path(args.path))
    validate_queue_payload(payload)
    defaults = payload.get("defaults") if isinstance(payload.get("defaults"), dict) else {}
    value = defaults.get(args.key)
    if value is None:
        return 0
    if isinstance(value, (dict, list)):
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    else:
        print(value)
    return 0


def command_item_violations(args: argparse.Namespace) -> int:
    payload = load_json_object(Path(args.queue_path)) if args.queue_path else {"defaults": {}}
    defaults = payload.get("defaults") if isinstance(payload.get("defaults"), dict) else {}
    item = load_json_object(Path(args.item_json))
    patterns = load_policy_patterns(Path(args.policy_path)) if args.policy_path else ()
    violations = compute_item_violations(item, defaults, patterns)
    print(json.dumps(violations, ensure_ascii=False, indent=2))
    return 0


def command_render_prompt(args: argparse.Namespace) -> int:
    item = load_json_object(Path(args.item_json))
    output = Path(args.output)
    rendered = render_prompt(
        Path(args.template),
        item,
        args.run_id,
        Path(args.artifact_dir),
        Path(args.project_root),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    return 0


def command_build_command(args: argparse.Namespace) -> int:
    payload = load_json_object(Path(args.queue_path)) if args.queue_path else {"defaults": {}}
    defaults = payload.get("defaults") if isinstance(payload.get("defaults"), dict) else {}
    item = load_json_object(Path(args.item_json))
    command = build_command(item, defaults, args.run_id, Path(args.project_root))
    print(json.dumps(command, ensure_ascii=False))
    return 0


def command_execution_mode(args: argparse.Namespace) -> int:
    payload = load_json_object(Path(args.queue_path)) if args.queue_path else {"defaults": {}}
    defaults = payload.get("defaults") if isinstance(payload.get("defaults"), dict) else {}
    item = load_json_object(Path(args.item_json))
    print(execution_mode_for(item, defaults))
    return 0


def command_update_item(args: argparse.Namespace) -> int:
    path = Path(args.path)
    payload = load_json_object(path)
    validate_queue_payload(payload)
    violations = json.loads(args.violations) if args.violations else None
    generated_files = json.loads(args.generated_files) if args.generated_files else None
    payload = update_item(
        payload,
        item_id=args.item_id,
        status=args.status,
        run_id=args.run_id,
        artifact_dir=args.artifact_dir,
        prompt_path=args.prompt_path,
        stdout_log=args.stdout_log,
        stderr_log=args.stderr_log,
        summary_path=args.summary_path,
        command=args.command,
        result=args.result,
        violations=violations,
        generated_files=generated_files,
    )
    save_json_object(path, payload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local alpha loop queue helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    loop_parser = subparsers.add_parser("run-loop")
    loop_parser.add_argument("--queue", required=True)
    loop_parser.add_argument("--queue-template")
    loop_parser.add_argument("--priority-manifest", "--expander-manifest", dest="priority_manifest")
    loop_parser.add_argument("--prompt-template", required=True)
    loop_parser.add_argument("--artifact-root", required=True)
    loop_parser.add_argument("--project-root", required=True)
    loop_parser.add_argument("--success-policy")
    loop_parser.add_argument("--run-id", default="")
    loop_parser.add_argument("--max-rounds", type=int, default=3)
    loop_parser.set_defaults(func=command_run_loop)

    validate_parser = subparsers.add_parser("validate-queue")
    validate_parser.add_argument("--path", required=True)
    validate_parser.set_defaults(func=command_validate_queue)

    next_parser = subparsers.add_parser("next-item")
    next_parser.add_argument("--path", required=True)
    next_parser.set_defaults(func=command_next_item)

    default_parser = subparsers.add_parser("queue-default")
    default_parser.add_argument("--path", required=True)
    default_parser.add_argument("--key", required=True)
    default_parser.set_defaults(func=command_queue_default)

    violations_parser = subparsers.add_parser("item-violations")
    violations_parser.add_argument("--item-json", required=True)
    violations_parser.add_argument("--queue-path")
    violations_parser.add_argument("--policy-path")
    violations_parser.set_defaults(func=command_item_violations)

    prompt_parser = subparsers.add_parser("render-prompt")
    prompt_parser.add_argument("--template", required=True)
    prompt_parser.add_argument("--item-json", required=True)
    prompt_parser.add_argument("--run-id", required=True)
    prompt_parser.add_argument("--artifact-dir", required=True)
    prompt_parser.add_argument("--project-root", required=True)
    prompt_parser.add_argument("--output", required=True)
    prompt_parser.set_defaults(func=command_render_prompt)

    command_parser = subparsers.add_parser("build-command")
    command_parser.add_argument("--item-json", required=True)
    command_parser.add_argument("--queue-path")
    command_parser.add_argument("--run-id", required=True)
    command_parser.add_argument("--project-root", required=True)
    command_parser.set_defaults(func=command_build_command)

    mode_parser = subparsers.add_parser("execution-mode")
    mode_parser.add_argument("--item-json", required=True)
    mode_parser.add_argument("--queue-path")
    mode_parser.set_defaults(func=command_execution_mode)

    update_parser = subparsers.add_parser("update-item")
    update_parser.add_argument("--path", required=True)
    update_parser.add_argument("--item-id", required=True)
    update_parser.add_argument("--status", required=True)
    update_parser.add_argument("--run-id")
    update_parser.add_argument("--artifact-dir")
    update_parser.add_argument("--prompt-path")
    update_parser.add_argument("--stdout-log")
    update_parser.add_argument("--stderr-log")
    update_parser.add_argument("--summary-path")
    update_parser.add_argument("--command")
    update_parser.add_argument("--result")
    update_parser.add_argument("--violations")
    update_parser.add_argument("--generated-files")
    update_parser.set_defaults(func=command_update_item)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

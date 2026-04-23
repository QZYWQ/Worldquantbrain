#!/usr/bin/env python3
"""Orchestrate a daily local alpha-mining pass.

This wrapper keeps the existing factory as the core workhorse, but adds the
missing daily control plane:

- choose the most promising active families from the success-state registry
- run the factory once per selected family
- collate the best official-batch recommendations into one daily bundle

The script stays local-only. It does not automate official WorldQuant flows.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from alpha_success_core import build_success_rate_state


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FACTORY_SCRIPT = PROJECT_ROOT / "scripts" / "alpha_family_factory.py"
DEFAULT_DAILY_ARTIFACT_ROOT = Path("harness/artifacts/alpha-daily")
DEFAULT_DAILY_PUBLISH_ROOT = Path("runs/research-queues")
STATE_PRIORITY = {"exploit": 0, "branch": 1, "explore": 2, "hold": 3, "kill": 4}
DEFAULT_ALLOWED_STATES = ("exploit", "branch", "explore")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the daily local alpha-mining pass.")
    parser.add_argument(
        "--family-dir",
        type=Path,
        default=Path("runs/expression-families"),
        help="Directory containing expression-family markdown docs.",
    )
    parser.add_argument(
        "--capture-dir",
        type=Path,
        default=Path("runs/simulation-captures"),
        help="Directory containing simulation-capture JSON files.",
    )
    parser.add_argument(
        "--candidate-batch-dir",
        type=Path,
        default=Path("runs/candidate-batches"),
        help="Directory containing durable candidate-batch JSON artifacts.",
    )
    parser.add_argument(
        "--candidate-check-dir",
        type=Path,
        default=Path("harness/artifacts"),
        help="Directory containing candidate-check evidence artifacts.",
    )
    parser.add_argument(
        "--success-policy",
        type=Path,
        default=Path("harness/alpha-success-policy.json"),
        help="Success-rate policy file used for local scheduling.",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=DEFAULT_DAILY_ARTIFACT_ROOT,
        help="Root directory for the per-family factory bundles produced by this runner.",
    )
    parser.add_argument(
        "--publish-root",
        type=Path,
        default=DEFAULT_DAILY_PUBLISH_ROOT,
        help="Durable output root used for the daily summary queue publication.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="",
        help="Optional run id override. Defaults to <YYYY-MM-DD>-daily-alpha-runner.",
    )
    parser.add_argument(
        "--family-limit",
        type=int,
        default=4,
        help="Maximum number of families to run in one daily pass.",
    )
    parser.add_argument(
        "--allowed-state",
        action="append",
        default=[],
        help="Family states eligible for the daily pass. Can be repeated.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=240,
        help="Per-family hard cap on generated candidates passed to the factory.",
    )
    parser.add_argument(
        "--per-seed",
        type=int,
        default=24,
        help="Maximum number of candidates to keep per seed expression.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum mutation depth per seed expression.",
    )
    parser.add_argument(
        "--reject-dead-similarity",
        type=float,
        default=0.92,
        help="Skip candidates that are too similar to known dead branches.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=55.0,
        help="Local score threshold used by the factory when building queues.",
    )
    parser.add_argument(
        "--max-total",
        type=int,
        default=8,
        help="Maximum number of queue items retained per family run.",
    )
    parser.add_argument(
        "--max-per-family",
        type=int,
        default=2,
        help="Maximum queue items from the same family in a family run.",
    )
    parser.add_argument(
        "--max-per-template",
        type=int,
        default=2,
        help="Maximum queue items sharing the same template in a family run.",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.94,
        help="Queue similarity threshold used within each family run.",
    )
    parser.add_argument(
        "--official-budget",
        type=int,
        default=2,
        help="Official-slot budget per family run.",
    )
    parser.add_argument(
        "--max-official-per-family",
        type=int,
        default=2,
        help="Maximum official budget slots per family run.",
    )
    parser.add_argument(
        "--official-similarity-threshold",
        type=float,
        default=0.88,
        help="Minimum expression dissimilarity required between official slot picks.",
    )
    parser.add_argument(
        "--seed-limit",
        type=int,
        default=0,
        help="Optional limit on how many seed docs to process in each family run.",
    )
    parser.add_argument(
        "--family-filter",
        action="append",
        default=[],
        help="Optional explicit family topic filter. If set, only these topics are considered.",
    )
    parser.add_argument(
        "--family-priority-file",
        type=Path,
        default=None,
        help="Optional JSON manifest with priority_family_keys used to override family scheduling order.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Select families and write the summary without invoking the family factory.",
    )
    return parser.parse_args()


def default_run_id(args: argparse.Namespace) -> str:
    if args.run_id:
        return args.run_id
    return f"{datetime.now().strftime('%Y-%m-%d')}-daily-alpha-runner"


def _allowed_states(args: argparse.Namespace) -> tuple[str, ...]:
    states = [state.strip() for state in args.allowed_state if state.strip()]
    if states:
        return tuple(dict.fromkeys(states))
    return DEFAULT_ALLOWED_STATES


def _state_rank(state: str) -> int:
    return STATE_PRIORITY.get(state, 99)


def _float_value(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def select_family_rows(
    family_registry: Sequence[dict[str, Any]],
    *,
    allowed_states: Sequence[str],
    explicit_family_filter: Sequence[str] = (),
    priority_family_keys: Sequence[str] = (),
    family_limit: int = 4,
) -> list[dict[str, Any]]:
    allowed = {state for state in allowed_states}
    topic_filter = {topic.strip() for topic in explicit_family_filter if topic.strip()}
    priority_rank = {
        family_key.strip(): index
        for index, family_key in enumerate(priority_family_keys)
        if family_key and family_key.strip()
    }
    default_priority_rank = len(priority_rank)

    candidates = [
        row
        for row in family_registry
        if str(row.get("state") or "") in allowed
        and (not topic_filter or str(row.get("family_key") or "") in topic_filter)
    ]

    candidates.sort(
        key=lambda row: (
            priority_rank.get(str(row.get("family_key") or ""), default_priority_rank),
            _state_rank(str(row.get("state") or "")),
            -int(row.get("submit_ready_count", 0) or 0),
            -int(row.get("full_gate_outcome_count", 0) or 0),
            -int(row.get("official_outcome_count", 0) or 0),
            -_float_value(
                (row.get("best_outcome") or {}).get("metrics", {}).get("fitness")
                or (row.get("best_outcome") or {}).get("metrics", {}).get("sharpe"),
                default=-9999.0,
            ),
            str(row.get("family_key") or ""),
        ),
    )
    return candidates[:family_limit]


def _priority_keys_from_item(item: Any) -> list[str]:
    if isinstance(item, str):
        stripped = item.strip()
        return [stripped] if stripped else []
    if isinstance(item, dict):
        for key in ("family_key", "topic", "family", "key"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return [value.strip()]
    return []


def load_priority_family_keys(path: Path | None) -> tuple[str, ...]:
    if path is None:
        return ()
    resolved = path if path.is_absolute() else (PROJECT_ROOT / path)
    if not resolved.exists():
        raise SystemExit(f"Family priority file not found: {path}")
    payload = json.loads(resolved.read_text(encoding="utf-8"))

    ordered: list[str] = []
    raw_items: Any
    if isinstance(payload, dict):
        if isinstance(payload.get("priority_family_keys"), list):
            raw_items = payload.get("priority_family_keys")
        elif isinstance(payload.get("shortlist"), list):
            raw_items = payload.get("shortlist")
        else:
            raise SystemExit(
                "Family priority file must expose priority_family_keys or shortlist."
            )
    elif isinstance(payload, list):
        raw_items = payload
    else:
        raise SystemExit("Family priority file must be a JSON object or array.")

    seen: set[str] = set()
    for item in raw_items:
        for family_key in _priority_keys_from_item(item):
            if family_key not in seen:
                seen.add(family_key)
                ordered.append(family_key)
    return tuple(ordered)


def _factory_command(args: argparse.Namespace, topic: str, run_id: str) -> list[str]:
    command = [
        sys.executable,
        str(FACTORY_SCRIPT),
        "--family-dir",
        str(args.family_dir),
        "--capture-dir",
        str(args.capture_dir),
        "--candidate-batch-dir",
        str(args.candidate_batch_dir),
        "--success-policy",
        str(args.success_policy),
        "--artifact-root",
        str(args.artifact_root),
        "--run-id",
        run_id,
        "--include-topic",
        topic,
        "--publish-queue",
        "--publish-root",
        str(args.publish_root),
        "--max-candidates",
        str(args.max_candidates),
        "--per-seed",
        str(args.per_seed),
        "--max-depth",
        str(args.max_depth),
        "--reject-dead-similarity",
        str(args.reject_dead_similarity),
        "--seed-limit",
        str(args.seed_limit),
        "--min-score",
        str(args.min_score),
        "--max-total",
        str(args.max_total),
        "--max-per-family",
        str(args.max_per_family),
        "--max-per-template",
        str(args.max_per_template),
        "--similarity-threshold",
        str(args.similarity_threshold),
        "--official-budget",
        str(args.official_budget),
        "--max-official-per-family",
        str(args.max_official_per_family),
        "--official-similarity-threshold",
        str(args.official_similarity_threshold),
    ]
    return command


def _load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def run_family_factory(args: argparse.Namespace, topic: str, run_id: str) -> dict[str, Any]:
    bundle_root = args.artifact_root / run_id
    command = _factory_command(args, topic, run_id)
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise SystemExit(
            f"alpha_family_factory failed for {topic} (run_id={run_id})\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    manifest = _load_json_if_exists(bundle_root / "manifest.json")
    official_budget = _load_json_if_exists(bundle_root / "official-budget.json")
    queue = _load_json_if_exists(bundle_root / "queue.json")
    selected_count = len(queue.get("items", [])) if isinstance(queue.get("items"), list) else 0
    return {
        "topic": topic,
        "run_id": run_id,
        "bundle_root": str(bundle_root),
        "selected_count": selected_count,
        "manifest": manifest,
        "official_budget": official_budget,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def build_daily_manifest(
    *,
    run_id: str,
    selected_families: Sequence[dict[str, Any]],
    family_runs: Sequence[dict[str, Any]],
    success_state: dict[str, Any],
    priority_family_keys: Sequence[str],
    args: argparse.Namespace,
) -> dict[str, Any]:
    all_budget_items: list[dict[str, Any]] = []
    for family_run in family_runs:
        items = family_run.get("official_budget", {}).get("items", [])
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    enriched = dict(item)
                    enriched["source_family_run"] = family_run["run_id"]
                    enriched["source_family_topic"] = family_run["topic"]
                    all_budget_items.append(enriched)

    all_budget_items.sort(
        key=lambda item: (
            -_float_value(item.get("gate_likelihood_score"), default=-9999.0),
            -_float_value(item.get("local_score"), default=-9999.0),
            int(item.get("mutation_depth", 0) or 0),
            str(item.get("family_topic") or ""),
            str(item.get("candidate_id") or ""),
        ),
    )
    daily_budget_items = all_budget_items[: args.official_budget]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "run_id": run_id,
        "objective": "maximize_internal_submit_ready_per_official_slot",
        "settings": {
            "family_limit": args.family_limit,
            "allowed_states": list(_allowed_states(args)),
            "family_filter": list(dict.fromkeys(args.family_filter)),
            "family_priority_file": str(args.family_priority_file) if args.family_priority_file else None,
            "priority_family_keys_loaded": list(priority_family_keys),
            "max_candidates": args.max_candidates,
            "per_seed": args.per_seed,
            "max_depth": args.max_depth,
            "reject_dead_similarity": args.reject_dead_similarity,
            "min_score": args.min_score,
            "max_total": args.max_total,
            "max_per_family": args.max_per_family,
            "max_per_template": args.max_per_template,
            "similarity_threshold": args.similarity_threshold,
            "official_budget": args.official_budget,
            "max_official_per_family": args.max_official_per_family,
            "official_similarity_threshold": args.official_similarity_threshold,
        },
        "success_state_counts": {
            "family_docs": len(success_state.get("family_docs", [])),
            "official_outcome_memory": len(success_state.get("official_outcome_memory", [])),
            "candidate_outcome_memory": len(success_state.get("candidate_outcome_memory", [])),
            "combined_outcome_memory": len(success_state.get("combined_outcome_memory", [])),
            "submit_ready_ledger": len(success_state.get("submit_ready_ledger", [])),
            "family_registry_summary": len(success_state.get("family_registry_summary", [])),
        },
        "selected_families": list(selected_families),
        "family_runs": list(family_runs),
        "daily_budget_items": daily_budget_items,
        "all_budget_items": all_budget_items,
    }


def render_daily_manifest_md(manifest: dict[str, Any]) -> str:
    lines = [
        "# Daily Alpha Mining Runner",
        "",
        f"- Run id: {manifest['run_id']}",
        f"- Objective: {manifest['objective']}",
        f"- Selected families: {len(manifest.get('selected_families', []))}",
        f"- Family runs: {len(manifest.get('family_runs', []))}",
        f"- Daily budget items: {len(manifest.get('daily_budget_items', []))}",
        "",
        "## Selected Families",
        "",
    ]
    for row in manifest.get("selected_families", []):
        lines.append(
            f"- {row['family_key']} [{row['state']}] "
            f"outcomes={row['official_outcome_count']} full_gates={row['full_gate_outcome_count']} "
            f"submit_ready={row['submit_ready_count']}"
        )
    lines.append("")
    lines.append("## Family Runs")
    lines.append("")
    for run in manifest.get("family_runs", []):
        lines.append(
            f"- {run['topic']} -> {run['bundle_root']} "
            f"(selected_count={run['selected_count']})"
        )
    lines.append("")
    lines.append("## Daily Official Budget")
    lines.append("")
    if not manifest.get("daily_budget_items"):
        lines.append("- No daily official budget item survived aggregation.")
    else:
        for item in manifest["daily_budget_items"]:
            lines.append(
                f"- {item['family_topic']} / {item.get('slot_reason', 'anchor')} "
                f"gate={item.get('gate_likelihood_score')} local={item.get('local_score')} "
                f"expr=`{item.get('expression')}`"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    run_id = default_run_id(args)
    allowed_states = _allowed_states(args)
    priority_family_keys = load_priority_family_keys(args.family_priority_file)
    success_state = build_success_rate_state(
        family_dir=args.family_dir,
        capture_dir=args.capture_dir,
        candidate_batch_dir=args.candidate_batch_dir,
        candidate_check_dir=args.candidate_check_dir,
    )
    selected_families = select_family_rows(
        success_state["family_registry_summary"],
        allowed_states=allowed_states,
        explicit_family_filter=args.family_filter,
        priority_family_keys=priority_family_keys,
        family_limit=args.family_limit,
    )

    if not selected_families:
        raise SystemExit("No families matched the current daily runner filters.")

    family_runs: list[dict[str, Any]] = []
    if not args.dry_run:
        for index, family in enumerate(selected_families, start=1):
            family_topic = str(family["family_key"])
            family_run_id = f"{run_id}-{index:02d}-{family_topic}"
            family_run = run_family_factory(args, family_topic, family_run_id)
            family_runs.append(family_run)
    manifest = build_daily_manifest(
        run_id=run_id,
        selected_families=selected_families,
        family_runs=family_runs,
        success_state=success_state,
        priority_family_keys=priority_family_keys,
        args=args,
    )
    manifest_text = render_daily_manifest_md(manifest)

    output_root = args.artifact_root / run_id
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "manifest.json"
    manifest_md_path = output_root / "manifest.md"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_md_path.write_text(manifest_text, encoding="utf-8")

    daily_output_root = PROJECT_ROOT / "runs" / "learning-loops"
    daily_output_root.mkdir(parents=True, exist_ok=True)
    daily_json_path = daily_output_root / f"{run_id}.json"
    daily_md_path = daily_output_root / f"{run_id}.md"
    daily_json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    daily_md_path.write_text(manifest_text, encoding="utf-8")

    print(f"Daily run bundle: {output_root}")
    print(f"Daily manifest: {daily_json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

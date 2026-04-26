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

from alpha_mining_core import load_family_docs
from alpha_success_core import build_success_rate_state, normalize_family_key
from account_capability_core import build_account_capability_report, index_account_capability
from complexity_budget_core import build_complexity_budget_report, index_complexity_budget
from economic_distinctness_core import build_economic_distinctness_report, index_economic_distinctness
from evidence_ladder_core import build_evidence_ladder_report, index_evidence_ladder
from factor_risk_overlay_core import build_factor_risk_overlay_report, index_factor_risk_overlay
from field_readiness_core import build_field_readiness_report, index_field_readiness, load_field_search_packs
from mechanism_failure_memory_core import build_mechanism_failure_memory_report, index_mechanism_failure_memory
from research_allocator_core import allocate_family_records
from research_contract_core import build_research_contract_report, index_research_contract_report
from validation_design_core import build_validation_design_report, index_validation_design
from validation_provenance_core import build_validation_provenance_report, index_validation_provenance


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
        "--field-search-pack-dir",
        type=Path,
        default=Path("runs/field-search-packs"),
        help="Directory containing field-search-pack markdown docs.",
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
        "--coverage-floor-pct",
        type=float,
        default=70.0,
        help="Minimum required parseable coverage floor across usable candidate fields.",
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


def load_success_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Success policy not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Success policy must be a JSON object: {path}")
    return payload


def _factory_command(args: argparse.Namespace, topic: str, run_id: str) -> list[str]:
    command = [
        sys.executable,
        str(FACTORY_SCRIPT),
        "--family-dir",
        str(args.family_dir),
        "--field-search-pack-dir",
        str(args.field_search_pack_dir),
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
        "--coverage-floor-pct",
        str(args.coverage_floor_pct),
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
    excluded_families: Sequence[dict[str, Any]],
    allocator_deferred_families: Sequence[dict[str, Any]],
    field_readiness_report: dict[str, Any],
    account_capability_report: dict[str, Any],
    research_contract_report: dict[str, Any],
    validation_design_report: dict[str, Any],
    factor_risk_overlay_report: dict[str, Any],
    complexity_budget_report: dict[str, Any],
    mechanism_failure_memory_report: dict[str, Any],
    economic_distinctness_report: dict[str, Any],
    validation_provenance_report: dict[str, Any],
    evidence_ladder_report: dict[str, Any],
    research_allocator_report: dict[str, Any],
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
            "field_search_pack_dir": str(args.field_search_pack_dir),
            "coverage_floor_pct": args.coverage_floor_pct,
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
        "field_readiness": {
            "counts": dict(field_readiness_report.get("counts", {})),
        },
        "account_capability": {
            "counts": dict(account_capability_report.get("counts", {})),
            "profile": dict(account_capability_report.get("profile", {})),
            "top_blocked": [
                item
                for item in account_capability_report.get("items", [])
                if str(item.get("assessment", {}).get("gate_status") or "") != "pass"
            ][:10],
        },
        "research_contract": {
            "counts": dict(research_contract_report.get("counts", {})),
        },
        "validation_design": {
            "counts": dict(validation_design_report.get("counts", {})),
        },
        "factor_risk_overlay": {
            "counts": dict(factor_risk_overlay_report.get("counts", {})),
        },
        "complexity_budget": {
            "counts": dict(complexity_budget_report.get("counts", {})),
        },
        "mechanism_failure_memory": {
            "counts": dict(mechanism_failure_memory_report.get("counts", {})),
        },
        "economic_distinctness": {
            "counts": dict(economic_distinctness_report.get("counts", {})),
        },
        "validation_provenance": {
            "counts": dict(validation_provenance_report.get("counts", {})),
        },
        "evidence_ladder": {
            "counts": dict(evidence_ladder_report.get("counts", {})),
        },
        "research_allocator": {
            "counts": dict(research_allocator_report.get("counts", {})),
            "selected_family_keys": list(research_allocator_report.get("selected_family_keys", [])),
        },
        "selected_families": list(selected_families),
        "excluded_families": list(excluded_families),
        "allocator_deferred_families": list(allocator_deferred_families),
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
        f"- Excluded by front gate: {len(manifest.get('excluded_families', []))}",
        f"- Deferred by allocator: {len(manifest.get('allocator_deferred_families', []))}",
        f"- Family runs: {len(manifest.get('family_runs', []))}",
        f"- Daily budget items: {len(manifest.get('daily_budget_items', []))}",
        f"- Field-readiness pass count: {manifest.get('field_readiness', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Account-capability pass count: {manifest.get('account_capability', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Research-contract pass count: {manifest.get('research_contract', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Validation-design pass count: {manifest.get('validation_design', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Factor-risk-overlay pass count: {manifest.get('factor_risk_overlay', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Complexity-budget pass count: {manifest.get('complexity_budget', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Economic-distinctness pass count: {manifest.get('economic_distinctness', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Binding provenance families: {manifest.get('validation_provenance', {}).get('counts', {}).get('binding_family_count', 0)}",
        f"- E3/E4 evidence count: {manifest.get('evidence_ladder', {}).get('counts', {}).get('E3_full_is', 0) + manifest.get('evidence_ladder', {}).get('counts', {}).get('E4_submit_ready', 0)}",
        f"- Allocator selected count: {manifest.get('research_allocator', {}).get('counts', {}).get('selected_count', 0)}",
        "",
        "## Selected Families",
        "",
    ]
    for row in manifest.get("selected_families", []):
        lines.append(
            f"- {row['family_key']} [{row['state']}] "
            f"effective={row.get('effective_state')} "
            f"readiness={row.get('field_readiness_gate_status')} "
            f"capability={row.get('account_capability_gate_status')} "
            f"contract={row.get('research_contract_gate_status')} "
            f"validation={row.get('validation_design_gate_status')} "
            f"factor={row.get('factor_risk_overlay_gate_status')} "
            f"complexity={row.get('complexity_budget_gate_status')} "
            f"distinctness={row.get('economic_distinctness_gate_status')} "
            f"provenance={row.get('validation_provenance_level')} "
            f"allocator={row.get('research_allocator_status')} "
            f"evidence={row.get('evidence_ladder_level')} "
            f"outcomes={row['official_outcome_count']} full_gates={row['full_gate_outcome_count']} "
            f"submit_ready={row['submit_ready_count']}"
        )
    lines.append("")
    lines.append("## Front Gate Exclusions")
    lines.append("")
    if not manifest.get("excluded_families"):
        lines.append("- No selected family was excluded by the front gates.")
    else:
        for row in manifest.get("excluded_families", []):
            lines.append(
                f"- {row['family_key']} "
                f"readiness={row.get('field_readiness_gate_status')} "
                f"capability={row.get('account_capability_gate_status')} "
                f"contract={row.get('research_contract_gate_status')} "
                f"validation={row.get('validation_design_gate_status')} "
                f"factor={row.get('factor_risk_overlay_gate_status')} "
                f"complexity={row.get('complexity_budget_gate_status')} "
                f"distinctness={row.get('economic_distinctness_gate_status')} "
                f"evidence={row.get('evidence_ladder_level')}"
            )
            for reason in row.get("field_readiness_reasons", [])[:2]:
                lines.append(f"  - {reason}")
            for reason in row.get("account_capability_reasons", [])[:2]:
                lines.append(f"  - {reason}")
            for reason in row.get("research_contract_reasons", [])[:2]:
                lines.append(f"  - {reason}")
            for reason in row.get("validation_design_reasons", [])[:2]:
                lines.append(f"  - {reason}")
            for reason in row.get("factor_risk_overlay_reasons", [])[:2]:
                lines.append(f"  - {reason}")
            for reason in row.get("complexity_budget_reasons", [])[:2]:
                lines.append(f"  - {reason}")
            for reason in row.get("economic_distinctness_reasons", [])[:2]:
                lines.append(f"  - {reason}")
    lines.append("")
    lines.append("## Allocator Deferred")
    lines.append("")
    if not manifest.get("allocator_deferred_families"):
        lines.append("- No family was deferred by the research allocator.")
    else:
        for row in manifest.get("allocator_deferred_families", []):
            lines.append(
                f"- {row['family_key']} "
                f"allocator={row.get('research_allocator_status')} "
                f"reason={row.get('research_allocator_reason')} "
                f"cluster={row.get('allocator_cluster_key')}"
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
    success_policy = load_success_policy(args.success_policy)
    success_state = build_success_rate_state(
        family_dir=args.family_dir,
        capture_dir=args.capture_dir,
        candidate_batch_dir=args.candidate_batch_dir,
        candidate_check_dir=args.candidate_check_dir,
    )
    family_docs = load_family_docs(args.family_dir, include_dead=True)
    evidence_ladder_report = build_evidence_ladder_report(
        family_docs=family_docs,
        outcome_memory=success_state.get("combined_outcome_memory", []),
        family_registry=success_state.get("family_registry_summary", []),
    )
    evidence_by_family = index_evidence_ladder(evidence_ladder_report)
    registry_rows_with_evidence: list[dict[str, Any]] = []
    for row in success_state["family_registry_summary"]:
        family_key = str(row.get("family_key") or "")
        assessment = evidence_by_family.get(family_key, {}).get("assessment", {})
        enriched = dict(row)
        enriched["registry_state"] = str(row.get("state") or "explore")
        enriched["state"] = str(assessment.get("effective_state") or row.get("state") or "explore")
        enriched["effective_state"] = enriched["state"]
        enriched["evidence_ladder_level"] = assessment.get("evidence_level")
        enriched["evidence_promotion_ceiling"] = assessment.get("promotion_ceiling")
        enriched["evidence_branch_budget_remaining"] = assessment.get("branch_budget_remaining")
        registry_rows_with_evidence.append(enriched)
    selected_families = select_family_rows(
        registry_rows_with_evidence,
        allowed_states=allowed_states,
        explicit_family_filter=args.family_filter,
        priority_family_keys=priority_family_keys,
        family_limit=len(registry_rows_with_evidence),
    )

    if not selected_families:
        raise SystemExit("No families matched the current daily runner filters.")

    selected_family_keys = {
        str(family.get("family_key") or "")
        for family in selected_families
        if str(family.get("family_key") or "")
    }
    selected_docs = [
        doc
        for doc in family_docs
        if normalize_family_key(str(getattr(doc, "topic", "") or "")) in selected_family_keys
    ]
    field_packs = load_field_search_packs(args.field_search_pack_dir)
    selected_field_packs = [
        pack
        for pack in field_packs
        if str(getattr(pack, "family_key", "") or "") in selected_family_keys
    ]
    field_readiness_report = build_field_readiness_report(
        field_packs=selected_field_packs,
        family_docs=selected_docs,
        coverage_floor_pct=args.coverage_floor_pct,
    )
    research_contract_report = build_research_contract_report(family_docs=selected_docs)
    account_capability_report = build_account_capability_report(
        family_docs=selected_docs,
        research_contract_report=research_contract_report,
    )
    validation_design_report = build_validation_design_report(family_docs=selected_docs)
    factor_risk_overlay_report = build_factor_risk_overlay_report(
        family_docs=selected_docs,
        research_contract_report=research_contract_report,
        validation_design_report=validation_design_report,
    )
    complexity_budget_report = build_complexity_budget_report(
        family_docs=selected_docs,
        policy=success_policy,
    )
    mechanism_failure_memory_report = build_mechanism_failure_memory_report(
        family_docs=selected_docs,
        family_registry=success_state.get("family_registry_summary", []),
        research_contract_report=research_contract_report,
    )
    economic_distinctness_report = build_economic_distinctness_report(
        family_docs=selected_docs,
        research_contract_report=research_contract_report,
        mechanism_failure_memory_report=mechanism_failure_memory_report,
    )
    validation_provenance_report = build_validation_provenance_report(
        family_docs=selected_docs,
        outcome_memory=success_state.get("combined_outcome_memory", []),
        family_registry=success_state.get("family_registry_summary", []),
    )
    readiness_by_family = index_field_readiness(field_readiness_report)
    capability_by_family = index_account_capability(account_capability_report)
    contract_by_family = index_research_contract_report(research_contract_report)
    validation_design_by_family = index_validation_design(validation_design_report)
    factor_risk_by_family = index_factor_risk_overlay(factor_risk_overlay_report)
    complexity_by_family = index_complexity_budget(complexity_budget_report)
    failure_memory_by_family = index_mechanism_failure_memory(mechanism_failure_memory_report)
    distinctness_by_family = index_economic_distinctness(economic_distinctness_report)
    provenance_by_family = index_validation_provenance(validation_provenance_report)

    gate_selected_families: list[dict[str, Any]] = []
    excluded_families: list[dict[str, Any]] = []
    for family in selected_families:
        family_key = str(family.get("family_key") or "")
        readiness_entry = readiness_by_family.get(
            family_key,
            {
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["field-readiness record is missing for this family"],
                }
            },
        )
        capability_entry = capability_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "required_scope": {},
                "capability_snapshot": {
                    "observed_combo_count": 0,
                    "observed_regions": [],
                    "observed_delays": [],
                    "observed_universes": [],
                    "observed_categories": [],
                    "required_combo": None,
                    "matching_combo": None,
                    "public_tier_notes": [],
                },
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["account-capability record is missing for this family"],
                },
            },
        )
        contract_entry = contract_by_family.get(
            family_key,
            {
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["research-contract record is missing for this family"],
                }
            },
        )
        validation_design_entry = validation_design_by_family.get(
            family_key,
            {
                "validation_design": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["validation-design record is missing for this family"],
                },
            },
        )
        factor_risk_entry = factor_risk_by_family.get(
            family_key,
            {
                "factor_profile": {
                    "expected_risks": [],
                    "hypothesis_risks": [],
                    "overlay_risks": [],
                },
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["factor-risk-overlay record is missing for this family"],
                },
            },
        )
        complexity_entry = complexity_by_family.get(
            family_key,
            {
                "counts": {
                    "expression_count": 0,
                    "variant_expression_count": 0,
                },
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["complexity-budget record is missing for this family"],
                },
            },
        )
        failure_memory_entry = failure_memory_by_family.get(
            family_key,
            {
                "mechanism_profile": {},
                "assessment": {
                    "negative_memory_status": "none",
                    "negative_memory_rank": 0,
                    "reasons": ["mechanism-failure-memory record is missing for this family"],
                },
            },
        )
        distinctness_entry = distinctness_by_family.get(
            family_key,
            {
                "changed_axes": [],
                "field_overlap_pct": 0.0,
                "expression_similarity": 0.0,
                "nearest_negative_family": None,
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["economic-distinctness record is missing for this family"],
                },
            },
        )
        provenance_entry = provenance_by_family.get(
            family_key,
            {
                "counts": {
                    "official_outcome_count": 0,
                    "local_scored_count": 0,
                    "local_queue_count": 0,
                },
                "assessment": {
                    "gate_status": "pass",
                    "strongest_level": "front_gate_only",
                    "binding_status": "diagnostic",
                    "reasons": ["validation-provenance record is missing for this family"],
                },
            },
        )
        enriched = dict(family)
        enriched["field_readiness_gate_status"] = str(
            readiness_entry.get("assessment", {}).get("gate_status") or "block"
        )
        enriched["field_readiness_reasons"] = list(
            readiness_entry.get("assessment", {}).get("reasons", [])
        )
        enriched["account_capability_gate_status"] = str(
            capability_entry.get("assessment", {}).get("gate_status") or "block"
        )
        enriched["account_capability_reasons"] = list(
            capability_entry.get("assessment", {}).get("reasons", [])
        )
        enriched["account_capability_required_scope"] = dict(capability_entry.get("required_scope", {}))
        enriched["account_capability_observed_combo_count"] = int(
            capability_entry.get("capability_snapshot", {}).get("observed_combo_count", 0) or 0
        )
        enriched["account_capability_observed_regions"] = list(
            capability_entry.get("capability_snapshot", {}).get("observed_regions", [])
        )
        enriched["account_capability_observed_delays"] = list(
            capability_entry.get("capability_snapshot", {}).get("observed_delays", [])
        )
        enriched["account_capability_observed_universes"] = list(
            capability_entry.get("capability_snapshot", {}).get("observed_universes", [])
        )
        enriched["account_capability_observed_categories"] = list(
            capability_entry.get("capability_snapshot", {}).get("observed_categories", [])
        )
        enriched["research_contract_gate_status"] = str(
            contract_entry.get("assessment", {}).get("gate_status") or "block"
        )
        enriched["research_contract_reasons"] = list(
            contract_entry.get("assessment", {}).get("reasons", [])
        )
        enriched["research_contract_fields"] = dict(contract_entry.get("contract", {}))
        enriched["validation_design_gate_status"] = str(
            validation_design_entry.get("assessment", {}).get("gate_status") or "block"
        )
        enriched["validation_design_reasons"] = list(
            validation_design_entry.get("assessment", {}).get("reasons", [])
        )
        enriched["validation_design_fields"] = dict(validation_design_entry.get("validation_design", {}))
        enriched["factor_risk_overlay_gate_status"] = str(
            factor_risk_entry.get("assessment", {}).get("gate_status") or "block"
        )
        enriched["factor_risk_overlay_reasons"] = list(
            factor_risk_entry.get("assessment", {}).get("reasons", [])
        )
        enriched["factor_risk_overlay_expected_risks"] = list(
            factor_risk_entry.get("factor_profile", {}).get("expected_risks", [])
        )
        enriched["factor_risk_overlay_hypothesis_risks"] = list(
            factor_risk_entry.get("factor_profile", {}).get("hypothesis_risks", [])
        )
        enriched["factor_risk_overlay_overlay_risks"] = list(
            factor_risk_entry.get("factor_profile", {}).get("overlay_risks", [])
        )
        enriched["complexity_budget_gate_status"] = str(
            complexity_entry.get("assessment", {}).get("gate_status") or "block"
        )
        enriched["complexity_budget_reasons"] = list(
            complexity_entry.get("assessment", {}).get("reasons", [])
        )
        enriched["complexity_budget_expression_count"] = int(
            complexity_entry.get("counts", {}).get("expression_count", 0) or 0
        )
        enriched["complexity_budget_variant_expression_count"] = int(
            complexity_entry.get("counts", {}).get("variant_expression_count", 0) or 0
        )
        enriched["mechanism_failure_memory_status"] = failure_memory_entry.get("assessment", {}).get("negative_memory_status")
        enriched["mechanism_failure_memory_rank"] = failure_memory_entry.get("assessment", {}).get("negative_memory_rank")
        enriched["mechanism_failure_memory_reasons"] = list(
            failure_memory_entry.get("assessment", {}).get("reasons", [])
        )
        enriched["mechanism_failure_memory_cluster"] = failure_memory_entry.get("mechanism_profile", {}).get("mechanism_cluster")
        enriched["economic_distinctness_gate_status"] = str(
            distinctness_entry.get("assessment", {}).get("gate_status") or "block"
        )
        enriched["economic_distinctness_reasons"] = list(
            distinctness_entry.get("assessment", {}).get("reasons", [])
        )
        enriched["economic_distinctness_nearest_negative_family"] = distinctness_entry.get("nearest_negative_family")
        enriched["economic_distinctness_changed_axes"] = list(distinctness_entry.get("changed_axes", []))
        enriched["economic_distinctness_field_overlap_pct"] = distinctness_entry.get("field_overlap_pct")
        enriched["economic_distinctness_expression_similarity"] = distinctness_entry.get("expression_similarity")
        enriched["validation_provenance_gate_status"] = str(
            provenance_entry.get("assessment", {}).get("gate_status") or "pass"
        )
        enriched["validation_provenance_level"] = provenance_entry.get("assessment", {}).get("strongest_level")
        enriched["validation_provenance_binding_status"] = provenance_entry.get("assessment", {}).get("binding_status")
        enriched["validation_provenance_reasons"] = list(
            provenance_entry.get("assessment", {}).get("reasons", [])
        )
        evidence_entry = evidence_by_family.get(family_key, {})
        evidence_assessment = evidence_entry.get("assessment", {}) if isinstance(evidence_entry, dict) else {}
        enriched["effective_state"] = str(
            evidence_assessment.get("effective_state") or enriched.get("state") or "explore"
        )
        enriched["evidence_ladder_level"] = evidence_assessment.get("evidence_level")
        enriched["evidence_promotion_ceiling"] = evidence_assessment.get("promotion_ceiling")
        enriched["evidence_branch_budget_remaining"] = evidence_assessment.get("branch_budget_remaining")
        enriched["allocator_state_allowed"] = enriched["effective_state"] in allowed_states
        if (
            enriched["field_readiness_gate_status"] == "pass"
            and enriched["account_capability_gate_status"] == "pass"
            and enriched["research_contract_gate_status"] == "pass"
            and enriched["validation_design_gate_status"] == "pass"
            and enriched["factor_risk_overlay_gate_status"] == "pass"
            and enriched["complexity_budget_gate_status"] == "pass"
            and enriched["economic_distinctness_gate_status"] == "pass"
        ):
            gate_selected_families.append(enriched)
        else:
            excluded_families.append(enriched)

    if not gate_selected_families:
        raise SystemExit("No families matched the current daily runner filters after front-gate checks.")

    research_allocator_report = allocate_family_records(
        records=gate_selected_families,
        family_limit=args.family_limit,
        policy=success_policy,
    )
    selected_families = list(research_allocator_report.get("selected_items", []))
    allocator_deferred_families = [
        row
        for row in research_allocator_report.get("items", [])
        if str(row.get("research_allocator_status") or "").startswith("deferred")
    ]

    if not selected_families:
        raise SystemExit("No family survived the research allocator in the current daily runner filters.")

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
        excluded_families=excluded_families,
        allocator_deferred_families=allocator_deferred_families,
        field_readiness_report=field_readiness_report,
        account_capability_report=account_capability_report,
        research_contract_report=research_contract_report,
        validation_design_report=validation_design_report,
        factor_risk_overlay_report=factor_risk_overlay_report,
        complexity_budget_report=complexity_budget_report,
        mechanism_failure_memory_report=mechanism_failure_memory_report,
        economic_distinctness_report=economic_distinctness_report,
        validation_provenance_report=validation_provenance_report,
        evidence_ladder_report=evidence_ladder_report,
        research_allocator_report=research_allocator_report,
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

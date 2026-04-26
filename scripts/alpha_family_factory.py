#!/usr/bin/env python3
"""Run a constrained local family-factory mining cycle.

This orchestrator keeps the professional separation of concerns:

- local scripts do the heavy candidate generation and pruning
- official simulate is treated as a scarce budget, not as the search engine
- family-level summaries and a micro-batch budget are produced explicitly

The script reuses the existing miner / scorecard / queue helpers and adds:

- topic-aware family filtering
- one-shot artifact bundle generation
- family action summaries
- a budgeted official test recommendation list
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from alpha_batch_miner import build_candidate_pool
from alpha_mining_core import (
    ParsedCapture,
    ParsedFamilyDoc,
    build_expression_bank,
    canonicalize_expression,
    dump_json,
    load_captures,
    load_family_docs,
    load_token_replacements,
    similarity_score,
    summarise_capture,
    summarise_family,
    write_jsonl,
)
from alpha_success_core import (
    build_combined_outcome_memory,
    build_family_registry_summary,
    build_submit_ready_ledger,
    normalize_family_key,
)
from complexity_budget_core import (
    build_complexity_budget_report,
    index_complexity_budget,
    render_complexity_budget_md,
)
from economic_distinctness_core import (
    build_economic_distinctness_report,
    index_economic_distinctness,
    render_economic_distinctness_md,
)
from factor_risk_overlay_core import (
    build_factor_risk_overlay_report,
    index_factor_risk_overlay,
    render_factor_risk_overlay_md,
)
from account_capability_core import (
    build_account_capability_report,
    index_account_capability,
    render_account_capability_md,
)
from candidate_scorecard import (
    attach_scorecard,
    build_capture_index,
    build_family_index,
    build_summary as build_score_summary,
    family_population,
)
from research_queue_builder import (
    build_queue_item,
    build_queue_document,
    build_summary as build_queue_summary,
    should_keep_candidate,
)
from field_readiness_core import (
    DEFAULT_COVERAGE_FLOOR_PCT,
    build_field_readiness_report,
    index_field_readiness,
    load_field_search_packs,
    render_field_readiness_md,
)
from evidence_ladder_core import (
    build_evidence_ladder_report,
    index_evidence_ladder,
    render_evidence_ladder_md,
)
from mechanism_failure_memory_core import (
    build_mechanism_failure_memory_report,
    index_mechanism_failure_memory,
    render_mechanism_failure_memory_md,
)
from research_contract_core import (
    build_research_contract_report,
    index_research_contract_report,
    render_research_contract_md,
)
from validation_design_core import (
    build_validation_design_report,
    index_validation_design,
    render_validation_design_md,
)
from validation_provenance_core import (
    build_validation_provenance_report,
    index_validation_provenance,
    render_validation_provenance_md,
)


DEFAULT_ARTIFACT_ROOT = Path("harness/artifacts/alpha-mining")
DEFAULT_SUCCESS_POLICY = Path("harness/alpha-success-policy.json")
STATE_PRIORITY = {"exploit": 0, "branch": 1, "explore": 2, "hold": 3, "kill": 4}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local family-factory alpha mining cycle.")
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
        help="Directory containing durable candidate-batch JSON artifacts with linked real evidence.",
    )
    parser.add_argument(
        "--success-policy",
        type=Path,
        default=DEFAULT_SUCCESS_POLICY,
        help="Success-rate-first policy JSON used for official budget triage.",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=DEFAULT_ARTIFACT_ROOT,
        help="Parent directory for the generated local artifact bundle.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id. Defaults to YYYY-MM-DD-family-factory.",
    )
    parser.add_argument(
        "--token-map",
        type=Path,
        action="append",
        default=[],
        help="Optional JSON token map. Repeat to merge multiple maps.",
    )
    parser.add_argument(
        "--include-topic",
        action="append",
        default=[],
        help="Regex filter for family topics/titles/paths. Repeat for multiple filters.",
    )
    parser.add_argument(
        "--exclude-topic",
        action="append",
        default=[],
        help="Regex filter for families that must be skipped.",
    )
    parser.add_argument(
        "--include-dead",
        action="store_true",
        help="Include family docs already marked dead. Off by default.",
    )
    parser.add_argument(
        "--coverage-floor-pct",
        type=float,
        default=DEFAULT_COVERAGE_FLOOR_PCT,
        help="Minimum required parseable coverage floor across usable candidate fields.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=1500,
        help="Hard cap on emitted local candidates.",
    )
    parser.add_argument(
        "--per-seed",
        type=int,
        default=64,
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
        "--seed-limit",
        type=int,
        default=0,
        help="Optional limit on how many seed docs to process.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=62.0,
        help="Minimum local score needed for queue consideration.",
    )
    parser.add_argument(
        "--max-total",
        type=int,
        default=24,
        help="Maximum number of items to keep in the final local queue.",
    )
    parser.add_argument(
        "--max-per-family",
        type=int,
        default=3,
        help="Maximum number of local queue items per family.",
    )
    parser.add_argument(
        "--max-per-template",
        type=int,
        default=2,
        help="Maximum number of queue items sharing the same template_id.",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.94,
        help="Reject a queue candidate if it is too similar to an already selected queue item.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("templates/research-queue.template.json"),
        help="Optional queue template JSON to copy structure from.",
    )
    parser.add_argument(
        "--official-budget",
        type=int,
        default=None,
        help="Maximum number of recommended official simulate slots. Defaults to the success policy.",
    )
    parser.add_argument(
        "--max-official-per-family",
        type=int,
        default=None,
        help="Maximum number of official budget slots per family. Defaults to the success policy.",
    )
    parser.add_argument(
        "--official-similarity-threshold",
        type=float,
        default=None,
        help="Minimum expression dissimilarity required between official slot picks. Defaults to the success policy.",
    )
    parser.add_argument(
        "--publish-queue",
        action="store_true",
        help="Write the queue summary into runs/research-queues/<run-id>.json/.md as a durable output.",
    )
    parser.add_argument(
        "--publish-root",
        type=Path,
        default=Path("runs/research-queues"),
        help="Durable output root used when --publish-queue is set.",
    )
    return parser.parse_args()


def default_run_id(args: argparse.Namespace) -> str:
    if args.run_id:
        return args.run_id
    return f"{datetime.now().strftime('%Y-%m-%d')}-family-factory"


def compile_patterns(patterns: Sequence[str]) -> tuple[re.Pattern[str], ...]:
    compiled: list[re.Pattern[str]] = []
    for pattern in patterns:
        compiled.append(re.compile(pattern, re.IGNORECASE))
    return tuple(compiled)


def family_match_text(doc: ParsedFamilyDoc) -> str:
    return "\n".join(
        (
            doc.topic,
            doc.title,
            str(doc.path),
            doc.path.name,
            doc.category,
        )
    )


def should_include_family(
    doc: ParsedFamilyDoc,
    *,
    include_patterns: Sequence[re.Pattern[str]],
    exclude_patterns: Sequence[re.Pattern[str]],
    include_dead: bool,
) -> bool:
    if doc.is_dead and not include_dead:
        return False

    haystack = family_match_text(doc)
    if include_patterns and not any(pattern.search(haystack) for pattern in include_patterns):
        return False
    if exclude_patterns and any(pattern.search(haystack) for pattern in exclude_patterns):
        return False
    return True


def merge_token_rules(paths: Sequence[Path]) -> tuple[dict[str, Any], ...]:
    merged: list[dict[str, Any]] = []
    for path in paths:
        merged.extend(load_token_replacements(path))
    return tuple(merged)


def load_success_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Success policy not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Success policy must be a JSON object: {path}")
    return data


def resolve_success_budget_args(args: argparse.Namespace, policy: dict[str, Any]) -> None:
    budget = policy.get("budget") if isinstance(policy.get("budget"), dict) else {}
    args.official_budget = (
        args.official_budget
        if args.official_budget is not None
        else int(budget.get("official_budget", 8))
    )
    args.max_official_per_family = (
        args.max_official_per_family
        if args.max_official_per_family is not None
        else int(budget.get("max_official_per_family", 2))
    )
    args.official_similarity_threshold = (
        args.official_similarity_threshold
        if args.official_similarity_threshold is not None
        else float(budget.get("official_similarity_threshold", 0.88))
    )


def family_key_for_topic(topic: str) -> str:
    return normalize_family_key(topic or "unknown")


def best_outcome_similarity(
    expression: str,
    outcomes: Sequence[dict[str, Any]],
) -> tuple[float, dict[str, Any] | None]:
    best_score = 0.0
    best_match: dict[str, Any] | None = None
    canonical = canonicalize_expression(expression)
    for outcome in outcomes:
        outcome_expression = canonicalize_expression(str(outcome.get("expression") or ""))
        if not outcome_expression:
            continue
        score = similarity_score(canonical, outcome_expression)
        if score > best_score:
            best_score = score
            best_match = outcome
    return best_score, best_match


def failure_similarity_penalty(similarity: float, priors: dict[str, Any]) -> float:
    start = float(priors.get("fail_similarity_penalty_start", 0.55))
    hard_drop = float(priors.get("fail_similarity_hard_drop", 0.82))
    if similarity < start:
        return 0.0
    width = max(0.01, hard_drop - start)
    capped = min(similarity, hard_drop)
    scaled = (capped - start) / width
    penalty = scaled * 20.0
    if similarity >= hard_drop:
        penalty += 35.0
    return penalty


def gate_penalty(failing_gates: Sequence[str], priors: dict[str, Any]) -> float:
    penalties = {
        "LOW_SHARPE": float(priors.get("low_sharpe_penalty", 0.0)),
        "LOW_FITNESS": float(priors.get("low_fitness_penalty", 0.0)),
        "LOW_SUB_UNIVERSE_SHARPE": float(priors.get("low_sub_universe_penalty", 0.0)),
        "SELF_CORRELATION": float(priors.get("self_correlation_penalty", 0.0)),
    }
    return sum(penalties.get(gate, 0.0) for gate in failing_gates)


def enrich_records_with_success_priors(
    records: Sequence[dict[str, Any]],
    *,
    family_registry: Sequence[dict[str, Any]],
    outcome_memory: Sequence[dict[str, Any]],
    submit_ready_ledger: Sequence[dict[str, Any]],
    policy: dict[str, Any],
    evidence_ladder_by_family: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    registry_by_key = {
        str(item.get("family_key") or ""): item
        for item in family_registry
    }
    submit_ready_count_by_family: dict[str, int] = defaultdict(int)
    for entry in submit_ready_ledger:
        submit_ready_count_by_family[str(entry.get("family_key") or "")] += 1

    failure_checks = {
        str(check).upper()
        for check in policy.get("failure_checks", [])
        if isinstance(check, str)
    }
    priors = policy.get("priors") if isinstance(policy.get("priors"), dict) else {}

    failed_outcomes_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for outcome in outcome_memory:
        family_key = str(outcome.get("family_key") or "")
        failing_gates = [
            gate
            for gate in outcome.get("failing_gates", [])
            if str(gate).upper() in failure_checks
        ]
        if failing_gates:
            failed_outcomes_by_family[family_key].append(outcome)

    enriched: list[dict[str, Any]] = []
    for record in records:
        family_topic = str(record.get("family_topic") or "unknown")
        family_key = family_key_for_topic(family_topic)
        registry_entry = registry_by_key.get(family_key, {})
        ladder_entry = (evidence_ladder_by_family or {}).get(family_key, {})
        ladder_assessment = ladder_entry.get("assessment", {}) if isinstance(ladder_entry, dict) else {}
        family_state = str(
            ladder_assessment.get("effective_state")
            or registry_entry.get("state")
            or "explore"
        )
        registry_state = str(registry_entry.get("state") or "explore")
        family_reason = str(registry_entry.get("reason") or "no family registry evidence")
        same_family_failed_outcomes = failed_outcomes_by_family.get(family_key, [])
        failure_similarity, failure_match = best_outcome_similarity(
            str(record.get("expression") or ""),
            same_family_failed_outcomes,
        )
        matched_failing_gates = tuple(failure_match.get("failing_gates", [])) if failure_match else tuple()
        state_adjustment = {
            "exploit": float(priors.get("exploit_state_bonus", 12.0)),
            "branch": float(priors.get("branch_state_bonus", 6.0)),
            "hold": -float(priors.get("hold_state_penalty", 18.0)),
            "kill": -float(priors.get("kill_state_penalty", 100.0)),
        }.get(family_state, 0.0)
        submit_ready_bonus = (
            float(priors.get("submit_ready_bonus", 20.0))
            if submit_ready_count_by_family.get(family_key, 0) > 0
            else 0.0
        )
        penalty = gate_penalty(matched_failing_gates, priors) + failure_similarity_penalty(failure_similarity, priors)
        gate_likelihood_score = round(float(record["scorecard"]["score"]) + state_adjustment + submit_ready_bonus - penalty, 2)
        hard_blocked = family_state == "kill" or failure_similarity >= float(priors.get("fail_similarity_hard_drop", 0.82))

        enriched_record = dict(record)
        enriched_record["success_prior"] = {
            "family_key": family_key,
            "family_state": family_state,
            "registry_state": registry_state,
            "family_state_reason": family_reason,
            "family_submit_ready_count": submit_ready_count_by_family.get(family_key, 0),
            "family_official_outcome_count": int(registry_entry.get("official_outcome_count", 0) or 0),
            "family_full_gate_outcome_count": int(registry_entry.get("full_gate_outcome_count", 0) or 0),
            "evidence_ladder_level": ladder_assessment.get("evidence_level"),
            "evidence_promotion_ceiling": ladder_assessment.get("promotion_ceiling"),
            "branch_budget_remaining": ladder_assessment.get("branch_budget_remaining"),
            "failure_similarity": round(failure_similarity, 4),
            "failure_match_capture_id": failure_match.get("capture_id") if failure_match else None,
            "failure_match_expression": failure_match.get("expression") if failure_match else None,
            "failure_match_failing_gates": list(matched_failing_gates),
            "gate_likelihood_score": gate_likelihood_score,
            "hard_blocked": hard_blocked,
        }
        enriched.append(enriched_record)

    enriched.sort(
        key=lambda record: (
            -float(record["success_prior"]["gate_likelihood_score"]),
            -float(record["scorecard"]["score"]),
            int(record.get("mutation_depth", 0)),
            str(record.get("candidate_id") or ""),
        )
    )
    return enriched


def queue_rank_key(record: dict[str, Any]) -> tuple[Any, ...]:
    success_prior = record.get("success_prior", {})
    scorecard = record["scorecard"]
    return (
        1 if success_prior.get("hard_blocked") else 0,
        -float(success_prior.get("gate_likelihood_score", -9999.0)),
        -float(scorecard["score"]),
        int(record.get("mutation_depth", 0)),
        -float(scorecard.get("health_score", 0.0)),
        str(record.get("candidate_id") or ""),
    )


def build_success_queue_item(record: dict[str, Any]) -> dict[str, Any]:
    item = build_queue_item(record)
    success_prior = record.get("success_prior", {})
    item["local_score"] = round(float(record["scorecard"]["score"]), 2)
    item["gate_likelihood_score"] = success_prior.get("gate_likelihood_score")
    item["family_state"] = success_prior.get("family_state")
    item["failure_similarity"] = success_prior.get("failure_similarity")
    item["hard_blocked"] = success_prior.get("hard_blocked")
    item["notes"] = (
        f"{item['notes']}; family_state={success_prior.get('family_state')}; "
        f"gate_score={success_prior.get('gate_likelihood_score')}; "
        f"failure_similarity={success_prior.get('failure_similarity')}"
    )
    return item


def select_queue_with_success_priors(
    records: Sequence[dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    sorted_records = sorted(records, key=queue_rank_key)

    selected: list[dict[str, Any]] = []
    reasons: dict[str, str] = {}
    family_counts: dict[str, int] = defaultdict(int)
    template_counts: dict[str, int] = defaultdict(int)

    best_by_family: dict[str, dict[str, Any]] = {}
    for record in sorted_records:
        key = str(record.get("candidate_id") or record.get("expression"))
        if record.get("success_prior", {}).get("hard_blocked"):
            reasons[key] = "success_hard_block"
            continue
        family = str(record.get("family_topic") or "unknown")
        current = best_by_family.get(family)
        if current is None or queue_rank_key(record) < queue_rank_key(current):
            best_by_family[family] = record

    for family, record in sorted(best_by_family.items(), key=lambda item: queue_rank_key(item[1])):
        if len(selected) >= args.max_total:
            break
        keep, reason = should_keep_candidate(record, selected, family_counts, template_counts, args)
        key = str(record.get("candidate_id") or record.get("expression"))
        if not keep:
            reasons[key] = reason
            continue
        selected.append(build_success_queue_item(record))
        family_counts[family] += 1
        template_counts[str(record.get("template_id") or "baseline")] += 1
        reasons[key] = "anchor"

    for record in sorted_records:
        if len(selected) >= args.max_total:
            break
        key = str(record.get("candidate_id") or record.get("expression"))
        if key in reasons:
            continue
        if record.get("success_prior", {}).get("hard_blocked"):
            reasons[key] = "success_hard_block"
            continue
        family = str(record.get("family_topic") or "unknown")
        template_id = str(record.get("template_id") or "baseline")
        keep, reason = should_keep_candidate(record, selected, family_counts, template_counts, args)
        if not keep:
            reasons[key] = reason
            continue
        selected.append(build_success_queue_item(record))
        family_counts[family] += 1
        template_counts[template_id] += 1
        reasons[key] = "accepted"

    return selected, reasons


def candidate_sort_key(record: dict[str, Any]) -> tuple[Any, ...]:
    scorecard = record["scorecard"]
    return (
        -float(scorecard["score"]),
        int(record.get("mutation_depth", 0)),
        -float(scorecard.get("health_score", 0.0)),
        -float(scorecard.get("family_fit_score", 0.0)),
        str(record.get("candidate_id") or ""),
    )


def anchor_sort_key(record: dict[str, Any]) -> tuple[Any, ...]:
    template_id = str(record.get("template_id") or "baseline")
    mutation_depth = int(record.get("mutation_depth", 0))
    return (
        0 if mutation_depth <= 0 else 1,
        0 if template_id == "baseline" else 1,
        -float(record["scorecard"]["score"]),
        mutation_depth,
        str(record.get("candidate_id") or ""),
    )


def score_candidates(
    candidates: Sequence[dict[str, Any]],
    *,
    family_docs: Sequence[ParsedFamilyDoc],
    captures: Sequence[ParsedCapture],
    bank: dict[str, list[str]],
    min_score: float,
) -> list[dict[str, Any]]:
    family_index = build_family_index(tuple(family_docs))
    capture_index = build_capture_index(tuple(captures))
    scored_records: list[dict[str, Any]] = []

    for record in candidates:
        family_doc = family_index.get(str(record.get("family_topic") or ""))
        if family_doc is None and record.get("source_doc"):
            source_doc = Path(str(record["source_doc"]))
            family_doc = (
                family_index.get(source_doc.name)
                or family_index.get(source_doc.stem)
                or family_index.get(str(source_doc))
            )

        seed_population = family_population(family_doc)
        if not seed_population and record.get("source_expression"):
            seed_population = [canonicalize_expression(str(record["source_expression"]))]

        scored = attach_scorecard(
            dict(record),
            family_doc,
            dead_population=bank["dead"],
            history_population=bank["history"] + capture_index["history"],
            seed_population=seed_population,
            min_score=min_score,
        )
        scored_records.append(scored)

    scored_records.sort(key=candidate_sort_key)
    return scored_records


def write_scored_csv(records: Sequence[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "candidate_id",
                "family_topic",
                "family_category",
                "template_id",
                "mutation_depth",
                "score",
                "health_score",
                "convergence_score",
                "novelty_score",
                "family_fit_score",
                "stability_score",
                "overfit_risk",
                "coupling_risk",
                "family_state",
                "gate_likelihood_score",
                "failure_similarity",
                "hard_blocked",
                "decision",
                "expression",
                "source_doc",
                "mutations",
            ],
        )
        writer.writeheader()
        for record in records:
            scorecard = record["scorecard"]
            success_prior = record.get("success_prior", {})
            writer.writerow(
                {
                    "candidate_id": record.get("candidate_id"),
                    "family_topic": record.get("family_topic"),
                    "family_category": record.get("family_category"),
                    "template_id": record.get("template_id"),
                    "mutation_depth": record.get("mutation_depth"),
                    "score": scorecard["score"],
                    "health_score": scorecard["health_score"],
                    "convergence_score": scorecard["convergence_score"],
                    "novelty_score": scorecard["novelty_score"],
                    "family_fit_score": scorecard["family_fit_score"],
                    "stability_score": scorecard["stability_score"],
                    "overfit_risk": scorecard["overfit_risk"],
                    "coupling_risk": scorecard["coupling_risk"],
                    "family_state": success_prior.get("family_state"),
                    "gate_likelihood_score": success_prior.get("gate_likelihood_score"),
                    "failure_similarity": success_prior.get("failure_similarity"),
                    "hard_blocked": success_prior.get("hard_blocked"),
                    "decision": scorecard["decision"],
                    "expression": record.get("expression"),
                    "source_doc": record.get("source_doc"),
                    "mutations": " | ".join(record.get("mutations", [])),
                }
            )


def captures_for_family(
    family: ParsedFamilyDoc,
    captures: Sequence[ParsedCapture],
) -> list[ParsedCapture]:
    matched: list[ParsedCapture] = []
    family_topic = family.topic.lower()
    family_name = family.path.stem.lower()
    for capture in captures:
        topic = (capture.topic or "").lower()
        path_name = capture.path.stem.lower()
        if topic == family_topic or topic == family_name:
            matched.append(capture)
            continue
        if family_topic and family_topic in topic:
            matched.append(capture)
            continue
        if family_name and family_name in path_name:
            matched.append(capture)
    return matched


def score_from_item(item: dict[str, Any]) -> float:
    if item.get("gate_likelihood_score") is not None:
        return float(item["gate_likelihood_score"])
    return float(item.get("score", 0.0))


def family_action(
    family: ParsedFamilyDoc,
    selected_count: int,
    *,
    live_capture_count: int,
    dead_capture_count: int,
    check_submission_count: int,
) -> str:
    if family.is_dead:
        return "kill"
    if selected_count <= 0:
        if dead_capture_count > 0 and live_capture_count <= 0:
            return "hold"
        return "explore"
    if check_submission_count > 0:
        return "exploit"
    if live_capture_count > 0:
        return "branch"
    return "explore"


def family_next_step(action: str) -> str:
    if action == "kill":
        return "Do not schedule this family again unless fresh external evidence materially changes the template."
    if action == "hold":
        return "Pause official testing. Only resume if a materially different same-family template earns new local support."
    if action == "exploit":
        return "Spend scarce official slots only on the anchor plus one orthogonal follow-up."
    if action == "branch":
        return "Keep one anchor and one structurally different follow-up in the next micro-batch."
    return "Run one clean anchor first, then add only one control if the anchor looks healthy."


def build_family_summary_records(
    families: Sequence[ParsedFamilyDoc],
    captures: Sequence[ParsedCapture],
    scored_records: Sequence[dict[str, Any]],
    queue_items: Sequence[dict[str, Any]],
    *,
    family_registry: Sequence[dict[str, Any]],
    field_readiness_by_family: dict[str, dict[str, Any]],
    account_capability_by_family: dict[str, dict[str, Any]],
    research_contract_by_family: dict[str, dict[str, Any]],
    validation_design_by_family: dict[str, dict[str, Any]],
    factor_risk_overlay_by_family: dict[str, dict[str, Any]],
    complexity_budget_by_family: dict[str, dict[str, Any]],
    mechanism_failure_memory_by_family: dict[str, dict[str, Any]],
    economic_distinctness_by_family: dict[str, dict[str, Any]],
    validation_provenance_by_family: dict[str, dict[str, Any]],
    evidence_ladder_by_family: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    registry_by_key = {
        str(item.get("family_key") or ""): item
        for item in family_registry
    }
    scored_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in scored_records:
        scored_by_family[str(record.get("family_topic") or "unknown")].append(record)

    queue_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in queue_items:
        queue_by_family[str(item.get("family_topic") or "unknown")].append(item)

    summaries: list[dict[str, Any]] = []
    for family in sorted(families, key=lambda doc: doc.topic):
        family_captures = captures_for_family(family, captures)
        live_capture_count = sum(1 for capture in family_captures if not capture.is_dead)
        dead_capture_count = sum(1 for capture in family_captures if capture.is_dead)
        check_submission_count = sum(1 for capture in family_captures if capture.has_check_submission)
        family_scored = sorted(scored_by_family.get(family.topic, []), key=candidate_sort_key)
        family_queue = sorted(queue_by_family.get(family.topic, []), key=lambda item: (-score_from_item(item), str(item.get("candidate_id"))))
        family_key = family_key_for_topic(family.topic)
        registry_entry = registry_by_key.get(family_key, {})
        readiness_entry = field_readiness_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "candidate_fields": [],
                "usable_candidate_fields": [],
                "blocked_candidate_fields": [],
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["field-readiness record is missing for this family"],
                },
            },
        )
        capability_entry = account_capability_by_family.get(
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
        contract_entry = research_contract_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "contract": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["research-contract record is missing for this family"],
                },
            },
        )
        validation_design_entry = validation_design_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "validation_design": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["validation-design record is missing for this family"],
                },
            },
        )
        factor_risk_entry = factor_risk_overlay_by_family.get(
            family_key,
            {
                "family_key": family_key,
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
        complexity_entry = complexity_budget_by_family.get(
            family_key,
            {
                "family_key": family_key,
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
        failure_memory_entry = mechanism_failure_memory_by_family.get(
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
        distinctness_entry = economic_distinctness_by_family.get(
            family_key,
            {
                "nearest_negative_family": None,
                "changed_axes": [],
                "field_overlap_pct": 0.0,
                "expression_similarity": 0.0,
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["economic-distinctness record is missing for this family"],
                },
            },
        )
        provenance_entry = validation_provenance_by_family.get(
            family_key,
            {
                "family_key": family_key,
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
        evidence_entry = evidence_ladder_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "assessment": {
                    "evidence_level": "E0_front_gate_only",
                    "promotion_ceiling": "explore",
                    "effective_state": "explore",
                    "branch_budget_remaining": 0,
                    "official_budget_cap": 1,
                    "reasons": ["evidence-ladder record is missing for this family"],
                },
            },
        )
        readiness_assessment = readiness_entry.get("assessment", {})
        capability_assessment = capability_entry.get("assessment", {})
        contract_assessment = contract_entry.get("assessment", {})
        validation_design_assessment = validation_design_entry.get("assessment", {})
        factor_risk_assessment = factor_risk_entry.get("assessment", {})
        complexity_assessment = complexity_entry.get("assessment", {})
        failure_memory_assessment = failure_memory_entry.get("assessment", {})
        distinctness_assessment = distinctness_entry.get("assessment", {})
        provenance_assessment = provenance_entry.get("assessment", {})
        evidence_assessment = evidence_entry.get("assessment", {})

        best_local = family_scored[0] if family_scored else None
        local_action = family_action(
            family,
            len(family_queue),
            live_capture_count=live_capture_count,
            dead_capture_count=dead_capture_count,
            check_submission_count=check_submission_count,
        )
        registry_state = str(registry_entry.get("state") or "explore")
        effective_state = str(evidence_assessment.get("effective_state") or registry_state)
        readiness_gate_status = str(readiness_assessment.get("gate_status") or "block")
        capability_gate_status = str(capability_assessment.get("gate_status") or "block")
        contract_gate_status = str(contract_assessment.get("gate_status") or "block")
        validation_design_gate_status = str(validation_design_assessment.get("gate_status") or "block")
        factor_risk_gate_status = str(factor_risk_assessment.get("gate_status") or "block")
        complexity_gate_status = str(complexity_assessment.get("gate_status") or "block")
        distinctness_gate_status = str(distinctness_assessment.get("gate_status") or "block")
        if family.is_dead:
            action = "kill"
        elif (
            readiness_gate_status != "pass"
            or capability_gate_status != "pass"
            or contract_gate_status != "pass"
            or validation_design_gate_status != "pass"
            or factor_risk_gate_status != "pass"
            or complexity_gate_status != "pass"
            or distinctness_gate_status != "pass"
        ):
            action = "hold"
        else:
            action = effective_state if effective_state != "explore" else local_action
        best_gate_likelihood = None
        if best_local and isinstance(best_local.get("success_prior"), dict):
            best_gate_likelihood = best_local["success_prior"].get("gate_likelihood_score")
        if family.is_dead:
            next_step = family_next_step(action)
        elif (
            readiness_gate_status != "pass"
            or capability_gate_status != "pass"
            or contract_gate_status != "pass"
            or validation_design_gate_status != "pass"
            or factor_risk_gate_status != "pass"
            or complexity_gate_status != "pass"
            or distinctness_gate_status != "pass"
        ):
            gate_messages: list[str] = []
            if readiness_gate_status != "pass":
                gate_messages.append(
                    "field-readiness: " + "; ".join(readiness_assessment.get("reasons", [])[:2])
                )
            if capability_gate_status != "pass":
                gate_messages.append(
                    "account-capability: " + "; ".join(capability_assessment.get("reasons", [])[:2])
                )
            if contract_gate_status != "pass":
                gate_messages.append(
                    "research-contract: " + "; ".join(contract_assessment.get("reasons", [])[:2])
                )
            if validation_design_gate_status != "pass":
                gate_messages.append(
                    "validation-design: " + "; ".join(validation_design_assessment.get("reasons", [])[:2])
                )
            if factor_risk_gate_status != "pass":
                gate_messages.append(
                    "factor-risk-overlay: " + "; ".join(factor_risk_assessment.get("reasons", [])[:2])
                )
            if complexity_gate_status != "pass":
                gate_messages.append(
                    "complexity-budget: " + "; ".join(complexity_assessment.get("reasons", [])[:2])
                )
            if distinctness_gate_status != "pass":
                gate_messages.append(
                    "economic-distinctness: " + "; ".join(distinctness_assessment.get("reasons", [])[:2])
                )
            next_step = "Do not schedule local mining until the front gate passes: " + " | ".join(gate_messages)
        else:
            next_step = family_next_step(action)
        summaries.append(
            {
                "topic": family.topic,
                "family_key": family_key,
                "title": family.title,
                "category": family.category,
                "path": str(family.path),
                "is_dead": family.is_dead,
                "candidate_count": len(family_scored),
                "selected_count": len(family_queue),
                "best_local_score": round(float(best_local["scorecard"]["score"]), 2) if best_local else None,
                "best_gate_likelihood_score": best_gate_likelihood,
                "best_local_expression": best_local["expression"] if best_local else None,
                "top_template_id": best_local.get("template_id") if best_local else None,
                "official_capture_count": len(family_captures),
                "official_live_capture_count": live_capture_count,
                "official_dead_capture_count": dead_capture_count,
                "official_check_submission_count": check_submission_count,
                "official_capture_ids": [capture.capture_id for capture in family_captures[:5]],
                "registry_state": registry_state,
                "registry_reason": str(registry_entry.get("reason") or "no success-rate registry entry"),
                "submit_ready_count": int(registry_entry.get("submit_ready_count", 0) or 0),
                "full_gate_outcome_count": int(registry_entry.get("full_gate_outcome_count", 0) or 0),
                "failing_gate_histogram": dict(registry_entry.get("failing_gate_histogram") or {}),
                "pending_gate_histogram": dict(registry_entry.get("pending_gate_histogram") or {}),
                "field_readiness_gate_status": readiness_gate_status,
                "field_readiness_usable_field_count": len(readiness_entry.get("usable_candidate_fields", [])),
                "field_readiness_blocked_fields": [
                    entry.get("field")
                    for entry in readiness_entry.get("blocked_candidate_fields", [])
                    if entry.get("field")
                ],
                "field_readiness_reasons": list(readiness_assessment.get("reasons", [])),
                "field_readiness_coverage_floor_pct": readiness_assessment.get("coverage_floor_pct"),
                "account_capability_gate_status": capability_gate_status,
                "account_capability_reasons": list(capability_assessment.get("reasons", [])),
                "account_capability_required_scope": dict(capability_entry.get("required_scope", {})),
                "account_capability_observed_combo_count": int(
                    capability_entry.get("capability_snapshot", {}).get("observed_combo_count", 0) or 0
                ),
                "account_capability_observed_regions": list(
                    capability_entry.get("capability_snapshot", {}).get("observed_regions", [])
                ),
                "account_capability_observed_delays": list(
                    capability_entry.get("capability_snapshot", {}).get("observed_delays", [])
                ),
                "account_capability_observed_universes": list(
                    capability_entry.get("capability_snapshot", {}).get("observed_universes", [])
                ),
                "account_capability_observed_categories": list(
                    capability_entry.get("capability_snapshot", {}).get("observed_categories", [])
                ),
                "research_contract_gate_status": contract_gate_status,
                "research_contract_reasons": list(contract_assessment.get("reasons", [])),
                "research_contract_fields": dict(contract_entry.get("contract", {})),
                "validation_design_gate_status": validation_design_gate_status,
                "validation_design_reasons": list(validation_design_assessment.get("reasons", [])),
                "validation_design_fields": dict(validation_design_entry.get("validation_design", {})),
                "factor_risk_overlay_gate_status": factor_risk_gate_status,
                "factor_risk_overlay_reasons": list(factor_risk_assessment.get("reasons", [])),
                "factor_risk_overlay_expected_risks": list(
                    factor_risk_entry.get("factor_profile", {}).get("expected_risks", [])
                ),
                "factor_risk_overlay_hypothesis_risks": list(
                    factor_risk_entry.get("factor_profile", {}).get("hypothesis_risks", [])
                ),
                "factor_risk_overlay_overlay_risks": list(
                    factor_risk_entry.get("factor_profile", {}).get("overlay_risks", [])
                ),
                "complexity_budget_gate_status": complexity_gate_status,
                "complexity_budget_reasons": list(complexity_assessment.get("reasons", [])),
                "complexity_budget_expression_count": int(
                    complexity_entry.get("counts", {}).get("expression_count", 0) or 0
                ),
                "complexity_budget_variant_expression_count": int(
                    complexity_entry.get("counts", {}).get("variant_expression_count", 0) or 0
                ),
                "mechanism_failure_memory_status": failure_memory_assessment.get("negative_memory_status"),
                "mechanism_failure_memory_rank": failure_memory_assessment.get("negative_memory_rank"),
                "mechanism_failure_memory_reasons": list(failure_memory_assessment.get("reasons", [])),
                "mechanism_failure_memory_cluster": failure_memory_entry.get("mechanism_profile", {}).get("mechanism_cluster"),
                "economic_distinctness_gate_status": distinctness_gate_status,
                "economic_distinctness_reasons": list(distinctness_assessment.get("reasons", [])),
                "economic_distinctness_nearest_negative_family": distinctness_entry.get("nearest_negative_family"),
                "economic_distinctness_changed_axes": list(distinctness_entry.get("changed_axes", [])),
                "economic_distinctness_field_overlap_pct": distinctness_entry.get("field_overlap_pct"),
                "economic_distinctness_expression_similarity": distinctness_entry.get("expression_similarity"),
                "validation_provenance_gate_status": str(
                    provenance_assessment.get("gate_status") or "pass"
                ),
                "validation_provenance_level": provenance_assessment.get("strongest_level"),
                "validation_provenance_binding_status": provenance_assessment.get("binding_status"),
                "validation_provenance_reasons": list(provenance_assessment.get("reasons", [])),
                "evidence_ladder_level": evidence_assessment.get("evidence_level"),
                "evidence_promotion_ceiling": evidence_assessment.get("promotion_ceiling"),
                "evidence_effective_state": effective_state,
                "evidence_branch_budget_remaining": evidence_assessment.get("branch_budget_remaining"),
                "evidence_official_budget_cap": evidence_assessment.get("official_budget_cap"),
                "evidence_ladder_reasons": list(evidence_assessment.get("reasons", [])),
                "local_action": local_action,
                "action": action,
                "next_step": next_step,
            }
        )

    summaries.sort(
        key=lambda item: (
            STATE_PRIORITY.get(item["action"], 9),
            -(item["best_gate_likelihood_score"] or -9999.0),
            -(item["best_local_score"] or 0.0),
            item["topic"],
        )
    )
    return summaries


def render_family_summary_md(records: Sequence[dict[str, Any]]) -> str:
    lines = [
        "# Family Factory Summary",
        "",
        "| family | action | readiness | capability | contract | validation | factor | complexity | distinctness | provenance | evidence | selected | gate score | best local score | live captures | submit-ready | failing gates |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| {topic} | {action} | {field_readiness_gate_status} | {account_capability_gate_status} | {research_contract_gate_status} | {validation_design_gate_status} | {factor_risk_overlay_gate_status} | {complexity_budget_gate_status} | {economic_distinctness_gate_status} | {validation_provenance_level} | {evidence_ladder_level} | {selected_count} | {best_gate_likelihood_score} | {best_local_score} | {official_live_capture_count} | {submit_ready_count} | {failing_gates} |".format(
                **{
                    **record,
                    "best_gate_likelihood_score": (
                        f"{record['best_gate_likelihood_score']:.2f}"
                        if isinstance(record.get("best_gate_likelihood_score"), (int, float))
                        else "-"
                    ),
                    "best_local_score": (
                        f"{record['best_local_score']:.2f}"
                        if isinstance(record.get("best_local_score"), (int, float))
                        else "-"
                    ),
                    "failing_gates": (
                        ", ".join(
                            f"{gate}:{count}"
                            for gate, count in sorted((record.get("failing_gate_histogram") or {}).items())
                        )
                        or "-"
                    ),
                }
            )
        )
    lines.append("")
    lines.append("## Next Steps")
    lines.append("")
    for record in records:
        lines.append(f"- `{record['topic']}` -> `{record['action']}`. {record['next_step']}")
    lines.append("")
    return "\n".join(lines)


def render_family_registry_md(records: Sequence[dict[str, Any]]) -> str:
    lines = [
        "# Family Registry",
        "",
        "| family | state | outcomes | full gates | submit-ready | reason |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| {record['family_key']} | {record['state']} | {record['official_outcome_count']} | "
            f"{record['full_gate_outcome_count']} | {record['submit_ready_count']} | {record['reason']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_outcome_memory_md(records: Sequence[dict[str, Any]]) -> str:
    full_gate_count = sum(1 for item in records if item.get("has_full_gate_coverage"))
    submit_ready_count = sum(1 for item in records if item.get("submit_ready"))
    candidate_count = sum(
        1 for item in records
        if str(item.get("capture_mode") or "") in {"candidate-batch", "candidate-check-status"}
    )
    lines = [
        "# Outcome Memory",
        "",
        f"- Outcomes: {len(records)}",
        f"- Candidate evidence rows: {candidate_count}",
        f"- Full gate coverage: {full_gate_count}",
        f"- Submit-ready: {submit_ready_count}",
        "",
        "| family | capture | evidence | submit-ready | failing | pending |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| {record['family_key']} | {record['capture_id']} | {record['evidence_level']} | "
            f"{'yes' if record.get('submit_ready') else 'no'} | "
            f"{', '.join(record.get('failing_gates', [])) or '-'} | "
            f"{', '.join(record.get('pending_gates', [])) or '-'} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_submit_ready_ledger_md(records: Sequence[dict[str, Any]]) -> str:
    lines = [
        "# Submit-Ready Ledger",
        "",
        f"- Entries: {len(records)}",
        "",
    ]
    if not records:
        lines.append("- No outcome currently satisfies the internal submit-ready standard.")
        lines.append("")
        return "\n".join(lines)
    lines.extend(
        [
            "| family | capture | alpha | simulation | expression |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for record in records:
        lines.append(
            f"| {record['family_key']} | {record['capture_id']} | {record.get('alpha_id') or '-'} | "
            f"{record.get('simulation_id') or '-'} | `{record['expression']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def max_similarity(expression: str, expressions: Iterable[str]) -> float:
    best = 0.0
    for other in expressions:
        score = similarity_score(expression, other)
        if score > best:
            best = score
    return best


def candidate_key(record: dict[str, Any]) -> str:
    return str(record.get("candidate_id") or record.get("expression") or "")


def best_follow_up_candidate(
    records: Sequence[dict[str, Any]],
    family_topic: str,
    *,
    picked: Sequence[dict[str, Any]],
    picked_keys: set[str],
    similarity_threshold: float,
) -> dict[str, Any] | None:
    family_picks = [item for item in picked if item["family_topic"] == family_topic]
    family_exprs = [item["expression"] for item in family_picks]
    global_exprs = [item["expression"] for item in picked]
    anchor_template = family_picks[0]["template_id"] if family_picks else None

    ranked: list[tuple[Any, ...]] = []
    for record in records:
        key = candidate_key(record)
        if key in picked_keys:
            continue
        if record.get("success_prior", {}).get("hard_blocked"):
            continue
        expression = str(record.get("expression") or "")
        family_sim = max_similarity(expression, family_exprs)
        global_sim = max_similarity(expression, global_exprs)
        if family_sim >= similarity_threshold:
            continue
        if global_sim >= 0.98:
            continue
        template_id = str(record.get("template_id") or "baseline")
        ranked.append(
            (
                0 if template_id != anchor_template else 1,
                -float(record.get("success_prior", {}).get("gate_likelihood_score", -9999.0)),
                -float(record["scorecard"]["score"]),
                family_sim,
                global_sim,
                int(record.get("mutation_depth", 0)),
                key,
                record,
            )
        )
    if not ranked:
        return None
    ranked.sort()
    return ranked[0][-1]


def build_official_budget(
    scored_records: Sequence[dict[str, Any]],
    family_summaries: Sequence[dict[str, Any]],
    *,
    budget: int,
    max_per_family: int,
    similarity_threshold: float,
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    scored_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in scored_records:
        scored_by_family[str(record.get("family_topic") or "unknown")].append(record)
    for records in scored_by_family.values():
        records.sort(
            key=lambda record: (
                1 if record.get("success_prior", {}).get("hard_blocked") else 0,
                -float(record.get("success_prior", {}).get("gate_likelihood_score", -9999.0)),
                *anchor_sort_key(record),
            )
        )

    priority_order = sorted(
        (
            summary
            for summary in family_summaries
            if summary["selected_count"] > 0 and summary["action"] in {"explore", "branch", "exploit"}
        ),
        key=lambda summary: (
            STATE_PRIORITY.get(summary["action"], 9),
            -(summary.get("best_gate_likelihood_score") or -9999.0),
            -(summary["best_local_score"] or 0.0),
            -summary["official_live_capture_count"],
            summary["topic"],
        ),
    )

    picks: list[dict[str, Any]] = []
    picked_keys: set[str] = set()
    family_pick_counts: dict[str, int] = defaultdict(int)
    policy_budget = policy.get("budget") if isinstance(policy.get("budget"), dict) else {}
    max_anchor_per_family = int(policy_budget.get("max_anchor_per_family", 1))
    anchor_counts: dict[str, int] = defaultdict(int)
    per_family_caps = {
        str(summary["topic"]): int(summary.get("evidence_official_budget_cap", 1) or 1)
        for summary in family_summaries
    }

    for summary in priority_order:
        if len(picks) >= budget:
            break
        family_topic = str(summary["topic"])
        family_records = scored_by_family.get(family_topic, [])
        if not family_records:
            continue
        anchor = next(
            (
                record
                for record in family_records
                if not record.get("success_prior", {}).get("hard_blocked")
            ),
            None,
        )
        if anchor is None or anchor_counts[family_topic] >= max_anchor_per_family:
            continue
        key = candidate_key(anchor)
        if key in picked_keys:
            continue
        picks.append(
            {
                "slot": len(picks) + 1,
                "family_topic": family_topic,
                "family_action": summary["action"],
                "family_state_reason": summary.get("registry_reason"),
                "slot_reason": "anchor",
                "candidate_id": anchor.get("candidate_id"),
                "template_id": anchor.get("template_id"),
                "mutation_depth": anchor.get("mutation_depth"),
                "local_score": anchor["scorecard"]["score"],
                "gate_likelihood_score": anchor.get("success_prior", {}).get("gate_likelihood_score"),
                "failure_similarity": anchor.get("success_prior", {}).get("failure_similarity"),
                "matched_failing_gates": anchor.get("success_prior", {}).get("failure_match_failing_gates", []),
                "expression": anchor["expression"],
                "source_doc": anchor.get("source_doc"),
            }
        )
        picked_keys.add(key)
        family_pick_counts[family_topic] += 1
        anchor_counts[family_topic] += 1

    while len(picks) < budget:
        progress = False
        for summary in priority_order:
            if len(picks) >= budget:
                break
            family_topic = str(summary["topic"])
            family_cap = min(max_per_family, per_family_caps.get(family_topic, 1))
            if family_pick_counts[family_topic] >= family_cap:
                continue
            family_records = scored_by_family.get(family_topic, [])
            if not family_records:
                continue
            follow_up = best_follow_up_candidate(
                family_records,
                family_topic,
                picked=picks,
                picked_keys=picked_keys,
                similarity_threshold=similarity_threshold,
            )
            if follow_up is None:
                continue
            picks.append(
                {
                    "slot": len(picks) + 1,
                    "family_topic": family_topic,
                    "family_action": summary["action"],
                    "family_state_reason": summary.get("registry_reason"),
                    "slot_reason": "orthogonal_follow_up",
                    "candidate_id": follow_up.get("candidate_id"),
                    "template_id": follow_up.get("template_id"),
                    "mutation_depth": follow_up.get("mutation_depth"),
                    "local_score": follow_up["scorecard"]["score"],
                    "gate_likelihood_score": follow_up.get("success_prior", {}).get("gate_likelihood_score"),
                    "failure_similarity": follow_up.get("success_prior", {}).get("failure_similarity"),
                    "matched_failing_gates": follow_up.get("success_prior", {}).get("failure_match_failing_gates", []),
                    "expression": follow_up["expression"],
                    "source_doc": follow_up.get("source_doc"),
                }
            )
            picked_keys.add(candidate_key(follow_up))
            family_pick_counts[family_topic] += 1
            progress = True
        if not progress:
            break

    return picks


def render_official_budget_md(items: Sequence[dict[str, Any]], args: argparse.Namespace, policy: dict[str, Any]) -> str:
    lines = [
        "# Official Budget Recommendation",
        "",
        f"- Objective: {policy.get('objective', 'maximize_internal_submit_ready_per_official_slot')}",
        f"- Budget: {args.official_budget}",
        f"- Max per family: {args.max_official_per_family}",
        f"- Orthogonality threshold: {args.official_similarity_threshold:.2f}",
        "",
    ]
    if not items:
        lines.append("- No official slots are recommended from this local run.")
        lines.append("")
        return "\n".join(lines)

    lines.append("| slot | family | action | reason | gate score | local score | fail sim | template | depth |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in items:
        lines.append(
            f"| {item['slot']} | {item['family_topic']} | {item['family_action']} | {item['slot_reason']} | "
            f"{float(item['gate_likelihood_score']):.2f} | {float(item['local_score']):.2f} | "
            f"{float(item.get('failure_similarity') or 0.0):.2f} | {item['template_id']} | {item['mutation_depth']} |"
        )
    lines.append("")
    lines.append("## Expressions")
    lines.append("")
    for item in items:
        lines.append(
            f"- Slot {item['slot']} `{item['family_topic']}` `{item['slot_reason']}`: "
            f"`{item['expression']}`"
        )
    lines.append("")
    return "\n".join(lines)


def bundle_manifest(
    *,
    run_id: str,
    success_policy: dict[str, Any],
    families: Sequence[ParsedFamilyDoc],
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
    captures: Sequence[ParsedCapture],
    candidates: Sequence[dict[str, Any]],
    scored: Sequence[dict[str, Any]],
    queue_document: dict[str, Any],
    family_summary: Sequence[dict[str, Any]],
    family_registry: Sequence[dict[str, Any]],
    outcome_memory: Sequence[dict[str, Any]],
    submit_ready_ledger: Sequence[dict[str, Any]],
    official_budget: Sequence[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "run_id": run_id,
        "objective": success_policy.get("objective"),
        "settings": {
            "family_dir": str(args.family_dir),
            "field_search_pack_dir": str(args.field_search_pack_dir),
            "capture_dir": str(args.capture_dir),
            "candidate_batch_dir": str(args.candidate_batch_dir),
            "success_policy": str(args.success_policy),
            "include_topic": list(args.include_topic),
            "exclude_topic": list(args.exclude_topic),
            "include_dead": args.include_dead,
            "coverage_floor_pct": args.coverage_floor_pct,
            "token_maps": [str(path) for path in args.token_map],
            "max_candidates": args.max_candidates,
            "per_seed": args.per_seed,
            "max_depth": args.max_depth,
            "reject_dead_similarity": args.reject_dead_similarity,
            "seed_limit": args.seed_limit,
            "min_score": args.min_score,
            "max_total": args.max_total,
            "max_per_family": args.max_per_family,
            "max_per_template": args.max_per_template,
            "similarity_threshold": args.similarity_threshold,
            "official_budget": args.official_budget,
            "max_official_per_family": args.max_official_per_family,
            "official_similarity_threshold": args.official_similarity_threshold,
            "publish_queue": args.publish_queue,
        },
        "counts": {
            "family_count": len(families),
            "field_readiness_count": len(field_readiness_report.get("items", [])),
            "field_readiness_pass_count": int(field_readiness_report.get("counts", {}).get("pass_count", 0)),
            "account_capability_count": len(account_capability_report.get("items", [])),
            "account_capability_pass_count": int(account_capability_report.get("counts", {}).get("pass_count", 0)),
            "research_contract_count": len(research_contract_report.get("items", [])),
            "research_contract_pass_count": int(research_contract_report.get("counts", {}).get("pass_count", 0)),
            "validation_design_count": len(validation_design_report.get("items", [])),
            "validation_design_pass_count": int(validation_design_report.get("counts", {}).get("pass_count", 0)),
            "factor_risk_overlay_count": len(factor_risk_overlay_report.get("items", [])),
            "factor_risk_overlay_pass_count": int(factor_risk_overlay_report.get("counts", {}).get("pass_count", 0)),
            "complexity_budget_count": len(complexity_budget_report.get("items", [])),
            "complexity_budget_pass_count": int(complexity_budget_report.get("counts", {}).get("pass_count", 0)),
            "mechanism_failure_memory_count": len(mechanism_failure_memory_report.get("items", [])),
            "negative_failure_memory_count": int(mechanism_failure_memory_report.get("counts", {}).get("negative_family_count", 0)),
            "economic_distinctness_count": len(economic_distinctness_report.get("items", [])),
            "economic_distinctness_pass_count": int(economic_distinctness_report.get("counts", {}).get("pass_count", 0)),
            "validation_provenance_count": len(validation_provenance_report.get("items", [])),
            "binding_provenance_count": int(validation_provenance_report.get("counts", {}).get("binding_family_count", 0)),
            "evidence_ladder_count": len(evidence_ladder_report.get("items", [])),
            "E3_full_is_count": int(evidence_ladder_report.get("counts", {}).get("E3_full_is", 0)),
            "E4_submit_ready_count": int(evidence_ladder_report.get("counts", {}).get("E4_submit_ready", 0)),
            "capture_count": len(captures),
            "candidate_count": len(candidates),
            "scored_count": len(scored),
            "queue_count": len(queue_document.get("items", [])),
            "family_summary_count": len(family_summary),
            "family_registry_count": len(family_registry),
            "official_outcome_count": len(outcome_memory),
            "submit_ready_count": len(submit_ready_ledger),
            "official_budget_count": len(official_budget),
        },
        "family_docs": [summarise_family(doc) for doc in families[:20]],
        "field_readiness": {
            "coverage_floor_pct": field_readiness_report.get("coverage_floor_pct"),
            "counts": dict(field_readiness_report.get("counts", {})),
            "top_blocked": [
                item
                for item in field_readiness_report.get("items", [])
                if str(item.get("assessment", {}).get("gate_status") or "") != "pass"
            ][:10],
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
            "top_blocked": [
                item
                for item in research_contract_report.get("items", [])
                if str(item.get("assessment", {}).get("gate_status") or "") != "pass"
            ][:10],
        },
        "validation_design": {
            "counts": dict(validation_design_report.get("counts", {})),
            "top_blocked": [
                item
                for item in validation_design_report.get("items", [])
                if str(item.get("assessment", {}).get("gate_status") or "") != "pass"
            ][:10],
        },
        "factor_risk_overlay": {
            "counts": dict(factor_risk_overlay_report.get("counts", {})),
            "top_blocked": [
                item
                for item in factor_risk_overlay_report.get("items", [])
                if str(item.get("assessment", {}).get("gate_status") or "") != "pass"
            ][:10],
        },
        "complexity_budget": {
            "counts": dict(complexity_budget_report.get("counts", {})),
            "top_blocked": [
                item
                for item in complexity_budget_report.get("items", [])
                if str(item.get("assessment", {}).get("gate_status") or "") != "pass"
            ][:10],
        },
        "mechanism_failure_memory": {
            "counts": dict(mechanism_failure_memory_report.get("counts", {})),
            "top_negative": [
                item
                for item in mechanism_failure_memory_report.get("items", [])
                if int(item.get("assessment", {}).get("negative_memory_rank", 0) or 0) > 0
            ][:10],
        },
        "economic_distinctness": {
            "counts": dict(economic_distinctness_report.get("counts", {})),
            "top_blocked": [
                item
                for item in economic_distinctness_report.get("items", [])
                if str(item.get("assessment", {}).get("gate_status") or "") != "pass"
            ][:10],
        },
        "validation_provenance": {
            "counts": dict(validation_provenance_report.get("counts", {})),
            "top_families": list(validation_provenance_report.get("items", [])[:10]),
        },
        "evidence_ladder": {
            "counts": dict(evidence_ladder_report.get("counts", {})),
            "top_families": list(evidence_ladder_report.get("items", [])[:10]),
        },
        "capture_docs": [summarise_capture(capture) for capture in captures[:20]],
        "top_queue_items": queue_document.get("items", [])[:10],
        "top_official_budget": list(official_budget[:10]),
    }


def ensure_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")


def maybe_publish_queue(
    *,
    queue_document: dict[str, Any],
    queue_summary_text: str,
    args: argparse.Namespace,
    run_id: str,
) -> dict[str, str] | None:
    if not args.publish_queue:
        return None
    json_path = args.publish_root / f"{run_id}.json"
    md_path = args.publish_root / f"{run_id}.md"
    dump_json(json_path, queue_document)
    ensure_text(md_path, queue_summary_text)
    return {"json": str(json_path), "md": str(md_path)}


def main() -> int:
    args = parse_args()
    run_id = default_run_id(args)
    output_root = args.artifact_root / run_id
    success_policy = load_success_policy(args.success_policy)
    resolve_success_budget_args(args, success_policy)

    include_patterns = compile_patterns(args.include_topic)
    policy_excludes = [
        pattern
        for pattern in success_policy.get("hard_exclude_topic_patterns", [])
        if isinstance(pattern, str) and pattern.strip()
    ]
    exclude_patterns = compile_patterns([*args.exclude_topic, *policy_excludes])

    all_family_docs = load_family_docs(args.family_dir, include_dead=True)
    captures = load_captures(args.capture_dir) if args.capture_dir.exists() else tuple()
    if not all_family_docs:
        raise SystemExit(f"No expression-family docs found in {args.family_dir}")

    selected_families = tuple(
        doc
        for doc in all_family_docs
        if should_include_family(
            doc,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            include_dead=args.include_dead,
        )
    )
    if not selected_families:
        raise SystemExit("No family docs remain after applying the current include/exclude filters.")

    selected_family_keys = {family_key_for_topic(doc.topic) for doc in selected_families}
    field_packs = load_field_search_packs(args.field_search_pack_dir)
    selected_field_packs = [pack for pack in field_packs if pack.family_key in selected_family_keys]
    field_readiness_report = build_field_readiness_report(
        field_packs=selected_field_packs,
        family_docs=selected_families,
        coverage_floor_pct=args.coverage_floor_pct,
    )
    field_readiness_by_family = index_field_readiness(field_readiness_report)
    research_contract_report = build_research_contract_report(family_docs=selected_families)
    research_contract_by_family = index_research_contract_report(research_contract_report)
    account_capability_report = build_account_capability_report(
        family_docs=selected_families,
        research_contract_report=research_contract_report,
    )
    account_capability_by_family = index_account_capability(account_capability_report)
    validation_design_report = build_validation_design_report(family_docs=selected_families)
    validation_design_by_family = index_validation_design(validation_design_report)
    factor_risk_overlay_report = build_factor_risk_overlay_report(
        family_docs=selected_families,
        research_contract_report=research_contract_report,
        validation_design_report=validation_design_report,
    )
    factor_risk_overlay_by_family = index_factor_risk_overlay(factor_risk_overlay_report)
    complexity_budget_report = build_complexity_budget_report(
        family_docs=selected_families,
        policy=success_policy,
    )
    complexity_budget_by_family = index_complexity_budget(complexity_budget_report)

    candidate_batch_dir = args.candidate_batch_dir if args.candidate_batch_dir.exists() else None
    outcome_memory = build_combined_outcome_memory(
        args.capture_dir if args.capture_dir.exists() else [],
        candidate_batches=candidate_batch_dir,
    )
    outcome_memory = [
        record
        for record in outcome_memory
        if str(record.get("family_key") or "") in selected_family_keys
    ]
    submit_ready_ledger = build_submit_ready_ledger(outcome_memory)
    family_registry = build_family_registry_summary([doc.path for doc in selected_families], outcome_memory)
    mechanism_failure_memory_report = build_mechanism_failure_memory_report(
        family_docs=selected_families,
        family_registry=family_registry,
        research_contract_report=research_contract_report,
    )
    mechanism_failure_memory_by_family = index_mechanism_failure_memory(mechanism_failure_memory_report)
    economic_distinctness_report = build_economic_distinctness_report(
        family_docs=selected_families,
        research_contract_report=research_contract_report,
        mechanism_failure_memory_report=mechanism_failure_memory_report,
    )
    economic_distinctness_by_family = index_economic_distinctness(economic_distinctness_report)
    ready_selected_families = tuple(
        doc
        for doc in selected_families
        if str(
            field_readiness_by_family.get(family_key_for_topic(doc.topic), {})
            .get("assessment", {})
            .get("gate_status", "block")
        )
        == "pass"
        and str(
            account_capability_by_family.get(family_key_for_topic(doc.topic), {})
            .get("assessment", {})
            .get("gate_status", "block")
        )
        == "pass"
        and str(
            research_contract_by_family.get(family_key_for_topic(doc.topic), {})
            .get("assessment", {})
            .get("gate_status", "block")
        )
        == "pass"
        and str(
            validation_design_by_family.get(family_key_for_topic(doc.topic), {})
            .get("assessment", {})
            .get("gate_status", "block")
        )
        == "pass"
        and str(
            factor_risk_overlay_by_family.get(family_key_for_topic(doc.topic), {})
            .get("assessment", {})
            .get("gate_status", "block")
        )
        == "pass"
        and str(
            complexity_budget_by_family.get(family_key_for_topic(doc.topic), {})
            .get("assessment", {})
            .get("gate_status", "block")
        )
        == "pass"
        and str(
            economic_distinctness_by_family.get(family_key_for_topic(doc.topic), {})
            .get("assessment", {})
            .get("gate_status", "block")
        )
        == "pass"
    )

    bank = build_expression_bank(all_family_docs, captures)
    token_rules = merge_token_rules(args.token_map)
    if ready_selected_families:
        candidates = build_candidate_pool(
            ready_selected_families,
            bank,
            token_rules,
            max_candidates=args.max_candidates,
            per_seed=args.per_seed,
            max_depth=args.max_depth,
            reject_dead_similarity=args.reject_dead_similarity,
            seed_limit=args.seed_limit,
        )
    else:
        candidates = []

    scored_records = score_candidates(
        candidates,
        family_docs=all_family_docs,
        captures=captures,
        bank=bank,
        min_score=args.min_score,
    )
    local_scored_counts: dict[str, int] = defaultdict(int)
    for record in scored_records:
        local_scored_counts[family_key_for_topic(str(record.get("family_topic") or ""))] += 1
    evidence_ladder_report = build_evidence_ladder_report(
        family_docs=selected_families,
        outcome_memory=outcome_memory,
        family_registry=family_registry,
        local_scored_counts=local_scored_counts,
    )
    evidence_ladder_by_family = index_evidence_ladder(evidence_ladder_report)
    scored_records = enrich_records_with_success_priors(
        scored_records,
        family_registry=family_registry,
        outcome_memory=outcome_memory,
        submit_ready_ledger=submit_ready_ledger,
        policy=success_policy,
        evidence_ladder_by_family=evidence_ladder_by_family,
    )
    selected_items, rejection_reasons = select_queue_with_success_priors(scored_records, args)
    local_queue_counts: dict[str, int] = defaultdict(int)
    for item in selected_items:
        local_queue_counts[family_key_for_topic(str(item.get("family_topic") or ""))] += 1
    validation_provenance_report = build_validation_provenance_report(
        family_docs=selected_families,
        outcome_memory=outcome_memory,
        family_registry=family_registry,
        local_scored_counts=local_scored_counts,
        local_queue_counts=local_queue_counts,
    )
    validation_provenance_by_family = index_validation_provenance(validation_provenance_report)
    evidence_ladder_report = build_evidence_ladder_report(
        family_docs=selected_families,
        outcome_memory=outcome_memory,
        family_registry=family_registry,
        local_scored_counts=local_scored_counts,
        local_queue_counts=local_queue_counts,
    )
    evidence_ladder_by_family = index_evidence_ladder(evidence_ladder_report)
    queue_document = build_queue_document(selected_items, args)
    queue_document["success_policy"] = {
        "objective": success_policy.get("objective"),
        "policy_path": str(args.success_policy),
        "family_registry_count": len(family_registry),
        "official_outcome_count": len(outcome_memory),
        "submit_ready_count": len(submit_ready_ledger),
        "field_readiness_pass_count": int(field_readiness_report.get("counts", {}).get("pass_count", 0)),
        "field_readiness_hold_count": int(field_readiness_report.get("counts", {}).get("hold_count", 0)),
        "field_readiness_block_count": int(field_readiness_report.get("counts", {}).get("block_count", 0)),
        "account_capability_pass_count": int(account_capability_report.get("counts", {}).get("pass_count", 0)),
        "account_capability_hold_count": int(account_capability_report.get("counts", {}).get("hold_count", 0)),
        "account_capability_block_count": int(account_capability_report.get("counts", {}).get("block_count", 0)),
        "research_contract_pass_count": int(research_contract_report.get("counts", {}).get("pass_count", 0)),
        "research_contract_hold_count": int(research_contract_report.get("counts", {}).get("hold_count", 0)),
        "research_contract_block_count": int(research_contract_report.get("counts", {}).get("block_count", 0)),
        "validation_design_pass_count": int(validation_design_report.get("counts", {}).get("pass_count", 0)),
        "validation_design_hold_count": int(validation_design_report.get("counts", {}).get("hold_count", 0)),
        "validation_design_block_count": int(validation_design_report.get("counts", {}).get("block_count", 0)),
        "factor_risk_overlay_pass_count": int(factor_risk_overlay_report.get("counts", {}).get("pass_count", 0)),
        "factor_risk_overlay_hold_count": int(factor_risk_overlay_report.get("counts", {}).get("hold_count", 0)),
        "factor_risk_overlay_block_count": int(factor_risk_overlay_report.get("counts", {}).get("block_count", 0)),
        "complexity_budget_pass_count": int(complexity_budget_report.get("counts", {}).get("pass_count", 0)),
        "complexity_budget_hold_count": int(complexity_budget_report.get("counts", {}).get("hold_count", 0)),
        "complexity_budget_block_count": int(complexity_budget_report.get("counts", {}).get("block_count", 0)),
        "negative_failure_memory_count": int(
            mechanism_failure_memory_report.get("counts", {}).get("negative_family_count", 0)
        ),
        "economic_distinctness_pass_count": int(
            economic_distinctness_report.get("counts", {}).get("pass_count", 0)
        ),
        "economic_distinctness_hold_count": int(
            economic_distinctness_report.get("counts", {}).get("hold_count", 0)
        ),
        "validation_provenance_binding_family_count": int(
            validation_provenance_report.get("counts", {}).get("binding_family_count", 0)
        ),
        "validation_provenance_hold_count": int(
            validation_provenance_report.get("counts", {}).get("hold_count", 0)
        ),
        "E3_full_is_count": int(evidence_ladder_report.get("counts", {}).get("E3_full_is", 0)),
        "E4_submit_ready_count": int(evidence_ladder_report.get("counts", {}).get("E4_submit_ready", 0)),
    }
    score_summary_text = build_score_summary(scored_records, ready_selected_families, args.min_score)
    queue_summary_text = build_queue_summary(selected_items, rejection_reasons, args)
    family_summary_records = build_family_summary_records(
        selected_families,
        captures,
        scored_records,
        selected_items,
        family_registry=family_registry,
        field_readiness_by_family=field_readiness_by_family,
        account_capability_by_family=account_capability_by_family,
        research_contract_by_family=research_contract_by_family,
        validation_design_by_family=validation_design_by_family,
        factor_risk_overlay_by_family=factor_risk_overlay_by_family,
        complexity_budget_by_family=complexity_budget_by_family,
        mechanism_failure_memory_by_family=mechanism_failure_memory_by_family,
        economic_distinctness_by_family=economic_distinctness_by_family,
        validation_provenance_by_family=validation_provenance_by_family,
        evidence_ladder_by_family=evidence_ladder_by_family,
    )
    family_summary_text = render_family_summary_md(family_summary_records)
    official_budget_items = build_official_budget(
        scored_records,
        family_summary_records,
        budget=args.official_budget,
        max_per_family=args.max_official_per_family,
        similarity_threshold=args.official_similarity_threshold,
        policy=success_policy,
    )
    official_budget_text = render_official_budget_md(official_budget_items, args, success_policy)
    family_registry_text = render_family_registry_md(family_registry)
    outcome_memory_text = render_outcome_memory_md(outcome_memory)
    submit_ready_ledger_text = render_submit_ready_ledger_md(submit_ready_ledger)
    field_readiness_text = render_field_readiness_md(field_readiness_report)
    account_capability_text = render_account_capability_md(account_capability_report)
    research_contract_text = render_research_contract_md(research_contract_report)
    validation_design_text = render_validation_design_md(validation_design_report)
    factor_risk_overlay_text = render_factor_risk_overlay_md(factor_risk_overlay_report)
    complexity_budget_text = render_complexity_budget_md(complexity_budget_report)
    mechanism_failure_memory_text = render_mechanism_failure_memory_md(mechanism_failure_memory_report)
    economic_distinctness_text = render_economic_distinctness_md(economic_distinctness_report)
    validation_provenance_text = render_validation_provenance_md(validation_provenance_report)
    evidence_ladder_text = render_evidence_ladder_md(evidence_ladder_report)

    output_root.mkdir(parents=True, exist_ok=True)
    candidates_path = output_root / "candidates.jsonl"
    scored_path = output_root / "scored.jsonl"
    scored_csv_path = output_root / "scored.csv"
    scorecard_md_path = output_root / "scorecard.md"
    queue_json_path = output_root / "queue.json"
    queue_md_path = output_root / "queue.md"
    family_summary_json_path = output_root / "family-summary.json"
    family_summary_md_path = output_root / "family-summary.md"
    family_registry_json_path = output_root / "family-registry.json"
    family_registry_md_path = output_root / "family-registry.md"
    outcome_memory_json_path = output_root / "outcome-memory.json"
    outcome_memory_md_path = output_root / "outcome-memory.md"
    submit_ready_ledger_json_path = output_root / "submit-ready-ledger.json"
    submit_ready_ledger_md_path = output_root / "submit-ready-ledger.md"
    success_policy_json_path = output_root / "success-policy.json"
    official_budget_json_path = output_root / "official-budget.json"
    official_budget_md_path = output_root / "official-budget.md"
    field_readiness_json_path = output_root / "field-readiness.json"
    field_readiness_md_path = output_root / "field-readiness.md"
    account_capability_json_path = output_root / "account-capability.json"
    account_capability_md_path = output_root / "account-capability.md"
    research_contract_json_path = output_root / "research-contract.json"
    research_contract_md_path = output_root / "research-contract.md"
    validation_design_json_path = output_root / "validation-design.json"
    validation_design_md_path = output_root / "validation-design.md"
    factor_risk_overlay_json_path = output_root / "factor-risk-overlay.json"
    factor_risk_overlay_md_path = output_root / "factor-risk-overlay.md"
    complexity_budget_json_path = output_root / "complexity-budget.json"
    complexity_budget_md_path = output_root / "complexity-budget.md"
    mechanism_failure_memory_json_path = output_root / "mechanism-failure-memory.json"
    mechanism_failure_memory_md_path = output_root / "mechanism-failure-memory.md"
    economic_distinctness_json_path = output_root / "economic-distinctness.json"
    economic_distinctness_md_path = output_root / "economic-distinctness.md"
    validation_provenance_json_path = output_root / "validation-provenance.json"
    validation_provenance_md_path = output_root / "validation-provenance.md"
    evidence_ladder_json_path = output_root / "evidence-ladder.json"
    evidence_ladder_md_path = output_root / "evidence-ladder.md"
    manifest_path = output_root / "manifest.json"

    write_jsonl(candidates, candidates_path)
    write_jsonl(scored_records, scored_path)
    write_scored_csv(scored_records, scored_csv_path)
    ensure_text(scorecard_md_path, score_summary_text)
    dump_json(queue_json_path, queue_document)
    ensure_text(queue_md_path, queue_summary_text)
    dump_json(family_summary_json_path, family_summary_records)
    ensure_text(family_summary_md_path, family_summary_text)
    dump_json(family_registry_json_path, family_registry)
    ensure_text(family_registry_md_path, family_registry_text)
    dump_json(outcome_memory_json_path, outcome_memory)
    ensure_text(outcome_memory_md_path, outcome_memory_text)
    dump_json(submit_ready_ledger_json_path, submit_ready_ledger)
    ensure_text(submit_ready_ledger_md_path, submit_ready_ledger_text)
    dump_json(success_policy_json_path, success_policy)
    dump_json(field_readiness_json_path, field_readiness_report)
    ensure_text(field_readiness_md_path, field_readiness_text)
    dump_json(account_capability_json_path, account_capability_report)
    ensure_text(account_capability_md_path, account_capability_text)
    dump_json(research_contract_json_path, research_contract_report)
    ensure_text(research_contract_md_path, research_contract_text)
    dump_json(validation_design_json_path, validation_design_report)
    ensure_text(validation_design_md_path, validation_design_text)
    dump_json(factor_risk_overlay_json_path, factor_risk_overlay_report)
    ensure_text(factor_risk_overlay_md_path, factor_risk_overlay_text)
    dump_json(complexity_budget_json_path, complexity_budget_report)
    ensure_text(complexity_budget_md_path, complexity_budget_text)
    dump_json(mechanism_failure_memory_json_path, mechanism_failure_memory_report)
    ensure_text(mechanism_failure_memory_md_path, mechanism_failure_memory_text)
    dump_json(economic_distinctness_json_path, economic_distinctness_report)
    ensure_text(economic_distinctness_md_path, economic_distinctness_text)
    dump_json(validation_provenance_json_path, validation_provenance_report)
    ensure_text(validation_provenance_md_path, validation_provenance_text)
    dump_json(evidence_ladder_json_path, evidence_ladder_report)
    ensure_text(evidence_ladder_md_path, evidence_ladder_text)
    dump_json(
        official_budget_json_path,
        {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "objective": success_policy.get("objective"),
            "budget_policy": {
                "success_policy": str(args.success_policy),
                "official_budget": args.official_budget,
                "max_official_per_family": args.max_official_per_family,
                "official_similarity_threshold": args.official_similarity_threshold,
            },
            "items": official_budget_items,
        },
    )
    ensure_text(official_budget_md_path, official_budget_text)

    published_paths = maybe_publish_queue(
        queue_document=queue_document,
        queue_summary_text=queue_summary_text,
        args=args,
        run_id=run_id,
    )

    manifest = bundle_manifest(
        run_id=run_id,
        success_policy=success_policy,
        families=selected_families,
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
        captures=captures,
        candidates=candidates,
        scored=scored_records,
        queue_document=queue_document,
        family_summary=family_summary_records,
        family_registry=family_registry,
        outcome_memory=outcome_memory,
        submit_ready_ledger=submit_ready_ledger,
        official_budget=official_budget_items,
        args=args,
    )
    if published_paths:
        manifest["published_queue"] = published_paths
    dump_json(manifest_path, manifest)

    print(f"Run bundle: {output_root}")
    if published_paths:
        print(f"Published queue JSON: {published_paths['json']}")
        print(f"Published queue MD: {published_paths['md']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

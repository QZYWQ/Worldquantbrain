#!/usr/bin/env python3
"""Build a diversified research queue from scored alpha candidates."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import sys
from typing import Any

from alpha_mining_core import (
    canonicalize_expression,
    dump_json,
    load_json,
    read_jsonl,
    similarity_score,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a ranked research queue from scored candidates.")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Scored JSONL produced by candidate_scorecard.py.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional queue JSON output path. Defaults to stdout.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="Optional markdown summary path.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("templates/research-queue.template.json"),
        help="Optional queue template JSON to copy structure from.",
    )
    parser.add_argument(
        "--max-total",
        type=int,
        default=20,
        help="Maximum number of items to keep in the final queue.",
    )
    parser.add_argument(
        "--max-per-family",
        type=int,
        default=3,
        help="Maximum number of items from the same family topic.",
    )
    parser.add_argument(
        "--max-per-template",
        type=int,
        default=2,
        help="Maximum number of items sharing the same template_id.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=62.0,
        help="Minimum local score needed for queue consideration.",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.94,
        help="Reject a candidate if it is too similar to already selected queue items.",
    )
    return parser.parse_args()


def freshness_score(category: str) -> int:
    category = (category or "").lower()
    if category in {"sentiment_news", "event_trigger", "volatility_risk"}:
        return 2
    if category in {"price_volume", "fundamental", "model_analyst"}:
        return 1
    return 1


def idea_strength(score: float) -> int:
    if score >= 82:
        return 3
    if score >= 68:
        return 2
    if score >= 52:
        return 1
    return 0


def correlation_novelty(scorecard: dict[str, Any]) -> int:
    novelty = float(scorecard.get("novelty_score", 0.0))
    if novelty >= 80:
        return 3
    if novelty >= 60:
        return 2
    if novelty >= 35:
        return 1
    return 0


def metric_headroom(scorecard: dict[str, Any]) -> int:
    score = float(scorecard.get("score", 0.0))
    overfit = float(scorecard.get("overfit_risk", 100.0))
    coupling = float(scorecard.get("coupling_risk", 100.0))
    if score >= 72 and overfit <= 45 and coupling <= 35:
        return 2
    if score >= 60 and overfit <= 60 and coupling <= 50:
        return 1
    return 0


def execution_simplicity(scorecard: dict[str, Any], mutation_depth: int) -> int:
    if mutation_depth <= 1 and float(scorecard.get("health_score", 0.0)) >= 70:
        return 1
    return 0


def current_status_for(record: dict[str, Any]) -> str:
    if int(record.get("mutation_depth", 0)) <= 0:
        return "new_direction"
    return "refine"


def next_step_for(record: dict[str, Any]) -> str:
    family = str(record.get("family_topic") or "unknown")
    template = str(record.get("template_id") or "baseline")
    mutation_depth = int(record.get("mutation_depth", 0))
    if mutation_depth <= 0:
        return f"Run the {family} baseline first, then keep only the least-coupled local variant."
    if template == "baseline":
        return f"Keep the {family} anchor only if the test-period view stays stable."
    return f"Compare this {family} variant against the family anchor and drop it if the ridge weakens."


def build_queue_item(record: dict[str, Any]) -> dict[str, Any]:
    scorecard = record["scorecard"]
    score = float(scorecard["score"])
    family_category = str(record.get("family_category") or scorecard.get("family_category") or "general")
    mutation_depth = int(record.get("mutation_depth", 0))
    template_id = str(record.get("template_id") or "baseline")
    expression = canonicalize_expression(str(record.get("expression") or ""))
    item_name = str(record.get("candidate_id") or f"{record.get('family_topic', 'candidate')}-{template_id}")

    return {
        "name": item_name,
        "idea_strength": idea_strength(score),
        "dataset_freshness": freshness_score(family_category),
        "correlation_novelty": correlation_novelty(scorecard),
        "metric_headroom": metric_headroom(scorecard),
        "execution_simplicity": execution_simplicity(scorecard, mutation_depth),
        "current_status": current_status_for(record),
        "notes": (
            f"score={score:.2f}; health={scorecard['health_score']:.2f}; "
            f"convergence={scorecard['convergence_score']:.2f}; novelty={scorecard['novelty_score']:.2f}; "
            f"overfit={scorecard['overfit_risk']:.2f}; coupling={scorecard['coupling_risk']:.2f}; "
            f"template={template_id}; mutations={' | '.join(record.get('mutations', [])) or 'baseline'}"
        ),
        "next_step": next_step_for(record),
        "expression": expression,
        "family_topic": record.get("family_topic"),
        "family_category": family_category,
        "template_id": template_id,
        "candidate_id": record.get("candidate_id"),
        "score": round(score, 2),
        "health_score": scorecard["health_score"],
        "convergence_score": scorecard["convergence_score"],
        "novelty_score": scorecard["novelty_score"],
        "family_fit_score": scorecard["family_fit_score"],
        "stability_score": scorecard["stability_score"],
        "overfit_risk": scorecard["overfit_risk"],
        "coupling_risk": scorecard["coupling_risk"],
        "source_doc": record.get("source_doc"),
        "mutations": record.get("mutations", []),
        "decision": scorecard["decision"],
    }


def candidate_similarity(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> float:
    if not selected:
        return 0.0
    candidate_expr = candidate.get("expression")
    best = 0.0
    for item in selected:
        score = similarity_score(candidate_expr, item.get("expression"))
        if score > best:
            best = score
    return best


def should_keep_candidate(
    candidate: dict[str, Any],
    selected: list[dict[str, Any]],
    family_counts: dict[str, int],
    template_counts: dict[str, int],
    args: argparse.Namespace,
) -> tuple[bool, str]:
    scorecard = candidate["scorecard"]
    if scorecard["decision"] == "drop" or float(scorecard["score"]) < args.min_score:
        return False, "scorecard_drop"

    family = str(candidate.get("family_topic") or "unknown")
    template_id = str(candidate.get("template_id") or "baseline")
    if family_counts[family] >= args.max_per_family:
        return False, "family_quota"
    if template_counts[template_id] >= args.max_per_template:
        return False, "template_quota"

    sim = candidate_similarity(candidate, selected)
    if sim >= args.similarity_threshold:
        same_family = any(item.get("family_topic") == family for item in selected)
        if same_family:
            return False, "same_family_similarity"
        return False, "global_similarity"

    return True, "accepted"


def select_queue(records: list[dict[str, Any]], args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, str]]:
    sorted_records = sorted(
        records,
        key=lambda record: (
            -float(record["scorecard"]["score"]),
            int(record.get("mutation_depth", 0)),
            -float(record["scorecard"].get("health_score", 0.0)),
            str(record.get("candidate_id") or ""),
        ),
    )

    selected: list[dict[str, Any]] = []
    reasons: dict[str, str] = {}
    family_counts: dict[str, int] = defaultdict(int)
    template_counts: dict[str, int] = defaultdict(int)

    # First pass: make sure each family can contribute a best anchor if possible.
    best_by_family: dict[str, dict[str, Any]] = {}
    for record in sorted_records:
        family = str(record.get("family_topic") or "unknown")
        current = best_by_family.get(family)
        if current is None or float(record["scorecard"]["score"]) > float(current["scorecard"]["score"]):
            best_by_family[family] = record

    for family, record in sorted(best_by_family.items(), key=lambda item: (-float(item[1]["scorecard"]["score"]), item[0])):
        if len(selected) >= args.max_total:
            break
        keep, reason = should_keep_candidate(record, selected, family_counts, template_counts, args)
        if not keep:
            reasons[str(record.get("candidate_id") or record.get("expression"))] = reason
            continue
        selected.append(build_queue_item(record))
        family_counts[family] += 1
        template_counts[str(record.get("template_id") or "baseline")] += 1
        reasons[str(record.get("candidate_id") or record.get("expression"))] = "anchor"

    # Second pass: fill remaining slots with the strongest non-duplicate candidates.
    for record in sorted_records:
        if len(selected) >= args.max_total:
            break
        family = str(record.get("family_topic") or "unknown")
        template_id = str(record.get("template_id") or "baseline")
        key = str(record.get("candidate_id") or record.get("expression"))
        if key in reasons:
            continue
        keep, reason = should_keep_candidate(record, selected, family_counts, template_counts, args)
        if not keep:
            reasons[key] = reason
            continue
        selected.append(build_queue_item(record))
        family_counts[family] += 1
        template_counts[template_id] += 1
        reasons[key] = "accepted"

    return selected, reasons


def build_queue_document(selected: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    if args.template.exists():
        template = load_json(args.template)
    else:
        template = {
            "_instructions": [
                "Generated by research_queue_builder.py.",
                "Use only for pre-simulate prioritization.",
            ],
            "items": [],
        }

    document = dict(template)
    document["generated_at"] = datetime.now().isoformat(timespec="seconds")
    document["selection_policy"] = {
        "max_total": args.max_total,
        "max_per_family": args.max_per_family,
        "max_per_template": args.max_per_template,
        "min_score": args.min_score,
        "similarity_threshold": args.similarity_threshold,
    }
    document["items"] = selected
    return document


def build_summary(selected: list[dict[str, Any]], reasons: dict[str, str], args: argparse.Namespace) -> str:
    lines = [
        "# Research Queue Summary",
        "",
        f"- Selected items: {len(selected)}",
        f"- Max total: {args.max_total}",
        f"- Max per family: {args.max_per_family}",
        f"- Max per template: {args.max_per_template}",
        f"- Min score: {args.min_score:.2f}",
        f"- Similarity threshold: {args.similarity_threshold:.2f}",
        "",
    ]

    lines.append("## Selected Items")
    lines.append("")
    for item in selected:
        lines.append(
            f"- {item['family_topic']}: score {item['score']:.2f}, "
            f"idea_strength {item['idea_strength']}, template {item['template_id']}"
        )
    lines.append("")

    if reasons:
        lines.append("## Rejection Reasons")
        lines.append("")
        counts = defaultdict(int)
        for reason in reasons.values():
            counts[reason] += 1
        for reason, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- {reason}: {count}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    scored_records = read_jsonl(args.input)
    selected, reasons = select_queue(list(scored_records), args)
    queue_document = build_queue_document(selected, args)

    if args.output:
        dump_json(args.output, queue_document)
    else:
        print(json.dumps(queue_document, ensure_ascii=False, indent=2, sort_keys=True))

    summary_text = build_summary(selected, reasons, args)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(summary_text + "\n", encoding="utf-8")
    else:
        print(summary_text, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

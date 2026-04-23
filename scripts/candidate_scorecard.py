#!/usr/bin/env python3
"""Score a candidate pool with conservative, family-aware heuristics.

The scorecard is deliberately not a proxy for official metrics. It only ranks
local candidates by structural health, convergence, novelty, and coupling risk.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
import sys
from typing import Any

from alpha_mining_core import (
    ParsedCapture,
    ParsedFamilyDoc,
    build_expression_bank,
    canonicalize_expression,
    dump_json,
    infer_category,
    load_captures,
    load_family_docs,
    quality_metrics,
    read_jsonl,
    write_jsonl,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score WorldQuant alpha candidates with local heuristics.")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSONL candidate file from alpha_batch_miner.py or a compatible source.",
    )
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
        "--output",
        type=Path,
        default=None,
        help="Optional scored JSONL output path. Defaults to stdout.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Optional CSV output path for spreadsheet inspection.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="Optional markdown summary path.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=62.0,
        help="Score threshold used for the keep/review/drop decision.",
    )
    parser.add_argument(
        "--selected-only",
        action="store_true",
        help="Emit only keep/review candidates instead of the full scored pool.",
    )
    return parser.parse_args()


def build_family_index(family_docs: tuple[ParsedFamilyDoc, ...]) -> dict[str, ParsedFamilyDoc]:
    index: dict[str, ParsedFamilyDoc] = {}
    for doc in family_docs:
        index[doc.topic] = doc
        index[doc.path.name] = doc
        index[doc.path.stem] = doc
        index[str(doc.path)] = doc
    return index


def build_capture_index(captures: tuple[ParsedCapture, ...]) -> dict[str, list[str]]:
    history: list[str] = []
    dead: list[str] = []
    for capture in captures:
        history.extend(capture.expressions)
        if capture.is_dead:
            dead.extend(capture.expressions)
    return {"history": history, "dead": dead}


def family_population(doc: ParsedFamilyDoc | None) -> list[str]:
    if doc is None:
        return []
    return [canonicalize_expression(expr) for expr in doc.all_expressions]


def attach_scorecard(
    record: dict[str, Any],
    family_doc: ParsedFamilyDoc | None,
    dead_population: list[str],
    history_population: list[str],
    seed_population: list[str],
    min_score: float,
) -> dict[str, Any]:
    expression = canonicalize_expression(str(record.get("expression") or ""))
    if not expression:
        return record

    metrics = quality_metrics(
        expression,
        family=family_doc,
        seed_population=seed_population,
        dead_population=dead_population,
        history_population=history_population,
    )

    generation_scorecard = record.get("scorecard")
    if isinstance(generation_scorecard, dict):
        record["generation_scorecard"] = generation_scorecard
    record["scorecard"] = metrics
    record["selection"] = {
        "keep": metrics["decision"] == "keep" and metrics["score"] >= min_score,
        "review": metrics["decision"] == "review" and metrics["score"] >= min_score,
        "drop": metrics["decision"] == "drop" or metrics["score"] < min_score,
    }
    record["family_category_inferred"] = infer_category(expression)
    if family_doc is not None:
        record["family_doc"] = str(family_doc.path)
        record["family_topic"] = family_doc.topic
        record["family_category"] = family_doc.category
    else:
        record.setdefault("family_category", record["family_category_inferred"])
    return record


def build_summary(
    scored_records: list[dict[str, Any]],
    family_docs: tuple[ParsedFamilyDoc, ...],
    min_score: float,
) -> str:
    counts = Counter(record["scorecard"]["decision"] for record in scored_records)
    selected = [record for record in scored_records if record["selection"]["keep"] or record["selection"]["review"]]
    selected_count = len(selected)
    best = max(scored_records, key=lambda record: (record["scorecard"]["score"], -record["scorecard"]["overfit_risk"]), default=None)

    lines = [
        "# Alpha Scorecard Summary",
        "",
        f"- Input candidates: {len(scored_records)}",
        f"- Family docs: {len(family_docs)}",
        f"- Min score: {min_score:.2f}",
        f"- Selected: {selected_count}",
        f"- Keep: {counts.get('keep', 0)}",
        f"- Review: {counts.get('review', 0)}",
        f"- Drop: {counts.get('drop', 0)}",
        "",
    ]

    if best:
        lines.extend(
            [
                "## Best Candidate",
                "",
                f"- Score: {best['scorecard']['score']:.2f}",
                f"- Decision: {best['scorecard']['decision']}",
                f"- Family: {best.get('family_topic', 'unknown')}",
                f"- Template: {best.get('template_id', 'unknown')}",
                f"- Expression: `{best['expression']}`",
                "",
            ]
        )

    top_by_family: dict[str, dict[str, Any]] = {}
    for record in scored_records:
        family = str(record.get("family_topic") or "unknown")
        current = top_by_family.get(family)
        if current is None or record["scorecard"]["score"] > current["scorecard"]["score"]:
            top_by_family[family] = record

    lines.append("## Top Family Anchors")
    lines.append("")
    for family, record in sorted(top_by_family.items(), key=lambda item: (-item[1]["scorecard"]["score"], item[0])):
        lines.append(
            f"- {family}: score {record['scorecard']['score']:.2f}, "
            f"decision {record['scorecard']['decision']}, template {record.get('template_id', 'unknown')}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    family_docs = load_family_docs(args.family_dir, include_dead=True)
    captures = load_captures(args.capture_dir) if args.capture_dir.exists() else tuple()
    bank = build_expression_bank(family_docs, captures)
    family_index = build_family_index(family_docs)
    capture_index = build_capture_index(captures)

    input_records = read_jsonl(args.input)
    scored_records: list[dict[str, Any]] = []
    for record in input_records:
        family_doc = family_index.get(str(record.get("family_topic") or ""))
        if family_doc is None and record.get("source_doc"):
            source_doc = Path(str(record["source_doc"]))
            family_doc = family_index.get(source_doc.name) or family_index.get(source_doc.stem) or family_index.get(str(source_doc))

        seed_population = family_population(family_doc)
        if not seed_population and record.get("source_expression"):
            seed_population = [canonicalize_expression(str(record["source_expression"]))]

        scored = attach_scorecard(
            dict(record),
            family_doc,
            dead_population=bank["dead"],
            history_population=bank["history"] + capture_index["history"],
            seed_population=seed_population,
            min_score=args.min_score,
        )
        if args.selected_only and scored["selection"]["drop"]:
            continue
        scored_records.append(scored)

    scored_records.sort(
        key=lambda record: (
            -float(record["scorecard"]["score"]),
            int(record.get("mutation_depth", 0)),
            -float(record["scorecard"].get("family_fit_score", 0.0)),
            str(record.get("candidate_id", "")),
        )
    )

    write_jsonl(scored_records, args.output)

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
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
                    "decision",
                    "expression",
                    "source_doc",
                    "mutations",
                ],
            )
            writer.writeheader()
            for record in scored_records:
                scorecard = record["scorecard"]
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
                        "decision": scorecard["decision"],
                        "expression": record.get("expression"),
                        "source_doc": record.get("source_doc"),
                        "mutations": " | ".join(record.get("mutations", [])),
                    }
                )

    summary_text = build_summary(scored_records, family_docs, args.min_score)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(summary_text + "\n", encoding="utf-8")
    else:
        print(summary_text, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

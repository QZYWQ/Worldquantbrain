#!/usr/bin/env python3
"""Generate a large, constrained pool of alpha candidates.

This script is intentionally conservative:

- it starts from existing family docs
- it mutates only a small set of structural axes
- it skips dead branches automatically when they are detectable
- it keeps the search local so the later scorecard can converge cleanly

The output is JSONL so it can be piped into the scorecard or inspected by hand.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Any, Iterable

from alpha_mining_core import (
    ParsedCapture,
    ParsedFamilyDoc,
    MutationPlan,
    abstract_expression,
    apply_mutation,
    best_similarity,
    build_expression_bank,
    candidate_from_expression,
    canonicalize_expression,
    dedupe_strings,
    dump_json,
    expression_signature,
    load_captures,
    load_family_docs,
    load_token_replacements,
    primitive_mutations,
    summarise_capture,
    summarise_family,
    write_jsonl,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate constrained WorldQuant alpha candidates.")
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
        "--token-map",
        type=Path,
        default=None,
        help="Optional JSON token replacement map for field-replacement experiments.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSONL output path. Defaults to stdout.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional summary JSON path for the generated pool.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=1000,
        help="Hard cap on emitted candidates.",
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
    return parser.parse_args()


def template_id_from_chain(chain: Iterable[MutationPlan]) -> str:
    kinds: list[str] = []
    for plan in chain:
        if plan.kind not in kinds:
            kinds.append(plan.kind)
    return "baseline" if not kinds else "+".join(kinds)


def enumerate_seed_candidates(
    family: ParsedFamilyDoc,
    seed_expression: str,
    *,
    seed_population: list[str],
    dead_population: list[str],
    history_population: list[str],
    token_rules: tuple[dict[str, Any], ...],
    per_seed_limit: int,
    max_depth: int,
    reject_dead_similarity: float,
) -> tuple[dict[str, Any], ...]:
    seed_expression = canonicalize_expression(seed_expression)
    queue: list[tuple[str, tuple[MutationPlan, ...]]] = [(seed_expression, tuple())]
    seen_signatures: set[str] = {expression_signature(seed_expression)}
    emitted: list[dict[str, Any]] = []

    baseline = candidate_from_expression(
        seed_expression,
        family,
        seed_expression,
        str(family.path),
        (),
        seed_population,
        dead_population,
        history_population,
    )
    baseline["template_id"] = "baseline"
    baseline["generation_priority"] = 1.0
    baseline["seed_expression"] = seed_expression
    baseline["source_similarity"] = round(best_similarity(seed_expression, seed_population), 4) if seed_population else 0.0
    if baseline["scorecard"]["dead_similarity"] < reject_dead_similarity:
        emitted.append(baseline)

    while queue and len(emitted) < per_seed_limit:
        current_expression, chain = queue.pop(0)
        if chain:
            candidate = candidate_from_expression(
                current_expression,
                family,
                seed_expression,
                str(family.path),
                chain,
                seed_population,
                dead_population,
                history_population,
            )
            if candidate["scorecard"]["dead_similarity"] < reject_dead_similarity:
                candidate["template_id"] = template_id_from_chain(chain)
                candidate["generation_priority"] = round(
                    sum(plan.priority for plan in chain) / max(len(chain), 1), 4
                )
                candidate["seed_expression"] = seed_expression
                candidate["source_similarity"] = round(
                    best_similarity(candidate["expression"], seed_population), 4
                ) if seed_population else 0.0
                emitted.append(candidate)

        if len(chain) >= max_depth:
            continue

        for plan in primitive_mutations(current_expression, token_rules=token_rules):
            mutated = apply_mutation(current_expression, plan)
            if not mutated:
                continue

            canonical = canonicalize_expression(mutated)
            signature = expression_signature(canonical)
            if signature in seen_signatures:
                continue
            if best_similarity(canonical, dead_population) >= reject_dead_similarity:
                continue

            seen_signatures.add(signature)
            queue.append((canonical, chain + (plan,)))

    return tuple(emitted[:per_seed_limit])


def build_candidate_pool(
    family_docs: tuple[ParsedFamilyDoc, ...],
    bank: dict[str, list[str]],
    token_rules: tuple[dict[str, Any], ...],
    *,
    max_candidates: int,
    per_seed: int,
    max_depth: int,
    reject_dead_similarity: float,
    seed_limit: int,
) -> tuple[dict[str, Any], ...]:
    candidates: list[dict[str, Any]] = []
    seen_candidate_signatures: set[str] = set()

    seed_docs = [doc for doc in family_docs if not doc.is_dead]
    if seed_limit > 0:
        seed_docs = seed_docs[:seed_limit]

    for family in seed_docs:
        family_seed_population = dedupe_strings(family.all_expressions)
        if not family_seed_population and family.baseline_expression:
            family_seed_population = [canonicalize_expression(family.baseline_expression)]
        seed_expressions = dedupe_strings(family.all_expressions)
        if not seed_expressions and family.baseline_expression:
            seed_expressions = [canonicalize_expression(family.baseline_expression)]

        for seed_expression in seed_expressions:
            if len(candidates) >= max_candidates:
                return tuple(candidates)

            per_seed_candidates = enumerate_seed_candidates(
                family,
                seed_expression,
                seed_population=family_seed_population,
                dead_population=bank["dead"],
                history_population=bank["history"],
                token_rules=token_rules,
                per_seed_limit=per_seed,
                max_depth=max_depth,
                reject_dead_similarity=reject_dead_similarity,
            )
            for candidate in per_seed_candidates:
                signature = candidate["scorecard"]["signature"]
                if signature in seen_candidate_signatures:
                    continue
                seen_candidate_signatures.add(signature)
                candidates.append(candidate)
                if len(candidates) >= max_candidates:
                    break

    return tuple(candidates)


def build_manifest(
    family_docs: tuple[ParsedFamilyDoc, ...],
    captures: tuple[ParsedCapture, ...],
    bank: dict[str, list[str]],
    candidates: tuple[dict[str, Any], ...],
    args: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "family_count": len(family_docs),
        "capture_count": len(captures),
        "seed_count": len(bank["seeds"]),
        "dead_count": len(bank["dead"]),
        "history_count": len(bank["history"]),
        "candidate_count": len(candidates),
        "settings": {
            "max_candidates": args.max_candidates,
            "per_seed": args.per_seed,
            "max_depth": args.max_depth,
            "reject_dead_similarity": args.reject_dead_similarity,
            "seed_limit": args.seed_limit,
        },
        "family_docs": [summarise_family(doc) for doc in family_docs[:10]],
        "capture_docs": [summarise_capture(capture) for capture in captures[:10]],
        "first_candidates": [
            {
                "candidate_id": candidate["candidate_id"],
                "template_id": candidate.get("template_id"),
                "score": candidate["scorecard"]["score"],
                "decision": candidate["scorecard"]["decision"],
                "expression": candidate["expression"],
            }
            for candidate in candidates[:10]
        ],
    }


def main() -> int:
    args = parse_args()
    family_docs = load_family_docs(args.family_dir, include_dead=True)
    captures = load_captures(args.capture_dir) if args.capture_dir.exists() else tuple()
    bank = build_expression_bank(family_docs, captures)
    token_rules = load_token_replacements(args.token_map)

    if not family_docs:
        raise SystemExit(f"No expression-family docs found in {args.family_dir}")

    candidates = build_candidate_pool(
        family_docs,
        bank,
        token_rules,
        max_candidates=args.max_candidates,
        per_seed=args.per_seed,
        max_depth=args.max_depth,
        reject_dead_similarity=args.reject_dead_similarity,
        seed_limit=args.seed_limit,
    )

    candidates = tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                -float(candidate["scorecard"]["score"]),
                int(candidate["mutation_depth"]),
                -float(candidate.get("generation_priority", 0.0)),
                candidate["candidate_id"],
            ),
        )
    )

    write_jsonl(candidates, args.output)
    manifest = build_manifest(family_docs, captures, bank, candidates, args)
    if args.manifest:
        dump_json(args.manifest, manifest)
    else:
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Publish durable evidence-ladder artifacts for local alpha research."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re

from alpha_mining_core import dump_json, load_family_docs
from alpha_success_core import build_combined_outcome_memory, build_family_registry_summary
from evidence_ladder_core import build_evidence_ladder_report, render_evidence_ladder_md
from alpha_success_core import normalize_family_key


DEFAULT_ARTIFACT_ROOT = Path("harness/artifacts/evidence-ladders")
DEFAULT_PUBLISH_ROOT = Path("runs/evidence-ladders")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a durable evidence-ladder artifact.")
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
        help="Optional durable candidate-batch directory used as read-only evidence input.",
    )
    parser.add_argument(
        "--candidate-check-dir",
        type=Path,
        default=Path("harness/artifacts"),
        help="Optional candidate-check artifact directory used as read-only evidence input.",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=DEFAULT_ARTIFACT_ROOT,
        help="Parent directory for the generated evidence-ladder bundle.",
    )
    parser.add_argument(
        "--publish-root",
        type=Path,
        default=DEFAULT_PUBLISH_ROOT,
        help="Durable output root used for the published evidence-ladder copy.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id. Defaults to YYYY-MM-DD-evidence-ladders.",
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
    return parser.parse_args()


def default_run_id(args: argparse.Namespace) -> str:
    if args.run_id:
        return args.run_id
    return f"{datetime.now().strftime('%Y-%m-%d')}-evidence-ladders"


def compile_patterns(patterns: list[str]) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns if pattern.strip())


def should_include_family(
    doc,
    *,
    include_patterns: tuple[re.Pattern[str], ...],
    exclude_patterns: tuple[re.Pattern[str], ...],
) -> bool:
    haystack = "\n".join(
        (
            str(getattr(doc, "topic", "") or ""),
            str(getattr(doc, "title", "") or ""),
            str(getattr(doc, "path", "") or ""),
        )
    )
    if include_patterns and not any(pattern.search(haystack) for pattern in include_patterns):
        return False
    if exclude_patterns and any(pattern.search(haystack) for pattern in exclude_patterns):
        return False
    return True


def ensure_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")


def main() -> int:
    args = parse_args()
    run_id = default_run_id(args)
    output_root = args.artifact_root / run_id
    include_patterns = compile_patterns(args.include_topic)
    exclude_patterns = compile_patterns(args.exclude_topic)

    family_docs = load_family_docs(args.family_dir, include_dead=True)
    selected_family_docs = [
        doc
        for doc in family_docs
        if should_include_family(
            doc,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
    ]
    outcome_memory = build_combined_outcome_memory(
        args.capture_dir if args.capture_dir.exists() else [],
        candidate_batches=(args.candidate_batch_dir if args.candidate_batch_dir.exists() else None),
        candidate_check_artifacts=(args.candidate_check_dir if args.candidate_check_dir.exists() else None),
    )
    selected_family_keys = {
        normalize_family_key(str(getattr(doc, "topic", "") or ""))
        for doc in selected_family_docs
    }
    filtered_outcome_memory = [
        record
        for record in outcome_memory
        if normalize_family_key(str(record.get("family_key") or "")) in selected_family_keys
    ]
    family_registry = build_family_registry_summary(
        [doc.path for doc in selected_family_docs],
        filtered_outcome_memory,
    )
    report = build_evidence_ladder_report(
        family_docs=selected_family_docs,
        outcome_memory=filtered_outcome_memory,
        family_registry=family_registry,
    )
    report["run_id"] = run_id
    report["settings"] = {
        "family_dir": str(args.family_dir),
        "capture_dir": str(args.capture_dir),
        "candidate_batch_dir": str(args.candidate_batch_dir),
        "candidate_check_dir": str(args.candidate_check_dir),
        "include_topic": list(args.include_topic),
        "exclude_topic": list(args.exclude_topic),
    }

    output_root.mkdir(parents=True, exist_ok=True)
    manifest_json_path = output_root / "manifest.json"
    manifest_md_path = output_root / "manifest.md"
    publish_json_path = args.publish_root / f"{run_id}.json"
    publish_md_path = args.publish_root / f"{run_id}.md"

    dump_json(manifest_json_path, report)
    ensure_text(manifest_md_path, render_evidence_ladder_md(report))
    dump_json(publish_json_path, report)
    ensure_text(publish_md_path, render_evidence_ladder_md(report))

    print(f"Run bundle: {output_root}")
    print(f"Published JSON: {publish_json_path}")
    print(f"Published MD: {publish_md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

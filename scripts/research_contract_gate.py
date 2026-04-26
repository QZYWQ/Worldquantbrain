#!/usr/bin/env python3
"""Publish durable family research-contract gate artifacts."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re

from alpha_mining_core import dump_json, load_family_docs
from research_contract_core import (
    build_research_contract_report,
    render_research_contract_md,
)


DEFAULT_ARTIFACT_ROOT = Path("harness/artifacts/research-contracts")
DEFAULT_PUBLISH_ROOT = Path("runs/research-contracts")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a durable family research-contract gate artifact.")
    parser.add_argument(
        "--family-dir",
        type=Path,
        default=Path("runs/expression-families"),
        help="Directory containing expression-family markdown docs.",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=DEFAULT_ARTIFACT_ROOT,
        help="Parent directory for the generated contract bundle.",
    )
    parser.add_argument(
        "--publish-root",
        type=Path,
        default=DEFAULT_PUBLISH_ROOT,
        help="Durable output root used for the published contract copy.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id. Defaults to YYYY-MM-DD-research-contracts.",
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
    return f"{datetime.now().strftime('%Y-%m-%d')}-research-contracts"


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
    report = build_research_contract_report(family_docs=selected_family_docs)
    report["run_id"] = run_id
    report["settings"] = {
        "family_dir": str(args.family_dir),
        "include_topic": list(args.include_topic),
        "exclude_topic": list(args.exclude_topic),
    }

    output_root.mkdir(parents=True, exist_ok=True)
    manifest_json_path = output_root / "manifest.json"
    manifest_md_path = output_root / "manifest.md"
    publish_json_path = args.publish_root / f"{run_id}.json"
    publish_md_path = args.publish_root / f"{run_id}.md"

    dump_json(manifest_json_path, report)
    ensure_text(manifest_md_path, render_research_contract_md(report))
    dump_json(publish_json_path, report)
    ensure_text(publish_md_path, render_research_contract_md(report))

    print(f"Run bundle: {output_root}")
    print(f"Published JSON: {publish_json_path}")
    print(f"Published MD: {publish_md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

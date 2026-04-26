#!/usr/bin/env python3
"""Shared validation-design parsing and gating helpers."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from alpha_success_core import normalize_family_key


SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
METADATA_RE = re.compile(r"^\s*-\s+([^:]+):\s*(.*)$")

REQUIRED_VALIDATION_FIELDS = (
    "primary_test_period",
    "regime_slices",
    "liquidity_slice",
    "subuniverse_gate",
    "factor_overlay",
    "comparison_controls",
    "promotion_rule",
    "demotion_rule",
)

VALIDATION_KEY_ALIASES = {
    "primary_test_period": "primary_test_period",
    "test_period": "primary_test_period",
    "regime_slices": "regime_slices",
    "regime_slice": "regime_slices",
    "liquidity_slice": "liquidity_slice",
    "subuniverse_gate": "subuniverse_gate",
    "sub_universe_gate": "subuniverse_gate",
    "subuniverse_check": "subuniverse_gate",
    "factor_overlay": "factor_overlay",
    "factor_neutralization_overlay": "factor_overlay",
    "comparison_controls": "comparison_controls",
    "controls": "comparison_controls",
    "promotion_rule": "promotion_rule",
    "demotion_rule": "demotion_rule",
}

EMPTY_PLACEHOLDER_VALUES = {
    "",
    "-",
    "na",
    "n_a",
    "none",
    "todo",
    "tbd",
    "later",
}

PERIOD_HINT_RE = re.compile(r"\b(?:p\d+[dwmy]|p\d+[ym]|p\d+|[1-9]\d*\s*(?:day|days|week|weeks|month|months|year|years|d|w|m|y))\b", re.IGNORECASE)


def _split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        heading = SECTION_HEADING_RE.match(line)
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _strip_inline_code(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("`") and stripped.endswith("`") and len(stripped) >= 2:
        return stripped[1:-1].strip()
    return stripped


def _normalize_validation_key(label: str) -> str:
    normalized = normalize_family_key(
        label.replace("/", "_")
        .replace("-", "_")
    )
    return VALIDATION_KEY_ALIASES.get(normalized, normalized)


def _parse_validation_section(section_text: str) -> dict[str, str]:
    validation: dict[str, str] = {}
    for line in section_text.splitlines():
        match = METADATA_RE.match(line)
        if not match:
            continue
        key = _normalize_validation_key(match.group(1).strip())
        value = _strip_inline_code(match.group(2))
        if value:
            validation[key] = value
    return validation


def _family_key_from_doc(doc: Any) -> str:
    topic = str(getattr(doc, "topic", "") or "")
    if topic:
        return normalize_family_key(topic)
    path = getattr(doc, "path", None)
    if path is not None:
        return normalize_family_key(Path(path).stem)
    return "unknown_family"


def _is_placeholder(value: str) -> bool:
    return normalize_family_key(value) in EMPTY_PLACEHOLDER_VALUES


def _looks_like_period(value: str) -> bool:
    return bool(PERIOD_HINT_RE.search(value or ""))


def build_validation_design_report(*, family_docs: Sequence[Any]) -> dict[str, Any]:
    docs_by_family: dict[str, list[Any]] = {}
    for doc in family_docs:
        docs_by_family.setdefault(_family_key_from_doc(doc), []).append(doc)

    items: list[dict[str, Any]] = []
    for family_key in sorted(docs_by_family):
        docs = docs_by_family[family_key]
        merged_design: dict[str, str] = {}
        design_sources: list[dict[str, Any]] = []

        for doc in docs:
            raw_text = str(getattr(doc, "raw_text", "") or "")
            sections = _split_sections(raw_text)
            design = _parse_validation_section(sections.get("Validation Design", ""))
            if design:
                design_sources.append({"path": str(getattr(doc, "path", "")), "validation_design": dict(design)})
                for key, value in design.items():
                    merged_design.setdefault(key, value)

        block_reasons: list[str] = []
        hold_reasons: list[str] = []
        if not design_sources:
            block_reasons.append("family doc is missing a `Validation Design` section")

        missing_fields = [
            field
            for field in REQUIRED_VALIDATION_FIELDS
            if not str(merged_design.get(field, "")).strip()
        ]
        if missing_fields:
            block_reasons.append(
                "validation design is missing required fields: " + ", ".join(missing_fields)
            )

        primary_test_period = str(merged_design.get("primary_test_period", "")).strip()
        if primary_test_period and not _looks_like_period(primary_test_period):
            hold_reasons.append("validation design primary test period is not parseable as a period or duration")

        comparison_controls = str(merged_design.get("comparison_controls", "")).strip()
        if comparison_controls and _is_placeholder(comparison_controls):
            hold_reasons.append("validation design comparison controls are still empty placeholders")

        factor_overlay = str(merged_design.get("factor_overlay", "")).strip()
        if factor_overlay and _is_placeholder(factor_overlay):
            hold_reasons.append("validation design factor overlay is still empty or explicitly disabled")

        if block_reasons:
            gate_status = "block"
            reasons = block_reasons
        elif hold_reasons:
            gate_status = "hold"
            reasons = hold_reasons
        else:
            gate_status = "pass"
            reasons = ["validation-design gate passed"]

        items.append(
            {
                "family_key": family_key,
                "source_family_doc_paths": [str(getattr(doc, "path", "")) for doc in docs],
                "validation_design": merged_design,
                "validation_sources": design_sources,
                "assessment": {
                    "gate_status": gate_status,
                    "reasons": reasons,
                    "missing_fields": missing_fields,
                },
            }
        )

    counts = {
        "family_count": len(items),
        "pass_count": sum(1 for item in items if item["assessment"]["gate_status"] == "pass"),
        "hold_count": sum(1 for item in items if item["assessment"]["gate_status"] == "hold"),
        "block_count": sum(1 for item in items if item["assessment"]["gate_status"] == "block"),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "bind each family to an explicit validation matrix before local mining continues",
        "required_fields": list(REQUIRED_VALIDATION_FIELDS),
        "counts": counts,
        "items": items,
    }


def index_validation_design(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_validation_design_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Validation Design",
        "",
        f"- Objective: {report.get('objective', 'validation design')}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Pass: {counts.get('pass_count', 0)}",
        f"- Hold: {counts.get('hold_count', 0)}",
        f"- Block: {counts.get('block_count', 0)}",
        "",
        "| family | gate | primary period | liquidity | subuniverse | factor overlay | reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        design = item.get("validation_design", {})
        assessment = item.get("assessment", {})
        lines.append(
            "| {family_key} | {gate_status} | {primary_test_period} | {liquidity_slice} | {subuniverse_gate} | {factor_overlay} | {reasons} |".format(
                family_key=item.get("family_key"),
                gate_status=assessment.get("gate_status"),
                primary_test_period=design.get("primary_test_period", "-"),
                liquidity_slice=design.get("liquidity_slice", "-"),
                subuniverse_gate=design.get("subuniverse_gate", "-"),
                factor_overlay=design.get("factor_overlay", "-"),
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    return "\n".join(lines)

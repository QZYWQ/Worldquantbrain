#!/usr/bin/env python3
"""Shared family research-contract parsing and gating helpers."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from alpha_success_core import normalize_family_key


SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
METADATA_RE = re.compile(r"^\s*-\s+([^:]+):\s*(.*)$")
PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
INTEGER_RE = re.compile(r"-?\d+")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")

REQUIRED_CONTRACT_FIELDS = (
    "mechanism",
    "data_category",
    "idea_type",
    "universe",
    "liquidity_fit",
    "holding_frequency",
    "delay",
    "neutralization_target",
    "decay",
    "truncation",
    "nan_policy",
    "pasteurization",
    "unit_handling",
    "coverage_floor_pct",
    "freshness_floor_days",
    "factor_risk_hypothesis",
    "kill_condition",
)

FAST_HOLDING_FREQUENCIES = {"intraday", "high_frequency"}
ALLOWED_HOLDING_FREQUENCIES = {"slow", "medium", "event", "intraday", "high_frequency"}
ALLOWED_LIQUIDITY_FITS = {
    "broad_liquid",
    "high_liquidity_only",
    "top_liquid",
    "sparse_event_acceptable",
    "sparse_fundamental_acceptable",
}
ALLOWED_PASTEURIZATION = {"enabled", "disabled", "inherit_platform_default"}
NEUTRALIZATION_NONE_VALUES = {"none", "na", "n_a", "not_applicable"}

CONTRACT_KEY_ALIASES = {
    "data_category": "data_category",
    "category": "data_category",
    "idea_type": "idea_type",
    "mechanism": "mechanism",
    "universe": "universe",
    "universe_fit": "universe",
    "liquidity_fit": "liquidity_fit",
    "holding_frequency": "holding_frequency",
    "signal_speed": "holding_frequency",
    "delay": "delay",
    "delay_class": "delay",
    "neutralization_target": "neutralization_target",
    "neutralization": "neutralization_target",
    "decay": "decay",
    "truncation": "truncation",
    "nan_policy": "nan_policy",
    "nan_handling": "nan_policy",
    "pasteurization": "pasteurization",
    "unit_handling": "unit_handling",
    "coverage_floor": "coverage_floor_pct",
    "coverage_floor_pct": "coverage_floor_pct",
    "freshness_floor": "freshness_floor_days",
    "freshness_floor_days": "freshness_floor_days",
    "factor_risk_hypothesis": "factor_risk_hypothesis",
    "kill_condition": "kill_condition",
}


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


def _normalize_contract_key(label: str) -> str:
    normalized = normalize_family_key(
        label.replace("/", "_")
        .replace("%", "_pct")
        .replace("-", "_")
    )
    return CONTRACT_KEY_ALIASES.get(normalized, normalized)


def _parse_contract_section(section_text: str) -> dict[str, str]:
    contract: dict[str, str] = {}
    for line in section_text.splitlines():
        match = METADATA_RE.match(line)
        if not match:
            continue
        key = _normalize_contract_key(match.group(1).strip())
        value = _strip_inline_code(match.group(2))
        if value:
            contract[key] = value
    return contract


def _percent_value(value: str) -> float | None:
    match = PERCENT_RE.search(value or "")
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _int_value(value: str) -> int | None:
    match = INTEGER_RE.search(value or "")
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def _first_non_empty(values: Sequence[str]) -> str:
    for value in values:
        if value:
            return value
    return ""


def _expressions_reference_target(expressions: Sequence[str], target: str) -> bool:
    if not target:
        return False
    pattern = re.compile(rf"\b{re.escape(target)}\b")
    return any(pattern.search(expression or "") for expression in expressions)


def build_research_contract_report(*, family_docs: Sequence[Any]) -> dict[str, Any]:
    docs_by_family: dict[str, list[Any]] = {}
    for doc in family_docs:
        family_key = normalize_family_key(str(getattr(doc, "topic", "") or getattr(doc, "path", "")))
        docs_by_family.setdefault(family_key, []).append(doc)

    items: list[dict[str, Any]] = []
    for family_key in sorted(docs_by_family):
        docs = docs_by_family[family_key]
        merged_contract: dict[str, str] = {}
        contract_sources: list[dict[str, Any]] = []
        expressions: list[str] = []
        metadata_universe_values: list[str] = []
        metadata_delay_values: list[str] = []
        metadata_region_values: list[str] = []

        for doc in docs:
            raw_text = str(getattr(doc, "raw_text", "") or "")
            sections = _split_sections(raw_text)
            contract = _parse_contract_section(sections.get("Research Contract", ""))
            if contract:
                contract_sources.append({"path": str(getattr(doc, "path", "")), "contract": dict(contract)})
                for key, value in contract.items():
                    merged_contract.setdefault(key, value)

            metadata_universe_values.append(str(getattr(doc, "universe", "") or ""))
            metadata_delay_values.append(str(getattr(doc, "delay", "") or ""))
            metadata_region_values.append(str(getattr(doc, "region", "") or ""))

            baseline_expression = str(getattr(doc, "baseline_expression", "") or "")
            variant_expressions = [str(value) for value in getattr(doc, "variant_expressions", ()) if str(value)]
            all_expressions = [str(value) for value in getattr(doc, "all_expressions", ()) if str(value)]
            expressions.extend(value for value in [baseline_expression, *variant_expressions, *all_expressions] if value)

        metadata_universe = _first_non_empty(metadata_universe_values)
        metadata_delay = _first_non_empty(metadata_delay_values)
        metadata_region = _first_non_empty(metadata_region_values)

        block_reasons: list[str] = []
        hold_reasons: list[str] = []

        if not contract_sources:
            block_reasons.append("family doc is missing a `Research Contract` section")

        missing_fields = [
            field
            for field in REQUIRED_CONTRACT_FIELDS
            if not str(merged_contract.get(field, "")).strip()
        ]
        if missing_fields:
            block_reasons.append(
                "research contract is missing required fields: " + ", ".join(missing_fields)
            )

        coverage_floor_pct = _percent_value(str(merged_contract.get("coverage_floor_pct", "")))
        if merged_contract.get("coverage_floor_pct") and coverage_floor_pct is None:
            hold_reasons.append("research contract coverage floor is not a parseable percentage")

        freshness_floor_days = _int_value(str(merged_contract.get("freshness_floor_days", "")))
        if merged_contract.get("freshness_floor_days") and freshness_floor_days is None:
            hold_reasons.append("research contract freshness floor is not a parseable integer day count")

        holding_frequency = normalize_family_key(str(merged_contract.get("holding_frequency", "")))
        if holding_frequency and holding_frequency not in ALLOWED_HOLDING_FREQUENCIES:
            hold_reasons.append(
                "research contract holding frequency must be one of: "
                + ", ".join(sorted(ALLOWED_HOLDING_FREQUENCIES))
            )

        liquidity_fit = normalize_family_key(str(merged_contract.get("liquidity_fit", "")))
        if liquidity_fit and liquidity_fit not in ALLOWED_LIQUIDITY_FITS:
            hold_reasons.append(
                "research contract liquidity fit must be one of: "
                + ", ".join(sorted(ALLOWED_LIQUIDITY_FITS))
            )

        pasteurization = normalize_family_key(str(merged_contract.get("pasteurization", "")))
        if pasteurization and pasteurization not in ALLOWED_PASTEURIZATION:
            hold_reasons.append(
                "research contract pasteurization must be one of: "
                + ", ".join(sorted(ALLOWED_PASTEURIZATION))
            )

        contract_universe = str(merged_contract.get("universe", "")).strip().upper()
        if contract_universe and metadata_universe and contract_universe != metadata_universe.upper():
            hold_reasons.append(
                f"research contract universe `{contract_universe}` does not match metadata universe `{metadata_universe}`"
            )

        contract_delay = str(merged_contract.get("delay", "")).strip()
        if contract_delay and metadata_delay and contract_delay != metadata_delay:
            hold_reasons.append(
                f"research contract delay `{contract_delay}` does not match metadata delay `{metadata_delay}`"
            )

        effective_delay = contract_delay or metadata_delay
        if holding_frequency in FAST_HOLDING_FREQUENCIES and effective_delay != "0":
            hold_reasons.append(
                f"holding frequency `{holding_frequency}` requires delay `0`, but the family is configured for delay `{effective_delay or '-'}'"
            )

        neutralization_target = normalize_family_key(str(merged_contract.get("neutralization_target", "")))
        if neutralization_target and neutralization_target not in NEUTRALIZATION_NONE_VALUES:
            if not _expressions_reference_target(tuple(expressions), neutralization_target):
                hold_reasons.append(
                    "research contract neutralization target is not referenced by baseline or variant expressions"
                )

        if block_reasons:
            gate_status = "block"
            reasons = block_reasons
        elif hold_reasons:
            gate_status = "hold"
            reasons = hold_reasons
        else:
            gate_status = "pass"
            reasons = ["research-contract gate passed"]

        items.append(
            {
                "family_key": family_key,
                "source_family_doc_paths": [str(getattr(doc, "path", "")) for doc in docs],
                "metadata": {
                    "region": metadata_region,
                    "universe": metadata_universe,
                    "delay": metadata_delay,
                    "category": str(getattr(docs[0], "category", "") or "") if docs else "",
                },
                "contract": merged_contract,
                "contract_sources": contract_sources,
                "coverage_floor_pct": coverage_floor_pct,
                "freshness_floor_days": freshness_floor_days,
                "assessment": {
                    "gate_status": gate_status,
                    "reasons": reasons,
                    "missing_fields": missing_fields,
                    "holding_frequency": holding_frequency or None,
                    "liquidity_fit": liquidity_fit or None,
                    "neutralization_target": neutralization_target or None,
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
        "objective": "gate local mining on a family research contract before seed expansion or queue promotion",
        "required_fields": list(REQUIRED_CONTRACT_FIELDS),
        "counts": counts,
        "items": items,
    }


def index_research_contract_report(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_research_contract_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Family Research Contract Gate",
        "",
        f"- Objective: {report.get('objective', 'family research contract gate')}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Pass: {counts.get('pass_count', 0)}",
        f"- Hold: {counts.get('hold_count', 0)}",
        f"- Block: {counts.get('block_count', 0)}",
        "",
        "| family | gate | universe | delay | holding frequency | neutralization | reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        contract = item.get("contract", {})
        assessment = item.get("assessment", {})
        lines.append(
            "| {family_key} | {gate_status} | {universe} | {delay} | {holding_frequency} | {neutralization_target} | {reasons} |".format(
                family_key=item.get("family_key"),
                gate_status=assessment.get("gate_status"),
                universe=contract.get("universe") or item.get("metadata", {}).get("universe") or "-",
                delay=contract.get("delay") or item.get("metadata", {}).get("delay") or "-",
                holding_frequency=contract.get("holding_frequency") or "-",
                neutralization_target=contract.get("neutralization_target") or "-",
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    lines.append("## Reasons")
    lines.append("")
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        lines.append(f"- `{item.get('family_key')}` -> `{assessment.get('gate_status')}`")
        for reason in assessment.get("reasons", []):
            lines.append(f"  - {reason}")
    lines.append("")
    return "\n".join(lines)

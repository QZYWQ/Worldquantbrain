#!/usr/bin/env python3
"""Mechanism-level failure-memory helpers."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from alpha_mining_core import abstract_expression, parse_function_calls, similarity_score, tokenize_expression
from alpha_success_core import build_family_registry_summary, normalize_family_key
from research_contract_core import build_research_contract_report, index_research_contract_report


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
RESERVED_IDENTIFIERS = {
    "and",
    "false",
    "if_else",
    "industry",
    "market",
    "none",
    "not",
    "or",
    "rank",
    "sector",
    "subindustry",
    "true",
}
NEGATIVE_STATUS_RANK = {
    "none": 0,
    "blocked_full_is": 1,
    "failed_full_is": 2,
    "hold": 3,
    "kill": 4,
    "dead_doc": 5,
}


def _family_key_from_doc(doc: Any) -> str:
    topic = str(getattr(doc, "topic", "") or "")
    if topic:
        return normalize_family_key(topic)
    path = getattr(doc, "path", None)
    if path is not None:
        return normalize_family_key(Path(path).stem)
    return "unknown_family"


def _field_tokens(expressions: Sequence[str]) -> tuple[str, ...]:
    function_names = {
        call.name.lower()
        for expression in expressions
        for call in parse_function_calls(expression)
    }
    tokens: list[str] = []
    for expression in expressions:
        for token in tokenize_expression(expression):
            lower = token.lower()
            if not IDENTIFIER_RE.match(lower):
                continue
            if lower in function_names or lower in RESERVED_IDENTIFIERS:
                continue
            if len(lower) <= 1:
                continue
            tokens.append(lower)
    return tuple(dict.fromkeys(tokens))


def _mechanism_cluster(contract: dict[str, Any]) -> str:
    return "|".join(
        (
            normalize_family_key(str(contract.get("data_category", "") or "unknown_data")),
            normalize_family_key(str(contract.get("mechanism", "") or "unknown_mechanism")),
            normalize_family_key(str(contract.get("holding_frequency", "") or "unknown_holding")),
            normalize_family_key(str(contract.get("neutralization_target", "") or "unknown_neutralization")),
        )
    )


def _uses_trade_when(expressions: Sequence[str]) -> bool:
    return any(call.name == "trade_when" for expression in expressions for call in parse_function_calls(expression))


def build_mechanism_failure_memory_report(
    *,
    family_docs: Sequence[Any] = (),
    family_registry: Sequence[dict[str, Any]] = (),
    research_contract_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not family_registry and family_docs:
        family_registry = build_family_registry_summary([getattr(doc, "path", doc) for doc in family_docs], [])
    if research_contract_report is None:
        research_contract_report = build_research_contract_report(family_docs=family_docs)

    registry_by_family = {
        str(item.get("family_key") or ""): dict(item)
        for item in family_registry
        if str(item.get("family_key") or "")
    }
    docs_by_family: dict[str, list[Any]] = {}
    for doc in family_docs:
        docs_by_family.setdefault(_family_key_from_doc(doc), []).append(doc)

    contract_by_family = index_research_contract_report(research_contract_report)
    all_family_keys = sorted(set(registry_by_family) | set(docs_by_family) | set(contract_by_family))

    items: list[dict[str, Any]] = []
    for family_key in all_family_keys:
        docs = docs_by_family.get(family_key, [])
        registry_entry = registry_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "state": "explore",
                "reason": "no family-registry entry was found",
                "failing_gate_histogram": {},
                "pending_gate_histogram": {},
                "full_gate_outcome_count": 0,
            },
        )
        contract_entry = contract_by_family.get(
            family_key,
            {
                "contract": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["research-contract record is missing for this family"],
                },
            },
        )
        contract = dict(contract_entry.get("contract", {}))
        expressions = [
            str(expression)
            for doc in docs
            for expression in getattr(doc, "all_expressions", ())
            if str(expression).strip()
        ]
        baseline_expression = next(
            (
                str(getattr(doc, "baseline_expression", "") or "")
                for doc in docs
                if str(getattr(doc, "baseline_expression", "") or "").strip()
            ),
            "",
        )
        field_tokens = _field_tokens(expressions)
        failing_gate_count = sum(int(value or 0) for value in (registry_entry.get("failing_gate_histogram") or {}).values())
        pending_gate_count = sum(int(value or 0) for value in (registry_entry.get("pending_gate_histogram") or {}).values())
        registry_state = str(registry_entry.get("state") or "explore")

        negative_status = "none"
        reasons: list[str] = []
        if any(bool(getattr(doc, "is_dead", False)) for doc in docs):
            negative_status = "dead_doc"
            reasons.append("family doc is already marked dead locally")
        elif registry_state == "kill":
            negative_status = "kill"
            reasons.append("family registry already marks this family kill")
        elif registry_state == "hold":
            negative_status = "hold"
            reasons.append("family registry already marks this family hold")
        elif int(registry_entry.get("full_gate_outcome_count", 0) or 0) > 0 and failing_gate_count > 0:
            negative_status = "failed_full_is"
            reasons.append("binding full-IS evidence already contains failing submission gates")
        elif int(registry_entry.get("full_gate_outcome_count", 0) or 0) > 0 and pending_gate_count > 0:
            negative_status = "blocked_full_is"
            reasons.append("binding full-IS evidence still contains pending submission gates")
        else:
            reasons.append("no negative mechanism-level memory has been observed yet")

        items.append(
            {
                "family_key": family_key,
                "source_family_doc_paths": [str(getattr(doc, "path", "")) for doc in docs],
                "registry_state": registry_state,
                "registry_reason": str(registry_entry.get("reason") or ""),
                "mechanism_profile": {
                    "mechanism_cluster": _mechanism_cluster(contract),
                    "data_category": str(contract.get("data_category", "") or ""),
                    "mechanism": str(contract.get("mechanism", "") or ""),
                    "idea_type": str(contract.get("idea_type", "") or ""),
                    "holding_frequency": str(contract.get("holding_frequency", "") or ""),
                    "neutralization_target": str(contract.get("neutralization_target", "") or ""),
                    "delay": str(contract.get("delay", "") or ""),
                    "universe": str(contract.get("universe", "") or ""),
                },
                "expression_profile": {
                    "baseline_expression": baseline_expression or None,
                    "abstract_baseline_expression": abstract_expression(baseline_expression) if baseline_expression else None,
                    "field_tokens": list(field_tokens),
                    "field_token_count": len(field_tokens),
                    "uses_trade_when": _uses_trade_when(expressions),
                },
                "counts": {
                    "expression_count": len(expressions),
                    "failing_gate_count": failing_gate_count,
                    "pending_gate_count": pending_gate_count,
                    "full_gate_outcome_count": int(registry_entry.get("full_gate_outcome_count", 0) or 0),
                },
                "assessment": {
                    "negative_memory_status": negative_status,
                    "negative_memory_rank": NEGATIVE_STATUS_RANK[negative_status],
                    "reasons": reasons,
                },
            }
        )

    counts = {
        "family_count": len(items),
        "negative_family_count": sum(
            1 for item in items if item.get("assessment", {}).get("negative_memory_rank", 0) > 0
        ),
        "negative_cluster_count": len(
            {
                item.get("mechanism_profile", {}).get("mechanism_cluster")
                for item in items
                if item.get("assessment", {}).get("negative_memory_rank", 0) > 0
                and str(item.get("mechanism_profile", {}).get("mechanism_cluster") or "")
            }
        ),
        "dead_doc_count": sum(1 for item in items if item.get("assessment", {}).get("negative_memory_status") == "dead_doc"),
        "kill_count": sum(1 for item in items if item.get("assessment", {}).get("negative_memory_status") == "kill"),
        "hold_count": sum(1 for item in items if item.get("assessment", {}).get("negative_memory_status") == "hold"),
        "failed_full_is_count": sum(
            1
            for item in items
            if item.get("assessment", {}).get("negative_memory_status") in {"failed_full_is", "blocked_full_is"}
        ),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "compress failed families into reusable mechanism and leg-level memory instead of only family-name memory",
        "counts": counts,
        "items": items,
    }


def index_mechanism_failure_memory(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_mechanism_failure_memory_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Mechanism Failure Memory",
        "",
        f"- Objective: {report.get('objective', 'mechanism failure memory')}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Negative families: {counts.get('negative_family_count', 0)}",
        f"- Negative clusters: {counts.get('negative_cluster_count', 0)}",
        "",
        "| family | status | cluster | field tokens | failing gates | pending gates | reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        mechanism_profile = item.get("mechanism_profile", {})
        expression_profile = item.get("expression_profile", {})
        item_counts = item.get("counts", {})
        lines.append(
            "| {family_key} | {status} | {cluster} | {field_tokens} | {failing_gate_count} | {pending_gate_count} | {reasons} |".format(
                family_key=item.get("family_key"),
                status=assessment.get("negative_memory_status"),
                cluster=mechanism_profile.get("mechanism_cluster"),
                field_tokens=", ".join(expression_profile.get("field_tokens", [])[:4]) or "-",
                failing_gate_count=item_counts.get("failing_gate_count", 0),
                pending_gate_count=item_counts.get("pending_gate_count", 0),
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    return "\n".join(lines)

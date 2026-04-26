#!/usr/bin/env python3
"""Economic-distinctness helpers built on mechanism-level failure memory."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from alpha_mining_core import similarity_score
from alpha_success_core import normalize_family_key
from mechanism_failure_memory_core import (
    build_mechanism_failure_memory_report,
    index_mechanism_failure_memory,
)
from research_contract_core import build_research_contract_report, index_research_contract_report


MATERIAL_AXES = {
    "data_category",
    "mechanism",
    "idea_type",
    "holding_frequency",
    "neutralization_target",
}


def _family_key_from_doc(doc: Any) -> str:
    topic = str(getattr(doc, "topic", "") or "")
    if topic:
        return normalize_family_key(topic)
    path = getattr(doc, "path", None)
    if path is not None:
        return normalize_family_key(Path(path).stem)
    return "unknown_family"


def _normalized_contract(contract: dict[str, Any]) -> dict[str, str]:
    return {
        key: normalize_family_key(str(value or ""))
        for key, value in contract.items()
    }


def _field_overlap(left: Sequence[str], right: Sequence[str]) -> float:
    left_set = {normalize_family_key(value) for value in left if str(value).strip()}
    right_set = {normalize_family_key(value) for value in right if str(value).strip()}
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / max(len(left_set | right_set), 1)


def _changed_axes(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    keys = (
        "data_category",
        "mechanism",
        "idea_type",
        "holding_frequency",
        "neutralization_target",
        "delay",
        "universe",
    )
    left_norm = _normalized_contract(left)
    right_norm = _normalized_contract(right)
    return [
        key
        for key in keys
        if left_norm.get(key) and right_norm.get(key) and left_norm.get(key) != right_norm.get(key)
    ]


def _neighbor_score(candidate: dict[str, Any], neighbor: dict[str, Any]) -> float:
    candidate_profile = candidate.get("mechanism_profile", {})
    neighbor_profile = neighbor.get("mechanism_profile", {})
    candidate_expr = candidate.get("expression_profile", {})
    neighbor_expr = neighbor.get("expression_profile", {})

    score = 0.0
    if normalize_family_key(str(candidate_profile.get("data_category", ""))) == normalize_family_key(str(neighbor_profile.get("data_category", ""))):
        score += 3.0
    if normalize_family_key(str(candidate_profile.get("mechanism", ""))) == normalize_family_key(str(neighbor_profile.get("mechanism", ""))):
        score += 3.0
    if normalize_family_key(str(candidate_profile.get("holding_frequency", ""))) == normalize_family_key(str(neighbor_profile.get("holding_frequency", ""))):
        score += 2.0
    if normalize_family_key(str(candidate_profile.get("neutralization_target", ""))) == normalize_family_key(str(neighbor_profile.get("neutralization_target", ""))):
        score += 1.0
    if normalize_family_key(str(candidate_profile.get("idea_type", ""))) == normalize_family_key(str(neighbor_profile.get("idea_type", ""))):
        score += 1.0
    if bool(candidate_expr.get("uses_trade_when")) == bool(neighbor_expr.get("uses_trade_when")):
        score += 0.5
    score += 2.0 * _field_overlap(
        candidate_expr.get("field_tokens", []),
        neighbor_expr.get("field_tokens", []),
    )
    candidate_baseline = str(candidate_expr.get("baseline_expression") or "")
    neighbor_baseline = str(neighbor_expr.get("baseline_expression") or "")
    if candidate_baseline and neighbor_baseline:
        score += 2.0 * similarity_score(candidate_baseline, neighbor_baseline)
    return round(score, 4)


def build_economic_distinctness_report(
    *,
    family_docs: Sequence[Any] = (),
    research_contract_report: dict[str, Any] | None = None,
    mechanism_failure_memory_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if research_contract_report is None:
        research_contract_report = build_research_contract_report(family_docs=family_docs)
    if mechanism_failure_memory_report is None:
        mechanism_failure_memory_report = build_mechanism_failure_memory_report(
            family_docs=family_docs,
            research_contract_report=research_contract_report,
        )

    contract_by_family = index_research_contract_report(research_contract_report)
    memory_by_family = index_mechanism_failure_memory(mechanism_failure_memory_report)
    all_family_keys = sorted(set(contract_by_family) | set(memory_by_family) | {_family_key_from_doc(doc) for doc in family_docs})

    negative_neighbors = [
        item
        for item in mechanism_failure_memory_report.get("items", [])
        if int(item.get("assessment", {}).get("negative_memory_rank", 0) or 0) > 0
    ]

    items: list[dict[str, Any]] = []
    for family_key in all_family_keys:
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
        memory_entry = memory_by_family.get(
            family_key,
            {
                "mechanism_profile": {},
                "expression_profile": {
                    "field_tokens": [],
                    "uses_trade_when": False,
                    "baseline_expression": None,
                },
                "assessment": {
                    "negative_memory_status": "none",
                    "negative_memory_rank": 0,
                    "reasons": ["mechanism-failure-memory record is missing for this family"],
                },
            },
        )
        candidate_contract = dict(contract_entry.get("contract", {}))
        candidate_profile = memory_entry.get("mechanism_profile", {})
        candidate_expr = memory_entry.get("expression_profile", {})

        if not candidate_profile or not candidate_contract:
            items.append(
                {
                    "family_key": family_key,
                    "nearest_negative_family": None,
                    "nearest_negative_status": None,
                    "neighbor_score": 0.0,
                    "changed_axes": [],
                    "field_overlap_pct": 0.0,
                    "expression_similarity": 0.0,
                    "assessment": {
                        "gate_status": "block",
                        "reasons": ["economic distinctness cannot be evaluated without a contract and mechanism profile"],
                    },
                }
            )
            continue

        ranked_neighbors: list[tuple[float, dict[str, Any]]] = []
        for neighbor in negative_neighbors:
            if str(neighbor.get("family_key") or "") == family_key:
                continue
            ranked_neighbors.append((_neighbor_score(memory_entry, neighbor), neighbor))
        ranked_neighbors.sort(key=lambda item: item[0], reverse=True)
        nearest_neighbor = ranked_neighbors[0][1] if ranked_neighbors else None
        neighbor_score = float(ranked_neighbors[0][0]) if ranked_neighbors else 0.0

        changed_axes: list[str] = []
        field_overlap_pct = 0.0
        expression_similarity = 0.0
        reasons: list[str] = []
        gate_status = "pass"

        if nearest_neighbor is None or neighbor_score < 6.0:
            reasons.append("no nearby negative mechanism neighbor requires an economic-difference test yet")
        else:
            neighbor_contract = contract_by_family.get(str(nearest_neighbor.get("family_key") or ""), {}).get("contract", {})
            neighbor_expr = nearest_neighbor.get("expression_profile", {})
            changed_axes = _changed_axes(candidate_contract, dict(neighbor_contract or {}))
            field_overlap_pct = round(
                100.0
                * _field_overlap(
                    candidate_expr.get("field_tokens", []),
                    neighbor_expr.get("field_tokens", []),
                ),
                2,
            )
            candidate_baseline = str(candidate_expr.get("baseline_expression") or "")
            neighbor_baseline = str(neighbor_expr.get("baseline_expression") or "")
            if candidate_baseline and neighbor_baseline:
                expression_similarity = round(100.0 * similarity_score(candidate_baseline, neighbor_baseline), 2)

            uses_trade_when_changed = bool(candidate_expr.get("uses_trade_when")) != bool(neighbor_expr.get("uses_trade_when"))
            has_material_difference = bool(set(changed_axes) & MATERIAL_AXES) or field_overlap_pct < 60.0 or uses_trade_when_changed

            if not has_material_difference:
                gate_status = "hold"
                reasons.append(
                    "family remains too close to a negative mechanism neighbor and does not show a material axis change"
                )
                if expression_similarity >= 82.0 or field_overlap_pct >= 65.0:
                    reasons.append("visible change still looks like a parameter or smoothing retune rather than a new economic leg")
            else:
                reasons.append("family keeps enough economic distance from the nearest negative mechanism neighbor")

        items.append(
            {
                "family_key": family_key,
                "nearest_negative_family": str(nearest_neighbor.get("family_key") or "") if nearest_neighbor else None,
                "nearest_negative_status": (
                    nearest_neighbor.get("assessment", {}).get("negative_memory_status")
                    if nearest_neighbor
                    else None
                ),
                "neighbor_score": round(neighbor_score, 4),
                "changed_axes": changed_axes,
                "field_overlap_pct": field_overlap_pct,
                "expression_similarity": expression_similarity,
                "assessment": {
                    "gate_status": gate_status,
                    "reasons": reasons,
                },
            }
        )

    counts = {
        "family_count": len(items),
        "pass_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "pass"),
        "hold_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "hold"),
        "block_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "block"),
        "compared_family_count": sum(1 for item in items if item.get("nearest_negative_family")),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "block families that only revive failed mechanisms through parameter-only retuning",
        "counts": counts,
        "items": items,
    }


def index_economic_distinctness(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_economic_distinctness_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Economic Distinctness",
        "",
        f"- Objective: {report.get('objective', 'economic distinctness')}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Pass: {counts.get('pass_count', 0)}",
        f"- Hold: {counts.get('hold_count', 0)}",
        f"- Block: {counts.get('block_count', 0)}",
        f"- Compared families: {counts.get('compared_family_count', 0)}",
        "",
        "| family | gate | nearest negative | changed axes | field overlap | expr sim | reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        lines.append(
            "| {family_key} | {gate_status} | {nearest_negative_family} | {changed_axes} | {field_overlap_pct}% | {expression_similarity}% | {reasons} |".format(
                family_key=item.get("family_key"),
                gate_status=assessment.get("gate_status"),
                nearest_negative_family=item.get("nearest_negative_family") or "-",
                changed_axes=", ".join(item.get("changed_axes", [])) or "-",
                field_overlap_pct=item.get("field_overlap_pct", 0.0),
                expression_similarity=item.get("expression_similarity", 0.0),
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    return "\n".join(lines)

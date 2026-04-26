#!/usr/bin/env python3
"""Shared validation-provenance helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from alpha_success_core import build_family_registry_summary, normalize_family_key


PROVENANCE_LEVEL_RANK = {
    "front_gate_only": 0,
    "local_support": 1,
    "metrics_only": 2,
    "partial_tests": 3,
    "partial_gate_checks": 4,
    "full_submission_gates": 5,
    "submit_ready": 6,
}


def _normalize_count_map(
    raw: Mapping[str, Any] | Sequence[tuple[str, Any]] | None,
) -> dict[str, int]:
    if raw is None:
        return {}
    items = raw.items() if isinstance(raw, Mapping) else raw
    normalized: dict[str, int] = {}
    for key, value in items:
        family_key = normalize_family_key(str(key))
        try:
            normalized[family_key] = int(value)
        except (TypeError, ValueError):
            normalized[family_key] = 0
    return normalized


def _family_key_from_doc(doc: Any) -> str:
    topic = str(getattr(doc, "topic", "") or "")
    if topic:
        return normalize_family_key(topic)
    path = getattr(doc, "path", None)
    if path is not None:
        return normalize_family_key(Path(path).stem)
    return "unknown_family"


def _outcome_rank(record: dict[str, Any]) -> tuple[int, int, int]:
    evidence_level = str(record.get("evidence_level") or "")
    return (
        PROVENANCE_LEVEL_RANK.get(evidence_level, 0),
        1 if record.get("submit_ready") else 0,
        -len(record.get("failing_gates", [])),
    )


def build_validation_provenance_report(
    *,
    family_docs: Sequence[Any] = (),
    outcome_memory: Sequence[dict[str, Any]] = (),
    family_registry: Sequence[dict[str, Any]] = (),
    local_scored_counts: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    local_queue_counts: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    if not family_registry and family_docs:
        family_registry = build_family_registry_summary(
            [getattr(doc, "path", doc) for doc in family_docs],
            outcome_memory,
        )

    registry_by_family = {
        str(item.get("family_key") or ""): dict(item)
        for item in family_registry
        if str(item.get("family_key") or "")
    }
    docs_by_family: dict[str, list[str]] = {}
    for doc in family_docs:
        family_key = _family_key_from_doc(doc)
        path = getattr(doc, "path", None)
        if path is not None:
            docs_by_family.setdefault(family_key, []).append(str(path))

    outcomes_by_family: dict[str, list[dict[str, Any]]] = {}
    for record in outcome_memory:
        family_key = normalize_family_key(str(record.get("family_key") or ""))
        outcomes_by_family.setdefault(family_key, []).append(dict(record))

    local_scored_by_family = _normalize_count_map(local_scored_counts)
    local_queue_by_family = _normalize_count_map(local_queue_counts)

    all_family_keys = sorted(
        set(registry_by_family)
        | set(docs_by_family)
        | set(outcomes_by_family)
        | set(local_scored_by_family)
        | set(local_queue_by_family)
    )

    items: list[dict[str, Any]] = []
    for family_key in all_family_keys:
        registry_entry = registry_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "topics": [family_key],
                "doc_paths": docs_by_family.get(family_key, []),
                "state": "explore",
                "reason": "no family-registry entry was found",
            },
        )
        family_outcomes = sorted(outcomes_by_family.get(family_key, []), key=_outcome_rank, reverse=True)
        outcome_level_counts = {level: 0 for level in ("metrics_only", "partial_tests", "partial_gate_checks", "full_submission_gates")}
        capture_mode_histogram: dict[str, int] = {}
        submit_ready_count = 0
        for record in family_outcomes:
            level = str(record.get("evidence_level") or "")
            if level in outcome_level_counts:
                outcome_level_counts[level] += 1
            if record.get("submit_ready"):
                submit_ready_count += 1
            capture_mode = str(record.get("capture_mode") or "")
            if capture_mode:
                capture_mode_histogram[capture_mode] = capture_mode_histogram.get(capture_mode, 0) + 1

        local_scored_count = int(local_scored_by_family.get(family_key, 0) or 0)
        local_queue_count = int(local_queue_by_family.get(family_key, 0) or 0)

        if submit_ready_count > 0:
            strongest_level = "submit_ready"
        elif outcome_level_counts["full_submission_gates"] > 0:
            strongest_level = "full_submission_gates"
        elif outcome_level_counts["partial_gate_checks"] > 0:
            strongest_level = "partial_gate_checks"
        elif outcome_level_counts["partial_tests"] > 0:
            strongest_level = "partial_tests"
        elif outcome_level_counts["metrics_only"] > 0:
            strongest_level = "metrics_only"
        elif local_queue_count > 0 or local_scored_count > 0:
            strongest_level = "local_support"
        else:
            strongest_level = "front_gate_only"

        registry_state = str(registry_entry.get("state") or "explore")
        if strongest_level in {"metrics_only", "partial_tests", "partial_gate_checks"}:
            gate_status = "hold"
            reasons = ["family only has non-binding shown or partial official evidence"]
        elif strongest_level == "local_support":
            gate_status = "pass"
            reasons = ["family only has local validation evidence, so any conclusion remains diagnostic only"]
        elif strongest_level == "front_gate_only":
            gate_status = "pass"
            reasons = ["family has no local or official validation evidence yet"]
        elif strongest_level == "submit_ready":
            gate_status = "pass"
            reasons = ["family has submit-ready validation provenance"]
        else:
            gate_status = "pass"
            reasons = ["family has binding full submission-gate provenance"]

        if registry_state in {"branch", "exploit"} and strongest_level not in {"full_submission_gates", "submit_ready"}:
            reasons.append(
                f"raw registry state `{registry_state}` outruns the strongest binding provenance level `{strongest_level}`"
            )

        strongest_outcome = family_outcomes[0] if family_outcomes else None
        items.append(
            {
                "family_key": family_key,
                "topics": list(registry_entry.get("topics", [])),
                "source_family_doc_paths": list(
                    dict.fromkeys([*docs_by_family.get(family_key, []), *list(registry_entry.get("doc_paths", []))])
                ),
                "counts": {
                    "official_outcome_count": len(family_outcomes),
                    "local_scored_count": local_scored_count,
                    "local_queue_count": local_queue_count,
                    "metrics_only_count": outcome_level_counts["metrics_only"],
                    "partial_tests_count": outcome_level_counts["partial_tests"],
                    "partial_gate_checks_count": outcome_level_counts["partial_gate_checks"],
                    "full_submission_gates_count": outcome_level_counts["full_submission_gates"],
                    "submit_ready_count": submit_ready_count,
                },
                "capture_mode_histogram": capture_mode_histogram,
                "strongest_outcome": (
                    {
                        "capture_id": strongest_outcome.get("capture_id"),
                        "capture_mode": strongest_outcome.get("capture_mode"),
                        "expression": strongest_outcome.get("expression"),
                        "evidence_level": "submit_ready"
                        if strongest_outcome.get("submit_ready")
                        else strongest_outcome.get("evidence_level"),
                    }
                    if strongest_outcome
                    else None
                ),
                "assessment": {
                    "gate_status": gate_status,
                    "strongest_level": strongest_level,
                    "binding_status": "binding"
                    if strongest_level in {"full_submission_gates", "submit_ready"}
                    else "diagnostic",
                    "registry_state": registry_state,
                    "reasons": reasons,
                },
            }
        )

    counts = {
        "family_count": len(items),
        "pass_count": sum(1 for item in items if item["assessment"]["gate_status"] == "pass"),
        "hold_count": sum(1 for item in items if item["assessment"]["gate_status"] == "hold"),
        "binding_family_count": sum(
            1
            for item in items
            if item["assessment"].get("binding_status") == "binding"
        ),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "label the strongest validation provenance so local or shown evidence is never mistaken for binding full-IS proof",
        "counts": counts,
        "items": items,
    }


def index_validation_provenance(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_validation_provenance_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Validation Provenance",
        "",
        f"- Objective: {report.get('objective', 'validation provenance')}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Pass: {counts.get('pass_count', 0)}",
        f"- Hold: {counts.get('hold_count', 0)}",
        f"- Binding families: {counts.get('binding_family_count', 0)}",
        "",
        "| family | strongest level | binding | gate | official outcomes | local support | reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        item_counts = item.get("counts", {})
        lines.append(
            "| {family_key} | {strongest_level} | {binding_status} | {gate_status} | {official_outcome_count} | {local_support} | {reasons} |".format(
                family_key=item.get("family_key"),
                strongest_level=assessment.get("strongest_level"),
                binding_status=assessment.get("binding_status"),
                gate_status=assessment.get("gate_status"),
                official_outcome_count=item_counts.get("official_outcome_count"),
                local_support=int(item_counts.get("local_scored_count", 0) or 0)
                + int(item_counts.get("local_queue_count", 0) or 0),
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    return "\n".join(lines)

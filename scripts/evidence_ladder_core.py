#!/usr/bin/env python3
"""Evidence-ladder parsing and promotion-governance helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from alpha_success_core import build_family_registry_summary, normalize_family_key


PROMOTABLE_STATE_RANK = {"explore": 0, "branch": 1, "exploit": 2}
EVIDENCE_LEVEL_RANK = {
    "E0_front_gate_only": 0,
    "E1_local_support": 1,
    "E2_partial_official": 2,
    "E3_full_is": 3,
    "E4_submit_ready": 4,
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


def _cap_state_by_ceiling(state: str, ceiling: str) -> str:
    normalized_state = str(state or "explore")
    normalized_ceiling = str(ceiling or "explore")
    if normalized_state in {"hold", "kill"}:
        return normalized_state
    state_rank = PROMOTABLE_STATE_RANK.get(normalized_state, 0)
    ceiling_rank = PROMOTABLE_STATE_RANK.get(normalized_ceiling, 0)
    if state_rank > ceiling_rank:
        return normalized_ceiling
    return normalized_state


def _determine_evidence_level(
    *,
    submit_ready_count: int,
    full_gate_outcome_count: int,
    official_outcome_count: int,
    candidate_outcome_count: int,
    strong_candidate_evidence_count: int,
    local_scored_count: int,
    local_queue_count: int,
) -> tuple[str, str]:
    if submit_ready_count > 0:
        return "E4_submit_ready", "submit_ready"
    if full_gate_outcome_count > 0:
        return "E3_full_is", "full_submission_gates"
    if (
        official_outcome_count > 0
        or candidate_outcome_count > 0
        or strong_candidate_evidence_count > 0
    ):
        return "E2_partial_official", "partial_official_or_candidate"
    if local_queue_count > 0 or local_scored_count > 0:
        return "E1_local_support", "local_support"
    return "E0_front_gate_only", "front_gate_only"


def _promotion_ceiling_for_level(level: str) -> str:
    if level == "E4_submit_ready":
        return "exploit"
    if level == "E3_full_is":
        return "branch"
    return "explore"


def _branch_budget_for_level(
    *,
    evidence_level: str,
    full_gate_outcome_count: int,
    failing_gate_count: int,
    pending_gate_count: int,
) -> int:
    if evidence_level == "E4_submit_ready":
        return 0
    if evidence_level == "E3_full_is":
        if (failing_gate_count > 0 or pending_gate_count > 0) and full_gate_outcome_count <= 1:
            return 1
        return 0
    if evidence_level in {"E1_local_support", "E2_partial_official"}:
        return 1
    return 0


def _official_budget_cap(
    *,
    evidence_level: str,
    branch_budget_remaining: int,
) -> int:
    if evidence_level == "E3_full_is":
        return 1 + max(branch_budget_remaining, 0)
    return 1


def build_evidence_ladder_report(
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
        outcomes_by_family.setdefault(family_key, []).append(record)

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
                "state": "explore",
                "reason": "no family-registry entry was found",
                "topics": [family_key],
                "doc_paths": docs_by_family.get(family_key, []),
                "official_outcome_count": 0,
                "candidate_outcome_count": 0,
                "full_gate_outcome_count": 0,
                "submit_ready_count": 0,
                "strong_candidate_evidence_count": 0,
                "failing_gate_histogram": {},
                "pending_gate_histogram": {},
            },
        )
        family_outcomes = outcomes_by_family.get(family_key, [])
        official_outcome_count = int(registry_entry.get("official_outcome_count", 0) or 0)
        candidate_outcome_count = int(registry_entry.get("candidate_outcome_count", 0) or 0)
        full_gate_outcome_count = int(registry_entry.get("full_gate_outcome_count", 0) or 0)
        submit_ready_count = int(registry_entry.get("submit_ready_count", 0) or 0)
        strong_candidate_evidence_count = int(registry_entry.get("strong_candidate_evidence_count", 0) or 0)
        failing_gate_count = sum(
            int(value or 0)
            for value in (registry_entry.get("failing_gate_histogram") or {}).values()
        )
        pending_gate_count = sum(
            int(value or 0)
            for value in (registry_entry.get("pending_gate_histogram") or {}).values()
        )
        local_scored_count = int(local_scored_by_family.get(family_key, 0) or 0)
        local_queue_count = int(local_queue_by_family.get(family_key, 0) or 0)

        evidence_level, evidence_source = _determine_evidence_level(
            submit_ready_count=submit_ready_count,
            full_gate_outcome_count=full_gate_outcome_count,
            official_outcome_count=official_outcome_count,
            candidate_outcome_count=candidate_outcome_count,
            strong_candidate_evidence_count=strong_candidate_evidence_count,
            local_scored_count=local_scored_count,
            local_queue_count=local_queue_count,
        )
        promotion_ceiling = _promotion_ceiling_for_level(evidence_level)
        effective_state = _cap_state_by_ceiling(
            str(registry_entry.get("state") or "explore"),
            promotion_ceiling,
        )
        branch_budget_remaining = _branch_budget_for_level(
            evidence_level=evidence_level,
            full_gate_outcome_count=full_gate_outcome_count,
            failing_gate_count=failing_gate_count,
            pending_gate_count=pending_gate_count,
        )
        official_budget_cap = _official_budget_cap(
            evidence_level=evidence_level,
            branch_budget_remaining=branch_budget_remaining,
        )

        reasons: list[str] = []
        if evidence_level == "E4_submit_ready":
            reasons.append("family already has submit-ready official evidence")
        elif evidence_level == "E3_full_is":
            reasons.append("family has binding full-IS gate coverage")
            if failing_gate_count > 0 or pending_gate_count > 0:
                reasons.append("branching is limited to one structural rescue until full-IS blockers change")
        elif evidence_level == "E2_partial_official":
            reasons.append("family only has partial official or candidate evidence")
            reasons.append("partial evidence can inform diagnostics, not promotion above explore")
        elif evidence_level == "E1_local_support":
            reasons.append("family only has local scoring or queue support")
            reasons.append("local evidence can justify one official probe, not branch promotion")
        else:
            reasons.append("family only has front-gate readiness and contract evidence")
            reasons.append("no promotion is allowed before local or official evidence appears")
        if effective_state != str(registry_entry.get("state") or "explore"):
            reasons.append(
                f"registry state `{registry_entry.get('state')}` is capped to `{effective_state}` by the evidence ladder"
            )

        items.append(
            {
                "family_key": family_key,
                "topics": list(registry_entry.get("topics", [])),
                "source_family_doc_paths": list(
                    dict.fromkeys([*docs_by_family.get(family_key, []), *list(registry_entry.get("doc_paths", []))])
                ),
                "source_capture_paths": list(registry_entry.get("capture_paths", [])),
                "counts": {
                    "official_outcome_count": official_outcome_count,
                    "candidate_outcome_count": candidate_outcome_count,
                    "full_gate_outcome_count": full_gate_outcome_count,
                    "submit_ready_count": submit_ready_count,
                    "strong_candidate_evidence_count": strong_candidate_evidence_count,
                    "local_scored_count": local_scored_count,
                    "local_queue_count": local_queue_count,
                    "failing_gate_count": failing_gate_count,
                    "pending_gate_count": pending_gate_count,
                },
                "assessment": {
                    "evidence_level": evidence_level,
                    "evidence_rank": EVIDENCE_LEVEL_RANK[evidence_level],
                    "evidence_source": evidence_source,
                    "promotion_ceiling": promotion_ceiling,
                    "registry_state": str(registry_entry.get("state") or "explore"),
                    "effective_state": effective_state,
                    "branch_budget_remaining": branch_budget_remaining,
                    "official_budget_cap": official_budget_cap,
                    "reasons": reasons,
                },
                "best_outcome": registry_entry.get("best_outcome"),
                "outcomes": [
                    {
                        "capture_id": item.get("capture_id"),
                        "capture_mode": item.get("capture_mode"),
                        "evidence_level": item.get("evidence_level"),
                        "has_full_gate_coverage": item.get("has_full_gate_coverage"),
                        "submit_ready": item.get("submit_ready"),
                        "failing_gates": list(item.get("failing_gates", [])),
                        "pending_gates": list(item.get("pending_gates", [])),
                    }
                    for item in family_outcomes[:10]
                ],
            }
        )

    counts = {
        "family_count": len(items),
        "E0_front_gate_only": sum(1 for item in items if item["assessment"]["evidence_level"] == "E0_front_gate_only"),
        "E1_local_support": sum(1 for item in items if item["assessment"]["evidence_level"] == "E1_local_support"),
        "E2_partial_official": sum(1 for item in items if item["assessment"]["evidence_level"] == "E2_partial_official"),
        "E3_full_is": sum(1 for item in items if item["assessment"]["evidence_level"] == "E3_full_is"),
        "E4_submit_ready": sum(1 for item in items if item["assessment"]["evidence_level"] == "E4_submit_ready"),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "cap family promotion and branch expansion by evidence quality instead of weak diagnostics",
        "counts": counts,
        "items": items,
    }


def index_evidence_ladder(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_evidence_ladder_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Evidence Ladder",
        "",
        f"- Objective: {report.get('objective', 'evidence ladder')}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- E0 front gate only: {counts.get('E0_front_gate_only', 0)}",
        f"- E1 local support: {counts.get('E1_local_support', 0)}",
        f"- E2 partial official: {counts.get('E2_partial_official', 0)}",
        f"- E3 full IS: {counts.get('E3_full_is', 0)}",
        f"- E4 submit ready: {counts.get('E4_submit_ready', 0)}",
        "",
        "| family | level | source | ceiling | effective state | branch budget | official cap | reasons |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        lines.append(
            "| {family_key} | {evidence_level} | {evidence_source} | {promotion_ceiling} | {effective_state} | {branch_budget_remaining} | {official_budget_cap} | {reasons} |".format(
                family_key=item.get("family_key"),
                evidence_level=assessment.get("evidence_level"),
                evidence_source=assessment.get("evidence_source"),
                promotion_ceiling=assessment.get("promotion_ceiling"),
                effective_state=assessment.get("effective_state"),
                branch_budget_remaining=assessment.get("branch_budget_remaining"),
                official_budget_cap=assessment.get("official_budget_cap"),
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    lines.append("## Reasons")
    lines.append("")
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        lines.append(
            f"- `{item.get('family_key')}` -> `{assessment.get('evidence_level')}` / `{assessment.get('effective_state')}`"
        )
        for reason in assessment.get("reasons", []):
            lines.append(f"  - {reason}")
    lines.append("")
    return "\n".join(lines)

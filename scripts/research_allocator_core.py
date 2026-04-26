#!/usr/bin/env python3
"""Shared research-allocation helpers for family-level scheduling."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence


DEFAULT_RESEARCH_ALLOCATOR = {
    "max_per_cluster": 1,
    "max_per_data_category": 2,
    "max_per_holding_frequency": 2,
    "max_per_idea_type": 1,
    "allow_backfill": True,
    "max_backfill_per_cluster": 1,
}


def _allocator_policy(policy: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = {}
    if isinstance(policy, dict):
        candidate = policy.get("research_allocator")
        if isinstance(candidate, dict):
            raw = candidate

    merged = dict(DEFAULT_RESEARCH_ALLOCATOR)
    for key, default in DEFAULT_RESEARCH_ALLOCATOR.items():
        value = raw.get(key)
        if isinstance(default, bool):
            if isinstance(value, bool):
                merged[key] = value
        else:
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                merged[key] = parsed
    return merged


def _research_contract_field(row: dict[str, Any], field_name: str) -> str:
    contract = row.get("research_contract_fields")
    if isinstance(contract, dict):
        value = contract.get(field_name)
        if value not in (None, ""):
            return str(value)
    value = row.get(field_name)
    return str(value or "")


def _cluster_key(row: dict[str, Any]) -> str:
    data_category = _research_contract_field(row, "data_category") or "unknown_data"
    mechanism = _research_contract_field(row, "mechanism") or "unknown_mechanism"
    holding_frequency = _research_contract_field(row, "holding_frequency") or "unknown_holding"
    return "|".join((data_category, mechanism, holding_frequency))


def _allocator_reason(row: dict[str, Any]) -> str | None:
    if row.get("hard_excluded"):
        return "hard_excluded"
    if str(row.get("field_readiness_gate_status") or "") != "pass":
        return "front_gate_readiness"
    if str(row.get("account_capability_gate_status") or "") != "pass":
        return "front_gate_capability"
    if str(row.get("research_contract_gate_status") or "") != "pass":
        return "front_gate_contract"
    if str(row.get("complexity_budget_gate_status") or "") != "pass":
        return "front_gate_complexity"
    if not bool(row.get("allocator_state_allowed", True)):
        return "state_not_allowed"
    return None


def allocate_family_records(
    *,
    records: Sequence[dict[str, Any]],
    family_limit: int,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    allocator = _allocator_policy(policy)
    prepared: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        enriched = dict(record)
        enriched["allocator_rank"] = index
        enriched["allocator_cluster_key"] = _cluster_key(enriched)
        enriched["allocator_data_category"] = _research_contract_field(enriched, "data_category") or "unknown_data"
        enriched["allocator_holding_frequency"] = _research_contract_field(enriched, "holding_frequency") or "unknown_holding"
        enriched["allocator_idea_type"] = _research_contract_field(enriched, "idea_type") or "unknown_idea"
        reason = _allocator_reason(enriched)
        enriched["allocator_ineligible_reason"] = reason
        prepared.append(enriched)

    selected_primary: list[dict[str, Any]] = []
    selected_backfill: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []

    cluster_counts: dict[str, int] = {}
    data_category_counts: dict[str, int] = {}
    holding_frequency_counts: dict[str, int] = {}
    idea_type_counts: dict[str, int] = {}
    backfill_cluster_counts: dict[str, int] = {}

    for item in prepared:
        if item.get("allocator_ineligible_reason"):
            item["research_allocator_status"] = "ineligible"
            item["research_allocator_reason"] = str(item.get("allocator_ineligible_reason"))
            deferred.append(item)
            continue

        cluster_key = str(item.get("allocator_cluster_key") or "")
        data_category = str(item.get("allocator_data_category") or "")
        holding_frequency = str(item.get("allocator_holding_frequency") or "")
        idea_type = str(item.get("allocator_idea_type") or "")

        if cluster_counts.get(cluster_key, 0) >= int(allocator["max_per_cluster"]):
            item["research_allocator_status"] = "deferred"
            item["research_allocator_reason"] = "cluster_cap"
            deferred.append(item)
            continue
        if data_category_counts.get(data_category, 0) >= int(allocator["max_per_data_category"]):
            item["research_allocator_status"] = "deferred"
            item["research_allocator_reason"] = "data_category_cap"
            deferred.append(item)
            continue
        if holding_frequency_counts.get(holding_frequency, 0) >= int(allocator["max_per_holding_frequency"]):
            item["research_allocator_status"] = "deferred"
            item["research_allocator_reason"] = "holding_frequency_cap"
            deferred.append(item)
            continue
        if idea_type_counts.get(idea_type, 0) >= int(allocator["max_per_idea_type"]):
            item["research_allocator_status"] = "deferred"
            item["research_allocator_reason"] = "idea_type_cap"
            deferred.append(item)
            continue

        item["research_allocator_status"] = "selected_primary"
        item["research_allocator_reason"] = "selected under diversity caps"
        selected_primary.append(item)
        cluster_counts[cluster_key] = cluster_counts.get(cluster_key, 0) + 1
        data_category_counts[data_category] = data_category_counts.get(data_category, 0) + 1
        holding_frequency_counts[holding_frequency] = holding_frequency_counts.get(holding_frequency, 0) + 1
        idea_type_counts[idea_type] = idea_type_counts.get(idea_type, 0) + 1
        if len(selected_primary) >= family_limit:
            break

    if bool(allocator["allow_backfill"]) and len(selected_primary) < family_limit:
        remaining = [
            item
            for item in deferred
            if item.get("research_allocator_status") == "deferred"
        ]
        still_deferred: list[dict[str, Any]] = []
        for item in remaining:
            if len(selected_primary) + len(selected_backfill) >= family_limit:
                still_deferred.append(item)
                continue

            cluster_key = str(item.get("allocator_cluster_key") or "")
            data_category = str(item.get("allocator_data_category") or "")
            holding_frequency = str(item.get("allocator_holding_frequency") or "")
            idea_type = str(item.get("allocator_idea_type") or "")
            if item.get("research_allocator_reason") != "cluster_cap":
                still_deferred.append(item)
                continue
            if backfill_cluster_counts.get(cluster_key, 0) >= int(allocator["max_backfill_per_cluster"]):
                still_deferred.append(item)
                continue
            if data_category_counts.get(data_category, 0) >= int(allocator["max_per_data_category"]):
                still_deferred.append(item)
                continue
            if holding_frequency_counts.get(holding_frequency, 0) >= int(allocator["max_per_holding_frequency"]):
                still_deferred.append(item)
                continue
            if idea_type_counts.get(idea_type, 0) >= int(allocator["max_per_idea_type"]):
                still_deferred.append(item)
                continue

            item["research_allocator_status"] = "selected_backfill"
            item["research_allocator_reason"] = "selected as controlled same-cluster backfill"
            selected_backfill.append(item)
            backfill_cluster_counts[cluster_key] = backfill_cluster_counts.get(cluster_key, 0) + 1
            cluster_counts[cluster_key] = cluster_counts.get(cluster_key, 0) + 1
            data_category_counts[data_category] = data_category_counts.get(data_category, 0) + 1
            holding_frequency_counts[holding_frequency] = holding_frequency_counts.get(holding_frequency, 0) + 1
            idea_type_counts[idea_type] = idea_type_counts.get(idea_type, 0) + 1

        deferred = [
            item
            for item in deferred
            if item.get("research_allocator_status") not in {"selected_backfill"}
        ]
        deferred.extend(still_deferred)

    selected_items = [*selected_primary, *selected_backfill][:family_limit]
    items_by_key = {
        str(item.get("family_key") or ""): item
        for item in selected_items + deferred
        if str(item.get("family_key") or "")
    }
    ordered_items = [
        items_by_key.get(str(item.get("family_key") or ""), dict(item))
        for item in prepared
    ]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "stop daily family selection from collapsing into one mechanism cluster before enough orthogonal coverage exists",
        "settings": {
            "family_limit": family_limit,
            **allocator,
        },
        "counts": {
            "input_count": len(prepared),
            "eligible_count": sum(1 for item in prepared if not item.get("allocator_ineligible_reason")),
            "selected_count": len(selected_items),
            "selected_primary_count": len(selected_primary),
            "selected_backfill_count": len(selected_backfill),
            "deferred_count": len([item for item in ordered_items if str(item.get("research_allocator_status") or "").startswith("deferred")]),
            "ineligible_count": len([item for item in ordered_items if item.get("research_allocator_status") == "ineligible"]),
        },
        "selected_family_keys": [str(item.get("family_key") or "") for item in selected_items if str(item.get("family_key") or "")],
        "selected_items": selected_items,
        "items": ordered_items,
    }

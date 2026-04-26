#!/usr/bin/env python3
"""Account capability awareness helpers for local alpha research.

This gate makes the current capability boundary explicit without pretending
that public tier notes are the same thing as current account entitlement.
It only marks a family as pass when the required region / delay / universe /
category scope is supported by local evidence.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from alpha_success_core import normalize_family_key
from research_contract_core import build_research_contract_report, index_research_contract_report


SESSION_BRIEF_DEFAULT_ROOT = Path("runs/session-briefs")

# Verified public notes from the current official pages inspected in this turn.
# These are advisory notes, not proof of the current account's entitlements.
PUBLIC_TIER_NOTES = (
    {
        "feature": "more_data_fields_and_regions",
        "source": "https://worldquantbrain.com/consultant",
        "note": "The consultant page states that more data fields and more regions are available.",
    },
    {
        "feature": "longer_is_period",
        "source": "https://platform.worldquantbrain.com/consultant-program/",
        "note": "The consultant-program page shows IS testing period expanding from 5 years to 10 years.",
    },
    {
        "feature": "multi_simulation",
        "source": "https://platform.worldquantbrain.com/consultant-program/",
        "note": "The consultant-program page lists multi-simulation as an additional functionality.",
    },
    {
        "feature": "visualization",
        "source": "https://platform.worldquantbrain.com/consultant-program/",
        "note": "The consultant-program page lists visualization as an additional functionality.",
    },
    {
        "feature": "python_api",
        "source": "https://worldquantbrain.com/consultant",
        "note": "The consultant page states that Python API access is an advanced feature.",
    },
    {
        "feature": "superalphas",
        "source": "https://worldquantbrain.com/consultant",
        "note": "The consultant page states that SuperAlphas are an advanced feature.",
    },
    {
        "feature": "research_shapes",
        "source": "https://www.worldquant.com/learn2quant/",
        "note": "Learn2Quant organizes research around data category, idea type, holding frequency, delay, risk management, and advanced ideas.",
    },
)

CATEGORY_ALIASES = {
    "analyst4": "analyst",
    "fundamental_scores": "model",
    "price_volume": "price_volume",
    "pv": "price_volume",
    "option": "options",
    "fnd": "fundamental",
    "fundamental": "fundamental",
    "general": "",
    "model": "model",
    "options": "options",
    "sentiment": "sentiment",
    "analyst": "analyst",
}


def _canonical_category(value: str) -> str:
    normalized = normalize_family_key(str(value or ""))
    return CATEGORY_ALIASES.get(normalized, normalized)


def _combo_key(region: str, delay: str, universe: str) -> str:
    return "|".join((region.upper().strip(), str(delay).strip(), universe.upper().strip()))


def _family_key_from_doc(doc: Any) -> str:
    topic = str(getattr(doc, "topic", "") or "")
    if topic:
        return normalize_family_key(topic)
    path = getattr(doc, "path", None)
    if path is not None:
        return normalize_family_key(Path(path).stem)
    return "unknown_family"


def _load_json_response(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _iter_evidence_paths(session_brief_root: Path) -> Iterable[Path]:
    if not session_brief_root.exists():
        return ()
    return sorted(
        path
        for path in session_brief_root.rglob("*.network-response")
        if path.is_file()
    )


def _collect_scope_evidence(session_brief_root: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    sources: list[dict[str, Any]] = []
    combos: dict[str, dict[str, Any]] = {}
    for path in _iter_evidence_paths(session_brief_root):
        payload = _load_json_response(path)
        if not payload:
            continue
        results = payload.get("results", [])
        if not isinstance(results, list):
            continue
        source_entry = {
            "path": str(path),
            "result_count": len(results),
        }
        sources.append(source_entry)
        for result in results:
            if not isinstance(result, dict):
                continue
            region = str(result.get("region") or "").upper().strip()
            delay = str(result.get("delay") or "").strip()
            universe = str(result.get("universe") or "").upper().strip()
            if not (region and delay and universe):
                continue
            category = _canonical_category(
                str(
                    (result.get("category") or {}).get("id")
                    or (result.get("dataset") or {}).get("id")
                    or ""
                )
            )
            combo = _combo_key(region, delay, universe)
            profile = combos.setdefault(
                combo,
                {
                    "region": region,
                    "delay": delay,
                    "universe": universe,
                    "field_count": 0,
                    "category_counts": Counter(),
                    "dataset_counts": Counter(),
                    "samples": [],
                },
            )
            profile["field_count"] += 1
            profile["category_counts"][category] += 1
            dataset_id = str((result.get("dataset") or {}).get("id") or "").strip()
            if dataset_id:
                profile["dataset_counts"][dataset_id] += 1
            sample = {
                "id": str(result.get("id") or ""),
                "dataset": dataset_id,
                "category": category,
                "coverage": result.get("coverage"),
                "alpha_count": result.get("alphaCount"),
                "user_count": result.get("userCount"),
            }
            if len(profile["samples"]) < 5:
                profile["samples"].append(sample)

    for combo in combos.values():
        combo["category_counts"] = dict(sorted(combo["category_counts"].items(), key=lambda item: (-item[1], item[0])))
        combo["dataset_counts"] = dict(sorted(combo["dataset_counts"].items(), key=lambda item: (-item[1], item[0])))
    return sources, combos


def build_account_capability_report(
    *,
    family_docs: Sequence[Any],
    research_contract_report: dict[str, Any] | None = None,
    session_brief_root: Path = SESSION_BRIEF_DEFAULT_ROOT,
) -> dict[str, Any]:
    if research_contract_report is None:
        research_contract_report = build_research_contract_report(family_docs=family_docs)

    contract_by_family = index_research_contract_report(research_contract_report)
    evidence_sources, combos = _collect_scope_evidence(session_brief_root)
    observed_regions = sorted({entry["region"] for entry in combos.values() if entry.get("region")})
    observed_delays = sorted({str(entry["delay"]) for entry in combos.values() if entry.get("delay")})
    observed_universes = sorted({entry["universe"] for entry in combos.values() if entry.get("universe")})
    observed_categories = sorted(
        {
            category
            for entry in combos.values()
            for category in entry.get("category_counts", {})
            if category
        }
    )

    docs_by_family: dict[str, list[Any]] = {}
    for doc in family_docs:
        docs_by_family.setdefault(_family_key_from_doc(doc), []).append(doc)

    all_family_keys = sorted(set(docs_by_family) | set(contract_by_family))

    items: list[dict[str, Any]] = []
    for family_key in all_family_keys:
        contract_entry = contract_by_family.get(
            family_key,
            {
                "metadata": {},
                "contract": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["research-contract record is missing for this family"],
                },
            },
        )
        contract = dict(contract_entry.get("contract", {}))
        metadata = dict(contract_entry.get("metadata", {}))

        required_region = str(metadata.get("region") or "").upper().strip()
        required_delay = str(metadata.get("delay") or contract.get("delay") or "").strip()
        required_universe = str(contract.get("universe") or metadata.get("universe") or "").upper().strip()
        required_category = _canonical_category(str(contract.get("data_category") or metadata.get("category") or ""))

        block_reasons: list[str] = []
        hold_reasons: list[str] = []

        if not required_region:
            block_reasons.append("required region is missing from the research contract metadata")
        if not required_delay:
            block_reasons.append("required delay is missing from the research contract metadata")
        if not required_universe:
            block_reasons.append("required universe is missing from the research contract metadata")
        if not required_category:
            block_reasons.append("required data category is missing from the research contract")
        if not evidence_sources:
            hold_reasons.append("no local session-brief field evidence is available for capability comparison")

        required_combo = _combo_key(required_region, required_delay, required_universe) if not block_reasons else ""
        matching_combo = combos.get(required_combo) if required_combo else None

        observed_combo_count = len(combos)
        supported_category_names = sorted(observed_categories)
        combo_category_count = 0
        observed_field_count = 0
        if matching_combo:
            observed_field_count = int(matching_combo.get("field_count", 0) or 0)
            combo_category_count = int(matching_combo.get("category_counts", {}).get(required_category, 0) or 0)
            if combo_category_count <= 0:
                hold_reasons.append(
                    "the observed capability snapshot has the right region / delay / universe combo, but not the required data category"
                )
            if observed_field_count <= 0:
                hold_reasons.append("the observed capability snapshot has no fields for the required combo")
        elif required_combo and not block_reasons:
            hold_reasons.append(
                "the current capability snapshot does not observe the required region / delay / universe combo"
            )

        if not block_reasons and not hold_reasons and matching_combo:
            gate_status = "pass"
            reasons = ["required scope is represented in the local capability snapshot"]
        elif block_reasons:
            gate_status = "block"
            reasons = block_reasons
        else:
            gate_status = "hold"
            reasons = hold_reasons or ["capability scope is not yet sufficiently evidenced"]

        items.append(
            {
                "family_key": family_key,
                "required_scope": {
                    "region": required_region,
                    "delay": required_delay,
                    "universe": required_universe,
                    "data_category": required_category,
                },
                "capability_snapshot": {
                    "observed_combo_count": observed_combo_count,
                    "observed_regions": observed_regions,
                    "observed_delays": observed_delays,
                    "observed_universes": observed_universes,
                    "observed_categories": supported_category_names,
                    "required_combo": required_combo or None,
                    "matching_combo": (
                        {
                            "region": matching_combo.get("region"),
                            "delay": matching_combo.get("delay"),
                            "universe": matching_combo.get("universe"),
                            "field_count": observed_field_count,
                            "category_counts": dict(matching_combo.get("category_counts", {})),
                            "dataset_counts": dict(matching_combo.get("dataset_counts", {})),
                            "samples": list(matching_combo.get("samples", [])),
                        }
                        if matching_combo
                        else None
                    ),
                    "public_tier_notes": list(PUBLIC_TIER_NOTES),
                },
                "assessment": {
                    "gate_status": gate_status,
                    "reasons": reasons,
                    "required_combo_supported": bool(matching_combo and combo_category_count > 0 and not block_reasons),
                    "required_category_supported": bool(combo_category_count > 0),
                },
            }
        )

    counts = {
        "family_count": len(items),
        "pass_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "pass"),
        "hold_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "hold"),
        "block_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "block"),
        "combo_count": len(combos),
        "evidence_source_count": len(evidence_sources),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "make account capability boundaries explicit before local family mining continues",
        "evidence_sources": evidence_sources,
        "profile": {
            "observed_regions": observed_regions,
            "observed_delays": observed_delays,
            "observed_universes": observed_universes,
            "observed_categories": observed_categories,
            "observed_combo_count": len(combos),
            "public_tier_notes": list(PUBLIC_TIER_NOTES),
        },
        "counts": counts,
        "items": items,
    }


def index_account_capability(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_account_capability_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    profile = report.get("profile", {})
    lines = [
        "# Account Capability Profile",
        "",
        f"- Objective: {report.get('objective', 'account capability profile')}",
        f"- Evidence sources: {counts.get('evidence_source_count', 0)}",
        f"- Observed combos: {counts.get('combo_count', 0)}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Pass: {counts.get('pass_count', 0)}",
        f"- Hold: {counts.get('hold_count', 0)}",
        f"- Block: {counts.get('block_count', 0)}",
        "",
        f"- Observed regions: {', '.join(profile.get('observed_regions', []) or ['-'])}",
        f"- Observed delays: {', '.join(profile.get('observed_delays', []) or ['-'])}",
        f"- Observed universes: {', '.join(profile.get('observed_universes', []) or ['-'])}",
        f"- Observed categories: {', '.join(profile.get('observed_categories', []) or ['-'])}",
        "",
        "## Families",
        "",
        "| family | gate | required scope | observed combo | reasons |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        required_scope = item.get("required_scope", {})
        snapshot = item.get("capability_snapshot", {})
        matching_combo = snapshot.get("matching_combo") or {}
        required_combo = snapshot.get("required_combo") or "-"
        observed_combo = "-"
        if matching_combo:
            observed_combo = "/".join(
                [
                    str(matching_combo.get("region") or "-"),
                    str(matching_combo.get("delay") or "-"),
                    str(matching_combo.get("universe") or "-"),
                ]
            )
        lines.append(
            "| {family_key} | {gate_status} | {region}/{delay}/{universe}/{data_category} | {observed_combo} | {reasons} |".format(
                family_key=item.get("family_key"),
                gate_status=item.get("assessment", {}).get("gate_status"),
                region=required_scope.get("region") or "-",
                delay=required_scope.get("delay") or "-",
                universe=required_scope.get("universe") or "-",
                data_category=required_scope.get("data_category") or "-",
                observed_combo=observed_combo if observed_combo != "-" else required_combo,
                reasons="; ".join(item.get("assessment", {}).get("reasons", [])[:2]),
            )
        )
    lines.append("")
    lines.append("## Public Tier Notes")
    lines.append("")
    for note in profile.get("public_tier_notes", [])[:10]:
        lines.append(f"- {note.get('feature')}: {note.get('note')} ({note.get('source')})")
    lines.append("")
    return "\n".join(lines)

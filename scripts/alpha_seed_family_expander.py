#!/usr/bin/env python3
"""Build a seed-family priority manifest for local alpha mining.

The expander stays local and evidence-aware:

- it reads existing family docs plus field-search packs
- it optionally folds in success-state memory when capture inputs are provided
- it emits a conservative shortlist for the daily runner to consume

It does not write candidate-batch JSON or trigger official WorldQuant actions.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from alpha_mining_core import load_family_docs
from alpha_success_core import build_success_rate_state
from account_capability_core import build_account_capability_report, index_account_capability
from complexity_budget_core import build_complexity_budget_report, index_complexity_budget
from economic_distinctness_core import build_economic_distinctness_report, index_economic_distinctness
from factor_risk_overlay_core import build_factor_risk_overlay_report, index_factor_risk_overlay
from validation_provenance_core import (
    build_validation_provenance_report,
    index_validation_provenance,
)
from field_readiness_core import (
    DEFAULT_COVERAGE_FLOOR_PCT,
    FieldSearchPackDoc,
    build_field_readiness_report,
    index_field_readiness,
    load_field_search_packs,
)
from evidence_ladder_core import EVIDENCE_LEVEL_RANK, build_evidence_ladder_report, index_evidence_ladder
from mechanism_failure_memory_core import (
    build_mechanism_failure_memory_report,
    index_mechanism_failure_memory,
)
from research_allocator_core import allocate_family_records
from research_contract_core import (
    build_research_contract_report,
    index_research_contract_report,
)
from validation_design_core import build_validation_design_report, index_validation_design


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACT_ROOT = Path("harness/artifacts/alpha-seed-expander")
DEFAULT_PUBLISH_ROOT = Path("runs/learning-loops")
DEFAULT_ALLOWED_STATES = ("exploit", "branch", "explore")
STATE_PRIORITY = {"exploit": 0, "branch": 1, "explore": 2, "hold": 3, "kill": 4}
PRIMARY_HINT_RE = re.compile(
    r"\b(primary|first item|first branch|best first|best immediate|try .* first|should be tried first|should be the first item)\b",
    re.IGNORECASE,
)
SECONDARY_HINT_RE = re.compile(r"\b(secondary|backup|control|later branch|later)\b", re.IGNORECASE)
DIVERSITY_HINT_RE = re.compile(
    r"\b(lower crowding|less crowded|different family|distinct|diversification|materially different)\b",
    re.IGNORECASE,
)
OFFICIAL_HINT_RE = re.compile(r"\b(official|verified|confirmed in this session|platform check)\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a priority shortlist of seed families.")
    parser.add_argument(
        "--family-dir",
        type=Path,
        default=Path("runs/expression-families"),
        help="Directory containing expression-family markdown docs.",
    )
    parser.add_argument(
        "--field-search-pack-dir",
        type=Path,
        default=Path("runs/field-search-packs"),
        help="Directory containing field-search-pack markdown docs.",
    )
    parser.add_argument(
        "--capture-dir",
        type=Path,
        default=None,
        help="Optional simulation-capture directory used to fold real outcomes into the seed ranking.",
    )
    parser.add_argument(
        "--candidate-batch-dir",
        type=Path,
        default=None,
        help="Optional durable candidate-batch directory used as read-only evidence input.",
    )
    parser.add_argument(
        "--candidate-check-dir",
        type=Path,
        default=None,
        help="Optional candidate-check artifact directory used as read-only evidence input.",
    )
    parser.add_argument(
        "--success-policy",
        type=Path,
        default=Path("harness/alpha-success-policy.json"),
        help="Success-policy JSON used for hard-exclude topic patterns.",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=DEFAULT_ARTIFACT_ROOT,
        help="Parent directory for the generated seed-family manifest bundle.",
    )
    parser.add_argument(
        "--publish-root",
        type=Path,
        default=DEFAULT_PUBLISH_ROOT,
        help="Durable output root used for the emitted manifest copy.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="",
        help="Optional run id override. Defaults to <YYYY-MM-DD>-alpha-seed-expander.",
    )
    parser.add_argument(
        "--shortlist-limit",
        type=int,
        default=8,
        help="Maximum number of non-excluded families to keep in the priority shortlist.",
    )
    parser.add_argument(
        "--allowed-state",
        action="append",
        default=[],
        help="Eligible family states for the shortlist. Can be repeated.",
    )
    parser.add_argument(
        "--coverage-floor-pct",
        type=float,
        default=DEFAULT_COVERAGE_FLOOR_PCT,
        help="Minimum required parseable coverage floor across usable candidate fields.",
    )
    return parser.parse_args()


def default_run_id(args: argparse.Namespace) -> str:
    if args.run_id:
        return args.run_id
    return f"{datetime.now().strftime('%Y-%m-%d')}-alpha-seed-expander"


def _allowed_states(args: argparse.Namespace) -> tuple[str, ...]:
    states = [state.strip() for state in args.allowed_state if state.strip()]
    if states:
        return tuple(dict.fromkeys(states))
    return DEFAULT_ALLOWED_STATES


def _normalize_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    resolved = path if path.is_absolute() else (PROJECT_ROOT / path)
    return resolved.resolve(strict=False)


def _default_optional_input(
    args_path: Path | None,
    default_path: Path,
    *,
    family_dir: Path,
) -> Path | None:
    if args_path is not None:
        return _normalize_path(args_path)
    default_resolved = _normalize_path(default_path)
    family_dir_default = _normalize_path(Path("runs/expression-families"))
    if family_dir == family_dir_default and default_resolved and default_resolved.exists():
        return default_resolved
    return None


def load_success_policy(path: Path) -> dict[str, Any]:
    resolved = _normalize_path(path)
    if resolved is None or not resolved.exists():
        return {}
    data = json.loads(resolved.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _state_rank(state: str) -> int:
    return STATE_PRIORITY.get(state, 99)


def _float_value(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _matches_any_pattern(texts: Iterable[str], patterns: Sequence[re.Pattern[str]]) -> bool:
    haystack = "\n".join(texts)
    return any(pattern.search(haystack) for pattern in patterns)


def _compile_policy_excludes(policy: dict[str, Any]) -> tuple[re.Pattern[str], ...]:
    compiled: list[re.Pattern[str]] = []
    for pattern in policy.get("hard_exclude_topic_patterns", []):
        if isinstance(pattern, str) and pattern.strip():
            compiled.append(re.compile(pattern, re.IGNORECASE))
    return tuple(compiled)


def _pack_score_components(pack: FieldSearchPackDoc) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if pack.candidate_fields:
        component = min(len(pack.candidate_fields) * 2.0, 10.0)
        score += component
        reasons.append(f"field-pack exposes {len(pack.candidate_fields)} candidate fields")
    if pack.baseline_ideas:
        component = min(len(pack.baseline_ideas) * 1.5, 6.0)
        score += component
        reasons.append(f"field-pack provides {len(pack.baseline_ideas)} baseline ideas")
    if pack.next_action_codes:
        component = min(len(pack.next_action_codes), 4)
        score += float(component)
        reasons.append("field-pack already names concrete next-action expressions/fields")

    if PRIMARY_HINT_RE.search(pack.raw_text):
        score += 10.0
        reasons.append("field-pack explicitly marks this lane as the first or primary seed")
    if SECONDARY_HINT_RE.search(pack.raw_text):
        score -= 2.0
        reasons.append("field-pack frames part of the lane as secondary/control only")
    if DIVERSITY_HINT_RE.search(pack.raw_text):
        score += 4.0
        reasons.append("field-pack argues for diversification or material distinctness")
    if OFFICIAL_HINT_RE.search(pack.raw_text):
        score += 4.0
        reasons.append("field-pack contains explicit official/verified language")
    return score, reasons


def _family_score_components(row: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    state = str(row.get("effective_state") or row.get("state") or "")
    state_bonus = {
        "exploit": 40.0,
        "branch": 28.0,
        "explore": 20.0,
        "hold": -20.0,
        "kill": -120.0,
    }.get(state, 0.0)
    if state_bonus:
        score += state_bonus
        reasons.append(f"family state contributes {state_bonus:+.0f} from `{state}`")

    submit_ready_count = int(row.get("submit_ready_count", 0) or 0)
    if submit_ready_count:
        component = min(submit_ready_count * 12.0, 24.0)
        score += component
        reasons.append(f"family has {submit_ready_count} submit-ready outcomes")

    full_gate_count = int(row.get("full_gate_outcome_count", 0) or 0)
    if full_gate_count:
        component = min(full_gate_count * 4.0, 12.0)
        score += component
        reasons.append(f"family has {full_gate_count} full gate records")

    official_count = int(row.get("official_outcome_count", 0) or 0)
    if official_count:
        component = min(official_count * 1.5, 6.0)
        score += component
        reasons.append(f"family has {official_count} official outcomes")

    best_metrics = (row.get("best_outcome") or {}).get("metrics") or {}
    best_fitness = _float_value(best_metrics.get("fitness") or best_metrics.get("is_fitness"), default=0.0)
    best_sharpe = _float_value(best_metrics.get("sharpe") or best_metrics.get("is_sharpe"), default=0.0)
    if best_fitness > 0:
        component = min(best_fitness * 2.0, 6.0)
        score += component
        reasons.append(f"best recorded fitness contributes {component:.2f}")
    elif best_sharpe > 0:
        component = min(best_sharpe, 4.0)
        score += component
        reasons.append(f"best recorded sharpe contributes {component:.2f}")
    return score, reasons


def build_priority_manifest(
    *,
    run_id: str,
    success_state: dict[str, Any],
    field_packs: Sequence[FieldSearchPackDoc],
    field_readiness_report: dict[str, Any],
    account_capability_report: dict[str, Any],
    research_contract_report: dict[str, Any],
    validation_design_report: dict[str, Any],
    factor_risk_overlay_report: dict[str, Any],
    complexity_budget_report: dict[str, Any],
    mechanism_failure_memory_report: dict[str, Any],
    economic_distinctness_report: dict[str, Any],
    validation_provenance_report: dict[str, Any],
    evidence_ladder_report: dict[str, Any],
    success_policy: dict[str, Any],
    allowed_states: Sequence[str],
    shortlist_limit: int,
) -> dict[str, Any]:
    rows_by_family = {
        str(row.get("family_key") or ""): dict(row)
        for row in success_state.get("family_registry_summary", [])
        if str(row.get("family_key") or "")
    }
    packs_by_family: dict[str, list[FieldSearchPackDoc]] = {}
    for pack in field_packs:
        packs_by_family.setdefault(pack.family_key, []).append(pack)

    exclude_patterns = _compile_policy_excludes(success_policy)
    readiness_by_family = index_field_readiness(field_readiness_report)
    capability_by_family = index_account_capability(account_capability_report)
    contract_by_family = index_research_contract_report(research_contract_report)
    validation_design_by_family = index_validation_design(validation_design_report)
    factor_risk_by_family = index_factor_risk_overlay(factor_risk_overlay_report)
    complexity_by_family = index_complexity_budget(complexity_budget_report)
    failure_memory_by_family = index_mechanism_failure_memory(mechanism_failure_memory_report)
    distinctness_by_family = index_economic_distinctness(economic_distinctness_report)
    provenance_by_family = index_validation_provenance(validation_provenance_report)
    evidence_by_family = index_evidence_ladder(evidence_ladder_report)
    all_family_keys = sorted(
        set(rows_by_family)
        | set(packs_by_family)
        | set(readiness_by_family)
        | set(capability_by_family)
        | set(contract_by_family)
        | set(validation_design_by_family)
        | set(factor_risk_by_family)
        | set(complexity_by_family)
        | set(failure_memory_by_family)
        | set(distinctness_by_family)
        | set(provenance_by_family)
        | set(evidence_by_family)
    )
    family_records: list[dict[str, Any]] = []
    for family_key in all_family_keys:
        row = rows_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "state": "explore",
                "reason": "field-search pack exists but no family registry row was found",
                "topics": [family_key],
                "doc_paths": [],
                "capture_paths": [],
                "baseline_expressions": [],
                "decision_lines": [],
                "explicit_state_hints": [],
                "official_outcome_count": 0,
                "candidate_outcome_count": 0,
                "full_gate_outcome_count": 0,
                "submit_ready_count": 0,
                "strong_candidate_evidence_count": 0,
                "failing_gate_histogram": {},
                "pending_gate_histogram": {},
                "best_outcome": None,
            },
        )
        evidence = evidence_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "assessment": {
                    "evidence_level": "E0_front_gate_only",
                    "promotion_ceiling": "explore",
                    "effective_state": str(row.get("state") or "explore"),
                    "branch_budget_remaining": 0,
                    "official_budget_cap": 1,
                    "reasons": ["evidence-ladder record is missing for this family"],
                },
            },
        )
        packs = packs_by_family.get(family_key, [])
        readiness = readiness_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "candidate_fields": [],
                "usable_candidate_fields": [],
                "blocked_candidate_fields": [],
                "coverage_by_field": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["field-readiness record is missing for this family"],
                },
            },
        )
        capability = capability_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "required_scope": {},
                "capability_snapshot": {
                    "observed_combo_count": 0,
                    "observed_regions": [],
                    "observed_delays": [],
                    "observed_universes": [],
                    "observed_categories": [],
                    "required_combo": None,
                    "matching_combo": None,
                    "public_tier_notes": [],
                },
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["account-capability record is missing for this family"],
                },
            },
        )
        contract = contract_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "contract": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["research-contract record is missing for this family"],
                },
            },
        )
        validation_design = validation_design_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "validation_design": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["validation-design record is missing for this family"],
                },
            },
        )
        factor_risk = factor_risk_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "factor_profile": {
                    "expected_risks": [],
                    "hypothesis_risks": [],
                    "overlay_risks": [],
                },
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["factor-risk-overlay record is missing for this family"],
                },
            },
        )
        complexity = complexity_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "counts": {
                    "expression_count": 0,
                    "variant_expression_count": 0,
                },
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["complexity-budget record is missing for this family"],
                },
            },
        )
        failure_memory = failure_memory_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "mechanism_profile": {},
                "expression_profile": {
                    "field_tokens": [],
                    "uses_trade_when": False,
                },
                "assessment": {
                    "negative_memory_status": "none",
                    "negative_memory_rank": 0,
                    "reasons": ["mechanism-failure-memory record is missing for this family"],
                },
            },
        )
        distinctness = distinctness_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "nearest_negative_family": None,
                "changed_axes": [],
                "field_overlap_pct": 0.0,
                "expression_similarity": 0.0,
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["economic-distinctness record is missing for this family"],
                },
            },
        )
        provenance = provenance_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "counts": {
                    "official_outcome_count": 0,
                    "local_scored_count": 0,
                    "local_queue_count": 0,
                },
                "assessment": {
                    "gate_status": "pass",
                    "strongest_level": "front_gate_only",
                    "binding_status": "diagnostic",
                    "reasons": ["validation-provenance record is missing for this family"],
                },
            },
        )
        readiness_assessment = readiness.get("assessment", {})
        capability_assessment = capability.get("assessment", {})
        contract_assessment = contract.get("assessment", {})
        validation_design_assessment = validation_design.get("assessment", {})
        factor_risk_assessment = factor_risk.get("assessment", {})
        complexity_assessment = complexity.get("assessment", {})
        failure_memory_assessment = failure_memory.get("assessment", {})
        distinctness_assessment = distinctness.get("assessment", {})
        provenance_assessment = provenance.get("assessment", {})
        evidence_assessment = evidence.get("assessment", {})
        pack_score = 0.0
        pack_reasons: list[str] = []
        for pack in packs:
            component, reasons = _pack_score_components(pack)
            pack_score += component
            pack_reasons.extend(reasons)

        family_score, family_reasons = _family_score_components(row)
        total_score = family_score + pack_score

        match_texts = [
            family_key,
            *(str(topic) for topic in row.get("topics", [])),
            *(str(path) for path in row.get("doc_paths", [])),
            *(str(pack.path) for pack in packs),
            *(pack.title for pack in packs),
        ]
        hard_excluded = _matches_any_pattern(match_texts, exclude_patterns) if exclude_patterns else False
        if hard_excluded:
            total_score -= 200.0
            pack_reasons.append("hard exclude topic pattern matched this family")

        gate_status = str(readiness_assessment.get("gate_status") or "block")
        if gate_status != "pass":
            total_score -= 60.0
            pack_reasons.append(f"field-readiness gate is `{gate_status}`")
        capability_gate_status = str(capability_assessment.get("gate_status") or "block")
        if capability_gate_status != "pass":
            total_score -= 80.0
            pack_reasons.append(f"account-capability gate is `{capability_gate_status}`")
        contract_gate_status = str(contract_assessment.get("gate_status") or "block")
        if contract_gate_status != "pass":
            total_score -= 80.0
            pack_reasons.append(f"research-contract gate is `{contract_gate_status}`")
        validation_design_gate_status = str(validation_design_assessment.get("gate_status") or "block")
        if validation_design_gate_status != "pass":
            total_score -= 70.0
            pack_reasons.append(f"validation-design gate is `{validation_design_gate_status}`")
        factor_risk_gate_status = str(factor_risk_assessment.get("gate_status") or "block")
        if factor_risk_gate_status != "pass":
            total_score -= 70.0
            pack_reasons.append(f"factor-risk-overlay gate is `{factor_risk_gate_status}`")
        complexity_gate_status = str(complexity_assessment.get("gate_status") or "block")
        if complexity_gate_status != "pass":
            total_score -= 70.0
            pack_reasons.append(f"complexity-budget gate is `{complexity_gate_status}`")
        distinctness_gate_status = str(distinctness_assessment.get("gate_status") or "block")
        if distinctness_gate_status != "pass":
            total_score -= 90.0
            pack_reasons.append(f"economic-distinctness gate is `{distinctness_gate_status}`")
        provenance_gate_status = str(provenance_assessment.get("gate_status") or "pass")
        if provenance_gate_status != "pass":
            total_score -= 6.0
            pack_reasons.append("strongest official-looking evidence is still non-binding")
        evidence_level = str(evidence_assessment.get("evidence_level") or "E0_front_gate_only")
        if evidence_level == "E4_submit_ready":
            total_score += 16.0
            pack_reasons.append("submit-ready evidence supports the current family posture")
        elif evidence_level == "E3_full_is":
            total_score += 8.0
            pack_reasons.append("binding full-IS evidence supports this family")
        elif evidence_level == "E2_partial_official":
            total_score -= 4.0
            pack_reasons.append("only partial official evidence exists for this family")

        candidate_fields = tuple(dict.fromkeys(field for pack in packs for field in pack.candidate_fields))
        baseline_ideas = tuple(dict.fromkeys(expr for pack in packs for expr in pack.baseline_ideas))
        next_action_codes = tuple(dict.fromkeys(code for pack in packs for code in pack.next_action_codes))
        priority_reasons = tuple(
            dict.fromkeys(
                [
                    *family_reasons,
                    *pack_reasons,
                    *list(readiness_assessment.get("reasons", [])),
                    *list(capability_assessment.get("reasons", [])),
                    *list(factor_risk_assessment.get("reasons", [])),
                    *list(validation_design_assessment.get("reasons", [])),
                    *list(distinctness_assessment.get("reasons", [])),
                ]
            )
        )
        family_records.append(
            {
                "family_key": family_key,
                "state": row.get("state") or "explore",
                "effective_state": evidence_assessment.get("effective_state") or row.get("state") or "explore",
                "reason": row.get("reason") or "",
                "priority_score": round(total_score, 4),
                "hard_excluded": hard_excluded,
                "field_readiness_gate_status": gate_status,
                "field_readiness_reasons": list(readiness_assessment.get("reasons", [])),
                "field_readiness_usable_candidate_fields": list(readiness.get("usable_candidate_fields", [])),
                "field_readiness_blocked_candidate_fields": list(readiness.get("blocked_candidate_fields", [])),
                "field_readiness_coverage_status": readiness_assessment.get("coverage_status"),
                "field_readiness_coverage_floor_pct": readiness_assessment.get("coverage_floor_pct"),
                "account_capability_gate_status": capability_gate_status,
                "account_capability_reasons": list(capability_assessment.get("reasons", [])),
                "account_capability_required_scope": dict(capability.get("required_scope", {})),
                "account_capability_observed_combo_count": int(
                    capability.get("capability_snapshot", {}).get("observed_combo_count", 0) or 0
                ),
                "account_capability_observed_regions": list(
                    capability.get("capability_snapshot", {}).get("observed_regions", [])
                ),
                "account_capability_observed_delays": list(
                    capability.get("capability_snapshot", {}).get("observed_delays", [])
                ),
                "account_capability_observed_universes": list(
                    capability.get("capability_snapshot", {}).get("observed_universes", [])
                ),
                "account_capability_observed_categories": list(
                    capability.get("capability_snapshot", {}).get("observed_categories", [])
                ),
                "research_contract_gate_status": contract_gate_status,
                "research_contract_reasons": list(contract_assessment.get("reasons", [])),
                "research_contract_fields": dict(contract.get("contract", {})),
                "validation_design_gate_status": validation_design_gate_status,
                "validation_design_reasons": list(validation_design_assessment.get("reasons", [])),
                "validation_design_fields": dict(validation_design.get("validation_design", {})),
                "factor_risk_overlay_gate_status": factor_risk_gate_status,
                "factor_risk_overlay_reasons": list(factor_risk_assessment.get("reasons", [])),
                "factor_risk_overlay_expected_risks": list(
                    factor_risk.get("factor_profile", {}).get("expected_risks", [])
                ),
                "factor_risk_overlay_hypothesis_risks": list(
                    factor_risk.get("factor_profile", {}).get("hypothesis_risks", [])
                ),
                "factor_risk_overlay_overlay_risks": list(
                    factor_risk.get("factor_profile", {}).get("overlay_risks", [])
                ),
                "complexity_budget_gate_status": complexity_gate_status,
                "complexity_budget_reasons": list(complexity_assessment.get("reasons", [])),
                "complexity_budget_expression_count": int(complexity.get("counts", {}).get("expression_count", 0) or 0),
                "complexity_budget_variant_expression_count": int(
                    complexity.get("counts", {}).get("variant_expression_count", 0) or 0
                ),
                "mechanism_failure_memory_status": failure_memory_assessment.get("negative_memory_status"),
                "mechanism_failure_memory_rank": failure_memory_assessment.get("negative_memory_rank"),
                "mechanism_failure_memory_reasons": list(failure_memory_assessment.get("reasons", [])),
                "mechanism_failure_memory_cluster": failure_memory.get("mechanism_profile", {}).get("mechanism_cluster"),
                "economic_distinctness_gate_status": distinctness_gate_status,
                "economic_distinctness_reasons": list(distinctness_assessment.get("reasons", [])),
                "economic_distinctness_nearest_negative_family": distinctness.get("nearest_negative_family"),
                "economic_distinctness_changed_axes": list(distinctness.get("changed_axes", [])),
                "economic_distinctness_field_overlap_pct": distinctness.get("field_overlap_pct"),
                "economic_distinctness_expression_similarity": distinctness.get("expression_similarity"),
                "validation_provenance_gate_status": provenance_gate_status,
                "validation_provenance_level": provenance_assessment.get("strongest_level"),
                "validation_provenance_binding_status": provenance_assessment.get("binding_status"),
                "validation_provenance_reasons": list(provenance_assessment.get("reasons", [])),
                "evidence_ladder_level": evidence_level,
                "evidence_ladder_source": evidence_assessment.get("evidence_source"),
                "evidence_ladder_promotion_ceiling": evidence_assessment.get("promotion_ceiling"),
                "evidence_ladder_effective_state": evidence_assessment.get("effective_state"),
                "evidence_ladder_branch_budget_remaining": evidence_assessment.get("branch_budget_remaining"),
                "evidence_ladder_official_budget_cap": evidence_assessment.get("official_budget_cap"),
                "evidence_ladder_reasons": list(evidence_assessment.get("reasons", [])),
                "allocator_state_allowed": str(evidence_assessment.get("effective_state") or row.get("state") or "explore") in allowed_states,
                "topics": list(row.get("topics", [])),
                "doc_paths": list(row.get("doc_paths", [])),
                "field_pack_paths": [pack.path.as_posix() for pack in packs],
                "official_outcome_count": int(row.get("official_outcome_count", 0) or 0),
                "full_gate_outcome_count": int(row.get("full_gate_outcome_count", 0) or 0),
                "submit_ready_count": int(row.get("submit_ready_count", 0) or 0),
                "candidate_field_count": len(candidate_fields),
                "candidate_fields": list(candidate_fields),
                "baseline_idea_count": len(baseline_ideas),
                "baseline_ideas": list(baseline_ideas),
                "next_action_code_count": len(next_action_codes),
                "next_action_codes": list(next_action_codes),
                "priority_reasons": list(priority_reasons),
            }
        )

    family_records.sort(
        key=lambda item: (
            1 if item.get("hard_excluded") else 0,
            0 if str(item.get("field_readiness_gate_status") or "") == "pass" else 1,
            0 if str(item.get("account_capability_gate_status") or "") == "pass" else 1,
            0 if str(item.get("research_contract_gate_status") or "") == "pass" else 1,
            0 if str(item.get("validation_design_gate_status") or "") == "pass" else 1,
            0 if str(item.get("factor_risk_overlay_gate_status") or "") == "pass" else 1,
            0 if str(item.get("complexity_budget_gate_status") or "") == "pass" else 1,
            0 if str(item.get("economic_distinctness_gate_status") or "") == "pass" else 1,
            0 if str(item.get("effective_state") or "") in allowed_states else 1,
            -EVIDENCE_LEVEL_RANK.get(str(item.get("evidence_ladder_level") or ""), 0),
            -_float_value(item.get("priority_score"), default=-9999.0),
            _state_rank(str(item.get("effective_state") or "")),
            str(item.get("family_key") or ""),
        )
    )

    allocator_report = allocate_family_records(
        records=family_records,
        family_limit=shortlist_limit,
        policy=success_policy,
    )
    family_records = list(allocator_report.get("items", []))
    shortlist = list(allocator_report.get("selected_items", []))
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "run_id": run_id,
        "objective": "prioritize materially different seed families before daily local mining",
        "settings": {
            "allowed_states": list(allowed_states),
            "shortlist_limit": shortlist_limit,
            "hard_exclude_topic_patterns": [
                pattern
                for pattern in success_policy.get("hard_exclude_topic_patterns", [])
                if isinstance(pattern, str)
            ],
        },
        "priority_family_keys": [item["family_key"] for item in shortlist],
        "shortlist": shortlist,
        "all_families": family_records,
        "field_readiness": {
            "coverage_floor_pct": field_readiness_report.get("coverage_floor_pct"),
            "counts": dict(field_readiness_report.get("counts", {})),
        },
        "account_capability": {
            "counts": dict(account_capability_report.get("counts", {})),
            "profile": dict(account_capability_report.get("profile", {})),
            "top_blocked": [
                item
                for item in account_capability_report.get("items", [])
                if str(item.get("assessment", {}).get("gate_status") or "") != "pass"
            ][:10],
        },
        "research_contract": {
            "counts": dict(research_contract_report.get("counts", {})),
        },
        "validation_design": {
            "counts": dict(validation_design_report.get("counts", {})),
        },
        "factor_risk_overlay": {
            "counts": dict(factor_risk_overlay_report.get("counts", {})),
        },
        "complexity_budget": {
            "counts": dict(complexity_budget_report.get("counts", {})),
        },
        "mechanism_failure_memory": {
            "counts": dict(mechanism_failure_memory_report.get("counts", {})),
        },
        "economic_distinctness": {
            "counts": dict(economic_distinctness_report.get("counts", {})),
        },
        "validation_provenance": {
            "counts": dict(validation_provenance_report.get("counts", {})),
        },
        "evidence_ladder": {
            "counts": dict(evidence_ladder_report.get("counts", {})),
        },
        "research_allocator": {
            "counts": dict(allocator_report.get("counts", {})),
            "selected_family_keys": list(allocator_report.get("selected_family_keys", [])),
        },
        "counts": {
            "family_registry_count": len(success_state.get("family_registry_summary", [])),
            "field_pack_count": len(field_packs),
            "account_capability_count": len(account_capability_report.get("items", [])),
            "account_capability_pass_count": int(account_capability_report.get("counts", {}).get("pass_count", 0)),
            "family_count": len(family_records),
            "shortlist_count": len(shortlist),
        },
    }


def render_manifest_md(manifest: dict[str, Any]) -> str:
    lines = [
        "# Alpha Seed Family Expander",
        "",
        f"- Run id: {manifest['run_id']}",
        f"- Objective: {manifest['objective']}",
        f"- Shortlist count: {manifest.get('counts', {}).get('shortlist_count', 0)}",
        f"- Family count: {manifest.get('counts', {}).get('family_count', 0)}",
        f"- Field-readiness pass count: {manifest.get('field_readiness', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Account-capability pass count: {manifest.get('account_capability', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Research-contract pass count: {manifest.get('research_contract', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Validation-design pass count: {manifest.get('validation_design', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Factor-risk-overlay pass count: {manifest.get('factor_risk_overlay', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Complexity-budget pass count: {manifest.get('complexity_budget', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Economic-distinctness pass count: {manifest.get('economic_distinctness', {}).get('counts', {}).get('pass_count', 0)}",
        f"- Binding provenance families: {manifest.get('validation_provenance', {}).get('counts', {}).get('binding_family_count', 0)}",
        f"- E3/E4 evidence count: {manifest.get('evidence_ladder', {}).get('counts', {}).get('E3_full_is', 0) + manifest.get('evidence_ladder', {}).get('counts', {}).get('E4_submit_ready', 0)}",
        f"- Allocator selected count: {manifest.get('research_allocator', {}).get('counts', {}).get('selected_count', 0)}",
        "",
        "## Priority Family Keys",
        "",
    ]
    priority_keys = manifest.get("priority_family_keys", [])
    if not priority_keys:
        lines.append("- No family survived the current seed-family filters.")
    else:
        for family_key in priority_keys:
            lines.append(f"- {family_key}")

    lines.extend(["", "## Shortlist", ""])
    shortlist = manifest.get("shortlist", [])
    if not shortlist:
        lines.append("- Shortlist is empty.")
    else:
        for item in shortlist:
            lines.append(
                f"- {item['family_key']} [{item['effective_state']}] score={item['priority_score']} "
                f"fields={item['candidate_field_count']} baselines={item['baseline_idea_count']} "
                f"readiness={item['field_readiness_gate_status']} "
                f"capability={item['account_capability_gate_status']} "
                f"contract={item['research_contract_gate_status']} "
                f"validation={item.get('validation_design_gate_status')} "
                f"factor={item.get('factor_risk_overlay_gate_status')} "
                f"complexity={item.get('complexity_budget_gate_status')} "
                f"distinctness={item.get('economic_distinctness_gate_status')} "
                f"provenance={item.get('validation_provenance_level')} "
                f"allocator={item.get('research_allocator_status')} "
                f"evidence={item['evidence_ladder_level']}"
            )
            for reason in item.get("priority_reasons", [])[:4]:
                lines.append(f"  - {reason}")
    lines.extend(["", "## Front Gate Holds", ""])
    held = [
        item
        for item in manifest.get("all_families", [])
        if (
            str(item.get("field_readiness_gate_status") or "") != "pass"
            or str(item.get("account_capability_gate_status") or "") != "pass"
            or str(item.get("research_contract_gate_status") or "") != "pass"
            or str(item.get("validation_design_gate_status") or "") != "pass"
            or str(item.get("factor_risk_overlay_gate_status") or "") != "pass"
            or str(item.get("complexity_budget_gate_status") or "") != "pass"
            or str(item.get("economic_distinctness_gate_status") or "") != "pass"
        )
    ]
    if not held:
        lines.append("- No family is currently blocked by the front gates.")
    else:
        for item in held:
            lines.append(
                f"- {item['family_key']} -> readiness={item['field_readiness_gate_status']} "
                f"capability={item.get('account_capability_gate_status')} "
                f"contract={item['research_contract_gate_status']} "
                f"validation={item.get('validation_design_gate_status')} "
                f"factor={item.get('factor_risk_overlay_gate_status')} "
                f"complexity={item.get('complexity_budget_gate_status')} "
                f"distinctness={item.get('economic_distinctness_gate_status')}"
            )
            for reason in item.get("field_readiness_reasons", [])[:3]:
                lines.append(f"  - {reason}")
            for reason in item.get("account_capability_reasons", [])[:3]:
                lines.append(f"  - {reason}")
            for reason in item.get("research_contract_reasons", [])[:3]:
                lines.append(f"  - {reason}")
            for reason in item.get("validation_design_reasons", [])[:3]:
                lines.append(f"  - {reason}")
            for reason in item.get("factor_risk_overlay_reasons", [])[:3]:
                lines.append(f"  - {reason}")
            for reason in item.get("complexity_budget_reasons", [])[:3]:
                lines.append(f"  - {reason}")
            for reason in item.get("economic_distinctness_reasons", [])[:3]:
                lines.append(f"  - {reason}")
            for reason in item.get("evidence_ladder_reasons", [])[:2]:
                lines.append(f"  - {reason}")
            for reason in item.get("validation_provenance_reasons", [])[:2]:
                lines.append(f"  - {reason}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    run_id = default_run_id(args)
    allowed_states = _allowed_states(args)

    family_dir = _normalize_path(args.family_dir)
    field_pack_dir = _normalize_path(args.field_search_pack_dir)
    if family_dir is None or not family_dir.exists():
        raise SystemExit(f"Family dir not found: {args.family_dir}")
    if field_pack_dir is None or not field_pack_dir.exists():
        raise SystemExit(f"Field-search-pack dir not found: {args.field_search_pack_dir}")

    capture_dir = _default_optional_input(
        args.capture_dir,
        Path("runs/simulation-captures"),
        family_dir=family_dir,
    )
    candidate_batch_dir = _default_optional_input(
        args.candidate_batch_dir,
        Path("runs/candidate-batches"),
        family_dir=family_dir,
    )
    candidate_check_dir = _default_optional_input(
        args.candidate_check_dir,
        Path("harness/artifacts"),
        family_dir=family_dir,
    )

    success_state = build_success_rate_state(
        family_dir=family_dir,
        capture_dir=capture_dir if capture_dir is not None and capture_dir.exists() else [],
        candidate_batch_dir=(candidate_batch_dir if candidate_batch_dir is not None and candidate_batch_dir.exists() else None),
        candidate_check_dir=(candidate_check_dir if candidate_check_dir is not None and candidate_check_dir.exists() else None),
    )
    success_policy = load_success_policy(args.success_policy)
    family_docs = load_family_docs(family_dir, include_dead=True)
    field_packs = load_field_search_packs(field_pack_dir)
    field_readiness_report = build_field_readiness_report(
        field_packs=field_packs,
        family_docs=family_docs,
        coverage_floor_pct=args.coverage_floor_pct,
    )
    research_contract_report = build_research_contract_report(family_docs=family_docs)
    account_capability_report = build_account_capability_report(
        family_docs=family_docs,
        research_contract_report=research_contract_report,
    )
    validation_design_report = build_validation_design_report(family_docs=family_docs)
    factor_risk_overlay_report = build_factor_risk_overlay_report(
        family_docs=family_docs,
        research_contract_report=research_contract_report,
        validation_design_report=validation_design_report,
    )
    complexity_budget_report = build_complexity_budget_report(
        family_docs=family_docs,
        policy=success_policy,
    )
    mechanism_failure_memory_report = build_mechanism_failure_memory_report(
        family_docs=family_docs,
        family_registry=success_state.get("family_registry_summary", []),
        research_contract_report=research_contract_report,
    )
    economic_distinctness_report = build_economic_distinctness_report(
        family_docs=family_docs,
        research_contract_report=research_contract_report,
        mechanism_failure_memory_report=mechanism_failure_memory_report,
    )
    validation_provenance_report = build_validation_provenance_report(
        family_docs=family_docs,
        outcome_memory=success_state.get("combined_outcome_memory", []),
        family_registry=success_state.get("family_registry_summary", []),
    )
    evidence_ladder_report = build_evidence_ladder_report(
        family_registry=success_state.get("family_registry_summary", []),
        outcome_memory=success_state.get("combined_outcome_memory", []),
    )
    manifest = build_priority_manifest(
        run_id=run_id,
        success_state=success_state,
        field_packs=field_packs,
        field_readiness_report=field_readiness_report,
        account_capability_report=account_capability_report,
        research_contract_report=research_contract_report,
        validation_design_report=validation_design_report,
        factor_risk_overlay_report=factor_risk_overlay_report,
        complexity_budget_report=complexity_budget_report,
        mechanism_failure_memory_report=mechanism_failure_memory_report,
        economic_distinctness_report=economic_distinctness_report,
        validation_provenance_report=validation_provenance_report,
        evidence_ladder_report=evidence_ladder_report,
        success_policy=success_policy,
        allowed_states=allowed_states,
        shortlist_limit=args.shortlist_limit,
    )
    manifest_text = render_manifest_md(manifest)

    artifact_root = _normalize_path(args.artifact_root)
    publish_root = _normalize_path(args.publish_root)
    if artifact_root is None or publish_root is None:
        raise SystemExit("Invalid output root.")
    output_root = artifact_root / run_id
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "manifest.json"
    manifest_md_path = output_root / "manifest.md"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_md_path.write_text(manifest_text, encoding="utf-8")

    publish_root.mkdir(parents=True, exist_ok=True)
    published_json = publish_root / f"{run_id}.json"
    published_md = publish_root / f"{run_id}.md"
    published_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    published_md.write_text(manifest_text, encoding="utf-8")

    print(f"Seed-family bundle: {output_root}")
    print(f"Seed-family manifest: {published_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

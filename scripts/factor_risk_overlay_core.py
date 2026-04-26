#!/usr/bin/env python3
"""Heuristic factor-risk overlay helpers."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from alpha_mining_core import parse_function_calls, tokenize_expression
from alpha_success_core import normalize_family_key
from research_contract_core import build_research_contract_report, index_research_contract_report
from validation_design_core import build_validation_design_report, index_validation_design


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

RISK_KEYWORDS = {
    "size": {
        "cap",
        "market_cap",
        "mktcap",
        "mkt_cap",
        "sharesout",
        "size",
        "small_cap",
        "large_cap",
    },
    "liquidity": {
        "adv",
        "adv20",
        "adv60",
        "avg_dollar_volume",
        "dollar_volume",
        "liquidity",
        "turnover",
        "volume",
        "vwap",
    },
    "volatility": {
        "atr",
        "implied_volatility",
        "iv",
        "sigma",
        "std",
        "std_dev",
        "variance",
        "vol",
        "volatility",
    },
    "momentum": {
        "close",
        "high",
        "low",
        "momentum",
        "open",
        "price",
        "return",
        "returns",
        "reversal",
        "trend",
    },
    "value": {
        "assets",
        "book",
        "cashflow",
        "ceq",
        "earnings",
        "equity",
        "income",
        "revenue",
        "sales",
        "value",
    },
    "quality": {
        "margin",
        "operating_income",
        "profit",
        "profitability",
        "quality",
        "roe",
        "roa",
    },
    "leverage": {
        "debt",
        "leverage",
        "liabilities",
        "liability",
    },
    "crowding": {
        "analyst",
        "attention",
        "buzz",
        "consensus",
        "crowding",
        "estimate",
        "news",
        "revision",
        "sentiment",
    },
    "industry": {
        "industry",
        "sector",
        "subindustry",
    },
    "statistical": {
        "orthogonal",
        "pca",
        "residual",
        "statistical",
    },
}

DEFAULT_RISKS_BY_CATEGORY = {
    "fundamental": ("value", "size"),
    "price_volume": ("momentum", "liquidity", "volatility"),
    "analyst": ("crowding", "industry"),
    "sentiment": ("crowding", "momentum"),
    "options": ("volatility", "liquidity"),
    "model": ("value", "momentum"),
}

DEFAULT_RISKS_BY_MECHANISM = {
    "slow_ratio": ("value", "size", "leverage"),
    "cross_sectional_rank": ("industry",),
    "analyst_drift": ("crowding", "industry"),
    "sentiment_rank": ("crowding", "momentum"),
    "event_gate": ("volatility", "liquidity"),
    "volatility_gate": ("volatility", "liquidity"),
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


def _token_risks(tokens: Sequence[str]) -> set[str]:
    matched: set[str] = set()
    lowered_tokens = {token.lower() for token in tokens}
    for risk, keywords in RISK_KEYWORDS.items():
        if lowered_tokens & keywords:
            matched.add(risk)
    return matched


def _mentioned_risks(*texts: str) -> set[str]:
    joined = " ".join(texts).lower()
    matched: set[str] = set()
    for risk, keywords in RISK_KEYWORDS.items():
        if any(keyword in joined for keyword in keywords):
            matched.add(risk)
    return matched


def build_factor_risk_overlay_report(
    *,
    family_docs: Sequence[Any],
    research_contract_report: dict[str, Any] | None = None,
    validation_design_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if research_contract_report is None:
        research_contract_report = build_research_contract_report(family_docs=family_docs)
    if validation_design_report is None:
        validation_design_report = build_validation_design_report(family_docs=family_docs)

    docs_by_family: dict[str, list[Any]] = {}
    for doc in family_docs:
        docs_by_family.setdefault(_family_key_from_doc(doc), []).append(doc)

    contract_by_family = index_research_contract_report(research_contract_report)
    validation_by_family = index_validation_design(validation_design_report)
    all_family_keys = sorted(set(docs_by_family) | set(contract_by_family) | set(validation_by_family))

    items: list[dict[str, Any]] = []
    for family_key in all_family_keys:
        docs = docs_by_family.get(family_key, [])
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
        validation_entry = validation_by_family.get(
            family_key,
            {
                "validation_design": {},
                "assessment": {
                    "gate_status": "block",
                    "reasons": ["validation-design record is missing for this family"],
                },
            },
        )

        contract = dict(contract_entry.get("contract", {}))
        validation_design = dict(validation_entry.get("validation_design", {}))
        expressions = [
            str(expression)
            for doc in docs
            for expression in getattr(doc, "all_expressions", ())
            if str(expression).strip()
        ]
        tokens = _field_tokens(expressions)
        token_risks = _token_risks(tokens)

        data_category = normalize_family_key(str(contract.get("data_category", "") or ""))
        mechanism = normalize_family_key(str(contract.get("mechanism", "") or ""))
        expected_risks = set(DEFAULT_RISKS_BY_CATEGORY.get(data_category, ()))
        expected_risks.update(DEFAULT_RISKS_BY_MECHANISM.get(mechanism, ()))
        expected_risks.update(risk for risk in token_risks if risk != "statistical")

        hypothesis_text = str(contract.get("factor_risk_hypothesis", "") or "")
        overlay_text = str(validation_design.get("factor_overlay", "") or "")
        controls_text = str(validation_design.get("comparison_controls", "") or "")
        hypothesis_risks = _mentioned_risks(hypothesis_text)
        overlay_risks = _mentioned_risks(overlay_text, controls_text)

        block_reasons: list[str] = []
        hold_reasons: list[str] = []
        if str(contract_entry.get("assessment", {}).get("gate_status") or "block") == "block":
            block_reasons.append("factor-risk overlay requires a passing-or-held research-contract record first")
        if str(validation_entry.get("assessment", {}).get("gate_status") or "block") == "block":
            block_reasons.append("factor-risk overlay requires a passing-or-held validation-design record first")
        if not expressions:
            block_reasons.append("family expressions are missing, so factor-risk hints cannot be inferred")

        uncovered_in_hypothesis = sorted(risk for risk in expected_risks if risk not in hypothesis_risks)
        uncovered_in_overlay = sorted(risk for risk in expected_risks if risk not in overlay_risks)
        covered_hypothesis_risks = sorted(risk for risk in expected_risks if risk in hypothesis_risks)
        covered_overlay_risks = sorted(risk for risk in expected_risks if risk in overlay_risks)

        if not block_reasons:
            if expected_risks and not covered_overlay_risks and "statistical" not in overlay_risks:
                hold_reasons.append(
                    "factor overlay does not address expected risks: " + ", ".join(sorted(expected_risks)[:3])
                )

        if block_reasons:
            gate_status = "block"
            reasons = block_reasons
        elif hold_reasons:
            gate_status = "hold"
            reasons = hold_reasons
        else:
            gate_status = "pass"
            reasons = ["factor-risk overlay gate passed"]

        items.append(
            {
                "family_key": family_key,
                "source_family_doc_paths": [str(getattr(doc, "path", "")) for doc in docs],
                "factor_profile": {
                    "data_category": data_category,
                    "mechanism": mechanism,
                    "field_tokens": list(tokens),
                    "expected_risks": sorted(expected_risks),
                    "token_risks": sorted(token_risks),
                    "hypothesis_risks": sorted(hypothesis_risks),
                    "overlay_risks": sorted(overlay_risks),
                },
                "assessment": {
                    "gate_status": gate_status,
                    "reasons": reasons,
                    "uncovered_hypothesis_risks": uncovered_in_hypothesis,
                    "uncovered_overlay_risks": uncovered_in_overlay,
                },
            }
        )

    counts = {
        "family_count": len(items),
        "pass_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "pass"),
        "hold_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "hold"),
        "block_count": sum(1 for item in items if item.get("assessment", {}).get("gate_status") == "block"),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "bind each family to a concrete factor-risk hypothesis and overlay before local mining continues",
        "counts": counts,
        "items": items,
    }


def index_factor_risk_overlay(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_factor_risk_overlay_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Factor Risk Overlay",
        "",
        f"- Objective: {report.get('objective', 'factor risk overlay')}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Pass: {counts.get('pass_count', 0)}",
        f"- Hold: {counts.get('hold_count', 0)}",
        f"- Block: {counts.get('block_count', 0)}",
        "",
        "| family | gate | expected risks | hypothesis risks | overlay risks | reasons |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        profile = item.get("factor_profile", {})
        assessment = item.get("assessment", {})
        lines.append(
            "| {family_key} | {gate_status} | {expected_risks} | {hypothesis_risks} | {overlay_risks} | {reasons} |".format(
                family_key=item.get("family_key"),
                gate_status=assessment.get("gate_status"),
                expected_risks=", ".join(profile.get("expected_risks", [])[:4]) or "-",
                hypothesis_risks=", ".join(profile.get("hypothesis_risks", [])[:4]) or "-",
                overlay_risks=", ".join(profile.get("overlay_risks", [])[:4]) or "-",
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    return "\n".join(lines)

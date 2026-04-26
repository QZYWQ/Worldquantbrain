#!/usr/bin/env python3
"""Shared family complexity-budget helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from alpha_mining_core import (
    canonicalize_expression,
    collect_threshold_values,
    collect_window_values,
    count_function_calls,
    infer_expression_categories,
    max_parenthesis_depth,
    quality_metrics,
)
from alpha_success_core import normalize_family_key


DEFAULT_COMPLEXITY_BUDGET = {
    "max_total_expressions": 6,
    "max_variant_expressions": 4,
    "max_function_calls_per_expression": 8,
    "max_parenthesis_depth_per_expression": 8,
    "max_window_values_per_expression": 5,
    "max_threshold_values_per_expression": 3,
    "max_category_count_per_expression": 2,
    "max_unique_windows_per_family": 8,
    "max_unique_thresholds_per_family": 4,
    "max_overfit_risk_per_expression": 72.0,
    "max_coupling_risk_per_expression": 55.0,
}


def _family_key_from_doc(doc: Any) -> str:
    topic = str(getattr(doc, "topic", "") or "")
    if topic:
        return normalize_family_key(topic)
    path = getattr(doc, "path", None)
    if path is not None:
        return normalize_family_key(Path(path).stem)
    return "unknown_family"


def _complexity_policy(policy: dict[str, Any] | None = None) -> dict[str, float]:
    raw = {}
    if isinstance(policy, dict):
        candidate = policy.get("complexity_budget")
        if isinstance(candidate, dict):
            raw = candidate

    merged = dict(DEFAULT_COMPLEXITY_BUDGET)
    for key, default in DEFAULT_COMPLEXITY_BUDGET.items():
        value = raw.get(key)
        if isinstance(default, int):
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                merged[key] = parsed
        else:
            try:
                parsed = float(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                merged[key] = parsed
    return merged


def build_complexity_budget_report(
    *,
    family_docs: Sequence[Any],
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    budget = _complexity_policy(policy)
    docs_by_family: dict[str, list[Any]] = {}
    for doc in family_docs:
        docs_by_family.setdefault(_family_key_from_doc(doc), []).append(doc)

    items: list[dict[str, Any]] = []
    for family_key in sorted(docs_by_family):
        docs = docs_by_family[family_key]
        expressions: list[str] = []
        source_paths: list[str] = []
        variant_expression_count = 0
        for doc in docs:
            source_paths.append(str(getattr(doc, "path", "")))
            expressions.extend(
                str(expression)
                for expression in getattr(doc, "all_expressions", ())
                if str(expression).strip()
            )
            variant_expression_count += len(
                [expression for expression in getattr(doc, "variant_expressions", ()) if str(expression).strip()]
            )

        deduped_expressions = list(
            dict.fromkeys(canonicalize_expression(expression) for expression in expressions if expression.strip())
        )
        expression_metrics: list[dict[str, Any]] = []
        unique_windows: set[float] = set()
        unique_thresholds: set[float] = set()
        max_function_calls = 0
        max_parenthesis = 0
        max_window_count = 0
        max_threshold_count = 0
        max_category_count = 0
        max_overfit_risk = 0.0
        max_coupling_risk = 0.0

        hold_reasons: list[str] = []
        block_reasons: list[str] = []

        if not deduped_expressions:
            block_reasons.append("family doc is missing baseline or variant expressions")

        for index, expression in enumerate(deduped_expressions, start=1):
            doc = docs[min(index - 1, len(docs) - 1)]
            windows = collect_window_values(expression)
            thresholds = collect_threshold_values(expression)
            categories = infer_expression_categories(expression)
            metrics = quality_metrics(expression, family=doc)
            function_call_count = count_function_calls(expression)
            parenthesis_depth = max_parenthesis_depth(expression)
            max_function_calls = max(max_function_calls, function_call_count)
            max_parenthesis = max(max_parenthesis, parenthesis_depth)
            max_window_count = max(max_window_count, len(windows))
            max_threshold_count = max(max_threshold_count, len(thresholds))
            max_category_count = max(max_category_count, len(categories))
            max_overfit_risk = max(max_overfit_risk, float(metrics.get("overfit_risk", 0.0) or 0.0))
            max_coupling_risk = max(max_coupling_risk, float(metrics.get("coupling_risk", 0.0) or 0.0))
            unique_windows.update(windows)
            unique_thresholds.update(thresholds)

            expression_metrics.append(
                {
                    "expression": expression,
                    "function_call_count": function_call_count,
                    "parenthesis_depth": parenthesis_depth,
                    "window_value_count": len(windows),
                    "threshold_value_count": len(thresholds),
                    "category_count": len(categories),
                    "overfit_risk": round(float(metrics.get("overfit_risk", 0.0) or 0.0), 2),
                    "coupling_risk": round(float(metrics.get("coupling_risk", 0.0) or 0.0), 2),
                }
            )

        if len(deduped_expressions) > int(budget["max_total_expressions"]):
            hold_reasons.append(
                f"family already exposes {len(deduped_expressions)} expressions, above the complexity budget of {int(budget['max_total_expressions'])}"
            )
        if variant_expression_count > int(budget["max_variant_expressions"]):
            hold_reasons.append(
                f"family already exposes {variant_expression_count} variants, above the variant budget of {int(budget['max_variant_expressions'])}"
            )
        if max_function_calls > int(budget["max_function_calls_per_expression"]):
            hold_reasons.append(
                f"at least one expression uses {max_function_calls} function calls, above the budget of {int(budget['max_function_calls_per_expression'])}"
            )
        if max_parenthesis > int(budget["max_parenthesis_depth_per_expression"]):
            hold_reasons.append(
                f"at least one expression reaches parenthesis depth {max_parenthesis}, above the budget of {int(budget['max_parenthesis_depth_per_expression'])}"
            )
        if max_window_count > int(budget["max_window_values_per_expression"]):
            hold_reasons.append(
                f"at least one expression uses {max_window_count} window values, above the budget of {int(budget['max_window_values_per_expression'])}"
            )
        if max_threshold_count > int(budget["max_threshold_values_per_expression"]):
            hold_reasons.append(
                f"at least one expression uses {max_threshold_count} threshold values, above the budget of {int(budget['max_threshold_values_per_expression'])}"
            )
        if max_category_count > int(budget["max_category_count_per_expression"]):
            hold_reasons.append(
                f"at least one expression mixes {max_category_count} data-category signals, above the budget of {int(budget['max_category_count_per_expression'])}"
            )
        if len(unique_windows) > int(budget["max_unique_windows_per_family"]):
            hold_reasons.append(
                f"family spans {len(unique_windows)} distinct windows, above the family budget of {int(budget['max_unique_windows_per_family'])}"
            )
        if len(unique_thresholds) > int(budget["max_unique_thresholds_per_family"]):
            hold_reasons.append(
                f"family spans {len(unique_thresholds)} distinct thresholds, above the family budget of {int(budget['max_unique_thresholds_per_family'])}"
            )
        if max_overfit_risk > float(budget["max_overfit_risk_per_expression"]):
            hold_reasons.append(
                f"at least one expression reaches overfit risk {max_overfit_risk:.2f}, above the budget of {float(budget['max_overfit_risk_per_expression']):.2f}"
            )
        if max_coupling_risk > float(budget["max_coupling_risk_per_expression"]):
            hold_reasons.append(
                f"at least one expression reaches coupling risk {max_coupling_risk:.2f}, above the budget of {float(budget['max_coupling_risk_per_expression']):.2f}"
            )

        if block_reasons:
            gate_status = "block"
            reasons = block_reasons
        elif hold_reasons:
            gate_status = "hold"
            reasons = hold_reasons
        else:
            gate_status = "pass"
            reasons = ["family stays within the current expression-complexity budget"]

        items.append(
            {
                "family_key": family_key,
                "source_family_doc_paths": list(dict.fromkeys(source_paths)),
                "counts": {
                    "doc_count": len(docs),
                    "expression_count": len(deduped_expressions),
                    "variant_expression_count": variant_expression_count,
                    "unique_window_count": len(unique_windows),
                    "unique_threshold_count": len(unique_thresholds),
                    "max_function_call_count": max_function_calls,
                    "max_parenthesis_depth": max_parenthesis,
                    "max_window_value_count": max_window_count,
                    "max_threshold_value_count": max_threshold_count,
                    "max_category_count": max_category_count,
                },
                "expression_metrics": expression_metrics,
                "assessment": {
                    "gate_status": gate_status,
                    "reasons": reasons,
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
        "objective": "stop weak family hypotheses from expanding through excessive same-family complexity",
        "budget": dict(budget),
        "counts": counts,
        "items": items,
    }


def index_complexity_budget(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_complexity_budget_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Complexity Budget",
        "",
        f"- Objective: {report.get('objective', 'complexity budget')}",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Pass: {counts.get('pass_count', 0)}",
        f"- Hold: {counts.get('hold_count', 0)}",
        f"- Block: {counts.get('block_count', 0)}",
        "",
        "| family | gate | expressions | variants | max calls | max depth | unique windows | reasons |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        item_counts = item.get("counts", {})
        lines.append(
            "| {family_key} | {gate_status} | {expression_count} | {variant_expression_count} | {max_function_call_count} | {max_parenthesis_depth} | {unique_window_count} | {reasons} |".format(
                family_key=item.get("family_key"),
                gate_status=assessment.get("gate_status"),
                expression_count=item_counts.get("expression_count"),
                variant_expression_count=item_counts.get("variant_expression_count"),
                max_function_call_count=item_counts.get("max_function_call_count"),
                max_parenthesis_depth=item_counts.get("max_parenthesis_depth"),
                unique_window_count=item_counts.get("unique_window_count"),
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    return "\n".join(lines)

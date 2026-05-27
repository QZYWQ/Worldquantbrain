#!/usr/bin/env python3
"""Rank alpha variations by economic interpretability after record-only checks."""
import json
import math
from pathlib import Path


PROJECT_ROOT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
VARIATIONS_FILE = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations.json"
RESULTS_FILE = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations-results.json"
CHECKS_FILE = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations-submission-check.json"
OUTPUT_JSON = PROJECT_ROOT / "runs/submission-memos/2026-05-22-alpha-variations-economic-top5.json"
OUTPUT_MD = PROJECT_ROOT / "runs/submission-memos/2026-05-22-alpha-variations-economic-top5.md"


ECONOMIC_THEMES = [
    {
        "name": "earnings_yield",
        "terms": ["earnings_per_share_average/close", "anl4_afv4_median_eps/close", "eps / close"],
        "score": 30,
        "thesis": "Relative earnings yield: stocks with stronger earnings power versus price should command better forward returns.",
    },
    {
        "name": "estimate_revision_or_analyst_attention",
        "terms": ["sales_estimate_count", "change_in_eps_surprise", "anl4_"],
        "score": 24,
        "thesis": "Analyst estimate and surprise information can capture delayed fundamental repricing.",
    },
    {
        "name": "balance_sheet_or_quality",
        "terms": ["assets / cap", "revenue", "tobins_q_ratio", "fnd6_", "unsystematic_risk"],
        "score": 22,
        "thesis": "Balance-sheet, valuation, revenue, and risk fields can proxy for quality, capital structure, or fundamental mispricing.",
    },
    {
        "name": "sentiment_conditioned_risk",
        "terms": ["scl12_sentiment", "sentiment"],
        "score": 18,
        "thesis": "Sentiment can condition when risk or reversal effects are more likely to be repriced.",
    },
    {
        "name": "price_volume_microstructure",
        "terms": ["volume", "vwap", "high", "low"],
        "score": 12,
        "thesis": "Price-volume and intraday range behavior can encode liquidity pressure, reversal, or crowding.",
    },
    {
        "name": "short_horizon_price_reversal",
        "terms": ["returns", "close"],
        "score": 6,
        "thesis": "Short-horizon price reversal is economically plausible but crowded and easier to overfit.",
    },
]

OPERATOR_TOKENS = [
    "rank(",
    "group_rank(",
    "group_neutralize(",
    "group_zscore(",
    "ts_",
    "trade_when(",
    "winsorize(",
    "ts_backfill(",
    "densify(",
    "bucket(",
    "quantile(",
    "reverse(",
    "multiply(",
    "divide(",
    "add(",
    "max(",
    "abs(",
    "zscore(",
    "normalize(",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


def finite_number(value, default=0.0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def bool_check(checks, name):
    for check in checks:
        if check.get("name") == name:
            return check.get("result") == "PASS"
    return None


def expression_complexity(expression):
    return sum(expression.count(token) for token in OPERATOR_TOKENS)


def economic_profile(expression):
    matched = []
    score = 0
    thesis = []
    lower_expr = expression.lower()
    for theme in ECONOMIC_THEMES:
        if any(term.lower() in lower_expr for term in theme["terms"]):
            matched.append(theme["name"])
            score += theme["score"]
            thesis.append(theme["thesis"])
    if not matched:
        thesis.append("No strong economic field theme detected; this looks closer to operator or parameter exploration.")
    return matched, score, thesis


def complexity_penalty(expression):
    complexity = expression_complexity(expression)
    penalty = max(0, complexity - 8) * 2
    if expression.count("*") + expression.count("/") + expression.count("+") + expression.count("-") > 8:
        penalty += 8
    if "trade_when(" in expression and complexity > 14:
        penalty += 8
    return complexity, penalty


def metric_score(metrics):
    sharpe = finite_number(metrics.get("sharpe"))
    fitness = finite_number(metrics.get("fitness"))
    turnover = finite_number(metrics.get("turnover"))
    score = 0
    score += min(max((sharpe - 1.0) * 18, -10), 26)
    score += min(max((fitness - 0.8) * 22, -10), 22)
    if 0.05 <= turnover <= 0.45:
        score += 8
    elif turnover > 0.7:
        score -= 8
    return score


def check_score(record):
    if record.get("strict_8pass"):
        return 24
    pass_count = finite_number(record.get("pass_count"))
    check_count = finite_number(record.get("check_count"))
    fail_count = finite_number(record.get("fail_count"))
    if check_count <= 0:
        return 0
    return min(18, pass_count * 2) - fail_count * 6


def build_records():
    variations = {item["id"]: item for item in load_json(VARIATIONS_FILE)}
    results = {
        item.get("original_id"): item
        for item in load_json(RESULTS_FILE)
        if isinstance(item, dict) and item.get("original_id")
    }
    checks = []
    if CHECKS_FILE.exists():
        checks = load_json(CHECKS_FILE)
    check_by_alpha = {item.get("alpha_id"): item for item in checks if isinstance(item, dict)}

    records = []
    for original_id, result in results.items():
        if result.get("status") != "SUCCESS":
            continue
        expression = result.get("expression") or variations.get(original_id, {}).get("regular", {}).get("code", "")
        alpha_id = result.get("new_alpha_id")
        check = check_by_alpha.get(alpha_id, {})
        themes, econ_score, theses = economic_profile(expression)
        complexity, penalty = complexity_penalty(expression)
        metrics = result.get("metrics") or {}
        checks_list = check.get("checks") or []
        total_score = (
            econ_score
            + metric_score(metrics)
            + check_score(check)
            - penalty
        )
        if not themes:
            total_score -= 12
        if complexity > 18:
            total_score -= 12
        if themes == ["short_horizon_price_reversal"]:
            total_score -= 8

        records.append(
            {
                "alpha_id": alpha_id,
                "original_id": original_id,
                "expression": expression,
                "settings": result.get("settings") or variations.get(original_id, {}).get("settings", {}),
                "metrics": metrics,
                "strict_8pass": bool(check.get("strict_8pass")),
                "pass_count": check.get("pass_count"),
                "check_count": check.get("check_count"),
                "failed_or_non_pass_checks": [
                    item.get("name") for item in check.get("non_pass_checks", [])
                ],
                "self_correlation": check.get("self_correlation"),
                "subuniverse_pass": bool_check(checks_list, "LOW_SUB_UNIVERSE_SHARPE"),
                "economic_themes": themes,
                "economic_thesis": theses,
                "complexity": complexity,
                "complexity_penalty": penalty,
                "metric_score": round(metric_score(metrics), 4),
                "check_score": round(check_score(check), 4),
                "economic_logic_score": econ_score,
                "total_score": round(total_score, 4),
            }
        )

    return sorted(records, key=lambda item: item["total_score"], reverse=True)


def render_markdown(top5, all_ranked):
    strict_8pass_count = sum(1 for item in all_ranked if item.get("strict_8pass"))
    if strict_8pass_count >= 5:
        scope_note = "At least 5 strict 8-pass alphas were available, so the Top 5 is selected only from strict 8-pass records."
    else:
        scope_note = "Fewer than 5 strict 8-pass alphas were available, so the list includes all strict 8-pass records first and then fills with the strongest remaining economic candidates."
    lines = [
        "# 2026-05-22 Alpha Variations Economic Top 5",
        "",
        "- Mode: RECORD ONLY. No alpha was submitted by this ranking step.",
        f"- Source simulation results: `{RESULTS_FILE}`",
        f"- Source official checks: `{CHECKS_FILE}`",
        f"- Successful simulations ranked: {len(all_ranked)}",
        f"- Strict 8-pass records available: {strict_8pass_count}",
        "",
        "Selection bias: prefer interpretable field logic, healthy real metrics, and official check evidence; penalize operator-heavy or short-window parameter stacks.",
        scope_note,
        "",
        "| Rank | Alpha ID | Original ID | Score | 8pass | Sharpe | Fitness | Turnover | Economic Theme |",
        "| ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for rank, item in enumerate(top5, start=1):
        metrics = item.get("metrics") or {}
        lines.append(
            "| {rank} | {alpha_id} | {original_id} | {score} | {pass8} | {sharpe} | {fitness} | {turnover} | {themes} |".format(
                rank=rank,
                alpha_id=item.get("alpha_id"),
                original_id=item.get("original_id"),
                score=item.get("total_score"),
                pass8="yes" if item.get("strict_8pass") else "no",
                sharpe=metrics.get("sharpe"),
                fitness=metrics.get("fitness"),
                turnover=metrics.get("turnover"),
                themes=", ".join(item.get("economic_themes") or ["none"]),
            )
        )

    lines.extend(["", "## Rationale", ""])
    for rank, item in enumerate(top5, start=1):
        metrics = item.get("metrics") or {}
        lines.extend(
            [
                f"### {rank}. `{item.get('alpha_id')}` from `{item.get('original_id')}`",
                "",
                f"- Expression: `{item.get('expression')}`",
                f"- Metrics: Sharpe={metrics.get('sharpe')}, Fitness={metrics.get('fitness')}, Turnover={metrics.get('turnover')}",
                f"- Official check posture: strict_8pass={item.get('strict_8pass')}, pass_count={item.get('pass_count')}, check_count={item.get('check_count')}, self_correlation={item.get('self_correlation')}",
                f"- Economic logic: {' '.join(item.get('economic_thesis') or [])}",
                f"- Complexity: operator_count_estimate={item.get('complexity')}, penalty={item.get('complexity_penalty')}",
                "",
            ]
        )

    lines.extend(["## Full Ranked Successful Set", ""])
    for rank, item in enumerate(all_ranked, start=1):
        metrics = item.get("metrics") or {}
        lines.append(
            f"{rank}. `{item.get('alpha_id')}` / `{item.get('original_id')}` "
            f"score={item.get('total_score')} sharpe={metrics.get('sharpe')} "
            f"fitness={metrics.get('fitness')} 8pass={item.get('strict_8pass')} "
            f"themes={','.join(item.get('economic_themes') or ['none'])}"
        )

    return "\n".join(lines) + "\n"


def main():
    ranked = build_records()
    ranked_8pass = [item for item in ranked if item.get("strict_8pass")]
    ranked_non_8pass = [item for item in ranked if not item.get("strict_8pass")]
    if len(ranked_8pass) >= 5:
        top5 = ranked_8pass[:5]
        selection_scope = "strict_8pass_only"
    else:
        top5 = (ranked_8pass + ranked_non_8pass)[:5]
        selection_scope = "all_8pass_then_best_non_8pass_fill"
    payload = {
        "mode": "RECORD_ONLY",
        "selection_rule": "If at least 5 strict 8-pass alphas exist, choose only from strict 8-pass. Otherwise include all strict 8-pass first, then fill with the best remaining candidates by economic logic score plus real metrics/check evidence, with complexity and parameter-stack penalties.",
        "selection_scope": selection_scope,
        "top5": top5,
        "all_ranked": ranked,
    }
    save_json(OUTPUT_JSON, payload)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(render_markdown(top5, ranked), encoding="utf-8")
    print("Saved economic top 5 JSON to:", OUTPUT_JSON)
    print("Saved economic top 5 memo to:", OUTPUT_MD)
    print("Top 5:")
    for index, item in enumerate(top5, start=1):
        metrics = item.get("metrics") or {}
        print(
            f"  {index}. {item.get('alpha_id')} ({item.get('original_id')}) "
            f"score={item.get('total_score')} sharpe={metrics.get('sharpe')} "
            f"fitness={metrics.get('fitness')} 8pass={item.get('strict_8pass')}"
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Filter non-inherited alpha candidates for economic logic review.

No submit calls are made by this script.
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, "/Users/zpdedn/Documents/github/worldquantAPI/user")
from machine_lib import login  # noqa: E402


PROJECT_ROOT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
VARIATION_RESULTS = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations-results.json"
SUBMISSION_MEMOS = PROJECT_ROOT / "runs/submission-memos"
OUTPUT_JSON = SUBMISSION_MEMOS / "2026-05-23-independent-non-inherited-candidate-filter.json"
OUTPUT_MD = SUBMISSION_MEMOS / "2026-05-23-independent-non-inherited-candidate-filter.md"
API_BASE = "https://api.worldquantbrain.com"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_all_alphas(session, limit: int = 100) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    offset = 0
    while True:
        url = f"{API_BASE}/users/self/alphas?limit={limit}&offset={offset}&hidden=false&type!=SUPER"
        response = session.get(url, timeout=60)
        response.raise_for_status()
        payload = response.json()
        batch = payload.get("results") or []
        records.extend(batch)
        count = int(payload.get("count") or len(records))
        if not batch or len(records) >= count:
            break
        offset += limit
        time.sleep(0.5)
    return records


def get_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = session.get(f"{API_BASE}/alphas/{alpha_id}", timeout=60)
    response.raise_for_status()
    return response.json()


def run_check(session, alpha_id: str) -> dict[str, Any]:
    last_error: dict[str, Any] | None = None
    for attempt in range(1, 35):
        response = session.get(f"{API_BASE}/alphas/{alpha_id}/check", timeout=60)
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            time.sleep(float(retry_after))
            continue
        if response.status_code == 401:
            return {"status": "RELOGIN", "checks": [], "error": "401"}
        if response.status_code != 200:
            last_error = {"status": "HTTP_ERROR", "http_status": response.status_code, "body": response.text[:500]}
            time.sleep(2)
            continue
        try:
            data = response.json()
        except Exception as exc:
            last_error = {"status": "NON_JSON", "body": response.text[:500], "exception": str(exc)}
            time.sleep(2)
            continue
        checks = data.get("is", {}).get("checks") or []
        non_pass = [item for item in checks if item.get("result") != "PASS"]
        return {
            "status": "CHECKED",
            "checks": checks,
            "check_count": len(checks),
            "pass_count": sum(1 for item in checks if item.get("result") == "PASS"),
            "strict_all_pass": bool(checks) and not non_pass,
            "non_pass_checks": non_pass,
            "raw": data,
        }
    return {"status": "CHECK_FAILED", "checks": [], "error": last_error or {"status": "retry_limit"}}


def expression_of(alpha: dict[str, Any]) -> str:
    regular = alpha.get("regular")
    if isinstance(regular, dict):
        return str(regular.get("code") or "")
    return str(regular or "")


def executable_expr(expr: str) -> str:
    return re.sub(r"/\*.*?\*/", "", expr, flags=re.S).strip()


def metrics_of(alpha: dict[str, Any]) -> dict[str, Any]:
    is_data = alpha.get("is") or {}
    checks = is_data.get("checks") or []
    sub_u = None
    self_corr = None
    for item in checks:
        if item.get("name") == "LOW_SUB_UNIVERSE_SHARPE":
            sub_u = item.get("value")
        if item.get("name") == "SELF_CORRELATION":
            self_corr = item.get("value")
    return {
        "sharpe": is_data.get("sharpe"),
        "fitness": is_data.get("fitness"),
        "turnover": is_data.get("turnover"),
        "returns": is_data.get("returns"),
        "drawdown": is_data.get("drawdown"),
        "margin": is_data.get("margin"),
        "longCount": is_data.get("longCount"),
        "shortCount": is_data.get("shortCount"),
        "subUniverseSharpe": sub_u,
        "selfCorrelation": self_corr,
    }


def field_tokens(expr: str) -> list[str]:
    expr = executable_expr(expr)
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", expr)
    operators = {
        "abs",
        "add",
        "and",
        "bucket",
        "densify",
        "divide",
        "group_neutralize",
        "group_rank",
        "if_else",
        "inverse",
        "log",
        "market",
        "max",
        "min",
        "multiply",
        "normalize",
        "or",
        "quantile",
        "rank",
        "reverse",
        "scale",
        "sector",
        "subindustry",
        "subtract",
        "trade_when",
        "ts_arg_max",
        "ts_arg_min",
        "ts_backfill",
        "ts_count_nans",
        "ts_decay_linear",
        "ts_delta",
        "ts_mean",
        "ts_rank",
        "ts_std_dev",
        "ts_sum",
        "ts_zscore",
        "winsorize",
        "zscore",
    }
    market_fields = {"open", "high", "low", "close", "vwap", "volume", "returns", "cap"}
    return sorted({token for token in tokens if token not in operators and token not in market_fields})


def economic_theme(expr: str) -> tuple[str, str, int]:
    e = executable_expr(expr).lower()
    fields = field_tokens(e)
    if any(token.startswith("anl") or token in {"eps", "revenue", "earnings_per_share_average"} for token in fields):
        return (
            "analyst_or_fundamental_revision",
            "Analyst estimate or accounting fields can capture delayed repricing of changed fundamentals.",
            24,
        )
    if any(
        token.startswith("fnd")
        or token.startswith("fn_")
        or token in {"assets", "assets_curr", "liabilities", "cashflow", "free_cashflow_max", "free_cashflow_min", "operating_income"}
        for token in fields
    ):
        return (
            "fundamental_quality_or_balance_sheet",
            "Fundamental statement fields can proxy for quality, financing pressure, asset intensity, or balance-sheet risk.",
            22,
        )
    if "unsystematic_risk" in e or "systematic_risk" in e:
        return (
            "risk_repricing",
            "Idiosyncratic or systematic risk changes can proxy for uncertainty repricing and investor risk appetite.",
            18,
        )
    if "scl" in e or "sentiment" in e:
        return (
            "sentiment_conditioned_repricing",
            "Sentiment can condition when risk, liquidity, or reversal effects are more likely to be repriced.",
            17,
        )
    if any(token in e for token in ("close", "returns", "high", "low", "volume", "vwap")):
        return (
            "price_volume_microstructure",
            "Price and volume behavior can capture reversal, liquidity pressure, or crowding, but it is often crowded and parameter-sensitive.",
            8,
        )
    return ("unclear", "No clear non-price economic mechanism was detected from fields alone.", 0)


def complexity(expr: str) -> int:
    expr = executable_expr(expr)
    return sum(expr.count(token) for token in ("(", "rank", "ts_", "group_", "trade_when", "quantile", "winsorize", "bucket"))


def metric_score(metrics: dict[str, Any]) -> float:
    sharpe = float(metrics.get("sharpe") or 0)
    fitness = float(metrics.get("fitness") or 0)
    turnover = float(metrics.get("turnover") or 0)
    returns = float(metrics.get("returns") or 0)
    sub_u = metrics.get("subUniverseSharpe")
    score = sharpe * 12 + fitness * 16 + returns * 30
    if sub_u is not None:
        score += float(sub_u) * 4
    if 0.01 <= turnover <= 0.25:
        score += 6
    elif turnover > 0.45:
        score -= 8
    return round(score, 2)


def reliability_flags(expr: str, metrics: dict[str, Any], check: dict[str, Any] | None) -> list[str]:
    flags: list[str] = []
    if (metrics.get("sharpe") or 0) >= 1.25 and (metrics.get("fitness") or 0) >= 1.0:
        flags.append("passes hard metric floor")
    if 0.01 <= (metrics.get("turnover") or 0) <= 0.25:
        flags.append("low or moderate turnover")
    if field_tokens(expr):
        flags.append("uses non-price field(s)")
    else:
        flags.append("price-only; weaker economic evidence")
    if check and check.get("strict_all_pass"):
        flags.append("official check all-pass")
    elif check and check.get("status") == "CHECKED":
        failed = ",".join(item.get("name", "") for item in check.get("non_pass_checks", []))
        flags.append(f"official check has non-pass: {failed}")
    return flags


def score_candidate(record: dict[str, Any]) -> dict[str, Any]:
    expr = record["expression"]
    theme, thesis, logic_score = economic_theme(expr)
    comp = complexity(expr)
    mscore = metric_score(record["metrics"])
    check = record.get("official_check")
    check_score = 0
    if check:
        if check.get("strict_all_pass"):
            check_score = 28
        elif check.get("status") == "CHECKED":
            check_score = max(0, int(check.get("pass_count") or 0) * 2 - len(check.get("non_pass_checks") or []) * 6)
    penalty = 0
    if comp > 12:
        penalty += 10
    if not field_tokens(expr):
        penalty += 12
    if (record["metrics"].get("turnover") or 0) > 0.45:
        penalty += 8
    total = round(mscore + logic_score + check_score - penalty, 2)
    idea_score = round(logic_score + mscore * 0.5 - max(0, comp - 8) * 0.5, 2)
    record.update(
        {
            "economic_theme": theme,
            "economic_thesis": thesis,
            "economic_logic_score": logic_score,
            "metric_score": mscore,
            "official_check_score": check_score,
            "complexity": comp,
            "score_penalty": penalty,
            "total_score": total,
            "idea_score": idea_score,
            "reliability_flags": reliability_flags(expr, record["metrics"], check),
        }
    )
    return record


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# 2026-05-23 Independent Non-Inherited Candidate Filter",
        "",
        "- Mode: RECORD ONLY. No alpha was submitted.",
        "- Scope: current account API alphas excluding 2026-05-22 inherited variation IDs.",
        f"- Account alpha count: {payload['account_alpha_count']}",
        f"- Inherited variation IDs excluded: {payload['inherited_variation_id_count']}",
        f"- Non-inherited alphas found: {payload['non_inherited_count']}",
        f"- Metric-prefiltered candidates: {payload['prefiltered_count']}",
        f"- Official-check attempted: {payload['official_check_attempted_count']}",
        "",
        "## Ranked Candidates",
        "",
    ]
    if not payload["ranked_candidates"]:
        lines.append("No reliable non-inherited candidate survived the filter.")
    else:
        lines.extend(
            [
                "| Rank | Alpha | Status | Score | Check | Sharpe | Fitness | Turnover | Theme | Expression |",
                "| ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for i, item in enumerate(payload["ranked_candidates"], 1):
            check = item.get("official_check") or {}
            check_text = (
                f"{check.get('pass_count')}/{check.get('check_count')}"
                if check.get("status") == "CHECKED"
                else check.get("status", "not_checked")
            )
            metrics = item["metrics"]
            lines.append(
                f"| {i} | {item['alpha_id']} | {item['status']}/{item['stage']} | {item['total_score']} | "
                f"{check_text} | {metrics.get('sharpe')} | {metrics.get('fitness')} | {metrics.get('turnover')} | "
                f"{item['economic_theme']} | `{item['expression']}` |"
            )
    lines.extend(["", "## Candidate Notes", ""])
    if not payload["ranked_candidates"]:
        lines.append("- No non-inherited alpha currently has both strong economics and official pass evidence.")
    for item in payload["ranked_candidates"]:
        lines.extend(
            [
                f"### {item['alpha_id']}",
                "",
                f"- Thesis: {item['economic_thesis']}",
                f"- Reliability flags: {', '.join(item['reliability_flags'])}",
                f"- Fields detected: {', '.join(item['fields']) if item['fields'] else 'price-only'}",
                f"- Interpretation: {item['interpretation']}",
                "",
            ]
        )
    lines.extend(["## Rejected / Weak Non-Inherited Observations", ""])
    for item in payload.get("weak_non_inherited", [])[:20]:
        metrics = item["metrics"]
        lines.append(
            f"- `{item['alpha_id']}` score={item['total_score']} "
            f"Sharpe={metrics.get('sharpe')} Fitness={metrics.get('fitness')} Turnover={metrics.get('turnover')}: "
            f"{item['reject_reason']} `{item['expression']}`"
        )
    lines.extend(["", "## Research Ideas Worth Rebuilding", ""])
    ideas = payload.get("research_ideas", [])
    if not ideas:
        lines.append("- No non-inherited economic idea is worth carrying forward from this scan.")
    for item in ideas:
        metrics = item["metrics"]
        lines.append(
            f"- `{item['alpha_id']}` idea_score={item['idea_score']} "
            f"Sharpe={metrics.get('sharpe')} Fitness={metrics.get('fitness')} Turnover={metrics.get('turnover')} "
            f"theme={item['economic_theme']}: {item['economic_thesis']} Expr: `{executable_expr(item['expression'])}`"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    inherited_ids = {
        item.get("new_alpha_id")
        for item in load_json(VARIATION_RESULTS)
        if item.get("new_alpha_id")
    }
    session = login()
    account_alphas = fetch_all_alphas(session)

    details: list[dict[str, Any]] = []
    for alpha in account_alphas:
        alpha_id = alpha.get("id")
        if not alpha_id or alpha_id in inherited_ids:
            continue
        details.append(get_alpha(session, alpha_id))
        time.sleep(0.25)

    non_inherited: list[dict[str, Any]] = []
    for alpha in details:
        expr = expression_of(alpha)
        metrics = metrics_of(alpha)
        fields = field_tokens(expr)
        record = {
            "alpha_id": alpha.get("id"),
            "status": alpha.get("status"),
            "stage": alpha.get("stage"),
            "dateCreated": alpha.get("dateCreated"),
            "dateSubmitted": alpha.get("dateSubmitted"),
            "author": alpha.get("author"),
            "expression": expr,
            "settings": alpha.get("settings", {}),
            "metrics": metrics,
            "fields": fields,
            "classifications": alpha.get("classifications", []),
        }
        non_inherited.append(record)

    prefiltered: list[dict[str, Any]] = []
    weak: list[dict[str, Any]] = []
    for record in non_inherited:
        metrics = record["metrics"]
        sharpe = metrics.get("sharpe") or 0
        fitness = metrics.get("fitness") or 0
        turnover = metrics.get("turnover") or 0
        status_ok = record["status"] == "UNSUBMITTED"
        metric_ok = sharpe >= 1.1 and fitness >= 0.8 and 0.01 <= turnover <= 0.7
        econ_ok = bool(record["fields"])
        if status_ok and metric_ok and econ_ok:
            prefiltered.append(record)
        else:
            scored = score_candidate(record)
            reason = []
            if not status_ok:
                reason.append(f"status={record['status']}")
            if not metric_ok:
                reason.append("below metric prefilter")
            if not econ_ok:
                reason.append("price-only or no non-price field")
            scored["reject_reason"] = ", ".join(reason)
            weak.append(scored)

    # Check only the most promising non-inherited candidates to avoid excessive
    # API pressure while the overnight scan is also running.
    prefiltered = sorted(prefiltered, key=lambda item: metric_score(item["metrics"]), reverse=True)
    for record in prefiltered[:15]:
        record["official_check"] = run_check(session, record["alpha_id"])
        time.sleep(1)

    ranked: list[dict[str, Any]] = []
    for record in prefiltered:
        if "official_check" not in record:
            record["official_check"] = {"status": "NOT_CHECKED"}
        score_candidate(record)
        record["interpretation"] = interpret(record)
        ranked.append(record)
    ranked.sort(key=lambda item: item["total_score"], reverse=True)

    weak.sort(key=lambda item: item["total_score"], reverse=True)
    ideas = [
        item
        for item in weak
        if item.get("fields")
        and item.get("economic_theme") not in ("price_volume_microstructure", "unclear")
        and item.get("idea_score", 0) > 15
    ]
    ideas.sort(key=lambda item: item["idea_score"], reverse=True)
    payload = {
        "mode": "RECORD_ONLY_NO_SUBMIT",
        "timestamp_utc": now_utc(),
        "account_alpha_count": len(account_alphas),
        "inherited_variation_source": str(VARIATION_RESULTS),
        "inherited_variation_id_count": len(inherited_ids),
        "non_inherited_count": len(non_inherited),
        "prefilter": {
            "status": "UNSUBMITTED",
            "sharpe_min": 1.1,
            "fitness_min": 0.8,
            "turnover_range": [0.01, 0.7],
            "requires_non_price_field": True,
        },
        "prefiltered_count": len(prefiltered),
        "official_check_attempted_count": sum(1 for item in ranked if item.get("official_check", {}).get("status") != "NOT_CHECKED"),
        "ranked_candidates": ranked,
        "weak_non_inherited": weak,
        "research_ideas": ideas[:10],
    }
    save_json(OUTPUT_JSON, payload)
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(f"account_alpha_count={len(account_alphas)}")
    print(f"inherited_excluded={len(inherited_ids)}")
    print(f"non_inherited={len(non_inherited)}")
    print(f"prefiltered={len(prefiltered)}")
    print(f"ranked={len(ranked)}")
    print(f"json={OUTPUT_JSON}")
    print(f"md={OUTPUT_MD}")


def interpret(record: dict[str, Any]) -> str:
    theme = record.get("economic_theme")
    expr = record.get("expression", "")
    if theme == "analyst_or_fundamental_revision":
        return "Potentially useful if it measures a fundamental revision or accounting signal rather than a pure smoothing artifact."
    if theme == "fundamental_quality_or_balance_sheet":
        return "Potentially useful if the field relation maps to quality, financing pressure, or accounting conservatism and survives sibling checks."
    if theme == "risk_repricing":
        return "Risk repricing can be economically plausible, but should be checked against crowding and regime dependence."
    if theme == "sentiment_conditioned_repricing":
        return "Sentiment gating can be plausible, but high operator complexity should be penalized unless checks and robustness are strong."
    if "close" in expr or "returns" in expr:
        return "Mostly price-action logic; treat as weaker unless it is tied to a broader mechanism."
    return "Needs a clearer field-level thesis before promotion."


if __name__ == "__main__":
    main()

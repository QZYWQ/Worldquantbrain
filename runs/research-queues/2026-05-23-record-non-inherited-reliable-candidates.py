#!/usr/bin/env python3
"""Record reliable non-inherited 2026-05-22/23 submit-ready candidates.

Record only. No submit endpoint is called.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, "/Users/zpdedn/Documents/github/worldquantAPI/user")
from machine_lib import login  # noqa: E402


PROJECT_ROOT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
API_BASE = "https://api.worldquantbrain.com"

VARIATION_RESULTS = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations-results.json"
CURRENT_8PASS_22 = PROJECT_ROOT / "runs/submission-memos/2026-05-22-current-8pass-record.json"
S2_RESULTS_23 = PROJECT_ROOT / "runs/research-queues/2026-05-23-operating-profitability-s2-composite/results.json"
OVERNIGHT_RESULTS_23 = PROJECT_ROOT / "runs/overnight-mining/2026-05-23-operating-profitability-24h/results.jsonl"

OUTPUT_JSON = PROJECT_ROOT / "runs/submission-memos/2026-05-23-non-inherited-reliable-candidates-record.json"
OUTPUT_MD = PROJECT_ROOT / "runs/submission-memos/2026-05-23-non-inherited-reliable-candidates-record.md"

SUBMITTED_ALPHA_IDS = {"A1kWl0LE", "np3Jrqal", "O0ovYJXg"}
HISTORICAL_22_WINNERS = {
    "GrkPoXPG": "2026-05-22 leverage/cash-burn final report winner",
    "omV7g2NE": "2026-05-22 leverage/cash-burn analyst composite",
    "vRd8lPVw": "2026-05-22 leverage/cash-burn analyst composite",
    "1YJeaRxz": "2026-05-22 leverage/cash-burn burn+3 candidate",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def variation_ids() -> set[str]:
    data = load_json(VARIATION_RESULTS)
    return {
        item.get("new_alpha_id")
        for item in data
        if isinstance(item, dict) and item.get("new_alpha_id")
    }


def expression_of(alpha: dict[str, Any]) -> str:
    regular = alpha.get("regular")
    if isinstance(regular, dict):
        return str(regular.get("code") or "")
    return str(regular or "")


def metrics_of(alpha: dict[str, Any]) -> dict[str, Any]:
    is_data = alpha.get("is") or {}
    return {
        "sharpe": is_data.get("sharpe"),
        "fitness": is_data.get("fitness"),
        "turnover": is_data.get("turnover"),
        "returns": is_data.get("returns"),
        "drawdown": is_data.get("drawdown"),
        "margin": is_data.get("margin"),
        "longCount": is_data.get("longCount"),
        "shortCount": is_data.get("shortCount"),
    }


def check_summary(check_payload: dict[str, Any]) -> dict[str, Any]:
    checks = check_payload.get("is", {}).get("checks") or []
    non_pass = [item for item in checks if item.get("result") != "PASS"]
    return {
        "check_count": len(checks),
        "pass_count": sum(1 for item in checks if item.get("result") == "PASS"),
        "strict_all_pass": bool(checks) and not non_pass,
        "non_pass_checks": non_pass,
        "self_correlation": next((item.get("value") for item in checks if item.get("name") == "SELF_CORRELATION"), None),
        "sub_universe_sharpe": next((item.get("value") for item in checks if item.get("name") == "LOW_SUB_UNIVERSE_SHARPE"), None),
        "checks": checks,
    }


def get_alpha(session, alpha_id: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    response = session.get(f"{API_BASE}/alphas/{alpha_id}", timeout=60)
    if response.status_code != 200:
        return None, {"http_status": response.status_code, "body": response.text[:500]}
    return response.json(), None


def get_check(session, alpha_id: str) -> dict[str, Any]:
    last_error = None
    for attempt in range(1, 50):
        response = session.get(f"{API_BASE}/alphas/{alpha_id}/check", timeout=60)
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            time.sleep(float(retry_after))
            continue
        if response.status_code != 200:
            last_error = {"http_status": response.status_code, "body": response.text[:500], "attempt": attempt}
            time.sleep(2)
            continue
        try:
            return response.json()
        except Exception as exc:
            last_error = {"error": str(exc), "body": response.text[:500], "attempt": attempt}
            time.sleep(2)
    return {"is": {"checks": []}, "check_error": last_error}


def is_price_only(expr: str) -> bool:
    lowered = expr.lower()
    economic_tokens = [
        "operating_income",
        "assets_curr",
        "free_cashflow",
        "fnd",
        "anl4",
        "eps",
        "revenue",
        "book_leverage",
        "cash_burn",
        "liab",
        "asset",
        "prstkc",
        "pstkc",
    ]
    return not any(token in lowered for token in economic_tokens)


def economic_logic(expr: str) -> tuple[bool, str]:
    lowered = expr.lower()
    if "operating_income" in lowered and "assets_curr" in lowered:
        return True, "operating profitability relative to working-capital resources"
    if "free_cashflow" in lowered:
        return True, "cash-flow confirmation or expectation"
    if "fnd6_rectr" in lowered and "fnd6_recd" in lowered:
        return True, "receivables quality ratio"
    if "fnd6_sppe" in lowered and "fnd6_siv" in lowered:
        return True, "fixed-asset or capital-intensity balance-sheet ratio"
    if "fnd6_prstkc" in lowered and "fnd6_pstkc" in lowered:
        return True, "preferred-stock capital-structure pressure"
    if "totassets_flag" in lowered:
        return True, "analyst total-assets flag; mechanically valid but weaker economics"
    if "revenue" in lowered:
        return True, "revenue growth or efficiency"
    if "eps" in lowered and "close" not in lowered:
        return True, "earnings change fundamental signal"
    if "book_leverage" in lowered and "cash_burn" in lowered:
        return True, "leverage adjusted by cash-burn pressure"
    if is_price_only(expr):
        return False, "price-only or market-microstructure expression; excluded by economic-logic rule"
    return False, "economic mechanism not strong enough under this strict filter"


def score(record: dict[str, Any]) -> float:
    metrics = record.get("live_metrics") or {}
    check = record.get("live_check_summary") or {}
    sharpe = float(metrics.get("sharpe") or 0)
    fitness = float(metrics.get("fitness") or 0)
    turnover = float(metrics.get("turnover") or 0)
    sub_u = check.get("sub_universe_sharpe")
    self_corr = check.get("self_correlation")
    value = sharpe * 12 + fitness * 18
    if sub_u is not None:
        value += float(sub_u) * 4
    if self_corr is not None:
        value -= float(self_corr) * 10
    if turnover <= 0.08:
        value += 4
    if record.get("source_day") == "2026-05-23":
        value += 3
    return round(value, 2)


def candidate_universe(inherited: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    excluded = {
        "submitted": [],
        "inherited_variation_22": [],
        "price_only_non_inherited_22": [],
        "historical_22_not_fetchable": [],
    }

    current_22 = load_json(CURRENT_8PASS_22)
    for item in current_22.get("records", []):
        alpha_id = item.get("alpha_id")
        if not alpha_id:
            continue
        if alpha_id in SUBMITTED_ALPHA_IDS:
            excluded["submitted"].append({"alpha_id": alpha_id, "source": str(CURRENT_8PASS_22)})
            continue
        if alpha_id in inherited:
            excluded["inherited_variation_22"].append(
                {"alpha_id": alpha_id, "expression": item.get("expression"), "metrics": item.get("metrics")}
            )
            continue
        ok, reason = economic_logic(item.get("expression") or "")
        if not ok:
            excluded["price_only_non_inherited_22"].append(
                {"alpha_id": alpha_id, "expression": item.get("expression"), "reason": reason}
            )
            continue
        records[alpha_id] = {
            "alpha_id": alpha_id,
            "source_day": "2026-05-22",
            "source": str(CURRENT_8PASS_22),
            "local_expression": item.get("expression"),
            "local_metrics": item.get("metrics"),
            "origin": "non-inherited 2026-05-22 current 8-pass record",
        }

    s2 = load_json(S2_RESULTS_23)
    for item in s2.get("results", []):
        alpha_id = item.get("alpha_id")
        if not alpha_id or alpha_id in SUBMITTED_ALPHA_IDS:
            if alpha_id in SUBMITTED_ALPHA_IDS:
                excluded["submitted"].append({"alpha_id": alpha_id, "source": str(S2_RESULTS_23)})
            continue
        records[alpha_id] = {
            "alpha_id": alpha_id,
            "source_day": "2026-05-23",
            "source": str(S2_RESULTS_23),
            "local_expression": item.get("expression"),
            "local_metrics": item.get("metrics"),
            "origin": "independent operating-profitability S2 result",
        }

    if OVERNIGHT_RESULTS_23.exists():
        for line in OVERNIGHT_RESULTS_23.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            alpha_id = item.get("alpha_id")
            if not alpha_id or alpha_id in SUBMITTED_ALPHA_IDS:
                continue
            records.setdefault(
                alpha_id,
                {
                    "alpha_id": alpha_id,
                    "source_day": "2026-05-23",
                    "source": str(OVERNIGHT_RESULTS_23),
                    "local_expression": item.get("expression"),
                    "local_metrics": item.get("metrics"),
                    "origin": "2026-05-23 operating-profitability 24h targeted runner",
                },
            )

    for alpha_id, note in HISTORICAL_22_WINNERS.items():
        if alpha_id not in records:
            records[alpha_id] = {
                "alpha_id": alpha_id,
                "source_day": "2026-05-22",
                "source": "2026-05-22 leverage/cash-burn reports",
                "origin": note,
                "historical_only": True,
            }
    return list(records.values()), excluded


def inspect_candidate(session, item: dict[str, Any]) -> dict[str, Any]:
    alpha_id = item["alpha_id"]
    alpha, fetch_error = get_alpha(session, alpha_id)
    record = dict(item)
    if fetch_error or alpha is None:
        record["posture"] = "excluded_not_live_fetchable"
        record["fetch_error"] = fetch_error
        return record

    expr = expression_of(alpha)
    ok_econ, econ_reason = economic_logic(expr)
    check = get_check(session, alpha_id)
    check_info = check_summary(check)
    metrics = metrics_of(alpha)

    record.update(
        {
            "status": alpha.get("status"),
            "stage": alpha.get("stage"),
            "dateSubmitted": alpha.get("dateSubmitted"),
            "expression": expr,
            "settings": alpha.get("settings") or {},
            "live_metrics": metrics,
            "live_check_summary": check_info,
            "live_check_raw": check,
            "economic_logic_ok": ok_econ,
            "economic_logic": econ_reason,
        }
    )

    reasons = []
    if alpha.get("status") != "UNSUBMITTED":
        reasons.append(f"status is {alpha.get('status')}, not UNSUBMITTED")
    if not check_info["strict_all_pass"]:
        reasons.append(f"live check is not strict 8/8: {check_info['pass_count']}/{check_info['check_count']}")
    if check_info.get("self_correlation") is not None and check_info["self_correlation"] > 0.7:
        reasons.append(f"self-correlation {check_info['self_correlation']} exceeds 0.7")
    if not ok_econ:
        reasons.append(econ_reason)

    record["posture"] = "eligible_record_only" if not reasons else "excluded"
    record["exclusion_reasons"] = reasons
    record["score"] = score(record) if record["posture"] == "eligible_record_only" else None
    return record


def render_md(payload: dict[str, Any]) -> str:
    eligible = payload["eligible_candidates"]
    inspected = payload["inspected_records"]
    lines = [
        "# 2026-05-23 Non-Inherited Reliable Candidate Record",
        "",
        "- Mode: RECORD ONLY. No alpha was submitted.",
        "- Scope: 2026-05-22 and 2026-05-23 local records.",
        "- Strict filter: exclude submitted alphas, exclude 2026-05-22 inherited variation IDs, require live UNSUBMITTED status, require live 8/8 official check, require self-correlation <= 0.7, require interpretable economic logic.",
        f"- Generated at UTC: `{payload['generated_at_utc']}`",
        f"- Already submitted excluded: `{', '.join(payload['submitted_alpha_ids'])}`",
        "",
        "## Eligible Candidates",
        "",
        "| Rank | Alpha | Source Day | Score | Sharpe | Fitness | Turnover | SubU | SelfCorr | Economic Logic | Expression |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    if eligible:
        for idx, item in enumerate(eligible, 1):
            metrics = item.get("live_metrics") or {}
            check = item.get("live_check_summary") or {}
            lines.append(
                f"| {idx} | `{item['alpha_id']}` | {item.get('source_day')} | {item.get('score')} | "
                f"{metrics.get('sharpe')} | {metrics.get('fitness')} | {metrics.get('turnover')} | "
                f"{check.get('sub_universe_sharpe')} | {check.get('self_correlation')} | "
                f"{item.get('economic_logic')} | `{item.get('expression')}` |"
            )
    else:
        lines.append("| - | - | - | - | - | - | - | - | - | - | - |")

    lines.extend(
        [
            "",
            "## Decision Notes",
            "",
            "- 2026-05-22 current 8-pass record had 21 unsubmitted strict 8-pass rows at creation time, but 19 were 2026-05-22 inherited variation IDs and the 2 non-inherited rows were price-only short-window reversals.",
            "- 2026-05-22 leverage/cash-burn report winners are not live-fetchable from the current API now (`404 Not found`), so they are not recorded as current reliable candidates.",
            "- 2026-05-23 independent operating-profitability S2 is the only source that currently produces a strict eligible non-inherited candidate after excluding already submitted `O0ovYJXg`.",
            "",
            "## Inspected Records",
            "",
            "| Alpha | Posture | Source Day | Live Check | SelfCorr | Reason |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for item in inspected:
        check = item.get("live_check_summary") or {}
        reason = "; ".join(item.get("exclusion_reasons") or [])
        if item.get("fetch_error"):
            reason = f"fetch_error={item['fetch_error']}"
        lines.append(
            f"| `{item['alpha_id']}` | {item.get('posture')} | {item.get('source_day')} | "
            f"{check.get('pass_count')}/{check.get('check_count')} | {check.get('self_correlation')} | {reason} |"
        )

    excluded = payload["pre_live_exclusions"]
    lines.extend(
        [
            "",
            "## Pre-Live Exclusion Summary",
            "",
            f"- Submitted excluded: {len(excluded['submitted'])}",
            f"- 2026-05-22 inherited variation rows excluded: {len(excluded['inherited_variation_22'])}",
            f"- 2026-05-22 non-inherited but price-only rows excluded: {len(excluded['price_only_non_inherited_22'])}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    inherited = variation_ids()
    candidates, pre_live_exclusions = candidate_universe(inherited)
    session = login()
    inspected = []
    for item in candidates:
        inspected.append(inspect_candidate(session, item))
        time.sleep(1)

    eligible = sorted(
        [item for item in inspected if item.get("posture") == "eligible_record_only"],
        key=lambda item: item.get("score") or 0,
        reverse=True,
    )
    payload = {
        "mode": "RECORD_ONLY_NO_SUBMIT",
        "generated_at_utc": now_utc(),
        "submitted_alpha_ids": sorted(SUBMITTED_ALPHA_IDS),
        "source_files": {
            "variation_results": str(VARIATION_RESULTS),
            "current_8pass_22": str(CURRENT_8PASS_22),
            "s2_results_23": str(S2_RESULTS_23),
            "overnight_results_23": str(OVERNIGHT_RESULTS_23),
        },
        "filter_policy": {
            "exclude_inherited_variation_ids": True,
            "require_live_status": "UNSUBMITTED",
            "require_live_official_check_8pass": True,
            "max_self_correlation": 0.7,
            "require_economic_logic": True,
            "no_submit": True,
        },
        "pre_live_exclusions": pre_live_exclusions,
        "inspected_records": inspected,
        "eligible_candidates": eligible,
    }
    write_json(OUTPUT_JSON, payload)
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(f"eligible={len(eligible)}")
    for item in eligible:
        print(
            f"{item['alpha_id']} score={item['score']} S={item['live_metrics'].get('sharpe')} "
            f"F={item['live_metrics'].get('fitness')} SC={item['live_check_summary'].get('self_correlation')}"
        )
    print(f"json={OUTPUT_JSON}")
    print(f"md={OUTPUT_MD}")


if __name__ == "__main__":
    main()

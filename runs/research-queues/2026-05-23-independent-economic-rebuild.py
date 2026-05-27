#!/usr/bin/env python3
"""Independent economic-logic rebuild batch.

This script runs simulations only. It never calls /submit.
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
OUT_DIR = PROJECT_ROOT / "runs/research-queues/2026-05-23-independent-economic-rebuild"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_JSON = OUT_DIR / "results.json"
REPORT_MD = OUT_DIR / "report.md"
API_BASE = "https://api.worldquantbrain.com"


BASE_SETTINGS = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "ON",
    "maxTrade": "OFF",
    "maxPosition": "OFF",
    "language": "FASTEXPR",
    "visualization": False,
    "startDate": "2019-01-01",
    "endDate": "2023-12-31",
}


CANDIDATES = [
    {
        "name": "op-income-history-industry-rank",
        "family": "operating_profitability",
        "thesis": "Companies whose operating income is strong relative to their own history may be undergoing persistent operating improvement.",
        "expression": "group_rank(ts_rank(operating_income,252), industry)",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "op-margin-revenue-ratio",
        "family": "operating_profitability",
        "thesis": "Operating income scaled by revenue approximates operating margin and should be compared within industry.",
        "expression": "group_rank(ts_rank(divide(operating_income, add(abs(revenue), 1)),252), industry)",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "op-income-change-zscore",
        "family": "operating_profitability",
        "thesis": "Sustained operating-income improvement can lag in prices when accounting updates arrive slowly.",
        "expression": "group_rank(ts_zscore(ts_delta(operating_income,252), 20), industry)",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "op-income-current-assets-ratio",
        "family": "operating_profitability",
        "thesis": "Operating income scaled by current assets proxies operating efficiency on working capital.",
        "expression": "group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), industry)",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fair-liability-history-negative",
        "family": "fair_value_liability_pressure",
        "thesis": "Rising level-1 fair-value liabilities can indicate balance-sheet pressure or future cash burden.",
        "expression": "reverse(group_rank(ts_rank(ts_backfill(fn_liab_fair_val_l1_a,252),252), industry))",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fair-liability-assets-ratio-negative",
        "family": "fair_value_liability_pressure",
        "thesis": "Fair-value liabilities scaled by current assets identify firms with heavier balance-sheet pressure.",
        "expression": "reverse(group_rank(ts_rank(divide(ts_backfill(fn_liab_fair_val_l1_a,252), add(abs(ts_backfill(assets_curr,252)),1)),252), industry))",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fair-liability-zscore-negative",
        "family": "fair_value_liability_pressure",
        "thesis": "A standardized fair-value-liability shock should be negative if it marks financial stress.",
        "expression": "reverse(group_rank(ts_zscore(winsorize(ts_backfill(fn_liab_fair_val_l1_a,252), std=4),120), industry))",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fair-liability-zscore-positive-control",
        "family": "fair_value_liability_pressure",
        "thesis": "Sign control for fair-value liabilities; keep only if the positive sign is empirically dominant.",
        "expression": "group_rank(ts_zscore(winsorize(ts_backfill(fn_liab_fair_val_l1_a,252), std=4),120), industry)",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fcf-max-slow-rank-63",
        "family": "cashflow_expectation",
        "thesis": "High analyst maximum FCF estimates may proxy optimistic cash-generation expectations.",
        "expression": "group_rank(ts_rank(ts_mean(free_cashflow_max,63),252), industry)",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fcf-max-slow-rank-126",
        "family": "cashflow_expectation",
        "thesis": "Slower FCF-estimate smoothing tests whether the idea survives lower turnover.",
        "expression": "group_rank(ts_rank(ts_mean(free_cashflow_max,126),252), industry)",
        "decay": 6,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fcfps-guidance-level",
        "family": "cashflow_guidance",
        "thesis": "Strong annual FCF per share guidance can indicate future cash-flow strength.",
        "expression": "group_rank(ts_zscore(ts_mean(anl4_fs_guidances_advanced_af_nd_fcfps_maxguidance,63),120), industry)",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fcfps-guidance-change",
        "family": "cashflow_guidance",
        "thesis": "An upward change in FCFPS guidance should matter more than a high stale level.",
        "expression": "group_rank(ts_delta(ts_mean(anl4_fs_guidances_advanced_af_nd_fcfps_maxguidance,20),63), industry)",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fcf-actual-vs-low-estimate",
        "family": "cashflow_surprise",
        "thesis": "Actual FCF exceeding low-side estimates can identify downside-risk relief or positive cash-flow surprise.",
        "expression": "group_rank(ts_zscore(anl4_fs_actuals_advanced_qf_nd_fcf_value,20) - ts_zscore(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,20), industry)",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fcf-actual-slow-rank",
        "family": "cashflow_surprise",
        "thesis": "Sustained actual FCF strength can be slower and less parameter-sensitive than 5-day zscores.",
        "expression": "group_rank(ts_rank(ts_mean(anl4_fs_actuals_advanced_qf_nd_fcf_value,63),252), industry)",
        "decay": 6,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "fcf-low-estimate-slow-rank",
        "family": "cashflow_surprise",
        "thesis": "High low-side FCF estimates may proxy reduced downside uncertainty in cash generation.",
        "expression": "group_rank(ts_rank(ts_mean(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,63),252), industry)",
        "decay": 6,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "current-assets-revenue-ratio",
        "family": "working_capital_quality",
        "thesis": "Current assets relative to revenue may proxy working-capital intensity; sign is uncertain and needs controls.",
        "expression": "group_rank(ts_rank(divide(assets_curr, add(abs(revenue),1)),252), industry)",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "current-assets-revenue-ratio-negative-control",
        "family": "working_capital_quality",
        "thesis": "Negative sign control: excessive current-asset intensity can indicate inefficient working capital or inventory/receivables buildup.",
        "expression": "reverse(group_rank(ts_rank(divide(assets_curr, add(abs(revenue),1)),252), industry))",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def settings_for(candidate: dict[str, Any]) -> dict[str, Any]:
    settings = dict(BASE_SETTINGS)
    settings["decay"] = candidate["decay"]
    settings["neutralization"] = candidate["neutralization"]
    return settings


def metric_dict(alpha: dict[str, Any]) -> dict[str, Any]:
    is_data = alpha.get("is") or {}
    checks = is_data.get("checks") or []
    sub_u = None
    for item in checks:
        if item.get("name") == "LOW_SUB_UNIVERSE_SHARPE":
            sub_u = item.get("value")
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
    }


def submit_simulation(session, candidate: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    payload = {
        "type": "REGULAR",
        "settings": settings_for(candidate),
        "regular": candidate["expression"],
    }
    response = session.post(f"{API_BASE}/simulations", json=payload, timeout=60)
    if response.status_code == 401:
        return None, {"status": "POST_AUTH_ERROR", "http_status": 401, "body": response.text[:500]}
    if response.status_code != 201:
        return None, {"status": "POST_FAILED", "http_status": response.status_code, "body": response.text[:1000]}
    return response.headers.get("Location"), None


def poll_simulation(session, location: str) -> dict[str, Any]:
    last_status = None
    for _ in range(180):
        response = session.get(location, timeout=60)
        if response.status_code == 401:
            return {"status": "POLL_AUTH_ERROR", "http_status": 401, "body": response.text[:500]}
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            time.sleep(float(retry_after))
            continue
        if response.status_code != 200:
            return {"status": "POLL_FAILED", "http_status": response.status_code, "body": response.text[:1000]}
        try:
            data = response.json()
        except Exception as exc:
            return {"status": "POLL_NON_JSON", "error": str(exc), "body": response.text[:500]}
        last_status = data.get("status")
        if last_status in ("COMPLETE", "WARNING"):
            return data
        if last_status in ("ERROR", "FAILED"):
            return data
        time.sleep(5)
    return {"status": "TIMEOUT", "last_status": last_status}


def fetch_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = session.get(f"{API_BASE}/alphas/{alpha_id}", timeout=60)
    response.raise_for_status()
    return response.json()


def run_check(session, alpha_id: str) -> dict[str, Any]:
    last_error = None
    for _ in range(40):
        response = session.get(f"{API_BASE}/alphas/{alpha_id}/check", timeout=60)
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            time.sleep(float(retry_after))
            continue
        if response.status_code != 200:
            last_error = {"http_status": response.status_code, "body": response.text[:500]}
            time.sleep(2)
            continue
        try:
            data = response.json()
        except Exception as exc:
            last_error = {"error": str(exc), "body": response.text[:500]}
            time.sleep(2)
            continue
        checks = data.get("is", {}).get("checks") or []
        non_pass = [item for item in checks if item.get("result") != "PASS"]
        return {
            "status": "CHECKED",
            "check_count": len(checks),
            "pass_count": sum(1 for item in checks if item.get("result") == "PASS"),
            "strict_all_pass": bool(checks) and not non_pass,
            "non_pass_checks": non_pass,
            "checks": checks,
            "raw": data,
        }
    return {"status": "CHECK_FAILED", "error": last_error}


def result_score(result: dict[str, Any]) -> float:
    metrics = result.get("metrics") or {}
    sharpe = float(metrics.get("sharpe") or 0)
    fitness = float(metrics.get("fitness") or 0)
    turnover = float(metrics.get("turnover") or 0)
    sub_u = metrics.get("subUniverseSharpe")
    score = sharpe * 12 + fitness * 18
    if sub_u is not None:
        score += float(sub_u) * 4
    if 0.01 <= turnover <= 0.3:
        score += 5
    elif turnover > 0.7:
        score -= 12
    if result.get("official_check", {}).get("strict_all_pass"):
        score += 30
    return round(score, 2)


def posture(result: dict[str, Any]) -> str:
    metrics = result.get("metrics") or {}
    sharpe = metrics.get("sharpe") or 0
    fitness = metrics.get("fitness") or 0
    turnover = metrics.get("turnover") or 0
    check = result.get("official_check") or {}
    if check.get("strict_all_pass"):
        return "candidate_record_only"
    if sharpe >= 1.1 and fitness >= 0.8 and turnover <= 0.7:
        return "near_candidate_check_next"
    if sharpe >= 0.8 and fitness >= 0.4 and turnover <= 0.8:
        return "rebuild_or_rescue"
    return "kill_or_hold"


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# 2026-05-23 Independent Economic Rebuild S0",
        "",
        "- Mode: SIMULATION ONLY. No alpha was submitted.",
        "- Objective: rebuild independent economic-logic candidates from non-inherited ideas.",
        f"- Candidates planned: {len(payload['candidates'])}",
        f"- Results recorded: {len(payload['results'])}",
        "",
        "## Strategy",
        "",
        "1. Exclude 2026-05-22 inherited-variation formulas and submitted families.",
        "2. Test mechanism-level expressions, not cosmetic parameter neighbors.",
        "3. Include sign controls for unclear balance-sheet directions.",
        "4. Promote only if real metrics and official check evidence justify it.",
        "",
        "## Results",
        "",
        "| Rank | Alpha | Family | Posture | Score | Sharpe | Fitness | Turnover | SubU | Check | Expression |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    ranked = sorted(payload["results"], key=result_score, reverse=True)
    for idx, item in enumerate(ranked, 1):
        metrics = item.get("metrics") or {}
        check = item.get("official_check") or {}
        check_text = (
            f"{check.get('pass_count')}/{check.get('check_count')}"
            if check.get("status") == "CHECKED"
            else check.get("status", "not_checked")
        )
        lines.append(
            f"| {idx} | {item.get('alpha_id')} | {item['family']} | {item.get('posture')} | {result_score(item)} | "
            f"{metrics.get('sharpe')} | {metrics.get('fitness')} | {metrics.get('turnover')} | "
            f"{metrics.get('subUniverseSharpe')} | {check_text} | `{item['expression']}` |"
        )
    lines.extend(["", "## Family Takeaways", ""])
    by_family: dict[str, list[dict[str, Any]]] = {}
    for item in payload["results"]:
        by_family.setdefault(item["family"], []).append(item)
    for family, items in sorted(by_family.items()):
        best = max(items, key=result_score)
        metrics = best.get("metrics") or {}
        lines.append(
            f"- `{family}` best `{best['name']}`: Sharpe={metrics.get('sharpe')}, "
            f"Fitness={metrics.get('fitness')}, Turnover={metrics.get('turnover')}, posture={best.get('posture')}."
        )
    lines.extend(["", "## Failed Or Error Records", ""])
    failed = [item for item in payload["results"] if item.get("status") != "COMPLETE"]
    if not failed:
        lines.append("- None.")
    for item in failed:
        lines.append(f"- `{item['name']}` status={item.get('status')} error={item.get('error')}")
    return "\n".join(lines) + "\n"


def main() -> None:
    session = login()
    if RESULTS_JSON.exists():
        payload = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
        payload["mode"] = "SIMULATION_ONLY_NO_SUBMIT"
        payload["candidates"] = CANDIDATES
        payload["resumed_at_utc"] = now_utc()
        payload.pop("finished_at_utc", None)
    else:
        payload: dict[str, Any] = {
            "mode": "SIMULATION_ONLY_NO_SUBMIT",
            "started_at_utc": now_utc(),
            "candidates": CANDIDATES,
            "results": [],
        }
    completed_names = {item.get("name") for item in payload.get("results", []) if item.get("name")}
    for idx, candidate in enumerate(CANDIDATES, 1):
        if candidate["name"] in completed_names:
            print(f"[{idx}/{len(CANDIDATES)}] {candidate['name']} already recorded; skipping", flush=True)
            continue
        print(f"[{idx}/{len(CANDIDATES)}] {candidate['name']}", flush=True)
        location, error = submit_simulation(session, candidate)
        if error and error.get("status") == "POST_AUTH_ERROR":
            session = login()
            location, error = submit_simulation(session, candidate)
        if error or not location:
            record = {**candidate, "status": (error or {}).get("status", "POST_FAILED"), "error": error}
            payload["results"].append(record)
            save_json(RESULTS_JSON, payload)
            print(f"  POST failed: {error}", flush=True)
            continue
        sim = poll_simulation(session, location)
        if sim.get("status") == "POLL_AUTH_ERROR":
            session = login()
            sim = poll_simulation(session, location)
        alpha_id = sim.get("alpha")
        record = {**candidate, "simulation_location": location, "simulation": sim, "status": sim.get("status")}
        if alpha_id:
            alpha = fetch_alpha(session, alpha_id)
            record["alpha_id"] = alpha_id
            record["alpha_detail"] = alpha
            record["metrics"] = metric_dict(alpha)
            metrics = record["metrics"]
            print(
                f"  {alpha_id} S={metrics.get('sharpe')} F={metrics.get('fitness')} TVR={metrics.get('turnover')}",
                flush=True,
            )
            if (metrics.get("sharpe") or 0) >= 1.1 and (metrics.get("fitness") or 0) >= 0.8 and (metrics.get("turnover") or 0) <= 0.7:
                record["official_check"] = run_check(session, alpha_id)
            else:
                record["official_check"] = {"status": "NOT_CHECKED_METRIC_FILTER"}
            record["posture"] = posture(record)
        else:
            print(f"  status={sim.get('status')} no alpha id", flush=True)
        payload["results"].append(record)
        payload["updated_at_utc"] = now_utc()
        save_json(RESULTS_JSON, payload)
        REPORT_MD.write_text(render_report(payload), encoding="utf-8")
        time.sleep(2)
    payload["finished_at_utc"] = now_utc()
    save_json(RESULTS_JSON, payload)
    REPORT_MD.write_text(render_report(payload), encoding="utf-8")
    print(f"results={RESULTS_JSON}")
    print(f"report={REPORT_MD}")


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

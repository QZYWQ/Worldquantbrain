#!/usr/bin/env python3
"""S1 rescue for independent operating profitability family.

Simulation only. No /submit call exists in this file.
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
OUT_DIR = PROJECT_ROOT / "runs/research-queues/2026-05-23-operating-profitability-s1-rescue"
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


BASE_EXPR = "group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), industry)"


CANDIDATES = [
    {
        "name": "op-assets-subindustry-group",
        "thesis": "Same operating-efficiency mechanism tested at a finer peer group to see whether industry ranking hides subindustry structure.",
        "expression": "group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), subindustry)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "name": "op-assets-decay3",
        "thesis": "Small decay rescue: test whether mild smoothing lifts Sharpe/Fitness without changing the economic mechanism.",
        "expression": BASE_EXPR,
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "op-assets-smoothed-fundamentals",
        "thesis": "Smooth numerator and scale variable before ranking to reduce reporting noise while preserving operating efficiency logic.",
        "expression": "group_rank(ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(assets_curr,63)), 1)),252), industry)",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "op-assets-composite-actual-fcf",
        "thesis": "Combine operating efficiency with actual FCF strength; both were near-positive but not submit-ready alone.",
        "expression": "group_rank(0.7 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252) + 0.3 * ts_rank(ts_mean(anl4_fs_actuals_advanced_qf_nd_fcf_value,63),252), industry)",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "op-assets-composite-fcf-max",
        "thesis": "Combine operating efficiency with slow analyst FCF expectation to test whether cash-flow expectation stabilizes the signal.",
        "expression": "group_rank(0.7 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252) + 0.3 * ts_rank(ts_mean(free_cashflow_max,126),252), industry)",
        "decay": 3,
        "neutralization": "INDUSTRY",
    },
    {
        "name": "op-assets-negative-control",
        "thesis": "Final-expression sign control. If this wins, the economic interpretation must be changed before further work.",
        "expression": "reverse(group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), industry))",
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


def post_simulation(session, candidate: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    response = session.post(
        f"{API_BASE}/simulations",
        json={"type": "REGULAR", "settings": settings_for(candidate), "regular": candidate["expression"]},
        timeout=60,
    )
    if response.status_code != 201:
        return None, {"status": "POST_FAILED", "http_status": response.status_code, "body": response.text[:1000]}
    return response.headers.get("Location"), None


def poll(session, location: str) -> dict[str, Any]:
    for _ in range(180):
        response = session.get(location, timeout=60)
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            time.sleep(float(retry_after))
            continue
        if response.status_code != 200:
            return {"status": "POLL_FAILED", "http_status": response.status_code, "body": response.text[:1000]}
        data = response.json()
        if data.get("status") in ("COMPLETE", "WARNING", "ERROR", "FAILED"):
            return data
        time.sleep(5)
    return {"status": "TIMEOUT"}


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


def posture(record: dict[str, Any]) -> str:
    metrics = record.get("metrics") or {}
    sharpe = metrics.get("sharpe") or 0
    fitness = metrics.get("fitness") or 0
    turnover = metrics.get("turnover") or 0
    check = record.get("official_check") or {}
    if check.get("strict_all_pass"):
        return "candidate_record_only"
    if sharpe >= 1.25 and fitness >= 1.0 and turnover <= 0.7:
        return "needs_official_check"
    if sharpe >= 1.1 and fitness >= 0.75 and turnover <= 0.7:
        return "near_candidate"
    if sharpe >= 0.8 and fitness >= 0.4 and turnover <= 0.8:
        return "rebuild_or_hold"
    return "kill_or_hold"


def score(record: dict[str, Any]) -> float:
    metrics = record.get("metrics") or {}
    val = (metrics.get("sharpe") or 0) * 12 + (metrics.get("fitness") or 0) * 18
    if metrics.get("subUniverseSharpe") is not None:
        val += metrics["subUniverseSharpe"] * 4
    if 0.01 <= (metrics.get("turnover") or 0) <= 0.3:
        val += 5
    if record.get("official_check", {}).get("strict_all_pass"):
        val += 30
    return round(val, 2)


def render_report(payload: dict[str, Any]) -> str:
    ranked = sorted(payload["results"], key=score, reverse=True)
    lines = [
        "# 2026-05-23 Operating Profitability S1 Rescue",
        "",
        "- Mode: SIMULATION ONLY. No alpha was submitted.",
        "- Parent: `vRdgb3dA` / `group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), industry)`.",
        "- Goal: lift near-candidate operating-efficiency signal without converting it into operator soup.",
        "",
        "| Rank | Alpha | Name | Posture | Score | Sharpe | Fitness | Turnover | SubU | Check | Expression |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for idx, item in enumerate(ranked, 1):
        metrics = item.get("metrics") or {}
        check = item.get("official_check") or {}
        check_text = (
            f"{check.get('pass_count')}/{check.get('check_count')}"
            if check.get("status") == "CHECKED"
            else check.get("status", "not_checked")
        )
        lines.append(
            f"| {idx} | {item.get('alpha_id')} | {item['name']} | {item.get('posture')} | {score(item)} | "
            f"{metrics.get('sharpe')} | {metrics.get('fitness')} | {metrics.get('turnover')} | "
            f"{metrics.get('subUniverseSharpe')} | {check_text} | `{item['expression']}` |"
        )
    lines.extend(["", "## Takeaway", ""])
    if ranked:
        best = ranked[0]
        metrics = best.get("metrics") or {}
        lines.append(
            f"- Best result: `{best['name']}` Sharpe={metrics.get('sharpe')}, "
            f"Fitness={metrics.get('fitness')}, Turnover={metrics.get('turnover')}, posture={best.get('posture')}."
        )
    return "\n".join(lines) + "\n"


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    session = login()
    payload: dict[str, Any] = {
        "mode": "SIMULATION_ONLY_NO_SUBMIT",
        "started_at_utc": now_utc(),
        "parent_alpha_id": "vRdgb3dA",
        "parent_expression": BASE_EXPR,
        "candidates": CANDIDATES,
        "results": [],
    }
    for idx, candidate in enumerate(CANDIDATES, 1):
        print(f"[{idx}/{len(CANDIDATES)}] {candidate['name']}", flush=True)
        location, error = post_simulation(session, candidate)
        if error or not location:
            record = {**candidate, "status": "POST_FAILED", "error": error}
            payload["results"].append(record)
            save_json(RESULTS_JSON, payload)
            continue
        sim = poll(session, location)
        alpha_id = sim.get("alpha")
        record = {**candidate, "simulation_location": location, "simulation": sim, "status": sim.get("status")}
        if alpha_id:
            alpha = fetch_alpha(session, alpha_id)
            record["alpha_id"] = alpha_id
            record["alpha_detail"] = alpha
            record["metrics"] = metric_dict(alpha)
            metrics = record["metrics"]
            print(f"  {alpha_id} S={metrics.get('sharpe')} F={metrics.get('fitness')} TVR={metrics.get('turnover')}", flush=True)
            if (metrics.get("sharpe") or 0) >= 1.25 and (metrics.get("fitness") or 0) >= 1.0 and (metrics.get("turnover") or 0) <= 0.7:
                record["official_check"] = run_check(session, alpha_id)
            else:
                record["official_check"] = {"status": "NOT_CHECKED_METRIC_FILTER"}
            record["posture"] = posture(record)
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


if __name__ == "__main__":
    main()

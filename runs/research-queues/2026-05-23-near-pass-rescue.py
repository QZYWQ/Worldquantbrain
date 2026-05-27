#!/usr/bin/env python3
"""Targeted rescue batch for non-inherited near-pass operating-profitability rows.

Simulation only. This script never calls /submit.
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
OUT_DIR = PROJECT_ROOT / "runs/research-queues/2026-05-23-near-pass-rescue"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_JSON = OUT_DIR / "results.json"
REPORT_MD = OUT_DIR / "report.md"
LOG_JSONL = OUT_DIR / "events.jsonl"
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

OP_RAW = "divide(operating_income, add(abs(assets_curr), 1))"
OP_S21 = "divide(ts_mean(operating_income,21), add(abs(ts_mean(assets_curr,21)), 1))"
OP_S42 = "divide(ts_mean(operating_income,42), add(abs(ts_mean(assets_curr,42)), 1))"
OP_S63 = "divide(ts_mean(operating_income,63), add(abs(ts_mean(assets_curr,63)), 1))"
OP_MARGIN = "divide(operating_income, add(abs(revenue), 1))"
FCF_MAX = "ts_rank(ts_mean(free_cashflow_max,126),252)"
FCF_ACTUAL = "ts_rank(ts_mean(anl4_fs_actuals_advanced_qf_nd_fcf_value,63),252)"
FCF_LOW = "ts_rank(ts_mean(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,63),252)"


def group_rank(expr: str) -> str:
    return f"group_rank({expr}, subindustry)"


def ts_rank(term: str, window: int) -> str:
    return f"ts_rank({term},{window})"


def add_candidate(
    rows: list[dict[str, Any]],
    name: str,
    parent: str,
    thesis: str,
    expression: str,
    decay: int = 0,
    neutralization: str = "SUBINDUSTRY",
) -> None:
    rows.append(
        {
            "name": name,
            "parent": parent,
            "thesis": thesis,
            "expression": expression,
            "decay": decay,
            "neutralization": neutralization,
        }
    )


def build_candidates() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    # KPkRjvGp rescue: keep strong Sharpe/SubU, try to lift Fitness with
    # confirmation or stability instead of just nudging the same window.
    op168 = ts_rank(OP_RAW, 168)
    add_candidate(rows, "kpkr-op168-fcfmax-80-20", "KPkRjvGp", "Operating efficiency with cash-flow expectation confirmation.", group_rank(f"0.8 * {op168} + 0.2 * {FCF_MAX}"), 3)
    add_candidate(rows, "kpkr-op168-fcfmax-75-25", "KPkRjvGp", "Moderate cash-flow confirmation while keeping operating efficiency dominant.", group_rank(f"0.75 * {op168} + 0.25 * {FCF_MAX}"), 3)
    add_candidate(rows, "kpkr-op168-fcfactual-85-15", "KPkRjvGp", "Small actual-cash-flow confirmation to avoid over-weighting noisy FCF data.", group_rank(f"0.85 * {op168} + 0.15 * {FCF_ACTUAL}"), 3)
    add_candidate(rows, "kpkr-op168-margin-75-25", "KPkRjvGp", "Combine current-asset efficiency with operating margin to change mechanism.", group_rank(f"0.75 * {op168} + 0.25 * {ts_rank(OP_MARGIN, 168)}"), 0)
    add_candidate(rows, "kpkr-op168-stability-85-15", "KPkRjvGp", "Reward profitability level while penalizing unstable operating efficiency.", group_rank(f"0.85 * {op168} - 0.15 * ts_rank(ts_std_dev({OP_RAW},126),252)"), 0)
    add_candidate(rows, "kpkr-op168-stability-80-20", "KPkRjvGp", "Stronger stability penalty for operating efficiency.", group_rank(f"0.8 * {op168} - 0.2 * ts_rank(ts_std_dev({OP_RAW},126),252)"), 0)

    # zqOzZojK rescue: current 50/50 FCF blend is close but short on Fitness.
    op252 = ts_rank(OP_RAW, 252)
    add_candidate(rows, "zqoz-fcfmax-60-40", "zqOzZojK", "Move from 50/50 toward operating-efficiency dominance.", group_rank(f"0.6 * {op252} + 0.4 * {FCF_MAX}"), 3)
    add_candidate(rows, "zqoz-fcfmax-65-35", "zqOzZojK", "Intermediate operating-efficiency dominance.", group_rank(f"0.65 * {op252} + 0.35 * {FCF_MAX}"), 3)
    add_candidate(rows, "zqoz-op168-fcfmax-70-30", "zqOzZojK", "Use the stronger 168-day operating-efficiency window with FCF confirmation.", group_rank(f"0.7 * {op168} + 0.3 * {FCF_MAX}"), 3)
    add_candidate(rows, "zqoz-op168-fcfmax-60-40", "zqOzZojK", "More balanced FCF confirmation with 168-day efficiency.", group_rank(f"0.6 * {op168} + 0.4 * {FCF_MAX}"), 3)

    # Actual FCF branch rescue: prior actual-FCF variants were too weak.
    op126 = ts_rank(OP_RAW, 126)
    add_candidate(rows, "actual-op126-actual-90-10", "MPkAO1Go/58MVb8JM", "Keep actual FCF as light confirmation only.", group_rank(f"0.9 * {op126} + 0.1 * {FCF_ACTUAL}"), 3)
    add_candidate(rows, "actual-op168-actual-90-10", "MPkAO1Go/58MVb8JM", "Light actual FCF confirmation on the stronger 168-day efficiency parent.", group_rank(f"0.9 * {op168} + 0.1 * {FCF_ACTUAL}"), 3)
    add_candidate(rows, "actual-op168-lowest-85-15", "MPkAO1Go/58MVb8JM", "Use low-side FCF estimates as downside-risk confirmation.", group_rank(f"0.85 * {op168} + 0.15 * {FCF_LOW}"), 3)

    # Smoothed-efficiency rescue: np3bww78 and newer 9qJQPNXV show useful Sharpe,
    # but smoothing can depress Fitness; try shorter smoothing and small confirmation.
    op_s63_r63 = ts_rank(OP_S63, 63)
    add_candidate(rows, "smooth63-r63-fcfmax-90-10", "np3bww78/9qJQPNXV", "Near-pass smoothed efficiency with light FCF expectation confirmation.", group_rank(f"0.9 * {op_s63_r63} + 0.1 * {FCF_MAX}"), 3)
    add_candidate(rows, "smooth63-r63-stability-90-10", "np3bww78/9qJQPNXV", "Smoothed efficiency with a light instability penalty.", group_rank(f"0.9 * {op_s63_r63} - 0.1 * ts_rank(ts_std_dev({OP_S63},126),252)"), 0)
    add_candidate(rows, "smooth42-r63", "np3bww78/9qJQPNXV", "Shorter accounting smoothing to recover Fitness while preserving lower turnover.", group_rank(ts_rank(OP_S42, 63)), 0)
    add_candidate(rows, "smooth42-r84", "np3bww78/9qJQPNXV", "Shorter smoothing with slightly longer rank window.", group_rank(ts_rank(OP_S42, 84)), 0)
    add_candidate(rows, "smooth21-r63", "np3bww78/9qJQPNXV", "Minimal smoothing to test whether 63-day smoothing over-damps the signal.", group_rank(ts_rank(OP_S21, 63)), 0)

    # One explicit final-expression sign control for the stability branch. If it
    # wins, the interpretation must change before more rescue budget is spent.
    add_candidate(rows, "stability-sign-control", "KPkRjvGp", "Final-expression sign control for the stability penalty branch.", f"reverse({group_rank(f'0.85 * {op168} - 0.15 * ts_rank(ts_std_dev({OP_RAW},126),252)')})", 0)
    return rows


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_event(record: dict[str, Any]) -> None:
    with LOG_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def settings_for(candidate: dict[str, Any]) -> dict[str, Any]:
    settings = dict(BASE_SETTINGS)
    settings["decay"] = candidate["decay"]
    settings["neutralization"] = candidate["neutralization"]
    return settings


def metric_dict(alpha: dict[str, Any]) -> dict[str, Any]:
    is_data = alpha.get("is") or {}
    checks = is_data.get("checks") or []
    return {
        "sharpe": is_data.get("sharpe"),
        "fitness": is_data.get("fitness"),
        "turnover": is_data.get("turnover"),
        "returns": is_data.get("returns"),
        "drawdown": is_data.get("drawdown"),
        "margin": is_data.get("margin"),
        "longCount": is_data.get("longCount"),
        "shortCount": is_data.get("shortCount"),
        "subUniverseSharpe": next((item.get("value") for item in checks if item.get("name") == "LOW_SUB_UNIVERSE_SHARPE"), None),
        "selfCorrelation": next((item.get("value") for item in checks if item.get("name") == "SELF_CORRELATION"), None),
    }


def run_check(session, alpha_id: str) -> dict[str, Any]:
    last_error = None
    for _ in range(45):
        response = session.get(f"{API_BASE}/alphas/{alpha_id}/check", timeout=60)
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            time.sleep(float(retry_after))
            continue
        if response.status_code != 200:
            last_error = {"http_status": response.status_code, "body": response.text[:500]}
            time.sleep(2)
            continue
        data = response.json()
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


def post_simulation(session, candidate: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    response = session.post(
        f"{API_BASE}/simulations",
        json={"type": "REGULAR", "settings": settings_for(candidate), "regular": candidate["expression"]},
        timeout=60,
    )
    if response.status_code == 401:
        return None, {"status": "POST_AUTH_ERROR", "http_status": 401, "body": response.text[:500]}
    if response.status_code != 201:
        return None, {"status": "POST_FAILED", "http_status": response.status_code, "body": response.text[:1000]}
    return response.headers.get("Location"), None


def poll(session, location: str) -> dict[str, Any]:
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
        data = response.json()
        last_status = data.get("status")
        if last_status in ("COMPLETE", "WARNING", "ERROR", "FAILED"):
            return data
        time.sleep(5)
    return {"status": "TIMEOUT", "last_status": last_status}


def fetch_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = session.get(f"{API_BASE}/alphas/{alpha_id}", timeout=60)
    response.raise_for_status()
    return response.json()


def posture(record: dict[str, Any]) -> str:
    metrics = record.get("metrics") or {}
    check = record.get("official_check") or {}
    sharpe = metrics.get("sharpe") or 0
    fitness = metrics.get("fitness") or 0
    turnover = metrics.get("turnover") or 0
    if check.get("strict_all_pass"):
        return "hard_8pass_record_only"
    if sharpe >= 1.25 and fitness >= 1.0 and turnover <= 0.7:
        return "metric_pass_check_failed_or_pending"
    if sharpe >= 1.25 and fitness >= 0.9 and turnover <= 0.7:
        return "near_pass_fitness_rescue"
    if sharpe >= 1.1 and fitness >= 0.75 and turnover <= 0.7:
        return "research_hold"
    return "kill_or_hold"


def score(record: dict[str, Any]) -> float:
    metrics = record.get("metrics") or {}
    check = record.get("official_check") or {}
    val = (metrics.get("sharpe") or 0) * 12 + (metrics.get("fitness") or 0) * 18
    sub_u = metrics.get("subUniverseSharpe")
    if sub_u is not None:
        val += sub_u * 4
    self_corr = None
    for item in check.get("checks") or []:
        if item.get("name") == "SELF_CORRELATION":
            self_corr = item.get("value")
            break
    if self_corr is not None:
        val -= self_corr * 8
    if check.get("strict_all_pass"):
        val += 35
    return round(val, 2)


def render_report(payload: dict[str, Any]) -> str:
    ranked = sorted(payload.get("results", []), key=score, reverse=True)
    lines = [
        "# 2026-05-23 Near-Pass Rescue",
        "",
        "- Mode: SIMULATION ONLY. No alpha was submitted.",
        "- Goal: rescue non-inherited operating-profitability near-pass rows by lifting Fitness or changing mechanism enough to survive correlation.",
        f"- Results recorded: {len(ranked)}",
        "",
        "| Rank | Alpha | Parent | Posture | Score | Sharpe | Fitness | Turnover | SubU | Check | Name | Expression |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
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
            f"| {idx} | {item.get('alpha_id')} | {item.get('parent')} | {item.get('posture')} | "
            f"{score(item)} | {metrics.get('sharpe')} | {metrics.get('fitness')} | "
            f"{metrics.get('turnover')} | {metrics.get('subUniverseSharpe')} | {check_text} | "
            f"{item.get('name')} | `{item.get('expression')}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    candidates = build_candidates()
    if RESULTS_JSON.exists():
        payload = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
        payload["resumed_at_utc"] = now_utc()
    else:
        payload = {
            "mode": "SIMULATION_ONLY_NO_SUBMIT",
            "started_at_utc": now_utc(),
            "candidates": candidates,
            "results": [],
        }
    completed = {item.get("name") for item in payload.get("results", []) if item.get("name")}
    session = login()
    for idx, candidate in enumerate(candidates, 1):
        if candidate["name"] in completed:
            print(f"[{idx}/{len(candidates)}] {candidate['name']} already done", flush=True)
            continue
        print(f"[{idx}/{len(candidates)}] {candidate['name']}", flush=True)
        append_event({"event": "start_candidate", "at": now_utc(), "candidate": candidate})
        location, error = post_simulation(session, candidate)
        if error and error.get("status") == "POST_AUTH_ERROR":
            session = login()
            location, error = post_simulation(session, candidate)
        if error or not location:
            record = {**candidate, "status": (error or {}).get("status", "POST_FAILED"), "error": error}
            payload["results"].append(record)
            save_json(RESULTS_JSON, payload)
            REPORT_MD.write_text(render_report(payload), encoding="utf-8")
            append_event({"event": "post_failed", "at": now_utc(), "record": record})
            time.sleep(2)
            continue
        sim = poll(session, location)
        if sim.get("status") == "POLL_AUTH_ERROR":
            session = login()
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
            if (metrics.get("sharpe") or 0) >= 1.1 and (metrics.get("fitness") or 0) >= 0.75 and (metrics.get("turnover") or 0) <= 0.7:
                record["official_check"] = run_check(session, alpha_id)
            else:
                record["official_check"] = {"status": "NOT_CHECKED_METRIC_FILTER"}
            record["posture"] = posture(record)
        else:
            print(f"  status={sim.get('status')} no alpha id", flush=True)
            record["official_check"] = {"status": "NOT_CHECKED_NO_ALPHA"}
            record["posture"] = "no_alpha"
        payload["results"].append(record)
        payload["updated_at_utc"] = now_utc()
        save_json(RESULTS_JSON, payload)
        REPORT_MD.write_text(render_report(payload), encoding="utf-8")
        append_event({"event": "record_result", "at": now_utc(), "alpha_id": alpha_id, "posture": record.get("posture")})
        time.sleep(3)
    payload["finished_at_utc"] = now_utc()
    save_json(RESULTS_JSON, payload)
    REPORT_MD.write_text(render_report(payload), encoding="utf-8")
    print(f"results={RESULTS_JSON}")
    print(f"report={REPORT_MD}")


if __name__ == "__main__":
    main()

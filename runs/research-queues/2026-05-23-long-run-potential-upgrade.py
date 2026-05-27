#!/usr/bin/env python3
"""Filter the interrupted long-run results and run a bounded upgrade batch.

Simulation/check only. This script never calls /submit.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, "/Users/zpdedn/Documents/github/worldquantAPI/user")
from machine_lib import login  # noqa: E402


PROJECT_ROOT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
LONG_RUN = PROJECT_ROOT / "runs/overnight-mining/2026-05-23-operating-profitability-24h/results.jsonl"
OUT_DIR = PROJECT_ROOT / "runs/research-queues/2026-05-23-long-run-potential-upgrade"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_JSON = OUT_DIR / "results.json"
SOURCE_JSON = OUT_DIR / "source-candidates-live-check.json"
REPORT_MD = OUT_DIR / "report.md"
EVENTS_JSONL = OUT_DIR / "events.jsonl"
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
OP_S63 = "divide(ts_mean(operating_income,63), add(abs(ts_mean(assets_curr,63)), 1))"
OP_MARGIN_RAW = "divide(operating_income, add(abs(revenue), 1))"
OP_MARGIN_S63 = "divide(ts_mean(operating_income,63), add(abs(ts_mean(revenue,63)), 1))"
FCF_MAX = "ts_rank(ts_mean(free_cashflow_max,126),252)"
FCF_LOW = "ts_rank(ts_mean(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,63),252)"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_event(record: dict[str, Any]) -> None:
    with EVENTS_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def ts_rank(expr: str, window: int) -> str:
    return f"ts_rank({expr},{window})"


def group_rank(expr: str, group: str = "subindustry") -> str:
    return f"group_rank({expr}, {group})"


def make_settings(decay: int = 0, neutralization: str = "SUBINDUSTRY") -> dict[str, Any]:
    settings = dict(BASE_SETTINGS)
    settings["decay"] = decay
    settings["neutralization"] = neutralization
    return settings


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


def build_upgrade_candidates() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    op126 = ts_rank(OP_RAW, 126)
    op168 = ts_rank(OP_RAW, 168)
    op_s63_r63 = ts_rank(OP_S63, 63)
    op_s63_r84 = ts_rank(OP_S63, 84)
    margin_s63_r378 = ts_rank(OP_MARGIN_S63, 378)
    margin_s63_r126 = ts_rank(OP_MARGIN_S63, 126)
    margin_s63_r84 = ts_rank(OP_MARGIN_S63, 84)
    margin_raw_r126 = ts_rank(OP_MARGIN_RAW, 126)

    add_candidate(rows, "op126-fcfmax-70-30", "N1Aoapdo/3qzWJ95O", "Reduce O0ovYJXg self-correlation with FCF expectation confirmation.", group_rank(f"0.7 * {op126} + 0.3 * {FCF_MAX}"), 3)
    add_candidate(rows, "op126-fcfmax-60-40", "N1Aoapdo/3qzWJ95O", "Stronger FCF confirmation while retaining operating-efficiency dominance.", group_rank(f"0.6 * {op126} + 0.4 * {FCF_MAX}"), 3)
    add_candidate(rows, "op126-fcflow-85-15", "N1Aoapdo/3qzWJ95O", "Use low-side FCF as downside-quality confirmation.", group_rank(f"0.85 * {op126} + 0.15 * {FCF_LOW}"), 3)
    add_candidate(rows, "op126-margin-75-25", "N1Aoapdo/3qzWJ95O", "Blend capital efficiency with operating margin to change mechanism.", group_rank(f"0.75 * {op126} + 0.25 * {margin_raw_r126}"), 0)

    add_candidate(rows, "smooth63-r63-fcfmax-85-15", "A1kdL3gX/9qJQPNXV", "Smooth profitability efficiency with light FCF confirmation.", group_rank(f"0.85 * {op_s63_r63} + 0.15 * {FCF_MAX}"), 3)
    add_candidate(rows, "smooth63-r84-fcfmax-85-15", "YPQdleoo/omVeAnZb", "Slightly slower smoothed efficiency with FCF confirmation.", group_rank(f"0.85 * {op_s63_r84} + 0.15 * {FCF_MAX}"), 3)
    add_candidate(rows, "smooth63-r63-fcflow-90-10", "A1kdL3gX/9qJQPNXV", "Smoothed efficiency with low-side FCF confirmation.", group_rank(f"0.9 * {op_s63_r63} + 0.1 * {FCF_LOW}"), 3)

    add_candidate(rows, "margin-s63-r378-fcfmax-70-30", "P0vE8GZL/qMgZPd12", "Lift slow operating-margin signal with FCF expectations.", group_rank(f"0.7 * {margin_s63_r378} + 0.3 * {FCF_MAX}"), 3)
    add_candidate(rows, "margin-s63-r378-op168-50-50", "P0vE8GZL/qMgZPd12", "Combine margin quality with working-capital efficiency.", group_rank(f"0.5 * {margin_s63_r378} + 0.5 * {op168}"), 0)
    add_candidate(rows, "margin-s63-r126-op168-50-50", "MPkAz8Ko/58MVqNp5", "Shorter margin rank plus working-capital efficiency.", group_rank(f"0.5 * {margin_s63_r126} + 0.5 * {op168}"), 0)
    add_candidate(rows, "margin-raw-r126-op168-50-50", "2rJkN9X5", "Current margin level plus working-capital efficiency.", group_rank(f"0.5 * {margin_raw_r126} + 0.5 * {op168}"), 0)
    add_candidate(rows, "margin-s63-r378-fcflow-85-15", "P0vE8GZL/qMgZPd12", "Slow margin signal with downside FCF confirmation.", group_rank(f"0.85 * {margin_s63_r378} + 0.15 * {FCF_LOW}"), 3)
    add_candidate(rows, "margin-s63-r84-op168-fcfmax", "78JVlV6L/9qJQanJ1", "Balanced margin, capital efficiency, and FCF confirmation.", group_rank(f"0.5 * {margin_s63_r84} + 0.3 * {op168} + 0.2 * {FCF_MAX}"), 3)
    return rows


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


def request_with_retries(session, method: str, url: str, **kwargs):
    last_error = None
    for _ in range(4):
        try:
            return session.request(method, url, **kwargs)
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(5)
    raise last_error


def fetch_alpha(session, alpha_id: str) -> dict[str, Any] | None:
    response = request_with_retries(session, "GET", f"{API_BASE}/alphas/{alpha_id}", timeout=60)
    if response.status_code != 200:
        return None
    return response.json()


def run_check(session, alpha_id: str) -> dict[str, Any]:
    last_error = None
    for _ in range(45):
        response = request_with_retries(session, "GET", f"{API_BASE}/alphas/{alpha_id}/check", timeout=60)
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
    response = request_with_retries(
        session,
        "POST",
        f"{API_BASE}/simulations",
        json={"type": "REGULAR", "settings": make_settings(candidate["decay"], candidate["neutralization"]), "regular": candidate["expression"]},
        timeout=60,
    )
    if response.status_code == 401:
        return None, {"status": "POST_AUTH_ERROR", "http_status": 401, "body": response.text[:500]}
    if response.status_code != 201:
        return None, {"status": "POST_FAILED", "http_status": response.status_code, "body": response.text[:1000]}
    return response.headers.get("Location"), None


def poll_simulation(session, location: str) -> dict[str, Any]:
    last_status = None
    for _ in range(180):
        response = request_with_retries(session, "GET", location, timeout=60)
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


def posture(record: dict[str, Any]) -> str:
    metrics = record.get("metrics") or {}
    check = record.get("official_check") or {}
    sharpe = metrics.get("sharpe") or 0
    fitness = metrics.get("fitness") or 0
    turnover = metrics.get("turnover") or 9
    if check.get("strict_all_pass"):
        return "hard_8pass_record_only"
    if sharpe >= 1.25 and fitness >= 1.0 and turnover <= 0.7:
        return "metric_pass_check_failed_or_pending"
    if sharpe >= 1.25 and fitness >= 0.9 and turnover <= 0.7:
        return "near_pass_fitness_rescue"
    if sharpe >= 1.1 and fitness >= 0.75 and turnover <= 0.7:
        return "research_hold"
    return "kill_or_hold"


def check_value(check: dict[str, Any], name: str) -> Any:
    return next((item.get("value") for item in check.get("checks") or [] if item.get("name") == name), None)


def score(record: dict[str, Any]) -> float:
    metrics = record.get("metrics") or {}
    check = record.get("official_check") or {}
    val = (metrics.get("sharpe") or 0) * 12 + (metrics.get("fitness") or 0) * 18
    sub_u = metrics.get("subUniverseSharpe")
    if sub_u is not None:
        val += sub_u * 4
    self_corr = check_value(check, "SELF_CORRELATION")
    if self_corr is not None:
        val -= self_corr * 8
    if check.get("strict_all_pass"):
        val += 35
    return round(val, 2)


def select_source_candidates(session) -> list[dict[str, Any]]:
    rows = load_jsonl(LONG_RUN)
    candidates = [
        row for row in rows
        if (row.get("metrics") or {}).get("sharpe", 0) >= 1.25
        and (row.get("metrics") or {}).get("fitness", 0) >= 0.8
        and (row.get("metrics") or {}).get("turnover", 9) <= 0.7
    ]
    candidates.sort(key=lambda row: ((row.get("metrics") or {}).get("fitness") or 0, (row.get("metrics") or {}).get("sharpe") or 0), reverse=True)
    checked: list[dict[str, Any]] = []
    for row in candidates[:24]:
        alpha_id = row.get("alpha_id")
        alpha = fetch_alpha(session, alpha_id) if alpha_id else None
        live_check = run_check(session, alpha_id) if alpha_id else {"status": "NO_ALPHA_ID"}
        checked.append(
            {
                "alpha_id": alpha_id,
                "name": row.get("name"),
                "posture": row.get("posture"),
                "branch": row.get("branch"),
                "expression": row.get("expression"),
                "local_metrics": row.get("metrics"),
                "live_metrics": metric_dict(alpha) if alpha else None,
                "live_status": (alpha or {}).get("status"),
                "live_stage": (alpha or {}).get("stage"),
                "live_check": live_check,
            }
        )
    save_json(SOURCE_JSON, {"mode": "LIVE_CHECK_LONG_RUN_CANDIDATES", "generated_at_utc": now_utc(), "source": str(LONG_RUN), "candidates": checked})
    return checked


def render_report(payload: dict[str, Any]) -> str:
    results = sorted(payload.get("results", []), key=score, reverse=True)
    source = payload.get("source_candidates", [])
    lines = [
        "# 2026-05-23 Long-Run Potential Upgrade",
        "",
        "- Mode: SIMULATION ONLY. No alpha was submitted.",
        "- Source: interrupted 24h operating-profitability run.",
        f"- Source candidates live-checked: {len(source)}",
        f"- Upgrade simulations recorded: {len(results)}",
        "",
        "## Upgrade Results",
        "",
        "| Rank | Alpha | Parent | Posture | Score | Sharpe | Fitness | Turnover | SubU | SelfCorr | Check | Name | Expression |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for idx, item in enumerate(results, 1):
        metrics = item.get("metrics") or {}
        check = item.get("official_check") or {}
        check_text = f"{check.get('pass_count')}/{check.get('check_count')}" if check.get("status") == "CHECKED" else check.get("status", "not_checked")
        lines.append(
            f"| {idx} | {item.get('alpha_id')} | {item.get('parent')} | {item.get('posture')} | "
            f"{score(item)} | {metrics.get('sharpe')} | {metrics.get('fitness')} | {metrics.get('turnover')} | "
            f"{metrics.get('subUniverseSharpe')} | {check_value(check, 'SELF_CORRELATION')} | {check_text} | "
            f"{item.get('name')} | `{item.get('expression')}` |"
        )
    lines.extend([
        "",
        "## Live-Checked Source Candidates",
        "",
        "| Rank | Alpha | Posture | Sharpe | Fitness | Turnover | Check | SelfCorr | Dominant Block | Name |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ])
    for idx, item in enumerate(source, 1):
        metrics = item.get("live_metrics") or item.get("local_metrics") or {}
        check = item.get("live_check") or {}
        non_pass = check.get("non_pass_checks") or []
        block = ",".join(entry.get("name", "") for entry in non_pass)
        check_text = f"{check.get('pass_count')}/{check.get('check_count')}" if check.get("status") == "CHECKED" else check.get("status", "not_checked")
        lines.append(
            f"| {idx} | {item.get('alpha_id')} | {item.get('posture')} | {metrics.get('sharpe')} | "
            f"{metrics.get('fitness')} | {metrics.get('turnover')} | {check_text} | {check_value(check, 'SELF_CORRELATION')} | {block} | {item.get('name')} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    session = login()
    source_candidates = select_source_candidates(session)
    candidates = build_upgrade_candidates()
    if RESULTS_JSON.exists():
        payload = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
        payload["resumed_at_utc"] = now_utc()
        payload["source_candidates"] = source_candidates
    else:
        payload = {
            "mode": "SIMULATION_ONLY_NO_SUBMIT",
            "started_at_utc": now_utc(),
            "source_candidates": source_candidates,
            "candidates": candidates,
            "results": [],
        }
    completed = {item.get("name") for item in payload.get("results", []) if item.get("name")}
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
            record["metrics"] = metric_dict(alpha or {})
            metrics = record["metrics"]
            print(f"  {alpha_id} S={metrics.get('sharpe')} F={metrics.get('fitness')} TVR={metrics.get('turnover')}", flush=True)
            if (metrics.get("sharpe") or 0) >= 1.1 and (metrics.get("fitness") or 0) >= 0.75 and (metrics.get("turnover") or 9) <= 0.7:
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

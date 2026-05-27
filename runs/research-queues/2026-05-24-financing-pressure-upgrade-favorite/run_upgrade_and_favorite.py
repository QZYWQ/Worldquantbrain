#!/usr/bin/env python3
"""
Targeted financing-pressure upgrade, final ranking, and favorite marking.

This wrapper uses the local WorldQuant API toolkit login/session from:
    /Users/zpdedn/Documents/github/worldquantAPI/user/machine_lib.py

It does not call any submit endpoint.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

USER_CODE_ROOT = Path("/Users/zpdedn/Documents/github/worldquantAPI/user")
sys.path.insert(0, str(USER_CODE_ROOT))

from machine_lib import login as brain_login  # noqa: E402


API_BASE = "https://api.worldquantbrain.com"
PROJECT_ROOT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
RUN_DIR = PROJECT_ROOT / "runs/research-queues/2026-05-24-financing-pressure-upgrade-favorite"
SOURCE_RUN_DIR = PROJECT_ROOT / "runs/overnight-mining/2026-05-23-financing-pressure-24h"
PREVIOUS_RELIABLE = PROJECT_ROOT / "runs/submission-memos/2026-05-23-non-inherited-reliable-candidates-record.json"
UPGRADE_POTENTIAL = SOURCE_RUN_DIR / "upgrade-potential-candidates.json"

EVENTS_JSONL = RUN_DIR / "events.jsonl"
RESULTS_JSON = RUN_DIR / "results.json"
FINAL_JSON = RUN_DIR / "final-ranked-favorite-candidates.json"
REPORT_MD = RUN_DIR / "report.md"

BASE_SETTINGS: dict[str, Any] = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "INDUSTRY",
    "truncation": 0.08,
    "pasteurization": "ON",
    "testPeriod": "P2Y",
    "unitHandling": "VERIFY",
    "nanHandling": "ON",
    "language": "FASTEXPR",
    "visualization": False,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def append_event(event: dict[str, Any]) -> None:
    event = {"at": utc_now(), **event}
    with EVENTS_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def settings(decay: int, neutralization: str) -> dict[str, Any]:
    out = dict(BASE_SETTINGS)
    out["decay"] = decay
    out["neutralization"] = neutralization
    return out


def clean(field: str) -> str:
    return f"winsorize(ts_backfill({field}, 252), std=4)"


def ratio(field: str, denom: str) -> str:
    return f"divide({clean(field)}, add(abs({clean(denom)}), 1))"


def pressure_change_expr(
    field: str,
    denom: str,
    smooth: int,
    delta: int,
    zwin: int,
    group: str,
) -> str:
    base = ratio(field, denom)
    inner = f"ts_zscore(ts_delta(ts_mean({base}, {smooth}), {delta}), {zwin})"
    return f"group_rank(reverse({inner}), {group})"


def pressure_level_expr(field: str, denom: str, rank_window: int, group: str) -> str:
    base = ratio(field, denom)
    inner = f"ts_rank({base}, {rank_window})"
    return f"group_rank(reverse({inner}), {group})"


def composite_expr(
    debt_field: str,
    obligation_field: str,
    debt_weight: float,
    group: str,
) -> str:
    obligation_weight = round(1.0 - debt_weight, 2)
    debt_part = f"reverse(ts_rank({ratio(debt_field, 'assets')}, 252))"
    obligation_part = f"reverse(ts_rank({ratio(obligation_field, 'assets')}, 252))"
    combo = f"{debt_weight:g} * {debt_part} + {obligation_weight:g} * {obligation_part}"
    return f"group_rank({combo}, {group})"


def candidate_key(candidate: dict[str, Any]) -> str:
    s = candidate.get("settings") or {}
    return json.dumps(
        {
            "expression": candidate.get("expression"),
            "decay": s.get("decay"),
            "neutralization": s.get("neutralization"),
            "nanHandling": s.get("nanHandling"),
        },
        sort_keys=True,
    )


def build_upgrade_candidates(existing_keys: set[str]) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []

    def add(name: str, expression: str, decay: int, neutralization: str, logic: str, source: str) -> None:
        group = "subindustry" if neutralization == "SUBINDUSTRY" else "industry"
        raw.append(
            {
                "name": name,
                "expression": expression,
                "settings": settings(decay, neutralization),
                "logic": logic,
                "source_parent": source,
                "group": group,
            }
        )

    # Priority 1: d5deq8bX fitness rescue. Change only one main lever per row.
    for smooth in (84, 126):
        add(
            f"d5-current-accrued-assets-s{smooth}-delta252-z120-industry-d3",
            pressure_change_expr("current_accrued_liabilities", "assets", smooth, 252, 120, "industry"),
            3,
            "INDUSTRY",
            "rising current accrued-liability pressure relative to assets",
            "d5deq8bX",
        )
    for zwin in (90, 150):
        add(
            f"d5-current-accrued-assets-s66-delta252-z{zwin}-industry-d3",
            pressure_change_expr("current_accrued_liabilities", "assets", 66, 252, zwin, "industry"),
            3,
            "INDUSTRY",
            "rising current accrued-liability pressure relative to assets",
            "d5deq8bX",
        )
    add(
        "d5-current-accrued-assets-s66-delta189-z120-industry-d3",
        pressure_change_expr("current_accrued_liabilities", "assets", 66, 189, 120, "industry"),
        3,
        "INDUSTRY",
        "rising current accrued-liability pressure relative to assets",
        "d5deq8bX",
    )
    add(
        "d5-current-accrued-assets-s66-delta252-z120-industry-d6",
        pressure_change_expr("current_accrued_liabilities", "assets", 66, 252, 120, "industry"),
        6,
        "INDUSTRY",
        "rising current accrued-liability pressure relative to assets",
        "d5deq8bX",
    )

    # Priority 2: debt-carrying-value denominator/time backups for E5kobRlG.
    for denom, rank_window, neut in (
        ("sales", 168, "INDUSTRY"),
        ("sales", 168, "SUBINDUSTRY"),
        ("assets", 168, "SUBINDUSTRY"),
        ("assets", 126, "INDUSTRY"),
    ):
        group = "subindustry" if neut == "SUBINDUSTRY" else "industry"
        add(
            f"debt-carrying-{denom}-r{rank_window}-{group}-d6-short",
            pressure_level_expr("debt_carrying_value", denom, rank_window, group),
            6,
            neut,
            "debt burden relative to operating scale or balance-sheet size",
            "E5kobRlG",
        )

    # Priority 3: true mechanism branches, not cosmetic copies.
    for weight in (0.7, 0.5):
        add(
            f"combo-debt-carrying-accrued-liabilities-w{weight:g}-industry-d6",
            composite_expr("debt_carrying_value", "accrued_liabilities_total", weight, "industry"),
            6,
            "INDUSTRY",
            "debt burden confirmed by accrued obligation pressure",
            "P0vjzQ6w",
        )
    add(
        "combo-debt-carrying-current-accrued-industry-d6",
        composite_expr("debt_carrying_value", "current_accrued_liabilities", 0.6, "industry"),
        6,
        "INDUSTRY",
        "debt burden confirmed by current obligation pressure",
        "P0vjzQ6w",
    )
    add(
        "combo-maturity-wall-current-accrued-industry-d6",
        composite_expr("debt_maturities_repayments_year2", "current_accrued_liabilities", 0.6, "industry"),
        6,
        "INDUSTRY",
        "near-term debt maturity wall confirmed by current obligations",
        "RRd09X0n",
    )

    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in raw:
        key = candidate_key(candidate)
        if key in seen or key in existing_keys:
            append_event({"event": "skip_duplicate_candidate", "name": candidate["name"]})
            continue
        seen.add(key)
        out.append(candidate)
    return out


def summarize_checks(alpha_id: str, checks: list[dict[str, Any]], status: str = "CHECKED") -> dict[str, Any]:
    pass_count = sum(1 for check in checks if check.get("result") == "PASS")
    non_pass = [
        {
            "name": check.get("name"),
            "result": check.get("result"),
            "value": check.get("value"),
            "limit": check.get("limit"),
        }
        for check in checks
        if check.get("result") != "PASS"
    ]
    return {
        "alpha_id": alpha_id,
        "status": status,
        "check_count": len(checks),
        "pass_count": pass_count,
        "strict_all_pass": len(checks) >= 8 and pass_count == len(checks),
        "self_correlation": next(
            (check.get("value") for check in checks if check.get("name") == "SELF_CORRELATION"),
            None,
        ),
        "sub_universe_sharpe": next(
            (check.get("value") for check in checks if check.get("name") == "LOW_SUB_UNIVERSE_SHARPE"),
            None,
        ),
        "non_pass_checks": non_pass,
        "checks": checks,
    }


class BrainClient:
    def __init__(self) -> None:
        self.session = brain_login()

    def reauth(self) -> None:
        append_event({"event": "reauth"})
        self.session = brain_login()

    def request(self, method: str, url: str, max_attempts: int = 8, **kwargs: Any):
        response = requests.Response()
        response.status_code = 599
        response._content = b""
        for attempt in range(max_attempts):
            try:
                response = self.session.request(method, url, timeout=60, **kwargs)
            except requests.RequestException as exc:
                wait = min(60, 5 * (attempt + 1))
                append_event(
                    {
                        "event": "request_exception",
                        "method": method,
                        "url": url,
                        "error": repr(exc),
                        "wait": wait,
                    }
                )
                time.sleep(wait)
                if attempt >= 1:
                    self.reauth()
                continue
            if response.status_code == 401:
                self.reauth()
                continue
            if "Retry-After" in response.headers:
                wait = float(response.headers["Retry-After"])
                append_event({"event": "retry_after", "method": method, "url": url, "wait": wait})
                time.sleep(wait)
                continue
            if response.status_code in (429, 500, 502, 503, 504):
                wait = min(180, 15 * (attempt + 1))
                append_event(
                    {
                        "event": "http_retry",
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "wait": wait,
                    }
                )
                time.sleep(wait)
                continue
            return response
        return response

    def fetch_alpha(self, alpha_id: str) -> dict[str, Any]:
        response = self.request("GET", f"{API_BASE}/alphas/{alpha_id}")
        item: dict[str, Any] = {"alpha_id": alpha_id, "status_code": response.status_code}
        if response.status_code != 200:
            item["body"] = response.text[:500]
            return item
        data = response.json()
        is_data = data.get("is") or {}
        checks = is_data.get("checks") or []
        subu = next((c.get("value") for c in checks if c.get("name") == "LOW_SUB_UNIVERSE_SHARPE"), None)
        self_corr = next((c.get("value") for c in checks if c.get("name") == "SELF_CORRELATION"), None)
        item.update(
            {
                "status": data.get("status"),
                "stage": data.get("stage"),
                "favorite": data.get("favorite"),
                "dateCreated": data.get("dateCreated"),
                "dateSubmitted": data.get("dateSubmitted"),
                "expression": (data.get("regular") or {}).get("code"),
                "settings": data.get("settings"),
                "metrics": {
                    "sharpe": is_data.get("sharpe"),
                    "fitness": is_data.get("fitness"),
                    "turnover": is_data.get("turnover"),
                    "returns": is_data.get("returns"),
                    "drawdown": is_data.get("drawdown"),
                    "margin": is_data.get("margin"),
                    "longCount": is_data.get("longCount"),
                    "shortCount": is_data.get("shortCount"),
                    "subuniverse_sharpe": subu,
                    "self_correlation": self_corr,
                },
                "cached_check": summarize_checks(alpha_id, checks, status="ALPHA_DETAIL_CHECK") if checks else None,
            }
        )
        return item

    def check_alpha(self, alpha_id: str) -> dict[str, Any]:
        last_body = ""
        for _ in range(2):
            response = self.request("GET", f"{API_BASE}/alphas/{alpha_id}/check", max_attempts=3)
            last_body = response.text or ""
            if response.status_code != 200:
                return {"alpha_id": alpha_id, "status": f"CHECK_FAIL_{response.status_code}", "body": last_body[:500]}
            if last_body.strip():
                data = response.json()
                checks = (data.get("is") or {}).get("checks") or []
                return summarize_checks(alpha_id, checks)
            time.sleep(5)
        return {"alpha_id": alpha_id, "status": "CHECK_EMPTY_BODY", "body": last_body[:500]}

    def simulate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        payload = {"type": "REGULAR", "settings": candidate["settings"], "regular": candidate["expression"]}
        post = self.request("POST", f"{API_BASE}/simulations", json=payload)
        if post.status_code != 201:
            return {
                "candidate": candidate,
                "simulation": {"status": f"POST_FAIL_{post.status_code}", "body": post.text[:500]},
            }
        progress_url = post.headers.get("Location")
        if not progress_url:
            return {"candidate": candidate, "simulation": {"status": "POST_NO_LOCATION", "body": post.text[:500]}}
        for _ in range(180):
            progress = self.request("GET", progress_url)
            data = progress.json() if progress.text.strip() else {}
            status = data.get("status")
            alpha_id = data.get("alpha")
            if status in ("COMPLETE", "WARNING") and alpha_id:
                return {
                    "candidate": candidate,
                    "simulation": {"status": status, "alpha_id": alpha_id},
                    "alpha": self.fetch_alpha(alpha_id),
                }
            if status == "ERROR":
                return {"candidate": candidate, "simulation": {"status": "ERROR", "progress": data}}
            time.sleep(5)
        return {"candidate": candidate, "simulation": {"status": "TIMEOUT"}}

    def mark_favorite(self, alpha_id: str) -> dict[str, Any]:
        before = self.fetch_alpha(alpha_id)
        if before.get("favorite") is True:
            return {"alpha_id": alpha_id, "status": "already_favorite", "verified_favorite": True}
        patch = self.request("PATCH", f"{API_BASE}/alphas/{alpha_id}", json={"favorite": True})
        after = self.fetch_alpha(alpha_id)
        return {
            "alpha_id": alpha_id,
            "status": "patched" if patch.status_code in (200, 201, 202) else f"PATCH_FAIL_{patch.status_code}",
            "patch_body": patch.text[:500],
            "verified_favorite": after.get("favorite") is True,
            "favorite_after": after.get("favorite"),
        }


def metric_pass(metrics: dict[str, Any]) -> bool:
    sharpe = metrics.get("sharpe")
    fitness = metrics.get("fitness")
    turnover = metrics.get("turnover")
    return sharpe is not None and fitness is not None and turnover is not None and sharpe >= 1.25 and fitness >= 1.0 and turnover <= 0.7


def score_candidate(candidate: dict[str, Any]) -> dict[str, float]:
    metrics = candidate.get("metrics") or {}
    check = candidate.get("check") or {}
    logic = (candidate.get("economic_logic") or "").lower()
    self_corr = check.get("self_correlation")
    sharpe = metrics.get("sharpe") or 0
    fitness = metrics.get("fitness") or 0
    turnover = metrics.get("turnover") or 1
    subu = check.get("sub_universe_sharpe") or metrics.get("subuniverse_sharpe") or 0

    economic = 82.0
    if "debt burden" in logic or "financing" in logic or "obligation" in logic or "maturity" in logic:
        economic = 95.0
    elif "operating profitability" in logic:
        economic = 92.0
    elif "operating efficiency" in logic and "fcf" in logic:
        economic = 88.0
    elif "downside fcf" in logic:
        economic = 86.0

    if self_corr is None:
        low_corr = 0.0
    elif self_corr <= 0.4:
        low_corr = 100.0
    elif self_corr <= 0.5:
        low_corr = 92.0
    elif self_corr <= 0.6:
        low_corr = 82.0
    elif self_corr <= 0.7:
        low_corr = 68.0
    else:
        low_corr = 0.0

    sharpe_score = min(100.0, 65.0 + max(0.0, sharpe - 1.25) * 45.0)
    fitness_score = min(100.0, 65.0 + max(0.0, fitness - 1.0) * 130.0)
    subu_score = min(100.0, 60.0 + max(0.0, subu - 0.7) * 45.0)
    turnover_score = 95.0 if 0.02 <= turnover <= 0.08 else 80.0
    metric = 0.35 * sharpe_score + 0.35 * fitness_score + 0.2 * subu_score + 0.1 * turnover_score
    non_inherited = 100.0
    final = 0.45 * economic + 0.25 * low_corr + 0.2 * metric + 0.1 * non_inherited
    return {
        "final_score": round(final, 2),
        "economic_logic_score": round(economic, 2),
        "low_selfcorr_score": round(low_corr, 2),
        "metric_score": round(metric, 2),
        "non_inherited_score": round(non_inherited, 2),
    }


def candidate_from_previous(row: dict[str, Any]) -> dict[str, Any]:
    metrics = row.get("live_metrics") or row.get("local_metrics") or {}
    check = row.get("live_check_summary") or {}
    return {
        "alpha_id": row.get("alpha_id"),
        "origin": row.get("origin"),
        "status": row.get("status") or "UNSUBMITTED",
        "expression": row.get("expression") or row.get("local_expression"),
        "economic_logic": row.get("economic_logic"),
        "metrics": {
            "sharpe": metrics.get("sharpe"),
            "fitness": metrics.get("fitness"),
            "turnover": metrics.get("turnover"),
            "returns": metrics.get("returns"),
            "drawdown": metrics.get("drawdown"),
            "margin": metrics.get("margin"),
            "subuniverse_sharpe": metrics.get("subUniverseSharpe") or check.get("sub_universe_sharpe"),
        },
        "check": check,
        "source_bucket": "previous_reliable_non_inherited",
    }


def candidate_from_financing(row: dict[str, Any]) -> dict[str, Any]:
    metrics = row.get("metrics") or {}
    check = row.get("live_check_summary") or {}
    return {
        "alpha_id": row.get("alpha_id"),
        "origin": "2026-05-23 financing-pressure 24h",
        "status": row.get("alpha_status") or "UNSUBMITTED",
        "expression": row.get("expression"),
        "economic_logic": row.get("economic_logic") or row.get("why_upgrade_potential"),
        "metrics": metrics,
        "check": check,
        "source_bucket": "financing_pressure",
    }


def build_report(data: dict[str, Any]) -> str:
    lines = [
        "# 2026-05-24 Upgrade And Favorite Record",
        "",
        "- Mode: simulation / official check / favorite only.",
        "- Submit endpoint: not used.",
        f"- Generated UTC: `{data['generated_at_utc']}`",
        f"- Upgrade candidates simulated: `{len(data['upgrade_results'])}`",
        f"- Upgrade hard 8-pass: `{len(data['upgrade_hard8'])}`",
        f"- Final favorite candidates: `{len(data['final_ranked'])}`",
        "",
        "## Upgrade Results",
        "",
        "| Alpha | Name | Sharpe | Fitness | Turnover | Check | SelfCorr | Logic |",
        "| --- | --- | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for row in data["upgrade_results"]:
        alpha = row.get("alpha") or {}
        sim = row.get("simulation") or {}
        chk = row.get("check") or {}
        metrics = alpha.get("metrics") or {}
        alpha_id = sim.get("alpha_id") or "-"
        check_text = "-"
        if chk:
            check_text = f"{chk.get('pass_count')}/{chk.get('check_count')}"
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | {} | {} |".format(
                alpha_id,
                row.get("candidate", {}).get("name"),
                metrics.get("sharpe"),
                metrics.get("fitness"),
                metrics.get("turnover"),
                check_text,
                chk.get("self_correlation"),
                row.get("candidate", {}).get("logic"),
            )
        )

    lines += [
        "",
        "## Final Ranked Favorite Candidates",
        "",
        "| Rank | Alpha | Final | Econ | LowCorr | Metric | Sharpe | Fitness | Turnover | SubU | SelfCorr | Favorite | Origin |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in data["final_ranked"]:
        metrics = row.get("metrics") or {}
        scores = row.get("scores") or {}
        check = row.get("check") or {}
        fav = row.get("favorite_result") or {}
        lines.append(
            "| {} | `{}` | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                row.get("rank"),
                row.get("alpha_id"),
                scores.get("final_score"),
                scores.get("economic_logic_score"),
                scores.get("low_selfcorr_score"),
                scores.get("metric_score"),
                metrics.get("sharpe"),
                metrics.get("fitness"),
                metrics.get("turnover"),
                check.get("sub_universe_sharpe") or metrics.get("subuniverse_sharpe"),
                check.get("self_correlation"),
                fav.get("verified_favorite"),
                row.get("origin"),
            )
        )
    lines += [
        "",
        "## Files",
        "",
        f"- Results JSON: `{RESULTS_JSON}`",
        f"- Final JSON: `{FINAL_JSON}`",
        f"- Events JSONL: `{EVENTS_JSONL}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    skip_sim = os.environ.get("WQB_SKIP_SIM", "0") == "1"
    skip_live_recheck = os.environ.get("WQB_SKIP_LIVE_RECHECK", "0") == "1"
    if not skip_sim:
        EVENTS_JSONL.write_text("", encoding="utf-8")
    append_event(
        {
            "event": "start",
            "user_code_root": str(USER_CODE_ROOT),
            "skip_sim": skip_sim,
            "skip_live_recheck": skip_live_recheck,
        }
    )

    long_run_rows = load_jsonl(SOURCE_RUN_DIR / "results.jsonl")
    existing_keys = {
        candidate_key({"expression": (row.get("candidate") or {}).get("expression"), "settings": (row.get("candidate") or {}).get("settings")})
        for row in long_run_rows
        if row.get("candidate")
    }
    upgrade_candidates = build_upgrade_candidates(existing_keys)
    append_event({"event": "upgrade_candidates_built", "count": len(upgrade_candidates)})

    client = BrainClient()
    upgrade_results: list[dict[str, Any]] = []
    if skip_sim:
        previous_partial = load_json(RESULTS_JSON, {})
        upgrade_results = previous_partial.get("upgrade_results", []) if isinstance(previous_partial, dict) else []
        append_event({"event": "skip_simulation_phase", "preserved_partial_results": len(upgrade_results)})
    else:
        for idx, candidate in enumerate(upgrade_candidates, 1):
            append_event({"event": "simulate_start", "index": idx, "count": len(upgrade_candidates), "name": candidate["name"]})
            row = client.simulate(candidate)
            alpha = row.get("alpha") or {}
            metrics = alpha.get("metrics") or {}
            if row.get("simulation", {}).get("alpha_id") and metric_pass(metrics):
                row["check"] = client.check_alpha(row["simulation"]["alpha_id"])
            upgrade_results.append(row)
            write_json(RESULTS_JSON, {"upgrade_candidates": upgrade_candidates, "upgrade_results": upgrade_results})
            append_event({"event": "simulate_finish", "index": idx, "result": row.get("simulation")})
            body = (row.get("simulation") or {}).get("body") or ""
            if "CONCURRENT_SIMULATION_LIMIT_EXCEEDED" in body:
                append_event({"event": "simulation_phase_stopped_for_concurrent_limit", "completed": len(upgrade_results)})
                break
            time.sleep(3)

    previous = load_json(PREVIOUS_RELIABLE, {})
    potential = load_json(UPGRADE_POTENTIAL, {})
    pool: dict[str, dict[str, Any]] = {}

    for row in previous.get("eligible_candidates", []):
        item = candidate_from_previous(row)
        if item.get("alpha_id"):
            pool[item["alpha_id"]] = item

    for row in potential.get("candidates", []):
        item = candidate_from_financing(row)
        if item.get("alpha_id") and (item.get("check") or {}).get("strict_all_pass"):
            pool[item["alpha_id"]] = item

    for row in upgrade_results:
        sim = row.get("simulation") or {}
        alpha = row.get("alpha") or {}
        check = row.get("check") or {}
        alpha_id = sim.get("alpha_id")
        if not alpha_id or not check.get("strict_all_pass"):
            continue
        pool[alpha_id] = {
            "alpha_id": alpha_id,
            "origin": "2026-05-24 financing-pressure targeted upgrade",
            "status": alpha.get("status") or "UNSUBMITTED",
            "expression": alpha.get("expression"),
            "economic_logic": (row.get("candidate") or {}).get("logic"),
            "metrics": alpha.get("metrics") or {},
            "check": check,
            "source_bucket": "new_upgrade",
        }

    # Fresh official checks before final ranking and favorite marking.
    refreshed: list[dict[str, Any]] = []
    for alpha_id, item in sorted(pool.items()):
        details = client.fetch_alpha(alpha_id)
        check = item.get("check") or {}
        if not skip_live_recheck:
            check = client.check_alpha(alpha_id)
        cached_check = details.get("cached_check")
        if not check.get("strict_all_pass") and cached_check and cached_check.get("strict_all_pass"):
            check = cached_check
        metrics = details.get("metrics") or item.get("metrics") or {}
        merged = {
            **item,
            "status": details.get("status") or item.get("status"),
            "favorite_before": details.get("favorite"),
            "metrics": metrics,
            "check": check,
        }
        refreshed.append(merged)
        append_event({"event": "refreshed_candidate", "alpha_id": alpha_id, "check": {k: check.get(k) for k in ("pass_count", "check_count", "self_correlation")}})

    final_ranked: list[dict[str, Any]] = []
    for item in refreshed:
        check = item.get("check") or {}
        self_corr = check.get("self_correlation")
        if item.get("status") != "UNSUBMITTED":
            continue
        if not check.get("strict_all_pass"):
            continue
        if self_corr is None or self_corr > 0.7:
            continue
        if not item.get("economic_logic"):
            continue
        item["scores"] = score_candidate(item)
        final_ranked.append(item)

    final_ranked.sort(key=lambda row: row["scores"]["final_score"], reverse=True)
    for idx, item in enumerate(final_ranked, 1):
        item["rank"] = idx

    for item in final_ranked:
        item["favorite_result"] = client.mark_favorite(item["alpha_id"])
        append_event({"event": "favorite_marked", "alpha_id": item["alpha_id"], "result": item["favorite_result"]})
        time.sleep(1)

    upgrade_hard8 = [
        row
        for row in upgrade_results
        if (row.get("check") or {}).get("strict_all_pass") is True
    ]
    output = {
        "generated_at_utc": utc_now(),
        "mode": "NO_SUBMIT_SIMULATE_CHECK_AND_FAVORITE_ONLY",
        "user_code_root": str(USER_CODE_ROOT),
        "source_files": {
            "previous_reliable": str(PREVIOUS_RELIABLE),
            "upgrade_potential": str(UPGRADE_POTENTIAL),
            "source_results": str(SOURCE_RUN_DIR / "results.jsonl"),
        },
        "upgrade_candidates": upgrade_candidates,
        "upgrade_results": upgrade_results,
        "upgrade_hard8": upgrade_hard8,
        "refreshed_pool": refreshed,
        "final_ranked": final_ranked,
    }
    write_json(RESULTS_JSON, output)
    write_json(FINAL_JSON, {"generated_at_utc": output["generated_at_utc"], "final_ranked": final_ranked})
    REPORT_MD.write_text(build_report(output), encoding="utf-8")
    append_event({"event": "finish", "final_count": len(final_ranked), "upgrade_hard8_count": len(upgrade_hard8)})
    print(json.dumps({"results": str(RESULTS_JSON), "final": str(FINAL_JSON), "report": str(REPORT_MD)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

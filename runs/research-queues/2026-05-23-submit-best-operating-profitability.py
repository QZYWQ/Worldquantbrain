#!/usr/bin/env python3
"""Submit the best operating-profitability 8-pass alpha and record evidence.

Single-target submission. User explicitly authorized one submit in the current
turn. This file submits only O0ovYJXg after a fresh live check.
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

SOURCE_MEMO = PROJECT_ROOT / "runs/submission-memos/2026-05-23-independent-operating-profitability-8pass-record.md"
SOURCE_RESULTS = PROJECT_ROOT / "runs/research-queues/2026-05-23-operating-profitability-s2-composite/results.json"
OVERNIGHT_STATE = PROJECT_ROOT / "runs/overnight-mining/2026-05-23-operating-profitability-24h/state.json"
OVERNIGHT_HARD = PROJECT_ROOT / "runs/overnight-mining/2026-05-23-operating-profitability-24h/hard_8pass_candidates.jsonl"

OUTPUT_JSON = PROJECT_ROOT / "runs/submission-memos/2026-05-23-submit-O0ovYJXg-operating-profitability.json"
OUTPUT_MD = PROJECT_ROOT / "runs/submission-memos/2026-05-23-submit-O0ovYJXg-operating-profitability.md"

SELECTED_ALPHA_ID = "O0ovYJXg"
SHORTLIST = ["O0ovYJXg", "j21QzK9E"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = session.get(f"{API_BASE}/alphas/{alpha_id}", timeout=60)
    response.raise_for_status()
    return response.json()


def get_check(session, alpha_id: str) -> dict[str, Any]:
    last_error: dict[str, Any] | None = None
    for attempt in range(1, 50):
        response = session.get(f"{API_BASE}/alphas/{alpha_id}/check", timeout=60)
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            time.sleep(float(retry_after))
            continue
        if response.status_code != 200:
            last_error = {
                "status": "CHECK_HTTP_ERROR",
                "status_code": response.status_code,
                "body": response.text[:500],
                "attempt": attempt,
            }
            time.sleep(2)
            continue
        try:
            return response.json()
        except Exception as exc:
            last_error = {
                "status": "CHECK_NON_JSON",
                "status_code": response.status_code,
                "body": response.text[:500],
                "attempt": attempt,
                "error": str(exc),
            }
            time.sleep(2)
    return {"is": {"checks": []}, "check_error": last_error or {"status": "CHECK_RETRY_LIMIT"}}


def submit_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = session.post(f"{API_BASE}/alphas/{alpha_id}/submit", timeout=60)
    return {
        "status_code": response.status_code,
        "accepted": response.status_code in (200, 201, 202),
        "text": response.text[:1000],
    }


def expression_of(alpha: dict[str, Any]) -> str:
    regular = alpha.get("regular")
    if isinstance(regular, dict):
        return str(regular.get("code") or "")
    return str(regular or "")


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


def check_summary(check_payload: dict[str, Any]) -> dict[str, Any]:
    checks = check_payload.get("is", {}).get("checks") or []
    non_pass = [item for item in checks if item.get("result") != "PASS"]
    return {
        "status": "CHECKED" if checks else "EMPTY_CHECK",
        "check_count": len(checks),
        "pass_count": sum(1 for item in checks if item.get("result") == "PASS"),
        "strict_all_pass": bool(checks) and not non_pass,
        "non_pass_checks": non_pass,
        "checks": checks,
    }


def load_s2_local_records() -> dict[str, dict[str, Any]]:
    payload = json.loads(SOURCE_RESULTS.read_text(encoding="utf-8"))
    return {item.get("alpha_id"): item for item in payload.get("results", []) if item.get("alpha_id")}


def overnight_snapshot() -> dict[str, Any]:
    state = None
    hard_count = 0
    if OVERNIGHT_STATE.exists():
        state = json.loads(OVERNIGHT_STATE.read_text(encoding="utf-8"))
    if OVERNIGHT_HARD.exists():
        hard_count = sum(1 for line in OVERNIGHT_HARD.read_text(encoding="utf-8").splitlines() if line.strip())
    return {
        "state": state,
        "hard_8pass_records_seen_at_decision": hard_count,
    }


def render_md(payload: dict[str, Any]) -> str:
    selected = payload["selected"]
    metrics = selected["live_metrics"]
    check = selected["live_check_summary"]
    submit = payload["submit_response"]
    post = payload["post_submit_alpha"]
    lines = [
        "# 2026-05-23 Submit O0ovYJXg Operating Profitability",
        "",
        "- Mode: SINGLE ALPHA SUBMISSION.",
        "- Authorization: user explicitly requested submitting one best candidate and recording it.",
        f"- Selected alpha: `{selected['alpha_id']}`",
        f"- Submit accepted: `{submit['accepted']}`; HTTP status `{submit['status_code']}`",
        f"- Post-submit status: `{post.get('status')}` / stage `{post.get('stage')}` / dateSubmitted `{post.get('dateSubmitted')}`",
        "",
        "## Selected Alpha",
        "",
        f"- Expression: `{selected['expression']}`",
        f"- Metrics: Sharpe={metrics.get('sharpe')}, Fitness={metrics.get('fitness')}, Turnover={metrics.get('turnover')}, SubU={metrics.get('subUniverseSharpe')}, SelfCorr={metrics.get('selfCorrelation')}",
        f"- Live official check: {check.get('pass_count')}/{check.get('check_count')} PASS; strict_all_pass={check.get('strict_all_pass')}",
        f"- Settings: region={selected['settings'].get('region')}, universe={selected['settings'].get('universe')}, delay={selected['settings'].get('delay')}, neutralization={selected['settings'].get('neutralization')}, decay={selected['settings'].get('decay')}",
        "",
        "## Rationale",
        "",
        "- Best current strict 8-pass candidate in the independent operating-profitability family.",
        "- Cleaner economic logic than the cash-flow composite sibling: within subindustry, rank operating income relative to current assets.",
        "- Better live metrics and lower self-correlation than `j21QzK9E` at the time of decision.",
        "- Current 24h targeted runner had no newer hard 8-pass record at decision time.",
        "",
        "## Live Shortlist",
        "",
        "| Alpha | Status Before Submit | Check | Sharpe | Fitness | Turnover | SubU | SelfCorr | Expression |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["shortlist"]:
        m = item["live_metrics"]
        c = item["live_check_summary"]
        lines.append(
            f"| {item['alpha_id']} | {item.get('status')} | {c.get('pass_count')}/{c.get('check_count')} | "
            f"{m.get('sharpe')} | {m.get('fitness')} | {m.get('turnover')} | {m.get('subUniverseSharpe')} | "
            f"{m.get('selfCorrelation')} | `{item['expression']}` |"
        )
    lines.extend(
        [
            "",
            "## Source Files",
            "",
            f"- Prior 8-pass memo: `{SOURCE_MEMO}`",
            f"- S2 result JSON: `{SOURCE_RESULTS}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    local_records = load_s2_local_records()
    if SELECTED_ALPHA_ID not in local_records:
        raise RuntimeError(f"{SELECTED_ALPHA_ID} not found in S2 local records.")

    session = login()
    shortlist: list[dict[str, Any]] = []
    for alpha_id in SHORTLIST:
        alpha = get_alpha(session, alpha_id)
        check = get_check(session, alpha_id)
        record = {
            "alpha_id": alpha_id,
            "status": alpha.get("status"),
            "stage": alpha.get("stage"),
            "dateSubmitted": alpha.get("dateSubmitted"),
            "expression": expression_of(alpha),
            "settings": alpha.get("settings") or {},
            "live_metrics": metrics_of(alpha),
            "live_check_summary": check_summary(check),
            "live_check_raw": check,
            "local_record": local_records.get(alpha_id),
        }
        shortlist.append(record)
        time.sleep(1)

    selected = next(item for item in shortlist if item["alpha_id"] == SELECTED_ALPHA_ID)
    if selected.get("status") != "UNSUBMITTED":
        raise RuntimeError(f"{SELECTED_ALPHA_ID} status is {selected.get('status')}, not UNSUBMITTED.")
    if not selected["live_check_summary"]["strict_all_pass"]:
        raise RuntimeError(
            f"{SELECTED_ALPHA_ID} live check did not pass: {selected['live_check_summary']['non_pass_checks']}"
        )

    submit_response = submit_alpha(session, SELECTED_ALPHA_ID)
    time.sleep(8)
    post_submit_alpha = get_alpha(session, SELECTED_ALPHA_ID)

    payload = {
        "mode": "SINGLE_ALPHA_SUBMISSION",
        "authorization": "User explicitly requested: 提交一个表现最好，经济逻辑最足的并进行记录",
        "timestamp_utc": now_utc(),
        "account_id": "CM54257",
        "source_memo": str(SOURCE_MEMO),
        "source_results": str(SOURCE_RESULTS),
        "selected_alpha_id": SELECTED_ALPHA_ID,
        "selection_policy": {
            "submit_count_limit": 1,
            "require_status_before_submit": "UNSUBMITTED",
            "require_live_official_check_all_pass": True,
            "prefer_best_metrics": True,
            "prefer_interpretable_economic_logic": True,
            "prefer_lower_self_correlation": True,
        },
        "overnight_snapshot_at_decision": overnight_snapshot(),
        "selected": selected,
        "shortlist": shortlist,
        "submit_response": submit_response,
        "post_submit_alpha": post_submit_alpha,
    }
    save_json(OUTPUT_JSON, payload)
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")

    print(f"selected={SELECTED_ALPHA_ID}")
    print(f"live_check={selected['live_check_summary']['pass_count']}/{selected['live_check_summary']['check_count']}")
    print(f"submit_status={submit_response['status_code']}")
    print(f"accepted={submit_response['accepted']}")
    print(f"post_status={post_submit_alpha.get('status')} stage={post_submit_alpha.get('stage')}")
    print(f"dateSubmitted={post_submit_alpha.get('dateSubmitted')}")
    print(f"json={OUTPUT_JSON}")
    print(f"md={OUTPUT_MD}")
    if not submit_response["accepted"]:
        raise RuntimeError(f"Submit was not accepted: {submit_response}")


if __name__ == "__main__":
    main()

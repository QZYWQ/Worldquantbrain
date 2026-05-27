#!/usr/bin/env python3
"""Submit one selected robust 8-pass alpha and record the evidence.

This script is intentionally single-target. The user authorized one submit.
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
INPUT_8PASS = PROJECT_ROOT / "runs/submission-memos/2026-05-22-current-8pass-record.json"
INPUT_SUBMITTED = PROJECT_ROOT / "runs/submission-memos/2026-05-22-current-submitted-alphas-record.json"
OUTPUT_JSON = PROJECT_ROOT / "runs/submission-memos/2026-05-23-submit-one-np3Jrqal.json"
OUTPUT_MD = PROJECT_ROOT / "runs/submission-memos/2026-05-23-submit-one-np3Jrqal.md"
API_BASE = "https://api.worldquantbrain.com"

# Chosen from the unsubmitted strict 8-pass set after excluding:
# - the already submitted earnings-yield sibling family,
# - short-window price-only reversals,
# - high-complexity operator stacks.
SELECTED_ALPHA_ID = "np3Jrqal"

# Small live-check shortlist used to document why the selected alpha is a better
# fit for this request than the raw metric winner or the most complex 8-pass row.
SHORTLIST = [
    "np3Jrqal",
    "9qJv2LJr",
    "omVpZnKm",
    "wpLmjx55",
    "E5k7R8ZK",
    "Wj9qxA0N",
    "RRd3zEPo",
    "d5dXKzmK",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checks_summary(check_payload: dict[str, Any]) -> dict[str, Any]:
    checks = check_payload.get("is", {}).get("checks", [])
    non_pass = [item for item in checks if item.get("result") != "PASS"]
    return {
        "check_count": len(checks),
        "pass_count": sum(1 for item in checks if item.get("result") == "PASS"),
        "all_pass": bool(checks) and not non_pass,
        "non_pass_checks": non_pass,
        "checks": checks,
    }


def expression_of(alpha: dict[str, Any]) -> str:
    regular = alpha.get("regular")
    if isinstance(regular, dict):
        return str(regular.get("code") or "")
    return str(regular or "")


def metrics_of(alpha: dict[str, Any]) -> dict[str, Any]:
    is_data = alpha.get("is", {}) or {}
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
                "error": "check_http_error",
                "status_code": response.status_code,
                "text": response.text[:500],
                "attempt": attempt,
            }
            time.sleep(2)
            continue
        try:
            return response.json()
        except Exception as exc:
            last_error = {
                "error": "check_non_json_response",
                "status_code": response.status_code,
                "text": response.text[:500],
                "attempt": attempt,
                "exception": str(exc),
            }
            time.sleep(2)
    return {"is": {"checks": []}, "check_error": last_error or {"error": "retry_limit_exceeded"}}


def submit_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = session.post(f"{API_BASE}/alphas/{alpha_id}/submit", timeout=60)
    return {
        "status_code": response.status_code,
        "text": response.text,
        "headers": dict(response.headers),
        "accepted": response.status_code in (200, 201, 202),
    }


def estimate_operator_count(expr: str) -> int:
    return sum(expr.count(token) for token in ("(", "rank", "ts_", "group_", "trade_when", "quantile", "winsorize"))


def selection_notes(record: dict[str, Any]) -> list[str]:
    alpha_id = record["alpha_id"]
    expr = record["expression"]
    notes: list[str] = []
    if alpha_id == "np3Jrqal":
        notes.append("selected: receivables-quality fundamental ratio with adjacent fnd6_rectr/fnd6_recd variants also passing")
        notes.append("selected: no live self-correlation value reported and low turnover")
        notes.append("selected: stronger sub-universe buffer than 9qJv2LJr while avoiding the tiny-denominator max() shape in omVpZnKm")
    if alpha_id == "wpLmjx55":
        notes.append("not selected: strongest metrics, but same earnings-yield family as already submitted A1kWl0LE")
        notes.append("not selected: recorded self-correlation to A1kWl0LE is high")
    if alpha_id == "d5dXKzmK":
        notes.append("not selected: strict 8-pass, but expression is a high-complexity sentiment/price-volume stack")
    if "close" in expr and "fnd" not in expr and "anl" not in expr:
        notes.append("not selected: price-only short-window reversal is more likely to be parameter fragile")
    if "fnd6_rectr" in expr and "fnd6_recd" in expr and alpha_id != "np3Jrqal":
        notes.append("same mechanism sibling: supports robustness of the selected receivables-quality ratio")
    return notes


def render_md(payload: dict[str, Any]) -> str:
    selected = payload["selected_record"]
    submit = payload["submit_response"]
    post = payload["post_submit_alpha"]
    metrics = selected["live_metrics"]
    check = selected["live_check_summary"]
    lines = [
        "# 2026-05-23 Submit One Robust 8-Pass Alpha",
        "",
        "- Mode: SINGLE ALPHA SUBMISSION.",
        "- Authorization: user explicitly requested one more submit from unsubmitted 8-pass candidates.",
        f"- Selected alpha: `{selected['alpha_id']}`",
        f"- Submitted: `{submit['accepted']}`; response status `{submit['status_code']}`",
        f"- Post-submit status: `{post.get('status')}` / stage `{post.get('stage')}` / dateSubmitted `{post.get('dateSubmitted')}`",
        "",
        "## Selected Alpha",
        "",
        f"- Expression: `{selected['expression']}`",
        f"- Metrics: Sharpe={metrics.get('sharpe')}, Fitness={metrics.get('fitness')}, Turnover={metrics.get('turnover')}",
        f"- Live check: pass_count={check.get('pass_count')}/{check.get('check_count')}, all_pass={check.get('all_pass')}",
        f"- Settings: region={selected['settings'].get('region')}, universe={selected['settings'].get('universe')}, delay={selected['settings'].get('delay')}, neutralization={selected['settings'].get('neutralization')}, decay={selected['settings'].get('decay')}",
        "",
        "## Selection Rationale",
        "",
        "- Chosen for interpretable fundamental logic: trade receivables relative to estimated doubtful receivables.",
        "- Chosen over the raw metric winner because the raw winner is a close sibling of an already submitted earnings-yield alpha.",
        "- Chosen over high-Sharpe price-only reversals and sentiment/price-volume stacks because those are more parameter-heavy or crowded.",
        "- Adjacent fnd6_rectr/fnd6_recd variants also passed, which is better evidence of mechanism stability than a single isolated parameter hit.",
        "",
        "## Live-Checked Shortlist",
        "",
        "| Alpha | Live Pass | Sharpe | Fitness | Turnover | Operator Estimate | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["shortlist_records"]:
        item_metrics = item.get("live_metrics", {})
        item_check = item.get("live_check_summary", {})
        lines.append(
            "| {alpha} | {passes}/{checks} | {sharpe} | {fitness} | {turnover} | {ops} | {notes} |".format(
                alpha=item["alpha_id"],
                passes=item_check.get("pass_count"),
                checks=item_check.get("check_count"),
                sharpe=item_metrics.get("sharpe"),
                fitness=item_metrics.get("fitness"),
                turnover=item_metrics.get("turnover"),
                ops=item["operator_count_estimate"],
                notes="; ".join(item.get("selection_notes") or []),
            )
        )
    lines.extend(
        [
            "",
            "## Submit Response",
            "",
            f"- Status code: `{submit['status_code']}`",
            f"- Response text length: `{len(submit.get('text') or '')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    source = load_json(INPUT_8PASS)
    submitted = load_json(INPUT_SUBMITTED)
    submitted_ids = {item.get("alpha_id") for item in submitted.get("records", [])}
    by_id = {item["alpha_id"]: item for item in source.get("records", [])}

    if SELECTED_ALPHA_ID in submitted_ids:
        raise RuntimeError(f"{SELECTED_ALPHA_ID} is already submitted in the local record")
    if SELECTED_ALPHA_ID not in by_id:
        raise RuntimeError(f"{SELECTED_ALPHA_ID} is not in the current 8-pass record")

    session = login()

    shortlist_records: list[dict[str, Any]] = []
    for alpha_id in SHORTLIST:
        local = by_id.get(alpha_id)
        if not local or alpha_id in submitted_ids:
            continue
        live_alpha = get_alpha(session, alpha_id)
        live_check = get_check(session, alpha_id)
        summary = checks_summary(live_check)
        expr = expression_of(live_alpha) or local.get("expression")
        shortlist_records.append(
            {
                "alpha_id": alpha_id,
                "local_metrics": local.get("metrics", {}),
                "live_metrics": metrics_of(live_alpha),
                "settings": live_alpha.get("settings", {}),
                "expression": expr,
                "status": live_alpha.get("status"),
                "stage": live_alpha.get("stage"),
                "dateSubmitted": live_alpha.get("dateSubmitted"),
                "live_check_summary": summary,
                "live_check_raw": live_check,
                "operator_count_estimate": estimate_operator_count(expr),
                "selection_notes": selection_notes({"alpha_id": alpha_id, "expression": expr}),
            }
        )
        time.sleep(1)

    selected_record = next((item for item in shortlist_records if item["alpha_id"] == SELECTED_ALPHA_ID), None)
    if selected_record is None:
        raise RuntimeError("selected alpha was not live-checked")
    if selected_record.get("status") != "UNSUBMITTED":
        raise RuntimeError(f"selected alpha status is {selected_record.get('status')}, not UNSUBMITTED")
    if not selected_record["live_check_summary"]["all_pass"]:
        raise RuntimeError(f"selected alpha did not pass live check: {selected_record['live_check_summary']['non_pass_checks']}")

    submit_response = submit_alpha(session, SELECTED_ALPHA_ID)
    time.sleep(5)
    post_submit_alpha = get_alpha(session, SELECTED_ALPHA_ID)

    payload = {
        "mode": "SINGLE_ALPHA_SUBMISSION",
        "authorization": "User explicitly requested: 从还没提交但是已经8pass的候选中再提交一个... 利用代码提交",
        "timestamp_utc": now_utc(),
        "source_8pass_record": str(INPUT_8PASS),
        "source_submitted_record": str(INPUT_SUBMITTED),
        "selected_alpha_id": SELECTED_ALPHA_ID,
        "selection_policy": {
            "exclude_already_submitted": True,
            "prefer_interpretable_economic_logic": True,
            "penalize_parameter_only_siblings": True,
            "penalize_operator_stacks": True,
            "require_live_official_check_all_pass": True,
            "submit_count_limit": 1,
        },
        "selected_record": selected_record,
        "shortlist_records": shortlist_records,
        "submit_response": submit_response,
        "post_submit_alpha": post_submit_alpha,
    }
    save_json(OUTPUT_JSON, payload)
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")

    print(f"selected={SELECTED_ALPHA_ID}")
    print(f"live_check={selected_record['live_check_summary']['pass_count']}/{selected_record['live_check_summary']['check_count']}")
    print(f"submit_status={submit_response['status_code']}")
    print(f"accepted={submit_response['accepted']}")
    print(f"json={OUTPUT_JSON}")
    print(f"md={OUTPUT_MD}")
    if not submit_response["accepted"]:
        raise RuntimeError(f"submit was not accepted: {submit_response}")


if __name__ == "__main__":
    main()

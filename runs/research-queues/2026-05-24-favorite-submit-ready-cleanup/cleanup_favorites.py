#!/usr/bin/env python3
"""Keep only live 8/8 unsubmitted candidates in the prior favorite list.

No submit endpoint is used. This script:
1. loads the previously marked favorite candidate IDs,
2. fetches live alpha details and official /check output,
3. removes favorite from candidates that are no longer submit-ready,
4. verifies favorite state after the patch.
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
RUN_DIR = PROJECT_ROOT / "runs/research-queues/2026-05-24-favorite-submit-ready-cleanup"
SOURCE_JSON = (
    PROJECT_ROOT
    / "runs/research-queues/2026-05-24-financing-pressure-upgrade-favorite/final-ranked-favorite-candidates.json"
)
POST_SUBMIT_JSON = PROJECT_ROOT / "runs/submission-memos/2026-05-24-submit-best-and-postcheck.json"
OUTPUT_JSON = RUN_DIR / "favorite-cleanup-results.json"
OUTPUT_MD = RUN_DIR / "favorite-cleanup-report.md"
API_BASE = "https://api.worldquantbrain.com"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def request_with_retries(session, method: str, url: str, **kwargs):
    last_response = None
    for attempt in range(1, 8):
        response = session.request(method, url, timeout=kwargs.pop("timeout", 60), **kwargs)
        last_response = response
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            time.sleep(float(retry_after))
            continue
        if response.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(90, attempt * 10))
            continue
        return response
    return last_response


def load_candidates() -> list[dict[str, Any]]:
    payload = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    ranked = payload.get("final_ranked")
    if not isinstance(ranked, list):
        raise RuntimeError(f"Missing final_ranked in {SOURCE_JSON}")
    return sorted(ranked, key=lambda item: int(item.get("rank") or 999999))


def expression_of(alpha: dict[str, Any]) -> str:
    regular = alpha.get("regular")
    if isinstance(regular, dict):
        return str(regular.get("code") or "")
    return str(regular or "")


def summarize_checks(checks: list[dict[str, Any]]) -> dict[str, Any]:
    non_pass = [item for item in checks if item.get("result") != "PASS"]
    by_name = {str(item.get("name")): item for item in checks if item.get("name")}
    self_corr = by_name.get("SELF_CORRELATION") or {}
    sub_u = by_name.get("LOW_SUB_UNIVERSE_SHARPE") or {}
    return {
        "check_count": len(checks),
        "pass_count": sum(1 for item in checks if item.get("result") == "PASS"),
        "strict_all_pass": bool(checks) and not non_pass,
        "non_pass_checks": non_pass,
        "self_correlation": self_corr.get("value"),
        "self_correlation_result": self_corr.get("result"),
        "self_correlation_limit": self_corr.get("limit"),
        "sub_universe_sharpe": sub_u.get("value"),
        "sub_universe_result": sub_u.get("result"),
        "checks": checks,
    }


def fetch_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = request_with_retries(session, "GET", f"{API_BASE}/alphas/{alpha_id}")
    if response is None:
        return {"alpha_id": alpha_id, "status_code": None, "error": "NO_RESPONSE"}
    if response.status_code != 200:
        return {
            "alpha_id": alpha_id,
            "status_code": response.status_code,
            "error": "FETCH_HTTP_ERROR",
            "body": response.text[:1000],
        }
    data = response.json()
    is_data = data.get("is") or {}
    checks = is_data.get("checks") or []
    return {
        "alpha_id": alpha_id,
        "status_code": response.status_code,
        "status": data.get("status"),
        "stage": data.get("stage"),
        "dateSubmitted": data.get("dateSubmitted"),
        "favorite": data.get("favorite"),
        "expression": expression_of(data),
        "metrics": {
            "sharpe": is_data.get("sharpe"),
            "fitness": is_data.get("fitness"),
            "turnover": is_data.get("turnover"),
            "returns": is_data.get("returns"),
            "drawdown": is_data.get("drawdown"),
            "margin": is_data.get("margin"),
            "longCount": is_data.get("longCount"),
            "shortCount": is_data.get("shortCount"),
        },
        "cached_check_summary": summarize_checks(checks),
        "raw": data,
    }


def check_alpha(session, alpha_id: str) -> dict[str, Any]:
    last_error: dict[str, Any] | None = None
    for attempt in range(1, 10):
        response = request_with_retries(session, "GET", f"{API_BASE}/alphas/{alpha_id}/check")
        if response is None:
            last_error = {"status": "NO_RESPONSE", "attempt": attempt}
            time.sleep(2)
            continue
        if response.status_code != 200:
            last_error = {
                "status": "CHECK_HTTP_ERROR",
                "status_code": response.status_code,
                "body": response.text[:1000],
                "attempt": attempt,
            }
            time.sleep(3)
            continue
        if not response.text.strip():
            last_error = {"status": "CHECK_EMPTY_BODY", "attempt": attempt}
            time.sleep(5)
            continue
        try:
            payload = response.json()
        except Exception as exc:
            last_error = {
                "status": "CHECK_NON_JSON",
                "status_code": response.status_code,
                "body": response.text[:1000],
                "attempt": attempt,
                "error": str(exc),
            }
            time.sleep(3)
            continue
        checks = (payload.get("is") or {}).get("checks") or []
        return {
            "alpha_id": alpha_id,
            "status": "CHECKED" if checks else "CHECK_NO_CHECKS",
            "summary": summarize_checks(checks),
            "raw": payload,
        }
    return {
        "alpha_id": alpha_id,
        "status": "CHECK_UNVERIFIED",
        "summary": summarize_checks([]),
        "error": last_error or {"status": "CHECK_RETRY_LIMIT"},
    }


def set_favorite(session, alpha_id: str, favorite: bool) -> dict[str, Any]:
    response = request_with_retries(session, "PATCH", f"{API_BASE}/alphas/{alpha_id}", json={"favorite": favorite})
    after = fetch_alpha(session, alpha_id)
    return {
        "alpha_id": alpha_id,
        "requested_favorite": favorite,
        "status_code": response.status_code if response is not None else None,
        "body": response.text[:1000] if response is not None else "",
        "favorite_after": after.get("favorite"),
        "verified": after.get("favorite") is favorite,
        "after_fetch_status_code": after.get("status_code"),
    }


def classify(alpha: dict[str, Any], check: dict[str, Any]) -> dict[str, Any]:
    summary = check.get("summary") or summarize_checks([])
    status = alpha.get("status")
    if alpha.get("status_code") != 200:
        category = "fetch_unverified"
        keep_favorite = True
        reason = "alpha detail fetch failed; leave favorite unchanged"
    elif status != "UNSUBMITTED":
        category = "not_submit_ready_status"
        keep_favorite = False
        reason = f"status is {status}, not UNSUBMITTED"
    elif check.get("status") != "CHECKED":
        category = "check_unverified"
        keep_favorite = True
        reason = "official check unavailable; leave favorite unchanged"
    elif summary.get("strict_all_pass"):
        category = "keep_submit_ready_8pass"
        keep_favorite = True
        reason = "UNSUBMITTED and official check is strict 8/8 PASS"
    else:
        names = ", ".join(str(item.get("name")) for item in summary.get("non_pass_checks") or [])
        category = "remove_not_8pass"
        keep_favorite = False
        reason = f"official check is not 8/8; non-pass checks: {names}"
    return {
        "category": category,
        "keep_favorite": keep_favorite,
        "reason": reason,
    }


def render_md(payload: dict[str, Any]) -> str:
    records = payload["records"]
    kept = [item for item in records if item["classification"]["category"] == "keep_submit_ready_8pass"]
    removed = [item for item in records if item["favorite_patch"] and item["favorite_patch"].get("verified")]
    unchanged_not_fav = [
        item
        for item in records
        if not item["classification"]["keep_favorite"] and item["live_alpha"].get("favorite") is not True
    ]
    unverified = [
        item
        for item in records
        if item["classification"]["category"] in {"fetch_unverified", "check_unverified"}
    ]
    lines = [
        "# 2026-05-24 Favorite Cleanup After Submission",
        "",
        "- Mode: OFFICIAL CHECK + FAVORITE CLEANUP ONLY.",
        "- Submit endpoint: not used.",
        f"- Source favorite candidate list: `{SOURCE_JSON}`",
        f"- Generated UTC: `{payload['timestamp_utc']}`",
        f"- Candidates checked: `{len(records)}`",
        f"- Favorite kept as submit-ready 8/8: `{len(kept)}`",
        f"- Favorite removed: `{len(removed)}`",
        f"- Already not favorite but not submit-ready: `{len(unchanged_not_fav)}`",
        f"- Unverified and left unchanged: `{len(unverified)}`",
        "",
        "## Current Submit-Ready Favorites",
        "",
        "| Rank | Alpha | Check | SelfCorr Result | SelfCorr | Sharpe | Fitness | Turnover | Logic |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in kept:
        check = item["live_check"]["summary"]
        metrics = item["live_alpha"].get("metrics") or {}
        lines.append(
            "| {rank} | `{alpha}` | {passes}/{checks} | {self_result} | {self_value} | {sharpe} | {fitness} | {turnover} | {logic} |".format(
                rank=item.get("rank"),
                alpha=item.get("alpha_id"),
                passes=check.get("pass_count"),
                checks=check.get("check_count"),
                self_result=check.get("self_correlation_result"),
                self_value=check.get("self_correlation"),
                sharpe=metrics.get("sharpe"),
                fitness=metrics.get("fitness"),
                turnover=metrics.get("turnover"),
                logic=item.get("economic_logic"),
            )
        )
    lines.extend(
        [
            "",
            "## Removed Or Not Kept",
            "",
            "| Rank | Alpha | Category | Favorite Before | Favorite After | Check | SelfCorr Result | SelfCorr | Reason |",
            "| ---: | --- | --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for item in records:
        if item["classification"]["keep_favorite"]:
            continue
        check = item["live_check"]["summary"]
        patch = item.get("favorite_patch") or {}
        lines.append(
            "| {rank} | `{alpha}` | {category} | {before} | {after} | {passes}/{checks} | {self_result} | {self_value} | {reason} |".format(
                rank=item.get("rank"),
                alpha=item.get("alpha_id"),
                category=item["classification"].get("category"),
                before=item["live_alpha"].get("favorite"),
                after=patch.get("favorite_after", item["live_alpha"].get("favorite")),
                passes=check.get("pass_count"),
                checks=check.get("check_count"),
                self_result=check.get("self_correlation_result"),
                self_value=check.get("self_correlation"),
                reason=item["classification"].get("reason"),
            )
        )
    if unverified:
        lines.extend(
            [
                "",
                "## Unverified",
                "",
                "These were left unchanged because removing favorite without official check evidence would be unsafe.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- JSON evidence: `{OUTPUT_JSON}`",
            f"- Markdown report: `{OUTPUT_MD}`",
            f"- Script: `{RUN_DIR / 'cleanup_favorites.py'}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    session = login()
    records: list[dict[str, Any]] = []
    for candidate in load_candidates():
        alpha_id = str(candidate["alpha_id"])
        alpha = fetch_alpha(session, alpha_id)
        check = check_alpha(session, alpha_id)
        classification = classify(alpha, check)
        favorite_patch = None
        if not classification["keep_favorite"] and alpha.get("favorite") is True:
            favorite_patch = set_favorite(session, alpha_id, False)
        records.append(
            {
                "rank": candidate.get("rank"),
                "alpha_id": alpha_id,
                "origin": candidate.get("origin"),
                "economic_logic": candidate.get("economic_logic"),
                "source_expression": candidate.get("expression"),
                "live_alpha": alpha,
                "live_check": check,
                "classification": classification,
                "favorite_patch": favorite_patch,
            }
        )
        print(
            f"{alpha_id} {classification['category']} favorite_before={alpha.get('favorite')} "
            f"patch={favorite_patch.get('verified') if favorite_patch else None}"
        )
        time.sleep(1)

    payload = {
        "mode": "OFFICIAL_CHECK_AND_FAVORITE_CLEANUP_ONLY",
        "timestamp_utc": utc_now(),
        "account_id": "CM54257",
        "user_code_root": "/Users/zpdedn/Documents/github/worldquantAPI/user",
        "source_json": str(SOURCE_JSON),
        "post_submit_json": str(POST_SUBMIT_JSON),
        "records": records,
        "summary": {
            "checked": len(records),
            "kept_submit_ready_8pass": sum(
                1 for item in records if item["classification"]["category"] == "keep_submit_ready_8pass"
            ),
            "removed_favorite": sum(
                1 for item in records if item.get("favorite_patch") and item["favorite_patch"].get("verified")
            ),
            "unverified_left_unchanged": sum(
                1
                for item in records
                if item["classification"]["category"] in {"fetch_unverified", "check_unverified"}
            ),
        },
    }
    dump_json(OUTPUT_JSON, payload)
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"json={OUTPUT_JSON}")
    print(f"md={OUTPUT_MD}")


if __name__ == "__main__":
    main()

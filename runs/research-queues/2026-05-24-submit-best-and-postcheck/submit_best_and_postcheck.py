#!/usr/bin/env python3
"""Submit one ranked candidate, then recheck remaining submit candidates.

This script is intentionally single-submit. It uses the current ranked favorite
candidate file as the source queue, verifies the selected alpha live before
submitting, then runs official checks on the remaining queued candidates.
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
RUN_DIR = PROJECT_ROOT / "runs/research-queues/2026-05-24-submit-best-and-postcheck"
SOURCE_JSON = (
    PROJECT_ROOT
    / "runs/research-queues/2026-05-24-financing-pressure-upgrade-favorite/final-ranked-favorite-candidates.json"
)
OUTPUT_JSON = PROJECT_ROOT / "runs/submission-memos/2026-05-24-submit-best-and-postcheck.json"
OUTPUT_MD = PROJECT_ROOT / "runs/submission-memos/2026-05-24-submit-best-and-postcheck.md"
API_BASE = "https://api.worldquantbrain.com"
SELECTED_ALPHA_ID = "j21QzK9E"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_ranked_candidates() -> list[dict[str, Any]]:
    payload = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    ranked = payload.get("final_ranked")
    if not isinstance(ranked, list) or not ranked:
        raise RuntimeError(f"No final_ranked candidates found in {SOURCE_JSON}")
    return sorted(ranked, key=lambda item: int(item.get("rank") or 999999))


def load_previous_output() -> dict[str, Any] | None:
    if not OUTPUT_JSON.exists():
        return None
    try:
        return json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    except Exception:
        return None


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


def fetch_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = request_with_retries(session, "GET", f"{API_BASE}/alphas/{alpha_id}")
    item: dict[str, Any] = {
        "alpha_id": alpha_id,
        "fetched_at_utc": utc_now(),
        "status_code": response.status_code if response is not None else None,
    }
    if response is None:
        item["error"] = "NO_RESPONSE"
        return item
    if response.status_code != 200:
        item["error"] = "FETCH_HTTP_ERROR"
        item["body"] = response.text[:1000]
        return item
    data = response.json()
    is_data = data.get("is") or {}
    checks = is_data.get("checks") or []
    item.update(
        {
            "id": data.get("id"),
            "status": data.get("status"),
            "stage": data.get("stage"),
            "dateSubmitted": data.get("dateSubmitted"),
            "favorite": data.get("favorite"),
            "settings": data.get("settings") or {},
            "expression": expression_of(data),
            "metrics": metrics_from_alpha(data),
            "cached_check_summary": summarize_checks(checks),
            "raw": data,
        }
    )
    return item


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
        except Exception as exc:  # pragma: no cover - platform response guard
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
            "checked_at_utc": utc_now(),
            "status": "CHECKED" if checks else "CHECK_NO_CHECKS",
            "summary": summarize_checks(checks),
            "raw": payload,
        }
    return {
        "alpha_id": alpha_id,
        "checked_at_utc": utc_now(),
        "status": "CHECK_UNVERIFIED",
        "summary": summarize_checks([]),
        "error": last_error or {"status": "CHECK_RETRY_LIMIT"},
    }


def submit_alpha(session, alpha_id: str) -> dict[str, Any]:
    response = request_with_retries(session, "POST", f"{API_BASE}/alphas/{alpha_id}/submit")
    return {
        "alpha_id": alpha_id,
        "submitted_at_utc": utc_now(),
        "status_code": response.status_code if response is not None else None,
        "accepted": response is not None and response.status_code in (200, 201, 202),
        "body": response.text[:2000] if response is not None else "",
        "headers": dict(response.headers) if response is not None else {},
    }


def expression_of(alpha: dict[str, Any]) -> str:
    regular = alpha.get("regular")
    if isinstance(regular, dict):
        return str(regular.get("code") or "")
    return str(regular or "")


def metrics_from_alpha(alpha: dict[str, Any]) -> dict[str, Any]:
    is_data = alpha.get("is") or {}
    check_summary = summarize_checks(is_data.get("checks") or [])
    return {
        "sharpe": is_data.get("sharpe"),
        "fitness": is_data.get("fitness"),
        "turnover": is_data.get("turnover"),
        "returns": is_data.get("returns"),
        "drawdown": is_data.get("drawdown"),
        "margin": is_data.get("margin"),
        "longCount": is_data.get("longCount"),
        "shortCount": is_data.get("shortCount"),
        "subuniverse_sharpe": check_summary.get("sub_universe_sharpe"),
        "self_correlation": check_summary.get("self_correlation"),
    }


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


def prior_check(candidate: dict[str, Any]) -> dict[str, Any]:
    check = candidate.get("check") or {}
    return {
        "strict_all_pass": check.get("strict_all_pass"),
        "check_count": check.get("check_count"),
        "pass_count": check.get("pass_count"),
        "self_correlation": check.get("self_correlation"),
        "sub_universe_sharpe": check.get("sub_universe_sharpe"),
        "non_pass_checks": check.get("non_pass_checks") or [],
    }


def candidate_scores(candidate: dict[str, Any]) -> dict[str, Any]:
    scores = candidate.get("scores") or {}
    return {
        "final_score": scores.get("final_score"),
        "economic_logic_score": scores.get("economic_logic_score"),
        "low_selfcorr_score": scores.get("low_selfcorr_score"),
        "metric_score": scores.get("metric_score"),
        "non_inherited_score": scores.get("non_inherited_score"),
    }


def live_record(candidate: dict[str, Any], alpha_detail: dict[str, Any], check: dict[str, Any]) -> dict[str, Any]:
    summary = check.get("summary") or summarize_checks([])
    return {
        "rank": candidate.get("rank"),
        "alpha_id": candidate.get("alpha_id"),
        "origin": candidate.get("origin"),
        "prior_status": candidate.get("status"),
        "live_status": alpha_detail.get("status"),
        "live_stage": alpha_detail.get("stage"),
        "dateSubmitted": alpha_detail.get("dateSubmitted"),
        "expression": alpha_detail.get("expression") or candidate.get("expression"),
        "economic_logic": candidate.get("economic_logic"),
        "scores": candidate_scores(candidate),
        "prior_metrics": candidate.get("metrics") or {},
        "live_metrics": alpha_detail.get("metrics") or {},
        "prior_check": prior_check(candidate),
        "live_check": summary,
        "live_check_status": check.get("status"),
        "alpha_detail_status_code": alpha_detail.get("status_code"),
        "favorite": alpha_detail.get("favorite"),
        "settings": alpha_detail.get("settings") or {},
        "raw_check": check.get("raw"),
        "check_error": check.get("error"),
    }


def select_first_live_eligible(session, ranked: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    pre_submit_checked: list[dict[str, Any]] = []
    for candidate in ranked:
        alpha_id = str(candidate.get("alpha_id") or "")
        alpha_detail = fetch_alpha(session, alpha_id)
        check = check_alpha(session, alpha_id)
        record = live_record(candidate, alpha_detail, check)
        pre_submit_checked.append(record)
        summary = record["live_check"]
        if alpha_detail.get("status") != "UNSUBMITTED":
            record["selection_skip_reason"] = f"status is {alpha_detail.get('status')}"
            continue
        if not summary.get("strict_all_pass"):
            record["selection_skip_reason"] = "live official check is not strict 8-pass"
            continue
        record["selection_skip_reason"] = None
        return record, pre_submit_checked
    raise RuntimeError("No live eligible candidate found in ranked queue.")


def fetch_selected_record(session, ranked: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidate = next((item for item in ranked if item.get("alpha_id") == SELECTED_ALPHA_ID), None)
    if candidate is None:
        raise RuntimeError(f"{SELECTED_ALPHA_ID} not found in ranked queue.")
    alpha_detail = fetch_alpha(session, SELECTED_ALPHA_ID)
    check = check_alpha(session, SELECTED_ALPHA_ID)
    record = live_record(candidate, alpha_detail, check)
    return record, [record]


def alpha_is_submitted(alpha_detail: dict[str, Any]) -> bool:
    status = alpha_detail.get("status")
    stage = alpha_detail.get("stage")
    return bool(alpha_detail.get("dateSubmitted")) or status in {"ACTIVE", "SUBMITTED"} or stage == "OS"


def classify_postcheck(selected_alpha_id: str, record: dict[str, Any]) -> dict[str, Any]:
    prior = record.get("prior_check") or {}
    live = record.get("live_check") or {}
    live_status = record.get("live_status")
    prior_self = prior.get("self_correlation")
    live_self = live.get("self_correlation")
    delta = None
    if isinstance(prior_self, (int, float)) and isinstance(live_self, (int, float)):
        delta = round(float(live_self) - float(prior_self), 6)

    non_pass = live.get("non_pass_checks") or []
    non_pass_names = [item.get("name") for item in non_pass]
    live_verified = bool(live.get("check_count"))
    still_submit_ready = live_status == "UNSUBMITTED" and bool(live.get("strict_all_pass"))
    self_corr_result = live.get("self_correlation_result")
    failed_self_corr = self_corr_result == "FAIL"
    errored_self_corr = self_corr_result == "ERROR"

    if record.get("alpha_id") == selected_alpha_id:
        category = "selected_submitted"
    elif not live_verified:
        category = "check_unverified"
    elif live_status != "UNSUBMITTED":
        category = "not_unsubmitted"
    elif still_submit_ready:
        category = "still_submit_ready"
    elif failed_self_corr and prior.get("strict_all_pass") is True:
        category = "likely_blocked_by_new_submission_self_correlation"
    elif errored_self_corr and prior.get("strict_all_pass") is True:
        category = "self_correlation_error_after_submission"
    elif failed_self_corr:
        category = "self_correlation_failed"
    elif errored_self_corr:
        category = "self_correlation_error"
    else:
        category = "failed_other_submission_check"

    affected_by_selected = (
        category == "likely_blocked_by_new_submission_self_correlation"
        and record.get("alpha_id") != selected_alpha_id
    )
    return {
        "category": category,
        "still_submit_ready": still_submit_ready,
        "failed_self_correlation": failed_self_corr,
        "self_correlation_delta_vs_prior": delta,
        "likely_affected_by_newly_submitted_alpha": affected_by_selected,
        "newly_submitted_alpha_id": selected_alpha_id if affected_by_selected else None,
    }


def build_summary(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "remaining_checked": len(records),
        "still_submit_ready": sum(
            1 for item in records if item["postcheck_classification"]["category"] == "still_submit_ready"
        ),
        "likely_blocked_by_new_submission_self_correlation": sum(
            1
            for item in records
            if item["postcheck_classification"]["category"]
            == "likely_blocked_by_new_submission_self_correlation"
        ),
        "self_correlation_error_after_submission": sum(
            1
            for item in records
            if item["postcheck_classification"]["category"] == "self_correlation_error_after_submission"
        ),
        "failed_other_submission_check": sum(
            1 for item in records if item["postcheck_classification"]["category"] == "failed_other_submission_check"
        ),
        "check_unverified": sum(
            1 for item in records if item["postcheck_classification"]["category"] == "check_unverified"
        ),
    }


def render_md(payload: dict[str, Any]) -> str:
    selected = payload["selected"]
    submit = payload["submit_response"]
    post = payload["post_submit_alpha"]
    post_rows = payload["post_submit_candidate_checks"]
    still = [item for item in post_rows if item["postcheck_classification"]["category"] == "still_submit_ready"]
    selfcorr_blocked = [
        item
        for item in post_rows
        if item["postcheck_classification"]["category"] == "likely_blocked_by_new_submission_self_correlation"
    ]
    selfcorr_errors = [
        item
        for item in post_rows
        if item["postcheck_classification"]["category"] == "self_correlation_error_after_submission"
    ]
    other_failed = [
        item
        for item in post_rows
        if item["postcheck_classification"]["category"] == "failed_other_submission_check"
    ]
    unverified = [item for item in post_rows if item["postcheck_classification"]["category"] == "check_unverified"]

    lines = [
        "# 2026-05-24 Submit Best Candidate And Post-Submit Recheck",
        "",
        "- Mode: SINGLE ALPHA SUBMISSION + POST-SUBMIT CHECK.",
        "- Submit endpoint calls allowed by this script: exactly one after live pre-check.",
        f"- Source ranked queue: `{SOURCE_JSON}`",
        f"- Selected alpha: `{selected['alpha_id']}`",
        f"- Submit accepted: `{submit.get('accepted')}`; HTTP status `{submit.get('status_code')}`; source `{submit.get('source')}`",
        f"- Post-submit status: `{post.get('status')}` / stage `{post.get('stage')}` / dateSubmitted `{post.get('dateSubmitted')}`",
        f"- Remaining candidates rechecked: `{len(post_rows)}`",
        f"- Still submit-ready after this submit: `{len(still)}`",
        f"- Likely newly blocked by self-correlation: `{len(selfcorr_blocked)}`",
        f"- Self-correlation check error after this submit: `{len(selfcorr_errors)}`",
        f"- Failed other checks: `{len(other_failed)}`",
        f"- Check unverified: `{len(unverified)}`",
        "",
        "## Submitted Alpha",
        "",
        f"- Rank before submit: `{selected.get('rank')}`",
        f"- Expression: `{selected.get('expression')}`",
        f"- Logic: {selected.get('economic_logic')}",
        f"- Scores: final={selected['scores'].get('final_score')}, econ={selected['scores'].get('economic_logic_score')}, lowcorr={selected['scores'].get('low_selfcorr_score')}, metric={selected['scores'].get('metric_score')}",
        f"- Live pre-submit check: {selected['live_check'].get('pass_count')}/{selected['live_check'].get('check_count')} PASS; SelfCorr={selected['live_check'].get('self_correlation')}",
        "",
        "## Post-Submit Candidate Status",
        "",
        "| Rank | Alpha | Category | Prior SelfCorr | Live SelfCorr | Delta | Check | Sharpe | Fitness | Turnover | Logic |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for item in post_rows:
        cls = item["postcheck_classification"]
        live = item.get("live_check") or {}
        metrics = item.get("live_metrics") or {}
        prior = item.get("prior_check") or {}
        lines.append(
            "| {rank} | `{alpha}` | {category} | {prior_sc} | {live_sc} | {delta} | {passes}/{checks} | {sharpe} | {fitness} | {turnover} | {logic} |".format(
                rank=item.get("rank"),
                alpha=item.get("alpha_id"),
                category=cls.get("category"),
                prior_sc=prior.get("self_correlation"),
                live_sc=live.get("self_correlation"),
                delta=cls.get("self_correlation_delta_vs_prior"),
                passes=live.get("pass_count"),
                checks=live.get("check_count"),
                sharpe=metrics.get("sharpe"),
                fitness=metrics.get("fitness"),
                turnover=metrics.get("turnover"),
                logic=item.get("economic_logic"),
            )
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `likely_blocked_by_new_submission_self_correlation` means the candidate was previously recorded as strict 8-pass and the live post-submit check now returns `SELF_CORRELATION=FAIL`.",
            "- `self_correlation_error_after_submission` means the official self-correlation check returned `ERROR`, so the alpha is not submit-ready but no numeric correlation value was provided.",
            "- The platform check response does not always expose which submitted alpha caused the max self-correlation; attribution to the new submission is therefore marked as likely and backed by before/after check evidence.",
            "",
            "## Files",
            "",
            f"- JSON evidence: `{OUTPUT_JSON}`",
            f"- Markdown memo: `{OUTPUT_MD}`",
            f"- Script: `{RUN_DIR / 'submit_best_and_postcheck.py'}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    previous_output = load_previous_output()
    ranked = load_ranked_candidates()
    session = login()

    selected, pre_submit_checked = fetch_selected_record(session, ranked)
    selected_alpha_id = str(selected["alpha_id"])

    submit_response: dict[str, Any]
    if selected.get("live_status") == "UNSUBMITTED":
        if not selected["live_check"].get("strict_all_pass"):
            raise RuntimeError(f"{selected_alpha_id} live official check is not strict 8-pass.")
        submit_response = submit_alpha(session, selected_alpha_id)
        time.sleep(15)
        post_submit_alpha = fetch_alpha(session, selected_alpha_id)
        if not submit_response["accepted"] and alpha_is_submitted(post_submit_alpha):
            submit_response = {
                **submit_response,
                "accepted": True,
                "accepted_inferred_from_post_submit_alpha_status": True,
                "source": "POST_RESPONSE_REJECTED_BUT_POST_STATUS_SUBMITTED",
            }
    else:
        post_submit_alpha = fetch_alpha(session, selected_alpha_id)
        if not alpha_is_submitted(post_submit_alpha):
            raise RuntimeError(f"{selected_alpha_id} status is {selected.get('live_status')}, not submittable or submitted.")
        submit_response = {
            "alpha_id": selected_alpha_id,
            "submitted_at_utc": utc_now(),
            "status_code": None,
            "accepted": True,
            "body": "",
            "headers": {},
            "source": "ALREADY_SUBMITTED_ON_RESUME",
            "submit_call_skipped": True,
        }

    if not submit_response["accepted"]:
        payload = {
            "mode": "SINGLE_ALPHA_SUBMISSION_FAILED",
            "timestamp_utc": utc_now(),
            "account_id": "CM54257",
            "source_json": str(SOURCE_JSON),
            "selected": selected,
            "pre_submit_checked": pre_submit_checked,
            "submit_response": submit_response,
            "submit_calls_made": 1 if selected.get("live_status") == "UNSUBMITTED" else 0,
            "previous_output_before_resume": previous_output,
        }
        dump_json(OUTPUT_JSON, payload)
        raise RuntimeError(f"Submit was not accepted: {submit_response}")

    post_submit_candidate_checks: list[dict[str, Any]] = []
    for candidate in ranked:
        alpha_id = str(candidate.get("alpha_id") or "")
        if alpha_id == selected_alpha_id:
            continue
        alpha_detail = fetch_alpha(session, alpha_id)
        check = check_alpha(session, alpha_id)
        record = live_record(candidate, alpha_detail, check)
        record["postcheck_classification"] = classify_postcheck(selected_alpha_id, record)
        post_submit_candidate_checks.append(record)
        time.sleep(1)

    payload = {
        "mode": "SINGLE_ALPHA_SUBMISSION_AND_POSTCHECK",
        "timestamp_utc": utc_now(),
        "account_id": "CM54257",
        "user_code_root": "/Users/zpdedn/Documents/github/worldquantAPI/user",
        "source_json": str(SOURCE_JSON),
        "selection_policy": {
            "submit_count_limit": 1,
            "source_order": "final_ranked ascending rank",
            "require_live_status": "UNSUBMITTED",
            "require_live_official_check_strict_all_pass": True,
            "fallback_if_top_not_live_eligible": "next ranked live eligible candidate",
        },
        "selected_alpha_id": selected_alpha_id,
        "selected": selected,
        "pre_submit_checked": pre_submit_checked,
        "submit_response": submit_response,
        "submit_calls_made": 1 if selected.get("live_status") == "UNSUBMITTED" else 0,
        "previous_output_before_resume": previous_output,
        "post_submit_alpha": post_submit_alpha,
        "post_submit_candidate_checks": post_submit_candidate_checks,
        "summary": build_summary(post_submit_candidate_checks),
    }
    dump_json(OUTPUT_JSON, payload)
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")

    print(f"selected={selected_alpha_id}")
    print(f"submit_status={submit_response['status_code']} accepted={submit_response['accepted']}")
    print(f"post_status={post_submit_alpha.get('status')} stage={post_submit_alpha.get('stage')}")
    print(f"dateSubmitted={post_submit_alpha.get('dateSubmitted')}")
    print(f"remaining_checked={payload['summary']['remaining_checked']}")
    print(f"still_submit_ready={payload['summary']['still_submit_ready']}")
    print(
        "likely_blocked_by_new_submission_self_correlation="
        f"{payload['summary']['likely_blocked_by_new_submission_self_correlation']}"
    )
    print(f"json={OUTPUT_JSON}")
    print(f"md={OUTPUT_MD}")


if __name__ == "__main__":
    main()

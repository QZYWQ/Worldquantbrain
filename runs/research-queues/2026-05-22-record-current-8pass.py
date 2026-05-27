#!/usr/bin/env python3
"""Record current account 8-pass alphas without submitting anything."""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


PROJECT_ROOT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
API_BASE = "https://api.worldquantbrain.com"

VARIATION_CHECKS = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations-submission-check.json"
FULL_CHECKS_OUT = PROJECT_ROOT / "runs/research-queues/2026-05-22-current-8pass-checks.json"
EIGHTPASS_JSON = PROJECT_ROOT / "runs/submission-memos/2026-05-22-current-8pass-record.json"
EIGHTPASS_MD = PROJECT_ROOT / "runs/submission-memos/2026-05-22-current-8pass-record.md"
SUBMITTED_JSON = PROJECT_ROOT / "runs/submission-memos/2026-05-22-current-submitted-alphas-record.json"
SUBMITTED_MD = PROJECT_ROOT / "runs/submission-memos/2026-05-22-current-submitted-alphas-record.md"


def load_credentials():
    username = os.environ.get("BRAIN_USERNAME") or os.environ.get("WQ_USERNAME")
    password = os.environ.get("BRAIN_PASSWORD") or os.environ.get("WQ_PASSWORD")
    if username and password:
        return username, password

    for path in (PROJECT_ROOT / "credential.txt", Path.home() / "brain_credentials.txt"):
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8").strip())
        if isinstance(data, dict):
            username = data.get("username") or data.get("user") or data.get("email")
            password = data.get("password")
        elif isinstance(data, list) and len(data) >= 2:
            username, password = data[0], data[1]
        else:
            username = password = None
        if username and password:
            return str(username), str(password)

    raise RuntimeError("Missing BRAIN credentials")


def login():
    username, password = load_credentials()
    session = requests.Session()
    session.auth = (username, password)
    response = session.post(f"{API_BASE}/authentication", timeout=60)
    print(f"Login status: {response.status_code}")
    response.raise_for_status()
    return session


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_json(path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fetch_account_alphas(session, max_results=1000):
    alphas = []
    limit = 100
    offset = 0
    while offset < max_results:
        url = f"{API_BASE}/users/self/alphas?limit={limit}&offset={offset}&hidden=false&type!=SUPER"
        response = session.get(url, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch self alphas: {response.status_code} {response.text[:500]}")
        data = response.json()
        results = data.get("results", [])
        alphas.extend(results)
        if len(results) < limit:
            break
        offset += limit
    return alphas


def metric_value(alpha, key):
    value = (alpha.get("is") or {}).get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def has_passable_hard_metrics(alpha):
    sharpe = metric_value(alpha, "sharpe")
    fitness = metric_value(alpha, "fitness")
    turnover = metric_value(alpha, "turnover")
    if sharpe is None or fitness is None or turnover is None:
        return False
    return sharpe >= 1.25 and fitness >= 1.0 and 0.01 <= turnover <= 0.7


def normalize_existing_check(row):
    if not isinstance(row, dict):
        return None
    if row.get("status") != "CHECKED":
        return None
    check_count = row.get("check_count")
    pass_count = row.get("pass_count")
    if not isinstance(check_count, int) or not isinstance(pass_count, int):
        return None
    return {
        "alpha_id": row.get("alpha_id"),
        "source": "existing_current_check",
        "status": "CHECKED",
        "checks": row.get("checks") or [],
        "check_count": check_count,
        "pass_count": pass_count,
        "fail_count": row.get("fail_count"),
        "strict_8pass": bool(row.get("strict_8pass")),
        "non_pass_checks": row.get("non_pass_checks") or [],
        "raw_check": row.get("raw_check"),
    }


def existing_current_checks():
    rows = load_json(VARIATION_CHECKS, [])
    checks = {}
    for row in rows:
        normalized = normalize_existing_check(row)
        if normalized and normalized.get("alpha_id"):
            checks[normalized["alpha_id"]] = normalized
    return checks


def parse_check_response(data):
    if data.get("is") == 0:
        return {"status": "RELOGIN"}
    is_data = data.get("is", {})
    if not isinstance(is_data, dict):
        return {
            "status": "CHECK_FAILED",
            "error": "unexpected response shape",
            "raw_check": data,
        }
    checks = is_data.get("checks", [])
    pass_count = sum(1 for check in checks if check.get("result") == "PASS")
    fail_count = sum(1 for check in checks if check.get("result") == "FAIL")
    non_pass = [
        {
            "name": check.get("name") or check.get("id") or "UNKNOWN",
            "result": check.get("result"),
            "value": check.get("value"),
            "limit": check.get("limit"),
        }
        for check in checks
        if check.get("result") != "PASS"
    ]
    return {
        "source": "fresh_official_check",
        "status": "CHECKED",
        "self_correlation": is_data.get("selfCorrelation"),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "strict_8pass": len(checks) >= 8 and pass_count == len(checks),
        "non_pass_checks": non_pass,
        "raw_check": data,
    }


def run_submission_check(session, alpha_id):
    for attempt in range(1, 50):
        response = session.get(f"{API_BASE}/alphas/{alpha_id}/check", timeout=60)
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            wait = float(retry_after)
            print(f"  {alpha_id}: retry-after {wait:.1f}s")
            time.sleep(wait)
            continue
        if response.status_code == 401:
            return {"status": "RELOGIN"}
        if response.status_code != 200:
            return {
                "source": "fresh_official_check",
                "status": "CHECK_FAILED",
                "http_status": response.status_code,
                "error": response.text[:500],
            }
        try:
            parsed = parse_check_response(response.json())
        except Exception as exc:
            print(f"  {alpha_id}: non-json check response, retrying ({exc})")
            time.sleep(2)
            continue
        if parsed.get("status") == "RELOGIN":
            return parsed
        return parsed
    return {
        "source": "fresh_official_check",
        "status": "CHECK_FAILED",
        "error": "retry limit exceeded",
    }


def check_name_value(checks, name):
    for check in checks or []:
        if check.get("name") == name:
            return check.get("value")
    return None


def summarize_alpha(alpha, check_record=None):
    is_data = alpha.get("is") or {}
    settings = alpha.get("settings") or {}
    regular = alpha.get("regular") or {}
    checks = (check_record or {}).get("checks") or is_data.get("checks") or []
    return {
        "alpha_id": alpha.get("id"),
        "status": alpha.get("status"),
        "stage": alpha.get("stage"),
        "date_created": alpha.get("dateCreated"),
        "date_submitted": alpha.get("dateSubmitted"),
        "author": alpha.get("author"),
        "expression": regular.get("code") if isinstance(regular, dict) else regular,
        "settings": settings,
        "metrics": {
            "sharpe": is_data.get("sharpe"),
            "fitness": is_data.get("fitness"),
            "turnover": is_data.get("turnover"),
            "returns": is_data.get("returns"),
            "drawdown": is_data.get("drawdown"),
            "margin": is_data.get("margin"),
            "longCount": is_data.get("longCount"),
            "shortCount": is_data.get("shortCount"),
            "subUniverseSharpe": check_name_value(checks, "LOW_SUB_UNIVERSE_SHARPE"),
            "selfCorrelation": check_name_value(checks, "SELF_CORRELATION"),
        },
        "check": check_record,
    }


def render_8pass_md(records, checked_count, skipped_count):
    lines = [
        "# 2026-05-22 Current 8-Pass Record",
        "",
        "- Mode: RECORD ONLY. No alpha was submitted by this script.",
        "- Scope: current official `/users/self/alphas` for the active account.",
        f"- Checked or reused candidate checks: {checked_count}",
        f"- Skipped by hard metric prefilter: {skipped_count}",
        f"- Current unsubmitted strict 8-pass alphas: {len(records)}",
        "",
    ]
    if not records:
        lines.append("No current unsubmitted strict 8-pass alpha found.")
        return "\n".join(lines) + "\n"
    lines.extend([
        "| Alpha ID | Status | Sharpe | Fitness | Turnover | SubU | SelfCorr | Check Source | Expression |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ])
    for item in records:
        metrics = item.get("metrics") or {}
        check = item.get("check") or {}
        expr = (item.get("expression") or "").replace("|", "\\|")
        lines.append(
            f"| {item.get('alpha_id')} | {item.get('status')} | {metrics.get('sharpe')} | "
            f"{metrics.get('fitness')} | {metrics.get('turnover')} | {metrics.get('subUniverseSharpe')} | "
            f"{metrics.get('selfCorrelation')} | {check.get('source')} | `{expr}` |"
        )
    return "\n".join(lines) + "\n"


def render_submitted_md(records):
    lines = [
        "# 2026-05-22 Current Submitted Alpha Record",
        "",
        "- Mode: RECORD ONLY. This file lists alphas already submitted or active.",
        f"- Current submitted/active alphas: {len(records)}",
        "",
    ]
    if not records:
        lines.append("No submitted or active alpha found in the current account.")
        return "\n".join(lines) + "\n"
    lines.extend([
        "| Alpha ID | Status | Stage | Date Submitted | Sharpe | Fitness | Turnover | Expression |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ])
    for item in records:
        metrics = item.get("metrics") or {}
        expr = (item.get("expression") or "").replace("|", "\\|")
        lines.append(
            f"| {item.get('alpha_id')} | {item.get('status')} | {item.get('stage')} | "
            f"{item.get('date_submitted')} | {metrics.get('sharpe')} | {metrics.get('fitness')} | "
            f"{metrics.get('turnover')} | `{expr}` |"
        )
    return "\n".join(lines) + "\n"


def main():
    started = datetime.now(timezone.utc).isoformat()
    session = login()
    alphas = fetch_account_alphas(session)
    existing = existing_current_checks()

    submitted = []
    checks_out = []
    eightpass = []
    skipped_by_metrics = 0

    print(f"Fetched official account alphas: {len(alphas)}")
    for index, alpha in enumerate(alphas, start=1):
        alpha_id = alpha.get("id")
        status = alpha.get("status")
        date_submitted = alpha.get("dateSubmitted")
        stage = alpha.get("stage")
        if status not in ("UNSUBMITTED", None) or date_submitted or stage == "OS":
            submitted.append(summarize_alpha(alpha))
            continue

        if not has_passable_hard_metrics(alpha):
            skipped_by_metrics += 1
            continue

        print(f"[{index}/{len(alphas)}] checking candidate {alpha_id}")
        check_record = existing.get(alpha_id)
        if not check_record:
            check_record = run_submission_check(session, alpha_id)
            if check_record.get("status") == "RELOGIN":
                session = login()
                check_record = run_submission_check(session, alpha_id)

        row = summarize_alpha(alpha, check_record)
        row["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
        checks_out.append(row)
        save_json(FULL_CHECKS_OUT, checks_out)

        if check_record.get("strict_8pass"):
            eightpass.append(row)

        time.sleep(2)

    eightpass.sort(
        key=lambda item: (
            item.get("metrics", {}).get("fitness") or 0,
            item.get("metrics", {}).get("sharpe") or 0,
        ),
        reverse=True,
    )
    submitted.sort(key=lambda item: item.get("date_submitted") or "", reverse=True)

    payload = {
        "mode": "RECORD_ONLY",
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "official_account_alpha_count": len(alphas),
        "checked_or_reused_candidate_count": len(checks_out),
        "skipped_by_hard_metric_prefilter": skipped_by_metrics,
        "current_unsubmitted_8pass_count": len(eightpass),
        "records": eightpass,
    }
    submitted_payload = {
        "mode": "RECORD_ONLY",
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "official_account_alpha_count": len(alphas),
        "submitted_or_active_count": len(submitted),
        "records": submitted,
    }

    save_json(EIGHTPASS_JSON, payload)
    EIGHTPASS_MD.write_text(
        render_8pass_md(eightpass, len(checks_out), skipped_by_metrics),
        encoding="utf-8",
    )
    save_json(SUBMITTED_JSON, submitted_payload)
    SUBMITTED_MD.write_text(render_submitted_md(submitted), encoding="utf-8")

    print("Saved current 8-pass JSON:", EIGHTPASS_JSON)
    print("Saved current 8-pass memo:", EIGHTPASS_MD)
    print("Saved submitted JSON:", SUBMITTED_JSON)
    print("Saved submitted memo:", SUBMITTED_MD)
    print(f"Current unsubmitted strict 8-pass: {len(eightpass)}")
    print(f"Submitted/active records: {len(submitted)}")


if __name__ == "__main__":
    main()

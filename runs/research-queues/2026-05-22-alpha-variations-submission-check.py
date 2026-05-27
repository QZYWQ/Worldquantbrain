#!/usr/bin/env python3
"""Record-only check for completed alpha variations.

This script never submits alphas. It only reads official check results and saves
strict 8-pass records for later manual review.
"""
import json
import os
import subprocess
import time
from pathlib import Path

import requests


PROJECT_ROOT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
VARIATIONS_FILE = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations.json"
RESULTS_FILE = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations-results.json"
CHECKS_FILE = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations-submission-check.json"
PASS_JSON_FILE = PROJECT_ROOT / "runs/submission-memos/2026-05-22-alpha-variations-8pass-alphas.json"
PASS_MD_FILE = PROJECT_ROOT / "runs/submission-memos/2026-05-22-alpha-variations-8pass-alphas.md"
ECONOMIC_TOP5_SCRIPT = PROJECT_ROOT / "runs/research-queues/2026-05-22-alpha-variations-economic-top5.py"
API_BASE = "https://api.worldquantbrain.com"
RECORD_ONLY = True


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


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


def ordered_successes():
    variations = load_json(VARIATIONS_FILE)
    results = {
        item.get("original_id"): item
        for item in load_json(RESULTS_FILE)
        if isinstance(item, dict) and item.get("original_id")
    }
    candidates = []
    for var in variations:
        result = results.get(var["id"])
        if not result or result.get("status") != "SUCCESS" or not result.get("new_alpha_id"):
            continue
        candidates.append(
            {
                "original_id": var["id"],
                "alpha_id": result["new_alpha_id"],
                "expression": result.get("expression") or var.get("regular", {}).get("code"),
                "settings": result.get("settings") or var.get("settings", {}),
                "metrics": result.get("metrics", {}),
                "simulation_status": result.get("simulation_status"),
            }
        )
    return candidates, len(variations), len(results)


def check_submission(session, alpha_id):
    for attempt in range(1, 8):
        response = session.get(f"{API_BASE}/alphas/{alpha_id}/check", timeout=60)
        retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if retry_after:
            wait_seconds = float(retry_after)
            print(f"  Rate limited; waiting {wait_seconds:.1f}s")
            time.sleep(wait_seconds)
            continue

        if response.status_code == 401 and attempt < 7:
            print("  Session expired; re-login required")
            return "RELOGIN"

        if response.status_code != 200:
            return {
                "status": "CHECK_FAILED",
                "http_status": response.status_code,
                "error": response.text[:500],
            }

        data = response.json()
        if data.get("is") == 0:
            print("  Session reported logged out; re-login required")
            return "RELOGIN"

        is_data = data.get("is", {})
        if not isinstance(is_data, dict):
            return {
                "status": "CHECK_FAILED",
                "error": "Unexpected check response shape",
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
            "status": "CHECKED",
            "self_correlation": is_data.get("selfCorrelation"),
            "checks": checks,
            "check_count": len(checks),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "strict_8pass": len(checks) >= 8 and fail_count == 0 and pass_count == len(checks),
            "non_pass_checks": non_pass,
            "raw_check": data,
        }

    return {"status": "CHECK_FAILED", "error": "Retry limit exceeded"}


def render_markdown(pass_alphas, all_results, expected_count, result_count):
    lines = [
        "# 2026-05-22 Alpha Variations 8-Pass Record",
        "",
        "- Mode: RECORD ONLY. No alpha was submitted by this script.",
        f"- Source results: `{RESULTS_FILE}`",
        f"- Full submission checks: `{CHECKS_FILE}`",
        f"- Variation result rows: {result_count}/{expected_count}",
        f"- Official 8-pass alphas: {len(pass_alphas)}",
        "",
    ]

    if pass_alphas:
        lines.extend(
            [
                "| Alpha ID | Original ID | Sharpe | Fitness | Turnover | Self-Correlation | Expression |",
                "| --- | --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for item in pass_alphas:
            metrics = item.get("metrics") or {}
            expression = (item.get("expression") or "").replace("|", "\\|")
            lines.append(
                "| {alpha_id} | {original_id} | {sharpe} | {fitness} | {turnover} | {self_corr} | `{expr}` |".format(
                    alpha_id=item.get("alpha_id"),
                    original_id=item.get("original_id"),
                    sharpe=metrics.get("sharpe"),
                    fitness=metrics.get("fitness"),
                    turnover=metrics.get("turnover"),
                    self_corr=item.get("self_correlation"),
                    expr=expression,
                )
            )
    else:
        lines.append("No strict 8-pass alpha found in this batch yet.")

    lines.extend(["", "## Checked Alpha Summary", ""])
    for item in all_results:
        failed_names = ", ".join(
            check.get("name", "UNKNOWN") for check in item.get("non_pass_checks", [])
        )
        status = "8PASS" if item.get("strict_8pass") else "NOT_8PASS"
        lines.append(
            f"- `{item.get('alpha_id')}` from `{item.get('original_id')}`: "
            f"{status}, pass_count={item.get('pass_count')}, check_count={item.get('check_count')}, "
            f"failed/non-pass={failed_names or '-'}"
        )

    return "\n".join(lines) + "\n"


def main():
    if not RECORD_ONLY:
        raise RuntimeError("This workflow is record-only and must not submit alphas.")

    candidates, expected_count, result_count = ordered_successes()
    print("Mode: RECORD ONLY - no alpha submission will be attempted")
    print(f"Variation result rows: {result_count}/{expected_count}")
    print(f"Successful simulations to check: {len(candidates)}")

    session = login()
    checked = []
    for index, candidate in enumerate(candidates, start=1):
        alpha_id = candidate["alpha_id"]
        print(f"\n[{index}/{len(candidates)}] Checking {alpha_id} ({candidate['original_id']})")
        check = check_submission(session, alpha_id)
        if check == "RELOGIN":
            session = login()
            check = check_submission(session, alpha_id)
        row = {**candidate, **check}
        checked.append(row)
        save_json(CHECKS_FILE, checked)

        label = "8PASS" if row.get("strict_8pass") else "NOT_8PASS"
        print(
            f"  {label}: pass_count={row.get('pass_count')}, "
            f"check_count={row.get('check_count')}, self_corr={row.get('self_correlation')}"
        )
        time.sleep(3)

    pass_alphas = [row for row in checked if row.get("strict_8pass")]
    save_json(CHECKS_FILE, checked)
    save_json(PASS_JSON_FILE, pass_alphas)
    PASS_MD_FILE.write_text(
        render_markdown(pass_alphas, checked, expected_count, result_count),
        encoding="utf-8",
    )

    print("\nSaved full checks to:", CHECKS_FILE)
    print("Saved 8-pass JSON to:", PASS_JSON_FILE)
    print("Saved 8-pass memo to:", PASS_MD_FILE)
    print(f"Strict 8-pass alpha count: {len(pass_alphas)}")

    print("\nRunning record-only economic Top 5 ranking...")
    subprocess.run(["python3", str(ECONOMIC_TOP5_SCRIPT)], check=True)


if __name__ == "__main__":
    main()

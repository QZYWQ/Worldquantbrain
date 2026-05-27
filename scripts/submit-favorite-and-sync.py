#!/usr/bin/env python3
"""Submit best favorite alpha and sync account state."""
import sys, json, time
from datetime import datetime
from pathlib import Path

from machine_lib import login

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
OUTPUT_DIR = PROJECT / "runs" / "submission-memos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Submission candidate: d5d8p1x2 (accrued_liabilities/assets)
# S=1.50, F=1.03, TVR=0.0204, SC=0.4580 (confirmed 8-pass in project record)
# Clean independent family, strong economic logic: rising liabilities → negative signal
TARGET_ALPHA = "d5d8p1x2"

def run_check(session, alpha_id, max_wait=300):
    """Run /check and poll until SC is computed."""
    print(f"\n  Running /check on {alpha_id}...", flush=True)
    resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}/check")

    deadline = time.time() + max_wait
    while time.time() < deadline:
        resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}/check")
        retry = resp.headers.get("retry-after")
        if retry:
            wait = float(retry)
            print(f"    Retry-After: {wait}s", flush=True)
            time.sleep(min(wait, 30))
            continue
        if resp.status_code != 200:
            time.sleep(5)
            continue

        try:
            data = resp.json()
        except:
            time.sleep(5)
            continue

        checks = data.get("is", {}).get("checks", [])
        if not checks:
            time.sleep(5)
            continue

        # Check if SC is computed
        sc = next((c for c in checks if c["name"] == "SELF_CORRELATION"), None)
        sc_val = sc.get("value") if sc else None

        all_pass = all(c["result"] == "PASS" for c in checks)
        fails = [c for c in checks if c["result"] != "PASS"]

        print(f"    Checks: {len(checks)} total, {len(fails)} fail, SC={sc_val}", flush=True)
        for c in checks:
            status = "✅" if c["result"] == "PASS" else "⏳" if c["result"] == "PENDING" else "❌"
            print(f"      {status} {c['name']}: {c['result']} (value={c.get('value')})", flush=True)

        if sc and sc["result"] != "PENDING":
            return all_pass, sc_val, checks

        time.sleep(5)

    # Last attempt
    print("    Timeout waiting for SC, using current state", flush=True)
    return all(c["result"] == "PASS" for c in checks), sc_val if sc else None, checks


def submit_alpha(session, alpha_id):
    """Submit alpha via API."""
    print(f"\n  Submitting {alpha_id}...", flush=True)
    resp = session.post(f"https://api.worldquantbrain.com/alphas/{alpha_id}/submit")
    print(f"    HTTP {resp.status_code}", flush=True)
    if resp.text:
        print(f"    Response: {resp.text[:300]}", flush=True)
    return resp.status_code == 200


def sync_account_state(session):
    """Fetch full account state."""
    print(f"\n  Syncing account state...", flush=True)
    all_a = []
    for offset in range(0, 2000, 100):
        r = session.get(
            f"https://api.worldquantbrain.com/users/self/alphas"
            f"?limit=100&offset={offset}&hidden=false&type!=SUPER&order=-is.sharpe"
        )
        if r.status_code != 200:
            break
        data = r.json()
        batch = data.get("results", [])
        all_a.extend(batch)
        if len(batch) < 100:
            break
        time.sleep(0.5)

    # Gather stats
    submitted = [a for a in all_a if "SUBMITTED" in a.get("status", "")]
    unsubmitted = [a for a in all_a if a.get("status") == "UNSUBMITTED"]

    summary = {
        "synced_at": datetime.now().isoformat(),
        "total": len(all_a),
        "submitted": len(submitted),
        "unsubmitted": len(unsubmitted),
        "positive_sharpe_unsubmitted": len([a for a in unsubmitted if a.get("is", {}).get("sharpe", 0) > 0]),
        "sharpe_ge_1.5_unsubmitted": len([a for a in unsubmitted if a.get("is", {}).get("sharpe", 0) >= 1.5]),
        "favorites_count": len([a for a in all_a if a.get("color") == "YELLOW"]),
    }

    print(f"    Total: {summary['total']}", flush=True)
    print(f"    Submitted (ACTIVE): {summary['submitted']}", flush=True)
    print(f"    Unsubmitted: {summary['unsubmitted']}", flush=True)
    print(f"    S>=1.5 unsubmitted: {summary['sharpe_ge_1.5_unsubmitted']}", flush=True)
    print(f"    Favorites: {summary['favorites_count']}", flush=True)

    return summary, all_a


def main():
    print("=" * 60, flush=True)
    print("  Favorite Alpha Submission Pipeline", flush=True)
    print(f"  Target: {TARGET_ALPHA}", flush=True)
    print(f"  Time: {datetime.now().isoformat()}", flush=True)
    print("=" * 60, flush=True)

    s = login()

    # Step 1: Run /check
    print(f"\n--- Step 1: Verification Check ---", flush=True)
    all_pass, sc_val, checks = run_check(s, TARGET_ALPHA)

    # Step 2: Submit if 8-pass
    print(f"\n--- Step 2: Submission ---", flush=True)
    submitted = False
    if all_pass:
        print(f"  ✅ All checks PASS (SC={sc_val}). Proceeding with submission.", flush=True)
        submitted = submit_alpha(s, TARGET_ALPHA)
    else:
        print(f"  ❌ Not all checks pass. Cannot submit.", flush=True)

    # Step 3: Verify submission
    print(f"\n--- Step 3: Post-Submission Verification ---", flush=True)
    if submitted:
        r = s.get(f"https://api.worldquantbrain.com/alphas/{TARGET_ALPHA}")
        if r.status_code == 200:
            d = r.json()
            print(f"  New status: {d.get('status')}", flush=True)
            print(f"  Sharpe: {d.get('is',{}).get('sharpe')}", flush=True)

    # Step 4: Sync account state
    print(f"\n--- Step 4: Account State Sync ---", flush=True)
    summary, all_alphas = sync_account_state(s)

    # Save state
    report = {
        "target_alpha": TARGET_ALPHA,
        "pre_check": {"all_pass": all_pass, "sc_value": sc_val},
        "submitted": submitted,
        "account_state": summary,
    }
    out_path = OUTPUT_DIR / f"submit-and-sync-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str))
    print(f"\n  Report saved: {out_path}", flush=True)

    print(f"\n{'='*60}", flush=True)
    if submitted:
        print(f"  ✅ {TARGET_ALPHA} SUBMITTED SUCCESSFULLY", flush=True)
    else:
        print(f"  ❌ {TARGET_ALPHA} NOT SUBMITTED", flush=True)
    print(f"  Account: {summary['total']} total, {summary['submitted']} submitted", flush=True)
    print(f"{'='*60}", flush=True)


if __name__ == "__main__":
    main()

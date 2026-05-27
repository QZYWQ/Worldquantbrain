#!/usr/bin/env python3
"""
Submission Check for Grk1xjWZ Rescue + Sign-flip Top Candidates
"""
import requests
import time
import json
import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

CANDIDATES = [
    "ZYr6YMgQ",  # rescue_01 - Grk1xjWZ sector替代 - Sharpe 1.65
    "gJx6kwVQ",  # rescue_04 - Grk1xjWZ decay=6+sector - Sharpe 1.60
    "VkOV1PwM",  # flip_01 - 2rJ8q1j8 reverse - Sharpe 1.38
    "xARqO2xp",  # flip_02 - blvGa3dR reverse - Sharpe 1.35
    "e7LmkjYJ",  # flip_02b - blvGa3dR reverse + INDUSTRY - Sharpe 1.34
]

def check_submission(s, alpha_id):
    """Check submission eligibility for an alpha."""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            result = s.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}/check")

            # Check for rate limiting
            if "retry-after" in result.headers:
                wait = float(result.headers["retry-after"])
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue

            if result.status_code != 200:
                print(f"  HTTP {result.status_code}: {result.content[:200]}")
                return None

            data = result.json()

            # Check if logged out
            if data.get("is") == 0:
                print("  Logged out, re-logging...")
                return "RELOG"

            is_data = data.get("is", {})
            checks = is_data.get("checks", [])

            # Parse checks into dict
            checks_dict = {}
            for check in checks:
                name = check.get("name", check.get("id", "UNKNOWN"))
                checks_dict[name] = {
                    "result": check.get("result"),
                    "value": check.get("value"),
                }

            # Get self-correlation
            sc = is_data.get("selfCorrelation")
            if sc is None:
                for check in checks:
                    if check.get("name") == "SELF_CORRELATION":
                        sc = check.get("value")
                        break

            return {
                "alpha_id": alpha_id,
                "self_correlation": sc,
                "checks": checks_dict,
                "all_pass": all(c.get("result") != "FAIL" for c in checks_dict.values()) if checks_dict else False,
            }

        except Exception as e:
            print(f"  Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                return None
    return None


def run_checks():
    s = login()
    results = []

    print(f"Checking {len(CANDIDATES)} candidates...")
    print("=" * 70)

    for i, alpha_id in enumerate(CANDIDATES):
        print(f"\n[{i+1}/{len(CANDIDATES)}] {alpha_id}")

        result = check_submission(s, alpha_id)

        if result == "RELOG":
            s = login()
            result = check_submission(s, alpha_id)

        if result is None:
            print(f"  FAILED to check")
            results.append({"alpha_id": alpha_id, "status": "CHECK_FAILED"})
            continue

        sc = result.get("self_correlation")
        checks = result.get("checks", {})
        all_pass = result.get("all_pass", False)

        print(f"  Self-Correlation: {sc}")
        print(f"  All Pass: {all_pass}")

        for name, check in checks.items():
            res = check.get("result", "N/A")
            val = check.get("value", "N/A")
            status = "✅" if res != "FAIL" else "❌"
            print(f"    {status} {name}: {res} (value={val})")

        results.append({
            "alpha_id": alpha_id,
            "self_correlation": sc,
            "checks": checks,
            "all_pass": all_pass,
        })

        # Rate limit
        time.sleep(3)

    print("\n" + "=" * 70)
    print("SUBMISSION CHECK SUMMARY")
    print("=" * 70)

    for r in results:
        alpha_id = r["alpha_id"]
        sc = r.get("self_correlation")
        all_pass = r.get("all_pass", False)
        sc_str = f"{sc:.4f}" if sc is not None else "N/A"
        pass_str = "✅ PASS" if all_pass else "❌ FAIL"
        print(f"  {alpha_id}: SC={sc_str}, {pass_str}")

        if not all_pass:
            print("    Failed checks:")
            for name, check in r.get("checks", {}).items():
                if check.get("result") == "FAIL":
                    print(f"      - {name}: {check.get('value')}")

    # Save results
    output = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-grk1xjwz-rescue-signflip-submission-check.json"
    with open(output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output}")

    return results


if __name__ == "__main__":
    run_checks()
#!/usr/bin/env python3
"""
Retry submission check for rate-limited candidates
"""
import time
import json
import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

CANDIDATES = [
    "GrkPoXPG",   # r5_ts_02 - inverse(ts_mean leverage)/(burn+2) - Sharpe 1.29
    "omV7g2NE",   # r5_sent_02 - same + sector - Sharpe 1.27
]


def check_submission(s, alpha_id):
    for attempt in range(10):
        try:
            result = s.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}/check")

            if "retry-after" in result.headers:
                wait = float(result.headers["retry-after"])
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait + 0.5)
                continue

            if result.status_code != 200:
                print(f"  HTTP {result.status_code}: {result.content[:200]}")
                return None

            data = result.json()

            if data.get("is") == 0:
                print("  Logged out, re-logging...")
                return "RELOG"

            is_data = data.get("is", {})
            checks = is_data.get("checks", [])

            checks_dict = {}
            for check in checks:
                name = check.get("name", check.get("id", "UNKNOWN"))
                checks_dict[name] = {
                    "result": check.get("result"),
                    "value": check.get("value"),
                }

            return {
                "alpha_id": alpha_id,
                "self_correlation": is_data.get("selfCorrelation"),
                "checks": checks_dict,
                "all_pass": all(c.get("result") != "FAIL" for c in checks_dict.values()) if checks_dict else False,
            }

        except Exception as e:
            print(f"  Error: {e}")
            if attempt < 9:
                time.sleep(5)
            else:
                return None
    return None


def run_checks():
    s = login()
    results = []

    print(f"Checking {len(CANDIDATES)} candidates (retry batch)...")
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

        time.sleep(5)

    print("\n" + "=" * 70)
    print("RETRY SUMMARY")
    print("=" * 70)

    for r in results:
        alpha_id = r["alpha_id"]
        sc = r.get("self_correlation")
        all_pass = r.get("all_pass", False)
        sc_str = f"{sc:.4f}" if sc is not None else "N/A"
        pass_str = "✅ PASS" if all_pass else "❌ FAIL"
        print(f"  {alpha_id}: SC={sc_str}, {pass_str}")

    output = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-retry-submission-check.json"
    with open(output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output}")

    return results


if __name__ == "__main__":
    run_checks()
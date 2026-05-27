#!/usr/bin/env python3
"""
Grk1xjWZ Sub-universe Rescue + Sign-flip Batch Simulation
2026-05-22 Overnight Alpha 升阶
"""

import requests
import time
import json
import sys
import os

sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

BATCH_FILE = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-grk1xjwz-rescue-signflip-batch.json"
OUTPUT_FILE = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-grk1xjwz-rescue-signflip-results.json"

# ============================================================================
# Alpha Expressions to Test
# ============================================================================

ALPHAS = [
    # === Priority 1: Grk1xjWZ Sub-universe Rescue ===
    # Original: group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), industry)
    # Sub-universe FAIL: 0.34/0.68

    # Rescue 1: sector instead of industry
    {
        "id": "rescue_01",
        "desc": "Grk1xjWZ - sector替代industry",
        "alpha": "group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # Rescue 2: rank() outer wrapper
    {
        "id": "rescue_02",
        "desc": "Grk1xjWZ - rank外层wrapper",
        "alpha": "rank(group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # Rescue 3: sector + cap bucket neutralization
    {
        "id": "rescue_03",
        "desc": "Grk1xjWZ - sector + cap bucket",
        "alpha": "group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
        "neutralizationBucket": "bucket(rank(cap), range='0.1, 1, 0.1')",
    },
    # Rescue 4: decay=6 + sector
    {
        "id": "rescue_04",
        "desc": "Grk1xjWZ - decay=6 + sector",
        "alpha": "group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector)",
        "decay": 6,
        "neutralization": "SUBINDUSTRY",
    },
    # Rescue 5: decay=8 + sector + cap bucket
    {
        "id": "rescue_05",
        "desc": "Grk1xjWZ - decay=8 + sector + cap bucket",
        "alpha": "group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector)",
        "decay": 8,
        "neutralization": "SUBINDUSTRY",
        "neutralizationBucket": "bucket(rank(cap), range='0.1, 1, 0.1')",
    },

    # === Priority 2: Sign-Flip - 2rJ8q1j8 ===
    # Original: group_neutralize(multiply(book_leverage_ratio_3, inverse(cash_burn_rate_v1)), industry)
    # Sharpe=-1.39, Fitness=-1.37
    {
        "id": "flip_01",
        "desc": "2rJ8q1j8 reverse - group_neutralize multiply/inverse",
        "alpha": "reverse(group_neutralize(multiply(book_leverage_ratio_3, inverse(cash_burn_rate_v1)), industry))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },

    # === Priority 2: Sign-Flip - blvGa3dR ===
    # Original: divide(book_leverage_ratio_3, add(cash_burn_rate_v1, 1))
    # Sharpe=-1.34, Fitness=-1.28
    {
        "id": "flip_02",
        "desc": "blvGa3dR reverse - divide leverage/burn",
        "alpha": "reverse(divide(book_leverage_ratio_3, add(cash_burn_rate_v1, 1)))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # blvGa3dR variant with industry neutralization
    {
        "id": "flip_02b",
        "desc": "blvGa3dR reverse + industry neutralization",
        "alpha": "reverse(divide(book_leverage_ratio_3, add(cash_burn_rate_v1, 1)))",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },

    # === Priority 2: Sign-Flip - akojVY7v ===
    # Original: subtract(book_leverage_ratio_3, cash_burn_rate_v1)
    # Sharpe=-1.10, Fitness=-0.97
    {
        "id": "flip_03",
        "desc": "akojVY7v reverse - subtract leverage/burn",
        "alpha": "reverse(subtract(book_leverage_ratio_3, cash_burn_rate_v1))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # akojVY7v + industry neutralization
    {
        "id": "flip_03b",
        "desc": "akojVY7v reverse + industry neutralization",
        "alpha": "reverse(subtract(book_leverage_ratio_3, cash_burn_rate_v1))",
        "decay": 0,
        "neutralization": "INDUSTRY",
    },
    # akojVY7v + sector neutralization
    {
        "id": "flip_03c",
        "desc": "akojVY7v reverse + sector neutralization",
        "alpha": "reverse(subtract(book_leverage_ratio_3, cash_burn_rate_v1))",
        "decay": 0,
        "neutralization": "SECTOR",
    },
]


def build_settings(alpha_info, region="USA", universe="TOP3000"):
    """Build simulation settings dict."""
    settings = {
        "instrumentType": "EQUITY",
        "region": region,
        "universe": universe,
        "delay": 1,
        "decay": alpha_info.get("decay", 0),
        "neutralization": alpha_info.get("neutralization", "SUBINDUSTRY"),
        "truncation": 0.08,
        "pasteurization": "ON",
        "testPeriod": "P2Y",
        "unitHandling": "VERIFY",
        "nanHandling": "ON",
        "language": "FASTEXPR",
        "visualization": False,
    }
    # Add optional neutralizationBucket if present
    if "neutralizationBucket" in alpha_info:
        settings["neutralizationBucket"] = alpha_info["neutralizationBucket"]
    return settings


def run_batch():
    """Run the full batch simulation."""
    s = login()
    results = []

    print(f"Starting batch simulation: {len(ALPHAS)} alphas")
    print("=" * 70)

    for i, alpha_info in enumerate(ALPHAS):
        alpha_id = alpha_info["id"]
        desc = alpha_info["desc"]
        alpha_expr = alpha_info["alpha"]

        print(f"\n[{i+1}/{len(ALPHAS)}] {alpha_id}: {desc}")
        print(f"  Expression: {alpha_expr[:80]}...")

        sim_data = {
            "type": "REGULAR",
            "settings": build_settings(alpha_info),
            "regular": alpha_expr,
        }

        try:
            # Submit simulation
            resp = s.post("https://api.worldquantbrain.com/simulations", json=sim_data)
            if resp.status_code != 201:
                print(f"  ERROR: HTTP {resp.status_code}: {resp.content[:200]}")
                results.append({
                    "id": alpha_id,
                    "desc": desc,
                    "status": "SUBMIT_ERROR",
                    "error": resp.content.decode("utf-8", errors="replace")[:200],
                })
                continue

            location = resp.headers.get("Location")
            print(f"  Submitted. Polling: {location}")

            # Poll for completion
            max_polls = 120
            for poll in range(max_polls):
                prog = s.get(location)
                h = prog.headers

                if h.get("Retry-After"):
                    wait = float(h["Retry-After"])
                    print(f"  Waiting {wait}s...")
                    time.sleep(wait)
                    continue

                result = prog.json()
                status = result.get("status", "UNKNOWN")

                if status in ("COMPLETE", "WARNING"):
                    alpha_id_result = result.get("alpha")
                    print(f"  COMPLETE! Alpha ID: {alpha_id_result}")

                    # Get full metrics
                    try:
                        ad = s.get(f"https://api.worldquantbrain.com/alphas/{alpha_id_result}").json()
                        is_m = ad.get("is", {})
                        metrics = {
                            "sharpe": is_m.get("sharpe"),
                            "fitness": is_m.get("fitness"),
                            "turnover": is_m.get("turnover"),
                            "margin": is_m.get("margin"),
                            "longCount": is_m.get("longCount"),
                            "shortCount": is_m.get("shortCount"),
                        }
                        sub_result = ad.get("is", {}).get("submissionEligibility", {})
                        checks = {}
                        for check in sub_result.get("checks", []):
                            checks[check.get("name", check.get("id", "UNKNOWN"))] = {
                                "result": check.get("result"),
                                "value": check.get("value"),
                            }
                    except Exception as e:
                        print(f"  Warning: Could not fetch metrics: {e}")
                        metrics = {}
                        checks = {}

                    results.append({
                        "id": alpha_id,
                        "desc": desc,
                        "original_alpha_id": alpha_id_result,
                        "expression": alpha_expr,
                        "status": status,
                        "metrics": metrics,
                        "checks": checks,
                        "settings": sim_data["settings"],
                    })
                    break
                elif status == "FAILED":
                    print(f"  FAILED: {result.get('error', 'Unknown error')}")
                    results.append({
                        "id": alpha_id,
                        "desc": desc,
                        "status": "FAILED",
                        "error": result.get("error", "Unknown"),
                    })
                    break
                else:
                    print(f"  Status: {status}, continuing...")
                    time.sleep(2)
            else:
                print(f"  TIMEOUT after {max_polls} polls")
                results.append({
                    "id": alpha_id,
                    "desc": desc,
                    "status": "TIMEOUT",
                })

        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append({
                "id": alpha_id,
                "desc": desc,
                "status": "EXCEPTION",
                "error": str(e),
            })

        # Rate limiting: sleep between simulations
        print(f"  Sleeping 4s before next simulation...")
        time.sleep(4)

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    print("BATCH COMPLETE")
    print(f"Results saved to: {OUTPUT_FILE}")

    # Summary
    completed = [r for r in results if r["status"] in ("COMPLETE", "WARNING")]
    print(f"\nCompleted: {len(completed)}/{len(ALPHAS)}")
    for r in completed:
        m = r.get("metrics", {})
        sharpe = m.get("sharpe", "N/A")
        fitness = m.get("fitness", "N/A")
        turnover = m.get("turnover", "N/A")
        print(f"  {r['id']}: Sharpe={sharpe:.2f}, Fitness={fitness:.2f}, TVR={turnover:.4f}")

    return results


if __name__ == "__main__":
    run_batch()
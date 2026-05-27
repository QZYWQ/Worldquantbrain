#!/usr/bin/env python3
"""
Round 4 - (burn+2) Structure Optimization
Key insight: burn+2 passes SubU (0.96) but Sharpe=1.23 is just under 1.2
Goal: Get Sharpe > 1.2 WITH burn+2
"""
import time
import json
import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

OUTPUT_FILE = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-round4-burn2-optimize-results.json"

# Core insight: 1/leverage/(burn+2) = divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2))
# This passed SubU=0.96 but Sharpe=1.23 (just under 1.2)
# Strategy: vary the leverage field and add decay/group_neutralize

ALPHAS = [
    # === Vary leverage field with burn+2 ===
    {
        "id": "r4_lev_01",
        "desc": "1/debt_to_equity/(burn+2)",
        "alpha": "divide(inverse(debt_to_equity_ratio), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r4_lev_02",
        "desc": "1/debt_to_assets/(burn+2)",
        "alpha": "divide(inverse(debt_to_assets), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r4_lev_03",
        "desc": "1/equity_multiplier/(burn+2)",
        "alpha": "divide(inverse(equity_multiplier), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Add group_neutralize to burn+2 variants ===
    {
        "id": "r4_gn_01",
        "desc": "1/leverage/(burn+2) + sector",
        "alpha": "group_neutralize(divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2)), sector)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r4_gn_02",
        "desc": "1/leverage/(burn+2) + industry",
        "alpha": "group_neutralize(divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2)), industry)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === decay with burn+2 ===
    {
        "id": "r4_decay_01",
        "desc": "1/leverage/(burn+2) + decay=5",
        "alpha": "divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2))",
        "decay": 5,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r4_decay_02",
        "desc": "1/leverage/(burn+2) + decay=8",
        "alpha": "divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2))",
        "decay": 8,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r4_decay_03",
        "desc": "1/debt_eq/(burn+2) + decay=5",
        "alpha": "divide(inverse(debt_to_equity_ratio), add(cash_burn_rate_v1, 2))",
        "decay": 5,
        "neutralization": "SUBINDUSTRY",
    },
    # === zscore/rank wrapper on burn+2 ===
    {
        "id": "r4_zscore_01",
        "desc": "zscore(1/leverage/(burn+2))",
        "alpha": "zscore(divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2)))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r4_zscore_gn",
        "desc": "zscore + group_neutralize(burn+2)",
        "alpha": "zscore(group_neutralize(divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2)), sector))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === multiply with cap for diversification ===
    {
        "id": "r4_cap_01",
        "desc": "1/leverage/(burn+2) * rank(cap)",
        "alpha": "multiply(divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2)), rank(cap))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === burn+3 variants ===
    {
        "id": "r4_burn3_01",
        "desc": "1/leverage/(burn+3)",
        "alpha": "divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 3))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r4_burn3_02",
        "desc": "1/leverage/(burn+3) + sector",
        "alpha": "group_neutralize(divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 3)), sector)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Alternative structure: burn * leverage with inverse ===
    {
        "id": "r4_alt_01",
        "desc": "inverse(burn+1) * inverse(leverage)",
        "alpha": "multiply(inverse(add(cash_burn_rate_v1, 1)), inverse(book_leverage_ratio_3))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r4_alt_02",
        "desc": "inverse(burn+1) * inverse(leverage) + sector",
        "alpha": "group_neutralize(multiply(inverse(add(cash_burn_rate_v1, 1)), inverse(book_leverage_ratio_3)), sector)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
]


def build_settings(alpha_info, region="USA", universe="TOP3000"):
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
    return settings


def run_batch():
    s = login()
    results = []

    print(f"Starting Round 4 batch: {len(ALPHAS)} alphas")
    print("=" * 70)

    for i, alpha_info in enumerate(ALPHAS):
        alpha_id = alpha_info["id"]
        desc = alpha_info["desc"]
        alpha_expr = alpha_info["alpha"]

        print(f"\n[{i+1}/{len(ALPHAS)}] {alpha_id}: {desc}")
        print(f"  {alpha_expr[:80]}...")

        sim_data = {
            "type": "REGULAR",
            "settings": build_settings(alpha_info),
            "regular": alpha_expr,
        }

        try:
            resp = s.post("https://api.worldquantbrain.com/simulations", json=sim_data)
            if resp.status_code != 201:
                print(f"  ERROR: HTTP {resp.status_code}: {resp.content[:200]}")
                results.append({"id": alpha_id, "desc": desc, "status": "SUBMIT_ERROR", "error": resp.content.decode("utf-8", errors="replace")[:200]})
                continue

            location = resp.headers.get("Location")
            print(f"  Submitted: {location}")

            max_polls = 120
            for _ in range(max_polls):
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
                    except Exception as e:
                        print(f"  Warning: Could not fetch metrics: {e}")
                        metrics = {}

                    results.append({
                        "id": alpha_id,
                        "desc": desc,
                        "original_alpha_id": alpha_id_result,
                        "expression": alpha_expr,
                        "status": status,
                        "metrics": metrics,
                        "settings": sim_data["settings"],
                    })
                    break
                elif status == "FAILED":
                    print(f"  FAILED: {result.get('error', 'Unknown error')}")
                    results.append({"id": alpha_id, "desc": desc, "status": "FAILED", "error": result.get("error", "Unknown")})
                    break
                else:
                    print(f"  Status: {status}")
                    time.sleep(2)
            else:
                print(f"  TIMEOUT")
                results.append({"id": alpha_id, "desc": desc, "status": "TIMEOUT"})

        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append({"id": alpha_id, "desc": desc, "status": "EXCEPTION", "error": str(e)})

        print(f"  Sleeping 4s...")
        time.sleep(4)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    print("ROUND 4 COMPLETE")
    print(f"Results: {OUTPUT_FILE}")

    completed = [r for r in results if r["status"] in ("COMPLETE", "WARNING")]
    print(f"\nCompleted: {len(completed)}/{len(ALPHAS)}")
    for r in completed:
        m = r.get("metrics", {})
        sharpe = m.get("sharpe", "N/A")
        fitness = m.get("fitness", "N/A")
        turnover = m.get("turnover", "N/A")
        print(f"  {r['id']}: Sharpe={sharpe:.2f}, Fitness={fitness:.2f}, TVR={turnover:.4f}")

    # Find best by Sharpe
    if completed:
        best = max(completed, key=lambda x: x.get("metrics", {}).get("sharpe", 0))
        print(f"\nBest by Sharpe: {best['id']} with {best.get('metrics', {}).get('sharpe'):.2f}")

        # Find any with Sharpe > 1.2
        above_12 = [r for r in completed if r.get("metrics", {}).get("sharpe", 0) > 1.2]
        if above_12:
            print(f"\nCandidates with Sharpe > 1.2:")
            for r in sorted(above_12, key=lambda x: x.get("metrics", {}).get("sharpe", 0), reverse=True):
                print(f"  {r['id']}: Sharpe={r.get('metrics',{}).get('sharpe'):.2f}")

    return results


if __name__ == "__main__":
    run_batch()
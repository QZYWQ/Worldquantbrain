#!/usr/bin/env python3
"""
Grk1xjWZ Sub-universe Rescue Round 2 - rank/zscore wrappers
"""
import requests
import time
import json
import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

BATCH_FILE = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-grk1xjwz-rescue-round2-batch.json"
OUTPUT_FILE = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-grk1xjwz-rescue-round2-results.json"

ALPHAS = [
    # === rank() outer wrapper - most likely to help ===
    {
        "id": "r2_rank_01",
        "desc": "rank外层 + sector neutralization",
        "alpha": "rank(group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r2_rank_02",
        "desc": "rank外层 + decay=6",
        "alpha": "rank(group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector))",
        "decay": 6,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r2_rank_03",
        "desc": "zscore外层 + sector neutralization",
        "alpha": "zscore(group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r2_rank_04",
        "desc": "rank外层 + industry neutralization",
        "alpha": "rank(group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), industry))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === quantile outer wrapper ===
    {
        "id": "r2_quantile_01",
        "desc": "quantile外层 + sector",
        "alpha": "quantile(group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Sign-flip with rank ===
    {
        "id": "r2_flip_rank_01",
        "desc": "2rJ8q1j8 sign-flip + rank外层",
        "alpha": "rank(reverse(group_neutralize(multiply(book_leverage_ratio_3, inverse(cash_burn_rate_v1)), industry)))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r2_flip_rank_02",
        "desc": "blvGa3dR sign-flip + rank外层",
        "alpha": "rank(reverse(divide(book_leverage_ratio_3, add(cash_burn_rate_v1, 1))))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Inverse of inverse - double-reverse ===
    {
        "id": "r2_dblinv_01",
        "desc": "inverse(book_leverage_ratio_3) / (cash_burn_rate_v1 + 1)",
        "alpha": "divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 1))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === ts_zscore on the core ratio before group_neutralize ===
    {
        "id": "r2_tsz_01",
        "desc": "ts_zscore before group_neutralize + sector",
        "alpha": "group_neutralize(ts_zscore(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), 20), sector)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Add cap as diversifier ===
    {
        "id": "r2_cap_01",
        "desc": "Core + cap weighted diversification",
        "alpha": "group_neutralize(divide(change_in_eps_surprise, add(book_leverage_ratio_3, 1)), sector) * rank(cap)",
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

    print(f"Starting Round 2 batch: {len(ALPHAS)} alphas")
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
    print("ROUND 2 COMPLETE")
    print(f"Results: {OUTPUT_FILE}")

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
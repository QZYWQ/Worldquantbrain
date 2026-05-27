#!/usr/bin/env python3
"""
Round 5 - Broader Field Exploration
Key insight: burn+2/3 solves SubU but Sharpe caps at ~1.26
Goal: Find new field combinations that can break above 1.3
"""
import time
import json
import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

OUTPUT_FILE = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-round5-broader-explore-results.json"

ALPHAS = [
    # === Alternative structure: different denominators with inverse leverage ===
    {
        "id": "r5_denom_01",
        "desc": "inverse(leverage) / (burn + abs_value)",
        "alpha": "divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, abs(change_in_eps_surprise)))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r5_denom_02",
        "desc": "inverse(leverage) / (burn + volatility)",
        "alpha": "divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, ts_std_dev(returns, 20)))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r5_denom_03",
        "desc": "inverse(leverage) / (burn + analyst_rating)",
        "alpha": "divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, consensus_analyst_rating))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === ts_ operators on the core ===
    {
        "id": "r5_ts_01",
        "desc": "ts_mean of inverse leverage / (burn+2)",
        "alpha": "divide(ts_mean(inverse(book_leverage_ratio_3), 20), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r5_ts_02",
        "desc": "inverse(ts_mean leverage) / (burn+2)",
        "alpha": "divide(inverse(ts_mean(book_leverage_ratio_3, 20)), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r5_ts_03",
        "desc": "ts_zscore leverage / (burn+2)",
        "alpha": "divide(ts_zscore(book_leverage_ratio_3, 20), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Different leverage fields ===
    {
        "id": "r5_lev_01",
        "desc": "inverse(liabilities_to_assets) / (burn+2)",
        "alpha": "divide(inverse(liabilities_to_assets), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r5_lev_02",
        "desc": "inverse(net_debt_to_equity) / (burn+2)",
        "alpha": "divide(inverse(net_debt_to_equity), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Combinations with analyst sentiment ===
    {
        "id": "r5_sent_01",
        "desc": "inverse(leverage) / (burn+2) * analyst_sentiment",
        "alpha": "multiply(divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2)), consensus_analyst_rating)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r5_sent_02",
        "desc": "inverse(leverage) * analyst / (burn+2) with sector",
        "alpha": "group_neutralize(multiply(divide(inverse(book_leverage_ratio_3), add(cash_burn_rate_v1, 2)), consensus_analyst_rating), sector)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Different numerators ===
    {
        "id": "r5_num_01",
        "desc": "inverse(eps_surprise) / (burn+2)",
        "alpha": "divide(inverse(change_in_eps_surprise), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "id": "r5_num_02",
        "desc": "inverse(earnings_momentum) / (burn+2)",
        "alpha": "divide(inverse(earnings_momentum_analyst_score), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === rank on ts structure ===
    {
        "id": "r5_ts_rank_01",
        "desc": "rank(ts_mean leverage) / (burn+2)",
        "alpha": "divide(rank(ts_mean(book_leverage_ratio_3, 20)), add(cash_burn_rate_v1, 2))",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    # === Multiply two fields instead of divide ===
    {
        "id": "r5_mul_01",
        "desc": "inverse(leverage) * inverse(burn+1) + sector",
        "alpha": "group_neutralize(multiply(inverse(book_leverage_ratio_3), inverse(add(cash_burn_rate_v1, 1))), sector)",
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

    print(f"Starting Round 5 batch: {len(ALPHAS)} alphas")
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
    print("ROUND 5 COMPLETE")
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

        above_12 = [r for r in completed if r.get("metrics", {}).get("sharpe", 0) > 1.2]
        if above_12:
            print(f"\nSharpe > 1.2 ({len(above_12)}):")
            for r in sorted(above_12, key=lambda x: x.get("metrics", {}).get("sharpe", 0), reverse=True):
                print(f"  {r['id']}: Sharpe={r.get('metrics',{}).get('sharpe'):.2f}")

    return results


if __name__ == "__main__":
    run_batch()
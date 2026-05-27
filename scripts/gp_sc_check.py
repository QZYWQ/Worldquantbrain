#!/usr/bin/env python3
"""Gross Profitability — SC Verification via machine_lib.

Uses get_check_submission from integrated pipeline code.
"""
import json, time
from pathlib import Path
from datetime import datetime
from machine_lib import login, get_check_submission

OUT = Path("/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures")

# S>=1.0 candidates from 24h batch
CANDIDATES = [
    # (alpha_id, name, sharpe, fitness, turnover)
    ("xARnGv3q", "p3_gir_d252", 1.320, 0.930, 0.0300),
    ("3qzA5m80", "p4_densify_d3", 1.060, 0.730, 0.0254),
    ("MPkxZ3Ra", "p4_densify_d0", 1.050, 0.720, 0.0369),
    ("rKAW8Xe8", "p4_densify_d6", 1.050, 0.720, 0.0206),
    ("58Mv5a0n", "p3_gir_d126", 0.990, 0.570, 0.0378),
    ("mLZXK3g6", "p1_gimax_sind", 0.950, 0.550, 0.0171),
    ("2rJKXwM5", "p3_gir_assets", 0.900, 0.540, 0.0233),
    ("xARnEZ9W", "p4_rank_wrap", 0.930, 0.560, 0.0252),
    ("zqOWnMbR", "p4_gimax_dens0", 0.890, 0.560, 0.0327),
]

s = login()

results = []
for aid, name, sharpe, fitness, tvr in CANDIDATES:
    print(f"\n  ▶ {name} ({aid}) S={sharpe:.3f} F={fitness:.3f} TVR={tvr:.4f}...", end=" ", flush=True)

    sc = get_check_submission(s, aid)

    if sc == "sleep":
        print("SESSION_EXPIRED", flush=True)
        s = login()
        continue
    elif sc == "fail":
        print("❌ FAIL (some check not passed)", flush=True)
        results.append({"alpha_id": aid, "name": name, "selfcorr": None, "status": "FAIL"})
    elif sc == "error":
        print("❌ CHECK_ERROR", flush=True)
        results.append({"alpha_id": aid, "name": name, "selfcorr": None, "status": "CHECK_ERROR"})
    elif sc is None or sc != sc:
        print("⚠️  SC pending or NaN", flush=True)
        results.append({"alpha_id": aid, "name": name, "selfcorr": None, "status": "PENDING"})
    else:
        sc_val = round(sc, 4)
        pass_8 = "PASS" if (sharpe >= 1.5 or sc_val < 0.7) else "NEAR"
        sc_flag = "✓" if (pass_8 == "PASS") else "⚠️ "
        print(f"{sc_flag} SC={sc_val:.4f} {pass_8}", flush=True)
        results.append({"alpha_id": aid, "name": name, "selfcorr": sc_val, "status": pass_8})

    time.sleep(2)

print("\n" + "=" * 70, flush=True)
print("SC VERIFICATION RESULTS", flush=True)
print("=" * 70, flush=True)
print(f"{'Name':<20} {'Sharpe':<8} {'Fitness':<8} {'TVR':<8} {'SC':<10} {'Status':<10}", flush=True)
print("-" * 70, flush=True)
for r in sorted([r for r in results], key=lambda x: {"PASS": 0, "NEAR": 1, "PENDING": 2, "FAIL": 3, "CHECK_ERROR": 4}.get(x["status"], 5)):
    c = next((c for c in CANDIDATES if c[0] == r["alpha_id"]), None)
    s_str = f'{r["selfcorr"]:.4f}' if r["selfcorr"] else "?"
    print(f'{r["name"]:<20} {c[2]:<8.3f if c else "?":<8} {c[3]:<8.3f if c else "?":<8} {c[4]:<8.4f if c else "?":<8} {s_str:<10} {r["status"]:<10}', flush=True)

report = {
    "generated_at": datetime.now().isoformat(),
    "results": results,
}
with open(str(OUT / f"gp_sc_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"), "w") as f:
    json.dump(report, f, indent=2, default=str)
print(f"\nSaved: {OUT}/gp_sc_check_*.json", flush=True)

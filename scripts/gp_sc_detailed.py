#!/usr/bin/env python3
"""Gross Profitability — SC Detailed Check via BRAIN API.

Uses machine_lib.login but reads raw /check response for SC value
even when other checks (like LOW_SHARPE) fail.
"""
import json, time, pandas as pd
from pathlib import Path
from datetime import datetime
from machine_lib import login

OUT = Path("/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures")

CANDIDATES = [
    ("xARnGv3q", "p3_gir_d252", 1.320, 0.930, 0.0300),
    ("3qzA5m80", "p4_densify_d3", 1.060, 0.730, 0.0254),
    ("MPkxZ3Ra", "p4_densify_d0", 1.050, 0.720, 0.0369),
    ("rKAW8Xe8", "p4_densify_d6", 1.050, 0.720, 0.0206),
    ("58Mv5a0n", "p3_gir_d126", 0.990, 0.570, 0.0378),
    ("mLZXK3g6", "p1_gimax_sind", 0.950, 0.550, 0.0171),
    ("xARnEZ9W", "p4_rank_wrap", 0.930, 0.560, 0.0252),
    ("2rJKXwM5", "p3_gir_assets", 0.900, 0.540, 0.0233),
    ("zqOWnMbR", "p4_gimax_dens0", 0.890, 0.560, 0.0327),
]

def detailed_check(s, aid):
    """Fetch /check and return all check details + SC value."""
    r = s.get(f"https://api.worldquantbrain.com/alphas/{aid}/check")
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}"}
    try:
        data = r.json()
    except:
        return {"error": "parse error"}
    is_data = data.get("is", {})
    checks = is_data.get("checks", [])
    if not checks:
        return {"error": "no checks", "raw": str(data)[:200]}
    # Build check map
    cm = {}
    for c in checks:
        cm[c["name"]] = {"result": c.get("result"), "value": c.get("value")}
    sc_val = None
    for c in checks:
        if c["name"] == "SELF_CORRELATION":
            sc_val = c.get("value")
    return {"checks": cm, "selfcorr": sc_val}

s = login()

results = []
for aid, name, sharpe, fitness, tvr in CANDIDATES:
    print(f"\n  ▶ {name} ({aid}) S={sharpe:.3f} F={fitness:.3f} TVR={tvr:.4f}", flush=True)
    d = detailed_check(s, aid)
    if "error" in d:
        print(f"    Error: {d['error']}", flush=True)
        results.append({"name": name, "alpha_id": aid, "error": d["error"], "selfcorr": None})
        continue

    checks = d["checks"]
    sc_val = d["selfcorr"]
    fails = [k for k, v in checks.items() if v["result"] != "PASS"]

    sc_str = f"{sc_val:.4f}" if sc_val is not None else "?"
    print(f"    SC={sc_str}  Fails: {fails}", flush=True)

    for chk_name, chk_data in sorted(checks.items()):
        v = chk_data["value"]
        v_str = f"{v:.4f}" if isinstance(v, (int, float)) else str(v or "?")
        pf = "✓" if chk_data["result"] == "PASS" else "✗"
        print(f"      {pf} {chk_name:<30s} {v_str}", flush=True)

    results.append({
        "name": name, "alpha_id": aid,
        "sharpe": sharpe, "fitness": fitness, "turnover": tvr,
        "selfcorr": sc_val,
        "checks": {k: {"result": v["result"], "value": v["value"]} for k, v in checks.items()},
        "fails": fails,
    })
    time.sleep(2)

# Summary
print("\n" + "=" * 80, flush=True)
print("SC DETAILED REPORT", flush=True)
print("=" * 80, flush=True)
print(f"{'Name':<20} {'Sharpe':<8} {'SC':<10} {'Pass/Total':<12} {'Bottleneck':<20}", flush=True)
print("-" * 80, flush=True)
for r in sorted(results, key=lambda x: -(x.get("sharpe") or 0)):
    fails = r.get("fails", [])
    pass_count = 8 - len(fails)
    bottleneck = fails[0] if fails else "NONE"
    sc = r.get("selfcorr")
    sc_str = f"{sc:.4f}" if sc else "?"
    print(f'{r["name"]:<20} {r["sharpe"]:<8.3f} {sc_str:<10} {pass_count}/8          {bottleneck:<20}', flush=True)

# Save
report = {
    "generated_at": datetime.now().isoformat(),
    "results": results,
}
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
with open(str(OUT / f"gp_sc_detailed_{ts}.json"), "w") as f:
    json.dump(report, f, indent=2, default=str)
print(f"\nSaved: gp_sc_detailed_{ts}.json", flush=True)

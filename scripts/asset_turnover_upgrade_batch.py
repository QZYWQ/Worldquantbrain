#!/usr/bin/env python3
"""Asset Turnover — Targeted Upgrade (升阶) to reach submission threshold.

Current best: S=1.16 F=0.82 (need ~S≥1.2 F≥1.0)
Strategies: truncation, densify+market mix, decay sweep, window sweep
"""
import sys, json, time
from datetime import datetime
from pathlib import Path

from machine_lib import login, set_alpha_properties

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
RESULTS_DIR = PROJECT / "runs" / "simulation-captures"

BASE = {
    "instrumentType": "EQUITY", "region": "USA", "universe": "TOP3000",
    "delay": 1, "truncation": 0.08, "pasteurization": "ON",
    "testPeriod": "P0Y", "unitHandling": "VERIFY", "nanHandling": "ON",
    "language": "FASTEXPR", "visualization": False,
}

def ws(field, window=252, std=4):
    return "winsorize(ts_backfill(%s, %d), std=%d)" % (field, window, std)

def sa(x):
    return "add(abs(%s), 1)" % x

W_REV = ws("revenue")
W_ASST = ws("assets")
RA = "divide(%s, %s)" % (W_REV, sa(W_ASST))

# --- Upgrade variants ---
UPGRADES = [
    # 1. Tighter truncation (0.05 instead of 0.08)
    ("up_trunc_005", "group_rank(%s, subindustry)" % RA, 6, "SUBINDUSTRY", 0.05),
    ("up_trunc_densify_005",
     "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % RA,
     0, "INDUSTRY", 0.05),
    ("up_trunc_densify3_005",
     "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % RA,
     3, "INDUSTRY", 0.05),

    # 2. Market + subindustry hybrid composite
    ("up_hybrid_50_50",
     "group_rank(0.5*ts_rank(%s, 252) + 0.5*ts_rank(%s, market), subindustry)" % (RA, RA),
     6, "SUBINDUSTRY", 0.08),
    ("up_hybrid_densify_market",
     "group_rank(%s, densify(bucket(group_rank(%s, market), range='0.1,1,0.1')))" % (RA, RA),
     0, "MARKET", 0.08),

    # 3. Higher decay sweep
    ("up_decay12_subind",
     "group_rank(%s, subindustry)" % RA, 12, "SUBINDUSTRY", 0.08),
    ("up_decay12_densify",
     "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % RA, 12, "INDUSTRY", 0.08),
    ("up_decay12_market",
     "group_rank(%s, market)" % RA, 12, "MARKET", 0.08),

    # 4. Window sweep (ts_rank instead of raw group_rank)
    ("up_tr60_subind",
     "group_rank(ts_rank(%s, 60), subindustry)" % RA, 6, "SUBINDUSTRY", 0.08),
    ("up_tr90_subind",
     "group_rank(ts_rank(%s, 90), subindustry)" % RA, 6, "SUBINDUSTRY", 0.08),
    ("up_tr180_subind",
     "group_rank(ts_rank(%s, 180), subindustry)" % RA, 6, "SUBINDUSTRY", 0.08),

    # 5. Winsorize std=3 (tighter outlier control)
    ("up_ws3_subind",
     "group_rank(divide(%s, %s), subindustry)" % (ws("revenue", std=3), sa(ws("assets", std=3))),
     6, "SUBINDUSTRY", 0.08),
    ("up_ws3_densify",
     "group_rank(divide(%s, %s), densify(bucket(rank(cap), range='0.1,1,0.1')))" % (ws("revenue", std=3), sa(ws("assets", std=3))),
     3, "INDUSTRY", 0.08),

    # 6. Z-score of ratio
    ("up_zscore126_subind",
     "group_rank(ts_zscore(%s, 126), subindustry)" % RA, 6, "SUBINDUSTRY", 0.08),
    ("up_zscore252_subind",
     "group_rank(ts_zscore(%s, 252), subindustry)" % RA, 6, "SUBINDUSTRY", 0.08),
]

def simulate(s, expr, name, decay, neut, trunc):
    settings = dict(BASE, decay=decay, neutralization=neut, truncation=trunc)
    sim_data = {"type": "REGULAR", "settings": settings, "regular": expr}
    resp = s.post("https://api.worldquantbrain.com/simulations", json=sim_data)
    if resp.status_code != 201:
        print("  ❌ HTTP %d" % resp.status_code, flush=True)
        return None
    url = resp.headers["Location"]
    for _ in range(180):
        time.sleep(5)
        prog = s.get(url)
        retry = prog.headers.get("Retry-After")
        if retry: time.sleep(float(retry)); continue
        if prog.status_code != 200: continue
        status = prog.json().get("status", "")
        if status in ("COMPLETE", "WARNING"):
            alpha_id = prog.json().get("alpha")
            if alpha_id:
                try:
                    set_alpha_properties(s, alpha_id, name="at_up_" + name,
                                         color="YELLOW", tags=["asset_turnover_upgrade"])
                except: pass
                ad = s.get("https://api.worldquantbrain.com/alphas/%s" % alpha_id).json()
                ism = ad.get("is", {})
                return {"alpha_id": alpha_id, "name": name,
                        "sharpe": ism.get("sharpe"), "fitness": ism.get("fitness"),
                        "turnover": ism.get("turnover")}
        elif status in ("CANCELLED", "ERROR"):
            print("  ❌ %s" % status, flush=True)
            return None
    return None

s = login()
print("Asset Turnover — Target Upgrade (升阶)", flush=True)
print("Variants: %d" % len(UPGRADES), flush=True)
results = []
START = 3
for idx, (name, expr, decay, neut, trunc) in enumerate(UPGRADES):
    if idx < START: continue
    print("\n  ▶ %s... (d=%d n=%s tr=%.2f)" % (name, decay, neut, trunc), flush=True)
    print("    expr: %s..." % expr[:70], flush=True)
    r = simulate(s, expr, name, decay, neut, trunc)
    if r:
        print("    ✅ S=%.2f F=%.2f TVR=%.4f" % (r["sharpe"], r["fitness"], r["turnover"]), flush=True)
        results.append(r)
    else:
        results.append({"name": name, "status": "FAILED"})
    time.sleep(4)

print("\n" + "=" * 60, flush=True)
print("  UPGRADE RESULTS", flush=True)
print("=" * 60, flush=True)
passes = [r for r in results if r.get("sharpe") is not None]
passes.sort(key=lambda x: x.get("sharpe", 0), reverse=True)
for r in passes:
    print("  %-30s S=%.2f F=%.2f TVR=%.4f" % (r["name"], r["sharpe"], r["fitness"], r["turnover"]), flush=True)

# Save
report = {"started": datetime.now().isoformat(), "results": results}
out = RESULTS_DIR / ("asset-turnover-upgrade-%s.json" % datetime.now().strftime("%Y%m%d_%H%M%S"))
out.write_text(json.dumps(report, indent=2, default=str))
print("\n  Saved: %s" % out, flush=True)

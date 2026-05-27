#!/usr/bin/env python3
"""Fix UNITS, re-simulate best p3, then trigger SC check.

Uses machine_lib.login — integrated pipeline code.
"""
import json, time, pandas as pd
from pathlib import Path
from datetime import datetime
from machine_lib import login

OUT = Path("/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures")
BASE = {
    "instrumentType":"EQUITY","region":"USA","universe":"TOP3000",
    "delay":1,"truncation":0.08,"pasteurization":"ON",
    "testPeriod":"P0Y","unitHandling":"IGNORE",  # FIX: IGNORE units for ratio
    "nanHandling":"ON","language":"FASTEXPR","visualization":False,
}

def sim(s, expr, name, decay=0, neut="SUBINDUSTRY"):
    payload = {"type":"REGULAR","settings":dict(BASE, decay=decay, neutralization=neut),"regular":expr}
    resp = s.post("https://api.worldquantbrain.com/simulations", json=payload)
    if resp.status_code != 201:
        print(f"    ❌ POST {resp.status_code}: {resp.text[:100]}", flush=True)
        return None
    url = resp.headers.get("Location")
    for _ in range(120):
        prog = s.get(url)
        if prog.headers.get("Retry-After"):
            time.sleep(float(prog.headers["Retry-After"])); continue
        data = prog.json()
        st = data.get("status"); aid = data.get("alpha")
        if st in ("COMPLETE","WARNING") and aid:
            ad = s.get(f"https://api.worldquantbrain.com/alphas/{aid}").json()
            im = ad.get("is",{})
            return {
                "alpha_id":aid,"name":name,"expression":expr,
                "sharpe":im.get("sharpe"),"fitness":im.get("fitness"),
                "turnover":im.get("turnover"),"decay":decay,"neut":neut,
            }
        elif st == "ERROR":
            print(f"    ❌ ERROR: {data.get('error','?')}", flush=True); return None
        time.sleep(5)
    print("    ⏰ TIMEOUT", flush=True); return None

def poll_check(s, aid, max_wait=180):
    """Poll /check waiting for SC to compute. Returns (selfcorr, fail_names) or None."""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        r = s.get(f"https://api.worldquantbrain.com/alphas/{aid}/check")
        if r.headers.get("Retry-After"):
            time.sleep(float(r.headers["Retry-After"])); continue
        try:
            data = r.json()
            checks = data.get("is", {}).get("checks", [])
            if not checks:
                time.sleep(10); continue
            sc_val = None
            for c in checks:
                if c["name"] == "SELF_CORRELATION":
                    sc_val = c.get("value")
            fails = [c["name"] for c in checks if c["result"] != "PASS"]
            return sc_val, fails, checks
        except:
            time.sleep(5)
    return None, None, None

s = login()

# ===== STEP 1: Re-simulate p3_gir_d252 with unitHandling=IGNORE =====
print("=" * 70, flush=True)
print("STEP 1: Re-simulate p3_gir_d252 with unitHandling=IGNORE", flush=True)
print("=" * 70, flush=True)

expr = "group_rank(ts_delta((gross_income_reported_value) / add(abs(total_assets_amount), 1), 252), subindustry)"
r = sim(s, expr, "p3_gir_d252_fixed", 6, "SUBINDUSTRY")
if r:
    aid = r["alpha_id"]
    print(f"  ✓ S={r['sharpe']:.3f} F={r['fitness']:.3f} TVR={r['turnover']:.4f} ({aid})", flush=True)
else:
    print("  ❌ sim failed", flush=True)
    aid = None

# ===== STEP 2: Also test p1_gimax_sind (high SubU) =====
print("\n" + "=" * 70, flush=True)
print("STEP 2: Re-simulate p1_gimax_sind with unitHandling=IGNORE", flush=True)
print("=" * 70, flush=True)

expr2 = "group_rank((gross_income_max) / add(abs(total_assets_amount), 1), subindustry)"
r2 = sim(s, expr2, "p1_gimax_sind_fixed", 0, "SUBINDUSTRY")
if r2:
    aid2 = r2["alpha_id"]
    print(f"  ✓ S={r2['sharpe']:.3f} F={r2['fitness']:.3f} TVR={r2['turnover']:.4f} ({aid2})", flush=True)
else:
    aid2 = None

# ===== STEP 3: Also try rank wrapper fix =====
print("\n" + "=" * 70, flush=True)
print("STEP 3: rank wrapper alternative (units-neutral)", flush=True)
print("=" * 70, flush=True)
expr3 = "group_rank(ts_delta(rank(gross_income_reported_value) / add(abs(rank(total_assets_amount)), 1), 252), subindustry)"
r3 = sim(s, expr3, "p3_gir_rank_units", 6, "SUBINDUSTRY")
if r3:
    aid3 = r3["alpha_id"]
    print(f"  ✓ S={r3['sharpe']:.3f} F={r3['fitness']:.3f} TVR={r3['turnover']:.4f} ({aid3})", flush=True)
else:
    aid3 = None

# ===== STEP 4: Wait then SC check =====
print("\n" + "=" * 70, flush=True)
print("STEP 4: SC check (waiting 120s for computation)", flush=True)
print("=" * 70, flush=True)
time.sleep(120)

for label, aid_val in [("p3_gir_d252_fixed", aid), ("p1_gimax_sind_fixed", aid2), ("p3_gir_rank_units", aid3)]:
    if not aid_val: continue
    print(f"\n  ▶ {label} ({aid_val})", flush=True)
    sc, fails, checks = poll_check(s, aid_val, max_wait=120)
    if sc is not None:
        sc_str = f"{sc:.4f}" if isinstance(sc, float) else str(sc)
        print(f"    SC={sc_str}  Failures: {fails}", flush=True)
    elif fails:
        print(f"    SC pending. Known failures: {fails}", flush=True)
    else:
        print(f"    Still computing...", flush=True)

print("\nDone.", flush=True)

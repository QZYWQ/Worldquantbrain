#!/usr/bin/env python3
"""GP — Fitness boost for p3_gir_d252.

Target F>=1.0, SubU>=0.7.
Strategies: decay sweep, neut change, window change, quantile trim.
"""
import json, time
from pathlib import Path
from machine_lib import login, set_alpha_properties

OUT = Path("/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures")
BASE = {
    "instrumentType":"EQUITY","region":"USA","universe":"TOP3000",
    "delay":1,"truncation":0.08,"pasteurization":"ON",
    "testPeriod":"P0Y","unitHandling":"VERIFY","nanHandling":"ON",
    "language":"FASTEXPR","visualization":False,
}

s = login()

def sim(sess, expr, name, decay=0, neut="SUBINDUSTRY"):
    payload = {"type":"REGULAR","settings":dict(BASE, decay=decay, neutralization=neut),"regular":expr}
    resp = sess.post("https://api.worldquantbrain.com/simulations", json=payload)
    if resp.status_code != 201:
        print(f"POST {resp.status_code}", flush=True); return None
    url = resp.headers.get("Location")
    for _ in range(120):
        pr = sess.get(url)
        if pr.headers.get("Retry-After"): time.sleep(float(pr.headers["Retry-After"])); continue
        d = pr.json(); st = d.get("status"); aid = d.get("alpha")
        if st in ("COMPLETE","WARNING") and aid:
            ad = sess.get(f"https://api.worldquantbrain.com/alphas/{aid}").json()
            im = ad.get("is",{})
            return {"alpha_id":aid,"name":name,"sharpe":im.get("sharpe"),"fitness":im.get("fitness"),
                    "turnover":im.get("turnover"),"decay":decay,"neut":neut}
        elif st == "ERROR": print(f"ERROR: {d.get('error','?')}", flush=True); return None
        time.sleep(5)
    return None

def check(sess, aid):
    r = sess.get(f"https://api.worldquantbrain.com/alphas/{aid}/check")
    if r.status_code != 200: return None, None
    try:
        cks = r.json().get("is",{}).get("checks",[])
        if not cks: return None, None
        sc = next((c.get("value") for c in cks if c["name"]=="SELF_CORRELATION"), None)
        fails = [c["name"] for c in cks if c["result"]!="PASS"]
        subu = next((c.get("value") for c in cks if c["name"]=="LOW_SUB_UNIVERSE_SHARPE"), None)
        return sc, {"fails": fails, "subu": subu, "checks": {c["name"]:c.get("result") for c in cks}}
    except: return None, None

# Construct GP expression variants from the d252 best
GI_TA = "(gross_income_reported_value) / add(abs(total_assets_amount), 1)"
GI_TA_RAW = "gross_income_reported_value / add(abs(total_assets_amount), 1)"

variants = [
    # Decay sweep for Fitness
    ("fb_d252_d0",  "group_rank(ts_delta(%s, 252), subindustry)" % GI_TA_RAW, 0, "SUBINDUSTRY"),
    ("fb_d252_d12", "group_rank(ts_delta(%s, 252), subindustry)" % GI_TA_RAW, 12, "SUBINDUSTRY"),
    ("fb_d252_d20", "group_rank(ts_delta(%s, 252), subindustry)" % GI_TA_RAW, 20, "SUBINDUSTRY"),
    # Shorter delta windows (SubU boost)
    ("fb_d63_d6",   "group_rank(ts_delta(%s, 63), subindustry)" % GI_TA_RAW, 6, "SUBINDUSTRY"),
    ("fb_d84_d6",   "group_rank(ts_delta(%s, 84), subindustry)" % GI_TA_RAW, 6, "SUBINDUSTRY"),
    ("fb_d126_d6",  "group_rank(ts_delta(%s, 126), subindustry)" % GI_TA_RAW, 6, "SUBINDUSTRY"),
    ("fb_d189_d6",  "group_rank(ts_delta(%s, 189), subindustry)" % GI_TA_RAW, 6, "SUBINDUSTRY"),
    # Neut change
    ("fb_d252_ind", "group_rank(ts_delta(%s, 252), industry)" % GI_TA_RAW, 6, "INDUSTRY"),
    ("fb_d252_mkt", "group_rank(ts_delta(%s, 252), market)" % GI_TA_RAW, 6, "MARKET"),
    # Quantile trim (reduce extreme values, boost Fitness)
    ("fb_d252_q10", "group_rank(ts_delta(quantile(%s, 0.1), 252), subindustry)" % GI_TA_RAW, 6, "SUBINDUSTRY"),
    # GI_max delta
    ("fb_gimax_d252","group_rank(ts_delta((gross_income_max) / add(abs(total_assets_amount), 1), 252), subindustry)", 6, "SUBINDUSTRY"),
    # Combined level + delta
    ("fb_gir_levdel","group_rank(add(ts_rank(%s, 252), ts_rank(ts_delta(%s, 252), 252)), subindustry)" % (GI_TA, GI_TA), 6, "SUBINDUSTRY"),
]

results = []
for name, expr, decay, neut in variants:
    print(f"  ▶ {name:20s} d={decay} neut={neut:12s}...", end=" ", flush=True)
    r = sim(s, expr, name, decay, neut)
    if r and r.get("sharpe"):
        print(f"S={r['sharpe']:.3f} F={r['fitness']:.3f} TVR={r['turnover']:.4f}", end="", flush=True)
        # Quick SC peek
        sc, info = check(s, r["alpha_id"])
        if info:
            subu = info.get("subu")
            print(f" SubU={subu}" if subu else "", end="", flush=True)
        print(flush=True)
        r["alpha_id"] = r.get("alpha_id","")
        results.append(r)
    else:
        print("FAIL", flush=True)
    time.sleep(3)

print("\n" + "=" * 70, flush=True)
print("FITNESS BOOST RESULTS", flush=True)
print("=" * 70, flush=True)
ranked = sorted(results, key=lambda x: -(x.get("sharpe") or 0))
for i, r in enumerate(ranked[:15]):
    print(f"#{i+1:2d} {r['name']:20s} S={r['sharpe']:.3f} F={r['fitness']:.3f} TVR={r['turnover']:.4f}", flush=True)
print("=" * 70, flush=True)

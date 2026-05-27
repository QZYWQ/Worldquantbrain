#!/usr/bin/env python3
"""
Gross Profitability — Quick Sign Confirmation (Lightweight)
Tests minimal expressions first, then escalates complexity.
"""
import json, time
from pathlib import Path
from datetime import datetime
from machine_lib import login, set_alpha_properties

OUT = Path("/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures")
BASE = {
    "instrumentType":"EQUITY","region":"USA","universe":"TOP3000",
    "delay":1,"truncation":0.08,"pasteurization":"ON",
    "testPeriod":"P0Y","unitHandling":"VERIFY","nanHandling":"ON",
    "language":"FASTEXPR","visualization":False,
}

s = login()

# Simplified expressions — no heavy ts_backfill, just rank/group_rank
variants = [
    # L1: Raw ratio (level)
    ("gir_level_mkt", "rank(gross_income_reported_value / total_assets_amount)", 0, "NONE"),
    ("gir_level_i", "group_rank(gross_income_reported_value / total_assets_amount, industry)", 0, "INDUSTRY"),
    ("gir_level_si", "group_rank(gross_income_reported_value / total_assets_amount, subindustry)", 0, "SUBINDUSTRY"),
    ("gir_flip", "-group_rank(gross_income_reported_value / total_assets_amount, subindustry)", 0, "SUBINDUSTRY"),
    # L2: gimax alternative (ultra-virgin field)
    ("gimax_level_si", "group_rank(gross_income_max / total_assets_amount, subindustry)", 0, "SUBINDUSTRY"),
    # L3: constructed gross profit: revenue - cogs
    ("const_level_i", "group_rank((revenue - cogs) / total_assets_amount, industry)", 0, "INDUSTRY"),
    ("const_level_si", "group_rank((revenue - cogs) / total_assets_amount, subindustry)", 0, "SUBINDUSTRY"),
]

for name, expr, decay, neut in variants:
    print(f"\n  ▶ {name}...", end=" ", flush=True)
    sim_data = {"type":"REGULAR","settings":dict(BASE, decay=decay, neutralization=neut),"regular":expr}
    resp = s.post("https://api.worldquantbrain.com/simulations", json=sim_data)
    if resp.status_code != 201:
        print(f"POST {resp.status_code}: {resp.text[:100]}", flush=True)
        continue
    url = resp.headers.get("Location")
    done = False
    for _ in range(30):
        prog = s.get(url)
        ra = prog.headers.get("Retry-After")
        if ra: time.sleep(float(ra)); continue
        st = prog.json().get("status")
        aid = prog.json().get("alpha")
        if st in ("COMPLETE","WARNING") and aid:
            ad = s.get(f"https://api.worldquantbrain.com/alphas/{aid}").json()
            im = ad.get("is",{})
            sval = im.get("sharpe",0)
            fval = im.get("fitness",0)
            tval = im.get("turnover",0)
            print(f"S={sval:.3f} F={fval:.3f} TVR={tval:.4f}  ({aid})", flush=True)
            done = True
            break
        elif st == "ERROR":
            print(f"ERROR: {prog.json().get('error','?')}", flush=True)
            done = True
            break
        time.sleep(5)
    if not done:
        print("TIMEOUT", flush=True)

print("\nDone.", flush=True)

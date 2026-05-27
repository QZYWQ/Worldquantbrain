#!/usr/bin/env python3
"""Revenue Growth Momentum — Targeted SUS fix."""

import sys

import json, time
from datetime import datetime
from pathlib import Path
from machine_lib import login, set_alpha_properties

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")

# Core insight: SUS fails because revenue concentration in some market caps
# Fixes to try:
# 1. Winsorize revenue before ratio
# 2. Tighter truncation (0.05 instead of 0.08)
# 3. Revenue/assets (diversified by size)
# 4. Different densify group structure

VARIANTS = [
    # 1. Winsorize revenue outliers
    ("group_rank(ts_delta(winsorize(ts_backfill(revenue, 252), std=4), 21) / ts_mean(winsorize(ts_backfill(revenue, 252), std=4), 252), industry)",
     6, "INDUSTRY", "rev_mom_c_ws4_d6"),
    ("group_rank(ts_delta(winsorize(ts_backfill(revenue, 252), std=3), 21) / ts_mean(winsorize(ts_backfill(revenue, 252), std=3), 252), industry)",
     6, "INDUSTRY", "rev_mom_c_ws3_d6"),

    # 2. Revenue/assets ratio (auto-normalized by company size)
    ("group_rank(ts_delta(revenue / ts_mean(assets, 252), 21), industry)",
     6, "INDUSTRY", "rev_mom_c_ra_d6"),

    # 3. Tighter densify bands
    ("group_rank(ts_delta(revenue, 21) / ts_mean(revenue, 252), densify(bucket(rank(cap), range='0.2, 1, 0.2')))",
     0, "INDUSTRY", "rev_mom_c_dn2_d0"),

    # 4. Group by sector (wider group helps SUS)
    ("group_rank(ts_delta(revenue, 21) / ts_mean(revenue, 252), sector)",
     6, "SECTOR", "rev_mom_c_sct_d6"),

    # 5. Market neutralized, wider universe
    ("group_rank(ts_delta(revenue, 21) / ts_mean(revenue, 252), industry)",
     6, "INDUSTRY", None),  # skip - already S=1.52, SUS=0.57
]

def check(name, s):
    aid = None
    results_file = PROJECT / "runs" / "simulation-captures" / "revenue-momentum-a-20260525_220424.json"
    data = json.loads(results_file.read_text())
    for r in data.get('results',[]):
        if 'densify_d0' in r.get('name','') and r.get('alpha_id'):
            aid = r['alpha_id']
            break
    if not aid:
        return None
    r = s.get(f"https://api.worldquantbrain.com/alphas/{aid}/check")
    if r.status_code == 200 and r.text.strip():
        return r.json()
    return None

def submit_and_check(s):
    results = []
    for expr, decay, neut, name in VARIANTS:
        if name is None:
            continue
        sim_data = {'type':'REGULAR','settings':{
            'instrumentType':'EQUITY','region':'USA','universe':'TOP3000','delay':1,
            'decay':decay,'neutralization':neut,'truncation':0.08,'pasteurization':'ON',
            'testPeriod':'P0Y','unitHandling':'VERIFY','nanHandling':'ON',
            'language':'FASTEXPR','visualization':False},'regular':expr}

        print(f"\n  ▶ {name}...", flush=True)
        resp = s.post('https://api.worldquantbrain.com/simulations', json=sim_data)
        if resp.status_code != 201:
            print(f"    ❌ HTTP {resp.status_code}", flush=True)
            results.append({"name":name,"status":"FAILED"})
            continue
        progress_url = resp.headers.get('Location')
        if not progress_url:
            results.append({"name":name,"status":"NO_LOCATION"})
            continue

        for attempt in range(180):
            time.sleep(5)
            prog = s.get(progress_url)
            retry = prog.headers.get("Retry-After")
            if retry: time.sleep(float(retry)); continue
            if prog.status_code != 200:
                if attempt % 12 == 0: print(f"    ⏳ HTTP {prog.status_code}", flush=True)
                continue
            status = prog.json().get("status","")
            if status in ("COMPLETE","WARNING"):
                alpha_id = prog.json().get("alpha")
                if alpha_id:
                    set_alpha_properties(s, alpha_id, name=name, color="YELLOW", tags=["rev_momentum"])
                    a_resp = s.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
                    if a_resp.status_code == 200:
                        ad = a_resp.json(); ism = ad.get("is",{})
                        s_=ism.get("sharpe"); f_=ism.get("fitness"); t_=ism.get("turnover")
                        print(f"    ✅ {name}: S={s_:.2f} F={f_:.2f} TVR={t_:.4f}", flush=True)
                        results.append({"name":name,"alpha_id":alpha_id,"sharpe":s_,"fitness":f_,"turnover":t_})
                break
            elif status in ("CANCELLED","ERROR"):
                print(f"    ❌ {name}: {status}", flush=True)
                results.append({"name":name,"status":status})
                break
        else:
            print(f"    ❌ {name}: TIMEOUT", flush=True)
            results.append({"name":name,"status":"TIMEOUT"})
    return results

def main():
    print(f"Revenue Growth Momentum — SUS fix targeted", flush=True)
    print(f"Started: {datetime.now().isoformat()}", flush=True)
    s = login()
    results = submit_and_check(s)
    report = {"started_at":datetime.now().isoformat(),"phase":"C_sus_fix","results":results}
    out=PROJECT/"runs"/"simulation-captures"/f"revenue-momentum-c-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report,indent=2,default=str))
    print(f"\n{'='*60}",flush=True)
    for r in results:
        if r.get("sharpe"):
            print(f"  {r['name']}: S={r['sharpe']:.2f} F={r.get('fitness',0):.2f}",flush=True)
        else:
            print(f"  {r['name']}: {r.get('status','?')}",flush=True)

main()

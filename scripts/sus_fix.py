#!/usr/bin/env python3
"""Targeted SUS fix for densify_d0 — truncation, sign flip, densify bands."""

import sys, json, time
from pathlib import Path
from datetime import datetime
from machine_lib import login, set_alpha_properties

PROJECT = Path('/Users/zpdedn/Documents/project/Worldquantbrain')
OUTPUT = PROJECT / 'runs' / 'simulation-captures'

# densify_d0 expression: group_rank(revenue_delta, densify(bucket(rank(cap))))
REV = "ts_delta(revenue, 21) / ts_mean(revenue, 252)"

VARIANTS = [
    # 1. Tighter truncation (0.05)
    (f"group_rank({REV}, densify(bucket(rank(cap), range='0.1, 1, 0.1')))", 0, "INDUSTRY", 0.05, "sus_trunc05"),
    # 2. Very tight truncation (0.03)
    (f"group_rank({REV}, densify(bucket(rank(cap), range='0.1, 1, 0.1')))", 0, "INDUSTRY", 0.03, "sus_trunc03"),
    # 3. Sign flip
    (f"-group_rank({REV}, densify(bucket(rank(cap), range='0.1, 1, 0.1')))", 0, "INDUSTRY", 0.08, "sus_flip"),
    # 4. Wider densify bands (5 buckets instead of 10)
    (f"group_rank({REV}, densify(bucket(rank(cap), range='0.1, 1, 0.2')))", 0, "INDUSTRY", 0.08, "sus_wide"),
    # 5. Narrower densify bands (20 buckets)
    (f"group_rank({REV}, densify(bucket(rank(cap), range='0.05, 1, 0.05')))", 0, "INDUSTRY", 0.08, "sus_narrow"),
    # 6. No densify, industry group_rank with tight truncation (S=1.52 baseline)
    (f"group_rank({REV}, industry)", 6, "INDUSTRY", 0.05, "sus_indu_trunc"),
    # 7. Trade_when for high-volume only (filters out small caps)
    (f"trade_when(rank(ts_mean(volume, 60)) > 0.3, rank({REV}), -1)", 0, "INDUSTRY", 0.08, "sus_tw"),
]

def simulate(sess, expr, decay, neut, trunc, name):
    settings = {'instrumentType':'EQUITY','region':'USA','universe':'TOP3000','delay':1,
                'decay':decay,'neutralization':neut,'truncation':trunc,'pasteurization':'ON',
                'testPeriod':'P0Y','unitHandling':'VERIFY','nanHandling':'ON',
                'language':'FASTEXPR','visualization':False}
    r = sess.post('https://api.worldquantbrain.com/simulations',
                  json={'type':'REGULAR','settings':settings,'regular':expr})
    if r.status_code != 201: print(f'FAIL HTTP {r.status_code}', flush=True); return None
    url = r.headers.get('Location')
    if not url: print('NO_LOCATION', flush=True); return None
    for _ in range(120):
        time.sleep(5)
        p = sess.get(url)
        if p.headers.get('Retry-After'): time.sleep(float(p.headers['Retry-After'])); continue
        result = p.json()
        aid = result.get('alpha')
        if result.get('status') in ('COMPLETE','WARNING') and aid:
            try:
                ad = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}').json()
                ism = ad.get('is',{})
                return {'alpha_id':aid,'name':name,'sharpe':ism.get('sharpe'),
                        'fitness':ism.get('fitness'),'turnover':ism.get('turnover'),
                        'decay':decay,'neut':neut,'trunc':trunc}
            except: return {'alpha_id':aid,'name':name,'status':'NODATA'}
        elif result.get('status') == 'ERROR': return None
    return None

def check_sus(sess, results):
    print("\n检查 /check 状态:", flush=True)
    time.sleep(30)
    for r in results:
        aid = r['alpha_id']
        for retry in range(5):
            rc = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}/check')
            ra = rc.headers.get('Retry-After')
            if ra: time.sleep(float(ra)+1); continue
            try:
                cd = rc.json()
                checks = cd.get('is',{}).get('checks',[])
                if not checks: time.sleep(5); continue
                sus = next((c for c in checks if c['name']=='LOW_SUB_UNIVERSE_SHARPE'), None)
                if sus:
                    result = sus['result']; val = sus.get('value','?'); limit = sus.get('limit','?')
                    print(f"  {r['name']:15s} S={r['sharpe']:.2f} SUS: {result} value={val} limit={limit}", flush=True)
                break
            except: time.sleep(5)
        time.sleep(2)

def main():
    print("SUS Fix — 靶向修复 densify_d0", flush=True)
    s = login()
    results = []
    for expr, decay, neut, trunc, name in VARIANTS:
        print(f"  {name} (trunc={trunc} decay={decay})...", end=' ', flush=True)
        r = simulate(s, expr, decay, neut, trunc, name)
        if r: print(f"S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f}", flush=True)
        else: print("FAIL", flush=True)
        results.append(r); time.sleep(2)

    check_sus(s, results)

    print(f"\n{'='*60}", flush=True)
    print("SUMMARY:", flush=True)
    for r in results:
        if r:
            print(f"  {r['name']:15s} S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f}", flush=True)
        else:
            print(f"  FAILED", flush=True)

    report = {"family":"revenue_momentum","phase":"sus_fix","anchor":"densify_d0","results":results}
    p = OUTPUT/f'sus-fix-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    Path(p).write_text(json.dumps(report,indent=2,default=str))
    print(f"\n📁 {p}", flush=True)

main()

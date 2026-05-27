#!/usr/bin/env python3
"""Profit Margin — 升阶工厂 (densify + decay + SC check)."""

import sys, json, time
from pathlib import Path
from datetime import datetime
from machine_lib import login, set_alpha_properties

PROJECT = Path('/Users/zpdedn/Documents/project/Worldquantbrain')
OUTPUT = PROJECT / 'runs' / 'simulation-captures'

# Best margin anchor: group_rank(ts_delta(net_income_avg/revenue, 21) / ts_mean(net_income_avg/revenue, 63), industry)
# S=1.32, F=0.82, TVR=0.14
# Stage A: densify + decay on the anchor expression

EXPR = "ts_delta(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), 21) / ts_mean(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), 63)"

VARIANTS = [
    # 1. Densify variants (replicate revenue momentum +0.24 S trick)
    (f"group_rank({EXPR}, densify(bucket(rank(cap), range='0.1, 1, 0.1')))", 0, "INDUSTRY", "margin_up_df0"),
    (f"group_rank({EXPR}, densify(bucket(rank(cap), range='0.1, 1, 0.1')))", 3, "INDUSTRY", "margin_up_df3"),
    (f"group_rank({EXPR}, densify(bucket(rank(cap), range='0.1, 1, 0.1')))", 6, "INDUSTRY", "margin_up_df6"),

    # 2. Decay sweep on core
    (f"group_rank({EXPR}, industry)", 0, "INDUSTRY", "margin_up_d0"),
    (f"group_rank({EXPR}, industry)", 3, "INDUSTRY", "margin_up_d3"),
    (f"group_rank({EXPR}, industry)", 6, "INDUSTRY", "margin_up_d6"),
    (f"group_rank({EXPR}, industry)", 10, "INDUSTRY", "margin_up_d10"),

    # 3. Subindustry
    (f"group_rank({EXPR}, subindustry)", 0, "SUBINDUSTRY", "margin_up_sub0"),
    (f"group_rank({EXPR}, subindustry)", 6, "SUBINDUSTRY", "margin_up_sub6"),

    # 4. Sector (wider group)
    (f"group_rank({EXPR}, sector)", 0, "SECTOR", "margin_up_sct0"),
    (f"group_rank({EXPR}, sector)", 6, "SECTOR", "margin_up_sct6"),

    # 5. Market
    (f"group_rank({EXPR}, market)", 0, "MARKET", "margin_up_mkt0"),
    (f"group_rank({EXPR}, market)", 6, "MARKET", "margin_up_mkt6"),
]

def simulate(sess, expr, decay, neut, name):
    settings = {'instrumentType':'EQUITY','region':'USA','universe':'TOP3000','delay':1,
                'decay':decay,'neutralization':neut,'truncation':0.08,'pasteurization':'ON',
                'testPeriod':'P0Y','unitHandling':'VERIFY','nanHandling':'ON',
                'language':'FASTEXPR','visualization':False}
    r = sess.post('https://api.worldquantbrain.com/simulations',
                  json={'type':'REGULAR','settings':settings,'regular':expr})
    if r.status_code != 201:
        print(f'FAIL (HTTP {r.status_code})', flush=True)
        return None
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
                        'fitness':ism.get('fitness'),'turnover':ism.get('turnover'),'decay':decay,'neut':neut}
            except: return {'alpha_id':aid,'name':name,'status':'NODATA'}
        elif result.get('status') == 'ERROR': return None
    return None

def main():
    print(f"Profit Margin — 升阶工厂", flush=True)
    print(f"Started: {datetime.now().isoformat()}", flush=True)
    print(f"Variants: {len(VARIANTS)}\n", flush=True)

    s = login()

    # Phase 1: Simulate
    print("Phase 1: 模拟升阶变体", flush=True)
    all_new = []
    for expr, decay, neut, name in VARIANTS:
        print(f"  {name}...", end=' ', flush=True)
        r = simulate(s, expr, decay, neut, name)
        if r:
            print(f"S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f}", flush=True)
            all_new.append(r)
        else:
            print("FAIL", flush=True)
        time.sleep(2)

    print(f"\n模拟完成: {len(all_new)}/{len(VARIANTS)}", flush=True)

    # Phase 2: Wait + SC check
    print("\n⏳ 等待60秒让SC计算...", flush=True)
    time.sleep(60)

    print("Phase 2: 批量检查SC", flush=True)
    eight_pass = []
    seven_pass = []

    for i, r in enumerate(all_new):
        if r['sharpe'] < 1.25 or r['turnover'] > 0.6:
            print(f"  [{i+1}/{len(all_new)}] {r['name']} S={r['sharpe']:.2f} — 跳过(S<1.25)", flush=True)
            continue

        print(f"  [{i+1}/{len(all_new)}] {r['name']} S={r['sharpe']:.2f}...", end=' ', flush=True)
        aid = r['alpha_id']

        for retry in range(15):
            rc = s.get(f'https://api.worldquantbrain.com/alphas/{aid}/check')
            ra = rc.headers.get('Retry-After')
            if ra: time.sleep(float(ra)+1); continue
            try:
                cd = rc.json()
                checks = cd.get('is',{}).get('checks',[])
                if not checks: time.sleep(5); continue
                fails = [c['name'] for c in checks if c['result']!='PASS']
                sc_val = next((c.get('value') for c in checks if c['name']=='SELF_CORRELATION'), None)
                r['sc'] = sc_val; r['fails'] = fails
                print(f"fail={fails} SC={sc_val}", flush=True)

                if not fails and r['sharpe']>=1.5 and r['turnover']<0.6:
                    print(f"  → ✅ 8-PASS!", flush=True)
                    eight_pass.append(r)
                else:
                    seven_pass.append(r)
                break
            except: time.sleep(5)
        else:
            print("PENDING", flush=True)
        time.sleep(2)

    # Report
    print(f"\n{'='*60}", flush=True)
    print(f"RESULT: 8-PASS: {len(eight_pass)}, 7-PASS: {len(seven_pass)}", flush=True)
    print(f"{'='*60}", flush=True)

    for r in eight_pass:
        print(f"\n✅ {r['name']}: id={r['alpha_id']}", flush=True)
        print(f"   S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f} SC={r.get('sc')}", flush=True)

    print(f"\n7-PASS (S≥1.25):", flush=True)
    for r in sorted(seven_pass, key=lambda x: x.get('sharpe',0), reverse=True):
        print(f"  {r['name']:25s} S={r['sharpe']:.2f} F={r['fitness']:.2f} fails={r.get('fails',[])}", flush=True)

    print(f"\n其他变体:", flush=True)
    others = [r for r in all_new if r not in eight_pass and r not in seven_pass]
    for r in sorted(others, key=lambda x: x.get('sharpe',0), reverse=True):
        print(f"  {r['name']:25s} S={r['sharpe']:.2f}", flush=True)

    # Save
    final = {
        'timestamp': datetime.now().isoformat(),
        'family': 'profit_margin',
        'phase': 'densify_upgrade',
        'anchor': EXPR,
        'eight_pass': [{'id':r['alpha_id'],'name':r['name'],'s':r['sharpe'],
                        'f':r['fitness'],'tvr':r['turnover'],'sc':r.get('sc')} for r in eight_pass],
        'seven_pass': [{'id':r['alpha_id'],'name':r['name'],'s':r['sharpe'],
                        'f':r['fitness'],'tvr':r['turnover'],'fails':r.get('fails'),'sc':r.get('sc')} for r in seven_pass],
    }
    p = OUTPUT / f'margin-upgrade-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    Path(p).write_text(json.dumps(final,indent=2,default=str))
    print(f"\n📁 {p}", flush=True)

main()

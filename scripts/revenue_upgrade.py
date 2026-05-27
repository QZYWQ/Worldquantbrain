#!/usr/bin/env python3
"""Revenue Momentum — 升阶工厂 + SC check."""

import sys, json, time
from pathlib import Path
from datetime import datetime
from machine_lib import login, set_alpha_properties

PROJECT = Path('/Users/zpdedn/Documents/project/Worldquantbrain')
OUTPUT = PROJECT / 'runs' / 'simulation-captures'

# Two base expressions to upgrade
BASES = [
    {
        'expr': 'ts_delta(revenue, 21) / ts_mean(revenue, 252)',
        's': 1.52, 'f': 1.24, 'tvr': 0.119,
        'name': 'rev_mom_core',
    },
    {
        'expr': 'ts_delta(revenue, 21) / ts_mean(revenue, 252)',
        's': 1.76, 'f': 1.35, 'tvr': 0.159,
        'name': 'rev_mom_densify',
        'base_group': "densify(bucket(rank(cap), range='0.1, 1, 0.1'))",
    },
]

def generate_variants():
    v = []
    for base in BASES:
        e = base['expr']
        nm = base['name']
        grp = base.get('base_group', 'industry')

        # Core group_rank (our anchor)
        for d in [0, 3, 6, 10]:
            v.append((f'group_rank({e}, {grp})', d, 'INDUSTRY', f'{nm}_g{d}'))

        # rank wrapper
        for d in [0, 6, 15]:
            v.append((f'rank(group_rank({e}, {grp}))', d, 'INDUSTRY', f'{nm}_rk{d}'))

        # zscore wrapper
        for d in [0, 6]:
            v.append((f'zscore(group_rank({e}, {grp}))', d, 'INDUSTRY', f'{nm}_zs{d}'))

        # ts_zscore
        for d in [0, 6]:
            for w in [63, 126]:
                v.append((f'ts_zscore(group_rank({e}, {grp}), {w})', d, 'INDUSTRY', f'{nm}_tz{w}_d{d}'))

        # Market group
        v.append((f'group_rank({e}, market)', 0, 'MARKET', f'{nm}_mkt'))

        # Subindustry
        for d in [0, 6]:
            v.append((f'group_rank({e}, subindustry)', d, 'SUBINDUSTRY', f'{nm}_sub{d}'))

        # Sign flip
        v.append((f'-group_rank({e}, {grp})', 0, 'INDUSTRY', f'{nm}_flip'))

        # Quantile
        v.append((f'quantile(group_rank({e}, {grp}), 0.1)', 0, 'INDUSTRY', f'{nm}_qt'))

        # ts_mean
        v.append((f'ts_mean(group_rank({e}, {grp}), 22)', 0, 'INDUSTRY', f'{nm}_tm22'))

        # Subindustry with densify (special SUS fix attempt)
        if grp != 'industry':
            v.append((f'group_rank({e}, subindustry)', 0, 'SUBINDUSTRY', f'{nm}_sub_d0'))

    return v

def simulate(sess, expr, name, decay, neut):
    settings = {'instrumentType':'EQUITY','region':'USA','universe':'TOP3000',
                'delay':1,'decay':decay,'neutralization':neut,'truncation':0.08,
                'pasteurization':'ON','testPeriod':'P2Y','unitHandling':'VERIFY',
                'nanHandling':'ON','language':'FASTEXPR','visualization':False}
    r = sess.post('https://api.worldquantbrain.com/simulations',
                  json={'type':'REGULAR','settings':settings,'regular':expr})
    if r.status_code != 201: return None
    url = r.headers.get('Location')
    if not url: return None
    for _ in range(120):
        time.sleep(5)
        prog = sess.get(url)
        if prog.headers.get('Retry-After'): time.sleep(float(prog.headers['Retry-After'])); continue
        result = prog.json()
        aid = result.get('alpha')
        if result.get('status') in ('COMPLETE','WARNING') and aid:
            ad = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}').json()
            ism = ad.get('is',{})
            return {'alpha_id':aid,'name':name,'sharpe':ism.get('sharpe'),
                    'fitness':ism.get('fitness'),'turnover':ism.get('turnover'),
                    'decay':decay,'neut':neut}
        elif result.get('status') == 'ERROR': return None
    return None

def check_sc(sess, results):
    """Check SC for all S>=1.25 variants, including against submitted+favorites."""
    print(f"\n⏳ 等待 SC 计算...", flush=True)
    time.sleep(60)

    eight_pass = []
    seven_pass = []

    for i, r in enumerate(results):
        if r['sharpe'] < 1.25 or r['turnover'] > 0.6:
            continue
        aid = r['alpha_id']
        print(f"\n  [{i+1}/{sum(1 for x in results if x['sharpe']>=1.25)}] {r['name']} S={r['sharpe']:.2f}...", end=' ', flush=True)

        for retry in range(15):
            rc = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}/check')
            ra = rc.headers.get('Retry-After')
            if ra: time.sleep(float(ra)+1); continue
            try:
                cd = rc.json()
                checks = cd.get('is',{}).get('checks',[])
                if not checks: time.sleep(5); continue

                fails = [c['name'] for c in checks if c['result']!='PASS']
                sc_val = next((c.get('value') for c in checks if c['name']=='SELF_CORRELATION'), None)
                r['sc'] = sc_val
                r['fails'] = fails

                print(f'fail={fails} SC={sc_val}', flush=True)

                if not fails and r['sharpe'] >= 1.5 and r['turnover'] < 0.6:
                    print(f'  → ✅ 8-PASS!', flush=True)
                    eight_pass.append(r)
                else:
                    seven_pass.append(r)
                break
            except: time.sleep(5)
        else:
            print('PENDING', flush=True)

    return eight_pass, seven_pass

def main():
    print(f"Revenue Momentum — 升阶工厂", flush=True)
    print(f"Started: {datetime.now().isoformat()}", flush=True)

    variants = generate_variants()
    print(f"Variants: {len(variants)}", flush=True)

    s = login()

    # Phase 1: Simulate all
    print(f"\nPhase 1: 模拟 {len(variants)} 变体", flush=True)
    all_new = []
    for expr, decay, neut, name in variants:
        print(f"  {name}...", end=' ', flush=True)
        r = simulate(s, expr, name, decay, neut)
        if r:
            print(f"S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f}", flush=True)
            all_new.append(r)
        else:
            print("FAIL", flush=True)
        time.sleep(2)

    print(f"\n模拟完成: {len(all_new)}/{len(variants)}", flush=True)

    # Phase 2: SC Check
    print(f"\nPhase 2: SC 检查", flush=True)
    eight, seven = check_sc(s, all_new)

    print(f"\n{'='*60}", flush=True)
    print(f"RESULT: 8-PASS: {len(eight)}, 7-PASS: {len(seven)}", flush=True)
    print(f"{'='*60}", flush=True)

    for r in eight:
        print(f"\n✅ {r['name']}: alpha_id={r['alpha_id']}", flush=True)
        print(f"   S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f} SC={r.get('sc')}", flush=True)

    for r in seven:
        print(f"\n{r['name']:35s} S={r['sharpe']:.2f} fails={r.get('fails',[])}", flush=True)

    # Save
    final = {
        'timestamp': datetime.now().isoformat(),
        'family': 'revenue_momentum',
        'eight_pass': [{'id':r['alpha_id'],'name':r['name'],'s':r['sharpe'],
                        'f':r['fitness'],'tvr':r['turnover'],'sc':r.get('sc')} for r in eight],
        'seven_pass': [{'id':r['alpha_id'],'name':r['name'],'s':r['sharpe'],
                        'f':r['fitness'],'tvr':r['turnover'],'sc':r.get('sc'),
                        'fails':r.get('fails')} for r in all_new if 1.0<=r.get('sharpe',0) and r not in eight],
    }
    p = OUTPUT / f'revenue-upgrade-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    Path(p).write_text(json.dumps(final,indent=2,default=str))
    print(f"\n📁 {p}", flush=True)

if __name__ == '__main__':
    main()

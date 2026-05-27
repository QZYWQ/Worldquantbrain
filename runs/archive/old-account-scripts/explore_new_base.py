#!/usr/bin/env python3
"""
探索新base字段 - 寻找Fitness>1.0且SelfCorr<0.7的候选
问题: close作为base时，group_*包装Fitness降到0.8-0.86
解决: 尝试returns/vwap/volume作为base
"""
import sys, json, time
from pathlib import Path
import requests

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.auth = ("zpdedn@gmail.com", "zp82648185000")
s.post('https://api.worldquantbrain.com/authentication')
print("Auth OK")

def inline_simulate_full(expr, name, decay=0, neutralization='SUBINDUSTRY'):
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': neutralization,
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    r = s.post('https://api.worldquantbrain.com/simulations', json={'type': 'REGULAR', 'settings': settings, 'regular': expr})
    if r.status_code != 201:
        return {'name': name, 'status': f'POST_FAIL_{r.status_code}', 'expression': expr}
    url = r.headers['Location']
    for _ in range(120):
        prog = s.get(url)
        h = prog.headers
        if h.get('Retry-After'):
            time.sleep(float(h['Retry-After']))
            continue
        result = prog.json()
        status = result.get('status')
        alpha_id = result.get('alpha')
        if status in ('COMPLETE', 'WARNING') and alpha_id:
            ad = s.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}').json()
            is_m = ad.get('is', {})
            checks = is_m.get('checks', [])
            return {
                'alpha_id': alpha_id, 'name': name, 'expression': expr,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'margin': is_m.get('margin'),
                'longCount': is_m.get('longCount', 0), 'shortCount': is_m.get('shortCount', 0),
                'selfcorr': next((c.get('value') for c in checks if c.get('name') == 'SELF_CORRELATION'), None),
                'checks': checks
            }
        time.sleep(5)
    return {'name': name, 'status': 'TIMEOUT', 'expression': expr}

print("="*80)
print("探索新Base字段 - 寻找Fitness>1.0且SelfCorr<0.7的Alpha")
print("="*80)

# 不同base字段的候选
CANDIDATES = [
    # 1. returns作为base (与close不同，可能selfcorr低)
    ("rank(-ts_zscore(returns, 5))", 0, "SUBINDUSTRY"),
    ("rank(-ts_zscore(returns, 10))", 0, "SUBINDUSTRY"),
    ("rank(-ts_zscore(returns, 20))", 0, "SUBINDUSTRY"),
    ("ts_zscore(returns, 5)", 0, "SUBINDUSTRY"),
    ("-ts_zscore(returns, 5)", 0, "SUBINDUSTRY"),

    # 2. vwap作为base
    ("rank(-ts_zscore(vwap, 5))", 0, "SUBINDUSTRY"),
    ("rank(-ts_zscore(vwap, 10))", 0, "SUBINDUSTRY"),
    ("-ts_zscore(vwap, 5)", 0, "SUBINDUSTRY"),

    # 3. volume作为base
    ("rank(-ts_zscore(volume, 5))", 0, "SUBINDUSTRY"),
    ("rank(-ts_zscore(volume, 10))", 0, "SUBINDUSTRY"),
    ("-ts_zscore(volume, 5)", 0, "SUBINDUSTRY"),

    # 4. 复合returns+close (可能降低selfcorr)
    ("rank(-ts_zscore(returns, 5)) * rank(-ts_zscore(close, 5))", 0, "SUBINDUSTRY"),
    ("rank(-ts_zscore(returns, 5)) + rank(-ts_zscore(close, 5))", 0, "SUBINDUSTRY"),

    # 5. 行业相对value (mdl77相关)
    ("rank(-ts_zscore(mdl77_25yearrelativevaluefactor_rel5yfcfp, 5))", 0, "SUBINDUSTRY"),
    ("rank(-ts_zscore(mdl77_fangma_mam5, 5))", 0, "SUBINDUSTRY"),

    # 6. 换neutralization - INDUSTRY可能不同
    ("rank(-ts_zscore(returns, 5))", 0, "INDUSTRY"),
    ("rank(-ts_zscore(vwap, 5))", 0, "INDUSTRY"),
]

results = []
for i, (expr, decay, neut) in enumerate(CANDIDATES):
    name = f'explore_{i+1}'
    print(f"\n[{name}] {expr[:65]}")
    r = inline_simulate_full(expr, name, decay=decay, neutralization=neut)
    results.append(r)

    if r.get('alpha_id'):
        sh = r.get('sharpe', 0) or 0
        ft = r.get('fitness', 0) or 0
        tv = r.get('turnover', 0) or 0
        sc = r.get('selfcorr')
        checks = r.get('checks', [])
        fail_names = [c['name'] for c in checks if c.get('result') == 'FAIL']
        print(f"  S={sh:.2f} F={ft:.2f} TVR={tv:.2f} SC={sc}")
        if fail_names:
            print(f"  FAIL: {fail_names}")
    else:
        print(f"  ❌ {r.get('status')}")
    time.sleep(3)

# 保存
save_path = OUTPUT_DIR / 'explore_new_base.json'
with open(save_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n已保存: {save_path}")

# 汇总
print("\n" + "="*80)
print("探索结果汇总")
print("="*80)

passing = []
for r in results:
    if not r.get('alpha_id'):
        continue
    sh = r.get('sharpe', 0) or 0
    ft = r.get('fitness', 0) or 0
    tv = r.get('turnover', 99) or 99
    sc = r.get('selfcorr', 1.0) or 1.0
    checks = r.get('checks', [])
    has_fail = any(c.get('result') == 'FAIL' for c in checks)

    if has_fail:
        status = "FAIL"
    elif sc > 0.7:
        status = "FAIL_SC"
    elif sh < 1.25 or ft < 1.0 or tv > 0.7:
        status = "FAIL_THRESH"
    else:
        status = "PASS"
        passing.append(r)

    print(f"\n[{status}] {r['expression'][:60]}")
    print(f"   S={sh:.2f} F={ft:.2f} TVR={tv:.2f} SC={sc:.4f}")

print(f"\n通过: {len(passing)}/{len(results)}")
if passing:
    print("\n✅ 可提交:")
    for r in passing:
        print(f"  {r['alpha_id']} | {r['expression'][:60]} | S={r['sharpe']:.2f} F={r['fitness']:.2f} SC={r.get('selfcorr')}")
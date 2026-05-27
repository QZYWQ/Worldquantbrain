#!/usr/bin/env python3
"""
对原始YPNaPkKA加decay降SelfCorr
不加任何其他改动，只增加decay
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

# 原始YPNaPkKA表达式（仅修改decay）
ORIGINAL_EXPR = "trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)"

print("="*80)
print("YPNaPkKA仅加Decay测试")
print("="*80)
print(f"原始表达式: {ORIGINAL_EXPR}\n")

# 测试不同decay值
DECAY_VALUES = [0, 3, 5, 7, 10, 12, 15, 20]

results = []
for decay in DECAY_VALUES:
    name = f'decay_{decay}'
    print(f"[{name}] 测试decay={decay}")
    r = inline_simulate_full(ORIGINAL_EXPR, name, decay=decay, neutralization='SUBINDUSTRY')
    r['decay'] = decay
    results.append(r)

    if r.get('alpha_id'):
        sh = r.get('sharpe', 0) or 0
        ft = r.get('fitness', 0) or 0
        tv = r.get('turnover', 0) or 0
        sc = r.get('selfcorr')
        checks = r.get('checks', [])
        fail_names = [c['name'] for c in checks if c.get('result') == 'FAIL']
        pass_count = sum(1 for c in checks if c.get('result') == 'PASS')
        print(f"  S={sh:.2f} F={ft:.2f} TVR={tv:.2f} SC={sc} | {pass_count} PASS")
        if fail_names:
            print(f"  FAIL: {fail_names}")
    else:
        print(f"  ❌ {r.get('status')}")
    time.sleep(3)

# 保存
save_path = OUTPUT_DIR / 'ypnakka_decay_test.json'
with open(save_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n已保存: {save_path}")

# 汇总
print("\n" + "="*80)
print("Decay测试结果汇总")
print("="*80)
print(f"{'Decay':>6} | {'Sharpe':>8} | {'Fitness':>8} | {'TVR':>8} | {'SelfCorr':>10} | {'PASS#':>6} | {'Status'}")
print("-" * 80)

passing = []
for r in results:
    d = r.get('decay', 0)
    sh = r.get('sharpe', 0) or 0
    ft = r.get('fitness', 0) or 0
    tv = r.get('turnover', 0) or 0
    sc = r.get('selfcorr')
    checks = r.get('checks', [])
    pass_count = sum(1 for c in checks if c.get('result') == 'PASS')
    has_fail = any(c.get('result') == 'FAIL' for c in checks)

    # 判断状态
    if has_fail:
        # 检查是否是仅 SELF_CORRELATION fail
        fail_names = [c['name'] for c in checks if c.get('result') == 'FAIL']
        if fail_names == ['SELF_CORRELATION'] and sc is not None and sc <= 0.7:
            status = "✅ PASS"
            passing.append(r)
        elif 'LOW_FITNESS' in fail_names:
            status = "❌ LOW_FIT"
        elif 'SELF_CORRELATION' in fail_names:
            status = "❌ SELF_CORR"
        else:
            status = f"❌ {fail_names}"
    elif sc is not None and sc > 0.7:
        status = "❌ SC>0.7"
    elif sh < 1.25 or ft < 1.0 or tv > 0.7:
        status = "❌ THRESH"
    else:
        status = "✅ PASS"
        passing.append(r)

    sc_str = f"{sc:.4f}" if sc is not None else "N/A"
    print(f"{d:>6} | {sh:>8.2f} | {ft:>8.2f} | {tv:>8.2f} | {sc_str:>10} | {pass_count:>6} | {status}")

print(f"\n通过: {len(passing)}/{len(results)}")

if passing:
    print("\n✅ 可提交:")
    for r in passing:
        print(f"  decay={r['decay']} | {r['alpha_id']} | S={r['sharpe']:.2f} F={r['fitness']:.2f} SC={r.get('selfcorr')}")
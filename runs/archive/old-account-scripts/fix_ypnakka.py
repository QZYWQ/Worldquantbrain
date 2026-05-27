#!/usr/bin/env python3
"""
修正YPNaPkKA - 解决SelfCorr(0.0033超限)和Unit问题
表达式: trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)
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
print("修正YPNaPkKA - SelfCorr=0.7033超限0.0033, Unit不兼容")
print("="*80)

# 原表达式的问题:
# 1. group_rank(ts_std_dev(returns,60), sector) > 0.7 - group_rank返回per-group scalar，不是matrix
# 2. abs(returns) > 0.1 - unit不匹配，returns是CSPrice类型
# 3. SelfCorr略超0.7

# 修复策略:
# A. 用外生volume/price条件替代sector rank条件 (解决unit问题)
# B. 添加decay降selfcorr
# C. 换exit condition

CANDIDATES = [
    # A1. volume相关性条件替代sector rank
    ("trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)", 0, "SUBINDUSTRY"),

    # A2. 更严格volume条件
    ("trade_when(ts_corr(close, volume, 20) > 0.3, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)", 0, "SUBINDUSTRY"),

    # A3. 改变量纲条件
    ("trade_when(ts_zscore(volume, 20) > 1.5, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)", 0, "SUBINDUSTRY"),

    # A4. volume变化率条件
    ("trade_when(ts_std_dev(volume, 5) > ts_std_dev(volume, 20), rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)", 0, "SUBINDUSTRY"),

    # B1. 加decay降selfcorr
    ("trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)", 5, "SUBINDUSTRY"),

    # B2. 更大decay
    ("trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)", 10, "SUBINDUSTRY"),

    # B3. decay加到exit condition
    ("trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)", 15, "SUBINDUSTRY"),

    # C1. 换exit condition - 不用abs(returns)
    ("trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), -1)", 0, "SUBINDUSTRY"),

    # C2. 用ts_std_dev作为exit
    ("trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), ts_std_dev(returns, 5) > 0.05)", 0, "SUBINDUSTRY"),

    # C3. rank(volume)条件
    ("trade_when(rank(volume) > 0.8, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)", 0, "SUBINDUSTRY"),

    # D1. zscore包装降selfcorr
    ("zscore(trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1))", 0, "SUBINDUSTRY"),

    # D2. rank包装
    ("rank(trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1))", 0, "SUBINDUSTRY"),
]

results = []
for i, (expr, decay, neut) in enumerate(CANDIDATES):
    name = f'fix_{i+1}'
    print(f"\n[{name}] decay={decay} {expr[:70]}")
    r = inline_simulate_full(expr, name, decay=decay, neutralization=neut)
    results.append(r)

    if r.get('alpha_id'):
        sh = r.get('sharpe', 0) or 0
        ft = r.get('fitness', 0) or 0
        tv = r.get('turnover', 0) or 0
        sc = r.get('selfcorr')
        checks = r.get('checks', [])
        fail_names = [c['name'] for c in checks if c.get('result') == 'FAIL']
        pass_count = sum(1 for c in checks if c.get('result') == 'PASS')
        print(f"  S={sh:.2f} F={ft:.2f} TVR={tv:.2f} SC={sc} | {pass_count} PASS, {len(fail_names)} FAIL")
        if fail_names:
            print(f"  FAIL: {fail_names}")
    else:
        print(f"  ❌ {r.get('status')}")
    time.sleep(3)

# 保存
save_path = OUTPUT_DIR / 'fix_ypnakka.json'
with open(save_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n已保存: {save_path}")

# 汇总
print("\n" + "="*80)
print("修正结果汇总")
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
        print(f"  {r['alpha_id']} | S={r['sharpe']:.2f} F={r['fitness']:.2f} SC={r.get('selfcorr')} | {r['expression'][:60]}")
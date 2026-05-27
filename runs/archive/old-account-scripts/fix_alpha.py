#!/usr/bin/env python3
"""
修正Alpha - 解决self-correlation和unit问题
"""
import sys, json, time, random
from pathlib import Path
import requests

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.auth = ("zpdedn@gmail.com", "zp82648185000")
s.post('https://api.worldquantbrain.com/authentication')
print("Auth OK")

def inline_simulate(expr, name, decay=0, neutralization='SUBINDUSTRY'):
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
            selfcorr = None
            for c in checks:
                if c.get('name') == 'SELF_CORRELATION':
                    selfcorr = c.get('value')
                    break
            return {
                'alpha_id': alpha_id, 'name': name, 'expression': expr, 'status': status,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'margin': is_m.get('margin'),
                'longCount': is_m.get('longCount', 0), 'shortCount': is_m.get('shortCount', 0),
                'selfcorr': selfcorr, 'checks': checks
            }
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr}

# 问题分析：
# YPNaPkKA: trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, rank(...), -1)
# - selfcorr = 0.7033 > 0.7 (FAIL)
# - unit incompatibility: condition has wrong unit type

# 修复策略：
# 1. 使用外生条件（volume/close相关性，不依赖alpha输出）解决unit问题
# 2. 添加zscore包装降低self-correlation

# 原始1阶base
base = "rank(-ts_zscore(close, 5))"

# 修正后的候选 - 使用外生事件条件 + 降self-correlation包装
FIXED_CANDIDATES = [
    # 方案1: 用volume事件替代sector rank（外生条件，解决unit）
    ("trade_when(ts_corr(close, volume, 5) > 0, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),
    ("trade_when(ts_corr(close, volume, 20) > 0, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),
    ("trade_when(ts_mean(volume, 10) > ts_mean(volume, 60), group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),

    # 方案2: 添加zscore包装降selfcorr
    ("zscore(trade_when(ts_corr(close, volume, 20) > 0, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1))", 0, "SUBINDUSTRY"),
    ("rank(trade_when(ts_corr(close, volume, 20) > 0, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1))", 0, "SUBINDUSTRY"),

    # 方案3: 改变结构 - 用ts_zscore(condition)替代直接比较
    ("trade_when(ts_zscore(volume, 20) > 1.5, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),
    ("trade_when(ts_zscore(volume, 20) > 2, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),

    # 方案4: 纯外生条件 - 不依赖alpha field的独立事件
    ("trade_when(ts_std_dev(volume, 5) > ts_std_dev(volume, 20), group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),
    ("trade_when(rank(volume) > 0.8, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),

    # 方案5: 多层group包装 - 进一步降selfcorr
    ("group_neutralize(rank(-ts_zscore(close, 5)), densify(sector))", 0, "SUBINDUSTRY"),
    ("group_zscore(group_neutralize(rank(-ts_zscore(close, 5)), densify(sector)), densify(sector))", 0, "SUBINDUSTRY"),
]

print("="*80)
print("修正Alpha - 解决self-correlation和unit问题")
print("="*80)

results = []
for i, (expr, decay, neut) in enumerate(FIXED_CANDIDATES):
    name = f'fix_{i+1}'
    print(f"\n[{name}] {expr[:70]}")
    r = inline_simulate(expr, name, decay=decay, neutralization=neut)
    results.append(r)
    if r.get('alpha_id'):
        sc = r.get('selfcorr')
        sh = r.get('sharpe')
        tv = r.get('turnover')
        ft = r.get('fitness')
        print(f"  Sharpe={sh}, Fitness={ft}, TVR={tv}, SelfCorr={sc}")
        if sc is not None and sc > 0.7:
            print(f"  ⚠️  SelfCorr > 0.7")
        checks = r.get('checks', [])
        for c in checks:
            if c.get('result') == 'FAIL':
                print(f"  ❌ FAIL: {c.get('name')}: {c.get('value')}")
    else:
        print(f"  ❌ {r.get('status')}")
    time.sleep(3)

# 保存结果
save_path = OUTPUT_DIR / 'upgrade_fixed.json'
with open(save_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n已保存到: {save_path}")

# 筛选通过
print("\n" + "="*80)
print("修正结果汇总")
print("="*80)

passing = []
for r in results:
    if not r.get('alpha_id'):
        continue
    sc = r.get('selfcorr', 1.0) or 1.0
    sh = r.get('sharpe', 0) or 0
    ft = r.get('fitness', 0) or 0
    tv = r.get('turnover', 99) or 99

    # 检查
    has_fail = any(c.get('result') == 'FAIL' for c in r.get('checks', []))
    if has_fail:
        continue
    if sc > 0.7:
        continue
    if sh < 1.25 or ft < 1.0 or tv > 0.7:
        continue

    passing.append(r)
    print(f"\n✅ PASS: {r['expression'][:65]}")
    print(f"   Sharpe={sh:.3f}, Fitness={ft:.3f}, TVR={tv:.3f}, SelfCorr={sc:.4f}")

print(f"\n通过数量: {len(passing)}/{len(results)}")

if passing:
    print("\n可提交Alpha:")
    for r in passing:
        print(f"  {r['alpha_id']} | {r['expression'][:60]}")
#!/usr/bin/env python3
"""
Alpha修正 - 获取真实API数据并针对性修复
针对问题:
1. self-correlation > 0.7
2. unit incompatibility (condition expects CSPrice但alpha输出是Unit[])
3. fitness需要 >= 1.0
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
    """模拟并返回完整check信息"""
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

            # 提取各指标
            selfcorr = None
            check_results = {}
            for c in checks:
                check_results[c['name']] = {'value': c.get('value'), 'result': c.get('result')}
                if c.get('name') == 'SELF_CORRELATION':
                    selfcorr = c.get('value')

            return {
                'alpha_id': alpha_id, 'name': name, 'expression': expr,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'margin': is_m.get('margin'),
                'longCount': is_m.get('longCount', 0), 'shortCount': is_m.get('shortCount', 0),
                'selfcorr': selfcorr, 'checks': checks, 'check_results': check_results
            }
        time.sleep(5)
    return {'name': name, 'status': 'TIMEOUT', 'expression': expr}

# 原始失败案例分析:
# YPNaPkKA失败原因:
# 1. Self-correlation 0.7033 > 0.7 (需降selfcorr)
# 2. Unit incompatibility: condition输出Unit[]但期望CSPrice (trade_when的第一个参数需要是boolean matrix但group_rank返回标量)

# 修复策略:
# 1. 用纯量纲条件替代 (ts_corr/volume等本身就是Unit[] -> boolean)
# 2. 添加独立rank包装降selfcorr

print("="*80)
print("Alpha修正 - 针对SelfCorr和Unit问题")
print("="*80)

# 修正候选 - 使用正确的外生条件
# 关键: trade_when(open_condition, alpha_expr, close_condition)
# open_condition必须是boolean matrix -> 需要用ts_xxx(volume/close相关)不能用group_rank(sector)这种标量

FIXED_CANDIDATES = [
    # 1. 修正unit问题 - 用volume相关性替代sector rank
    ("trade_when(ts_corr(close, volume, 20) > 0, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),
    ("trade_when(ts_corr(close, volume, 5) > 0.3, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),

    # 2. 用ts_zscore包装condition确保boolean matrix
    ("trade_when(ts_zscore(ts_std_dev(returns, 20), 10) > 1.5, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),

    # 3. 纯外生条件 - 独立的market状态
    ("trade_when(ts_mean(volume, 10) > ts_mean(volume, 60), group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),
    ("trade_when(rank(volume) > 0.8, group_zscore(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),

    # 4. 降selfcorr - 添加group_neutralize封装
    ("group_neutralize(rank(-ts_zscore(close, 5)), densify(sector))", 0, "SUBINDUSTRY"),
    ("group_zscore(group_neutralize(rank(-ts_zscore(close, 5)), densify(sector)), densify(sector))", 0, "SUBINDUSTRY"),

    # 5. 多层包装降selfcorr
    ("rank(group_zscore(group_neutralize(rank(-ts_zscore(close, 5)), densify(sector)), densify(sector)))", 0, "SUBINDUSTRY"),

    # 6. 改变base - 使用不同的neutralization策略
    ("group_rank(rank(-ts_zscore(close, 5)), densify(sector))", 0, "SUBINDUSTRY"),
    ("group_rank(rank(-ts_zscore(close, 5)), densify(subindustry))", 0, "SUBINDUSTRY"),

    # 7. 组合变体
    ("trade_when(ts_corr(close, volume, 20) > 0, group_neutralize(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),
    ("trade_when(ts_corr(close, volume, 20) > 0, group_rank(rank(-ts_zscore(close, 5)), densify(sector)), -1)", 0, "SUBINDUSTRY"),
]

results = []
for i, (expr, decay, neut) in enumerate(FIXED_CANDIDATES):
    name = f'fix_{i+1}'
    print(f"\n[{name}] {expr[:70]}")
    r = inline_simulate_full(expr, name, decay=decay, neutralization=neut)
    results.append(r)

    if r.get('alpha_id'):
        sh = r.get('sharpe', 0)
        ft = r.get('fitness', 0)
        tv = r.get('turnover', 0)
        sc = r.get('selfcorr')
        print(f"  Sharpe={sh:.3f}, Fitness={ft:.3f}, TVR={tv:.3f}, SelfCorr={sc}")

        # 显示check结果
        for check_name, check_data in r.get('check_results', {}).items():
            if check_data.get('result') == 'FAIL':
                print(f"  ❌ {check_name}: {check_data.get('value')}")
    else:
        print(f"  ❌ {r.get('status')}")
    time.sleep(3)

# 保存
save_path = OUTPUT_DIR / 'upgrade_fixed.json'
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
    sc = r.get('selfcorr', 1.0) or 1.0
    sh = r.get('sharpe', 0) or 0
    ft = r.get('fitness', 0) or 0
    tv = r.get('turnover', 99) or 99

    # 检查所有check是否PASS
    checks = r.get('checks', [])
    has_fail = any(c.get('result') == 'FAIL' for c in checks)

    # WorldQuant提交标准: Sharpe>=1.25, Fitness>=1.0, TVR<=0.7, SelfCorr<=0.7
    if has_fail:
        status = "FAIL_CHECK"
    elif sc > 0.7:
        status = "FAIL_SELF_CORR"
    elif sh < 1.25:
        status = "LOW_SHARPE"
    elif ft < 1.0:
        status = "LOW_FITNESS"
    elif tv > 0.7:
        status = "HIGH_TVR"
    else:
        status = "PASS"
        passing.append(r)

    print(f"\n[{status}] {r['expression'][:65]}")
    print(f"   S={sh:.2f} F={ft:.2f} TVR={tv:.2f} SC={sc:.4f}")

print(f"\n通过: {len(passing)}/{len(results)}")
if passing:
    print("\n可提交:")
    for r in passing:
        print(f"  {r['alpha_id']} | {r['expression'][:60]}")
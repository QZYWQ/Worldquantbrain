#!/usr/bin/env python3
"""
继续极致优化 - 聚焦TVR<0.6且Sharpe>1.8的候选
"""
import sys, json, time, random
from pathlib import Path
import requests

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.auth = ("zpdedn@gmail.com", "zp82648185000")
s.post('https://api.worldquantbrain.com/authentication')
print(f"Auth OK")

sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import trade_when_factory, check_submission, view_alphas

def save(name, data):
    path = OUTPUT_DIR / name
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  [Saved] {name}")

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
            return {
                'alpha_id': alpha_id, 'name': name, 'expression': expr, 'status': status,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'margin': is_m.get('margin'),
                'longCount': is_m.get('longCount', 0), 'shortCount': is_m.get('shortCount', 0),
                'decay': decay, 'neutralization': neutralization
            }
        elif status == 'ERROR':
            return {'alpha_id': None, 'name': name, 'status': 'ERROR', 'expression': expr}
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr}

# ========== 最佳SO候选 (TVR<0.6且Sharpe高) ==========
best_so_candidates = [
    # (expression, decay, neutralization, tvr)
    ("group_zscore(rank(-ts_zscore(close, 5)), densify(sector))", 5, "SUBINDUSTRY"),   # so_11: Sharpe=1.88, TVR=0.531
    ("rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector)))", 5, "INDUSTRY"),   # so_4: Sharpe=1.79, TVR=0.522
    ("rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector)))", 10, "INDUSTRY"), # so_7: Sharpe=1.50, TVR=0.397
]

# ========== 第三阶: Trade When ==========
print("=== 第三阶: Trade When ===")
th_candidates = []

for expr, decay, neut in best_so_candidates:
    print(f"  Building TH for: {expr[:60]}")
    for alpha in trade_when_factory('trade_when', expr, 'USA'):
        th_candidates.append((alpha, decay, neut))

# 额外: rank/zscore包装变体 (低TVR优化)
for expr, decay, neut in best_so_candidates:
    th_candidates.append((f"rank({expr})", decay, neut))
    th_candidates.append((f"zscore({expr})", decay, neut))
    th_candidates.append((f"rank(zscore({expr}))", decay, neut))

# 额外: 组合sign-flip
for expr, decay, neut in best_so_candidates:
    th_candidates.append((f"-rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector)))", 5, "SUBINDUSTRY"))

print(f"TH候选数量: {len(th_candidates)}")
random.shuffle(th_candidates)

print("\n=== 模拟第三阶 ===")
th_results = []
for i, (expr, decay, neut) in enumerate(th_candidates[:36]):
    name = f'th_{i+1}'
    print(f"  [{name}] {expr[:65]}")
    r = inline_simulate(expr, name, decay=decay, neutralization=neut)
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']:.3f} Fitness={r['fitness']:.3f} TVR={r['turnover']:.3f}")
    else:
        print(f"    {r['status']}")
    th_results.append(r)
    time.sleep(3)

save('upgrade-th-results.json', th_results)

# ========== 筛选: TVR<0.6 且 Sharpe>1.5 ==========
th_balanced = [r for r in th_results if r.get('sharpe', 0) >= 1.5 and r.get('turnover', 99) < 0.6]
th_balanced.sort(key=lambda x: x.get('sharpe', 0), reverse=True)

print(f"\nTH通过(Sharpe>=1.5, TVR<0.6): {len(th_balanced)}")
for r in th_balanced[:10]:
    print(f"  Sharpe={r['sharpe']:.3f} TVR={r['turnover']:.3f} {r['expression'][:60]}")

# ========== 极致TVR优化: 降低TVR ==========
print("\n=== 极致TVR优化 ===")
if th_balanced:
    best = th_balanced[0]
    print(f"当前最佳: Sharpe={best['sharpe']:.3f} TVR={best['turnover']:.3f}")

# 用原始1阶close做更多变体 (更灵活)
ultra_candidates = []

# 窗口变体
for win in [3, 5, 7, 10]:
    base = f"rank(-ts_zscore(close, {win}))"
    for neut in ['SUBINDUSTRY', 'INDUSTRY']:
        for decay in [0, 5, 10, 15]:
            # 纯rank包装 (降TVR)
            ultra_candidates.append((f"rank({base})", decay, neut))
            # group包装
            ultra_candidates.append((f"group_zscore({base}, densify(sector))", decay, neut))

# 组合field变体
for field in ['close', 'returns', 'volume']:
    for op in ['ts_zscore', 'ts_rank']:
        base = f"rank(-{op}({field}, 5))"
        for neut in ['SUBINDUSTRY', 'INDUSTRY']:
            for decay in [0, 5]:
                ultra_candidates.append((base, decay, neut))

print(f"Ultra候选: {len(ultra_candidates)}")
random.shuffle(ultra_candidates)

ultra_results = []
for i, (expr, decay, neut) in enumerate(ultra_candidates[:30]):
    name = f'ultra_{i+1}'
    print(f"  [{name}] {expr[:60]}")
    r = inline_simulate(expr, name, decay=decay, neutralization=neut)
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']:.3f} Fitness={r['fitness']:.3f} TVR={r['turnover']:.3f}")
    ultra_results.append(r)
    time.sleep(2)

save('upgrade-ultra-results.json', ultra_results)

# ========== 最终汇总 ==========
print("\n" + "="*60)
print("最终结果")
print("="*60)

all_results = th_results + ultra_results

# 高Sharpe低TVR
elite = [r for r in all_results if r.get('sharpe', 0) >= 2.0 and r.get('turnover', 99) < 0.6]
balanced = [r for r in all_results if r.get('sharpe', 0) >= 1.7 and r.get('turnover', 99) < 0.55]

print(f"\nElite (Sharpe>=2.0, TVR<0.6): {len(elite)}")
for r in elite:
    print(f"  [{r['sharpe']:.3f} TVR={r['turnover']:.3f}] {r['expression'][:70]}")

print(f"\nBalanced (Sharpe>=1.7, TVR<0.55): {len(balanced)}")
for r in balanced[:10]:
    print(f"  [{r['sharpe']:.3f} TVR={r['turnover']:.3f}] {r['expression'][:70]}")

# 提交检查
if balanced:
    stone_bag = [r['alpha_id'] for r in balanced if r.get('alpha_id')]
    gold_bag = []
    if stone_bag:
        print(f"\n检查 {len(stone_bag)} 个候选...")
        gold_bag = check_submission(stone_bag, gold_bag, 0)
        print(f"通过检查: {len(gold_bag)}")
        if gold_bag:
            print("\n可提交Alpha:")
            view_alphas(gold_bag)

# 保存最终结果
final_results = {
    'th_tested': len(th_results),
    'ultra_tested': len(ultra_results),
    'elite_count': len(elite),
    'balanced_count': len(balanced),
    'th_balanced': [{'expr': r['expression'], 'sharpe': r['sharpe'], 'tvr': r['turnover']} for r in th_balanced[:10]],
    'elite': [{'expr': r['expression'], 'sharpe': r['sharpe'], 'tvr': r['turnover']} for r in elite],
}
save('upgrade-final.json', final_results)

print("\n完成!")
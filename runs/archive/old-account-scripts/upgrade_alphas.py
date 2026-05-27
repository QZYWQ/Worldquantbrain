#!/usr/bin/env python3
"""
极致优化脚本 - 对通过1阶阈值的alpha进行2、3阶升阶
目标: Sharpe > 2.0, Fitness > 1.0, TVR < 0.6
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
from machine_lib import get_group_second_order_factory, trade_when_factory, check_submission, view_alphas

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

# ========== 输入alphas (从alpha_loop.py获取) ==========
fo_layer = [
    ("rank(-ts_zscore(close, 5))", 0, 'SUBINDUSTRY'),  # zq5azOZ1, Sharpe=1.87
    ("rank(-ts_zscore(close, 5))", 0, 'INDUSTRY'),      # kqnROeX8, Sharpe=1.78
]

# ========== 第二阶工厂 - 扩展候选 ==========
print("=== 第二阶工厂 (Group Operations) ===")
group_ops = ['group_rank', 'group_zscore', 'group_neutralize']

# 扩展: 不同neutralization组合
neutralizations = ['SUBINDUSTRY', 'INDUSTRY', 'SECTOR', 'market']
decays = [0, 5, 10, 15]

so_candidates = []
for expr, base_decay, base_neut in fo_layer:
    for group_op in group_ops:
        for neut in neutralizations:
            for decay in decays:
                # 生成group表达式
                alpha = f"{group_op}({expr}, densify(sector))"
                so_candidates.append((alpha, decay, neut))

# 额外: 添加 rank 包装变体
for expr, base_decay, base_neut in fo_layer:
    for group_op in ['group_rank', 'group_zscore']:
        for neut in neutralizations:
            for decay in decays:
                alpha = f"rank({group_op}({expr}, densify(sector)))"
                so_candidates.append((alpha, decay, neut))

print(f"SO候选数量: {len(so_candidates)}")
random.shuffle(so_candidates)

# ========== 模拟SO ==========
print("\n=== 模拟第二阶 (前30个) ===")
so_batch = so_candidates[:30]
so_results = []

for i, (expr, decay, neut) in enumerate(so_batch):
    name = f'so_{i+1}'
    print(f"  [{name}] decay={decay} neut={neut} {expr[:60]}")
    r = inline_simulate(expr, name, decay=decay, neutralization=neut)
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']:.3f} Fitness={r['fitness']:.3f} TVR={r['turnover']:.3f}")
    else:
        print(f"    {r['status']}")
    so_results.append(r)
    time.sleep(3)

save('upgrade-so-results.json', so_results)

# 严格筛选: Sharpe > 1.5
so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.5]
print(f"\nSO通过(>=1.5): {len(so_passing)}/{len(so_results)}")

# 排序取Top5
so_passing.sort(key=lambda x: x.get('sharpe', 0), reverse=True)
top_so = so_passing[:5]
print("\nTop 5 SO:")
for r in top_so:
    print(f"  Sharpe={r['sharpe']:.3f} {r['expression'][:60]}")

# ========== 第三阶工厂 ==========
print("\n=== 第三阶工厂 (Trade When) ===")
# 只对top SO做3阶
th_candidates = []
for r in top_so:
    expr = r['expression']
    decay = r.get('decay', 0)
    for alpha in trade_when_factory('trade_when', expr, 'USA'):
        th_candidates.append((alpha, decay))

# 也尝试不带trade_when的变体 - 纯rank/zscore包装
for r in top_so:
    expr = r['expression']
    decay = r.get('decay', 0)
    # rank包装
    th_candidates.append((f"rank({expr})", decay))
    # zscore包装
    th_candidates.append((f"zscore({expr})", decay))
    # 组合包装
    th_candidates.append((f"rank(zscore({expr}))", decay))

print(f"TH候选数量: {len(th_candidates)}")
random.shuffle(th_candidates)

# 模拟TH
print("\n=== 模拟第三阶 (前24个) ===")
th_batch = th_candidates[:24]
th_results = []

for i, (expr, decay) in enumerate(th_batch):
    name = f'th_{i+1}'
    print(f"  [{name}] {expr[:65]}")
    r = inline_simulate(expr, name, decay=decay, neutralization='SUBINDUSTRY')
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']:.3f} Fitness={r['fitness']:.3f} TVR={r['turnover']:.3f}")
    else:
        print(f"    {r['status']}")
    th_results.append(r)
    time.sleep(3)

save('upgrade-th-results.json', th_results)

# 筛选: Sharpe >= 1.5
th_passing = [r for r in th_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.5]
th_passing.sort(key=lambda x: x.get('sharpe', 0), reverse=True)
print(f"\nTH通过(>=1.5): {len(th_passing)}/{len(th_results)}")

# ========== 极致优化: 暴力扩展Top候选 ==========
print("\n=== 极致优化: 暴力扩展Top SO ===")
best_so = so_passing[0] if so_passing else None

if best_so and best_so.get('sharpe', 0) < 2.0:
    print(f"当前最佳: Sharpe={best_so['sharpe']:.3f}, 进行暴力扩展...")

    ultra_candidates = []
    best_expr = best_so['expression']

    # 变体1: 不同的group和neutralization组合
    for neut in ['SUBINDUSTRY', 'INDUSTRY', 'SECTOR', 'market', 'subindustry']:
        for decay in [0, 5, 10, 15, 20]:
            for group_op in ['group_rank', 'group_zscore', 'group_neutralize']:
                alpha = f"{group_op}(rank(-ts_zscore(close, 5)), densify(sector))"
                ultra_candidates.append((alpha, decay, neut))

    # 变体2: 窗口变化
    for win in [3, 5, 7, 10]:
        for neut in ['SUBINDUSTRY', 'INDUSTRY']:
            for decay in [0, 5, 10]:
                alpha = f"rank(-ts_zscore(close, {win}))"
                ultra_candidates.append((alpha, decay, neut))

    # 变体3: 多层组合
    for neut in ['SUBINDUSTRY', 'INDUSTRY']:
        for decay in [0, 5]:
            alpha = f"group_rank(rank(-ts_zscore(close, 5)), densify(sector))"
            ultra_candidates.append((alpha, decay, neut))
            alpha = f"rank(group_zscore(-ts_zscore(close, 5), densify(sector)))"
            ultra_candidates.append((alpha, decay, neut))

    print(f"暴力候选: {len(ultra_candidates)}")
    random.shuffle(ultra_candidates)

    # 模拟前40个
    ultra_results = []
    for i, (expr, decay, neut) in enumerate(ultra_candidates[:40]):
        name = f'ultra_{i+1}'
        print(f"  [{name}] {expr[:60]}")
        r = inline_simulate(expr, name, decay=decay, neutralization=neut)
        if r.get('alpha_id'):
            print(f"    Sharpe={r['sharpe']:.3f} Fitness={r['fitness']:.3f} TVR={r['turnover']:.3f}")
        ultra_results.append(r)
        time.sleep(2)

    save('upgrade-ultra-results.json', ultra_results)

    # 找最佳
    ultra_passing = [r for r in ultra_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.5]
    ultra_passing.sort(key=lambda x: x.get('sharpe', 0), reverse=True)
    print(f"\nUltra通过(>=1.5): {len(ultra_passing)}")
    for r in ultra_passing[:5]:
        print(f"  Sharpe={r['sharpe']:.3f} {r['expression'][:60]}")

# ========== 汇总报告 ==========
print("\n" + "="*60)
print("极致优化结果汇总")
print("="*60)

all_results = so_results + th_results
if 'ultra_results' in dir():
    all_results += ultra_results

high_sharpe = [r for r in all_results if r.get('sharpe', 0) >= 2.0]
good_sharpe = [r for r in all_results if 1.5 <= r.get('sharpe', 0) < 2.0]

print(f"\nSharpe >= 2.0: {len(high_sharpe)}")
for r in high_sharpe:
    print(f"  [{r['sharpe']:.3f}] {r['expression'][:70]}")

print(f"\n1.5 <= Sharpe < 2.0: {len(good_sharpe)}")
for r in good_sharpe[:10]:
    print(f"  [{r['sharpe']:.3f}] {r['expression'][:70]}")

# 提交检查
if high_sharpe:
    stone_bag = [r['alpha_id'] for r in high_sharpe if r.get('alpha_id')]
    gold_bag = []
    if stone_bag:
        print(f"\n检查 {len(stone_bag)} 个高Sharpe候选...")
        gold_bag = check_submission(stone_bag, gold_bag, 0)
        print(f"通过检查: {len(gold_bag)}")
        if gold_bag:
            print("\n可提交Alpha:")
            view_alphas(gold_bag)

save('upgrade-summary.json', {
    'so_tested': len(so_results),
    'th_tested': len(th_results),
    'ultra_tested': len(ultra_results) if 'ultra_results' in dir() else 0,
    'high_sharpe_count': len(high_sharpe),
    'good_sharpe_count': len(good_sharpe),
    'all_results_count': len(all_results)
})

print("\n完成!")
#!/usr/bin/env python3
"""
may19-promising alphas 2/3阶升阶
从 may19-promising-alphas.json 加载95个候选，升阶SO+TH
"""
import sys, json, time, random
from pathlib import Path
import requests

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.auth = ("zpdedn@gmail.com", "zp82648185000")
s.post('https://api.worldquantbrain.com/authentication')
print(f"Auth OK", flush=True)

sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import get_group_second_order_factory, trade_when_factory, check_submission, view_alphas

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

def save(name, data):
    path = OUTPUT_DIR / name
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  [Saved] {name}", flush=True)

# ========== 加载候选 ==========
with open('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/may19-promising-alphas.json') as f:
    data = json.load(f)

alphas = data['alphas']
# 筛选: Sharpe >= 1.5, Fitness >= 1.0, CONCENTRATED_WEIGHT = PASS
candidates = [
    a for a in alphas
    if a.get('sharpe', 0) >= 1.5
    and a.get('fitness', 0) >= 1.0
    and a['checks'].get('CONCENTRATED_WEIGHT') == 'PASS'
]
# 按 fitness 降序
candidates.sort(key=lambda x: x.get('fitness', 0), reverse=True)
print(f"升阶候选: {len(candidates)}", flush=True)

# ========== SO升阶 ==========
# 对TOP20候选做SO扩展（每个候选12个SO变体）
group_ops = ['group_rank', 'group_zscore', 'group_neutralize']
neut_groups = ['subindustry', 'industry', 'sector', 'market', 'bucket(rank(cap), range=\'0.1, 1, 0.1\')']
decays = [0, 6, 10, 15]

so_candidates = []

for cand in candidates[:20]:
    orig_expr = cand['expression']
    orig_id = cand['alphaId']
    orig_s = cand['sharpe']
    orig_f = cand['fitness']
    print(f"\n处理 {orig_id} (S={orig_s:.2f}, F={orig_f:.2f})", flush=True)

    # 1. 直接加group wrapper
    for gop in group_ops:
        for grp in neut_groups:
            for dec in decays:
                expr = f"{gop}({orig_expr}, densify({grp}))"
                so_candidates.append({
                    'expr': expr, 'decay': dec, 'neut': 'INDUSTRY',
                    'parent': orig_id, 'method': 'direct_group_wrapper'
                })

    # 2. rank包装
    for dec in [0, 6, 10]:
        expr = f"rank({orig_expr})"
        so_candidates.append({
            'expr': expr, 'decay': dec, 'neut': 'INDUSTRY',
            'parent': orig_id, 'method': 'rank_wrapper'
        })

    # 3. zscore包装
    for dec in [0, 6, 10]:
        expr = f"zscore({orig_expr})"
        so_candidates.append({
            'expr': expr, 'decay': dec, 'neut': 'INDUSTRY',
            'parent': orig_id, 'method': 'zscore_wrapper'
        })

print(f"\nSO总候选: {len(so_candidates)}", flush=True)
random.shuffle(so_candidates)

# 模拟SO（前60个）
print("\n=== 模拟SO (前60个) ===", flush=True)
so_results = []
for i, cand in enumerate(so_candidates[:60]):
    name = f"so_{i+1}_{cand['parent']}"
    expr = cand['expr']
    print(f"[{name}] {expr[:60]}...", flush=True)
    r = inline_simulate(expr, name, decay=cand['decay'], neutralization=cand['neut'])
    if r.get('alpha_id'):
        print(f"  Sharpe={r['sharpe']:.3f} Fitness={r['fitness']:.3f} TVR={r['turnover']:.3f}", flush=True)
    else:
        print(f"  {r['status']}", flush=True)
    r['parent'] = cand['parent']
    r['method'] = cand['method']
    so_results.append(r)
    time.sleep(3)

save('may19_upgrade_so_results.json', so_results)

# 筛选SO通过: Sharpe >= 1.5
so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.5]
so_passing.sort(key=lambda x: x.get('sharpe', 0), reverse=True)
print(f"\nSO通过(S>=1.5): {len(so_passing)}/{len(so_results)}", flush=True)

for r in so_passing[:10]:
    print(f"  S={r['sharpe']:.2f} F={r['fitness']:.2f} {r['method']} {r['expression'][:60]}", flush=True)

# ========== TH升阶 ==========
# 对SO通过者做TH
print("\n=== TH升阶 ===", flush=True)
th_candidates = []

for r in so_passing[:10]:  # Top 10 SO
    expr = r['expression']
    decay = r.get('decay', 0)

    # 1. trade_when 变体（用sentiment/returns信号触发）
    tw_events = [
        "ts_rank(scl12_sentiment_fast_d1, 10) > 0.6",
        "ts_rank(scl12_sentiment_fast_d1, 20) > 0.6",
        "rank(vwap/vwap_ts_mean(20)) > 0.6",
        "rank(ts_std_dev(returns, 5) / ts_std_dev(returns, 20)) > 0.7",
        "rank(volume / ts_mean(volume, 20)) > 0.6",
    ]
    for ev in tw_events:
        th_candidates.append({
            'expr': f"trade_when({ev}, {expr})",
            'decay': decay,
            'parent': r.get('parent', 'unknown'),
            'method': f'trade_when'
        })

    # 2. rank/zscore 嵌套包装
    th_candidates.append({'expr': f"rank({expr})", 'decay': decay, 'parent': r.get('parent', 'unknown'), 'method': 'rank_rank'})
    th_candidates.append({'expr': f"zscore({expr})", 'decay': decay, 'parent': r.get('parent', 'unknown'), 'method': 'zscore_wrap'})
    th_candidates.append({'expr': f"rank(zscore({expr}))", 'decay': decay, 'parent': r.get('parent', 'unknown'), 'method': 'rank_zscore'})

    # 3. quantile包装（降低极端值影响）
    th_candidates.append({'expr': f"quantile({expr}, 0.2)", 'decay': decay, 'parent': r.get('parent', 'unknown'), 'method': 'quantile_wrap'})
    th_candidates.append({'expr': f"quantile({expr}, 0.8)", 'decay': decay, 'parent': r.get('parent', 'unknown'), 'method': 'quantile_upper'})

print(f"TH总候选: {len(th_candidates)}", flush=True)
random.shuffle(th_candidates)

# 模拟TH（前48个）
print("\n=== 模拟TH (前48个) ===", flush=True)
th_results = []
for i, cand in enumerate(th_candidates[:48]):
    name = f"th_{i+1}_{cand['parent']}"
    expr = cand['expr']
    print(f"[{name}] {expr[:60]}...", flush=True)
    r = inline_simulate(expr, name, decay=cand['decay'], neutralization='SUBINDUSTRY')
    if r.get('alpha_id'):
        print(f"  Sharpe={r['sharpe']:.3f} Fitness={r['fitness']:.3f} TVR={r['turnover']:.3f}", flush=True)
    else:
        print(f"  {r['status']}", flush=True)
    r['parent'] = cand['parent']
    r['method'] = cand['method']
    th_results.append(r)
    time.sleep(3)

save('may19_upgrade_th_results.json', th_results)

# 筛选TH通过
th_passing = [r for r in th_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.5]
th_passing.sort(key=lambda x: x.get('sharpe', 0), reverse=True)
print(f"\nTH通过(S>=1.5): {len(th_passing)}/{len(th_results)}", flush=True)

for r in th_passing[:10]:
    print(f"  S={r['sharpe']:.2f} F={r['fitness']:.2f} {r['method']} {r['expression'][:60]}", flush=True)

# ========== 汇总 ==========
print("\n" + "="*60, flush=True)
print("may19 升阶汇总", flush=True)
print("="*60, flush=True)

all_good = so_passing + th_passing
# 去重（按expression）
seen = set()
unique_good = []
for r in all_good:
    expr = r.get('expression', '')
    if expr not in seen:
        seen.add(expr)
        unique_good.append(r)

unique_good.sort(key=lambda x: x.get('sharpe', 0), reverse=True)
print(f"\n总优质(S>=1.5): {len(unique_good)} 去重后", flush=True)

for r in unique_good[:15]:
    print(f"  S={r['sharpe']:.2f} F={r['fitness']:.2f} TV={r['turnover']:.3f} | {r['method']} | {r['expression'][:70]}", flush=True)

# 提交检查
if unique_good:
    stone_bag = [r['alpha_id'] for r in unique_good[:20] if r.get('alpha_id')]
    gold_bag = []
    if stone_bag:
        print(f"\n检查 {len(stone_bag)} 个候选...", flush=True)
        gold_bag = check_submission(stone_bag, gold_bag, 0)
        print(f"通过检查: {len(gold_bag)}", flush=True)
        if gold_bag:
            print("\n可提交Alpha:", flush=True)
            view_alphas(gold_bag)

save('may19_upgrade_summary.json', {
    'so_tested': len(so_results),
    'th_tested': len(th_results),
    'so_passing': len(so_passing),
    'th_passing': len(th_passing),
    'unique_good': len(unique_good),
    'all_good': [{'sharpe': r['sharpe'], 'fitness': r['fitness'], 'turnover': r['turnover'],
                  'method': r['method'], 'expr': r['expression'][:80]} for r in unique_good[:20]]
})

print("\n完成!", flush=True)
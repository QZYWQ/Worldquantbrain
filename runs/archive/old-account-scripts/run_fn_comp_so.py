#!/usr/bin/env python3
"""SO expansion for fn_comp direction A"""
import sys, json, time, random, requests
from pathlib import Path

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')

s = requests.Session()
s.auth = ('zpdedn@gmail.com', 'zp82648185000')
s.post('https://api.worldquantbrain.com/authentication')
print('Auth OK', flush=True)

def inline_simulate(s, expr, name=None, decay=0):
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': 'INDUSTRY',
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    r = s.post('https://api.worldquantbrain.com/simulations', json={'type': 'REGULAR', 'settings': settings, 'regular': expr})
    if r.status_code != 201:
        return {'alpha_id': None, 'name': name, 'status': f'POST_FAIL_{r.status_code}', 'expression': expr}
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
            }
        elif status == 'ERROR':
            return {'alpha_id': None, 'name': name, 'status': 'ERROR', 'expression': expr}
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr}

# Load SO candidates
with open(OUTPUT_DIR / 'fn_comp_direction_A_so.json') as f:
    data = json.load(f)
fo_expr = data['fo']
decay = data['decay']
so_list = data['so_list']
print(f'Loaded {len(so_list)} SO candidates', flush=True)

# Shuffle and simulate top 18
random.shuffle(so_list)
batch = so_list[:18]
print(f'Simulating {len(batch)} SO candidates...', flush=True)

so_results = []
for i, expr in enumerate(batch):
    name = f'fn_so_{i+1}'
    print(f'[{name}] {expr[:70]}...', flush=True)
    r = inline_simulate(s, expr, name=name, decay=decay)
    if r.get('alpha_id'):
        print(f'  Sharpe={r["sharpe"]}, Fitness={r["fitness"]}, TVR={r["turnover"]} L={r["longCount"]} S={r["shortCount"]}', flush=True)
    else:
        print(f'  {r["status"]}', flush=True)
    so_results.append(r)
    time.sleep(5)

# Save results
with open(OUTPUT_DIR / 'fn_comp_A_so_results.json', 'w') as f:
    json.dump(so_results, f, indent=2, default=str)
print(f'\n[Saved] fn_comp_A_so_results.json ({len(so_results)} results)', flush=True)

# Passing: Sharpe >= 1.0, Fitness >= 0.7
so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.0 and r.get('fitness', 0) >= 0.7]
print(f'\nSO passing (Sharpe>=1.0, Fitness>=0.7): {len(so_passing)}/{len(so_results)}')
for r in so_passing:
    print(f'  {r["alpha_id"]} Sharpe={r["sharpe"]} Fitness={r["fitness"]} TVR={r["turnover"]}')

# Relaxed: Sharpe >= 0.5, Fitness >= 0.3
if not so_passing:
    so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.5 and r.get('fitness', 0) >= 0.3]
    print(f'\nSO passing relaxed (Sharpe>=0.5, Fitness>=0.3): {len(so_passing)}/{len(so_results)}')

# Save passing tracker
so_tracker = [[r['alpha_id'], r['expression'], r['sharpe'], r['turnover'], r['fitness'], r['margin'], '', decay] for r in so_passing]
with open(OUTPUT_DIR / 'fn_comp_A_so_tracker.json', 'w') as f:
    json.dump({'count': len(so_tracker), 'alphas': so_tracker}, f, indent=2, default=str)

# Gold bag: add original FO alpha Jjng3wwj (Sharpe=1.21, Fitness=0.67)
gold = [('Jjng3wwj', 1.21, 0.67, 0.012)]
for r in so_passing:
    gold.append((r['alpha_id'], r['sharpe'], r['fitness'], r['turnover']))
print(f'\nGold bag candidates: {len(gold)}')
for g in gold:
    print(f'  {g[0]} Sharpe={g[1]:.2f} Fitness={g[2]:.2f} TVR={g[3]:.4f}')

with open(OUTPUT_DIR / 'fn_comp_A_gold_bag.json', 'w') as f:
    json.dump({'count': len(gold), 'gold': gold}, f, indent=2, default=str)
print('\nDONE', flush=True)
#!/usr/bin/env python3
"""SO expansion for unsubmitted unsystematic_risk downstream candidates"""
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

with open(OUTPUT_DIR / 'unsub_unsys_so.json') as f:
    candidates = json.load(f)

all_results = {}

for aid, data in candidates.items():
    orig_s = data['sharpe']
    orig_f = data['fitness']
    so_list = data['so_list'][:12]  # Top 12 per candidate
    print(f'\n=== {aid} (S={orig_s}, F={orig_f}) ===')
    print(f'Simulating {len(so_list)} SO variants', flush=True)

    results = []
    for i, expr in enumerate(so_list):
        name = f'{aid}_so{i+1}'
        print(f'[{name}] {expr[:60]}...', flush=True)
        r = inline_simulate(s, expr, name=name, decay=6)
        if r.get('alpha_id'):
            print(f'  Sharpe={r["sharpe"]}, Fitness={r["fitness"]}, TVR={r["turnover"]}', flush=True)
        else:
            print(f'  {r["status"]}', flush=True)
        results.append(r)
        time.sleep(5)

    # Save per-candidate results
    with open(OUTPUT_DIR / f'so_expand_{aid}.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    # Passing: Sharpe >= 1.25, Fitness >= 1.0
    passing = [r for r in results if r.get('sharpe') is not None and r.get('sharpe') >= 1.25 and r.get('fitness', 0) >= 1.0]
    print(f'Passing (S>=1.25, F>=1.0): {len(passing)}/{len(results)}')

    # Also check for Fitness boost potential (Sharpe >= 1.25, Fitness >= 0.7)
    promising = [r for r in results if r.get('sharpe') is not None and r.get('sharpe') >= 1.25 and r.get('fitness', 0) >= 0.7]
    print(f'Promising (S>=1.25, F>=0.7): {len(promising)}/{len(results)}')

    gold_for_cand = []
    if passing:
        ids = [r['alpha_id'] for r in passing[:5]]
        gold = check_submission(ids, [], 0)
        for g in gold:
            gold_for_cand.append({'id': g[0], 'self_corr': g[1]})
            print(f'  GOLD: {g[0]} self_corr={g[1]:.4f}')

    all_results[aid] = {
        'original': {'sharpe': orig_s, 'fitness': orig_f},
        'results': results,
        'passing_count': len(passing),
        'promising_count': len(promising),
        'gold': gold_for_cand,
    }
    print(f'Done {aid}', flush=True)

print(f'\n=== SUMMARY ===')
for aid, data in all_results.items():
    orig = data['original']
    print(f'{aid}: {data["passing_count"]} passing, {data["promising_count"]} promising, {len(data["gold"])} gold')
    print(f'  Original: S={orig["sharpe"]}, F={orig["fitness"]}')

with open(OUTPUT_DIR / 'unsub_unsys_so_results.json', 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print('\nDONE', flush=True)
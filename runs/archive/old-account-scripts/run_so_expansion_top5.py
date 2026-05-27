#!/usr/bin/env python3
"""SO expansion pipeline on top 5 candidates - all failed self-correlation"""
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
                'decay': decay,
            }
        elif status == 'ERROR':
            return {'alpha_id': None, 'name': name, 'status': 'ERROR', 'expression': expr}
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr}

# Load candidates with SO
with open(OUTPUT_DIR / 'top5_candidates_so.json') as f:
    candidates = json.load(f)

all_results = {}
total_simulated = 0

for aid, data in candidates.items():
    orig_sharpe = data['sharpe']
    orig_fitness = data['fitness']
    orig_self_corr = data['self_corr']
    so_list = data['so_list'][:12]  # Top 12 SO variants per candidate
    print(f'\n=== {aid} (S={orig_sharpe}, F={orig_fitness}, self_corr={orig_self_corr}) ===')
    print(f'SO candidates: {len(so_list)}, simulating {len(so_list[:12])}', flush=True)

    results = []
    for i, expr in enumerate(so_list[:12]):
        name = f'{aid}_so{i+1}'
        print(f'[{name}] {expr[:60]}...', flush=True)
        r = inline_simulate(s, expr, name=name, decay=6)
        if r.get('alpha_id'):
            print(f'  Sharpe={r["sharpe"]}, Fitness={r["fitness"]}, TVR={r["turnover"]}', flush=True)
        else:
            print(f'  {r["status"]}', flush=True)
        results.append(r)
        total_simulated += 1
        time.sleep(5)

    # Save per-candidate results
    with open(OUTPUT_DIR / f'so_expand_{aid}.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    # Check submission for best passing SO
    passing = [r for r in results if r.get('sharpe') is not None and r.get('sharpe') >= 1.25 and r.get('fitness', 0) >= 1.0]
    print(f'Passing (S>=1.25, F>=1.0): {len(passing)}/{len(results)}')

    gold_for_cand = []
    if passing:
        # Check submission
        ids = [r['alpha_id'] for r in passing[:5]]
        from machine_lib import check_submission
        gold = check_submission(ids, [], 0)
        print(f'Gold bag: {len(gold)}')
        for g in gold:
            gold_for_cand.append({'id': g[0], 'self_corr': g[1]})
            print(f'  {g[0]} self_corr={g[1]:.4f}')

    all_results[aid] = {
        'original': {'sharpe': orig_sharpe, 'fitness': orig_fitness, 'self_corr': orig_self_corr},
        'results': results,
        'passing_count': len(passing),
        'gold': gold_for_cand,
    }

    print(f'Done {aid}, total simulated: {total_simulated}', flush=True)

print(f'\n=== PIPELINE COMPLETE: {total_simulated} alphas simulated ===')

# Summary
for aid, data in all_results.items():
    orig = data['original']
    print(f'{aid}: {data["passing_count"]} passing SO, {len(data["gold"])} submission-ready')
    print(f'  Original: S={orig["sharpe"]}, F={orig["fitness"]}, self_corr={orig["self_corr"]}')

# Save final
with open(OUTPUT_DIR / 'so_expansion_summary.json', 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print('\nDONE', flush=True)
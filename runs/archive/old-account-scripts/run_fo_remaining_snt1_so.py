#!/usr/bin/env python3
"""FO remaining fields + snt1 simplified SO test"""
import sys, json, time, requests
from pathlib import Path

BATCH_FILE = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-16-fo-remaining-snt1-so.json')
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')

s = requests.Session()
s.auth = ('zpdedn@gmail.com', 'zp82648185000')
s.post('https://api.worldquantbrain.com/authentication')
print('Auth OK', flush=True)

def inline_simulate(s, expr, name=None, settings_override=None):
    base_settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': 0, 'neutralization': 'INDUSTRY',
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    if settings_override:
        base_settings.update(settings_override)
    r = s.post('https://api.worldquantbrain.com/simulations', json={'type': 'REGULAR', 'settings': base_settings, 'regular': expr})
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

with open(BATCH_FILE) as f:
    batch = json.load(f)

candidates = batch['candidates']
print(f'Loaded {len(candidates)} candidates', flush=True)

results = []
for i, cand in enumerate(candidates):
    name = cand['name']
    expr = cand['expression']
    settings = cand.get('settings', {})
    print(f'[{i+1}/{len(candidates)}] {name}: {expr[:60]}...', flush=True)
    r = inline_simulate(s, expr, name=name, settings_override=settings)
    if r.get('alpha_id'):
        print(f'  Sharpe={r["sharpe"]}, Fitness={r["fitness"]}, TVR={r["turnover"]}', flush=True)
    else:
        print(f'  {r["status"]}', flush=True)
    results.append(r)
    time.sleep(3)

output_file = OUTPUT_DIR / f'{batch["capture_id"]}_results.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f'\nSaved {output_file}', flush=True)

# Triage
PASS = [r for r in results if r.get('alpha_id') and r.get('sharpe', 0) >= 1.25 and r.get('fitness', 0) >= 1.0]

print(f'\n=== COMBINED SO RESULTS ===')
print(f'PASS (S>=1.25, F>=1.0): {len(PASS)}')
for r in PASS:
    print(f'  {r["name"]}: S={r["sharpe"]:.2f}, F={r["fitness"]:.2f}, TVR={r["turnover"]:.4f}')

if PASS:
    print(f'\nSelf-correlation check on {len(PASS)} passing...', flush=True)
    from machine_lib import check_submission
    ids = [r['alpha_id'] for r in PASS[:5]]
    gold = check_submission(ids, [], 0)
    gold_dict = {g[0]: g[1] for g in gold}
    FINAL = []
    for r in PASS:
        r['self_corr'] = gold_dict.get(r['alpha_id'], None)
        if r['self_corr'] is not None:
            print(f'  {r["name"]}: self_corr={r["self_corr"]:.4f}')
            if r['self_corr'] < 0.7:
                FINAL.append(r)
    print(f'FINAL (self_corr < 0.7): {len(FINAL)}')
    for r in FINAL:
        print(f'  {r["name"]}: S={r["sharpe"]:.2f}, F={r["fitness"]:.2f}, self_corr={r["self_corr"]:.4f}')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

print('\nDONE', flush=True)
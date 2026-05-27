#!/usr/bin/env python3
"""FO Field Health Scout batch runner"""
import sys, json, time, requests
from pathlib import Path

BATCH_FILE = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-16-fo-field-health-scout.json')
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')

s = requests.Session()
s.auth = ('zpdedn@gmail.com', 'zp82648185000')
s.post('https://api.worldquantbrain.com/authentication')
print('Auth OK', flush=True)

def inline_simulate(s, expr, name=None):
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': 0, 'neutralization': 'NONE',
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'OFF',
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

with open(BATCH_FILE) as f:
    batch = json.load(f)

candidates = batch['candidates']
print(f'Loaded {len(candidates)} field health candidates', flush=True)

results = []
for i, cand in enumerate(candidates):
    name = cand['name']
    expr = cand['expression']
    print(f'[{i+1}/{len(candidates)}] {name}: {expr[:60]}...', flush=True)
    r = inline_simulate(s, expr, name=name)
    if r.get('alpha_id'):
        print(f'  Sharpe={r["sharpe"]}, Fitness={r["fitness"]}, TVR={r["turnover"]}, L={r["longCount"]}, S={r["shortCount"]}', flush=True)
    else:
        print(f'  {r["status"]}', flush=True)
    results.append(r)
    time.sleep(3)

# Save
output_file = OUTPUT_DIR / f'{batch["capture_id"]}_results.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f'\nSaved {output_file}', flush=True)

# Triage: pass vs kill
PASS = []
KILL_NULL = []
KILL_WEAK = []
for r in results:
    if not r.get('alpha_id'):
        KILL_NULL.append(r['name'])
    elif r.get('sharpe', 0) > 0.3:
        PASS.append(r)
    else:
        KILL_WEAK.append(r['name'])

print(f'\n=== FIELD HEALTH TRIAGE ===')
print(f'PASS (Sharpe > 0.3): {len(PASS)}')
for r in PASS:
    print(f'  {r["name"]}: S={r["sharpe"]:.2f}, F={r["fitness"]:.2f}')
print(f"KILL (alphaId=null - field doesn't exist): {len(KILL_NULL)}")
for n in KILL_NULL:
    print(f'  {n}')
print(f'KILL (Sharpe <= 0.3 - no signal): {len(KILL_WEAK)}')
for n in KILL_WEAK:
    print(f'  {n}')

print('\nDONE', flush=True)
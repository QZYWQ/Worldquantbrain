#!/usr/bin/env python3
"""SO Expansion for fundamental2 options batch"""
import sys, json, time, requests
from pathlib import Path

BATCH_FILE = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-19-fundamental2-options-exploration.json')
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
print(f'Loaded {len(candidates)} SO candidates', flush=True)

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

# Save raw results
output_file = OUTPUT_DIR / f'{batch["capture_id"]}_results.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f'\nSaved {output_file}', flush=True)

# Triage: passing vs weak
PASS = []
WEAK = []
for r in results:
    if r.get('alpha_id') and r.get('fitness', 0) >= 1.0 and r.get('sharpe', 0) >= 1.25:
        PASS.append(r)
    else:
        WEAK.append(r)

print(f'\n=== PASS ({len(PASS)}) ===')
for r in PASS:
    print(f'{r["name"]}: S={r["sharpe"]}, F={r["fitness"]}, TVR={r["turnover"]}')

print(f'\n=== WEAK ({len(WEAK)}) ===')
for r in WEAK:
    s_val = r.get('sharpe', 'N/A')
    f_val = r.get('fitness', 'N/A')
    print(f'{r["name"]}: S={s_val}, F={f_val}, status={r["status"]}')

print(f'\nTotal: {len(results)}, Pass: {len(PASS)}, Weak: {len(WEAK)}')
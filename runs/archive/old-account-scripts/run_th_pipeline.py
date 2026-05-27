#!/usr/bin/env python3
"""Third Order pipeline - simulates TH from 8 SO alphas"""
import sys, json, time, random, requests
from pathlib import Path
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import trade_when_factory, check_submission

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')

s = requests.Session()
s.auth = ('zpdedn@gmail.com', 'zp82648185000')
r = s.post('https://api.worldquantbrain.com/authentication')
print('Auth:', r.status_code, flush=True)

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

with open('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/step12-so-layer.json') as f:
    so_layer = json.load(f)['layer']
print(f'Loaded {len(so_layer)} SO alphas', flush=True)

th_alpha_list = []
for expr, decay in so_layer:
    for alpha in trade_when_factory('trade_when', expr, 'USA'):
        th_alpha_list.append((alpha, decay))
print(f'TH: {len(th_alpha_list)} generated', flush=True)

random.shuffle(th_alpha_list)
th_batch = th_alpha_list[:8]
print(f'Simulating {len(th_batch)} TH candidates...', flush=True)

th_results = []
for i, (expr, decay) in enumerate(th_batch):
    name = f'th_{i+1}'
    print(f'[{name}] {expr[:65]}...', flush=True)
    r = inline_simulate(s, expr, name=name, decay=decay)
    if r.get('alpha_id'):
        print(f'  Sharpe={r["sharpe"]}, Fitness={r["fitness"]}, TVR={r["turnover"]}', flush=True)
    else:
        print(f'  {r["status"]}', flush=True)
    th_results.append(r)
    time.sleep(3)

path = OUTPUT_DIR / 'step14-th-results.json'
with open(path, 'w') as f:
    json.dump(th_results, f, indent=2, default=str)
print(f'Saved step14-th-results.json ({len(th_results)} results)', flush=True)

th_passing = [r for r in th_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.0 and r.get('fitness', 0) >= 0.7]
print(f'TH passing: {len(th_passing)}/{len(th_results)}', flush=True)

th_tracker = [[r['alpha_id'], r['expression'], r['sharpe'], r['turnover'], r['fitness'], r['margin'], '', r.get('decay', 6)] for r in th_passing]

stone_bag = [a[0] for a in th_tracker if a[0]]
gold_bag = []
if stone_bag:
    gold_bag = check_submission(stone_bag, gold_bag, 0)
    print(f'Gold bag from TH: {len(gold_bag)}', flush=True)

# Add so_7
gold_bag.append(('gJmojOQm', 0.2997))
print(f'Gold bag final: {len(gold_bag)}', flush=True)

for a in gold_bag:
    print(f'  {a[0]} self_corr={a[1]:.4f}', flush=True)

with open(OUTPUT_DIR / 'step16-gold-bag.json', 'w') as f:
    json.dump({'count': len(gold_bag), 'gold': gold_bag}, f, indent=2, default=str)
with open(OUTPUT_DIR / 'step15-th-tracker.json', 'w') as f:
    json.dump({'count': len(th_tracker), 'alphas': th_tracker}, f, indent=2, default=str)
print('DONE', flush=True)
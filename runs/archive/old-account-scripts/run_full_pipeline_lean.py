#!/usr/bin/env python3
"""
Lean self-contained 3-order alpha factory
Does NOT depend on single_simulate (avoids hardcoded print/state issues)
Does inline simulation with direct API calls and proper polling
"""
import sys, json, time, random, requests
from pathlib import Path

sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import (
    login as brain_login, process_datafields,
    first_order_factory, load_task_pool_single,
    get_group_second_order_factory, trade_when_factory,
    check_submission, view_alphas, prune
)

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save(name, data):
    path = OUTPUT_DIR / name
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f'  [Saved] {name}')

def inline_simulate(s, expr, name=None, decay=0, neutralization='INDUSTRY'):
    """Run single alpha simulation with inline polling"""
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': neutralization,
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    sim_data = {'type': 'REGULAR', 'settings': settings, 'regular': expr}

    r = s.post('https://api.worldquantbrain.com/simulations', json=sim_data)
    if r.status_code != 201:
        print(f'  [{name}] POST failed {r.status_code}: {r.text[:100]}')
        return None

    url = r.headers['Location']
    for attempt in range(120):
        prog = s.get(url)
        h = prog.headers
        if h.get('Retry-After'):
            time.sleep(float(h['Retry-After']))
            continue
        result = prog.json()
        status = result.get('status')
        alpha_id = result.get('alpha')
        if status in ('COMPLETE', 'WARNING') and alpha_id:
            ar = s.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
            if ar.status_code == 200:
                ad = ar.json()
                is_m = ad.get('is', {})
                return {
                    'alpha_id': alpha_id,
                    'name': name,
                    'expression': expr,
                    'status': status,
                    'sharpe': is_m.get('sharpe'),
                    'fitness': is_m.get('fitness'),
                    'turnover': is_m.get('turnover'),
                    'margin': is_m.get('margin'),
                    'longCount': is_m.get('longCount'),
                    'shortCount': is_m.get('shortCount'),
                }
        elif status == 'ERROR':
            return {'alpha_id': None, 'name': name, 'status': 'ERROR', 'expression': expr}
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr}


def get_datafields_safe(s, dataset_id, region='USA', universe='TOP3000', delay=1):
    """Safe wrapper that handles API pagination correctly"""
    url_template = ("https://api.worldquantbrain.com/data-fields?"
        f"&instrumentType=EQUITY&region={region}&delay={delay}&universe={universe}"
        f"&dataset.id={dataset_id}&limit=50&offset={{x}}")
    count_resp = s.get(url_template.format(x=0))
    count = count_resp.json().get('count', 50)
    all_fields = []
    for offset in range(0, count, 50):
        resp = s.get(url_template.format(x=offset))
        data = resp.json()
        if 'results' in data:
            all_fields.extend(data['results'])
        elif isinstance(data, list):
            all_fields.extend(data)
    import pandas as pd
    return pd.DataFrame(all_fields)

# === PIPELINE ===
s = brain_login()
print('=== STEP 1: Login OK ===\n')

year = 2026  # hardcoded for current context

print('=== STEP 2: Get DataFields (model51) ===')
df = get_datafields_safe(s, 'model51', 'USA', 'TOP3000', 1)
matrix_fields = df[df['type'] == 'MATRIX']['id'].tolist()
print(f'Matrix fields ({len(matrix_fields)}): {matrix_fields}\n')

print('=== STEP 3: Preprocess ===')
pc_fields = process_datafields(df)
print(f'Preprocessed: {len(pc_fields)} expressions\n')

print('=== STEP 4: First Order Factory ===')
first_order = first_order_factory(pc_fields, ['ts_rank', 'ts_zscore', 'ts_delta', 'ts_mean'])
print(f'Generated: {len(first_order)} first-order alphas')
print(f'Sample: {first_order[:3]}\n')

print('=== STEP 5-6: Simulate First Order (limit 12) ===')
random.shuffle(first_order)
first_order_batch = first_order[:12]
init_decay = 6

fo_results = []
for i, expr in enumerate(first_order_batch):
    name = f'fo_{i+1}'
    print(f'  [{name}] {expr[:60]}')
    result = inline_simulate(s, expr, name=name, decay=init_decay)
    if result:
        fo_results.append(result)
        sh = result.get('sharpe', 'N/A')
        ft = result.get('fitness', 'N/A')
        print(f'    -> Sharpe={sh}, Fitness={ft}')
    time.sleep(2)

save('step6-fo-results.json', fo_results)

# Find passing alphas (Sharpe >= 0.5, Fitness >= 0.3)
fo_passing = [r for r in fo_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.5 and r.get('fitness', 0) >= 0.3]
print(f'\nFirst order passing: {len(fo_passing)}/{len(fo_results)}')
for r in fo_passing:
    print(f'  {r["name"]} Sharpe={r["sharpe"]:.2f} Fitness={r["fitness"]:.2f} expr={r["expression"][:50]}')

if not fo_passing:
    print('\nNO PASSING FIRST ORDER ALPHAS')
    save('pipeline-summary.json', {'pipeline': 'ABORTED', 'stage': 'first_order', 'fo_passed': 0})
    sys.exit(0)

# Build fo_tracker in same format as get_alphas returns: [alpha_id, exp, sharpe, turnover, fitness, margin, dateCreated, decay]
fo_tracker = []
for r in fo_passing:
    fo_tracker.append([
        r['alpha_id'], r['expression'],
        r['sharpe'], r['turnover'], r['fitness'], r['margin'],
        '', init_decay
    ])

print('\n=== STEP 7-8: Prune ===')
fo_layer = prune(fo_tracker, 'model51', 3)
print(f'After prune: {len(fo_layer)} alphas')
save('step8-fo-layer.json', {'count': len(fo_layer), 'layer': fo_layer})

print('\n=== STEP 9: Second Order Factory ===')
group_ops = ['group_rank', 'group_zscore', 'group_neutralize']
so_alpha_list = []
for expr, decay in fo_layer:
    for alpha in get_group_second_order_factory([expr], group_ops, 'USA'):
        so_alpha_list.append((alpha, decay))
print(f'Second order alphas: {len(so_alpha_list)}')
print(f'Sample: {so_alpha_list[:3] if so_alpha_list else "none"}\n')

if not so_alpha_list:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'second_order_gen', 'fo_passed': len(fo_passing)})
    sys.exit(0)

print('=== STEP 10: Simulate Second Order (limit 18) ===')
random.shuffle(so_alpha_list)
so_batch = so_alpha_list[:18]

so_results = []
for i, (expr, decay) in enumerate(so_batch):
    name = f'so_{i+1}'
    print(f'  [{name}] {expr[:70]}')
    result = inline_simulate(s, expr, name=name, decay=decay)
    if result:
        so_results.append(result)
        sh = result.get('sharpe', 'N/A')
        ft = result.get('fitness', 'N/A')
        print(f'    -> Sharpe={sh}, Fitness={ft}')
    time.sleep(2)

save('step10-so-results.json', so_results)

# Find passing SO (Sharpe >= 0.8, Fitness >= 0.5)
so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.8 and r.get('fitness', 0) >= 0.5]
print(f'\nSecond order passing: {len(so_passing)}/{len(so_results)}')
for r in so_passing:
    print(f'  {r["name"]} Sharpe={r["sharpe"]:.2f} Fitness={r["fitness"]:.2f}')

if not so_passing:
    print('\nNO PASSING SECOND ORDER ALPHAS - trying lower threshold (Sharpe >= 0.5, Fitness >= 0.3)')
    so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.5 and r.get('fitness', 0) >= 0.3]
    print(f'Second order passing (relaxed): {len(so_passing)}')

if not so_passing:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'second_order', 'fo_passed': len(fo_passing), 'so_passed': 0})
    sys.exit(0)

# Build so_tracker
so_tracker = []
for r in so_passing:
    so_tracker.append([
        r['alpha_id'], r['expression'],
        r['sharpe'], r['turnover'], r['fitness'], r['margin'],
        '', r.get('decay', init_decay)
    ])

print('\n=== STEP 11-12: Prune Second Order ===')
so_layer = prune(so_tracker, 'model51', 3)
print(f'After prune: {len(so_layer)} alphas')
save('step12-so-layer.json', {'count': len(so_layer), 'layer': so_layer})

if not so_layer:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'second_order_prune', 'fo_passed': len(fo_passing), 'so_passed': len(so_passing)})
    sys.exit(0)

print('\n=== STEP 13: Third Order Factory ===')
th_alpha_list = []
for expr, decay in so_layer:
    for alpha in trade_when_factory('trade_when', expr, 'USA'):
        th_alpha_list.append((alpha, decay))
print(f'Third order alphas: {len(th_alpha_list)}')
print(f'Sample: {th_alpha_list[:3] if th_alpha_list else "none"}\n')

if not th_alpha_list:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'third_order_gen', 'fo_passed': len(fo_passing), 'so_passed': len(so_passing)})
    sys.exit(0)

print('=== STEP 14: Simulate Third Order (limit 18) ===')
random.shuffle(th_alpha_list)
th_batch = th_alpha_list[:18]

th_results = []
for i, (expr, decay) in enumerate(th_batch):
    name = f'th_{i+1}'
    print(f'  [{name}] {expr[:70]}')
    result = inline_simulate(s, expr, name=name, decay=decay)
    if result:
        th_results.append(result)
        sh = result.get('sharpe', 'N/A')
        ft = result.get('fitness', 'N/A')
        print(f'    -> Sharpe={sh}, Fitness={ft}')
    time.sleep(2)

save('step14-th-results.json', th_results)

# Find passing TH (Sharpe >= 1.0, Fitness >= 0.7)
th_passing = [r for r in th_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.0 and r.get('fitness', 0) >= 0.7]
print(f'\nThird order passing: {len(th_passing)}/{len(th_results)}')
for r in th_passing:
    print(f'  {r["name"]} Sharpe={r["sharpe"]:.2f} Fitness={r["fitness"]:.2f}')

# Build th_tracker
th_tracker = []
for r in th_passing:
    th_tracker.append([
        r['alpha_id'], r['expression'],
        r['sharpe'], r['turnover'], r['fitness'], r['margin'],
        '', r.get('decay', init_decay)
    ])

save('step15-th-tracker.json', {'count': len(th_tracker), 'alphas': th_tracker})

print('\n=== STEP 16: Check Submission ===')
stone_bag = [a[0] for a in th_tracker if a[0]]
gold_bag = []
if stone_bag:
    print(f'Checking {len(stone_bag)} alphas...')
    gold_bag = check_submission(stone_bag, gold_bag, 0)
    print(f'Passed: {len(gold_bag)}')
    save('step16-gold-bag.json', {'count': len(gold_bag), 'gold': gold_bag})
else:
    print('No candidates to check')

print('\n=== STEP 17: Top Alphas ===')
if gold_bag:
    view_alphas(gold_bag)
else:
    print('No gold bag - top tracker alphas:')
    for a in th_tracker[:10]:
        print(f'  {a[0]} Sharpe={a[2]:.3f} Fitness={a[4]:.3f}')

summary = {
    'first_order_gen': len(first_order),
    'first_order_simulated': len(fo_results),
    'first_order_passed': len(fo_passing),
    'second_order_gen': len(so_alpha_list),
    'second_order_simulated': len(so_results),
    'second_order_passed': len(so_passing),
    'third_order_gen': len(th_alpha_list),
    'third_order_simulated': len(th_results),
    'third_order_passed': len(th_passing),
    'gold_bag': len(gold_bag),
    'fo_results': fo_results,
    'so_results': so_results,
    'th_results': th_results,
}

print('\n=== PIPELINE COMPLETE ===')
print(json.dumps(summary, indent=2))
save('pipeline-complete.json', summary)
print('\nAll output saved to simulation-captures/')
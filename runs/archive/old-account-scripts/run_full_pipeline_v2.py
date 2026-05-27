#!/usr/bin/env python3
"""
Full 3-order alpha factory pipeline - self-contained
Uses single session, no repeated login() calls, direct API throughout.
"""
import sys, json, time, random
from pathlib import Path
import pandas as pd
import requests

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Login (single session, reused) ───────────────────────────────────────────
s = requests.Session()
s.auth = ("zpdedn@gmail.com", "zp82648185000")
resp = s.post('https://api.worldquantbrain.com/authentication')
print(f"=== STEP 1: Login → {resp.status_code} ===\n")

# ── DataFields (direct API, no library helper to avoid session issues) ─────────
url = ("https://api.worldquantbrain.com/data-fields?"
       "instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000"
       "&dataset.id=model51&limit=50&offset=0")
data = s.get(url).json()
df = pd.DataFrame(data.get('results', []))
matrix_fields = df[df['type'] == 'MATRIX']['id'].tolist()
print(f"=== STEP 2: DataFields (model51) ===")
print(f"Matrix fields ({len(matrix_fields)}): {matrix_fields}\n")

# ── Preprocess ─────────────────────────────────────────────────────────────────
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import process_datafields, first_order_factory, load_task_pool_single
from machine_lib import get_group_second_order_factory, trade_when_factory, prune, check_submission, view_alphas

pc_fields = process_datafields(df)
print(f"=== STEP 3: Preprocess ===")
print(f"Preprocessed: {len(pc_fields)} expressions\n")

# ── First Order Factory ────────────────────────────────────────────────────────
first_order = first_order_factory(pc_fields, ['ts_rank', 'ts_zscore', 'ts_delta', 'ts_mean'])
print(f"=== STEP 4: First Order Factory ===")
print(f"Generated: {len(first_order)} alphas\n")

# ── Inline Simulate ───────────────────────────────────────────────────────────
def inline_simulate(expr, name, decay=0, neutralization='INDUSTRY'):
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
            }
        elif status == 'ERROR':
            return {'alpha_id': None, 'name': name, 'status': 'ERROR', 'expression': expr}
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr}

def save(name, data):
    path = OUTPUT_DIR / name
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  [Saved] {name}")

# ── Simulate First Order (limit 12) ───────────────────────────────────────────
random.shuffle(first_order)
init_decay = 6
fo_results = []
for i, expr in enumerate(first_order[:12]):
    print(f"  [fo_{i+1}] {expr[:60]}")
    r = inline_simulate(expr, f'fo_{i+1}', decay=init_decay)
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']}, Fitness={r['fitness']}")
    else:
        print(f"    {r['status']}")
    fo_results.append(r)
    time.sleep(3)

save('step6-fo-results.json', fo_results)
fo_passing = [r for r in fo_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.5 and r.get('fitness', 0) >= 0.3]
print(f"\nFirst order passing: {len(fo_passing)}/{len(fo_results)}")

if not fo_passing:
    save('pipeline-summary.json', {'pipeline': 'ABORTED', 'stage': 'first_order', 'fo_passed': 0})
    print("NO PASSING FIRST ORDER ALPHAS")
    sys.exit(0)

fo_tracker = [[r['alpha_id'], r['expression'], r['sharpe'], r['turnover'], r['fitness'], r['margin'], '', init_decay] for r in fo_passing]

# ── Prune First Order ──────────────────────────────────────────────────────────
fo_layer = prune(fo_tracker, 'model51', 3)
print(f"\n=== STEP 7-8: Prune → {len(fo_layer)} after prune ===")
save('step8-fo-layer.json', {'count': len(fo_layer), 'layer': fo_layer})

# ── Second Order Factory ───────────────────────────────────────────────────────
group_ops = ['group_rank', 'group_zscore', 'group_neutralize']
so_alpha_list = []
for expr, decay in fo_layer:
    for alpha in get_group_second_order_factory([expr], group_ops, 'USA'):
        so_alpha_list.append((alpha, decay))
print(f"\n=== STEP 9: Second Order Factory → {len(so_alpha_list)} alphas ===")
print(f"Sample: {so_alpha_list[:2] if so_alpha_list else 'none'}\n")

if not so_alpha_list:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'second_order_gen', 'fo_passed': len(fo_passing)})
    sys.exit(0)

# ── Simulate Second Order (limit 18) ─────────────────────────────────────────
random.shuffle(so_alpha_list)
so_results = []
for i, (expr, decay) in enumerate(so_alpha_list[:18]):
    print(f"  [so_{i+1}] {expr[:70]}")
    r = inline_simulate(expr, f'so_{i+1}', decay=decay)
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']}, Fitness={r['fitness']}")
    else:
        print(f"    {r['status']}")
    so_results.append(r)
    time.sleep(3)

save('step10-so-results.json', so_results)
so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.8 and r.get('fitness', 0) >= 0.5]
if not so_passing:
    so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.5 and r.get('fitness', 0) >= 0.3]
print(f"\nSecond order passing: {len(so_passing)}/{len(so_results)}")

if not so_passing:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'second_order', 'fo_passed': len(fo_passing), 'so_passed': 0})
    sys.exit(0)

so_tracker = [[r['alpha_id'], r['expression'], r['sharpe'], r['turnover'], r['fitness'], r['margin'], '', decay] for r in so_passing]

# ── Prune Second Order ─────────────────────────────────────────────────────────
so_layer = prune(so_tracker, 'model51', 3)
print(f"\n=== STEP 11-12: Prune → {len(so_layer)} after prune ===")
save('step12-so-layer.json', {'count': len(so_layer), 'layer': so_layer})

if not so_layer:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'second_order_prune', 'fo_passed': len(fo_passing), 'so_passed': len(so_passing)})
    sys.exit(0)

# ── Third Order Factory ────────────────────────────────────────────────────────
th_alpha_list = []
for expr, decay in so_layer:
    for alpha in trade_when_factory('trade_when', expr, 'USA'):
        th_alpha_list.append((alpha, decay))
print(f"\n=== STEP 13: Third Order Factory → {len(th_alpha_list)} alphas ===")
print(f"Sample: {th_alpha_list[:2] if th_alpha_list else 'none'}\n")

if not th_alpha_list:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'third_order_gen', 'fo_passed': len(fo_passing), 'so_passed': len(so_passing)})
    sys.exit(0)

# ── Simulate Third Order (limit 18) ──────────────────────────────────────────
random.shuffle(th_alpha_list)
th_results = []
for i, (expr, decay) in enumerate(th_alpha_list[:18]):
    print(f"  [th_{i+1}] {expr[:70]}")
    r = inline_simulate(expr, f'th_{i+1}', decay=decay)
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']}, Fitness={r['fitness']}")
    else:
        print(f"    {r['status']}")
    th_results.append(r)
    time.sleep(3)

save('step14-th-results.json', th_results)
th_passing = [r for r in th_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.0 and r.get('fitness', 0) >= 0.7]
print(f"\nThird order passing: {len(th_passing)}/{len(th_results)}")

th_tracker = [[r['alpha_id'], r['expression'], r['sharpe'], r['turnover'], r['fitness'], r['margin'], '', decay] for r in th_passing]
save('step15-th-tracker.json', {'count': len(th_tracker), 'alphas': th_tracker})

# ── Submission Check ───────────────────────────────────────────────────────────
stone_bag = [a[0] for a in th_tracker if a[0]]
gold_bag = []
if stone_bag:
    print(f"\n=== STEP 16: Checking {len(stone_bag)} alphas ===")
    gold_bag = check_submission(stone_bag, gold_bag, 0)
    print(f"Passed submission: {len(gold_bag)}")
    save('step16-gold-bag.json', {'count': len(gold_bag), 'gold': gold_bag})
else:
    print("\n=== STEP 16: No candidates to check ===")

# ── Top Alphas ─────────────────────────────────────────────────────────────────
print("\n=== STEP 17: Top Alphas ===")
if gold_bag:
    view_alphas(gold_bag)
else:
    for a in th_tracker[:10]:
        print(f"  {a[0]} Sharpe={a[2]:.3f} Fitness={a[4]:.3f}")

# ── Summary ───────────────────────────────────────────────────────────────────
summary = {
    'first_order_gen': len(first_order), 'first_order_simulated': len(fo_results),
    'first_order_passed': len(fo_passing), 'second_order_gen': len(so_alpha_list),
    'second_order_simulated': len(so_results), 'second_order_passed': len(so_passing),
    'third_order_gen': len(th_alpha_list), 'third_order_simulated': len(th_results),
    'third_order_passed': len(th_passing), 'gold_bag': len(gold_bag),
}
print("\n=== PIPELINE COMPLETE ===")
print(json.dumps(summary, indent=2))
save('pipeline-complete.json', summary)
print(f"\nAll results saved to {OUTPUT_DIR}/")
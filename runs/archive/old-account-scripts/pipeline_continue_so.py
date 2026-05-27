#!/usr/bin/env python3
"""
Pipeline continuation from Step 8 FO layer:
- fo_2: ts_zscore(unsystematic_risk_last_60_days, 66) → Sharpe=0.91, Fitness=0.58
- fo_3: ts_mean(correlation_last_360_days_spy, 120) → Sharpe=0.63, Fitness=0.49
Runs Second Order factory on these 2 FO candidates.
"""
import sys, json, time, random
from pathlib import Path
import requests

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.auth = ("zpdedn@gmail.com", "zp82648185000")
s.post('https://api.worldquantbrain.com/authentication')
print(f"Auth OK")

sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import get_group_second_order_factory, prune, trade_when_factory, check_submission, view_alphas

def save(name, data):
    path = OUTPUT_DIR / name
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  [Saved] {name}")

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

# ── FO Layer from step8 ────────────────────────────────────────────────────────
fo_layer = [
    ["ts_zscore(winsorize(ts_backfill(unsystematic_risk_last_60_days, 120), std=4), 66)", 6],
    ["ts_mean(winsorize(ts_backfill(correlation_last_360_days_spy, 120), std=4), 120)", 6],
]
fo_tracker = [
    ["alpha_a", "ts_zscore(winsorize(ts_backfill(unsystematic_risk_last_60_days, 120), std=4), 66)", 0.91, 0.154, 0.58, 0.0008, "", 6],
    ["alpha_b", "ts_mean(winsorize(ts_backfill(correlation_last_360_days_spy, 120), std=4), 120)", 0.63, 0.012, 0.49, 0.0127, "", 6],
]

# ── Second Order Factory ──────────────────────────────────────────────────────
print("=== STEP 9: Second Order Factory ===")
group_ops = ['group_rank', 'group_zscore', 'group_neutralize']
so_alpha_list = []
for expr, decay in fo_layer:
    for alpha in get_group_second_order_factory([expr], group_ops, 'USA'):
        so_alpha_list.append((alpha, decay))
print(f"SO alphas generated: {len(so_alpha_list)}")
print(f"Sample: {so_alpha_list[:3] if so_alpha_list else 'none'}\n")

if not so_alpha_list:
    print("No SO alphas generated")
    sys.exit(0)

# ── Simulate Second Order ─────────────────────────────────────────────────────
print("=== STEP 10: Simulate Second Order ===")
random.shuffle(so_alpha_list)
so_batch = so_alpha_list[:24]

so_results = []
for i, (expr, decay) in enumerate(so_batch):
    name = f'so_{i+1}'
    print(f"  [{name}] {expr[:70]}")
    r = inline_simulate(expr, name, decay=decay)
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']}, Fitness={r['fitness']}, TVR={r['turnover']}")
    else:
        print(f"    {r['status']}")
    so_results.append(r)
    time.sleep(3)

save('step10-so-results.json', so_results)
print(f"\nSO simulated: {len(so_results)}")

# Passing thresholds
so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.8 and r.get('fitness', 0) >= 0.5]
if not so_passing:
    so_passing = [r for r in so_results if r.get('sharpe') is not None and r.get('sharpe') >= 0.5 and r.get('fitness', 0) >= 0.3]
print(f"SO passing: {len(so_passing)}/{len(so_results)}")

if not so_passing:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'second_order', 'fo_passed': 2, 'so_passed': 0})
    sys.exit(0)

# Build so_tracker (same format as prune expects)
so_tracker = []
for r in so_passing:
    so_tracker.append([r['alpha_id'], r['expression'], r['sharpe'], r['turnover'], r['fitness'], r['margin'], '', r.get('decay', 6)])

# ── Prune Second Order ─────────────────────────────────────────────────────────
print(f"\n=== STEP 11-12: Prune → {len(so_tracker)} candidates ===")
so_layer = prune(so_tracker, 'model51', 3)
print(f"After prune: {len(so_layer)}")
save('step12-so-layer.json', {'count': len(so_layer), 'layer': so_layer})

if not so_layer:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'second_order_prune', 'fo_passed': 2, 'so_passed': len(so_passing)})
    sys.exit(0)

# ── Third Order Factory ────────────────────────────────────────────────────────
print(f"\n=== STEP 13: Third Order Factory ===")
th_alpha_list = []
for expr, decay in so_layer:
    for alpha in trade_when_factory('trade_when', expr, 'USA'):
        th_alpha_list.append((alpha, decay))
print(f"TH alphas: {len(th_alpha_list)}")

if not th_alpha_list:
    save('pipeline-summary.json', {'pipeline': 'PARTIAL', 'stage': 'third_order_gen', 'fo_passed': 2, 'so_passed': len(so_passing)})
    sys.exit(0)

# ── Simulate Third Order ────────────────────────────────────────────────────────
print(f"\n=== STEP 14: Simulate Third Order (limit 18) ===")
random.shuffle(th_alpha_list)
th_batch = th_alpha_list[:18]

th_results = []
for i, (expr, decay) in enumerate(th_batch):
    name = f'th_{i+1}'
    print(f"  [{name}] {expr[:70]}")
    r = inline_simulate(expr, name, decay=decay)
    if r.get('alpha_id'):
        print(f"    Sharpe={r['sharpe']}, Fitness={r['fitness']}")
    else:
        print(f"    {r['status']}")
    th_results.append(r)
    time.sleep(3)

save('step14-th-results.json', th_results)
th_passing = [r for r in th_results if r.get('sharpe') is not None and r.get('sharpe') >= 1.0 and r.get('fitness', 0) >= 0.7]
print(f"\nTH passing: {len(th_passing)}/{len(th_results)}")

th_tracker = [[r['alpha_id'], r['expression'], r['sharpe'], r['turnover'], r['fitness'], r['margin'], '', r.get('decay', 6)] for r in th_passing]
save('step15-th-tracker.json', {'count': len(th_tracker), 'alphas': th_tracker})

# ── Submission Check ────────────────────────────────────────────────────────────
stone_bag = [a[0] for a in th_tracker if a[0]]
gold_bag = []
if stone_bag:
    print(f"\n=== STEP 16: Checking {len(stone_bag)} alphas ===")
    gold_bag = check_submission(stone_bag, gold_bag, 0)
    print(f"Passed: {len(gold_bag)}")
    save('step16-gold-bag.json', {'count': len(gold_bag), 'gold': gold_bag})

print("\n=== STEP 17: Top Alphas ===")
if gold_bag:
    view_alphas(gold_bag)
else:
    for a in th_tracker[:10]:
        print(f"  {a[0]} Sharpe={a[2]:.3f} Fitness={a[4]:.3f}")

summary = {
    'fo_layer': [f[0] for f in fo_layer],
    'second_order_gen': len(so_alpha_list),
    'second_order_simulated': len(so_results),
    'second_order_passed': len(so_passing),
    'third_order_gen': len(th_alpha_list),
    'third_order_simulated': len(th_results),
    'third_order_passed': len(th_passing),
    'gold_bag': len(gold_bag),
}
print("\n=== PIPELINE CONTINUATION COMPLETE ===")
print(json.dumps(summary, indent=2))
save('pipeline-complete.json', summary)
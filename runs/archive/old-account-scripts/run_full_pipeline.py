#!/usr/bin/env python3
"""
Full 3-order alpha factory pipeline
Dataset: model51 (Systematic Risk Metrics) - low crowding, 16 fields
"""
import sys, json, time, random
from pathlib import Path

sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import (
    login, get_datafields, process_datafields,
    first_order_factory, load_task_pool_single,
    single_simulate, get_alphas, prune,
    get_group_second_order_factory, trade_when_factory,
    check_submission, view_alphas
)

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save(name, data):
    path = OUTPUT_DIR / name
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  [Saved] {path}")

s = login()
print("=== STEP 1: Login ===")
print("Logged in OK\n")

print("=== STEP 2: Get DataFields (model51) ===")
df = get_datafields(s, dataset_id='model51', region='USA', universe='TOP3000', delay=1)
matrix_fields = df[df['type'] == 'MATRIX']['id'].tolist()
print(f"Matrix fields ({len(matrix_fields)}): {matrix_fields}\n")

print("=== STEP 3: Preprocess ===")
pc_fields = process_datafields(df)
print(f"Preprocessed expressions: {len(pc_fields)}\n")

print("=== STEP 4: First Order Factory ===")
first_order = first_order_factory(pc_fields, ["ts_rank", "ts_zscore", "ts_delta", "ts_mean"])
print(f"First order alphas generated: {len(first_order)}")
print(f"Sample: {first_order[:3]}\n")

print("=== STEP 5: Load Task Pool ===")
init_decay = 6
random.shuffle(first_order)
fo_alpha_list = [(a, init_decay) for a in first_order[:20]]
fo_pools = load_task_pool_single(fo_alpha_list, 3)
print(f"Pools: {len(fo_pools)}\n")

print("=== STEP 6: First Order Simulate ===")
single_simulate(fo_pools, "SUBINDUSTRY", "USA", "TOP3000", 0)
print("First order simulate done\n")

print("=== STEP 7: Get Promising First Order Alphas ===")
time.sleep(5)
fo_tracker = get_alphas("05-01", "05-15", 0.5, 0.3, "USA", 50, "track")
print(f"First order promising: {len(fo_tracker)}")
save("step7-fo-tracker.json", {"count": len(fo_tracker), "alphas": fo_tracker})
print()

if len(fo_tracker) == 0:
    print("NO PASSING FIRST ORDER ALPHAS - aborting")
    sys.exit(0)

print("=== STEP 8: Prune ===")
fo_layer = prune(fo_tracker, 'model51', 3)
print(f"After prune: {len(fo_layer)}")
save("step8-fo-layer.json", {"count": len(fo_layer), "layer": fo_layer})
print()

print("=== STEP 9: Second Order Factory ===")
group_ops = ["group_rank", "group_zscore", "group_neutralize"]
so_alpha_list = []
for expr, decay in fo_layer:
    for alpha in get_group_second_order_factory([expr], group_ops, "USA"):
        so_alpha_list.append((alpha, decay))
print(f"Second order alphas: {len(so_alpha_list)}")
print(f"Sample: {so_alpha_list[:3]}\n")

print("=== STEP 10: Simulate Second Order ===")
random.shuffle(so_alpha_list)
so_pools = load_task_pool_single(so_alpha_list[:30], 3)
single_simulate(so_pools, 'SUBINDUSTRY', 'USA', 'TOP3000', 0)
print("Second order simulate done\n")

print("=== STEP 11: Get Second Order Alphas ===")
time.sleep(5)
so_tracker = get_alphas("05-01", "05-15", 0.8, 0.5, "USA", 100, "track")
print(f"Second order promising: {len(so_tracker)}")
save("step11-so-tracker.json", {"count": len(so_tracker), "alphas": so_tracker})
print()

if len(so_tracker) == 0:
    print("NO PASSING SECOND ORDER ALPHAS - stopping pipeline")
    sys.exit(0)

print("=== STEP 12: Prune Second Order ===")
so_layer = prune(so_tracker, 'model51', 3)
print(f"After prune: {len(so_layer)}")
save("step12-so-layer.json", {"count": len(so_layer), "layer": so_layer})
print()

print("=== STEP 13: Third Order Factory ===")
th_alpha_list = []
for expr, decay in so_layer:
    for alpha in trade_when_factory("trade_when", expr, "USA"):
        th_alpha_list.append((alpha, decay))
print(f"Third order alphas: {len(th_alpha_list)}")
print(f"Sample: {th_alpha_list[:3]}\n")

print("=== STEP 14: Simulate Third Order ===")
random.shuffle(th_alpha_list)
th_pools = load_task_pool_single(th_alpha_list[:30], 3)
single_simulate(th_pools, 'SUBINDUSTRY', 'USA', 'TOP3000', 0)
print("Third order simulate done\n")

print("=== STEP 15: Get Third Order Alphas (Submit) ===")
time.sleep(5)
th_tracker = get_alphas("05-01", "05-15", 1.0, 0.7, "USA", 200, "submit")
print(f"Third order candidates: {len(th_tracker)}")
save("step15-th-tracker.json", {"count": len(th_tracker), "alphas": th_tracker})
print()

print("=== STEP 16: Check Submission ===")
stone_bag = [a[0] for a in th_tracker]
gold_bag = []
if stone_bag:
    print(f"Checking {len(stone_bag)} alphas...")
    gold_bag = check_submission(stone_bag, gold_bag, 0)
    print(f"Passed: {len(gold_bag)}")
    save("step16-gold-bag.json", {"count": len(gold_bag), "gold": gold_bag})
else:
    print("No candidates to check")

print("=== STEP 17: View Top Alphas ===")
if gold_bag:
    view_alphas(gold_bag)
else:
    print("No gold bag - showing top trackers")
    for a in th_tracker[:10]:
        print(f"  {a[0]} Sharpe={a[2]:.3f} Fitness={a[4]:.3f}")

summary = {
    "first_order_gen": len(first_order),
    "first_order_passed": len(fo_tracker),
    "second_order_gen": len(so_alpha_list),
    "second_order_passed": len(so_tracker),
    "third_order_gen": len(th_alpha_list),
    "third_order_passed": len(th_tracker),
    "gold_bag": len(gold_bag)
}
print("\n=== PIPELINE COMPLETE ===")
print(json.dumps(summary, indent=2))
save("pipeline-complete.json", summary)
print("All steps done!")
#!/usr/bin/env python3
"""
整理可提交的alpha - 基于已运行的升级结果
"""
import sys, json
from pathlib import Path
import requests

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')

s = requests.Session()
s.auth = ("zpdedn@gmail.com", "zp82648185000")
s.post('https://api.worldquantbrain.com/authentication')

sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import check_submission, view_alphas

# 基于运行结果整理的最佳候选
BEST_CANDIDATES = [
    # 1阶原始 (从alpha_loop.py)
    {"expr": "rank(-ts_zscore(close, 5))", "decay": 0, "neutralization": "SUBINDUSTRY", "sharpe": 1.87, "fitness": 1.04, "turnover": 0.53, "source": "1阶原始"},
    {"expr": "rank(-ts_zscore(close, 5))", "decay": 0, "neutralization": "INDUSTRY", "sharpe": 1.78, "fitness": 1.05, "turnover": 0.52, "source": "1阶原始"},

    # 2阶SO
    {"expr": "group_zscore(rank(-ts_zscore(close, 5)), densify(sector))", "decay": 5, "neutralization": "SUBINDUSTRY", "sharpe": 1.88, "fitness": 1.05, "turnover": 0.531, "source": "2阶SO"},
    {"expr": "rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector)))", "decay": 5, "neutralization": "INDUSTRY", "sharpe": 1.79, "fitness": 1.05, "turnover": 0.522, "source": "2阶SO"},
    {"expr": "rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector)))", "decay": 10, "neutralization": "INDUSTRY", "sharpe": 1.50, "fitness": 0.93, "turnover": 0.397, "source": "2阶SO"},

    # 3阶TH (trade_when)
    {"expr": "trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, group_zscore(rank(-ts_zscore(close,5)),densify(sector)), -1)", "decay": 0, "neutralization": "SUBINDUSTRY", "sharpe": 1.66, "fitness": 0.91, "turnover": 0.360, "source": "3阶TH"},
    {"expr": "trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, rank(group_zscore(rank(-ts_zscore(close,5)),densify(sector))), -1)", "decay": 0, "neutralization": "SUBINDUSTRY", "sharpe": 1.59, "fitness": 1.06, "turnover": 0.266, "source": "3阶TH"},
    {"expr": "trade_when(ts_corr(close, volume, 20) > 0, rank(group_zscore(rank(-ts_zscore(close,5)),densify(sector))), -1)", "decay": 0, "neutralization": "SUBINDUSTRY", "sharpe": 1.45, "fitness": 0.84, "turnover": 0.240, "source": "3阶TH"},
    {"expr": "trade_when(ts_corr(close, volume, 5) < 0, group_zscore(rank(-ts_zscore(close,5)),densify(sector)), -1)", "decay": 0, "neutralization": "SUBINDUSTRY", "sharpe": 1.46, "fitness": 0.71, "turnover": 0.363, "source": "3阶TH"},
    {"expr": "trade_when(ts_corr(close, volume, 5) > 0.3, group_zscore(rank(-ts_zscore(close,5)),densify(sector)), -1)", "decay": 0, "neutralization": "SUBINDUSTRY", "sharpe": 1.27, "fitness": 0.61, "turnover": 0.284, "source": "3阶TH"},
]

def inline_simulate(expr, name, decay=0, neutralization='SUBINDUSTRY'):
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': neutralization,
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    r = s.post('https://api.worldquantbrain.com/simulations', json={'type': 'REGULAR', 'settings': settings, 'regular': expr})
    if r.status_code != 201:
        return None
    url = r.headers['Location']
    for _ in range(120):
        prog = s.get(url)
        h = prog.headers
        if h.get('Retry-After'):
            import time
            time.sleep(float(h['Retry-After']))
            continue
        result = prog.json()
        status = result.get('status')
        alpha_id = result.get('alpha')
        if status in ('COMPLETE', 'WARNING') and alpha_id:
            ad = s.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}').json()
            is_m = ad.get('is', {})
            return {
                'alpha_id': alpha_id,
                'sharpe': is_m.get('sharpe'),
                'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'),
                'margin': is_m.get('margin'),
            }
        import time
        time.sleep(5)
    return None

# 筛选通过阈值的候选
PASS_THRESHOLDS = {"sharpe": 1.25, "fitness": 0.8, "turnover": 0.7}
submissible = []
for c in BEST_CANDIDATES:
    if c['sharpe'] >= PASS_THRESHOLDS['sharpe'] and c['fitness'] >= PASS_THRESHOLDS['fitness'] and c['turnover'] <= PASS_THRESHOLDS['turnover']:
        submissible.append(c)

print("=" * 80)
print("可提交Alpha候选 (Sharpe>=1.25, Fitness>=0.8, TVR<=0.7)")
print("=" * 80)

for i, c in enumerate(submissible):
    print(f"\n【{i+1}】 {c['source']}")
    print(f"    Expression: {c['expr']}")
    print(f"    Decay: {c['decay']}, Neutralization: {c['neutralization']}")
    print(f"    Sharpe: {c['sharpe']:.3f}, Fitness: {c['fitness']:.3f}, TVR: {c['turnover']:.3f}")

print(f"\n\n共 {len(submissible)} 个候选需要模拟获取alpha_id...")
print("正在模拟获取alpha_id...\n")

alpha_ids = []
for i, c in enumerate(submissible):
    print(f"模拟 [{i+1}/{len(submissible)}]: {c['expr'][:50]}...")
    r = inline_simulate(c['expr'], f"sub_{i+1}", c['decay'], c['neutralization'])
    if r and r.get('alpha_id'):
        c['alpha_id'] = r['alpha_id']
        alpha_ids.append(r['alpha_id'])
        print(f"  -> ID: {r['alpha_id']}, Sharpe={r['sharpe']}")
    else:
        c['alpha_id'] = None
        print(f"  -> 失败")
    import time
    time.sleep(3)

# 检查提交资格
stone_bag = [c['alpha_id'] for c in submissible if c.get('alpha_id')]
print(f"\n\n共 {len(stone_bag)} 个alpha_id待检查...")
gold_bag = check_submission(stone_bag, [], 0)

print("\n" + "=" * 80)
print("最终可提交Alpha")
print("=" * 80)
if gold_bag:
    view_alphas(gold_bag)
else:
    print("无gold bag候选")
    print("\n候选详情:")
    for c in submissible:
        print(f"  {c.get('alpha_id', 'N/A')} | Sharpe={c['sharpe']:.3f} | {c['expr'][:60]}")

# 保存结果
save_path = OUTPUT_DIR / 'upgrade_submissible.json'
with open(save_path, 'w') as f:
    json.dump(submissible, f, indent=2, default=str)
print(f"\n已保存到: {save_path}")
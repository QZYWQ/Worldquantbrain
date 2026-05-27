#!/usr/bin/env python3
"""
Alpha 2阶/3阶 Optimization Pipeline
针对用户提供的unsubmitted alpha进行极致升阶优化

Priority:
1. 高Fitness候选 (F > 1.3): 6XRqZ02Y, MPblNjqM, qMnArZeZ, wp5VVGRY
2. 用户优先候选 (10条): blNRGAJl, WjN75gAO, RRNaRYm1等
3. ts_rank系列: rKboMqz3, j2nQQbRk, O0npXMlq, 9q9QQ6vV
"""

import sys
import json
import time
import requests
from pathlib import Path

# 凭证和路径
CREDENTIALS = ('zpdedn@gmail.com', 'zp82648185000')
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
BATCH_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches')
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')

# ============================================================
# Alpha ID列表 (从用户数据整理)
# ============================================================

# Priority 1: 高Fitness候选 (F >= 1.3)
HIGH_FITNESS_CANDIDATES = [
    {'id': '6XRqZ02Y', 'orig_s': 1.11, 'orig_f': 1.82, 'tvr': 0.029, 'note': '新结构fnd6_rea-fnd6_pstkrv/fnd6_pstkl'},
    {'id': 'MPblNjqM', 'orig_s': 1.02, 'orig_f': 1.56, 'tvr': 0.037, 'note': '同上变体'},
    {'id': 'qMnArZeZ', 'orig_s': 1.33, 'orig_f': 1.35, 'tvr': 0.016, 'note': '疑似blNRGAJl变体,双达标'},
    {'id': 'wp5VVGRY', 'orig_s': 0.96, 'orig_f': 1.80, 'tvr': 0.008, 'note': 'fn_interest_paid新方向'},
]

# Priority 2: 用户优先候选 (10条)
USER_PRIORITY_CANDIDATES = [
    {'id': 'blNRGAJl', 'orig_s': 1.14, 'orig_f': 1.26, 'tvr': 0.018, 'note': 'Sharpe差0.11+权重集中'},
    {'id': 'WjN75gAO', 'orig_s': 0.84, 'orig_f': 0.99, 'tvr': 0.015, 'note': '双重不达标'},
    {'id': 'RRNaRYm1', 'orig_s': 1.00, 'orig_f': 0.90, 'tvr': 0.020, 'note': '三重问题'},
    {'id': '9q9VLAm1', 'orig_s': 1.00, 'orig_f': 0.90, 'tvr': 0.020, 'note': '三重问题'},
    {'id': '1Yow6066', 'orig_s': 0.77, 'orig_f': 0.93, 'tvr': 0.029, 'note': '三重问题'},
    {'id': 'Xgk7Qz6X', 'orig_s': 1.03, 'orig_f': 0.64, 'tvr': 0.013, 'note': 'Fitness差0.36'},
    {'id': '78xjEAML', 'orig_s': 1.03, 'orig_f': 0.64, 'tvr': 0.013, 'note': 'Fitness差0.36'},
    {'id': 'e7ngp37l', 'orig_s': 0.89, 'orig_f': 0.67, 'tvr': 0.016, 'note': '简单结构但弱'},
    {'id': 'P0n7xG3q', 'orig_s': 0.83, 'orig_f': 0.65, 'tvr': 0.011, 'note': '简单结构但弱'},
    {'id': 'vR5jdo7A', 'orig_s': 0.72, 'orig_f': 0.69, 'tvr': 0.014, 'note': '简单结构但弱'},
]

# Priority 3: ts_rank系列 (F ≈ 1.29-1.31)
TS_RANK_CANDIDATES = [
    {'id': 'rKboMqz3', 'orig_s': 0.77, 'orig_f': 1.31, 'tvr': 0.009, 'note': 'ts_rank(fnd6_recco)'},
    {'id': 'j2nQQbRk', 'orig_s': 0.77, 'orig_f': 1.31, 'tvr': 0.012, 'note': 'ts_rank(fnd6_prstkc)'},
    {'id': 'O0npXMlq', 'orig_s': 0.76, 'orig_f': 1.29, 'tvr': 0.012, 'note': 'ts_rank(fnd6_rectr)'},
    {'id': '9q9QQ6vV', 'orig_s': 0.76, 'orig_f': 1.29, 'tvr': 0.013, 'note': 'ts_rank(fnd6_reajo)'},
]

# ============================================================
# API Functions
# ============================================================

def get_alpha_expression(sess, alpha_id):
    """获取alpha expression"""
    r = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
    if r.status_code != 200:
        print(f"  Failed to fetch {alpha_id}: {r.status_code}")
        return None
    data = r.json()
    return data.get('regular', {}).get('code')

def inline_simulate(sess, expr, name=None, decay=0, neutralization='INDUSTRY'):
    """模拟单个alpha"""
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': neutralization,
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    r = sess.post('https://api.worldquantbrain.com/simulations',
                  json={'type': 'REGULAR', 'settings': settings, 'regular': expr})
    if r.status_code != 201:
        return {'alpha_id': None, 'name': name, 'status': f'POST_FAIL_{r.status_code}', 'expression': expr, 'decay': decay}
    url = r.headers['Location']
    for _ in range(120):
        prog = sess.get(url)
        h = prog.headers
        if h.get('Retry-After'):
            time.sleep(float(h['Retry-After']))
            continue
        result = prog.json()
        status = result.get('status')
        alpha_id = result.get('alpha')
        if status in ('COMPLETE', 'WARNING') and alpha_id:
            ad = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}').json()
            is_m = ad.get('is', {})
            return {
                'alpha_id': alpha_id, 'name': name, 'expression': expr, 'status': status,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'margin': is_m.get('margin'),
                'longCount': is_m.get('longCount', 0), 'shortCount': is_m.get('shortCount', 0),
                'decay': decay, 'neutralization': neutralization,
            }
        elif status == 'ERROR':
            return {'alpha_id': None, 'name': name, 'status': 'ERROR', 'expression': expr, 'decay': decay}
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr, 'decay': decay}


# ============================================================
# 2阶/3阶 优化变换模板
# ============================================================

def apply_2nd_order_transforms(base_expr, alpha_id):
    """应用2阶变换: rank, group_rank, zscore, ts_mean等"""
    transforms = []

    # 2阶A: rank标准化
    transforms.append({
        'name': f'{alpha_id}_2A_rank',
        'expr': f'rank({base_expr})',
        'decay': 0,
        'neutralization': 'INDUSTRY',
        'stage': '2阶A'
    })

    # 2阶B: group_rank行业中性
    transforms.append({
        'name': f'{alpha_id}_2B_group_rank',
        'expr': f'group_rank(rank({base_expr}), subindustry)',
        'decay': 0,
        'neutralization': 'SUBINDUSTRY',
        'stage': '2阶B'
    })

    # 2阶C: ts_mean平滑
    transforms.append({
        'name': f'{alpha_id}_2C_ts_mean',
        'expr': f'ts_mean({base_expr}, 22)',
        'decay': 0,
        'neutralization': 'INDUSTRY',
        'stage': '2阶C'
    })

    # 2阶D: zscore标准化
    transforms.append({
        'name': f'{alpha_id}_2D_zscore',
        'expr': f'zscore({base_expr})',
        'decay': 0,
        'neutralization': 'INDUSTRY',
        'stage': '2阶D'
    })

    # 2阶E: group_zscore
    transforms.append({
        'name': f'{alpha_id}_2E_group_zscore',
        'expr': f'group_zscore({base_expr}, industry)',
        'decay': 0,
        'neutralization': 'INDUSTRY',
        'stage': '2阶E'
    })

    return transforms


def apply_3rd_order_transforms(base_expr, alpha_id):
    """应用3阶变换: trade_when, decay等"""
    transforms = []

    # 3阶A: trade_when + 量价背离
    transforms.append({
        'name': f'{alpha_id}_3A_trade_when_corr',
        'expr': f'trade_when(ts_corr(close, volume, 20) < 0, rank({base_expr}), -1)',
        'decay': 6,
        'neutralization': 'INDUSTRY',
        'stage': '3阶A'
    })

    # 3阶B: trade_when + 成交量放大
    transforms.append({
        'name': f'{alpha_id}_3B_trade_when_vol',
        'expr': f'trade_when(ts_mean(volume, 10) > ts_mean(volume, 60), rank({base_expr}), -1)',
        'decay': 8,
        'neutralization': 'INDUSTRY',
        'stage': '3阶B'
    })

    # 3阶C: decay alone (降低TVR)
    transforms.append({
        'name': f'{alpha_id}_3C_decay8',
        'expr': f'rank({base_expr})',
        'decay': 8,
        'neutralization': 'INDUSTRY',
        'stage': '3阶C'
    })

    # 3阶D: group_rank + decay
    transforms.append({
        'name': f'{alpha_id}_3D_group_rank_decay',
        'expr': f'group_rank(rank({base_expr}), subindustry)',
        'decay': 6,
        'neutralization': 'SUBINDUSTRY',
        'stage': '3阶D'
    })

    # 3阶E: ts_zscore + decay
    transforms.append({
        'name': f'{alpha_id}_3E_ts_zscore_decay',
        'expr': f'ts_zscore({base_expr}, 20)',
        'decay': 6,
        'neutralization': 'INDUSTRY',
        'stage': '3阶E'
    })

    # 3阶F: sector异动触发
    transforms.append({
        'name': f'{alpha_id}_3F_sector_outperform',
        'expr': f'trade_when(group_rank(ts_std_dev(returns, 60), sector) > 0.7, rank({base_expr}), -1)',
        'decay': 8,
        'neutralization': 'SECTOR',
        'stage': '3阶F'
    })

    return transforms


# ============================================================
# 主流程
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Alpha 2阶/3阶优化')
    parser.add_argument('--priority', type=int, default=1, choices=[1, 2, 3],
                      help='1=高Fitness候选, 2=用户优先, 3=ts_rank系列')
    parser.add_argument('--alpha-id', type=str, default=None,
                      help='指定单个alpha ID进行优化')
    parser.add_argument('--max-variants', type=int, default=12,
                      help='每个alpha最大变体数量')
    parser.add_argument('--decay-only', action='store_true',
                      help='只测试decay变化')
    parser.add_argument('--json-file', type=str, default=None,
                      help='从本地JSON加载候选 (格式: may19-promising-alphas.json)')
    parser.add_argument('--min-sharpe', type=float, default=1.5,
                      help='最小Sharpe阈值 (默认1.5)')
    parser.add_argument('--min-fitness', type=float, default=1.0,
                      help='最小Fitness阈值 (默认1.0)')
    args = parser.parse_args()

    # 初始化session
    sess = requests.Session()
    sess.auth = CREDENTIALS
    r = sess.post('https://api.worldquantbrain.com/authentication')
    print(f'Auth: {r.status_code}', flush=True)

    # 从JSON加载候选
    if args.json_file:
        json_path = Path(args.json_file)
        if not json_path.exists():
            json_path = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures') / args.json_file
        with open(json_path) as f:
            jdata = json.load(f)
        candidates = []
        for a in jdata.get('alphas', []):
            if (a.get('sharpe', 0) >= args.min_sharpe
                and a.get('fitness', 0) >= args.min_fitness
                and a.get('checks', {}).get('CONCENTRATED_WEIGHT') == 'PASS'):
                candidates.append({
                    'id': a['alphaId'],
                    'orig_s': a['sharpe'],
                    'orig_f': a['fitness'],
                    'tvr': a['turnover'],
                    'note': a['expression'][:60]
                })
        candidates.sort(key=lambda x: x['orig_f'], reverse=True)
        print(f'\n从JSON加载: {len(candidates)} 候选 (S>={args.min_sharpe}, F>={args.min_fitness})')
    elif args.alpha_id:
        candidates = [{'id': args.alpha_id, 'orig_s': 0, 'orig_f': 0, 'tvr': 0, 'note': '指定'}]
    elif args.priority == 1:
        candidates = HIGH_FITNESS_CANDIDATES
    elif args.priority == 2:
        candidates = USER_PRIORITY_CANDIDATES
    else:
        candidates = TS_RANK_CANDIDATES

    print(f'\n=== Alpha {args.priority}阶优化 ===')
    print(f'候选数量: {len(candidates)}')

    all_results = {}

    for cand in candidates:
        alpha_id = cand['id']
        print(f'\n=== 处理 {alpha_id} (Orig S={cand["orig_s"]}, F={cand["orig_f"]}) ===')

        # 获取原始表达式
        base_expr = get_alpha_expression(sess, alpha_id)
        if not base_expr:
            print(f'  获取表达式失败, 跳过')
            continue
        print(f'  原始: {base_expr[:80]}...')

        results = []

        if args.decay_only:
            # 只测试decay变化
            for decay in [0, 4, 6, 8, 10, 12]:
                name = f'{alpha_id}_decay{decay}'
                print(f'  -> {name}', end=' ', flush=True)
                r = inline_simulate(sess, base_expr, name=name, decay=decay)
                if r.get('alpha_id'):
                    print(f'S={r["sharpe"]:.2f}, F={r["fitness"]:.2f}, TVR={r["turnover"]:.4f}')
                else:
                    print(f'{r["status"]}')
                results.append(r)
                time.sleep(3)
        else:
            # 生成变体
            variants_2nd = apply_2nd_order_transforms(base_expr, alpha_id)
            variants_3rd = apply_3rd_order_transforms(base_expr, alpha_id)

            all_variants = variants_2nd + variants_3rd

            # 限制数量
            if args.max_variants > 0:
                all_variants = all_variants[:args.max_variants]

            print(f'  生成 {len(all_variants)} 个变体')

            for v in all_variants:
                name = v['name']
                print(f'  -> {name}', end=' ', flush=True)
                r = inline_simulate(
                    sess, v['expr'], name=name,
                    decay=v['decay'], neutralization=v['neutralization']
                )
                if r.get('alpha_id'):
                    print(f'S={r["sharpe"]:.2f}, F={r["fitness"]:.2f}, TVR={r["turnover"]:.4f}')
                else:
                    print(f'{r["status"]}')
                results.append(r)
                time.sleep(3)  # API限流保护

        # 保存结果
        all_results[alpha_id] = {
            'original': cand,
            'base_expression': base_expr,
            'results': results,
        }

        # 找出通过
        passing = [r for r in results if r.get('sharpe') and r['sharpe'] >= 1.25 and r.get('fitness', 0) >= 1.0]
        if passing:
            print(f'  ** PASSING: {len(passing)}/{len(results)}')
            for p in passing:
                print(f'     {p["name"]}: S={p["sharpe"]:.2f}, F={p["fitness"]:.2f}, TVR={p["turnover"]:.4f}, dec={p["decay"]}')

    # 保存全部结果
    output_file = OUTPUT_DIR / f'optimization_p{args.priority}_{time.strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f'\n结果已保存: {output_file}')

    # 汇总
    print('\n=== 汇总 ===')
    for aid, data in all_results.items():
        results = data['results']
        passing = [r for r in results if r.get('sharpe') and r['sharpe'] >= 1.25 and r.get('fitness', 0) >= 1.0]
        print(f'{aid}: {len(passing)} passing / {len(results)} tested')

if __name__ == '__main__':
    main()
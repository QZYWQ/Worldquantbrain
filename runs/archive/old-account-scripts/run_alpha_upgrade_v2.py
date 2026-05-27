#!/usr/bin/env python3
"""
Alpha 2阶/3阶 Optimization Pipeline v2
改进版: 每个alpha处理后立即保存结果
"""

import sys
import json
import time
import requests
from pathlib import Path

CREDENTIALS = ('zpdedn@gmail.com', 'zp82648185000')
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
BATCH_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches')
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')


def get_alpha_expression(sess, alpha_id):
    r = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get('regular', {}).get('code')


def inline_simulate(sess, expr, name=None, decay=0, neutralization='INDUSTRY'):
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
        return {'alpha_id': None, 'name': name, 'status': f'POST_FAIL_{r.status_code}', 'expression': expr, 'decay': decay, 'neutralization': neutralization}
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
            return {'alpha_id': None, 'name': name, 'status': 'ERROR', 'expression': expr, 'decay': decay, 'neutralization': neutralization}
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr, 'decay': decay, 'neutralization': neutralization}


def apply_2nd_order_transforms(base_expr, alpha_id):
    transforms = []
    transforms.append({'name': f'{alpha_id}_2A_rank', 'expr': f'rank({base_expr})', 'decay': 0, 'neutralization': 'INDUSTRY', 'stage': '2阶A'})
    transforms.append({'name': f'{alpha_id}_2B_group_rank', 'expr': f'group_rank(rank({base_expr}), subindustry)', 'decay': 0, 'neutralization': 'SUBINDUSTRY', 'stage': '2阶B'})
    transforms.append({'name': f'{alpha_id}_2C_ts_mean', 'expr': f'ts_mean({base_expr}, 22)', 'decay': 0, 'neutralization': 'INDUSTRY', 'stage': '2阶C'})
    transforms.append({'name': f'{alpha_id}_2D_zscore', 'expr': f'zscore({base_expr})', 'decay': 0, 'neutralization': 'INDUSTRY', 'stage': '2阶D'})
    transforms.append({'name': f'{alpha_id}_2E_group_zscore', 'expr': f'group_zscore({base_expr}, industry)', 'decay': 0, 'neutralization': 'INDUSTRY', 'stage': '2阶E'})
    return transforms


def apply_3rd_order_transforms(base_expr, alpha_id):
    transforms = []
    transforms.append({'name': f'{alpha_id}_3A_trade_when_corr', 'expr': f'trade_when(ts_corr(close, volume, 20) < 0, rank({base_expr}), -1)', 'decay': 6, 'neutralization': 'INDUSTRY', 'stage': '3阶A'})
    transforms.append({'name': f'{alpha_id}_3B_trade_when_vol', 'expr': f'trade_when(ts_mean(volume, 10) > ts_mean(volume, 60), rank({base_expr}), -1)', 'decay': 8, 'neutralization': 'INDUSTRY', 'stage': '3阶B'})
    transforms.append({'name': f'{alpha_id}_3C_decay8', 'expr': f'rank({base_expr})', 'decay': 8, 'neutralization': 'INDUSTRY', 'stage': '3阶C'})
    transforms.append({'name': f'{alpha_id}_3D_group_rank_decay', 'expr': f'group_rank(rank({base_expr}), subindustry)', 'decay': 6, 'neutralization': 'SUBINDUSTRY', 'stage': '3阶D'})
    transforms.append({'name': f'{alpha_id}_3E_ts_zscore_decay', 'expr': f'ts_zscore({base_expr}, 20)', 'decay': 6, 'neutralization': 'INDUSTRY', 'stage': '3阶E'})
    transforms.append({'name': f'{alpha_id}_3F_sector_outperform', 'expr': f'trade_when(group_rank(ts_std_dev(returns, 60), sector) > 0.7, rank({base_expr}), -1)', 'decay': 8, 'neutralization': 'SECTOR', 'stage': '3阶F'})
    return transforms


def save_intermediate_results(results_dict, output_path):
    """保存中间结果"""
    with open(output_path, 'w') as f:
        json.dump(results_dict, f, indent=2, default=str)
    print(f'  [已保存] {output_path}')


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Alpha 2阶/3阶优化 v2')
    parser.add_argument('--priority', type=int, default=1, choices=[1, 2, 3], help='1=高Fitness, 2=用户优先, 3=ts_rank')
    parser.add_argument('--alpha-id', type=str, default=None, help='指定alpha ID')
    parser.add_argument('--max-variants', type=int, default=12, help='每个alpha最大变体')
    parser.add_argument('--resume', action='store_true', help='从之前的输出恢复')
    args = parser.parse_args()

    sess = requests.Session()
    sess.auth = CREDENTIALS
    r = sess.post('https://api.worldquantbrain.com/authentication')
    print(f'Auth: {r.status_code}', flush=True)

    # 候选列表定义
    HIGH_FITNESS = [
        {'id': '6XRqZ02Y', 'orig_s': 1.11, 'orig_f': 1.82}, {'id': 'MPblNjqM', 'orig_s': 1.02, 'orig_f': 1.56},
        {'id': 'qMnArZeZ', 'orig_s': 1.33, 'orig_f': 1.35}, {'id': 'wp5VVGRY', 'orig_s': 0.96, 'orig_f': 1.80},
    ]
    USER_PRIORITY = [
        {'id': 'blNRGAJl', 'orig_s': 1.14, 'orig_f': 1.26}, {'id': 'WjN75gAO', 'orig_s': 0.84, 'orig_f': 0.99},
        {'id': 'RRNaRYm1', 'orig_s': 1.00, 'orig_f': 0.90}, {'id': '9q9VLAm1', 'orig_s': 1.00, 'orig_f': 0.90},
        {'id': '1Yow6066', 'orig_s': 0.77, 'orig_f': 0.93}, {'id': 'Xgk7Qz6X', 'orig_s': 1.03, 'orig_f': 0.64},
        {'id': '78xjEAML', 'orig_s': 1.03, 'orig_f': 0.64}, {'id': 'e7ngp37l', 'orig_s': 0.89, 'orig_f': 0.67},
        {'id': 'P0n7xG3q', 'orig_s': 0.83, 'orig_f': 0.65}, {'id': 'vR5jdo7A', 'orig_s': 0.72, 'orig_f': 0.69},
    ]
    TS_RANK = [
        {'id': 'rKboMqz3', 'orig_s': 0.77, 'orig_f': 1.31}, {'id': 'j2nQQbRk', 'orig_s': 0.77, 'orig_f': 1.31},
        {'id': 'O0npXMlq', 'orig_s': 0.76, 'orig_f': 1.29}, {'id': '9q9QQ6vV', 'orig_s': 0.76, 'orig_f': 1.29},
    ]

    if args.alpha_id:
        candidates = [{'id': args.alpha_id, 'orig_s': 0, 'orig_f': 0}]
    elif args.priority == 1:
        candidates = HIGH_FITNESS
    elif args.priority == 2:
        candidates = USER_PRIORITY
    else:
        candidates = TS_RANK

    output_file = OUTPUT_DIR / f'optimization_p{args.priority}_{time.strftime("%Y%m%d_%H%M%S")}.json'

    # 恢复之前的结果
    all_results = {}
    if args.resume and output_file.exists():
        with open(output_file) as f:
            all_results = json.load(f)
        print(f'恢复 {len(all_results)} 个alpha的之前结果')

    print(f'\n=== Alpha {args.priority}阶优化 ===')
    print(f'候选数量: {len(candidates)}')

    for cand in candidates:
        alpha_id = cand['id']
        if alpha_id in all_results and all_results[alpha_id].get('results'):
            print(f'\n=== 跳过已完成的 {alpha_id} ===')
            continue

        print(f'\n=== 处理 {alpha_id} (Orig S={cand["orig_s"]}, F={cand["orig_f"]}) ===', flush=True)

        base_expr = get_alpha_expression(sess, alpha_id)
        if not base_expr:
            print(f'  获取表达式失败, 跳过')
            continue
        print(f'  原始: {base_expr[:80]}...', flush=True)

        results = []

        variants_2nd = apply_2nd_order_transforms(base_expr, alpha_id)
        variants_3rd = apply_3rd_order_transforms(base_expr, alpha_id)
        all_variants = (variants_2nd + variants_3rd)[:args.max_variants]

        print(f'  生成 {len(all_variants)} 个变体', flush=True)

        for v in all_variants:
            print(f'  -> {v["name"]}', end=' ', flush=True)
            r = inline_simulate(sess, v['expr'], name=v['name'], decay=v['decay'], neutralization=v['neutralization'])
            if r.get('alpha_id'):
                print(f'S={r["sharpe"]:.2f}, F={r["fitness"]:.2f}, TVR={r["turnover"]:.4f}', flush=True)
            else:
                print(f'{r["status"]}', flush=True)
            results.append(r)
            time.sleep(3)

        all_results[alpha_id] = {
            'original': cand,
            'base_expression': base_expr,
            'results': results,
        }

        # 每个alpha处理完立即保存
        save_intermediate_results(all_results, output_file)

        passing = [r for r in results if r.get('sharpe') and r['sharpe'] >= 1.25 and r.get('fitness', 0) >= 1.0]
        if passing:
            print(f'  ** PASSING: {len(passing)}/{len(results)}')
            for p in passing:
                print(f'     {p["name"]}: S={p["sharpe"]:.2f}, F={p["fitness"]:.2f}, TVR={p["turnover"]:.4f}')

    # 最终保存
    save_intermediate_results(all_results, output_file)

    print('\n=== 汇总 ===')
    total_passing = 0
    for aid, data in all_results.items():
        results = data['results']
        passing = [r for r in results if r.get('sharpe') and r['sharpe'] >= 1.25 and r.get('fitness', 0) >= 1.0]
        print(f'{aid}: {len(passing)} passing / {len(results)} tested')
        total_passing += len(passing)
    print(f'\n总计通过: {total_passing}')
    print(f'输出文件: {output_file}')

if __name__ == '__main__':
    main()
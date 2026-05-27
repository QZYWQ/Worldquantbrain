#!/usr/bin/env python3
"""
may19-promising alphas 批量升阶
对从JSON加载的候选进行SO+TH升阶, 每个候选取最佳变体

Usage:
    python3 run_may19_upgrade_v2.py --limit 20 --max-variants 6
"""
import sys, json, time, random
from pathlib import Path
import requests

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')

CREDENTIALS = ('zpdedn@gmail.com', 'zp82648185000')

def get_alpha_expression(sess, alpha_id):
    r = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
    if r.status_code != 200:
        return None
    return r.json().get('regular', {}).get('code')

def inline_simulate(sess, expr, name, decay=0, neutralization='SUBINDUSTRY'):
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
        return {'alpha_id': None, 'name': name, 'status': f'POST_FAIL_{r.status_code}', 'expression': expr}
    url = r.headers['Location']
    result = None
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
                'decay': decay, 'neutralization': neutralization
            }
        elif status == 'ERROR':
            return {'alpha_id': None, 'name': name, 'status': 'ERROR', 'expression': expr}
        elif status in ('COMPLETE', 'WARNING') and not alpha_id:
            # API returned completion but no alpha_id - return the status
            return {'alpha_id': None, 'name': name, 'status': status, 'expression': expr}
        time.sleep(5)
    return {'alpha_id': None, 'name': name, 'status': 'TIMEOUT', 'expression': expr}

def build_so_variants(base_expr, parent_id):
    """为base expression构建SO变体"""
    variants = []

    # SO1: rank包装 (降TVR)
    for decay in [0, 6]:
        variants.append({
            'name': f'{parent_id}_so_rank_d{decay}',
            'expr': f'rank({base_expr})',
            'decay': decay, 'neut': 'SUBINDUSTRY', 'method': 'rank_wrapper'
        })

    # SO2: zscore包装
    for decay in [0, 6]:
        variants.append({
            'name': f'{parent_id}_so_zscore_d{decay}',
            'expr': f'zscore({base_expr})',
            'decay': decay, 'neut': 'SUBINDUSTRY', 'method': 'zscore_wrapper'
        })

    # SO3: group_rank封装
    for decay in [0, 6]:
        variants.append({
            'name': f'{parent_id}_so_grp_rank_d{decay}',
            'expr': f'group_rank({base_expr}, subindustry)',
            'decay': decay, 'neut': 'INDUSTRY', 'method': 'group_rank'
        })

    # SO4: group_zscore封装
    for decay in [0, 6]:
        variants.append({
            'name': f'{parent_id}_so_grp_zscore_d{decay}',
            'expr': f'group_zscore({base_expr}, subindustry)',
            'decay': decay, 'neut': 'INDUSTRY', 'method': 'group_zscore'
        })

    # SO5: decay线性增强
    for decay in [8, 15]:
        variants.append({
            'name': f'{parent_id}_so_decay_d{decay}',
            'expr': base_expr,
            'decay': decay, 'neut': 'SUBINDUSTRY', 'method': f'decay_{decay}'
        })

    return variants

def build_aggressive_variants(base_expr, parent_id):
    """
    激进变体 - 专门设计来降低自相关
    策略:
    1. sign flip (反转信号)
    2. 替换核心field (returns->vwap/close)
    3. 不同neutralization group
    4. inverse代替rank
    5. ts_delta on signal (检测变化而非水平)
    6. 完全不同的decay窗口
    """
    variants = []

    # A1: Sign flip
    variants.append({
        'name': f'{parent_id}_ag_flip',
        'expr': f'-({base_expr})',
        'decay': 0, 'neut': 'SUBINDUSTRY', 'method': 'sign_flip'
    })

    # A2: Double sign flip (undoes sign flip but changes structure)
    variants.append({
        'name': f'{parent_id}_ag_flip_rank',
        'expr': f'rank(-({base_expr}))',
        'decay': 0, 'neut': 'SUBINDUSTRY', 'method': 'sign_flip_rank'
    })

    # A3: Replace returns with vwap-based signal
    # 找到returns相关的部分并替换
    expr_vwap = base_expr.replace('returns', 'close/vwap')
    if expr_vwap != base_expr:
        variants.append({
            'name': f'{parent_id}_ag_vwap',
            'expr': expr_vwap,
            'decay': 0, 'neut': 'SUBINDUSTRY', 'method': 'vwap_signal'
        })

    # A4: Different decay window (激进而非渐变)
    for new_decay in [20, 30]:
        variants.append({
            'name': f'{parent_id}_ag_decay{new_decay}',
            'expr': base_expr,
            'decay': new_decay, 'neut': 'SUBINDUSTRY', 'method': f'decay_{new_decay}'
        })

    # A5: Different neutralization group
    for grp in ['sector', 'industry', 'bucket(rank(cap), range=\'0.1, 1, 0.1\')']:
        variants.append({
            'name': f'{parent_id}_ag_neut_{grp[:10]}',
            'expr': f'group_neutralize({base_expr}, densify({grp}))',
            'decay': 0, 'neut': 'INDUSTRY', 'method': f'neut_{grp[:8]}'
        })

    # A6: ts_delta on the signal (检测变化而非水平)
    variants.append({
        'name': f'{parent_id}_ag_delta',
        'expr': f'ts_delta({base_expr}, 5)',
        'decay': 0, 'neut': 'SUBINDUSTRY', 'method': 'ts_delta'
    })

    # A7: inverse instead of rank
    variants.append({
        'name': f'{parent_id}_ag_inverse',
        'expr': f'inverse({base_expr})',
        'decay': 0, 'neut': 'SUBINDUSTRY', 'method': 'inverse'
    })

    # A8: quantile on raw signal
    variants.append({
        'name': f'{parent_id}_ag_quantile',
        'expr': f'quantile({base_expr}, 0.5)',
        'decay': 0, 'neut': 'SUBINDUSTRY', 'method': 'quantile_mid'
    })

    # A9: ts_zscore with different window
    variants.append({
        'name': f'{parent_id}_ag_ts_zscore',
        'expr': f'ts_zscore({base_expr}, 10)',
        'decay': 0, 'neut': 'SUBINDUSTRY', 'method': 'ts_zscore_win10'
    })

    # A10: cross-sectional zscore instead of time-series
    variants.append({
        'name': f'{parent_id}_ag_cs_zscore',
        'expr': f'zscore({base_expr})',
        'decay': 0, 'neut': 'SECTOR', 'method': 'cs_zscore_sector'
    })

    return variants

def build_th_variants(base_expr, parent_id, decay=0):
    """为base expression构建TH变体"""
    variants = []

    # TH1: rank + rank 双包装
    variants.append({
        'name': f'{parent_id}_th_rank_rank',
        'expr': f'rank(rank({base_expr}))',
        'decay': decay, 'neut': 'SUBINDUSTRY', 'method': 'rank_rank'
    })

    # TH2: rank + zscore
    variants.append({
        'name': f'{parent_id}_th_rank_zscore',
        'expr': f'rank(zscore({base_expr}))',
        'decay': decay, 'neut': 'SUBINDUSTRY', 'method': 'rank_zscore'
    })

    # TH3: trade_when sentiment触发
    variants.append({
        'name': f'{parent_id}_th_tw_sentiment',
        'expr': f'trade_when(ts_rank(scl12_sentiment_fast_d1, 20) > 0.6, {base_expr}, -1)',
        'decay': decay, 'neut': 'SUBINDUSTRY', 'method': 'trade_when_sentiment'
    })

    # TH4: trade_when 量异动触发
    variants.append({
        'name': f'{parent_id}_th_tw_volume',
        'expr': f'trade_when(rank(volume / ts_mean(volume, 20)) > 0.6, {base_expr}, -1)',
        'decay': decay, 'neut': 'SUBINDUSTRY', 'method': 'trade_when_volume'
    })

    # TH5: quantile 0.2降极端
    variants.append({
        'name': f'{parent_id}_th_quantile_low',
        'expr': f'quantile({base_expr}, 0.2)',
        'decay': decay, 'neut': 'SUBINDUSTRY', 'method': 'quantile_low'
    })

    # TH6: quantile 0.8
    variants.append({
        'name': f'{parent_id}_th_quantile_high',
        'expr': f'quantile({base_expr}, 0.8)',
        'decay': decay, 'neut': 'SUBINDUSTRY', 'method': 'quantile_high'
    })

    return variants

def main():
    import argparse
    parser = argparse.ArgumentParser(description='may19 alphas 批量升阶')
    parser.add_argument('--json-file', type=str, default='may19-promising-alphas.json')
    parser.add_argument('--limit', type=int, default=20, help='处理候选数量')
    parser.add_argument('--max-variants', type=int, default=6, help='每个候选最大变体')
    parser.add_argument('--pass-threshold', type=float, default=1.5, help='Sharpe通过阈值')
    args = parser.parse_args()

    # 初始化session
    sess = requests.Session()
    sess.auth = CREDENTIALS
    r = sess.post('https://api.worldquantbrain.com/authentication')
    print(f'Auth: {r.status_code}', flush=True)

    # 加载候选
    json_path = OUTPUT_DIR / args.json_file
    with open(json_path) as f:
        jdata = json.load(f)

    candidates = []
    for a in jdata.get('alphas', []):
        if (a.get('sharpe', 0) >= 1.5
            and a.get('fitness', 0) >= 1.0
            and a.get('checks', {}).get('CONCENTRATED_WEIGHT') == 'PASS'):
            candidates.append({
                'id': a['alphaId'],
                'orig_s': a['sharpe'],
                'orig_f': a['fitness'],
                'tvr': a['turnover'],
                'expr': a['expression']
            })
    candidates.sort(key=lambda x: x['orig_f'], reverse=True)
    candidates = candidates[:args.limit]
    print(f'\n加载 {len(candidates)} 候选 (S>=1.5, F>=1.0, CW=PASS)', flush=True)

    all_results = []
    all_passing = []

    for cand in candidates:
        aid = cand['id']
        base_expr = cand['expr']
        print(f'\n=== {aid} (S={cand["orig_s"]:.2f}, F={cand["orig_f"]:.2f}) ===', flush=True)

        # 构建SO变体
        so_variants = build_so_variants(base_expr, aid)[:args.max_variants]
        print(f'  SO变体: {len(so_variants)}', flush=True)

        so_results = []
        for v in so_variants:
            print(f'  -> {v["name"]}', end=' ', flush=True)
            r = inline_simulate(sess, v['expr'], v['name'], v['decay'], v['neut'])
            if r.get('alpha_id'):
                print(f'S={r["sharpe"]:.3f} F={r["fitness"]:.3f} TVR={r["turnover"]:.3f}', flush=True)
            else:
                print(f'{r["status"]}', flush=True)
            r['parent'] = aid
            r['method'] = v['method']
            so_results.append(r)
            all_results.append(r)
            time.sleep(3)

        # 激进变体测试
        print(f'  激进变体:', flush=True)
        ag_variants = build_aggressive_variants(base_expr, aid)
        for v in ag_variants[:8]:
            print(f'  -> {v["name"]}', end=' ', flush=True)
            r = inline_simulate(sess, v['expr'], v['name'], v['decay'], v['neut'])
            if r.get('alpha_id'):
                print(f'S={r["sharpe"]:.3f} F={r["fitness"]:.3f} TVR={r["turnover"]:.3f}', flush=True)
            else:
                print(f'{r["status"]}', flush=True)
            r['parent'] = aid
            r['method'] = v['method']
            all_results.append(r)
            if r.get('sharpe') and r['sharpe'] >= args.pass_threshold:
                all_passing.append(r)
            time.sleep(3)

        # 找最佳SO
        so_passing = [r for r in so_results if r.get('sharpe') and r['sharpe'] >= args.pass_threshold]
        so_passing.sort(key=lambda x: x['sharpe'], reverse=True)

        # 对最佳SO做TH
        if so_passing:
            best_so = so_passing[0]
            print(f'  Best SO: S={best_so["sharpe"]:.3f} {best_so["method"]}', flush=True)
            th_variants = build_th_variants(best_so['expression'], aid, best_so.get('decay', 0))[:args.max_variants]
            print(f'  TH变体: {len(th_variants)}', flush=True)

            for v in th_variants:
                print(f'  -> {v["name"]}', end=' ', flush=True)
                r = inline_simulate(sess, v['expr'], v['name'], v['decay'], v['neut'])
                if r.get('alpha_id'):
                    print(f'S={r["sharpe"]:.3f} F={r["fitness"]:.3f} TVR={r["turnover"]:.3f}', flush=True)
                else:
                    print(f'{r["status"]}', flush=True)
                r['parent'] = aid
                r['method'] = v['method']
                all_results.append(r)
                if r.get('sharpe') and r['sharpe'] >= args.pass_threshold:
                    all_passing.append(r)
                time.sleep(3)

            # 其他通过的SO也做TH
            for so in so_passing[1:3]:
                th_variants = build_th_variants(so['expression'], aid, so.get('decay', 0))[:4]
                for v in th_variants[:2]:
                    print(f'  -> {v["name"]}', end=' ', flush=True)
                    r = inline_simulate(sess, v['expr'], v['name'], v['decay'], v['neut'])
                    if r.get('alpha_id'):
                        print(f'S={r["sharpe"]:.3f} F={r["fitness"]:.3f} TVR={r["turnover"]:.3f}', flush=True)
                    else:
                        print(f'{r["status"]}', flush=True)
                    r['parent'] = aid
                    r['method'] = v['method']
                    all_results.append(r)
                    if r.get('sharpe') and r['sharpe'] >= args.pass_threshold:
                        all_passing.append(r)
                    time.sleep(3)

        # 中间保存
        with open(OUTPUT_DIR / f'may19_upgrade_results.json', 'w') as f:
            json.dump({
                'all_results': all_results,
                'all_passing': [{'sharpe': r['sharpe'], 'fitness': r['fitness'],
                                 'turnover': r['turnover'], 'method': r['method'],
                                 'expr': r['expression'][:80]} for r in all_passing]
            }, f, indent=2, default=str)

    # 最终汇总
    print(f'\n{"="*60}', flush=True)
    print(f'升阶完成: 测试 {len(all_results)} 变体, 通过 {len(all_passing)} (S>={args.pass_threshold})', flush=True)

    all_passing.sort(key=lambda x: x['sharpe'], reverse=True)
    print(f'\nTop Passing:', flush=True)
    for r in all_passing[:15]:
        print(f"  S={r['sharpe']:.2f} F={r.get('fitness',0):.2f} {r['method']} | {r['expression'][:70]}", flush=True)

    # 提交检查
    if all_passing:
        from machine_lib import check_submission, view_alphas
        stone_bag = [r['alpha_id'] for r in all_passing[:20] if r.get('alpha_id')]
        gold_bag = []
        if stone_bag:
            print(f'\n检查 {len(stone_bag)} 个候选...', flush=True)
            gold_bag = check_submission(stone_bag, gold_bag, 0)
            print(f'通过检查: {len(gold_bag)}', flush=True)
            if gold_bag:
                print('\n可提交Alpha:', flush=True)
                view_alphas(gold_bag)

    with open(OUTPUT_DIR / 'may19_upgrade_final.json', 'w') as f:
        json.dump({
            'total_tested': len(all_results),
            'total_passing': len(all_passing),
            'candidates_processed': args.limit,
            'passing': [{'sharpe': r['sharpe'], 'fitness': r.get('fitness'), 'turnover': r.get('turnover'),
                         'method': r['method'], 'alpha_id': r.get('alpha_id'),
                         'expr': r['expression'][:100]} for r in all_passing]
        }, f, indent=2, default=str)

    print('\n完成!', flush=True)

if __name__ == '__main__':
    main()
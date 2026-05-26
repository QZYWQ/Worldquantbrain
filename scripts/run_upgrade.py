#!/usr/bin/env python3
"""
升阶管道 — 对7-pass候选执行SO/TH升阶
策略: rank wrapper, market neut, densify cap, quantile trim, decay调整
"""
import sys, json, time, os
from pathlib import Path
from datetime import datetime
import requests

CRED_PATH = Path('/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt')
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_creds = json.loads(CRED_PATH.read_text().strip())
CREDENTIALS = (_creds[0], _creds[1])

# 7-pass 候选 (需升阶)
TARGETS = [
    # operating_income 家族 (与已提交的0mzWQbPK同family)
    {'id': 'N1Aoapdo', 's': 1.76, 'f': 1.15, 'tvr': 0.0598, 'sc': 0.9872},
    {'id': 'MPkAX0LM', 's': 1.65, 'f': 1.18, 'tvr': 0.0398, 'sc': 0.9975},
    {'id': 'A1kdL3gX', 's': 1.61, 'f': 1.03, 'tvr': 0.0516, 'sc': 0.8732},
]

def login():
    s = requests.Session()
    s.auth = CREDENTIALS
    r = s.post('https://api.worldquantbrain.com/authentication')
    print(f'[AUTH] {r.status_code} {CREDENTIALS[0]}', flush=True)
    if r.status_code != 201: sys.exit(1)
    return s

def get_expr(sess, aid):
    r = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}')
    if r.status_code == 200:
        ad = r.json()
        return ad.get('regular', {}).get('code', '')
    return ''

def sim(sess, expr, name, decay=0, neut='SUBINDUSTRY'):
    """Simulate and return result"""
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': neut,
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    r = sess.post('https://api.worldquantbrain.com/simulations',
                  json={'type': 'REGULAR', 'settings': settings, 'regular': expr})
    if r.status_code != 201:
        return None
    url = r.headers['Location']
    for _ in range(120):
        prog = sess.get(url)
        h = prog.headers
        if h.get('Retry-After'):
            time.sleep(float(h['Retry-After']))
            continue
        result = prog.json()
        alpha_id = result.get('alpha')
        if result.get('status') in ('COMPLETE', 'WARNING') and alpha_id:
            ad = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}').json()
            is_m = ad.get('is', {})
            return {
                'alpha_id': alpha_id, 'name': name, 'expression': expr,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'decay': decay,
                'neutralization': neut
            }
        elif result.get('status') == 'ERROR':
            return None
        time.sleep(5)
    return None

def check(sess, aid, retries=10):
    """Check submission status with retry"""
    for _ in range(retries):
        rc = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}/check')
        ra = rc.headers.get('Retry-After')
        if ra:
            time.sleep(float(ra) + 1)
            continue
        try:
            cd = rc.json()
            checks = cd.get('is', {}).get('checks', [])
            if not checks:
                time.sleep(5)
                continue
            fails = [c['name'] for c in checks if c['result'] != 'PASS']
            sc = next((c.get('value') for c in checks if c['name']=='SELF_CORRELATION'), None)
            return fails, sc, checks
        except:
            time.sleep(5)
    return None, None, None

# ===== 升级策略 =====
def build_upgrades(base_expr, aid):
    """构建升阶变体"""
    variants = []

    # S1: rank wrapper (已验证最有效降SC)
    for decay in [0, 6, 15]:
        variants.append({
            'name': f'{aid}_s1_rank_d{decay}',
            'expr': f'rank({base_expr})',
            'decay': decay, 'neut': 'SUBINDUSTRY'
        })

    # S2: group_rank(market) — market中性化
    variants.append({
        'name': f'{aid}_s2_grp_market',
        'expr': f'group_rank({base_expr}, market)',
        'decay': 0, 'neut': 'MARKET'
    })

    # S3: zscore wrapper
    for decay in [0, 6]:
        variants.append({
            'name': f'{aid}_s3_zscore_d{decay}',
            'expr': f'zscore({base_expr})',
            'decay': decay, 'neut': 'SUBINDUSTRY'
        })

    # S4: quantile trim
    variants.append({
        'name': f'{aid}_s4_quantile',
        'expr': f'quantile({base_expr}, 0.1)',
        'decay': 0, 'neut': 'SUBINDUSTRY'
    })

    # S5: sign flip
    variants.append({
        'name': f'{aid}_s5_flip',
        'expr': f'-({base_expr})',
        'decay': 0, 'neut': 'SUBINDUSTRY'
    })

    # S6: group_neutralize + densify(bucket(rank(cap))) — gJmojOQm成功策略
    variants.append({
        'name': f'{aid}_s6_densify_cap',
        'expr': f'group_neutralize({base_expr}, densify(bucket(rank(cap), range=\'0.1, 1, 0.1\')))',
        'decay': 0, 'neut': 'SUBINDUSTRY'
    })

    # S7: ts_mean平滑
    variants.append({
        'name': f'{aid}_s7_tsmean',
        'expr': f'ts_mean({base_expr}, 22)',
        'decay': 0, 'neut': 'SUBINDUSTRY'
    })

    # S8: decay=30
    variants.append({
        'name': f'{aid}_s8_decay30',
        'expr': base_expr,
        'decay': 30, 'neut': 'SUBINDUSTRY'
    })

    return variants

def main():
    print('='*70, flush=True)
    print(f'升阶管道启动 [{datetime.now().isoformat()}]', flush=True)
    print('='*70, flush=True)

    sess = login()
    all_upgrade_results = []
    new_eight_pass = []

    for target in TARGETS:
        aid = target['id']
        print(f'\n=== {aid} (S={target["s"]:.2f}, F={target["f"]:.2f}, SC={target["sc"]}) ===', flush=True)

        # Get expression
        base_expr = get_expr(sess, aid)
        if not base_expr:
            print(f'  No expression found', flush=True)
            continue
        print(f'  base: {base_expr[:80]}...', flush=True)

        # Build variants
        variants = build_upgrades(base_expr, aid)
        print(f'  变体: {len(variants)}', flush=True)

        passed_any = False
        for v in variants:
            print(f'  -> {v["name"]}', end=' ', flush=True)
            r = sim(sess, v['expr'], v['name'], v['decay'], v['neut'])

            if r and r.get('sharpe') and r['sharpe'] >= 1.25 and r['fitness'] >= 0.8:
                print(f'S={r["sharpe"]:.3f} F={r["fitness"]:.3f} TVR={r["turnover"]:.4f}', end='', flush=True)

                # Check submission
                fails, sc_val, _ = check(sess, r['alpha_id'])
                if fails is not None:
                    r['sc'] = sc_val
                    r['parent'] = aid
                    r['check_fails'] = fails
                    all_upgrade_results.append(r)

                    if not fails and r['sharpe'] >= 1.5 and r['turnover'] < 0.6:
                        print(f' → ✓ 8-PASS! SC={sc_val}', end='', flush=True)
                        new_eight_pass.append(r)
                        passed_any = True
                    else:
                        print(f' → fails={fails} SC={sc_val}', end='', flush=True)
                else:
                    print(f' → CHECK_PENDING', end='', flush=True)
            else:
                sv = r.get('sharpe', 0) if r else 0
                s_str = f'{sv:.2f}' if r else 'FAIL'
                print(f' {s_str}', end='', flush=True)

            print(flush=True)
            time.sleep(4)  # Rate limit

        if not passed_any:
            print(f'  ✗ 无通过变体', flush=True)

    # Report
    print('\n' + '='*70, flush=True)
    print('升阶结果汇总', flush=True)
    print('='*70, flush=True)
    print(f'测试变体: {len(all_upgrade_results)}', flush=True)
    print(f'新8-pass: {len(new_eight_pass)}', flush=True)

    if new_eight_pass:
        print(f'\n新8-pass 候选:', flush=True)
        for c in new_eight_pass:
            print(f'  ✓ {c["alpha_id"]:12s} S={c["sharpe"]:.2f} F={c["fitness"]:.2f} '
                  f'TVR={c["turnover"]:.4f} SC={c.get("sc","?")} parent={c["parent"]}', flush=True)

    # Save
    report = {
        'timestamp': datetime.now().isoformat(),
        'targets': [t['id'] for t in TARGETS],
        'new_eight_pass': [{
            'alpha_id': c['alpha_id'], 'sharpe': c['sharpe'],
            'fitness': c['fitness'], 'turnover': c['turnover'],
            'selfcorr': c.get('sc'), 'parent': c['parent'],
            'expression': c['expression'][:120]
        } for c in new_eight_pass],
        'all_results': [{
            'name': r['name'], 'sharpe': r['sharpe'],
            'fitness': r['fitness'], 'turnover': r['turnover'],
            'sc': r.get('sc'), 'check_fails': r.get('check_fails'),
            'parent': r['parent']
        } for r in all_upgrade_results],
    }
    out_path = OUTPUT_DIR / f'upgrade-results-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'\n报告: {out_path}', flush=True)

if __name__ == '__main__':
    main()

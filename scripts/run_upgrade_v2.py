#!/usr/bin/env python3
"""
升阶v2 — 先模拟所有变体, 再批量检查SC
"""
import sys, json, time
from pathlib import Path
from datetime import datetime
import requests

CRED_PATH = Path('/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt')
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_creds = json.loads(CRED_PATH.read_text().strip())
CREDENTIALS = (_creds[0], _creds[1])

TARGETS = [
    {'id': 'N1Aoapdo', 's': 1.76, 'f': 1.15, 'tvr': 0.0598},
    {'id': 'MPkAX0LM', 's': 1.65, 'f': 1.18, 'tvr': 0.0398},
    {'id': 'A1kdL3gX', 's': 1.61, 'f': 1.03, 'tvr': 0.0516},
]

def login():
    s = requests.Session()
    s.auth = CREDENTIALS
    r = s.post('https://api.worldquantbrain.com/authentication')
    print(f'[AUTH] {r.status_code}', flush=True)
    return s

def get_expr(sess, aid):
    r = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}')
    return r.json().get('regular', {}).get('code', '') if r.status_code == 200 else ''

def simulate(sess, expr, name, decay=0, neut='SUBINDUSTRY'):
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': neut,
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    r = sess.post('https://api.worldquantbrain.com/simulations',
                  json={'type': 'REGULAR', 'settings': settings, 'regular': expr})
    if r.status_code != 201: return None
    url = r.headers['Location']
    for _ in range(120):
        prog = sess.get(url)
        if prog.headers.get('Retry-After'):
            time.sleep(float(prog.headers['Retry-After']))
            continue
        result = prog.json()
        alpha_id = result.get('alpha')
        if result.get('status') in ('COMPLETE', 'WARNING') and alpha_id:
            ad = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}').json()
            is_m = ad.get('is', {})
            return {
                'alpha_id': alpha_id, 'name': name,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'decay': decay,
                'neut': neut, 'expression': expr[:100],
            }
        elif result.get('status') == 'ERROR': return None
        time.sleep(5)
    return None

def sim_with_retry(sess, expr, name, decay=0, neut='SUBINDUSTRY', max_retry=3):
    for attempt in range(max_retry):
        r = simulate(sess, expr, name, decay, neut)
        if r: return r
        print(f'  retry {attempt+1}', flush=True)
        time.sleep(10)
    return None

# Phase 1: Simulate
def phase1(sess):
    print('Phase 1: 模拟所有升阶变体', flush=True)
    all_new = []

    for target in TARGETS:
        aid = target['id']
        base = get_expr(sess, aid)
        if not base:
            print(f'  {aid}: 无表达式', flush=True)
            continue
        print(f'\n{aid} base: {base[:60]}...', flush=True)

        variants = []
        # rank wrapper
        for d in [0, 6, 15]:
            variants.append((f'rank({base})', d, 'SUBINDUSTRY', f'rank_d{d}'))
        # market group_rank
        variants.append((f'group_rank({base}, market)', 0, 'MARKET', 'grp_market'))
        # zscore
        for d in [0, 6]:
            variants.append((f'zscore({base})', d, 'SUBINDUSTRY', f'zscore_d{d}'))
        # densify(cap)
        variants.append((f'group_neutralize({base}, densify(bucket(rank(cap), range=\"0.1, 1, 0.1\")))', 0, 'SUBINDUSTRY', 'densify_cap'))
        # sign flip
        variants.append((f'-({base})', 0, 'SUBINDUSTRY', 'flip'))
        # quantile
        variants.append((f'quantile({base}, 0.1)', 0, 'SUBINDUSTRY', 'quantile'))
        # ts_mean
        variants.append((f'ts_mean({base}, 22)', 0, 'SUBINDUSTRY', 'tsmean'))
        # decay 30
        variants.append((base, 30, 'SUBINDUSTRY', 'decay30'))

        for expr, decay, neut, tag in variants:
            name = f'{aid}_{tag}'
            print(f'  {name}...', end=' ', flush=True)
            r = sim_with_retry(sess, expr, name, decay, neut)
            if r:
                print(f'S={r["sharpe"]:.2f} F={r["fitness"]:.2f} TVR={r["turnover"]:.4f}', flush=True)
                r['parent'] = aid
                all_new.append(r)
            else:
                print('FAIL', flush=True)
            time.sleep(3)

    return all_new

# Phase 2: Check SC
def phase2(sess, all_new):
    print('\nPhase 2: 批量检查SC', flush=True)
    eight_pass = []
    seven_pass = []

    for i, r in enumerate(all_new):
        if r['sharpe'] < 1.25 or r['turnover'] > 0.6:
            continue

        aid = r['alpha_id']
        print(f'  [{i+1}/{len(all_new)}] {aid} S={r["sharpe"]:.2f}...', end=' ', flush=True)

        for retry in range(15):
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
                r['sc'] = sc
                r['fails'] = fails

                if not fails and r['sharpe'] >= 1.5 and r['turnover'] < 0.6:
                    print(f'✓ 8-PASS SC={sc}', flush=True)
                    eight_pass.append(r)
                else:
                    print(f'fail={fails} SC={sc}', flush=True)
                    seven_pass.append(r)
                break
            except:
                time.sleep(5)
        else:
            print('PENDING', flush=True)

    return eight_pass, seven_pass

def main():
    sess = login()
    all_new = phase1(sess)
    print(f'\n模拟完成: {len(all_new)} 变体', flush=True)

    save = {
        'phase1': [{'id': r['alpha_id'], 'name': r['name'], 's': r['sharpe'],
                     'f': r['fitness'], 'tvr': r['turnover'], 'parent': r['parent']}
                   for r in all_new],
    }
    with open(OUTPUT_DIR / 'upgrade_phase1.json', 'w') as f:
        json.dump(save, f, indent=2, default=str)

    print('\n等待60秒让SC计算...', flush=True)
    time.sleep(60)

    eight, seven = phase2(sess, all_new)
    print(f'\n8-pass: {len(eight)}, 7-pass: {len(seven)}')

    for r in eight:
        print(f'  ✓ {r["alpha_id"]:12s} S={r["sharpe"]:.2f} F={r["fitness"]:.2f} TVR={r["turnover"]:.4f} SC={r.get("sc")} parent={r["parent"]}')

    final = {
        'timestamp': datetime.now().isoformat(),
        'new_eight_pass': [{'id': r['alpha_id'], 's': r['sharpe'], 'f': r['fitness'],
                             'tvr': r['turnover'], 'sc': r.get('sc'), 'parent': r['parent'],
                             'name': r['name']} for r in eight],
        'still_seven': [{'id': r['alpha_id'], 's': r['sharpe'], 'f': r['fitness'],
                          'tvr': r['turnover'], 'sc': r.get('sc'), 'fails': r.get('fails')} for r in seven],
    }
    p = OUTPUT_DIR / f'upgrade_phase2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(p, 'w') as f:
        json.dump(final, f, indent=2, default=str)
    print(f'\n报告: {p}', flush=True)

if __name__ == '__main__':
    main()

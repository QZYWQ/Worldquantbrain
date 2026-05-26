#!/usr/bin/env python3
"""
新账户 Alpha Pipeline — discovery → check → rank → favorite
Usage: python3 discover_check_rank.py
"""
import sys, json, time, os
from pathlib import Path
from datetime import datetime
import requests
from collections import defaultdict


# === CONFIG ===
CRED_PATH = Path('/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt')
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_creds = json.loads(CRED_PATH.read_text().strip())
CREDENTIALS = (_creds[0], _creds[1])

# KILLED families from old account
KILLED_PATTERNS = [
    'ts_decay_linear', 'ts_corr(close,volume', 'ts_std_dev(returns',
    'volume/ts_mean(volume', 'ts_rank(earnings', 'growth_potential_rank_derivative'
]

ECON_KEYWORDS = {
    'operating_income': 1, 'assets_curr': 1, 'debt_carrying': 1,
    'revenue': 1, 'earnings': 1, 'eps': 1, 'anl4_': 1,
    'fnd6_': 1, 'income': 1, 'profit': 1, 'cashflow': 1,
    'close': 2, 'volume': 2, 'returns': 2, 'vwap': 2, 'high': 2, 'low': 2,
    'scl12': 3, 'sentiment': 3, 'buzz': 3,
    'mdl': 4, 'model': 4, 'unsystematic': 4,
}

def login():
    s = requests.Session()
    s.auth = CREDENTIALS
    r = s.post('https://api.worldquantbrain.com/authentication')
    print(f'[AUTH] {r.status_code} {CREDENTIALS[0]}', flush=True)
    if r.status_code != 201:
        print(f'  {r.text[:200]}', flush=True)
        sys.exit(1)
    return s

def get_expr(ad):
    reg = ad.get('regular', {})
    return reg.get('code', '') if isinstance(reg, dict) else ''

def ecom_type(expr):
    expr_l = expr.lower()
    for kw, pri in sorted(ECON_KEYWORDS.items(), key=lambda x: x[1]):
        if kw in expr_l:
            return kw.split('_')[0] if '_' in kw else kw, pri
    return 'price_volume', 3

def is_killed(expr):
    expr_s = expr.replace(' ', '')
    return any(p in expr_s for p in KILLED_PATTERNS)

def get_all_unsubmitted(sess):
    """Fetch ALL unsubmitted alphas from account"""
    all_a = []
    for offset in range(0, 2000, 100):
        url = (f'https://api.worldquantbrain.com/users/self/alphas?limit=100&offset={offset}'
               f'&status=UNSUBMITTED&hidden=false&type!=SUPER&order=-is.sharpe')
        r = sess.get(url)
        if r.status_code != 200:
            break
        data = r.json()
        items = data.get('results', [])
        all_a.extend(items)
        if len(items) < 100:
            break
        time.sleep(1)
    return all_a

def enrich_expressions(sess, alphas):
    """Fetch full alpha detail to get expression"""
    enriched = []
    for i, a in enumerate(alphas):
        aid = a['id']
        s_val = a['is']['sharpe']
        f_val = a['is']['fitness']
        t_val = a['is']['turnover']
        expr = ''
        reg = a.get('regular', {})
        if isinstance(reg, dict):
            expr = reg.get('code', '')
        if not expr:
            r = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}')
            if r.status_code == 200:
                expr = get_expr(r.json())
            time.sleep(0.5)

        enriched.append({
            'alpha_id': aid,
            'sharpe': s_val, 'fitness': f_val, 'turnover': t_val,
            'expression': expr,
            'decay': a.get('settings', {}).get('decay', 0),
            'neut': a.get('settings', {}).get('neutralization', ''),
        })

        if (i+1) % 50 == 0:
            print(f'  expressions: {i+1}/{len(alphas)}', flush=True)

    return enriched

def check_alpha(sess, aid):
    """Check submission status"""
    r = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}/check')
    if r.status_code != 200:
        return None, None, None
    try:
        data = r.json()
    except:
        return None, None, None
    is_data = data.get('is', {})
    checks = is_data.get('checks', [])
    if not checks:
        return None, None, None

    results = {c['name']: c['result'] for c in checks}
    sc_val = next((c.get('value') for c in checks if c['name'] == 'SELF_CORRELATION'), None)
    fails = [k for k, v in results.items() if v != 'PASS']
    return fails, sc_val, results

def simulate_upgrade(sess, expr, name, decay=0, neut='SUBINDUSTRY'):
    """Simulate a single alpha variant"""
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
        status = result.get('status')
        alpha_id = result.get('alpha')
        if status in ('COMPLETE', 'WARNING') and alpha_id:
            ad = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}').json()
            is_m = ad.get('is', {})
            return {
                'alpha_id': alpha_id, 'name': name, 'expression': expr,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'decay': decay,
                'neutralization': neut
            }
        elif status == 'ERROR':
            return None
        time.sleep(5)
    return None

def compute_score(alpha):
    """Composite score (lower = better): econ 30%, sc 20%, sharpe 20%, turnover 15%, fitness 15%"""
    expr = alpha.get('expression', '')
    s_val = alpha.get('sharpe', 0) or 0
    f_val = alpha.get('fitness', 0) or 0
    t_val = alpha.get('turnover', 1) or 1
    sc_val = alpha.get('selfcorr', 1) or 1

    _, econ_pri = ecom_type(expr)
    norm_econ = (econ_pri - 1) / 3  # 0=best(lowest), 1=worst
    norm_sc = min(sc_val / 0.7, 1.0) if isinstance(sc_val, (int, float)) else 0.5
    norm_sharpe = max(0, min(1, (1.5 - min(s_val, 3.0)) / 1.5))
    norm_fitness = max(0, min(1, (1.0 - min(f_val, 2.0)) / 1.0))
    norm_turnover = max(0, min(1, t_val / 0.6))

    killed_penalty = 1.0 if is_killed(expr) else 0.0

    return (norm_econ * 0.25 + norm_sc * 0.20 + norm_sharpe * 0.20 +
            norm_fitness * 0.15 + norm_turnover * 0.10 + killed_penalty * 0.10)

# ===== MAIN =====
def main():
    print('='*70, flush=True)
    print(f'新账户 Alpha Pipeline [{datetime.now().isoformat()}]', flush=True)
    print('='*70, flush=True)

    sess = login()

    # STEP 1: Fetch all unsubmitted
    print('\n=== Step 1: 获取所有Unsubmitted Alpha ===', flush=True)
    all_a = get_all_unsubmitted(sess)
    print(f'总alpha数: {len(all_a)}', flush=True)

    # STEP 2: Threshold filter + get expressions
    print('\n=== Step 2: 阈值过滤 + 获取表达式 ===', flush=True)
    candidates_raw = [a for a in all_a
                      if (a['is']['sharpe'] or 0) >= 1.25
                      and (a['is']['fitness'] or 0) >= 0.8
                      and (a['is']['turnover'] or 1) < 0.6]
    print(f'阈值通过: {len(candidates_raw)}', flush=True)

    enriched = enrich_expressions(sess, candidates_raw)

    # STEP 3: Check submission status
    print('\n=== Step 3: 检查提交状态 ===', flush=True)
    high_priority = [e for e in enriched if e['sharpe'] >= 1.5 and e['fitness'] >= 1.0]
    high_priority.sort(key=lambda x: x['sharpe'], reverse=True)

    eight_pass = []
    seven_pass = []
    needs_work = []

    for i, e in enumerate(high_priority):
        aid = e['alpha_id']
        print(f'  [{i+1}/{len(high_priority)}] {aid} S={e["sharpe"]:.2f}...', end=' ', flush=True)
        fails, sc_val, all_checks = check_alpha(sess, aid)
        e['selfcorr'] = sc_val
        e['failures'] = fails

        if fails is None:
            print('CHECK_EMPTY', flush=True)
            needs_work.append(e)
        elif len(fails) == 0:
            print(f'✓ 8-PASS SC={sc_val}', flush=True)
            eight_pass.append(e)
        elif len(fails) <= 2:
            print(f'7-pass fails={fails} SC={sc_val}', flush=True)
            seven_pass.append(e)
        else:
            print(f'pass={len(all_checks)-len(fails)}/{len(all_checks)} fails={fails}', flush=True)
            needs_work.append(e)

        time.sleep(1.5)

    print(f'\n结果: 8-pass={len(eight_pass)}, 7-pass={len(seven_pass)}, needs_work={len(needs_work)}', flush=True)

    # STEP 4: Score & rank
    print('\n=== Step 4: 评分排序 ===', flush=True)
    ranked = []
    for e in eight_pass + seven_pass:
        score = compute_score(e)
        e['total_score'] = score
        ranked.append(e)

    ranked.sort(key=lambda x: (x['total_score'], -x['sharpe']))

    # Print ranking
    print(f'\n{"Rank":<5} {"AlphaID":<12} {"Sharpe":<8} {"Fitness":<8} {"TVR":<8} {"SC":<8} {"Score":<6} {"Status":<10} {"Type":<15}', flush=True)
    print('-'*80, flush=True)
    for i, c in enumerate(ranked):
        status = '8-PASS' if c in eight_pass else '7-pass'
        etype, _ = ecom_type(c['expression'])
        sc = c.get('selfcorr', '?')
        if isinstance(sc, float):
            sc_str = f'{sc:.3f}'
        else:
            sc_str = str(sc)
        print(f'{i+1:<5} {c["alpha_id"]:<12} {c["sharpe"]:<8.2f} {c["fitness"]:<8.2f} '
              f'{c["turnover"]:<8.4f} {sc_str:<8} {c["total_score"]:<6.3f} {status:<10} {etype:<15}', flush=True)

    # STEP 5: Mark favorites
    print('\n=== Step 5: 标记Favorite ===', flush=True)
    to_fav = [c for c in ranked if c['sharpe'] >= 1.5][:30]
    fav_count = 0
    for c in to_fav:
        r = sess.patch(f'https://api.worldquantbrain.com/alphas/{c["alpha_id"]}', json={
            'color': 'YELLOW', 'tags': ['favorite']
        })
        if r.status_code in (200, 204):
            fav_count += 1
            print(f'  ✓ {c["alpha_id"]}', flush=True)
        else:
            print(f'  ✗ {c["alpha_id"]} ({r.status_code})', flush=True)
        time.sleep(0.3)
    print(f'标记favorite: {fav_count}/{len(to_fav)}', flush=True)

    # STEP 6: Save report
    print('\n=== Step 6: 保存报告 ===', flush=True)
    report = {
        'generated_at': datetime.now().isoformat(),
        'account': CREDENTIALS[0],
        'summary': {
            'total_alphas': len(all_a),
            'threshold_pass': len(candidates_raw),
            'eight_pass': len(eight_pass),
            'seven_pass': len(seven_pass),
            'needs_work': len(needs_work),
            'favorites_marked': fav_count,
        },
        'ranking': [{
            'rank': i+1,
            'alpha_id': c['alpha_id'],
            'sharpe': c['sharpe'],
            'fitness': c['fitness'],
            'turnover': c['turnover'],
            'selfcorr': c.get('selfcorr'),
            'score': c['total_score'],
            'status': '8-PASS' if c in eight_pass else '7-pass',
            'failures': c.get('failures', []),
            'decay': c.get('decay', 0),
            'neutralization': c.get('neut', ''),
            'expression_preview': c.get('expression', '')[:100],
        } for i, c in enumerate(ranked[:50])]
    }

    report_path = OUTPUT_DIR / f'new-account-pipeline-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'报告已保存: {report_path}', flush=True)

    # Final summary
    print('\n' + '='*70, flush=True)
    print('最终汇总', flush=True)
    print('='*70, flush=True)
    print(f'总alpha: {len(all_a)}', flush=True)
    print(f'8-pass就绪: {len(eight_pass)}', flush=True)
    print(f'7-pass待升阶: {len(seven_pass)}', flush=True)
    print(f'标记Favorite: {fav_count}', flush=True)

    print('\nTop 10 最终排名:', flush=True)
    for c in ranked[:10]:
        sc = c.get('selfcorr', '?')
        if isinstance(sc, float): sc_str = f'{sc:.3f}'
        else: sc_str = str(sc)
        print(f'  #{ranked.index(c)+1:2d} {c["alpha_id"]:12s} S={c["sharpe"]:.2f} F={c["fitness"]:.2f} '
              f'TVR={c["turnover"]:.4f} SC={sc_str} {c.get("expression","")[:60]}', flush=True)

    print(f'\n报告: {report_path}', flush=True)

if __name__ == '__main__':
    main()

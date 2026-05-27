#!/usr/bin/env python3
"""Fitness boost for asset turnover candidate (need F>=1.0)."""
import sys, json, time
from pathlib import Path
from datetime import datetime

from machine_lib import login, set_alpha_properties

OUT = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')

WS3_MKT_RAW = 'divide(winsorize(ts_backfill(revenue, 252), std=3), add(abs(winsorize(ts_backfill(assets, 252), std=3)), 1))'

variants = [
    ('fb_mkt_d15', 'group_rank(%s, market)' % WS3_MKT_RAW, 15, 'MARKET'),
    ('fb_mkt_d20', 'group_rank(%s, market)' % WS3_MKT_RAW, 20, 'MARKET'),
    ('fb_mkt_r6', 'group_rank(rank(%s), market)' % WS3_MKT_RAW, 6, 'MARKET'),
    ('fb_mkt_ts', 'group_rank(ts_mean(%s, 22), market)' % WS3_MKT_RAW, 0, 'MARKET'),
    ('fb_mkt_t05', 'group_rank(%s, market)' % WS3_MKT_RAW, 12, 'MARKET'),  # trunc 0.05

    # densify + market hybrid
    ('fb_dc_mkt', "group_neutralize(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % WS3_MKT_RAW, 0, 'MARKET'),
    ('fb_dc_mkt_d6', "group_neutralize(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % WS3_MKT_RAW, 6, 'MARKET'),

    # P2Y test period (longer evaluation)
    ('fb_p2y_d12', 'group_rank(%s, market)' % WS3_MKT_RAW, 12, 'MARKET'),  # testPeriod=P2Y
]

s = login()
results = []
for name, expr, decay, neut in variants:
    is_p2y = 'p2y' in name
    sim = {
        'type': 'REGULAR',
        'settings': {
            'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
            'delay': 1, 'decay': decay, 'neutralization': neut,
            'truncation': 0.05 if 't05' in name else 0.08,
            'pasteurization': 'ON',
            'testPeriod': 'P2Y' if is_p2y else 'P0Y',
            'unitHandling': 'VERIFY', 'nanHandling': 'ON',
            'language': 'FASTEXPR', 'visualization': False,
        },
        'regular': expr,
    }
    print('\n  ▶ %s (d=%d n=%s %s)...' % (name, decay, neut, 'P2Y' if is_p2y else 'P0Y'), flush=True)
    resp = s.post('https://api.worldquantbrain.com/simulations', json=sim)
    if resp.status_code != 201:
        print('    ❌ HTTP %d' % resp.status_code, flush=True)
        results.append({'name': name, 'status': 'FAILED'})
        time.sleep(4)
        continue
    url = resp.headers['Location']
    result = None
    for _ in range(180):
        time.sleep(5)
        prog = s.get(url)
        if prog.headers.get('Retry-After'): time.sleep(float(prog.headers['Retry-After'])); continue
        if prog.status_code != 200: continue
        st = prog.json().get('status', '')
        if st in ('COMPLETE', 'WARNING'):
            aid = prog.json().get('alpha')
            if aid:
                set_alpha_properties(s, aid, name=name, color='YELLOW', tags=['at_fb'])
                ad = s.get('https://api.worldquantbrain.com/alphas/%s' % aid).json()
                im = ad.get('is', {})
                result = {'alpha_id': aid, 'name': name, 'sharpe': im.get('sharpe'),
                          'fitness': im.get('fitness'), 'turnover': im.get('turnover')}
            break
        elif st in ('CANCELLED', 'ERROR'):
            break
    if result:
        print('    ✅ S=%.2f F=%.2f TVR=%.4f' % (result['sharpe'], result['fitness'], result['turnover']), flush=True)
        results.append(result)
    else:
        print('    ❌ FAIL', flush=True)
        results.append({'name': name, 'status': 'FAILED'})
    time.sleep(4)

print('\n' + '='*60, flush=True)
print('  FITNESS BOOST RESULTS', flush=True)
print('='*60, flush=True)
passes = [r for r in results if r.get('sharpe')]
passes.sort(key=lambda x: x.get('fitness',0) or 0, reverse=True)
for r in passes:
    flag = '✅' if (r.get('fitness') or 0) >= 1.0 else ''
    flag2 = '✅' if (r.get('sharpe') or 0) >= 1.2 else ''
    print('  %-20s S=%.2f F=%.2f TVR=%.4f  S%s F%s' % (r['name'], r['sharpe'], r['fitness'], r['turnover'], flag2, flag), flush=True)

opf = OUT / ('at-fb-%s.json' % datetime.now().strftime('%Y%m%d_%H%M%S'))
opf.write_text(json.dumps({'started': datetime.now().isoformat(), 'results': results}, indent=2))
print('\nSaved: %s' % opf, flush=True)

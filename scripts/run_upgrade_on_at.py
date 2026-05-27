#!/usr/bin/env python3
"""Use existing upgrade framework on asset turnover best candidate."""
import sys, json, time
from pathlib import Path
from datetime import datetime

from machine_lib import login, set_alpha_properties

PROJECT = Path('/Users/zpdedn/Documents/project/Worldquantbrain')
OUT = PROJECT / 'runs' / 'simulation-captures'
OUT.mkdir(parents=True, exist_ok=True)

BASE = 'group_rank(divide(winsorize(ts_backfill(revenue, 252), std=3), add(abs(winsorize(ts_backfill(assets, 252), std=3)), 1)), subindustry)'

variants = [
    ('at_ws3_r0', 'rank(%s)' % BASE, 0, 'SUBINDUSTRY'),
    ('at_ws3_r6', 'rank(%s)' % BASE, 6, 'SUBINDUSTRY'),
    ('at_ws3_r15', 'rank(%s)' % BASE, 15, 'SUBINDUSTRY'),
    ('at_ws3_z0', 'zscore(%s)' % BASE, 0, 'SUBINDUSTRY'),
    ('at_ws3_z6', 'zscore(%s)' % BASE, 6, 'SUBINDUSTRY'),
    ('at_ws3_gm', 'group_rank(%s, market)' % BASE, 0, 'MARKET'),
    ('at_ws3_gs', 'group_rank(%s, sector)' % BASE, 0, 'SECTOR'),
    ('at_ws3_gi', 'group_rank(%s, industry)' % BASE, 0, 'INDUSTRY'),
    ('at_ws3_dc', "densify(bucket(rank(cap), range='0.1, 1, 0.1'), %s)" % BASE, 0, 'SUBINDUSTRY'),
    ('at_ws3_q0', 'quantile(%s, 0.1)' % BASE, 0, 'SUBINDUSTRY'),
    ('at_ws3_q6', 'quantile(%s, 0.1)' % BASE, 6, 'SUBINDUSTRY'),
    ('at_ws3_tm', 'ts_mean(%s, 22)' % BASE, 0, 'SUBINDUSTRY'),
    ('at_ws3_d30', BASE, 30, 'SUBINDUSTRY'),
    ('at_ws3_d15', BASE, 15, 'SUBINDUSTRY'),
    ('at_ws3_dm12', BASE, 12, 'MARKET'),
]

s = login()
print('Existing upgrade framework — %d variants' % len(variants), flush=True)
results = []
for name, expr, decay, neut in variants:
    sim = {
        'type': 'REGULAR',
        'settings': {
            'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
            'delay': 1, 'decay': decay, 'neutralization': neut,
            'truncation': 0.08, 'pasteurization': 'ON',
            'testPeriod': 'P0Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
            'language': 'FASTEXPR', 'visualization': False,
        },
        'regular': expr,
    }
    print('\n  ▶ %s (d=%d n=%s)...' % (name, decay, neut), flush=True)
    resp = s.post('https://api.worldquantbrain.com/simulations', json=sim)
    if resp.status_code != 201:
        print('    ❌ HTTP %d' % resp.status_code, flush=True)
        results.append({'name': name, 'status': 'FAILED'})
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
                set_alpha_properties(s, aid, name=name, color='YELLOW', tags=['at_u2'])
                ad = s.get('https://api.worldquantbrain.com/alphas/%s' % aid).json()
                im = ad.get('is', {})
                result = {'alpha_id': aid, 'name': name, 'sharpe': im.get('sharpe'),
                          'fitness': im.get('fitness'), 'turnover': im.get('turnover'),
                          'decay': decay, 'neut': neut}
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
print('  EXISTING UPGRADE FRAMEWORK RESULTS', flush=True)
print('='*60, flush=True)
passes = [r for r in results if r.get('sharpe')]
passes.sort(key=lambda x: x.get('sharpe',0), reverse=True)
for r in passes:
    print('  %-20s S=%.2f F=%.2f TVR=%.4f' % (r['name'], r['sharpe'], r['fitness'], r['turnover']), flush=True)

report = {'started': datetime.now().isoformat(), 'results': results}
opf = OUT / ('at-u2-%s.json' % datetime.now().strftime('%Y%m%d_%H%M%S'))
opf.write_text(json.dumps(report, indent=2, default=str))
print('\nSaved: %s' % opf, flush=True)

#!/usr/bin/env python3
"""Decay scan for 1Yad2OAz - trying different decay windows + neutralization combinations"""
import sys, time
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
import requests

sess = requests.Session()
sess.auth = ('zpdedn@gmail.com', 'zp82648185000')
sess.post('https://api.worldquantbrain.com/authentication')
print('Auth OK')

base_expr = 'group_neutralize(ts_decay_linear((-ts_zscore(returns,252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry),40),subindustry)'

# rank wrapper with different decay + different neutralization
variants = [
    # Decay 35-42 with rank + different neut
    ('rank(' + base_expr + ')', 38, 'INDUSTRY', 'rank_ind38'),
    ('rank(' + base_expr + ')', 40, 'INDUSTRY', 'rank_ind40'),
    ('rank(' + base_expr + ')', 38, 'SECTOR', 'rank_sec38'),
    ('rank(' + base_expr + ')', 35, 'SECTOR', 'rank_sec35'),
    # zscore wrapper
    ('zscore(' + base_expr + ')', 35, 'SUBINDUSTRY', 'zscore35'),
    ('zscore(' + base_expr + ')', 38, 'SUBINDUSTRY', 'zscore38'),
    # quantile 0.3 to reduce tail
    ('quantile(rank(' + base_expr + '), 0.3)', 35, 'SUBINDUSTRY', 'quantile35'),
    ('quantile(rank(' + base_expr + '), 0.3)', 38, 'SUBINDUSTRY', 'quantile38'),
    # rank + sector neutralization
    ('rank(group_neutralize(ts_decay_linear((-ts_zscore(returns,252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry),40),sector))', 35, 'SECTOR', 'rank_sector35'),
]

def get_sc(sess, alpha_id):
    for attempt in range(3):
        time.sleep(3)
        result = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}/check')
        if result.status_code == 200:
            try:
                data = result.json()
                checks = data.get('is', {}).get('checks', [])
                sc = next((c.get('value') for c in checks if c.get('name')=='SELF_CORRELATION'), None)
                sc_res = next((c.get('result') for c in checks if c.get('name')=='SELF_CORRELATION'), None)
                return sc, sc_res
            except:
                continue
        elif 'retry-after' in result.headers:
            time.sleep(float(result.headers['retry-after']))
    return None, None

for expr, decay, neut, name in variants:
    print(f'Simulating {name}...', flush=True)
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': neut,
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    r = sess.post('https://api.worldquantbrain.com/simulations', json={'type': 'REGULAR', 'settings': settings, 'regular': expr})
    if r.status_code != 201:
        print(f'  POST_FAIL'); continue
    url = r.headers['Location']
    for _ in range(120):
        prog = sess.get(url)
        h = prog.headers
        if h.get('Retry-After'):
            time.sleep(float(h['Retry-After'])); continue
        result = prog.json()
        status = result.get('status')
        alpha_id = result.get('alpha')
        if status in ('COMPLETE', 'WARNING') and alpha_id:
            ad = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}').json()
            is_m = ad.get('is', {})
            sharpe = is_m.get('sharpe')
            fitness = is_m.get('fitness')
            turnover = is_m.get('turnover')
            sc, sc_res = get_sc(sess, alpha_id)
            print(f'  S={sharpe:.3f} F={fitness:.3f} TVR={turnover:.3f} SC={sc} ({sc_res}) | {alpha_id}')
            break
        elif status == 'ERROR':
            print(f'  ERROR'); break
        time.sleep(5)
    time.sleep(3)

print('Done')
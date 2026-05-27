#!/usr/bin/env python3
"""wpnEgzz5 sentiment-based alpha aggressive upgrade"""
import sys, time
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
import requests

sess = requests.Session()
sess.auth = ('zpdedn@gmail.com', 'zp82648185000')
sess.post('https://api.worldquantbrain.com/authentication')
print('Auth OK')

# wpnEgzz5 expression (sentiment-based)
base_expr = 'trade_when(rank(ts_mean(scl12_sentiment_fast_d1,20)) > 0.55, group_neutralize(ts_decay_linear((-ts_zscore(returns, 252)) * group_rank(rank(1 / (1 + ts_std_dev(close / vwap, 20))) * rank(ts_mean(volume, 120) / ts_mean(volume, 80)), subindustry), 40), subindustry), -1)'

# Core returns part (without sentiment trigger)
core_returns = 'group_neutralize(ts_decay_linear((-ts_zscore(returns, 252)) * group_rank(rank(1 / (1 + ts_std_dev(close / vwap, 20))) * rank(ts_mean(volume, 120) / ts_mean(volume, 80)), subindustry), 40), subindustry)'

variants = [
    # 去trade_when
    (core_returns, 0, 'no_tw'),
    # rank包装
    ('rank(' + core_returns + ')', 0, 'rank_wrap'),
    # zscore包装
    ('zscore(' + core_returns + ')', 0, 'zscore_wrap'),
    # 不同decay
    (core_returns.replace(', 40)', ', 30)'), 0, 'decay30'),
    (core_returns.replace(', 40)', ', 35)'), 0, 'decay35'),
    (core_returns.replace(', 40)', ', 45)'), 0, 'decay45'),
    # 不同neutralization
    (core_returns.replace('subindustry), subindustry)', 'industry), industry)'), 0, 'neut_industry'),
    (core_returns.replace('subindustry), subindustry)', 'sector), sector)'), 0, 'neut_sector'),
    # TW + rank
    ('trade_when(rank(ts_mean(scl12_sentiment_fast_d1,20)) > 0.55, rank(' + core_returns + '), -1)', 0, 'tw_rank'),
    # TW + zscore
    ('trade_when(rank(ts_mean(scl12_sentiment_fast_d1,20)) > 0.55, zscore(' + core_returns + '), -1)', 0, 'tw_zscore'),
    # TW + decay调整
    ('trade_when(rank(ts_mean(scl12_sentiment_fast_d1,20)) > 0.55, group_neutralize(ts_decay_linear((-ts_zscore(returns, 252)) * group_rank(rank(1 / (1 + ts_std_dev(close / vwap, 20))) * rank(ts_mean(volume, 120) / ts_mean(volume, 80)), subindustry), 30), subindustry), -1)', 0, 'tw_decay30'),
    # 激进: 换sentiment field
    ('trade_when(rank(ts_mean(scl12_sentiment_fast_d1,10)) > 0.55, ' + core_returns + ', -1)', 0, 'tw_sent10'),
    ('trade_when(rank(ts_mean(scl12_sentiment_fast_d1,30)) > 0.55, ' + core_returns + ', -1)', 0, 'tw_sent30'),
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

for expr, decay, name in variants:
    print(f'Simulating {name}...', flush=True)
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': 'SUBINDUSTRY',
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
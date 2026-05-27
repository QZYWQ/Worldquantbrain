#!/usr/bin/env python3
"""Batch check SC for all may19 promising alphas - slower, more reliable"""
import sys, time, json
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
import requests

sess = requests.Session()
sess.auth = ('zpdedn@gmail.com', 'zp82648185000')
sess.post('https://api.worldquantbrain.com/authentication')
print('Auth OK')

with open('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/may19-promising-alphas.json') as f:
    data = json.load(f)

alpha_ids = [a['alphaId'] for a in data['alphas']]
print(f'Total to check: {len(alpha_ids)}')

results = {}
checked = 0
for i, aid in enumerate(alpha_ids):
    print(f'[{i+1}/{len(alpha_ids)}] {aid}...', end=' ', flush=True)

    for attempt in range(5):
        time.sleep(5)
        result = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}/check')
        if result.status_code == 200:
            try:
                js = result.json()
                checks = js.get('is', {}).get('checks', [])
                sc = next((c.get('value') for c in checks if c.get('name')=='SELF_CORRELATION'), None)
                sc_res = next((c.get('result') for c in checks if c.get('name')=='SELF_CORRELATION'), None)
                sharpe = next((c.get('value') for c in checks if c.get('name')=='LOW_SHARPE'), None)
                fitness = next((c.get('value') for c in checks if c.get('name')=='LOW_FITNESS'), None)
                turnover = next((c.get('value') for c in checks if c.get('name')=='LOW_TURNOVER'), None)
                results[aid] = {'sc': sc, 'sc_result': sc_res, 'sharpe': sharpe, 'fitness': fitness, 'turnover': turnover}
                checked += 1
                print(f'SC={sc} ({sc_res}) [{checked} done]')
                break
            except Exception as e:
                print(f'err {e}, retry {attempt+1}')
                time.sleep(15)
                continue
        elif result.status_code == 429:
            print(f'429, wait 60s...', end=' ', flush=True)
            time.sleep(60)
        else:
            print(f'HTTP {result.status_code}, retry {attempt+1}')
            time.sleep(10)
    time.sleep(5)

# Sort by SC (None values last)
def sort_key(x):
    sc = x[1].get('sc')
    return sc if sc is not None else 999

sorted_results = sorted(results.items(), key=sort_key)

print()
print(f'=== Results: {len(results)} checked, {checked} successful ===')
print()
print('Low SC candidates (<0.8):')
low_sc = [(aid, r) for aid, r in sorted_results if r.get('sc') is not None and r.get('sc') < 0.8]
print(f'Count: {len(low_sc)}')
for aid, r in low_sc[:30]:
    sc = r.get('sc')
    s = r.get('sharpe')
    f = r.get('fitness')
    tvr = r.get('turnover')
    print(f'  SC={sc:.4f} | S={s:.3f} F={f:.3f} TVR={tvr:.3f} | {aid}')

print()
print('All by SC:')
for aid, r in sorted_results:
    sc = r.get('sc')
    sc_res = r.get('sc_result', 'N/A')
    s = r.get('sharpe', '?')
    f = r.get('fitness', '?')
    tvr = r.get('turnover', '?')
    print(f'  SC={sc} ({sc_res}) | S={s} F={f} | {aid}')

# Save
with open('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/may19_sc_check.json', 'w') as f:
    json.dump({'results': results, 'sorted': [(a, r) for a, r in sorted_results]}, f, indent=2, default=str)
print(f'\nSaved {len(results)} results')
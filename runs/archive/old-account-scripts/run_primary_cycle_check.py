#!/usr/bin/env python3
"""Check primary cycle candidates and run model51 FO batch"""
import sys, time
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
import requests
from machine_lib import check_submission, view_alphas

sess = requests.Session()
sess.auth = ('zpdedn@gmail.com', 'zp82648185000')
sess.post('https://api.worldquantbrain.com/authentication')
print('Auth OK')

# Primary cycle SC=PASS candidates
ids = ['qMmld9JE', 'd5l07rpX', 'RRk8k3Ln']
for aid in ids:
    ad = sess.get(f'https://api.worldquantbrain.com/alphas/{aid}').json()
    is_m = ad.get('is', {})
    print(f'{aid}: S={is_m.get("sharpe")} F={is_m.get("fitness")} TV={is_m.get("turnover")}')

print()
print('Running submission check...')
gold_bag = []
stone_bag = ids
gold = check_submission(stone_bag, gold_bag, 0)
print(f'Passed: {len(gold)}')
if gold:
    view_alphas(gold)
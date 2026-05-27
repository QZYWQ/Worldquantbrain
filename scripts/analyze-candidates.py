#!/usr/bin/env python3
"""Final analysis - find best candidates for optimization"""

import json

with open('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-all.json') as f:
    data = json.load(f)

alphas = data['alphas']
interesting = data['interesting']

# Already submitted
submitted_alpha_ids = {
    'O0bXoVV1', 'LLgOWZmn', '88Ob79jV', 'GrnExm2Q', 'e7dPWeop', 'A1gVE97w',
    'bloqmdJK', 'A1g6AlWg', 'Xg2X2jxl', 'E5g7vMjJ', 'E5repQ81', 'd5l07rpX',
    'gJmojOQm', '0mAE3qzp', '1YodbWO6', '2rvNV1qJ', 'RRNmMErj', '1YopVrdW',
    'xAeN6jGp'
}

# User's priority candidates from the table
user_priority_ids = {
    'blNRGAJl', 'WjN75gAO', 'RRNaRYm1', '9q9VLAm1', '1Yow6066',
    'Xgk7Qz6X', '78xjEAML', 'e7ngp37l', 'P0n7xG3q', 'vR5jdo7A',
    # negative to positive
    'npn7lvMw', '3qElZx8X', 'O0n7qR6Y'
}

# Get unsubmitted candidates (not submitted, not in user's priority list)
unsubmitted = [a for a in interesting if a['id'] not in submitted_alpha_ids]
print(f"Total unsubmitted with metrics: {len(unsubmitted)}")

# Get best candidates that are NOT in user's priority list
candidates = []
for a in unsubmitted:
    if a['id'] not in user_priority_ids:
        candidates.append(a)

print(f"Candidates not in user's priority list: {len(candidates)}")

# Sort by fitness
candidates.sort(key=lambda x: x['fitness'], reverse=True)

# Get top 50 by fitness
top50 = candidates[:50]

print("\n" + "="*100)
print("TOP 50 CANDIDATES NOT IN USER'S PRIORITY LIST (by fitness)")
print("="*100)

for i, a in enumerate(top50):
    sharpe = a['sharpe']
    fitness = a['fitness']
    turnover = a['turnover']
    returns = a['returns']
    alpha_id = a['id']
    code = a['code']
    checks = a['checks']
    long_count = a.get('longCount', 0)
    short_count = a.get('shortCount', 0)

    # Get failing checks only
    fail_checks = [c for c in checks if 'FAIL' in c]

    print(f"\n{i+1}. {alpha_id} S={sharpe:.2f} F={fitness:.2f} TVR={turnover:.4f} R={returns:.4f}")
    print(f"   Long={long_count} Short={short_count}")
    print(f"   Code: {code[:85]}")
    print(f"   Fail: {fail_checks}")

# Also show top candidates grouped by field
print("\n" + "="*100)
print("BEST CANDIDATES BY FIELD FAMILY")
print("="*100)

# Group by main field
field_groups = {}
for a in candidates[:200]:  # consider top 200
    code = a['code']
    if 'fn_interest_paid' in code:
        field = 'fn_interest_paid'
    elif 'fn_liab' in code:
        field = 'fn_liab'
    elif 'fn_antidilutive' in code:
        field = 'fn_antidilutive'
    elif 'fnd6_aox' in code:
        field = 'fnd6_aox'
    elif 'fnd6_rectr' in code and 'fnd6_recd' not in code:
        field = 'fnd6_rectr'
    elif 'fnd6_rectr/fnd6_recd' in code:
        field = 'fnd6_rectr/fnd6_recd'
    elif 'fnd6_rectr/fnd6_recco' in code:
        field = 'fnd6_rectr/fnd6_recco'
    elif 'fnd6_rea' in code and 'fnd6_prclq' in code:
        field = 'fnd6_rea/fnd6_prclq'
    elif 'fnd6_rea' in code:
        field = 'fnd6_rea'
    elif 'fnd6_recco' in code:
        field = 'fnd6_recco'
    elif 'fnd6_sppe' in code:
        field = 'fnd6_sppe'
    elif 'fnd6_siv' in code:
        field = 'fnd6_siv'
    elif 'fnd6_prstkc' in code:
        field = 'fnd6_prstkc'
    elif 'fnd6_pstk' in code:
        field = 'fnd6_pstk'
    else:
        field = 'other'

    if field not in field_groups:
        field_groups[field] = []
    field_groups[field].append(a)

# For each field, show best candidate
for field in sorted(field_groups.keys(), key=lambda f: -max(c['fitness'] for c in field_groups[f]) if field_groups[f] else 0):
    group = field_groups[field]
    if not group:
        continue
    best = max(group, key=lambda x: x['fitness'])
    print(f"\n{field}: {len(group)} candidates, best={best['id']} S={best['sharpe']:.2f} F={best['fitness']:.2f}")
    print(f"  Code: {best['code'][:85]}")

# Save top candidates to file
output_data = {
    'total_unsubmitted': len(unsubmitted),
    'candidates_not_in_user_priority': len(candidates),
    'top_50_by_fitness': top50,
    'field_groups': {k: [{'id': a['id'], 'code': a['code'], 'sharpe': a['sharpe'], 'fitness': a['fitness']} for a in v]
                     for k, v in field_groups.items()}
}

with open('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-analysis.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print("\n\nSaved analysis to brain-unsubmitted-analysis.json")
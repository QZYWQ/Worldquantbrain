#!/usr/bin/env python3
"""
Alpha Mining Loop — 24h continuous scan
Uses existing machine_lib.py functions
"""

import sys
import json
import os
import time
import requests
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from machine_lib import login, get_datafields

# Known strong candidate combos (tested first, before field scan)
# Each tuple: (expression, [(decay, neutralization), ...])
KNOWN_CANDIDATES = [
    # Strong base: close ts_zscore variants with sign-flip
    ('rank(-ts_zscore(close, 5))', [('5', 'SUBINDUSTRY'), ('5', 'INDUSTRY'), ('10', 'SUBINDUSTRY')]),
    ('-ts_zscore(close, 5)', [('5', 'SUBINDUSTRY'), ('5', 'INDUSTRY')]),

    # Compound signals: returns + vwap
    ('rank(-ts_zscore(returns, 5)) * rank(-ts_zscore(vwap, 5))', [('5', 'SUBINDUSTRY')]),
    ('rank(-ts_zscore(returns, 10)) * rank(-ts_zscore(vwap, 5))', [('5', 'SUBINDUSTRY')]),

    # Volume combos
    ('rank(-ts_zscore(volume, 5)) * rank(-ts_zscore(close, 5))', [('5', 'SUBINDUSTRY'), ('10', 'SUBINDUSTRY')]),

    # fn_comp with group
    ('group_rank(-ts_zscore(fn_comp_options_grants_fair_value_q, 5), industry)', [('5', 'SUBINDUSTRY'), ('10', 'SUBINDUSTRY')]),
    ('group_neutralize(rank(-ts_zscore(fn_comp_options_grants_fair_value_q, 5)), industry)', [('5', 'SUBINDUSTRY')]),

    # tobins_q
    ('rank(-ts_zscore(tobins_q_ratio, 5))', [('10', 'SUBINDUSTRY'), ('15', 'SUBINDUSTRY')]),
    ('-ts_zscore(tobins_q_ratio, 5)', [('5', 'SUBINDUSTRY')]),

    # mdl77 low-alpha fields
    ('ts_zscore(mdl77_deepvaluefactor_pfcf, 5)', [('5', 'SUBINDUSTRY'), ('10', 'SUBINDUSTRY')]),
    ('ts_zscore(mdl77_fangma_mam5, 5)', [('5', 'SUBINDUSTRY'), ('10', 'SUBINDUSTRY')]),

    # fnd6 new fields
    ('rank(-ts_zscore(fnd6_capxy, 5))', [('5', 'SUBINDUSTRY'), ('10', 'SUBINDUSTRY')]),

    # sign-flip on new fields
    ('-ts_zscore(fnd6_capxy, 5)', [('5', 'SUBINDUSTRY')]),
]

# Config
CHECK_INTERVAL = 300  # 5 min between rounds
PROJECT_ROOT = Path(os.environ.get("BRAIN_PROJECT_ROOT", "/Users/zpdedn/Documents/project/Worldquantbrain"))
RUN_ID = os.environ.get("BRAIN_RUN_ID", datetime.now().strftime("%Y-%m-%d-%H%M%S"))
OUTPUT_DIR = Path(
    os.environ.get(
        "BRAIN_ALPHA_OUTPUT_DIR",
        str(PROJECT_ROOT / "runs" / "overnight-mining" / RUN_ID),
    )
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Thresholds
MIN_SHARPE = 1.25
MIN_FITNESS = 1.0
MAX_TURNOVER = 0.7
MAX_SELFCORR = 0.7
MINING_HOURS = float(os.environ.get("BRAIN_MINING_HOURS", "24"))
MAX_SIMULATIONS = int(os.environ.get("BRAIN_MAX_SIMULATIONS", "600"))


def budget_available(state, deadline):
    return time.time() < deadline and state["submitted"] < MAX_SIMULATIONS

# Candidate generation templates
def generate_candidates(fields, max_per_field=3):
    """Generate alpha candidates from fields"""
    candidates = []
    ops_windows = [5, 10, 20]

    for _, row in fields.iterrows():
        fld = row['id']
        cov = row['coverage']
        if cov < 0.3:
            continue

        for op in ['ts_zscore', 'rank']:
            for win in ops_windows:
                if op == 'ts_zscore':
                    expr = f'ts_zscore({fld}, {win})'
                else:
                    expr = f'rank(-ts_zscore({fld}, {win}))'

                candidates.append({
                    'expr': expr,
                    'field': fld,
                    'op': op,
                    'window': win
                })

                if len(candidates) >= max_per_field * len(fields):
                    break

    return candidates[:50]  # cap per round

def simulate_candidate(s, expr, decay=0, neutralization='SUBINDUSTRY', state=None, deadline=None):
    """Simulate single candidate"""
    if state is not None and deadline is not None and not budget_available(state, deadline):
        return None

    sim_data = {
        'type': 'REGULAR',
        'settings': {
            'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
            'delay': 1, 'decay': decay, 'neutralization': neutralization,
            'truncation': 0.08, 'pasteurization': 'ON',
            'unitHandling': 'VERIFY', 'nanHandling': 'ON',
            'language': 'FASTEXPR', 'visualization': False,
        },
        'regular': expr
    }
    resp = s.post('https://api.worldquantbrain.com/simulations', json=sim_data, timeout=30)
    if resp.status_code != 201:
        print(f"  Submit failed {resp.status_code}: {resp.text[:120]}")
        return None
    if state is not None:
        state["submitted"] += 1
        print(f"  Submitted count: {state['submitted']}/{MAX_SIMULATIONS}")
    progress_url = resp.headers.get('Location', '')
    if not progress_url:
        return None

    for _ in range(60):
        if deadline is not None and time.time() >= deadline:
            return None
        prog = s.get(progress_url, timeout=30)
        data = prog.json()
        status = data.get('status', '')
        if status in ('COMPLETE', 'WARNING'):
            alpha_id = data.get('alpha', '')
            if alpha_id:
                r = s.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}', timeout=30).json()
                return r
            return None
        time.sleep(float(prog.headers.get('Retry-After', 5)))
    return None

def evaluate_alpha(r):
    """Evaluate if alpha passes thresholds"""
    if not r:
        return None, 'no_result'

    is_data = r.get('is', {})
    sharpe = is_data.get('sharpe')
    fitness = is_data.get('fitness')
    turnover = is_data.get('turnover')

    if sharpe is None:
        return None, 'no_sharpe'

    checks = is_data.get('checks', [])
    selfcorr = None
    for c in checks:
        if c['name'] == 'SELF_CORRELATION':
            selfcorr = c.get('value')
            break

    # Check thresholds
    if sharpe is None or sharpe < MIN_SHARPE:
        return None, f'low_sharpe={sharpe}'
    if fitness is None or fitness < MIN_FITNESS:
        return None, f'low_fitness={fitness}'
    if turnover is None or turnover > MAX_TURNOVER:
        return None, f'high_turnover={turnover}'
    if selfcorr is not None and selfcorr > MAX_SELFCORR:
        return None, f'high_selfcorr={selfcorr:.2f}'

    return {
        'id': r.get('id'),
        'expr': r.get('regular', {}).get('code') if isinstance(r.get('regular'), dict) else r.get('regular'),
        'sharpe': sharpe,
        'fitness': fitness,
        'turnover': turnover,
        'selfcorr': selfcorr,
        'timestamp': datetime.now().isoformat()
    }, 'pass'

def save_passed_alpha(alpha, round_num):
    """Save passed alpha to file"""
    fpath = OUTPUT_DIR / f"passed_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(fpath, 'a') as f:
        f.write(json.dumps(alpha) + '\n')
    print(f"  [Round {round_num}] SAVED: {alpha['expr'][:60]} | sharpe={alpha['sharpe']:.2f} fit={alpha['fitness']:.2f} tvr={alpha['turnover']:.2f}")

def run_round(s, round_num, state, deadline):
    """Run one scan round"""
    print(f"\n=== Round {round_num} @ {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    if not budget_available(state, deadline):
        print("  Budget or time limit reached before round start.")
        return 0

    # 0. Test known strong candidates first
    print(f"  Testing {len(KNOWN_CANDIDATES)} known candidates...")
    known_passed = 0
    for expr, variants in KNOWN_CANDIDATES:
        for decay_str, neut in variants:
            if not budget_available(state, deadline):
                print("  Budget or time limit reached during known candidates.")
                return known_passed
            decay = int(decay_str)
            try:
                r = simulate_candidate(s, expr, decay=decay, neutralization=neut, state=state, deadline=deadline)
                result, status = evaluate_alpha(r)
                if status == 'pass':
                    save_passed_alpha(result, round_num)
                    known_passed += 1
                time.sleep(1)
            except Exception as e:
                print(f"  Error: {expr[:50]}: {e}")
                continue
    print(f"  Known: {known_passed} passed")

    # 1. Get available fields
    print("  Scanning fields...")
    fields = get_datafields(s, search='fn_comp')
    if fields.empty:
        fields = get_datafields(s, search='fnd6')

    # Sort by coverage and low alpha count
    fields = fields[(fields['coverage'] > 0.4) & (fields['alphaCount'] < 500)]
    fields = fields.sort_values('alphaCount')
    fields = fields.head(20)
    print(f"  {len(fields)} candidate fields")

    # 2. Generate candidates
    candidates = generate_candidates(fields)
    print(f"  {len(candidates)} candidates generated")

    # 3. Simulate and evaluate
    passed = 0
    for i, cand in enumerate(candidates):
        if not budget_available(state, deadline):
            print("  Budget or time limit reached during generated candidates.")
            break
        try:
            r = simulate_candidate(s, cand['expr'], state=state, deadline=deadline)
            result, status = evaluate_alpha(r)

            if status == 'pass':
                save_passed_alpha(result, round_num)
                passed += 1
            else:
                print(f"  [{i+1}] FAIL: {cand['expr'][:50]} — {status}")

            time.sleep(1)  # Be nice to API

        except Exception as e:
            print(f"  Error simulating {cand['expr'][:50]}: {e}")
            continue

    print(f"  Round {round_num} done: {passed} passed")
    return passed

def main():
    """Main loop"""
    print("=== Alpha Mining Loop Started ===")
    print(f"Check interval: {CHECK_INTERVAL}s")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Thresholds: Sharpe>{MIN_SHARPE}, Fitness>{MIN_FITNESS}, TVR<{MAX_TURNOVER}, SelfCorr<{MAX_SELFCORR}")
    print(f"Run id: {RUN_ID}")
    print(f"Mining hours: {MINING_HOURS}")
    print(f"Max simulations: {MAX_SIMULATIONS}")

    round_num = 0
    total_passed = 0
    deadline = time.time() + MINING_HOURS * 3600
    state = {"submitted": 0}

    while budget_available(state, deadline):
        try:
            s = login()
            print("Logged in OK")

            while budget_available(state, deadline):
                round_num += 1
                passed = run_round(s, round_num, state, deadline)
                total_passed += passed
                print(f"  Total passed so far: {total_passed}")
                print(f"  Total submitted so far: {state['submitted']}/{MAX_SIMULATIONS}")

                if passed == 0:
                    print("  No passes this round, waiting longer...")
                    time.sleep(min(CHECK_INTERVAL * 3, max(0, deadline - time.time())))
                else:
                    time.sleep(min(CHECK_INTERVAL, max(0, deadline - time.time())))

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}, waiting 60s...")
            time.sleep(min(60, max(0, deadline - time.time())))
        except Exception as e:
            print(f"Error: {e}, waiting 30s...")
            time.sleep(min(30, max(0, deadline - time.time())))

    print("=== Alpha Mining Loop Stopped ===")
    print(f"Rounds: {round_num}")
    print(f"Submitted: {state['submitted']}")
    print(f"Passed: {total_passed}")

if __name__ == '__main__':
    main()

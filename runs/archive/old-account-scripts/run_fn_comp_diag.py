#!/usr/bin/env python3
"""
fn_comp sparse field diagnostic - 2 candidates
Tests raw direction of fn_comp_options_grants_fair_value_q with NONE neutralization
Stop: both Sharpe < 0.3 OR Fitness < 0.5 → STOP lane
"""
import json
import time
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

BATCH_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-14-fn-comp-sparse-diagnostic.json'
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SHARPE_FLOOR = 0.3
FITNESS_FLOOR = 0.5

def run_simulation(s, candidate):
    name = candidate['name']
    expr = candidate['expression']
    settings = candidate['settings']

    print(f"  -> Simulating: {name}")
    print(f"     Expression: {expr}")

    sim_data = {
        'type': 'REGULAR',
        'settings': settings,
        'regular': expr
    }

    try:
        resp = s.post('https://api.worldquantbrain.com/simulations', json=sim_data, timeout=30)
        progress_url = resp.headers.get('Location', '')
    except Exception as e:
        print(f"     POST error: {e}")
        return None

    for attempt in range(180):
        try:
            prog = s.get(progress_url, timeout=30)
            data = prog.json()
            status = data.get('status', '')

            if status in ('COMPLETE', 'WARNING'):
                alpha_id = data.get('alpha', '')
                if alpha_id:
                    alpha_data = s.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}', timeout=30).json()
                    alpha_data['_simulation_status'] = status
                    alpha_data['_candidate_name'] = name
                    return alpha_data
                return {'status': status, '_candidate_name': name}
            elif status == 'ERROR':
                print(f"     Simulation ERROR: {data}")
                return {'status': 'ERROR', '_candidate_name': name, '_error': data}

            retry_after = float(prog.headers.get('Retry-After', 5))
            print(f"     Waiting {retry_after}s... (attempt {attempt+1})")
            time.sleep(retry_after)
        except Exception as e:
            print(f"     Poll error: {e}")
            time.sleep(5)

    print(f"     Timeout")
    return {'status': 'TIMEOUT', '_candidate_name': name}


def extract_metrics(alpha_data):
    if not alpha_data or alpha_data.get('status') in ('ERROR', 'TIMEOUT'):
        return None

    is_data = alpha_data.get('is', {})
    if not is_data:
        return None

    sharpe = is_data.get('sharpe')
    fitness = is_data.get('fitness')
    turnover = is_data.get('turnover')
    returns = is_data.get('returns')
    drawdown = is_data.get('drawdown')

    checks = is_data.get('checks', [])
    selfcorr = None
    for c in checks:
        if c['name'] == 'SELF_CORRELATION':
            selfcorr = c.get('value')
            break

    return {
        'sharpe': sharpe,
        'fitness': fitness,
        'turnover': turnover,
        'returns': returns,
        'drawdown': drawdown,
        'selfcorr': selfcorr
    }


def main():
    print(f"=== fn_comp Sparse Field Diagnostic ===")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Stop: both Sharpe < {SHARPE_FLOOR} OR Fitness < {FITNESS_FLOOR} → STOP lane")
    print()

    with open(BATCH_FILE, 'r') as f:
        batch = json.load(f)

    candidates = batch['candidates']
    print(f"Loaded {len(candidates)} candidates")
    print()

    s = login()
    print("Logged in OK")
    print()

    results = []

    for i, candidate in enumerate(candidates):
        print(f"[Candidate {i+1}/{len(candidates)}]")
        result = run_simulation(s, candidate)
        metrics = extract_metrics(result)

        name = candidate['name']
        expr = candidate['expression']

        if metrics:
            sharpe = metrics.get('sharpe')
            fitness = metrics.get('fitness')
            turnover = metrics.get('turnover')
            returns = metrics.get('returns')
            drawdown = metrics.get('drawdown')

            print(f"  [RESULT] {name}")
            print(f"           Sharpe={sharpe}, Fitness={fitness}, TVR={turnover}, Ret={returns}, DD={drawdown}")

            results.append({
                'candidate': name,
                'expression': expr,
                'metrics': metrics,
                'sharpe': sharpe,
                'fitness': fitness,
                'turnover': turnover,
                'returns': returns
            })
        else:
            results.append({
                'candidate': name,
                'expression': expr,
                'metrics': None
            })
            print(f"  [FAIL] {name} - no metrics")

        print()
        time.sleep(2)

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for r in results:
        m = r['metrics']
        if m:
            print(f"{r['candidate']}: Sharpe={m.get('sharpe')}, Fitness={m.get('fitness')}, TVR={m.get('turnover')}")

    # Decision
    print()
    sharpe_vals = [r.get('sharpe') for r in results if r.get('sharpe') is not None]
    fitness_vals = [r.get('fitness') for r in results if r.get('fitness') is not None]

    if len(sharpe_vals) == 2:
        print(f"Positive direction Sharpe: {sharpe_vals[0]:.3f}")
        print(f"Negative direction Sharpe: {sharpe_vals[1]:.3f}")
        print(f"Positive Fitness: {fitness_vals[0]:.3f}")
        print(f"Negative Fitness: {fitness_vals[1]:.3f}")

        both_weak = all(s < SHARPE_FLOOR or f < FITNESS_FLOOR for s, f in zip(sharpe_vals, fitness_vals))
        pos_close_to_user = sharpe_vals[0] >= 0.4 and fitness_vals[0] >= FITNESS_FLOOR
        neg_better = sharpe_vals[1] > sharpe_vals[0] and fitness_vals[1] >= fitness_vals[0]

        print()
        print("=" * 60)
        print("DECISION")
        print("=" * 60)

        if both_weak:
            print("*** HARD STOP TRIGGERED ***")
            print("Both candidates below Sharpe floor or Fitness floor")
            print("Decision: STOP fn_comp_q lane - do not rescue sparse field")
            decision = 'STOP_LANE'
        elif pos_close_to_user:
            print(f"Positive direction ~{sharpe_vals[0]:.2f} approaching user-reported 0.42")
            print("Decision: Consider one more candidate with industry or backfill")
            decision = 'POSITIVE_VIABLE'
        elif neg_better:
            print("Negative direction significantly better")
            print("Decision: Refine negative direction with small batch")
            decision = 'NEGATIVE_BETTER'
        else:
            print("Inconclusive - marginal result")
            decision = 'INCONCLUSIVE'

    output_file = OUTPUT_DIR / f"2026-05-14-fn-comp-sparse-diagnostic-results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'batch': '2026-05-14-fn-comp-sparse-diagnostic',
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'results': results
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
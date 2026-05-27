#!/usr/bin/env python3
"""
mdl77_2amv Final Structural Rescue Batch
3 candidates - last structural rescue before killing the lane
Stop condition: best Fitness < 0.7 OR (Turnover dropped significantly AND Sharpe < 1.0 AND Returns < 0.07)
"""
import json
import time
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

BATCH_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-14-mdl77-2amv-final-structural-rescue.json'
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FITNESS_FLOOR = 0.7
SHARPE_FLOOR = 1.0
RETURNS_FLOOR = 0.07
TURNOVER_TARGET = 0.29

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


def evaluate_rescue(metrics, baseline_sharpe=1.45, baseline_fitness=0.53, baseline_tvr=0.6765):
    """Evaluate if this rescue candidate passes the stop condition thresholds"""
    if metrics is None:
        return 'fail', 'no_metrics'

    sharpe = metrics.get('sharpe')
    fitness = metrics.get('fitness')
    turnover = metrics.get('turnover')
    returns = metrics.get('returns')

    print(f"  [METRICS] Sharpe={sharpe}, Fitness={fitness}, TVR={turnover}, Ret={returns}")

    # Hard stop: Fitness < 0.7
    if fitness is not None and fitness < FITNESS_FLOOR:
        return 'kill', f'Fitness {fitness:.2f} < {FITNESS_FLOOR} floor'

    # Hard stop: Sharpe collapsed
    if sharpe is not None and sharpe < SHARPE_FLOOR:
        return 'kill', f'Sharpe {sharpe:.2f} < {SHARPE_FLOOR} floor'

    # Hard stop: Returns collapsed
    if returns is not None and returns < RETURNS_FLOOR:
        return 'kill', f'Returns {returns:.4f} < {RETURNS_FLOOR} floor'

    # Passed all floors - check if meaningfully better than baseline
    if fitness is not None and fitness >= FITNESS_FLOOR:
        return 'pass', f'Fitness {fitness:.2f} >= {FITNESS_FLOOR}'

    return 'marginal', 'passed floors but below Fitness target'


def main():
    print(f"=== mdl77_2amv Final Structural Rescue ===")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Fitness floor: {FITNESS_FLOOR}")
    print(f"Sharpe floor: {SHARPE_FLOOR}")
    print(f"Returns floor: {RETURNS_FLOOR}")
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
    best_fitness = 0

    for i, candidate in enumerate(candidates):
        print(f"[Candidate {i+1}/{len(candidates)}]")
        result = run_simulation(s, candidate)
        metrics = extract_metrics(result)

        name = candidate['name']
        expr = candidate['expression']

        if metrics:
            verdict, reason = evaluate_rescue(metrics)
            print(f"  [{verdict.upper()}] {name}: {reason}")

            sharpe = metrics.get('sharpe')
            fitness = metrics.get('fitness')
            turnover = metrics.get('turnover')

            if fitness is not None and fitness > best_fitness:
                best_fitness = fitness

            results.append({
                'candidate': name,
                'expression': expr,
                'metrics': metrics,
                'verdict': verdict,
                'reason': reason
            })
        else:
            results.append({
                'candidate': name,
                'expression': expr,
                'metrics': None,
                'verdict': 'fail',
                'reason': 'no metrics'
            })
            print(f"  [FAIL] {name} - no metrics")

        print()
        time.sleep(2)

    # Summary
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Best Fitness achieved: {best_fitness:.2f}")
    print(f"Fitness floor: {FITNESS_FLOOR}")
    print()

    kills = [r for r in results if r['verdict'] == 'kill']
    passes = [r for r in results if r['verdict'] == 'pass']

    print(f"Kill: {len(kills)}")
    print(f"Pass: {len(passes)}")

    if kills:
        print("\nKilled candidates:")
        for r in kills:
            print(f"  {r['candidate']}: {r['reason']}")

    if passes:
        print("\nPassing candidates:")
        for r in passes:
            m = r['metrics']
            print(f"  {r['candidate']}: Sharpe={m.get('sharpe')}, Fitness={m.get('fitness')}, TVR={m.get('turnover')}")

    # Hard stop decision
    print()
    print("=" * 60)
    print("DECISION")
    print("=" * 60)

    if best_fitness < FITNESS_FLOOR:
        print(f"*** HARD STOP TRIGGERED ***")
        print(f"Best Fitness {best_fitness:.2f} < {FITNESS_FLOOR} floor")
        print(f"Decision: STOP mdl77_2amv lane")
        print(f"Next: fn_comp_options_grants_fair_value_q or new mdl77/model77 field")
        decision = 'STOP_LANE'
    elif passes:
        print(f"Best Fitness {best_fitness:.2f} >= {FITNESS_FLOOR}")
        print(f"Decision: Lane viable - candidate(s) found")
        decision = 'VIABLE'
    else:
        print(f"No kills but no passes - marginal result")
        print(f"Decision: Proceed with caution, consider fn_comp next")
        decision = 'MARGINAL'

    output_file = OUTPUT_DIR / f"2026-05-14-mdl77-2amv-final-structural-rescue-results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'batch': '2026-05-14-mdl77-2amv-final-structural-rescue',
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'best_fitness': best_fitness,
            'fitness_floor': FITNESS_FLOOR,
            'results': results
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
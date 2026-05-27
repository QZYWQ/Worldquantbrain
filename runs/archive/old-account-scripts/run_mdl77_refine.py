#!/usr/bin/env python3
"""
mdl77_2amv signflip refine batch
Runs the 5 candidates from 2026-05-14-mdl77-2amv-signflip-refine.json
"""
import json
import time
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

BATCH_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-14-mdl77-2amv-signflip-refine.json'
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_SHARPE_THRESHOLD = 0.5
MIN_FITNESS_THRESHOLD = 0.8

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

    for attempt in range(120):
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


def print_result(name, metrics):
    if metrics is None:
        print(f"  [FAIL] {name} - no metrics")
        return None

    sharpe = metrics.get('sharpe')
    fitness = metrics.get('fitness')
    turnover = metrics.get('turnover')
    returns = metrics.get('returns')
    drawdown = metrics.get('drawdown')
    selfcorr = metrics.get('selfcorr')

    print(f"  [RESULT] {name}")
    print(f"           Sharpe={sharpe}, Fitness={fitness}, TVR={turnover}, Ret={returns}, DD={drawdown}, SelfCorr={selfcorr}")

    if sharpe is not None and sharpe >= MIN_SHARPE_THRESHOLD and fitness is not None and fitness >= MIN_FITNESS_THRESHOLD:
        print(f"           *** CANDIDATE QUALITY ***")
        return 'candidate'
    elif sharpe is not None and sharpe >= MIN_SHARPE_THRESHOLD:
        print(f"           above Sharpe threshold, needs fitness improvement")
        return 'polish'
    else:
        print(f"           below thresholds")
        return 'kill'


def main():
    print(f"=== mdl77_2amv Signflip Refine Batch ===")
    print(f"Started: {datetime.now().isoformat()}")
    print()

    with open(BATCH_FILE, 'r') as f:
        batch = json.load(f)

    candidates = batch['candidates']
    print(f"Loaded {len(candidates)} candidates")
    print(f"Stop condition: Sharpe < 0.5 AND Fitness < 0.8 for all → kill refinement")
    print()

    s = login()
    print("Logged in OK")
    print()

    results = []
    kill_count = 0

    for i, candidate in enumerate(candidates):
        print(f"[Candidate {i+1}/{len(candidates)}]")
        result = run_simulation(s, candidate)
        metrics = extract_metrics(result)
        verdict = print_result(candidate['name'], metrics)
        results.append({
            'candidate': candidate['name'],
            'expression': candidate['expression'],
            'metrics': metrics,
            'verdict': verdict
        })
        print()

        if verdict == 'kill':
            kill_count += 1

        time.sleep(2)

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    candidate_quality = [r for r in results if r['verdict'] == 'candidate']
    polish = [r for r in results if r['verdict'] == 'polish']
    kills = [r for r in results if r['verdict'] == 'kill']

    print(f"Candidate quality: {len(candidate_quality)}")
    print(f"Needs polish: {len(polish)}")
    print(f"Kill: {len(kills)}")

    if candidate_quality:
        print("\nCandidate quality alphas:")
        for r in candidate_quality:
            m = r['metrics']
            print(f"  {r['candidate']}: Sharpe={m.get('sharpe')}, Fitness={m.get('fitness')}, TVR={m.get('turnover')}")

    if polish:
        print("\nNeeds polish:")
        for r in polish:
            m = r['metrics']
            print(f"  {r['candidate']}: Sharpe={m.get('sharpe')}, Fitness={m.get('fitness')}, TVR={m.get('turnover')}")

    all_below_threshold = all(
        (r['metrics'].get('sharpe') or 0) < MIN_SHARPE_THRESHOLD or (r['metrics'].get('fitness') or 0) < MIN_FITNESS_THRESHOLD
        for r in results if r['metrics']
    )

    if all_below_threshold and len(results) == len(kills):
        print("\nSTOP RULE: All variants below Sharpe 0.5 + Fitness 0.8")
        print("Recommendation: Kill this refinement, move to next lane")
    elif candidate_quality:
        print("\nLane still productive - candidate(s) found")

    output_file = OUTPUT_DIR / f"2026-05-14-mdl77-2amv-signflip-refine-results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'batch': '2026-05-14-mdl77-2amv-signflip-refine',
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'candidate_quality_count': len(candidate_quality),
                'polish_count': len(polish),
                'kill_count': len(kills),
                'all_below_threshold': all_below_threshold
            }
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
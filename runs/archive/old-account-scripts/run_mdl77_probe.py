#!/usr/bin/env python3
"""
mdl77 low-crowding probe batch executor
Runs the 6 candidates from 2026-05-13-mdl77-low-crowding-probe.json
Stops early if all main candidates are below Sharpe 0.3
"""
import json
import time
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

BATCH_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-13-mdl77-low-crowding-probe.json'
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_SHARPE_THRESHOLD = 0.3

def run_simulation(s, candidate):
    """Run single simulation and return result"""
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
        print(f"     Progress URL: {progress_url}")
    except Exception as e:
        print(f"     POST error: {e}")
        return None

    # Poll for completion
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

    print(f"     Timeout after 120 attempts")
    return {'status': 'TIMEOUT', '_candidate_name': name}


def extract_metrics(alpha_data):
    """Extract key metrics from alpha result"""
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
    """Print formatted result"""
    if metrics is None:
        print(f"  [FAIL] {name} - no metrics")
        return False

    sharpe = metrics.get('sharpe')
    fitness = metrics.get('fitness')
    turnover = metrics.get('turnover')
    returns = metrics.get('returns')
    selfcorr = metrics.get('selfcorr')

    print(f"  [RESULT] {name}")
    print(f"           Sharpe={sharpe}, Fitness={fitness}, TVR={turnover}, Ret={returns}, SelfCorr={selfcorr}")

    if sharpe is not None and sharpe >= MIN_SHARPE_THRESHOLD:
        print(f"           *** ABOVE THRESHOLD ***")
        return True
    else:
        print(f"           below threshold")
        return False


def main():
    print(f"=== mdl77 Low-Crowding Probe Batch ===")
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # Load batch
    with open(BATCH_FILE, 'r') as f:
        batch = json.load(f)

    candidates = batch['candidates']
    print(f"Loaded {len(candidates)} candidates from batch")
    print(f"Policy: D1-first, bounded first probe")
    print()

    # Login
    s = login()
    print("Logged in OK")
    print()

    results = []

    # Phase 1: NONE neutralization health check (candidate 1)
    print("[Phase 1] Field-health diagnostic (NONE neutralization)")
    health_result = run_simulation(s, candidates[0])
    health_metrics = extract_metrics(health_result)
    print_result(candidates[0]['name'], health_metrics)
    results.append({
        'candidate': candidates[0]['name'],
        'phase': 1,
        'metrics': health_metrics
    })
    print()

    # Phase 2: Baseline and sign control (candidates 2-3)
    print("[Phase 2] Baseline and sign control (INDUSTRY neutralization)")

    baseline_result = run_simulation(s, candidates[1])
    baseline_metrics = extract_metrics(baseline_result)
    baseline_pass = print_result(candidates[1]['name'], baseline_metrics)
    results.append({
        'candidate': candidates[1]['name'],
        'phase': 2,
        'metrics': baseline_metrics
    })
    print()

    # If baseline negative, run sign flip control immediately
    baseline_sharpe = baseline_metrics.get('sharpe') if baseline_metrics else None
    if baseline_sharpe is not None and baseline_sharpe < 0:
        print("[Phase 2b] Baseline negative - running sign flip control")
        signflip_result = run_simulation(s, candidates[2])
        signflip_metrics = extract_metrics(signflip_result)
        signflip_pass = print_result(candidates[2]['name'], signflip_metrics)
        results.append({
            'candidate': candidates[2]['name'],
            'phase': '2b',
            'metrics': signflip_metrics
        })
        print()
    else:
        print(f"[Phase 2b] Skipping sign flip - baseline Sharpe {baseline_sharpe} not negative")
        print()

    # Phase 3: Deep-value siblings (candidates 4-6)
    print("[Phase 3] Deep-value siblings (INDUSTRY neutralization)")

    deep_value_pass_count = 0
    for i in [3, 4, 5]:
        result = run_simulation(s, candidates[i])
        metrics = extract_metrics(result)
        passed = print_result(candidates[i]['name'], metrics)
        if passed:
            deep_value_pass_count += 1
        results.append({
            'candidate': candidates[i]['name'],
            'phase': 3,
            'metrics': metrics
        })
        print()
        time.sleep(2)  # Be nice to API

    # Phase 4: Sign flip (if not already run)
    baseline_sharpe = baseline_metrics.get('sharpe') if baseline_metrics else None
    if baseline_sharpe is not None and baseline_sharpe >= 0:
        print("[Phase 4] Running sign flip control (baseline was positive)")
        signflip_result = run_simulation(s, candidates[2])
        signflip_metrics = extract_metrics(signflip_result)
        signflip_pass = print_result(candidates[2]['name'], signflip_metrics)
        results.append({
            'candidate': candidates[2]['name'],
            'phase': 4,
            'metrics': signflip_metrics
        })
        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    main_candidates = [r for r in results if r['phase'] in (2, 3)]
    sharpe_values = [r['metrics'].get('sharpe') for r in main_candidates if r['metrics'] and r['metrics'].get('sharpe') is not None]

    print(f"Main candidates (baseline + deep-value): {len(main_candidates)}")
    if sharpe_values:
        print(f"Sharpe values: {[f'{s:.3f}' for s in sharpe_values]}")
        print(f"Max Sharpe: {max(sharpe_values):.3f}")
        print(f"All below 0.3: {all(s < 0.3 for s in sharpe_values)}")

    if sharpe_values and all(s < 0.3 for s in sharpe_values):
        print()
        print("STOP RULE TRIGGERED: All main candidates below Sharpe 0.3")
        print("Recommendation: Kill this lane, do not spend more budget")
    else:
        print()
        print("Lane still viable - proceed with next iteration based on results")

    # Save results
    output_file = OUTPUT_DIR / f"2026-05-13-mdl77-low-crowding-probe-results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'batch': '2026-05-13-mdl77-low-crowding-probe',
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'main_candidates_count': len(main_candidates),
                'sharpe_values': sharpe_values,
                'max_sharpe': max(sharpe_values) if sharpe_values else None,
                'all_below_0_3': all(s < 0.3 for s in sharpe_values) if sharpe_values else None
            }
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
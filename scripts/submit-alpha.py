#!/usr/bin/env python3
"""Submit alphas using machine_lib"""

import sys

from machine_lib import login, get_check_submission

def submit_alpha(alpha_id):
    """Submit a single alpha"""
    s = login()

    # First check submission status
    print(f"Checking {alpha_id}...")
    result = s.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")

    if result.status_code != 200:
        print(f"Error getting alpha: {result.status_code}")
        return False

    data = result.json()
    print(f"  Status: {data.get('status')}")
    print(f"  Sharpe: {data.get('is', {}).get('sharpe')}")
    print(f"  Fitness: {data.get('is', {}).get('fitness')}")

    # Check if ready to submit
    checks = data.get('is', {}).get('checks', [])
    all_pass = all(c.get('result') == 'PASS' for c in checks)
    print(f"  All checks pass: {all_pass}")

    # Try to submit
    print(f"  Attempting submit...")
    submit_response = s.post(
        "https://api.worldquantbrain.com/alphas/" + alpha_id + "/submit"
    )
    print(f"  Submit response: {submit_response.status_code}")
    print(f"  Response: {submit_response.text[:500] if submit_response.text else 'empty'}")

    return submit_response.status_code == 200

def main():
    alpha_ids = ['1YoX2GxX', 'd5nbrQ5J', 'ZYjARRL3']

    for alpha_id in alpha_ids:
        print(f"\n{'='*60}")
        print(f"Processing {alpha_id}")
        print('='*60)

        try:
            success = submit_alpha(alpha_id)
            if success:
                print(f"✅ {alpha_id} submitted successfully!")
            else:
                print(f"❌ {alpha_id} submission failed")
        except Exception as e:
            print(f"Error: {e}")

        import time
        time.sleep(2)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Gross Profitability — Field Health Diagnostic Pack

Phase 1 of 24h batch mining plan.
Verifies field availability, coverage, update frequency on BRAIN platform.
"""
import sys, json, time
from pathlib import Path
from datetime import datetime

from machine_lib import login, get_datafields, get_datasets

OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/field-search-packs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REGION = 'USA'
DELAY = 1
UNIVERSE = 'TOP3000'

# Primary fields to check
PRIMARY_FIELDS = [
    'gross_profit', 'gross_margin', 'gross_income',
    'cost_of_revenue', 'cogs', 'cost_of_goods_sold',
    'revenue', 'sales',
    'assets', 'total_assets',
]

# Secondary fields (fallbacks / alternatives)
SECONDARY_FIELDS = [
    'cap', 'market_cap',
    'net_income', 'income',
    'operating_income',
    'current_assets', 'fixed_assets',
    'ppent',
]

def main():
    sess = login()
    print(f'\nField Health Check — {REGION} D{DELAY} {UNIVERSE}', flush=True)
    print('=' * 70, flush=True)

    # 1. Search each primary field
    results = {}
    for field in PRIMARY_FIELDS:
        try:
            df = get_datafields(sess, search=field, region=REGION, delay=DELAY, universe=UNIVERSE)
            rows = df.to_dict('records') if not df.empty else []
            matches = [r for r in rows if field.lower() in r.get('id', '').lower()]
            results[field] = {
                'total_results': len(rows),
                'exact_matches': len(matches),
                'fields': [{'id': r['id'], 'type': r.get('type', '?'),
                            'coverage': r.get('coverage', '?'), 'dataset': r.get('dataset', {}).get('id', '?')}
                           for r in matches[:5]] if matches else
                          [{'id': r['id'], 'type': r.get('type', '?'),
                            'coverage': r.get('coverage', '?'), 'dataset': r.get('dataset', {}).get('id', '?')}
                           for r in rows[:3]],
            }
            if matches:
                print(f'  ✓ {field}: {len(matches)} exact matches — {matches[0]["id"]} (cov={matches[0].get("coverage","?")})', flush=True)
            elif rows:
                print(f'  ~ {field}: no exact match, {len(rows)} related results', flush=True)
            else:
                print(f'  ✗ {field}: no results found', flush=True)
        except Exception as e:
            print(f'  ✗ {field}: error — {e}', flush=True)
            results[field] = {'error': str(e)}
        time.sleep(1)

    # 2. Quick check secondaries
    print('\nSecondary fields:', flush=True)
    for field in SECONDARY_FIELDS:
        try:
            df = get_datafields(sess, search=field, region=REGION, delay=DELAY, universe=UNIVERSE, limit=5)
            count = len(df)
            if count > 0:
                print(f'  ✓ {field}: {count} results', flush=True)
            else:
                print(f'  ✗ {field}: no results', flush=True)
        except Exception as e:
            print(f'  ✗ {field}: error — {e}', flush=True)
        time.sleep(0.5)

    # 3. Nutrition facts for primary confirmed fields
    print('\n--- Nutrition Facts for confirmed fields ---', flush=True)
    confirmed = [r['fields'][0]['id'] for r in results.values()
                 if isinstance(r, dict) and r.get('exact_matches', 0) > 0 and r['fields']]

    for field_id in confirmed[:5]:
        try:
            df = get_datafields(sess, search=field_id.split('(')[0], region=REGION, delay=DELAY, universe=UNIVERSE)
            rows = df.to_dict('records') if not df.empty else []
            match = next((r for r in rows if r['id'] == field_id), None)
            if match:
                print(f'\n  {field_id}:')
                print(f'    coverage:  {match.get("coverage", "?")}')
                print(f'    type:      {match.get("type", "?")}')
                print(f'    dataset:   {match.get("dataset", {}).get("id", "?")}')
                print(f'    users:     {match.get("userCount", "?")}')
                print(f'    alphas:    {match.get("alphaCount", "?")}')
        except Exception as e:
            print(f'  {field_id}: error — {e}')
        time.sleep(0.5)

    # 4. Dataset listing for fundamental datasets
    print('\n\n--- Available fundamental datasets ---', flush=True)
    try:
        ds = get_datasets(sess, region=REGION, delay=DELAY, universe=UNIVERSE)
        fnd = ds[ds['id'].str.contains('fnd|fundamental|financial', case=False, na=False)]
        for _, r in fnd.iterrows():
            print(f'  {r["id"]:40s} {r.get("name",""):40s}', flush=True)
    except Exception as e:
        print(f'  error: {e}', flush=True)

    # Summary
    print('\n' + '=' * 70, flush=True)
    confirmed_primary = [k for k, v in results.items()
                         if isinstance(v, dict) and v.get('exact_matches', 0) > 0]
    print(f'Confirmed primary fields: {confirmed_primary}', flush=True)
    print(f'Unavailable: {[k for k, v in results.items() if isinstance(v, dict) and v.get("exact_matches", 0) == 0]}', flush=True)

    # Save report
    report = {
        'generated_at': datetime.now().isoformat(),
        'region': REGION, 'delay': DELAY, 'universe': UNIVERSE,
        'primary_fields': results,
        'confirmed_primary_fields': confirmed_primary,
    }
    path = OUTPUT_DIR / f'gp_field_health_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'\nReport saved: {path}', flush=True)

if __name__ == '__main__':
    main()

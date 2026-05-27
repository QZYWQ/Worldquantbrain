#!/usr/bin/env python3
"""Profit Margin Expansion — S-1 baselines + window sweep."""

import sys

import json, time
from datetime import datetime
from pathlib import Path
from machine_lib import login, set_alpha_properties

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")

# Economic logic: 利润/营收比率的变化 → 盈利质量提升 → 超额收益
# 比率天然去规模偏倚，SUS 比 raw revenue 友好

# S-1: Baseline verification (3 baselines)
# Win skeleton from Revenue: group_rank(ts_delta(x, 21) / ts_mean(x, 252), industry)

BASELINES = [
    # Baseline 1: Net margin change rate (with backfill for sparse data)
    ("group_rank(ts_delta(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), 21) / ts_mean(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), 252), industry)",
     0, "INDUSTRY", "margin_nm_21_252"),

    # Baseline 2: Net margin change, medium windows
    ("group_rank(ts_delta(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), 63) / ts_mean(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), 252), industry)",
     0, "INDUSTRY", "margin_nm_63_252"),

    # Baseline 3: Operating margin (operating_income / revenue - different from submitted operating_income/assets)
    ("group_rank(ts_delta(ts_backfill(operating_income / revenue, 252), 63) / ts_mean(ts_backfill(operating_income / revenue, 252), 252), industry)",
     0, "INDUSTRY", "margin_om_63_252"),
]

# S0: If baselines pass, expand to window sweep
S0_VARIANTS = []
NM = [
    # Windows (21/63/126 delta × 63/126/252 mean)
    (21, 63), (21, 126), (21, 252),
    (63, 63), (63, 126), (63, 252),
    (126, 126), (126, 252),
]
for d, m in NM:
    S0_VARIANTS.append((f"group_rank(ts_delta(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), {d}) / ts_mean(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), {m}), industry)",
                        0, "INDUSTRY", f"margin_nm_d{d}m{m}"))
    S0_VARIANTS.append((f"group_rank(ts_delta(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), {d}) / ts_mean(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), {m}), subindustry)",
                        0, "SUBINDUSTRY", f"margin_nm_{d}m{m}_sub"))

# Operator variants
BODY = "ts_delta(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), 21) / ts_mean(winsorize(ts_backfill(net_income_avg / revenue, 252), std=4), 252)"
S0_VARIANTS.append((f"ts_rank(group_rank({BODY}, industry), 126)", 0, "INDUSTRY", "margin_nm_tr126"))
S0_VARIANTS.append((f"zscore(group_rank({BODY}, industry))", 0, "INDUSTRY", "margin_nm_zs"))

def simulate(session, expr, decay, neut, name):
    settings = {'instrumentType':'EQUITY','region':'USA','universe':'TOP3000','delay':1,
                'decay':decay,'neutralization':neut,'truncation':0.08,'pasteurization':'ON',
                'testPeriod':'P0Y','unitHandling':'VERIFY','nanHandling':'ON',
                'language':'FASTEXPR','visualization':False}
    r = session.post('https://api.worldquantbrain.com/simulations',
                     json={'type':'REGULAR','settings':settings,'regular':expr})
    if r.status_code != 201: return None
    url = r.headers.get('Location')
    if not url: return None
    for _ in range(120):
        time.sleep(5)
        p = session.get(url)
        if p.headers.get('Retry-After'): time.sleep(float(p.headers['Retry-After'])); continue
        result = p.json()
        aid = result.get('alpha')
        if result.get('status') in ('COMPLETE','WARNING') and aid:
            ad = session.get(f'https://api.worldquantbrain.com/alphas/{aid}').json()
            ism = ad.get('is',{})
            return {'alpha_id':aid,'name':name,'sharpe':ism.get('sharpe'),
                    'fitness':ism.get('fitness'),'turnover':ism.get('turnover'),'decay':decay,'neut':neut}
        elif result.get('status') == 'ERROR': return None
    return None

def main():
    # Phase 1: 3 baselines
    print(f"Profit Margin Expansion — S-1 Baselines", flush=True)
    s = login()
    results = []

    for expr, decay, neut, name in BASELINES:
        print(f"  {name}...", end=' ', flush=True)
        r = simulate(s, expr, decay, neut, name)
        if r:
            print(f"S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f}", flush=True)
            results.append(r)
        else:
            print("FAIL", flush=True)
        time.sleep(2)

    print(f"\nS-1 RESULTS:", flush=True)
    viable = [r for r in results if r.get('sharpe') and r['sharpe'] >= 1.0]
    for r in viable:
        print(f"  ✅ {r['name']}: S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f}", flush=True)
    not_viable = [r for r in results if not r.get('sharpe') or r['sharpe'] < 1.0]
    for r in not_viable:
        print(f"  ❌ {r['name']}: S={r.get('sharpe',0):.2f}", flush=True)

    # If any baseline viable, proceed to S0
    if viable:
        print(f"\n方向确认！进入 S0 窗口扫描...", flush=True)
        for expr, decay, neut, name in S0_VARIANTS:
            print(f"  {name}...", end=' ', flush=True)
            r = simulate(s, expr, decay, neut, name)
            if r:
                print(f"S={r['sharpe']:.2f} F={r['fitness']:.2f} TVR={r['turnover']:.4f}", flush=True)
                results.append(r)
            else:
                print("FAIL", flush=True)
            time.sleep(2)

    # Save
    report = {
        "started_at": datetime.now().isoformat(),
        "family": "profit_margin_expansion",
        "economic_logic": "净利润率变化 → 盈利质量改善 → 超额收益",
        "results": results
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = PROJECT / "runs" / "simulation-captures" / f"margin-momentum-{ts}.json"
    out.write_text(json.dumps(report, indent=2, default=str))

    # Summary
    print(f"\n{'='*60}", flush=True)
    print(f"TOTAL: {len(results)} variants", flush=True)
    s15 = [r for r in results if r.get('sharpe') and r['sharpe'] >= 1.5]
    s10 = [r for r in results if r.get('sharpe') and 1.0 <= r['sharpe'] < 1.5]
    for r in s15:
        print(f"  ⭐ {r['name']}: S={r['sharpe']:.2f} F={r['fitness']:.2f}", flush=True)
    for r in s10:
        print(f"  🔶 {r['name']}: S={r['sharpe']:.2f} F={r['fitness']:.2f}", flush=True)

main()

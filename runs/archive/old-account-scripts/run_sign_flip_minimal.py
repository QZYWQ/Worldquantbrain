#!/usr/bin/env python3
"""
Minimal Sign-Flip Batch - Direct execution
"""
import sys
from machine_lib import login, load_task_pool_single

# Force unbuffered output
sys.stdout = sys.stderr

alphas = [
    # j2nZRxnj - Priority 1
    ("reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry))", 0),
    ("reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry))", 5),
    ("reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry))", 10),
    # 1YogjVnm - Priority 1
    ("reverse(log(add(divide(fnd6_pstkl, fnd6_pstkrv), 1)))", 0),
    ("reverse(log(add(divide(fnd6_pstkl, fnd6_pstkrv), 1)))", 5),
    ("reverse(log(add(divide(fnd6_pstkl, fnd6_pstkrv), 1)))", 10),
    # RRNrvOrg - Priority 2
    ("reverse(divide(fnd6_pstkl, fnd6_pstkrv))", 0),
    ("reverse(divide(fnd6_pstkl, fnd6_pstkrv))", 5),
    ("reverse(divide(fnd6_pstkl, fnd6_pstkrv))", 10),
    # 78xdj8zv - Priority 2
    ("reverse(quantile(divide(fnd6_recco, fnd6_rectr), driver=gaussian))", 0),
    ("reverse(quantile(divide(fnd6_recco, fnd6_rectr), driver=gaussian))", 5),
    # YPNAxoYR - Priority 2
    ("reverse(multiply(fnd6_pstkc, inverse(add(abs(fnd6_pstkc), 1))))", 0),
    ("reverse(multiply(fnd6_pstkc, inverse(add(abs(fnd6_pstkc), 1))))", 5),
    # pwn65wXo - Priority 3
    ("rank(fnd6_rank)", 0),
    ("rank(fnd6_rank)", 5),
    # qMnz9vQ2 - Priority 3
    ("divide(fnd6_rank, multiply(fnd6_rank, 1.0))", 0),
    ("divide(fnd6_rank, multiply(fnd6_rank, 1.0))", 5),
]

pool = load_task_pool_single(alphas, 10)
print(f"Pool size: {len(pool)} tasks", flush=True)

from machine_lib import single_simulate
single_simulate(pool, "SUBINDUSTRY", "USA", "TOP3000", 0)
print("ALL DONE", flush=True)
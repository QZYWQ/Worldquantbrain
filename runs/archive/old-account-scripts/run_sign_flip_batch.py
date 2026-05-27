#!/usr/bin/env python3
"""
Sign-Flip Batch Simulator - 2026-05-16
Priority candidates for reverse expression testing
"""

from machine_lib import login, single_simulate, load_task_pool_single

# ============================================================
# Sign-Flip Alpha Pool
# Format: (expression, decay)
# ============================================================

sign_flip_alphas = [
    # ===== Priority 1: j2nZRxnj (Sharpe -1.17, Fitness -0.99) =====
    # Original: group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry)
    # Reverse: reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry))
    ("reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry))", 0),
    ("reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry))", 5),
    ("reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry))", 10),

    # ===== Priority 1: 1YogjVnm (Sharpe -0.82, Fitness -0.93) =====
    # Original: log(add(divide(fnd6_pstkl, fnd6_pstkrv), 1))
    # Reverse: reverse(log(add(divide(fnd6_pstkl, fnd6_pstkrv), 1)))
    ("reverse(log(add(divide(fnd6_pstkl, fnd6_pstkrv), 1)))", 0),
    ("reverse(log(add(divide(fnd6_pstkl, fnd6_pstkrv), 1)))", 5),
    ("reverse(log(add(divide(fnd6_pstkl, fnd6_pstkrv), 1)))", 10),

    # ===== Priority 2: RRNrvOrg (Sharpe -0.61, Fitness -0.63) =====
    # Original: divide(fnd6_pstkl, fnd6_pstkrv)
    # Reverse: reverse(divide(fnd6_pstkl, fnd6_pstkrv))
    ("reverse(divide(fnd6_pstkl, fnd6_pstkrv))", 0),
    ("reverse(divide(fnd6_pstkl, fnd6_pstkrv))", 5),
    ("reverse(divide(fnd6_pstkl, fnd6_pstkrv))", 10),

    # ===== Priority 2: 78xdj8zv (Sharpe -0.87, Fitness -0.51) =====
    # Original: quantile(divide(fnd6_recco, fnd6_rectr), driver=gaussian)
    # Reverse: reverse(quantile(divide(fnd6_recco, fnd6_rectr), driver=gaussian))
    ("reverse(quantile(divide(fnd6_recco, fnd6_rectr), driver=gaussian))", 0),
    ("reverse(quantile(divide(fnd6_recco, fnd6_rectr), driver=gaussian))", 5),

    # ===== Priority 2: YPNAxoYR (Sharpe -0.75, Fitness -0.51) =====
    # Original: multiply(fnd6_pstkc, inverse(add(abs(fnd6_pstkc), 1)))
    # Reverse: reverse(multiply(fnd6_pstkc, inverse(add(abs(fnd6_pstkc), 1))))
    ("reverse(multiply(fnd6_pstkc, inverse(add(abs(fnd6_pstkc), 1))))", 0),
    ("reverse(multiply(fnd6_pstkc, inverse(add(abs(fnd6_pstkc), 1))))", 5),

    # ===== Priority 3: pwn65wXo (Sharpe -1.06, Fitness -0.59) =====
    # Original: fnd6_rank (negative sign in expression)
    # Reverse: remove negative sign or test rank variant
    ("rank(fnd6_rank)", 0),
    ("rank(fnd6_rank)", 5),

    # ===== Priority 3: qMnz9vQ2 (Sharpe -1.08, Fitness -0.59) =====
    # Original: divide(fnd6_rank, multiply(fnd6_rank, 1.0)) with negative
    # Reverse: divide(fnd6_rank, multiply(fnd6_rank, 1.0)) positive
    ("divide(fnd6_rank, multiply(fnd6_rank, 1.0))", 0),
    ("divide(fnd6_rank, multiply(fnd6_rank, 1.0))", 5),
]

# ============================================================
# Simulation Settings
# ============================================================
NEUTRALIZATION = "SUBINDUSTRY"  # API only accepts SUBINDUSTRY, not "industry"
REGION = "USA"
UNIVERSE = "TOP3000"
START_FROM_TASK = 0  # Set > 0 to resume from a specific task
LIMIT_PER_TASK = 10  # Number of alphas per simulation task

print(f"Total alphas: {len(sign_flip_alphas)}")
print(f"Neutralization: {NEUTRALIZATION}")
print(f"Region: {REGION}, Universe: {UNIVERSE}")
print(f"Decay values: [0, 5, 10] per alpha")
print(f"Alphas per task: {LIMIT_PER_TASK}")
print()

# ============================================================
# Run Simulation
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Starting Sign-Flip Batch Simulation")
    print("=" * 60)

    # Create task pool
    task_pool = load_task_pool_single(sign_flip_alphas, LIMIT_PER_TASK)
    print(f"Total tasks: {len(task_pool)}")

    # Run
    single_simulate(task_pool, NEUTRALIZATION, REGION, UNIVERSE, START_FROM_TASK)

    print("=" * 60)
    print("Sign-Flip Batch Complete!")
    print("=" * 60)
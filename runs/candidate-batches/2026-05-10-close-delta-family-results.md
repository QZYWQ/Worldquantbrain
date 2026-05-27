# 2026-05-10 Close Delta Family - 8-Pass Candidates

## Current 8-Pass Candidates (Self-Correlation PENDING)

| Alpha | Expression | Decay | IS Sharpe | IS Fitness | IS Turnover | Test Fitness | 8-Pass | Self-Corr |
|-------|-----------|-------|-----------|------------|-------------|--------------|--------|-----------|
| **O0bXoVV1** | ts_zscore(-ts_delta(close,1),10) | 18 | 2.19 | **1.20** | 0.5665 | 2.20 | ✓ | PENDING |
| **npZ5gLZ3** | ts_zscore(-ts_delta(close,1),10) | 15 | 2.18 | **1.17** | 0.5825 | 2.13 | ✓ | PENDING |
| **RR2wr78b** | ts_zscore(-ts_delta(close,1),10) | 12 | 2.13 | **1.11** | 0.6056 | 2.09 | ✓ | PENDING |
| **2raoKqWN** | ts_zscore(-ts_delta(close,2),10) | 18 | 1.91 | **1.11** | 0.4294 | 1.77 | ✓ | PENDING |
| **e7dZ20Yp** | ts_rank(-ts_delta(close,1),10) | 18 | 2.12 | **1.09** | 0.5539 | 1.90 | ✓ | PENDING |
| **58ada9KN** | ts_rank(-ts_delta(close,1),10) | 16 | 2.12 | **1.08** | 0.5668 | 1.87 | ✓ | PENDING |
| **1YaAmGvR** | ts_rank(-ts_delta(close,1),10) | 20 | 2.08 | **1.07** | 0.5424 | 1.85 | ✓ | PENDING |
| **RR2waX1g** | ts_rank(-ts_delta(close,1),10) | 15 | 2.12 | **1.07** | 0.5742 | 1.82 | ✓ | PENDING |
| **P0wmXK8L** | ts_rank(-ts_delta(close,1),10) | 14 | 2.11 | **1.06** | 0.5822 | 1.80 | ✓ | PENDING |
| **88axrW0W** | ts_rank(-ts_delta(close,1),10) | 12 | 2.10 | **1.04** | 0.6016 | 1.79 | ✓ | PENDING |
| **akA9N8nw** | ts_rank(-ts_delta(close,2),10) | 18 | 1.99 | **1.12** | 0.4366 | 1.60 | ✓ | PENDING |
| **ZY2vWqpY** | ts_rank(-ts_delta(close,2),10) | 12 | 1.99 | **1.07** | 0.4754 | 1.54 | ✓ | PENDING |

## Previous Assets/Cap Family Winner
| Alpha | Expression | Decay | IS Sharpe | IS Fitness | IS Turnover | Test Fitness | 8-Pass | Self-Corr |
|-------|-----------|-------|-----------|------------|-------------|--------------|--------|-----------|
| **e7dPWeop** | ts_rank(ts_delta(assets/cap,2),20) | 6 | 1.96 | **1.02** | 0.5433 | 1.78 | ✓ | ACTIVE |

## Key Finding
Both ts_rank and ts_zscore variants pass 8 checks. ts_zscore with decay=15 (npZ5gLZ3) gives the highest combined score (Sharpe 2.18, Fitness 1.17).

## Self-Correlation Issue
One alpha failed SC check: "Self-correlation 0.8785 is above cutoff of 0.7 and Sharpe not better by 10.0% or more."

The close delta family may have self-correlation issues since these are all based on the same underlying signal (-ts_delta(close,1)). We need to wait for SC results before knowing which can actually be submitted together.
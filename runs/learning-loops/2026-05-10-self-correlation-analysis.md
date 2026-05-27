# 2026-05-10 Self-Correlation Analysis - Close Delta Family

## Findings

All close delta family candidates failed Self-Correlation check with values > 0.95:

| Alpha | Expression | Decay | IS Sharpe | IS Fitness | Self-Corr | Result |
|-------|-----------|-------|-----------|------------|-----------|--------|
| O0bXoVV1 | ts_zscore(-ts_delta(close,1),10) | 18 | 2.19 | 1.20 | SUBMITTED | ✓ |
| npZ5gLZ3 | ts_zscore(-ts_delta(close,1),10) | 15 | 2.18 | 1.17 | FAIL (0.95+) | ✗ |
| RR2wr78b | ts_zscore(-ts_delta(close,1),10) | 12 | 2.13 | 1.11 | FAIL (0.95+) | ✗ |
| akA9N8nw | ts_rank(-ts_delta(close,2),10) | 18 | 1.99 | 1.12 | FAIL (0.95+) | ✗ |
| 2raoKqWN | ts_zscore(-ts_delta(close,2),10) | 18 | 1.91 | 1.11 | FAIL (0.95+) | ✗ |
| e7dZ20Yp | ts_rank(-ts_delta(close,1),10) | 18 | 2.12 | 1.09 | FAIL (0.95+) | ✗ |

## Root Cause

All alphas in the close delta family use `ts_delta(close, N)` as the core signal. Since O0bXoVV1 was already submitted with this signal family, all siblings show >0.95 correlation and cannot be submitted together.

## Conclusion

- Close delta family: 1 submission possible (O0bXoVV1)
- Assets/cap family: 1 submission possible (e7dPWeop)
- Total: 2 alpha submissions from May 8-9 research

## Other Candidates from May 8-9

After the close delta and assets/cap families, the remaining May 8-9 alphas are:
- FND6 family: Fitness < 0.5, Sharpe < 0.8 - too weak
- Growth potential family: Fitness < 0.35, Sharpe < 0.65 - too weak
- Other expressions: All have Sharpe < 0.8 or Fitness < 0.5

## Next Steps

Need to explore completely new data fields/signal families to find additional 8-pass candidates.
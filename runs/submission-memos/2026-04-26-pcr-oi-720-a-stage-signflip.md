# 2026-04-26 pcr_oi_720 A-Stage Sign-Flip Result

## Result

- Official simulate completed on `platform.worldquantbrain.com` for `-ts_rank(pcr_oi_720, 20)` with the same baseline settings as the prior A-stage run.
- TEST view: Sharpe `-0.14`, Fitness `-0.02`, Turnover `24.36%`, Returns `-0.29%`, Drawdown `2.20%`, Margin `-0.24‱`.
- IS view: Sharpe `0.07`, Fitness `0.01`, Turnover `22.79%`, Returns `0.16%`, Drawdown `5.16%`, Margin `0.14‱`.
- IS Testing Status: `4 PASS`, `3 FAIL`, `1 PENDING`.

## Decision

- Keep the original `ts_rank(pcr_oi_720, 20)` direction as the B-stage base.
- The sign-flipped control did not improve TEST and does not replace the baseline.
- Move into B-stage shape exploration from the original direction only.

## Comparison To Prior Baseline

- Prior official baseline from `runs/research-contracts/2026-04-26-s1-prescreen-results.md`:
  - IS Sharpe `0.03` / Fitness `0.00`
  - TEST Sharpe `0.49` / Fitness `0.10`
- Directional conclusion:
  - sign-flip is materially worse on TEST, so keep the original sign.

## Next B-Stage Batch

- `signed_power(ts_rank(pcr_oi_720, 20), 2)`
- `signed_power(ts_rank(pcr_oi_720, 60), 2)`
- `zscore_power(ts_rank(pcr_oi_720, 20), 2)`
- `zscore_power(ts_rank(pcr_oi_720, 60), 2)`

## Evidence

- Live official Simulate page results were reviewed in the logged-in Chrome session.
- The test period was revealed with `Show test period` and the result summary was read from the official page.

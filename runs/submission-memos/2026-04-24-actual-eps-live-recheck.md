# 2026-04-24 Actual EPS Live Recheck

- Re-check time: `2026-04-24 18:40:19 CST (+0800)`
- Scope: `Gr372wO3`, `pw1pLoEx`, `9qA2nmmq`, `A1O2Arjg`
- Verification boundary: live official WorldQuant BRAIN alpha detail pages and `/check` endpoints from the logged-in browser session

## Results

- `Gr372wO3`
  - Expression: `group_rank(ts_rank(anl4_af_eps_value / close, 60), industry)`
  - IS: Sharpe `1.59`, Fitness `1.17`, Turnover `17.16%`
  - TEST: Sharpe `1.03`, Fitness `0.54`
  - `/check` self-correlation: `FAIL` at `0.7818` vs `d5l07rpX`
  - Verdict: strong IS, but blocked by self-correlation

- `pw1pLoEx`
  - Expression: `group_rank(-ts_rank(anl4_af_eps_value / close, 60), industry)`
  - IS: Sharpe `-1.59`, Fitness `-1.17`
  - `/check` self-correlation: `FAIL` at `0.7818` vs `d5l07rpX`
  - Verdict: hard reject

- `9qA2nmmq`
  - Expression: `group_rank(ts_rank(actual_eps_value_quarterly / close, 60), industry)`
  - IS: Sharpe `1.43`, Fitness `0.89`, Turnover `16.47%`
  - TEST: Sharpe `0.27`, Fitness `0.07`
  - `/check` self-correlation: still `PENDING` at capture time
  - Verdict: weaker than the baseline and not a useful branch

- `A1O2Arjg`
  - Expression: `group_rank(ts_rank(anl4_af_eps_value / close, 120), industry)`
  - IS: Sharpe `1.34`, Fitness `1.04`, Turnover `12.88%`
  - TEST: Sharpe `1.02`, Fitness `0.57`
  - `/check` self-correlation: `FAIL` at `0.7965` vs `d5l07rpX`
  - Verdict: viable on IS, but still blocked by self-correlation

## Decision

- Freeze the `actual_eps_value_close_industry` family.
- Do not spend more budget on near-neighbor polishing inside this family.
- The best current line remains blocked because the official `/check` endpoint resolves self-correlation against an existing alpha.
- If research continues from this topic, it needs a materially different branch rather than another 60d/120d/field-alias tweak.

# 2026-04-24 Analyst EPS Price Industry Live Re-check

- Re-check time: `2026-04-24 20:36:25 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN alpha detail API from the logged-in browser session
- Scope: `qMmld9JE`
- Family: `analyst_eps_price_industry`

## Fresh Official Status

- `qMmld9JE`
  - Expression: `group_rank(ts_rank(earnings_per_share_average/close, 60), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `AVERAGE`
  - IS summary: `Sharpe 1.64 / Fitness 1.03 / Turnover 17.32% / Returns 6.82%`
  - TEST summary: `Sharpe 0.15 / Fitness 0.03 / Turnover 17.12% / Returns 0.50%`
  - Official checks:
    - `LOW_SHARPE`: `PASS`
    - `LOW_FITNESS`: `PASS`
    - `LOW_TURNOVER`: `PASS`
    - `HIGH_TURNOVER`: `PASS`
    - `CONCENTRATED_WEIGHT`: `PASS`
    - `LOW_SUB_UNIVERSE_SHARPE`: `PASS`
    - `SELF_CORRELATION`: `PENDING`
    - `MATCHES_COMPETITION`: `PASS`

## Decision Impact

- This is the strongest live candidate seen in the current session so far.
- It clears the visible IS floor and sub-universe gate, so it is a real candidate, but TEST is still too weak for submission.
- Keep the family alive for one more structural comparison; the first follow-up should be the median sibling, not more same-window polishing.
- Do not call this submit-ready yet.

## Source Trace

- Live alpha endpoint:
  - `https://api.worldquantbrain.com/alphas/qMmld9JE`
- Live simulation endpoint:
  - `https://api.worldquantbrain.com/simulations/7QlWBdi14XS9RNfuRzKFfr`

## Next Trigger

If the median sibling does not materially improve holdout or correlation posture, freeze the primary direction and move to a different family.
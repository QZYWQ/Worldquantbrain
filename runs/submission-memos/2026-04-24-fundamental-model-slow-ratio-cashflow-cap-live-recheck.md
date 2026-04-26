# 2026-04-24 Fundamental Model Slow Ratio Cashflow Cap Live Re-check

- Re-check time: `2026-04-24 19:42:35 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN alpha detail API from the logged-in browser session
- Scope: `Jj5kq9pn`
- Family: `fundamental_model_slow_ratio_cashflow`

## Fresh Official Status

- `Jj5kq9pn`
  - Expression: `ts_rank(group_rank(ts_mean(cashflow / cap, 63), subindustry), 90)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `INFERIOR`
  - IS summary: `Sharpe 0.29 / Fitness 0.08 / Turnover 7.28% / Returns 0.93%`
  - TEST summary: `Sharpe 1.40 / Fitness 0.82 / Turnover 7.02% / Returns 4.25%`
  - Official checks:
    - `LOW_SHARPE`: `FAIL`
    - `LOW_FITNESS`: `FAIL`
    - `LOW_SUB_UNIVERSE_SHARPE`: `FAIL`
    - `CONCENTRATED_WEIGHT`: `PASS`
    - `UNITS`: `WARNING`
    - `SELF_CORRELATION`: `PENDING`

## Decision Impact

- The 90d smoothed cashflow/cap variant does not rescue the family.
- It is materially weaker than the earlier cashflow/cap anchors recorded in the project docs.
- The live official API still shows `SELF_CORRELATION=PENDING`, but the line is already dead on IS, Fitness, and sub-universe.
- Freeze `fundamental_model_slow_ratio_cashflow` and do not spend more budget on same-family smoothing or window polishing.
- If research continues, it should move to a materially different family or information source.

## Source Trace

- Live alpha endpoint:
  - `https://api.worldquantbrain.com/alphas/Jj5kq9pn`
- Live simulation endpoint:
  - `https://api.worldquantbrain.com/simulations/1MJgU969l5bRa5H151BIcIIU`

## Next Trigger

Only revisit this family if a genuinely new information source appears that is not just another `cashflow / cap` smoothing or horizon tweak.

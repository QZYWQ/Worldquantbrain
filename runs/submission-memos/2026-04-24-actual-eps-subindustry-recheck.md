# 2026-04-24 Actual EPS Subindustry Re-check

- Re-check time: `2026-04-24 19:49:50 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN alpha detail API from the logged-in browser session
- Scope: `kqLMrxKk`, `Gr3NAOaP`
- Family: `actual_eps_value_close_industry`

## Fresh Official Status

- `kqLMrxKk`
  - Expression: `group_rank(ts_rank(anl4_af_eps_value / close, 60), subindustry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `AVERAGE`
  - IS summary: `Sharpe 1.59 / Fitness 1.01 / Turnover 18.45% / Returns 7.49%`
  - TEST summary: `Sharpe 1.10 / Fitness 0.53 / Turnover 18.03% / Returns 4.26%`
  - Official checks:
    - `LOW_SHARPE`: `PASS`
    - `LOW_FITNESS`: `PASS`
    - `LOW_SUB_UNIVERSE_SHARPE`: `PASS`
    - `SELF_CORRELATION`: `FAIL` at `0.7651`

- `Gr3NAOaP`
  - Expression: `group_rank(ts_rank(actual_eps_value_quarterly / close, 60), subindustry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `INFERIOR`
  - IS summary: `Sharpe 1.50 / Fitness 0.84 / Turnover 17.68% / Returns 5.60%`
  - TEST summary: `Sharpe 0.67 / Fitness 0.24 / Turnover 17.41% / Returns 2.26%`
  - Official checks:
    - `LOW_SHARPE`: `PASS`
    - `LOW_FITNESS`: `FAIL` (`0.84` vs `1.0`)
    - `LOW_SUB_UNIVERSE_SHARPE`: `PASS`
    - `SELF_CORRELATION`: `PENDING`

## Decision Impact

- The subindustry follow-up improves the actual-EPS family on the full-IS side, but it still does not produce a submit-ready alpha.
- `kqLMrxKk` is the best local candidate in this family so far, but it is blocked by official self-correlation against `d5l07rpX`.
- `Gr3NAOaP` does not rescue the family: it loses the Fitness gate and does not yet resolve self-correlation.
- Freeze `actual_eps_value_close_industry` for the current budget. No more same-family smoothing, window polishing, or field-axis tweaking is justified.
- If research continues, it needs a materially different family or information source.

## Source Trace

- Live alpha endpoints:
  - `https://api.worldquantbrain.com/alphas/kqLMrxKk`
  - `https://api.worldquantbrain.com/alphas/kqLMrxKk/check`
  - `https://api.worldquantbrain.com/alphas/Gr3NAOaP`
  - `https://api.worldquantbrain.com/alphas/Gr3NAOaP/check`
- Live simulation endpoints:
  - `https://api.worldquantbrain.com/simulations/1MJgU969l5bRa5H151BIcIIU`
  - `https://api.worldquantbrain.com/simulations/44oKtx6GE4uGbZdAwFkzFoD`

## Next Trigger

Only revisit this family if a genuinely new actual-EPS source appears that is not just another close-price ratio, horizon tweak, or neutralization tweak.

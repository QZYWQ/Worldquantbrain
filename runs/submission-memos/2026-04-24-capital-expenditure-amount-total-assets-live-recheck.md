# 2026-04-24 Capital Expenditure Amount Total Assets Live Re-check

- Re-check time: `2026-04-24 20:24:40 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN alpha detail API from the logged-in browser session
- Scope: `N15GoLWX`
- Family: `capital_expenditure_amount_total_assets_industry`

## Fresh Official Status

- `N15GoLWX`
  - Expression: `group_rank(ts_rank(capital_expenditure_amount / total_assets_amount, 84), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `INFERIOR`
  - IS summary: `Sharpe 0.43 / Fitness 0.15 / Turnover 6.45% / Returns 1.45%`
  - TEST summary: `Sharpe -0.08 / Fitness -0.01 / Turnover 6.45% / Returns -0.25%`
  - Official checks:
    - `LOW_SHARPE`: `FAIL`
    - `LOW_FITNESS`: `FAIL`
    - `LOW_TURNOVER`: `PASS`
    - `HIGH_TURNOVER`: `PASS`
    - `CONCENTRATED_WEIGHT`: `PASS`
    - `LOW_SUB_UNIVERSE_SHARPE`: `PASS`
    - `SELF_CORRELATION`: `PENDING`
    - `MATCHES_COMPETITION`: `PASS`

## Decision Impact

- The capex-to-total-assets normalization branch does not rescue the capex family.
- IS Sharpe and Fitness are both far below the submission floor, and TEST is negative, so the line is not a near-pass candidate.
- Freeze `capital_expenditure_amount` as a family and stop spending budget on same-axis denominator swaps or smoother windows.
- If research continues, it should move to a materially different family or information source.

## Source Trace

- Live alpha endpoint:
  - `https://api.worldquantbrain.com/alphas/N15GoLWX`
- Live simulation endpoint:
  - `https://api.worldquantbrain.com/simulations/6HdomeTf58qaA3phbuz0N9`

## Next Trigger

Only revisit this family if a genuinely new thesis appears that is not just another capex normalization, smoothing, or industry-rank variant.
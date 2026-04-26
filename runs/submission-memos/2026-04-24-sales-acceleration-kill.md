# 2026-04-24 Sales Acceleration Kill Memo

- Recheck time: `2026-04-24 23:39:08 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN simulate + alpha detail API from the logged-in browser session
- Scope: `om9XLvzv` baseline vs `1YnRXKlW` control
- Family: `sales_acceleration`

## Decision

- Freeze and kill `sales_acceleration`.
- Do not run the 21d / 126d follow-ups.
- Move the next research hour to a genuinely new family or information source.

## Fresh Official Status

- Baseline `om9XLvzv`
  - Expression: `group_rank(ts_delta(ts_delta(revenue, 63), 63), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `INFERIOR`
  - IS summary: `Sharpe -0.12 / Fitness -0.02 / Turnover 5.57% / Returns -0.41%`
  - TEST summary: `Sharpe -0.22 / Fitness -0.04 / Turnover 5.26% / Returns -0.48%`
  - Official checks:
    - `LOW_SHARPE`: `FAIL`
    - `LOW_FITNESS`: `FAIL`
    - `LOW_TURNOVER`: `PASS`
    - `HIGH_TURNOVER`: `PASS`
    - `CONCENTRATED_WEIGHT`: `PASS`
    - `LOW_SUB_UNIVERSE_SHARPE`: `PASS`
    - `UNITS`: `WARNING`
    - `SELF_CORRELATION`: `PENDING`
    - `MATCHES_COMPETITION`: `PASS`

- Control `1YnRXKlW`
  - Expression: `group_rank(ts_delta(revenue, 63), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `INFERIOR`
  - IS summary: `Sharpe 0.16 / Fitness 0.04 / Turnover 4.83% / Returns 0.76%`
  - TEST summary: `Sharpe -0.60 / Fitness -0.25 / Turnover 4.47% / Returns -2.25%`
  - Official checks:
    - `LOW_SHARPE`: `FAIL`
    - `LOW_FITNESS`: `FAIL`
    - `LOW_TURNOVER`: `PASS`
    - `HIGH_TURNOVER`: `PASS`
    - `CONCENTRATED_WEIGHT`: `PASS`
    - `LOW_SUB_UNIVERSE_SHARPE`: `PASS`
    - `UNITS`: `WARNING`
    - `SELF_CORRELATION`: `PENDING`
    - `MATCHES_COMPETITION`: `PASS`

## Why Kill

- The second-difference baseline lost to the first-difference control on IS, so the acceleration thesis did not beat the simpler revenue delta.
- The control itself failed holdout badly, so there is no submit-ready path in this family.
- Both members kept the same unit warning, which is another reason not to invest more cleanup budget here.
- This batch gives a clear stop signal: the family is not worth window polishing, sign-flip cleanup, or deeper same-source expansion.

## Official Evidence Used

- `runs/field-search-packs/2026-04-24-sales-acceleration.md`
- `runs/expression-families/2026-04-24-sales-acceleration.md`
- `https://api.worldquantbrain.com/simulations/4boeSf4z34IibQbWuCCQWFy`
- `https://api.worldquantbrain.com/simulations/3KxIea7zd4vp976PMbgTc1U`
- `https://api.worldquantbrain.com/alphas/om9XLvzv`
- `https://api.worldquantbrain.com/alphas/1YnRXKlW`
- `https://api.worldquantbrain.com/alphas/om9XLvzv/recordsets/yearly-stats`
- `https://api.worldquantbrain.com/alphas/1YnRXKlW/recordsets/yearly-stats`

## Next Step

- Pivot to a genuinely new family or information source.
- If budget must stay inside the current registry, `operating_income_history_position` is the least-bad backup, but it should not displace a new-source search.


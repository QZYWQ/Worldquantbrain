# 2026-04-24 Analyst Disagreement Live Re-check

- Re-check time: `2026-04-24 20:31:05 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN alpha detail API from the logged-in browser session
- Scope: `npONXblE`
- Family: `analyst_disagreement_dts_spe_industry`

## Fresh Official Status

- `npONXblE`
  - Expression: `group_rank(-ts_rank(anl4_afv4_dts_spe, 60), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `INFERIOR`
  - IS summary: `Sharpe -0.08 / Fitness -0.01 / Turnover 11.00% / Returns -0.20%`
  - TEST summary: `Sharpe 0.49 / Fitness 0.15 / Turnover 10.77% / Returns 1.14%`
  - Official checks:
    - `LOW_SHARPE`: `FAIL`
    - `LOW_FITNESS`: `FAIL`
    - `LOW_TURNOVER`: `PASS`
    - `HIGH_TURNOVER`: `PASS`
    - `CONCENTRATED_WEIGHT`: `PASS`
    - `LOW_SUB_UNIVERSE_SHARPE`: `FAIL`
    - `SELF_CORRELATION`: `PENDING`
    - `MATCHES_COMPETITION`: `PASS`

## Decision Impact

- The inverse-disagreement sign hypothesis does not work on the official live check.
- The branch is not near the submission floor, and it also fails the sub-universe gate.
- Freeze `analyst_disagreement_dts_spe_industry` and do not spend more budget on same-axis windows or sibling swaps unless a genuinely different thesis is introduced.
- If research continues, it should move to a materially different family or information source.

## Source Trace

- Live alpha endpoint:
  - `https://api.worldquantbrain.com/alphas/npONXblE`
- Live simulation endpoint:
  - `https://api.worldquantbrain.com/simulations/45kR6MeOa4sU9TB2Nq4mGJx`

## Next Trigger

Only revisit this family if a new analyst thesis appears that is not just a sign flip, time tweak, or another same-field sibling.
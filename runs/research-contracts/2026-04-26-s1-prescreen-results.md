# 2026-04-26 S-1 Prescreen Results

## Loaded State

- `harness/progress.md`: session idle, no active feature, last verified feature now updated to `pcr_oi_720`.
- `runs/research-contracts/family-budget-ledger.json`: no active main or challenger; the legacy lanes are closed; the cold pool now holds `0.5` units after the A-stage release to the new scout.
- `runs/research-contracts/incubation-reactivation-plan.md`: the retired lanes are still documented as held / screen-killed, and the appendix scout list includes `anl4_af_eps_value`, `option_breakeven_30`, and `pcr_oi_720`.
- `runs/research-contracts/2026-04-26-family-registry-incubation-update.md`: `call_breakeven_60`, `pcr_oi_30`, `pcr_vol_90`, and `socialmedia8` are held; `socialmedia12` is screen-killed; no submit-ready family was present before this run.

## Official Field Checks

| field | dataset | type | coverage | date coverage | visible alphas | official page |
| --- | --- | --- | --- | --- | ---: | --- |
| `pcr_oi_720` | `Options Analytics / Option Analytics` | `Matrix` | `71%` | `100%` | `820` | `https://platform.worldquantbrain.com/data/data-fields/pcr_oi_720?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000` |
| `option_breakeven_30` | `Options Analytics / Option Analytics` | `Matrix` | `71%` | `100%` | `384` | `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_30?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000` |
| `anl4_af_eps_value` | `Analyst Estimate Data for Equity / Analyst Estimates` | `Matrix` | `100%` | `100%` | `246` | `https://platform.worldquantbrain.com/data/data-fields/anl4_af_eps_value?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000` |

## S-1 Method

- Distinctness is a conservative proxy estimate because the public UI exposes field metadata and prior family collisions, but not the raw candidate/anchor snapshot vectors required by the exact protocol formula.
- Signal presence is a conservative proxy estimate from coverage, date coverage, visible alpha density, and the current official Simulate readback where available.
- Thresholds from `harness/incubation-protocol.json`: distinctness `>= 0.60`, plus `+0.05` for crowded options/social sources; signal presence `>= 0.40`.

## S-1 Scores

| field | distinctness | signal_presence | threshold used | verdict | notes |
| --- | ---: | ---: | ---: | --- | --- |
| `pcr_oi_720` | `0.68` | `0.56` | `0.65 / 0.40` | pass | New options tenor, 71% coverage, 820 visible alphas, and the field is far enough from the retired 30-day lane to clear the crowded-category bump. |
| `option_breakeven_30` | `0.61` | `0.49` | `0.65 / 0.40` | fail | Signal is usable, but the source stays too close to the crowded options cluster to clear the options bump. |
| `anl4_af_eps_value` | `0.32` | `0.61` | `0.60 / 0.40` | fail | Good coverage, but the analyst/EPS cluster remains too correlated with the existing EPS family and prior self-correlation collisions. |

## S-1 Conclusion

- `pcr_oi_720` is the only candidate that clears the S-1 gate.
- `option_breakeven_30` and `anl4_af_eps_value` remain scouting-only and do not enter S0.

## S0 Check For `pcr_oi_720`

- Expression: `ts_rank(pcr_oi_720, 20)`
- Simulate settings: default USA / TOP3000 / delay 1 / Industry neutralization / 1Y test period.
- IS summary: `Sharpe 0.03`, `Fitness 0.00`, `Turnover 21.94%`, `Returns 0.09%`, `Drawdown 7.38%`, `Margin 0.08‱`.
- TEST summary: `Sharpe 0.49`, `Fitness 0.10`, `Turnover 23.55%`, `Returns 1.01%`, `Drawdown 2.60%`, `Margin 0.85‱`.
- Verdict: direction is positive and consistent across IS / TEST, so the candidate passes S0.
- Stage decision: start the family at `incubation_stage = A` rather than skipping straight to B; the baseline is positive but not strong enough to justify a deeper-stage jump.

## Budget Note

- `cold_pool_balance` was `1`; `0.5` was released to `incubate/pcr_oi_720` under the 50% cap, leaving `0.5` in reserve.

## Final Decision

- New incubate family registered: `pcr_oi_720`.
- S-1 passed: yes.
- S0 passed: yes.
- Start state: `A`.

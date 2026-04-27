# PV13 Custretsig Retsig A-Stage Family

## Metadata
- Date: 2026-04-27
- Topic: `pv13_custretsig_retsig`
- Source domain: `pv13 (Relationship Data for Equity)`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Stage: `A`
- State: `incubate`
- min_depth_completed: `false` (protocol-gated until E-stage)

## Hypothesis
Relationship-graph state variables should lead the slower accounting / analyst families by reading operating structure directly from customer / competitor links.

## Baseline
- Expression: `ts_rank(pv13_custretsig_retsig, 60)`
- Official alpha: `O0b0Kr6q`
- IS Sharpe / Fitness: `0.60 / 0.40`
- TEST Sharpe / Fitness: `0.77 / 0.53`
- Turnover: `63.97%`

## Sign-Flip Control
- Expression: `-ts_rank(pv13_custretsig_retsig, 60)`
- Official alpha: `WjajWKmd`
- IS Sharpe / Fitness: `-0.60 / -0.40`
- TEST Sharpe / Fitness: `-0.77 / -0.53`
- Turnover: `63.97%`

## A-Stage Decision
- `pv13_custretsig_retsig`: PASS -> keep the original sign and move to B-stage shape exploration.
- The sign-flip control was decisively weaker, so do not spend any more budget on the flipped direction.
- `min_depth_completed` remains `false` per the incubation protocol; this lane is incubate, not minimum-depth-complete.

## Next Step
- Use the original expression only for B-stage follow-up.
- Prefer one-axis shape changes first; do not touch the source family identity yet.

## B-Stage Follow-up
- B best: `ts_rank(pv13_custretsig_retsig, 80)` -> TEST `0.77`, Fitness `0.53`, Turnover `63.42%`.
- Structure control: `group_neutralize(ts_rank(pv13_custretsig_retsig, 80), subindustry)` -> TEST `-3.80`, Fitness `-1.39`.
- Decision: A-stage anchor remains the current best; do not advance to C stage yet.
- Observation: `ts_zscore` was dead and the 40-window micro-tune underperformed the A anchor.


# B-Stage Shape Exploration Plan: pv13 Top-3

## Scope

- Active lane: `pv13` relationship-data family
- Stage: `B` shape exploration
- Goal: improve `Fitness` or reduce `Turnover` without introducing a new data domain
- Official operator check: `ts_zscore` and `ts_scale` are available on the current WorldQuant BRAIN operator page

## Working Baselines

- `pv13_ustomergraphrank_page_rank` -> `ts_rank(pv13_ustomergraphrank_page_rank, 120)`
- `pv13_com_page_rank` -> `ts_rank(pv13_com_page_rank, 120)`
- `pv13_custretsig_retsig` -> `ts_rank(pv13_custretsig_retsig, 60)`

## Decision Rules

- Run the three candidates in priority order:
  1. `pv13_ustomergraphrank_page_rank`
  2. `pv13_com_page_rank`
  3. `pv13_custretsig_retsig`
- Submit a candidate variant only after a local dedupe gate check.
- Stop exploring a direction if the first variant in that direction falls below 80% of the candidate's A-stage TEST Sharpe.
- Keep expressions minimal and do not add new fields.
- Use the single structure-control probe as an expression-level `group_neutralize(..., subindustry)` variant so it survives the expression-only dedupe gate.

## Candidate 1: `pv13_ustomergraphrank_page_rank`

A-stage anchor:

- `ts_rank(pv13_ustomergraphrank_page_rank, 120)`

Planned B-stage variants:

1. `ts_zscore(pv13_ustomergraphrank_page_rank, 120)`
   - Purpose: operator replacement, same horizon
2. `ts_scale(pv13_ustomergraphrank_page_rank, 120)`
   - Purpose: operator replacement, range compression control
3. `ts_rank(pv13_ustomergraphrank_page_rank, 90)`
   - Purpose: shorter-horizon micro-tuning
4. `ts_rank(pv13_ustomergraphrank_page_rank, 150)`
   - Purpose: longer-horizon micro-tuning
5. `group_neutralize(ts_rank(pv13_ustomergraphrank_page_rank, 120), subindustry)`
   - Purpose: structure-axis control

## Candidate 2: `pv13_com_page_rank`

A-stage anchor:

- `ts_rank(pv13_com_page_rank, 120)`

Planned B-stage variants:

1. `ts_zscore(pv13_com_page_rank, 120)`
   - Purpose: operator replacement, same horizon
2. `ts_scale(pv13_com_page_rank, 120)`
   - Purpose: operator replacement, range compression control
3. `ts_rank(pv13_com_page_rank, 90)`
   - Purpose: shorter-horizon micro-tuning
4. `ts_rank(pv13_com_page_rank, 150)`
   - Purpose: longer-horizon micro-tuning
5. `group_neutralize(ts_rank(pv13_com_page_rank, 120), subindustry)`
   - Purpose: structure-axis control

## Candidate 3: `pv13_custretsig_retsig`

A-stage anchor:

- `ts_rank(pv13_custretsig_retsig, 60)`

Planned B-stage variants:

1. `ts_zscore(pv13_custretsig_retsig, 60)`
   - Purpose: operator replacement, same horizon
2. `ts_scale(pv13_custretsig_retsig, 60)`
   - Purpose: operator replacement, range compression control
3. `ts_rank(pv13_custretsig_retsig, 40)`
   - Purpose: shorter-horizon micro-tuning
4. `ts_rank(pv13_custretsig_retsig, 80)`
   - Purpose: longer-horizon micro-tuning
5. `group_neutralize(ts_rank(pv13_custretsig_retsig, 60), subindustry)`
   - Purpose: structure-axis control

## Execution Notes

- Record each official simulation in `runs/evidence/result_ledger.db`.
- If a variant falls more than 20% below the A-stage TEST Sharpe, stop the remaining variants in that direction.
- If a candidate does not improve on A-stage after the planned probes, keep the A-stage anchor as the working best and move on.

# C Stage Plan: pv13 Family Hybrid Scan

## Scope
- Family: `pv13` relationship-data lanes
- Parent anchors:
  - `ts_rank(pv13_ustomergraphrank_page_rank, 150)`
  - `ts_rank(pv13_com_page_rank, 150)`
- Protocol note: the incubation protocol caps C-stage at 3 variants, so this batch uses the three highest-value hybrid shapes instead of the full 8-variant prompt sweep.

## Hypothesis
Combining customer-network and competitor-network centrality should expose a broader operating-structure signal than either lane alone, while keeping the family inside the same data domain and preserving interpretability.

## Selected Variants
1. `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 150) + ts_rank(pv13_com_page_rank, 150), industry)`
   - Purpose: simplest additive hybrid; checks whether the two relationship signals reinforce each other directly.
2. `group_rank(0.7 * ts_rank(pv13_ustomergraphrank_page_rank, 150) + 0.3 * ts_rank(pv13_com_page_rank, 150), industry)`
   - Purpose: weighted hybrid that leans toward the stronger customer-centrality lane.
3. `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 150) * ts_rank(pv13_com_page_rank, 150), industry)`
   - Purpose: nonlinear interaction test; checks whether co-movement across the two relationship graphs is more informative than a simple sum.

## Settings
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Neutralization setting: `NONE`
- Test period: `P1Y`
- Pasteurization: `ON`
- Unit handling: `VERIFY`
- NaN handling: `ON`
- Language: `FASTEXPR`
- Platform decay setting: `0`

## Execution Order
1. Run local dedupe gate for each candidate expression.
2. Submit official simulations for the three selected variants.
3. Poll until the platform returns `COMPLETE` and an alpha id.
4. Fetch the alpha details JSON and record IS / TEST metrics.
5. Write the batch capture, result ledger entries, and C-stage summary.

## Success Criteria
- Best TEST Sharpe >= `1.1`
- Best TEST Fitness >= `1.8`
- If no variant clears both thresholds, keep the family as incubate and hold the current A-stage anchor.

## Notes
- No new data domain is introduced.
- The batch stays interpretable and stays inside the pv13 relationship family.
- Previous B-stage work showed that `ts_zscore` and `group_neutralize(..., subindustry)` both degraded the family, so this C batch avoids those levers.

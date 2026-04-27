# PV13 Remaining Batch Prep

## Selection Summary
- Total fields selected: 10
- Priority split: 9 high + 1 medium fallback
- Medium fallback used: `pv13_revere_index_value`
- Selection basis: visible pv13 report rows with previously explored fields excluded

## Dry-Run Preview
- Generated candidates: 240
- Ledger duplicates removed: 0
- Similarity warnings: 48
- Candidates remaining after dedupe gate: 240
- Candidates kept for preview: 100
- Top N surfaced: 5

## Observations
- The selected field list is dominated by relationship-network centrality and count-based relationship proxies, which is consistent with pv13's structure.
- `pv13_revere_index_value` rises to the top because the current sorter strongly rewards the lowest-crowding field once coverage is flat.
- The preview shows repeated expressions across neutralization variants because neutralization is metadata in the current offline skeleton, not part of the expression string.
- Similarity warnings cluster on the graph-centrality family (`ustomergraphrank*`, `com_rk_au`, `ompetitorgraphrank_hub_rank`), which suggests these rows sit close to recently stored structural patterns in the ledger.

## Top 5 Preview
- `pv13_revere_index_value` repeated five times in the preview: decay 120 (Market, None), decay 20 (Market, None), decay 60 (Market)

## Recommendation
- Do not move to live batch S0 yet unless the live submission wrapper can treat neutralization as a first-class execution parameter or the candidate mix is diversified further.
- The dry-run is useful as a shortlist preview, but the current preview is too concentrated in one field family to justify immediate slot spending.

## Diversity Fix Note
- Problem found: the first dry-run let one field family dominate the Top 5 because the sorter had no field-aware penalty and the top selection did not cap repeated fields.
- Fix applied: `scripts/batch_s0_scan.py` now applies a raw-score field diversity penalty during ranking and caps final Top N selection at 2 candidates per field.
- Result after the fix: the v2 dry-run Top 5 spans 5 distinct fields instead of collapsing to one field, so the preview now matches the intended broad-sweep behavior.
- Current v2 preview top fields: `pv13_revere_index_value`, `pv13_revere_key_sector_total`, `pv13_ompetitorgraphrank_hub_rank`, `pv13_com_rk_au`, `rel_num_comp`.

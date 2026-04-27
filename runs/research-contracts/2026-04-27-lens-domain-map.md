# 2026-04-27 LENS Domain Map

## Scope

LENS is the domain roam: use the RECURVE missing-data hypothesis to look for data classes that are orthogonal to the exhausted model-series and slow-ratio lanes.

## Evidence Used

- `runs/field-search-packs/*.md`
- `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
- `runs/session-briefs/2026-04-25-model-live-search.json`
- `runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
- `runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`
- No standalone `field_list.json` or global directory file was found.

## Domain Map: What Has Been Deeply Mined

| Domain | Field-search packs present | Example field families | Status |
| --- | --- | --- | --- |
| Analyst | yes | `anl4_*`, `actual_*`, `sales_estimate_*`, guidance / consensus ratios | deeply mined |
| Fundamental | yes | `operating_income`, `sales`, `revenue`, `capex`, `invested_capital`, `shareholders_equity_total_2 / cap` | deeply mined |
| News / Social | yes | `nws18_*`, `scl12_*`, `snt_*` | deeply mined |
| Options / Volatility | yes | `pcr_oi_*`, `pcr_vol_*`, `option_breakeven_*`, `put_breakeven_*`, `implied_volatility_mean_skew_*` | deeply mined |
| Model | yes | `growth_potential_rank_derivative`, `relative_valuation_rank_derivative`, `multi_factor_*`, `mdl177_*` | deeply mined |
| Price / Volume / Event | yes | `volume`, `adv20`, `vwap`, `historical_volatility_20`, `close` | shallow-to-moderate, but not a new domain |

## Domain Map: What Exists In The Inventory But Has Not Been Field-Pack Driven

| Domain | Inventory evidence | Example fields | Status |
| --- | --- | --- | --- |
| Relationship Data for Equity | `dataset pv13`, `subcategory Relationship`, 165 fields in the saved inventory | `pv13_com_page_rank`, `pv13_custretsig_retsig`, `pv13_hierarchy_min2_pureplay_3000_sector` | untouched in field-search packs |
| Report Footnotes | `dataset fundamental2`, 318 fields in the saved inventory; forum tip separates footnotes from the main statements | `fnd2_a_seniornotes`, `fnd2_a_restructuringcharges`, `fnd2_a_sbcpnargmpmwggil` | untouched in field-search packs |
| Risk Models | `dataset model51`, 16 fields in the saved inventory | `beta_last_60_days_spy`, `correlation_last_90_days_spy`, `unsystematic_risk_last_360_days` | untouched in field-search packs |

## Why The Untouched Domains Matter

These three domains are the best inventory-backed ways to escape the current repeated failure mode:

- they are not another slow fundamental window sweep
- they are not another analyst consensus sibling
- they are not another model-series rerating branch
- they are not another options tenor sweep

They can supply the missing forward-leading operational state that RECURVE asked for.

## Candidate Directions

### 1) Relationship graph / supply-chain network data

- **Why it is orthogonal:** it is structural, not just another accounting or analyst level; the signal lives in network position, peer pressure, and dependency topology.
- **What RECURVE demand it can satisfy:** a more forward-leading operational state proxy that can turn before reported sales or income.
- **Suggested Data Explorer keywords:** `pv13`, `relationship`, `customer`, `competitor`, `PageRank`, `HITS`, `hierarchy`, `sector`, `pureplay`.
- **Why it is the best first pick:** the saved inventory shows many live fields with full or high coverage, so this is a real, browseable domain rather than a speculative guess.

### 2) Report footnotes / note-level accounting detail

- **Why it is orthogonal:** it is not the main statement stream; it captures hidden obligations, tax, pension, share-based compensation, acquisition, and inventory detail that the current lanes do not use.
- **What RECURVE demand it can satisfy:** a slower but more structurally informative state proxy that can reveal financing pressure or operating change earlier than income-statement windows.
- **Suggested Data Explorer keywords:** `fundamental2`, `footnote`, `tax`, `pension`, `debt`, `share-based compensation`, `acquisition`, `inventory`, `notes`.
- **Why it is a strong second pick:** the forum crawl explicitly separates footnotes from the main fundamental statement set, so this is a clean untapped branch.

### 3) Risk model regime metrics

- **Why it is orthogonal:** it measures market risk, correlation, and idiosyncratic instability rather than business fundamentals or crowd sentiment.
- **What RECURVE demand it can satisfy:** a low-decay regime component that could stabilize or de-burst the current families.
- **Suggested Data Explorer keywords:** `model51`, `beta`, `correlation`, `systematic_risk`, `unsystematic_risk`, `SPY`.
- **Why it is useful:** it is present in the saved inventory, but no field-search pack in this workspace has targeted it yet.

## First Recommendation

**Best first new domain:** `Relationship Data for Equity` (`pv13`)

**Reason:** it is the most obviously orthogonal to the exhausted model / accounting / analyst loops, it is richly populated in the current inventory, and it is the most plausible source of a durable, forward-leading operational state proxy.

## Follow-On Browse Order

1. `pv13` relationship graph fields.
2. `fundamental2` footnotes fields.
3. `model51` risk model fields.
4. If all three still look like recycled state proxies, move to a truly new external domain and search again with fresh keywords.

# S-1 预筛结果：pv13 首选 3 字段

## Loaded State

- `harness/progress.md`: `idle`, no active feature.
- `runs/research-contracts/current-incubation-summary.md`: pv13 top-3 passed S-1; dedupe is pending.
- Scout files executed: `2026-04-27-s1-pv13-custretsig-retsig-scout.md`, `2026-04-27-s1-pv13-ustomergraphrank-page-rank-scout.md`, `2026-04-27-s1-pv13-com-page-rank-scout.md`

## Official Field Checks

| field | dataset | type | coverage | date coverage | visible alphas | official page |
| --- | --- | --- | --- | --- | ---: | --- |
| `pv13_custretsig_retsig` | `Relationship Data for Equity` | `MATRIX` | `92.76%` | `100.00%` | `2435` | `api.worldquantbrain.com/data-fields/pv13_custretsig_retsig` |
| `pv13_ustomergraphrank_page_rank` | `Relationship Data for Equity` | `MATRIX` | `79.06%` | `—` | `890` | `api.worldquantbrain.com/data-fields/pv13_ustomergraphrank_page_rank` |
| `pv13_com_page_rank` | `Relationship Data for Equity` | `MATRIX` | `89.66%` | `—` | `1914` | `api.worldquantbrain.com/data-fields/pv13_com_page_rank` |

## S-1 Method
- Threshold used for the conservative proxy: `0.60 / 0.40`.
- The exact snapshot-vector distinctness formula is not directly observable from the public UI, so these scores use a conservative proxy from live field metadata.
- Distinctness is judged by source-family separation from the failed analyst / qfv4 / profitability / model lanes and by whether the field reads a different operating ecosystem (customer / competitor graph rather than accounting or analyst consensus).
- Signal presence is judged by visible crowding, coverage, and whether the field surface looks active enough to support a tradeable S-1 scout.

## S-1 Scores

| field | distinctness | signal_presence | verdict | notes |
| --- | ---: | ---: | --- | --- |
| `pv13_custretsig_retsig` | `0.93` | `0.90` | `PASS` | Most direct lead-like customer signal in pv13; high coverage and the strongest visible alpha crowding of the three. |
| `pv13_ustomergraphrank_page_rank` | `0.88` | `0.71` | `PASS` | Customer network centrality is still orthogonal to the failed analyst/profitability/model families, but visible crowding is lighter and coverage is lower. |
| `pv13_com_page_rank` | `0.90` | `0.82` | `PASS` | Competitor network centrality gives a structurally different view of operating state with strong coverage and visible alpha usage. |

## Overall Read

- All three fields cleared the conservative S-1 metadata proxy screen.
- None of the three looks like a same-family analyst / profitability clone; the distinctness is coming from relationship-network semantics instead of accounting or analyst consensus.
- The strongest signal surface is `pv13_custretsig_retsig`; the other two still clear the bar and remain viable follow-ons.

## Recommendation

- `pv13_custretsig_retsig`: proceed to S-1.5 dedupe gate.
- `pv13_ustomergraphrank_page_rank`: proceed to S-1.5 dedupe gate.
- `pv13_com_page_rank`: proceed to S-1.5 dedupe gate.
- Next step after dedupe: S0 parameter scan, not baseline expansion in S-1.

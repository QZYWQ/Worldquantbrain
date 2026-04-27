# D Stage Check: pv13_ustomergraphrank_page_rank

## Field availability
- Field: `pv13_ustomergraphrank_page_rank`
- Dataset: `pv13 (Relationship Data for Equity)`
- Category: `Price Volume / Relationship`
- Type: `Matrix`
- Region: `USA`
- Delay: `1`
- Universe: `TOP3000`
- Coverage: `79%`
- Alphas: `900`
- Description: `the PageRank of customers`
- Update frequency: not surfaced on the field page

## D-stage verdict
- PASS
- No delay-0, unknown-variable, or unavailable-operator block surfaced.
- The candidate can proceed to E-stage evaluation inside the normal pv13 lane.

## Notes
- The field is reachable in Data Explorer and in the simulate path.
- The main candidate is not blocked by platform availability.

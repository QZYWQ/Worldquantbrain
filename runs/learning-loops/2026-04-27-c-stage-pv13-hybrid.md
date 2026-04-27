# Learning Loop: pv13 C-stage Hybrid Scan

## What We Tested
- Hybridized the two strongest pv13 relationship lanes:
  - `pv13_ustomergraphrank_page_rank`
  - `pv13_com_page_rank`
- Tested three interpretable C-stage shapes under `group_rank(..., industry)`:
  - simple additive blend
  - weighted additive blend
  - multiplicative interaction

## What Happened
- The weighted additive blend was the best hybrid:
  - `group_rank(0.7 * ts_rank(pv13_ustomergraphrank_page_rank, 150) + 0.3 * ts_rank(pv13_com_page_rank, 150), industry)`
  - TEST Sharpe `0.99`
  - Fitness `1.72`
  - Turnover `2.12%`
- The simple sum and product variants both landed below that weighted blend.
- None of the C-stage variants beat the existing customer-centrality A anchor.

## What We Learned
- Same-domain hybridization can improve efficiency, especially turnover, without necessarily creating a stronger signal.
- The customer-centrality anchor is still the cleanest lead; the competitor lane is useful as a secondary ingredient, not as a replacement.
- The hybrid search space looks saturated enough that more same-family polishing is probably low value.

## Next Move
- Keep the A-stage customer-centrality anchor as the working best.
- Hold the C-stage hybrid as a reference, not a promotion lead.
- If pv13 is revisited later, use a genuinely new mechanism instead of more additive tweaks between the same two ranks.

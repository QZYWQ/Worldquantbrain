# 2026-04-27 RECURVE Round 2

## Why This Matters

The pv13 family showed that a relationship-data lane can survive a long incubate path and still fail on the final Sharpe floor. That makes structure reverse-engineering the right next move: keep the same data domain, but change the way the signal is built.

## What We Learned

- The strongest legacy lines are not complicated operator soups.
- They consistently add one of two things to a raw state variable:
  - peer-relative ranking via `group_rank`
  - state construction via a ratio or a smoothing layer before the final rank
- `group_neutralize` is not the same thing as the winning `group_rank` pattern.
- pv13's current lead lane is still too bare: it ranks a raw relationship metric, but it does not yet build a richer peer-relative state.

## Most Important Gaps In pv13

1. Explicit peer context around the signal.
2. A slower state-construction layer before the final rank.

## Next Move

- First try: `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 150), industry)`
- Second try: a smoothed history-position version of the same relationship field
- Third try: a customer-vs-competitor spread or ratio

## Practical Rule

Do not spend the next pv13 hour adding more hybrid complexity.
The legacy winners suggest that a clean peer-conditioned structure is the more likely route to higher Sharpe.


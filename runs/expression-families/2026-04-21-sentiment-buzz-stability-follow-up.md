# Sentiment Buzz Stability Follow-up Expression Family

## Metadata

- Date: `2026-04-21`
- Topic: `sentiment_buzz_stability_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-21-sentiment-buzz-stability.md`
  - `./runs/notes/daily/official-alpha-cycle-day-04.md`

## Hypothesis

Relative sentiment volume should be more stable after a modest smoothing window, and the right lookback may produce a distinct non-analyst family that is less correlated than the operating_income ridge while still staying interpretable.

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `snt_buzz`
- Confirmed neutralization:
  - `industry`
- Assumptions to test:
  - A moderate smoothing window may improve signal stability without flattening the sentiment signal completely.
  - The best window may sit near `63d`, but the family should be tested with a faster and slower control first.
  - If this lane behaves better than the operating_income ridge, it can become the new primary branch; otherwise it should be killed quickly.

## Baseline Expression

```text
group_rank(ts_mean(snt_buzz, 63), industry)
```

## Variant 1

- Goal:
  Test whether a faster smoothing window reacts better to fresh buzz changes.
- Main lever:
  Reduce the smoothing window from `63` to `21`.

```text
group_rank(ts_mean(snt_buzz, 21), industry)
```

## Variant 2

- Goal:
  Test whether heavier smoothing improves stability and Fitness.
- Main lever:
  Increase the smoothing window from `63` to `126`.

```text
group_rank(ts_mean(snt_buzz, 126), industry)
```

## Variant 3

- Goal:
  Test whether very slow smoothing changes the family enough to improve the test-period view.
- Main lever:
  Increase the smoothing window from `63` to `252`.

```text
group_rank(ts_mean(snt_buzz, 252), industry)
```

## Batch 02 Update

- The `21d` control landed at `Sharpe 0.22 / Fitness 0.06 / Turnover 2.79% / Returns 1.05% / Drawdown 7.13% / Margin 7.52‱`.
- It is still weaker than the `63d` baseline on the quality metrics that matter most, even though turnover is lighter than the previous capture.
- Treat the fast window as a negative control and keep the slower `126d` and `252d` probes pending.

## Batch 03 Update

- The `126d` probe landed at `Sharpe 0.03 / Fitness 0.00 / Turnover 2.45% / Returns 0.11% / Drawdown 4.47% / Margin 0.90‱`.
- It is materially weaker than the `63d` baseline and does not improve the ridge.
- Keep the `252d` probe as the last planned control before calling the family dead or branching away.

## Batch 04 Update

- The `252d` control failed cleanly on the test-period view at `Sharpe -0.44 / Fitness -0.17 / Turnover 1.73% / Returns -1.76% / Drawdown 5.94% / Margin -20.33‱`.
- Visible IS Testing Status counts were `4 PASS / 3 FAIL / 1 PENDING`.
- `Submit Alpha` stayed disabled and no visible `Check Submission` or non-null subuniverse evidence appeared.
- This confirms the family is dead; do not spend more time polishing the buzz window sweep.

## Expected First Failure

- Sharpe:
  The raw buzz signal may still be noisy even after smoothing.
- Fitness:
  This may remain the first bottleneck if the signal is too crowded or too jumpy.
- Turnover:
  The faster variant could become too active if buzz reacts sharply to events.
- Weight:
  Concentration may show up if only a small set of names carries the useful sentiment signal.
- Sub-universe:
  Still unknown until real simulation results and testing status evidence appear.
- Self-correlation:
  Unknown until live checks exist.

## Optimization Order

1. Sweep only the smoothing window first; do not add extra operators until the ridge shape is known.
2. Keep the family on one field and one neutralization choice for the first batch.
3. If the family fails to produce a better ridge than the operating_income branch, abandon it quickly and move to the next non-analyst lane.

## Branch Decision

- Kill the sentiment-buzz stability family.
- Keep the 63d baseline and 21d/126d/252d controls as a completed negative sweep for reference only.
- Move the next live simulation effort to the strongest remaining fundamentals branch instead of any more buzz smoothing.

# PCR OI All Industry Rank Follow-up Expression Family

## Metadata

- Date: `2026-04-22`
- Topic: `pcr_oi_all_industry_rank_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-20-event-option-volume-gate.md`
  - official WorldQuant BRAIN simulate UI in this session

## Hypothesis

If the put/call open-interest ratio is ranked directly inside its industry group, the branch may keep the strong TEST-period behavior while reducing the in-sample drift that showed up in the gate-based option family.

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `pcr_oi_all`
- Confirmed neutralization:
  - `industry`
- Assumptions to test:
  - A plain direct-rank baseline may be more stable than the earlier gate-based option family.
  - Light smoothing could reduce day-to-day noise without destroying the TEST-period edge.
  - A slower rank window or tighter grouping axis may improve the weak IS readout.

## Baseline Expression

```text
group_rank(ts_rank(pcr_oi_all, 20), industry)
```

## Variant 1

- Goal:
  Test whether a short smoothing layer on `pcr_oi_all` improves IS without breaking the test-period edge.
- Main lever:
  Add a 5-day mean before the rank.

```text
group_rank(ts_rank(ts_mean(pcr_oi_all, 5), 20), industry)
```

## Variant 2

- Goal:
  Test whether heavier smoothing stabilizes the signal more than the 5-day version.
- Main lever:
  Add a 20-day mean before the rank.

```text
group_rank(ts_rank(ts_mean(pcr_oi_all, 20), 20), industry)
```

## Variant 3

- Goal:
  Test whether a slower history window improves the balance between IS and TEST.
- Main lever:
  Extend the rank window from `20` to `60`.

```text
group_rank(ts_rank(pcr_oi_all, 60), industry)
```

## Variant 4

- Goal:
  Test whether a tighter grouping frame helps the sparse options signal.
- Main lever:
  Swap `industry` for `subindustry`.

```text
group_rank(ts_rank(pcr_oi_all, 20), subindustry)
```

## Current Live Probe

- Simulation 17 currently shows the direct-rank baseline above.
- IS summary:
  `Sharpe 0.19 / Fitness 0.03 / Turnover 26.81% / Returns 0.54% / Drawdown 6.89% / Margin 0.41‱`
- TEST summary:
  `Sharpe 1.32 / Fitness 0.44 / Turnover 28.60% / Returns 3.15% / Drawdown 1.32% / Margin 2.20‱`
- No visible `Check Submission` evidence or non-null `subuniverse_pass` appeared in the session, and `Submit Alpha` stayed disabled.

## Variant 1 Update

- The first smoothing probe replaced the raw field with a 5-day mean:

```text
group_rank(ts_rank(ts_mean(pcr_oi_all, 5), 20), industry)
```

- IS summary:
  `Sharpe -0.15 / Fitness -0.02 / Turnover 20.55% / Returns -0.42% / Drawdown 9.70% / Margin -0.41‱`
- TEST summary:
  `Sharpe -1.52 / Fitness -0.64 / Turnover 19.98% / Returns -3.51% / Drawdown 4.19% / Margin -3.51‱`
- This probe broke both IS and TEST, so the branch is now a kill rather than a keep.

## Expected First Failure

- Sharpe:
  The gap between IS and TEST suggests the branch may be too regime-dependent.
- Fitness:
  IS Fitness is still far from candidate quality.
- Turnover:
  The direct-rank baseline is costly enough that any added smoothing should be checked carefully.
- Weight:
  Options coverage may still concentrate the active book if the signal is too sparse.
- Sub-universe:
  This remains a structural risk until official submission-style evidence appears.
- Self-correlation:
  Unknown until real check evidence exists.

## Optimization Order

1. Test light smoothing first, because it is the cheapest way to see whether the weak IS readout is mostly noise.
2. If smoothing fails, test the slower `60`-day rank window next.
3. If the signal still looks unstable, tighten the grouping axis with `subindustry`.
4. If none of the variants improves IS materially, kill this branch and return to a stronger family.

## Next Simulation Batch

- Planned batch:
  none.
- Backup branch:
  keep the direct-rank baseline archived as an exploratory control and move on to a stronger family instead of polishing this options line further.

## Decision

- Kill the `pcr_oi_all` direct-rank options branch.
- Keep the baseline capture as a local lesson on how a promising TEST view can still collapse on IS.
- Return to a stronger family or a different forum-backed template rather than spending more sims on this lane.

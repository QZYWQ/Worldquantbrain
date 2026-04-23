# Fundamental / Model Slow Ratio Equity / Cap Structural Follow-up

## Metadata

- Date: `2026-04-23`
- Topic: `fundamental_model_slow_ratio_equity_cap_structural_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`
  - `./runs/expression-families/2026-04-23-fundamental-model-slow-ratio-equity-cap-follow-up.md`
  - `./runs/simulation-captures/2026-04-23-fundamental-model-slow-ratio-equity-cap-batch-11.json`

## Hypothesis

The live `shareholders_equity_total_2 / cap` branch is still the best accessible slow-ratio family on this account, but the current `industry 90d` anchor fails the full-IS `LOW_SHARPE` and `LOW_FITNESS` gates. The next valid move is structural, not another near-duplicate window sweep: test whether a simpler cross-sectional form or a slower smoothed ratio can lift full-IS robustness while staying inside the same forum-backed slow-ratio template family.

## Confirmed Inputs

- confirmed usable numerator: `shareholders_equity_total_2`
- confirmed usable sibling numerator: `total_assets_amount`
- confirmed denominator: `cap`
- confirmed grouping: `industry`, `subindustry`
- confirmed live anchor:
  `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)`
- confirmed current blockers from official API:
  `LOW_SHARPE`, `LOW_FITNESS`, `SELF_CORRELATION`

## Baseline Expression

```text
ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)
```

## Variant 1

- Goal:
  Test the KB-backed direct cross-sectional ratio form instead of the 90d history rank.
- Main lever:
  Remove the outer `ts_rank`, following the same family shape as `group_rank(net_income_annual / cap, industry)`.

```text
group_rank(shareholders_equity_total_2 / cap, industry)
```

## Variant 2

- Goal:
  Slow the ratio itself before ranking so the branch behaves more like the classic slow fundamental template.
- Main lever:
  Add `ts_mean(..., 63)` before the group rank and restore the long outer history rank.

```text
ts_rank(group_rank(ts_mean(shareholders_equity_total_2 / cap, 63), industry), 252)
```

## Variant 3

- Goal:
  Check whether a slightly slower smoother is more robust than the 63d smoother.
- Main lever:
  Replace the `63` smoother with `90`.

```text
ts_rank(group_rank(ts_mean(shareholders_equity_total_2 / cap, 90), industry), 252)
```

## Variant 4

- Goal:
  Keep the slower smoother but remove the outer history rank to reduce path dependence.
- Main lever:
  Use a simple smoothed cross-sectional form.

```text
group_rank(ts_mean(shareholders_equity_total_2 / cap, 63), industry)
```

## Variant 5

- Goal:
  Keep the already verified grouping control in the structure set so group mutations do not drift away from live evidence.
- Main lever:
  Swap `industry` for `subindustry` while keeping the current live shape.

```text
ts_rank(group_rank(shareholders_equity_total_2 / cap, subindustry), 90)
```

## Optimization Order

1. Compare direct cross-sectional vs smoothed-history variants before changing numerators again.
2. Treat `industry` as the default group and `subindustry` only as a structural control.
3. Favor `63 / 84 / 90 / 126 / 252` windows if the miner expands the smoother/history frames.
4. Keep the sibling `total_assets_amount / cap` lane out of the main branch unless a structural variant clearly dominates the equity numerator.

## Next Simulation Batch

- Baseline:
  `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)`
- Variant 1:
  `group_rank(shareholders_equity_total_2 / cap, industry)`
- Variant 2:
  `ts_rank(group_rank(ts_mean(shareholders_equity_total_2 / cap, 63), industry), 252)`
- Variant 3:
  `ts_rank(group_rank(ts_mean(shareholders_equity_total_2 / cap, 90), industry), 252)`
- Variant 4:
  `group_rank(ts_mean(shareholders_equity_total_2 / cap, 63), industry)`

## Live Evidence

- `group_rank(ts_mean(shareholders_equity_total_2 / cap, 84), industry)`
  - simulation `UmHBJ61G565b75d8EbL7Ij` -> alpha `2rn6NegP`
  - full-IS `Sharpe 0.34 / Fitness 0.15`
  - exact failures: `LOW_SHARPE`, `LOW_FITNESS`, `LOW_SUB_UNIVERSE_SHARPE`
  - `SELF_CORRELATION`: `PENDING`
- `ts_rank(group_rank(ts_mean(shareholders_equity_total_2 / cap, 63), industry), 252)`
  - simulation `29fGhsbgU4GJaGPbejr4pqK` -> alpha `akWz1Z05`
  - full-IS `Sharpe 0.18 / Fitness 0.06`
  - exact failures: `LOW_SHARPE`, `LOW_FITNESS`, `LOW_SUB_UNIVERSE_SHARPE`
  - shown-test-period card improved to `Sharpe 1.29 / Fitness 1.07`, but this did not carry into the full-IS gates
  - `SELF_CORRELATION`: `PENDING`

## Decision

- Kill the structural smoothing/simple branch tested in this note.
- Keep the broader `shareholders_equity_total_2 / cap` family in `branch` only because the earlier raw-ratio `industry 90d` anchor still dominates these follow-ups on official evidence.
- Do not continue official testing from this structural note unless a materially different same-family template appears from local mining or fresh KB evidence.

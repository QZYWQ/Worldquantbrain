# 2026-04-25 Option Breakeven 30 Intake Decision

## Conclusion

The project is not blocked by a lack of expression mutations. It is blocked by family intake quality: too many candidate lanes were being treated as if they were still open after the evidence had already frozen or killed them.

For the next research hour, the best live candidate source is `option_breakeven_30`.

## Why This Source Wins

- The official Data Explorer page confirms `option_breakeven_30` exists in `USA / D1 / TOP3000`.
- The field is a direct Options Analytics matrix, so it is economically distinct from the frozen analyst, social-media, and model-rerating lanes.
- Coverage is good enough for a first probe: `71%` coverage and `100%` date coverage.
- Crowding is acceptable for a first batch: `384` visible alphas.
- The source is cleaner than the social-media lanes and less crowded than the call-only sibling set.

## Why Not The Other Nearby Lanes

- `socialmedia12` is frozen and explicitly closed.
- `socialmedia8` is frozen after the first official batch and should not be reopened on sign, lookback, smoothing, or group tweaks.
- `put_breakeven_60` is frozen for the current budget after the first batch.
- `call_breakeven_60` has already been pushed through a live recheck and later freeze memo; it is not the best next-hour use of budget.
- `anl4_af_eps_value` / actual-EPS style ideas are strong but the close-ratio family has already been frozen on self-correlation grounds.

## Root Cause Of The Family-Finding Problem

The current project skeleton is better at triage than at source selection.

What it does well:

- preserves frozen / killed memory
- blocks cosmetic variants from being treated as new families
- carries field-readiness, contract, evidence, and allocator gates

What still leaks:

- source ranking can still surface near-neighbors of already-frozen lanes
- a family can look "new" even when the only change is a better-looking restatement of the same mechanism
- the project still needs to bias harder toward sources that are officially visible, economically distinct, and branchable before the first batch

## Next Minimal Batch Shape

- Baseline: `group_rank(ts_rank(option_breakeven_30 / close, 20), sector)`
- Sign control: `-group_rank(ts_rank(option_breakeven_30 / close, 20), sector)`
- Sibling control: `group_rank(ts_rank(option_breakeven_90 / close, 20), sector)`
- Sibling sign control: `-group_rank(ts_rank(option_breakeven_90 / close, 20), sector)`

## Decision

- Continue.
- Use `option_breakeven_30` as the next family source.
- If the baseline or sibling comes back structurally weak, freeze immediately and rotate.

## Evidence

- `runs/field-search-packs/2026-04-25-option-breakeven-30.md`
- `runs/expression-families/2026-04-25-option-breakeven-30.md`
- Official Data Explorer page:
  - `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_30?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Official Data Explorer search results:
  - `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=call%20breakeven&universe=TOP3000`
  - `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=option%20breakeven&universe=TOP3000`

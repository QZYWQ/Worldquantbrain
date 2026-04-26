# 2026-04-25 Option Breakeven 30 Live First Batch

## Decision

- Freeze `option_breakeven_30` for the current budget.
- Rotate to the next fresh source instead of polishing this options-consensus lane further.
- Do not reopen this family with sign flips, lookbacks, smoothing, or group-axis tweaks.

## Official Evidence

- Field search pack: `runs/field-search-packs/2026-04-25-option-breakeven-30.md`
- Expression family: `runs/expression-families/2026-04-25-option-breakeven-30.md`
- Simulation capture: `runs/simulation-captures/2026-04-25-option-breakeven-30-batch-01.json`
- Official Data Explorer field pages:
  - `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_30?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
  - `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_90?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`

## Field Facts

- `option_breakeven_30`
  - dataset/category: `Options Analytics`
  - type: `Matrix`
  - coverage: `71%`
  - date coverage: `100%`
  - visible alphas: `384`
- `option_breakeven_90`
  - dataset/category: `Options Analytics`
  - type: `Matrix`
  - coverage: `71%`
  - date coverage: `100%`
  - visible alphas: `325`

## Batch 01 Results

- Baseline `Jj5a1Okj`
  - Expression: `group_rank(ts_rank(option_breakeven_30 / close, 20), sector)`
  - IS: `Sharpe 1.48`, `Fitness 0.54`, `Turnover 38.01%`, `Returns 5.01%`
  - TEST: `Sharpe 2.25`, `Fitness 0.82`
  - Checks: `LOW_SHARPE=PASS`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Sign flip `pw1bpv0g`
  - Expression: `-group_rank(ts_rank(option_breakeven_30 / close, 20), sector)`
  - IS: `Sharpe -1.48`, `Fitness -0.54`, `Turnover 38.01%`, `Returns -5.01%`
  - TEST: `Sharpe -2.25`, `Fitness -0.82`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- 90d sibling `LLlowWaM`
  - Expression: `group_rank(ts_rank(option_breakeven_90 / close, 20), sector)`
  - IS: `Sharpe 1.22`, `Fitness 0.49`, `Turnover 35.55%`, `Returns 5.67%`
  - TEST: `Sharpe 1.99`, `Fitness 0.77`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- 90d sign flip `Gr3j75V3`
  - Expression: `-group_rank(ts_rank(option_breakeven_90 / close, 20), sector)`
  - IS: `Sharpe -1.22`, `Fitness -0.49`, `Turnover 35.55%`, `Returns -5.67%`
  - TEST: `Sharpe -1.99`, `Fitness -0.77`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`

## Why Freeze

- The only positive control is the 30d baseline, and it still fails both `LOW_FITNESS` and `CONCENTRATED_WEIGHT`.
- The 90d sibling softens turnover and keeps sub-universe coverage cleaner, but it gives back too much Sharpe/Fitness.
- Both sign-flip controls are pure mirror images; they do not reveal a hidden reverse edge.
- This is a clean freeze, not a near-pass.

## Next Step

- Rotate to `option4` open-interest / volatility-spread branch after fresh official field verification.
- Do not return to `option_breakeven_30` unless a genuinely new structural idea appears.

## Status

- `freeze`
- `rotate`

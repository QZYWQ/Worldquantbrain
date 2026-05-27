# FND6 Capxy Cap Subindustry Expression Family

## Metadata

- Date: `2026-05-03`
- Topic: `fnd6_capxy_cap_subindustry`
- Source: user screenshot showing `group_rank(fnd6_capxy/cap, subindustry)`
- Region: `USA` assumed; verify on official BRAIN
- Universe: `TOP3000` assumed; verify on official BRAIN
- Delay: `1` assumed; verify on official BRAIN

## Hypothesis

Higher capex intensity relative to capitalization may identify companies investing more heavily than direct subindustry peers. If that investment is productive, the market may underreact and the stock may trend upward over a slow horizon.

## Interpretation

```text
group_rank(fnd6_capxy / cap, subindustry)
```

- `fnd6_capxy / cap` is a size-normalized capital-spending intensity ratio, assuming `fnd6_capxy` is a capex-related fundamental field and `cap` is the capitalization denominator.
- `group_rank(..., subindustry)` compares firms only against close business-model peers, which is important because capital intensity differs structurally across sectors.
- The expression has no explicit time-series transform. It is mostly a cross-sectional level signal, likely slow-moving if the numerator is quarterly or annual.

## Project Context

- This exact `fnd6_capxy` expression is not found in the existing project artifacts.
- Adjacent capex work exists and is cautionary:
  - `capital_expenditure_amount / close` with `group_rank(ts_rank(..., 84), industry)` produced IS Sharpe `0.75`, Fitness `0.53`, `LOW_SHARPE` fail, and `LOW_FITNESS` fail, then was frozen.
  - `capital_expenditure_amount / total_assets_amount` later showed IS Sharpe `0.43`, Fitness `0.15`, and negative TEST, then was frozen.
- Therefore this family should start as an `S0` / cheap triage lane, not as a polished candidate lane.

## Main Risks

- Sign convention:
  If `fnd6_capxy` is stored as a negative cash-flow outflow, the raw ratio may rank lower capex intensity as better unless sign-corrected.
- Economic sign:
  High capex can mean productive growth, but it can also mean overinvestment, weak free cash flow, or capital-heavy low-return expansion.
- Denominator effects:
  Dividing by `cap` can create small-cap outliers and concentration.
- Update rhythm:
  Fundamental capex fields may update slowly; the raw ratio may be stale and overly dependent on denominator movement.
- Coverage:
  Existing nearby fundamental capex fields had only partial coverage in project notes, so sub-universe risk is real.
- Crowding / correlation:
  The family can overlap with investment, value, growth, and capital-structure factors.

## Required Gate Before Simulation Expansion

Run the New Dataset Intake Gate from the promoted skill rule:

```text
fnd6_capxy
fnd6_capxy != 0 ? 1 : 0
ts_std_dev(fnd6_capxy, N) != 0 ? 1 : 0
abs(fnd6_capxy) > X
ts_median(fnd6_capxy, 1000) > X
X < scale_down(fnd6_capxy) && scale_down(fnd6_capxy) < Y
abs(fnd6_capxy / cap) > X
```

Treat these as field-health diagnostics only. Do not score them as alpha candidates.

## Minimal Simulation Queue

Only run this queue if the field gate confirms availability, usable coverage, and understandable sign convention.

### Baseline

```text
group_rank(fnd6_capxy / cap, subindustry)
```

Purpose: test the screenshot's direct thesis.

### Sign Control

```text
-group_rank(fnd6_capxy / cap, subindustry)
```

Purpose: test whether the economic sign is reversed. If the baseline Sharpe is negative or weak and this is materially better, continue only on the flipped sign.

### History-Relative Control

```text
ts_rank(group_rank(fnd6_capxy / cap, subindustry), 252)
```

Purpose: test whether a firm's current capex intensity is high versus its own recent history after peer ranking.

### Smoothing Control

```text
group_rank(ts_mean(fnd6_capxy / cap, 63), subindustry)
```

Purpose: test whether smoothing the slow fundamental ratio improves stability without killing the signal.

### Grouping Control

```text
group_rank(fnd6_capxy / cap, industry)
```

Purpose: test whether subindustry is too narrow or sparse.

## Decision Rules

- If both baseline and sign control are far below viability, kill instead of tuning lookbacks.
- If baseline is negative and sign control is positive, immediately carry the flipped expression forward and stop polishing the original sign.
- If both signs are weak but the history-relative control improves, treat the signal as a timing / acceleration idea rather than a raw level idea.
- If subindustry fails coverage or concentration while industry survives, move the group axis wider before touching smoothing.
- If official checks later show `LOW_SUB_UNIVERSE_SHARPE`, do not create a candidate batch unless a distinct normalization or field source fixes it.

## Submission Posture

- Current posture: exploratory only.
- Not submission-ready.
- No real Sharpe, Fitness, Turnover, Weight, Sub-universe, Self-correlation, or Test Period result exists for this exact expression in the project.

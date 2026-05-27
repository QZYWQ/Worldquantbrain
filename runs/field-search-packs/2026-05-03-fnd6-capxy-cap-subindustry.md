# FND6 Capxy Cap Subindustry Field Search Pack

## Metadata

- Date: `2026-05-03`
- Topic: `fnd6_capxy_cap_subindustry`
- Region: `USA` assumed; verify on official BRAIN
- Universe: `TOP3000` assumed; verify on official BRAIN
- Delay: `1` assumed; verify on official BRAIN

## Hypothesis

Within each subindustry, companies with higher capital-expenditure intensity relative to capitalization may be investing more aggressively in future capacity or growth, so their stocks may rank higher over a slow horizon.

## Why This Could Matter

- `fnd6_capxy / cap` is an interpretable reinvestment-intensity ratio if `fnd6_capxy` is a capital-expenditure amount and `cap` is the platform capitalization denominator.
- `group_rank(..., subindustry)` is the right first structural instinct because raw capex intensity differs heavily by business model; cross-industry comparisons are noisy.
- The project already has adjacent negative evidence: a different capex branch, `capital_expenditure_amount / close`, produced only IS Sharpe `0.75` and Fitness `0.53` and was frozen. This does not kill `fnd6_capxy / cap`, but it argues for a cheap diagnostic gate before spending more budget.
- Capex can have two economic signs: productive reinvestment can be positive, but overinvestment and cash-flow drag can be negative. A sign control is mandatory.

## Data Explorer Search Terms

- Primary terms: `fnd6_capxy`, `capital expenditures`, `capex`, `capital expenditure`
- Sibling terms: `fnd6_capxs`, `capex`, `capital_expenditure_amount`, `invested capital`
- Denominator terms: `cap`, `market cap`, `capitalization`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `fnd6_capxy` | likely `fundamental6`; verify | Screenshot numerator; likely capex / capital-spending related | Unknown; must check Data Explorer and diagnostic simulations | Unknown |
| `cap` | platform core field; verify exact meaning | Needed to normalize capex by size / capitalization | Usually available, but exact denominator behavior must be checked | Common denominator, likely crowded |
| `fnd6_capxs` | `fundamental6`; prior project control | Nearby capex sibling from earlier project search | Prior project note showed `50%` coverage in `USA / D1 / TOP3000`; recheck before reuse | Prior project note showed less crowded than broad `capex` |
| `capex` | `fundamental6`; prior fallback | Broad capex fallback, not preferred | Prior project note showed `50%` coverage in `USA / D1 / TOP3000`; recheck before reuse | Prior project note showed very crowded |
| `capital_expenditure_amount` | `analyst4`; prior adjacent branch | Analyst estimate capex sibling, already tested in a different normalization | Prior project note showed `75.24%` coverage, but this is not the screenshot field | Low-crowding historically, but prior expression failed IS |

## Coverage And Quality Checks

- Coverage:
  Unknown for `fnd6_capxy`; must be measured before family expansion.
- Missingness:
  Fundamental capex fields can be sparse or stale; record non-zero coverage separately from raw coverage.
- Region / delay compatibility:
  Unknown from the screenshot; verify the exact account / region / delay setting.
- Field type:
  Unknown from the screenshot; if `fnd6_capxy` is an annual or quarterly fundamental field, expect slow update rhythm.
- Sign convention:
  Critical. If the field is recorded as cash outflow, higher raw values may mean less investment unless sign is corrected.

## New Dataset Quick Evaluation

Run these as diagnostic simulations with `None` neutralization and decay `0`.
Interpret `Long Count` + `Short Count` against the selected universe size; do not treat these diagnostics as alpha candidates.

| Diagnostic | Expression | What to inspect |
| --- | --- | --- |
| Raw coverage | `fnd6_capxy` | Approximate numerator coverage |
| Non-zero coverage | `fnd6_capxy != 0 ? 1 : 0` | Average daily non-zero numerator availability |
| Update frequency | `ts_std_dev(fnd6_capxy, N) != 0 ? 1 : 0` | Whether updates behave like annual, quarterly, monthly, or stale data |
| Bounds | `abs(fnd6_capxy) > X` | Whether the field is signed, positive-only, or extreme-heavy |
| Long-window center | `ts_median(fnd6_capxy, 1000) > X` | Long-window location and sign convention |
| Distribution band | `X < scale_down(fnd6_capxy) && scale_down(fnd6_capxy) < Y` | Whether most observations cluster in a narrow band |
| Ratio sanity | `abs(fnd6_capxy / cap) > X` | Whether small-cap denominator effects create outliers |

## Baseline Expression Ideas

1. `group_rank(fnd6_capxy / cap, subindustry)`
2. `-group_rank(fnd6_capxy / cap, subindustry)`
3. `ts_rank(group_rank(fnd6_capxy / cap, subindustry), 252)`
4. `group_rank(ts_mean(fnd6_capxy / cap, 63), subindustry)`
5. `group_rank(fnd6_capxy / cap, industry)`

## Likely First Failure

- Sharpe:
  Sign ambiguity is the first risk; capex intensity can mean growth investment or wasteful overinvestment.
- Fitness:
  Slow update rhythm may keep turnover low but returns weak.
- Turnover:
  Probably low unless the denominator `cap` injects price-driven movement.
- Weight:
  Small-cap denominator effects can create concentration.
- Sub-universe:
  Sparse fundamental coverage can fail sub-universe even if the headline ratio looks reasonable.
- Self-correlation:
  Could overlap with existing value, growth, investment, and capital-structure ratios.

## Next Action

- First confirm `fnd6_capxy` and `cap` are available in the current account / region / delay.
- Run the New Dataset Quick Evaluation diagnostics before alpha variants.
- If coverage and sign convention are acceptable, simulate the baseline and sign flip together.
- Stop same-axis polishing if both signs are weak, because the adjacent capex family already has weak project evidence.

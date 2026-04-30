# Two Alpha Rescue Project Lessons

## Metadata
- Date: 2026-04-30
- Scope: project-level durable learning loop
- Evidence status: based on official `/alphas/{id}/check` evidence already captured in project memos
- Source artifacts:
  - `runs/submission-memos/2026-04-30-sales-estimate-count-decay10-submitted.md`
  - `runs/submission-memos/2026-04-30-llgowzmn-pv-range-close-position-ready.md`
  - `runs/simulation-captures/2026-04-30-unsubmitted-near-miss-filter.md`
  - `runs/simulation-captures/2026-04-30-unsubmitted-followup-after-llgowzmn.json`

## Executive Lesson

Two different rescue paths worked on 2026-04-30:

1. A low-turnover analyst-count family was rescued by simplifying the structure and shortening the decay window.
2. A high-turnover price-volume range-position family was rescued by increasing the measurement window and smoothing window to stabilize sub-universe behavior.

The common lesson is not "add more operators." The useful move was to identify the dominant failing check and change one structural lever that directly targeted it.

## Alpha 1: Analyst Count Coverage Signal

### Final Alpha

```text
rank(ts_decay_linear(sales_estimate_count, 10))
```

- Alpha ID: `A1g6AlWg`
- Status: user-reported submitted
- Family: analyst coverage / sales estimate count
- Settings: USA / TOP3000 / Delay 1 / Industry neutralization / Fast Expression

### Official Pre-Submission Evidence

- Sharpe: `1.70`
- Fitness: `1.03`
- Returns: `4.58%`
- Turnover: `3.49%`
- Drawdown: `2.71%`
- Margin: `0.002626`
- Sub-universe Sharpe: PASS, `0.91 / 0.74`
- Self-correlation: PASS, `0.0771 / 0.7`
- Weight concentration: PASS
- Competition match: PASS

### What Worked

The successful repair was not `group_rank(ts_decay_linear(sales_estimate_count, 20), industry)`. That version stayed close but failed Fitness at `0.94 / 1.00`.

The better repair shortened the decay window and used plain cross-sectional rank:

```text
rank(ts_decay_linear(sales_estimate_count, 10))
```

This kept turnover low while lifting Fitness over the official floor.

### Carry-Forward Rule

For sparse or slow analyst-coverage count fields, try the shortest economically plausible decay window before adding group transforms. A plain `rank(ts_decay_linear(field, 10))` style control can be stronger than a longer window plus group rank when the failure is Fitness rather than concentration.

### Stop Boundary

The submitted alpha now represents the `sales_estimate_count` family. Do not keep polishing near-neighbor variants such as:

- `rank(ts_decay_linear(sales_estimate_count, 5))`
- `rank(ts_decay_linear(sales_estimate_count, 20))`
- `group_rank(ts_decay_linear(sales_estimate_count, 20), industry)`
- cosmetic delta or group-axis variants

Use this family for post-submit monitoring only unless fresh official evidence shows a real submission problem.

## Alpha 2: Price-Volume Range Close Position

### Final Alpha

```text
group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 30)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 30))) * (1 - rank(ts_std_dev(returns, 30))), 12), industry)
```

- Alpha ID: `LLgOWZmn`
- Status: `UNSUBMITTED` at capture time; user starred / protected it in the UI
- Family: price-volume range close position with volatility filter
- Settings: USA / TOP3000 / Delay 1 / Industry neutralization / Fast Expression / Truncation 0.08

### Official Check Evidence

- Sharpe: `2.18`
- Fitness: `1.21`
- Returns: `14.59%`
- Turnover: `47.46%`
- Drawdown: `4.22%`
- Margin: `0.000615`
- Sub-universe Sharpe: PASS, `0.99 / 0.94`
- Self-correlation: PASS, `0.6392 / 0.7`
- Weight concentration: PASS
- Competition match: PASS, Challenge and IQC2026S1

### Starting Near-Miss

```text
group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 20)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 20))) * (1 - rank(ts_std_dev(returns, 20))), 9), industry)
```

- Alpha ID: `KPXaX5Yz`
- Sharpe: `2.05`
- Fitness: `1.02`
- Returns: `13.63%`
- Turnover: `54.57%`
- Failed check: Sub-universe Sharpe `0.87 / 0.89`

### What Worked

The successful repair changed one coherent stability axis:

- range / volatility lookback: `20 -> 30`
- decay smoothing: `9 -> 12`

That repair reduced turnover and raised sub-universe Sharpe enough to pass without changing the core thesis.

### Carry-Forward Rule

For price-volume range-position alphas that already pass Sharpe and Fitness but fail Sub-universe narrowly, first try a moderate stability repair: lengthen the range and volatility windows together, then slightly increase decay smoothing. This targets robustness more directly than adding unrelated gates or neutralization churn.

### Protection Boundary

`LLgOWZmn` is the protected version of this family. Do not delete, hide, or overwrite it during future cleanup.

Do not submit multiple close siblings from the same family. The self-correlation pass margin is real but not wide: `0.6392 / 0.7`. Same-family siblings such as `KPXaX5Yz`, `vRegzXqG`, `E5gJYAqL`, `KPXa8Aog`, and `KPXaq0Nx` should be treated as redundant after `LLgOWZmn`.

## Batch Triage Lesson

The follow-up scan after `LLgOWZmn` found:

- `887` visible unsubmitted alphas
- `14` pre-candidates
- `12` checked near-misses
- `0` additional fully passing non-conflicting candidates

This matters because the correct decision after finding a passing rescued variant was to stop same-family mining, not to keep searching the same pool for cosmetic siblings.

## Reusable Heuristics

- Rescue near-misses by failing check, not by random operator addition.
- When Fitness is just below the floor on a slow count field, simplify and shorten before grouping.
- When Sub-universe is narrowly low on a price-volume family, stabilize the core measurement window before changing thesis.
- Once a family has one clean passing representative, lock that representative and suppress near-neighbor submissions.
- A pending or passing self-correlation check is not enough context by itself; compare against the active submitted family list before marking anything as a candidate.

## Next-Session Use

Before cleaning unsubmitted alphas or generating more same-family variants:

1. Protect `A1g6AlWg` as submitted analyst-count representative.
2. Protect `LLgOWZmn` as the current price-volume range-position candidate.
3. Exclude `sales_estimate_count` siblings from new submission work.
4. Exclude `range_close_position` siblings unless `LLgOWZmn` fails fresh official evidence.
5. Open a genuinely distinct family for the next research slot.

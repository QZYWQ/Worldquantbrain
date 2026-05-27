# Financing Pressure S2 Field Search Pack

## Research Hypothesis

Balance-sheet financing pressure should have predictive value when compared within industries:

- high debt burden can constrain future equity upside
- rising current/accrued liabilities can signal near-term obligation pressure
- maturity walls and issuance costs can proxy refinancing stress
- tax payable and deferred tax liability fields may capture accounting-quality pressure

## Current Evidence Boundary

This pack uses project-captured official/API evidence from prior runs. It does not claim a new field is currently available unless it appeared in prior official API or simulation artifacts.

Primary source artifacts:

- `runs/overnight-mining/2026-05-23-financing-pressure-24h/field-search-snapshot.json`
- `runs/overnight-mining/2026-05-23-financing-pressure-24h/report.md`
- `runs/overnight-mining/2026-05-23-financing-pressure-24h/upgrade-potential-candidates.json`
- `runs/research-queues/2026-05-24-financing-pressure-upgrade-favorite/report.md`

## Field Shortlist

| Field | Mechanism | Prior coverage / crowding evidence | Current use |
| --- | --- | --- | --- |
| `debt_carrying_value` | debt burden level | coverage `0.6720`, user count `1`, alpha count `1` in prior snapshot | primary anchor |
| `current_accrued_liabilities` | current obligation pressure | coverage `0.4343`, user count `2`, alpha count `2` | pressure-change rescue |
| `current_accrued_liabilities_total` | current obligation alternate | coverage `0.4086`, user count `1`, alpha count `1` | composite branch |
| `accrued_liabilities_total` | broader accrued obligations | coverage `0.4400`, user count `16`, alpha count `20` | debt+obligation confirmation |
| `debt_maturities_repayments_year2` | maturity wall pressure | coverage `0.5606`, user count `13`, alpha count `13` | mechanism branch |
| `debt_issuance_costs_total` | issuance cost / financing friction | coverage `0.4753`, user count `0`, alpha count `0` | field branch |
| `taxes_payable_total_value` | near-term tax payable burden | coverage `0.5559`, user count `0`, alpha count `0` | field branch |
| `deferred_tax_liability_goodwill_intangibles` | accounting liability quality | coverage `0.4504`, user count `0`, alpha count `0` | exploratory branch |

## Field Health Rules For This Run

Before treating any newly strong expression as candidate-grade, confirm:

- coverage is not concentrated in too few stocks
- `Long Count` and `Short Count` remain healthy
- raw field diagnostics are not being mistaken for alpha candidates
- field updates are not too stale for the chosen horizon
- sparse fields are not only passing through concentration

Diagnostic shapes, if needed:

```text
<field>
<field> != 0 ? 1 : 0
ts_std_dev(<field>, 22) != 0 ? 1 : 0
ts_std_dev(<field>, 66) != 0 ? 1 : 0
scale_down(<field>)
```

Run diagnostics with:

- neutralization `None`
- decay `0`
- `nanHandling` off when checking raw coverage behavior

## Expression Entry Points

Level pressure:

```text
group_rank(reverse(ts_rank(divide(clean(field), add(abs(clean(denom)), 1)), N)), group)
```

Change in pressure:

```text
group_rank(reverse(ts_zscore(ts_delta(ts_mean(divide(clean(field), add(abs(clean(assets)), 1)), smooth), delta), zwin)), group)
```

Mechanism confirmation:

```text
group_rank(w1 * reverse(ts_rank(field_a / assets, 252)) + w2 * reverse(ts_rank(field_b / assets, 252)), group)
```

where:

```text
clean(x) = winsorize(ts_backfill(x, 252), std=4)
```

## Field Rejection Rules

- If a field returns `unknown variable`, mark it blocked and suppress all same-field variants in the current run.
- If a field only works as a raw field-health diagnostic but fails all alpha expressions, keep it as data evidence, not a candidate.
- If a field branch only improves by changing constants but not mechanism, do not count it as a low-correlation branch.

## Next Check

The next official action is simulation/check only through:

`runs/overnight-mining/2026-05-24-financing-pressure-s2-24h/launch_24h.sh`

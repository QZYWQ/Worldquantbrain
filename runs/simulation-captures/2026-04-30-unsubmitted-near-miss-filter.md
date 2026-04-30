# Unsubmitted Near-Miss Filter

Date: 2026-04-30

## Official Scan Boundary

- Source: official `/users/self/alphas` list from the logged-in WorldQuant BRAIN session.
- Total alpha objects: 892
- Submitted / active: 5
- Visible unsubmitted: 887
- Unsubmitted with exactly one near-threshold failed check: 15
- Fresh `/check` was requested for the near-miss set. For still-failing alphas, `SELF_CORRELATION` generally remained `PENDING`, so conflict judgment uses submitted-family exclusion plus known rescued variants where available.

## Submitted Families To Avoid

| Alpha ID | Family | Expression |
| --- | --- | --- |
| `A1g6AlWg` | analyst count | `rank(ts_decay_linear(sales_estimate_count, 10))` |
| `E5g7vMjJ` | close/volume reversal-correlation | `group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 5), subindustry)` |
| `qMmpvp8v` | short-horizon returns reversal | `-ts_mean(returns, 5)` |
| `E5repQ81` | analyst EPS / price | `group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)` |
| `d5l07rpX` | EPS / price | `group_rank(ts_rank(earnings_per_share_average/close, 120), industry)` |

## Keep

### Primary Rescue Family: Price-Volume Range Close Position

Near-miss seed:

```text
group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 20)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 20))) * (1 - rank(ts_std_dev(returns, 20))), 9), industry)
```

- Alpha ID: `KPXaX5Yz`
- Failing condition: `LOW_SUB_UNIVERSE_SHARPE`, value `0.87`, limit `0.89`
- Metrics: Sharpe `2.05`, Fitness `1.02`, Returns `13.63%`, Turnover `54.57%`
- Conflict posture: not identical to submitted price-volume lines; rescued variant has official `SELF_CORRELATION=PASS`.

Rescued version already tested:

```text
group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 30)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 30))) * (1 - rank(ts_std_dev(returns, 30))), 12), industry)
```

- Alpha ID: `LLgOWZmn`
- Official checks: all PASS
- Self-correlation: PASS, value `0.6392`, limit `0.7`
- Sub-universe Sharpe: PASS, value `0.99`, limit `0.94`
- Metrics: Sharpe `2.18`, Fitness `1.21`, Returns `14.59%`, Turnover `47.46%`

Same-family near-miss siblings:

| Alpha ID | Failed Check | Value / Limit | Note |
| --- | --- | ---: | --- |
| `E5gJYAqL` | `LOW_SUB_UNIVERSE_SHARPE` | `0.86 / 0.89` | same family; lower priority than `KPXaX5Yz` |
| `vRegzXqG` | `LOW_FITNESS` | `0.99 / 1.00` | same family; likely fixable, but redundant after `LLgOWZmn` |
| `KPXa8Aog` | `LOW_FITNESS` | `0.96 / 1.00` | same family; less attractive |
| `KPXaq0Nx` | `LOW_FITNESS` | `0.95 / 1.00` | same family; less attractive |

## Secondary, Lower Priority

### Call Breakeven 60

Distinct from the 5 submitted alphas, but lower rescue probability because this family already has a stop memo after several repair probes.

| Alpha ID | Expression | Failed Check | Value / Limit |
| --- | --- | --- | ---: |
| `A1OX3kKE` | `group_rank(ts_rank(call_breakeven_60 / close, 10), sector)` | `LOW_FITNESS` | `0.92 / 1.00` |
| `kqLp3jJz` | `group_rank(ts_rank(ts_decay_linear(call_breakeven_60 / close, 2), 10), sector)` | `LOW_FITNESS` | `0.89 / 1.00` |
| `zqJ79qPX` | `group_rank(ts_rank(call_breakeven_60 / close, 8), sector)` | `LOW_FITNESS` | `0.88 / 1.00` |

## Exclude

| Alpha ID | Reason |
| --- | --- |
| `xAPMogmJ` | same `sales_estimate_count` family as submitted `A1g6AlWg` |
| `QP2exOr5` | same `sales_estimate_count` family as submitted `A1g6AlWg` |
| `9qA2nmmq` | EPS / analyst family overlaps submitted `E5repQ81` and `d5l07rpX` |
| `xAP6Y5zm` | close/volume correlation sibling overlaps submitted `E5g7vMjJ` |
| `2raPMQox` | same range-close family but worse than the already rescued `LLgOWZmn`; Sub-universe gap is not small enough |
| `88a1kA6W` | simplified range-close branch; same lane and weaker than `LLgOWZmn` |
| `rKJXX1ej` | simplified range-close branch; same lane and weaker than `LLgOWZmn` |

## Decision

- Best current non-conflicting rescue target is the range-close-position family, but use the already rescued `LLgOWZmn` expression rather than the failing seed.
- Do not spend more time on `sales_estimate_count` siblings; that family is already represented by a submitted alpha.
- Keep call-breakeven as a distant backup only if a new options-slot is needed, not as the next best use of budget.

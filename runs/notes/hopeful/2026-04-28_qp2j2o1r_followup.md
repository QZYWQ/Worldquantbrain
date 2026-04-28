# QP2J2o1r Follow-Up

## Original Hopeful Alpha

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 20)), 5), subindustry)
```

## Metrics

- sharpe: 1.13
- fitness: 0.64
- turnover: 0.2211
- margin: 0.000647
- drawdown: 0.0406
- returns: 0.0715

## Judgment

- hopeful: yes
- candidate: no

## Main Issues

- Sharpe is below 1.25.
- Fitness is below 0.8.

## Strengths

- Turnover is controlled below 0.3.
- Returns and margin are positive.
- Drawdown is low.

## Follow-Up Variant Directions

- Adjust `ts_delta` window: 5 / 10 / 20.
- Adjust `ts_corr` window: 10 / 20 / 60.
- Adjust decay window: 3 / 5 / 10.
- Adjust neutralization group: industry / subindustry / sector.
- Target turnover below 0.3 while improving Sharpe and fitness.

## Prepared Manual Variants

1. Longer price delta window:

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 20)) * -rank(ts_corr(rank(close), rank(volume), 20)), 5), subindustry)
```

2. Longer correlation window:

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 60)), 5), subindustry)
```

3. Stronger smoothing:

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 20)), 10), subindustry)
```

# ANL4 Total Assets Flag Submission Memo

Date: 2026-04-30

## Status

- Alpha ID: `Xg2X2jxl`
- Submission status: user-reported submitted.
- Platform post-submit status: not independently rechecked in this memo.
- Role in current portfolio: submitted analyst / fundamental flag representative.

## Submitted Alpha

```text
rank(ts_mean(anl4_totassets_flag, 20))
```

## Settings

- Instrument Type: Equity
- Region: USA
- Universe: TOP3000
- Language: Fast Expression
- Delay: 1
- Decay setting: 0
- Truncation: 0.08
- Neutralization: Industry
- Pasteurization: On
- Max Trade: Off
- Max Position: Off

## Latest Pre-Submission Evidence

Source: official WorldQuant BRAIN API result observed in the live research session before submission.

- Sharpe: `1.30`
- Fitness: `1.30`
- Returns: `12.47%`
- Turnover: `2.41%`
- Drawdown: `14.52%`
- Margin: `0.010339`
- Long Count: `1516`
- Short Count: `264`

Visible checks at capture time:

- `LOW_SHARPE`: PASS, value `1.30`, limit `1.25`
- `LOW_FITNESS`: PASS, value `1.30`, limit `1.0`
- `LOW_TURNOVER`: PASS
- `HIGH_TURNOVER`: PASS
- `CONCENTRATED_WEIGHT`: PASS
- `LOW_SUB_UNIVERSE_SHARPE`: PASS, value `0.75`, limit `0.56`
- `MATCHES_COMPETITION`: PASS
- `SELF_CORRELATION`: PENDING at the pre-submission capture point

## Why This Was The Better Submission Priority

This candidate was preferred over the close-delta / close-volume-correlation candidate because it had a more distinct information source and better robustness margins:

- Information source: analyst / fundamental total-assets flag, not price-volume behavior.
- Fitness: `1.30`, materially above the `1.0` floor.
- Turnover: `2.41%`, much lower than the price-volume correlation candidate's `14.08%`.
- Sub-universe: `0.75 / 0.56`, much wider than the price-volume correlation candidate's exact pass at `0.56 / 0.56`.

## Follow-On Effect

After this alpha was submitted, the price-volume correlation candidate:

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 9), subindustry)
```

failed self-correlation with:

```text
Self-correlation 0.9896 is above cutoff of 0.7 and Sharpe not better by 10.0% or more.
```

This confirmed that the submitted alpha changed the remaining queue's correlation reality. The correct response was to keep the submitted `anl4_totassets_flag` line and stop the later price-volume correlation branch.

## Carry-Forward Rule

When choosing between two near-pass candidates, prioritize the one with:

- a more distinct information source,
- stronger Fitness margin,
- lower turnover,
- wider Sub-universe margin,
- and less dependence on a pending self-correlation result.

After one candidate is submitted, re-evaluate the rest of the queue. The submitted set is now different, so previous `SELF_CORRELATION: PENDING` candidates cannot be treated as unchanged opportunities.

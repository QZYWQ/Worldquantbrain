# Price Volume Corr Self-Corr Stop Memo

Date: 2026-04-30

## Status

- Alpha ID: `zqPX5OkX`
- Current action: stop this candidate for submission.
- Source status: user-reported official Check Submission result.
- Independent recheck in this memo: not performed.

## Affected Alpha

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 9), subindustry)
```

Settings captured before the failed self-correlation check:

- Instrument Type: Equity
- Region: USA
- Universe: TOP3000
- Delay: 1
- Decay setting: 0
- Truncation: 0.08
- Neutralization setting: Industry
- Expression neutralization group: `subindustry`
- Pasteurization: On

## Prior Visible Gate Evidence

From the earlier official API capture:

- Sharpe: `1.30`
- Fitness: `1.04`
- Returns: `8.95%`
- Turnover: `14.08%`
- Drawdown: `7.62%`
- Sub-universe Sharpe: PASS, `0.56 / 0.56`
- Weight concentration: PASS
- Competition match: PASS
- Self-correlation: previously `PENDING`

## New Failed Gate

After the user submitted:

```text
rank(ts_mean(anl4_totassets_flag, 20))
```

the price-volume correlation candidate failed Check Submission:

```text
Self-correlation 0.9896 is above cutoff of 0.7 and Sharpe not better by 10.0% or more.
```

## Decision

- Do not submit `zqPX5OkX`.
- Do not spend more submission budget on close siblings from the same short-horizon close-delta / close-volume-correlation branch.
- Treat small lookback and decay changes as likely redundant unless a future official check shows a materially lower self-correlation path.
- Keep the submitted `rank(ts_mean(anl4_totassets_flag, 20))` line as the valid representative in the current submitted set.

## Reasoning

The formula-level family distinction was real: `zqPX5OkX` is a price-volume technical signal, while `rank(ts_mean(anl4_totassets_flag, 20))` is an analyst / fundamental flag signal. The platform-level submission result is stronger evidence than formula semantics. A self-correlation value of `0.9896` means the realized alpha behavior is almost fully overlapping with the already-submitted set.

Because the value is far above the `0.7` cutoff, this is not a near-miss rescue target. The appropriate response is to stop the branch and rotate to a genuinely different information source or construction.

## Carry-Forward Rule

When a candidate has strong visible checks but self-correlation is still pending, treat it as `near-pass`, not as submit-ready. If a later submission causes the candidate to fail self-correlation above `0.95`, lock the submitted alpha and stop the affected branch rather than trying cosmetic parameter changes.

# LLgOWZmn PV Range Close Position Ready Memo

Date: 2026-04-30

## Status

- Alpha ID: `LLgOWZmn`
- Current platform status: `UNSUBMITTED`
- Stage: `IS`
- Submission action: not executed in this memo.

## Expression

```text
group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 30)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 30))) * (1 - rank(ts_std_dev(returns, 30))), 12), industry)
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

## Fresh Official Check

Source: official `/alphas/LLgOWZmn` and `/alphas/LLgOWZmn/check` on 2026-04-30.

- Sharpe: `2.18`
- Fitness: `1.21`
- Returns: `14.59%`
- Turnover: `47.46%`
- Drawdown: `4.22%`
- Margin: `0.000615`
- Long Count: `1567`
- Short Count: `1570`

Checks:

- `LOW_SHARPE`: PASS, value `2.18`, limit `1.25`
- `LOW_FITNESS`: PASS, value `1.21`, limit `1.0`
- `LOW_TURNOVER`: PASS, value `0.4746`, limit `0.01`
- `HIGH_TURNOVER`: PASS, value `0.4746`, limit `0.7`
- `CONCENTRATED_WEIGHT`: PASS
- `LOW_SUB_UNIVERSE_SHARPE`: PASS, value `0.99`, limit `0.94`
- `SELF_CORRELATION`: PASS, value `0.6392`, limit `0.7`
- `MATCHES_COMPETITION`: PASS, Challenge and IQC2026S1

## Decision

- This is the strongest current non-submitted rescue candidate.
- It is distinct enough from the five active submitted alphas to consider submission, because it uses intraday range/close position plus range and volatility filtering rather than analyst counts, EPS ratios, pure returns reversal, or close-volume correlation.
- Main risk: self-correlation margin is not wide (`0.6392` vs `0.7`), so do not submit multiple close siblings from this same family.
- Recommended action: submit only this best variant if the user confirms the final submission action.

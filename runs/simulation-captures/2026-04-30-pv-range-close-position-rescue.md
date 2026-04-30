# PV Range Close Position Rescue

Date: 2026-04-30

## Settings

- Instrument Type: Equity
- Region: USA
- Universe: TOP3000
- Delay: 1
- Decay setting: 0
- Truncation: 0.08
- Neutralization: Industry
- Pasteurization: On
- Unit Handling: Verify
- NaN Handling: Off
- Period: 2019-01-01 to 2023-12-31
- Max Trade: Off
- Max Position: Off

## Results

| Label | Alpha ID | Sharpe | Fitness | Returns | Turnover | Drawdown | Sub-universe | Self-correlation | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline_decay9_window20 | KPXaX5Yz | 2.05 | 1.02 | 13.63% | 54.57% | 4.55% | FAIL 0.87 / 0.89 | PENDING | reject |
| decay12_window20 | Vk2K1brb | 2.05 | 1.11 | 13.79% | 47.28% | 4.46% | PASS 0.90 / 0.89 | PASS 0.6437 / 0.7 | backup |
| decay15_window20 | 2raPMQox | 1.89 | 1.04 | 12.91% | 42.28% | 5.79% | FAIL 0.74 / 0.82 | PENDING | reject |
| decay12_window30 | LLgOWZmn | 2.18 | 1.21 | 14.59% | 47.46% | 4.22% | PASS 0.99 / 0.94 | PASS 0.6392 / 0.7 | best |

## Best Expression

```text
group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 30)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 30))) * (1 - rank(ts_std_dev(returns, 30))), 12), industry)
```

## Decision

- The family is salvageable.
- Prefer `decay12_window30` over `decay12_window20`.
- Do not use `decay15_window20`; the additional smoothing hurts Sub-universe sharply.
- Self-correlation passes for the two viable variants but is not extremely low, so treat this as a near-submit candidate, not a broad family to keep mutating.

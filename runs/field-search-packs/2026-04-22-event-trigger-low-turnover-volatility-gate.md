# Event Trigger / Low Turnover Volatility Gate Field Search Pack

## Metadata

- Date: `2026-04-22`
- Topic: `event_trigger_low_turnover_volatility_gate`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`
  - official Data Explorer search results for `historical_volatility_20`

## Hypothesis

High-volatility regimes may be the right context for a low-turnover pressure alpha because the spread between `close` and `vwap` matters more when the tape is active.

## Why This Could Matter

- The volume-gate pressure lane is already killed, so the next branch needs a real regime change.
- Forum guidance explicitly suggests `trade_when`-style event alphas and high-volatility gating.
- `historical_volatility_20` gives a slower regime anchor than the earlier price-volume gate.
- `close` and `vwap` keep the pressure leg interpretable.
- `industry` keeps the cross-sectional comparison disciplined.

## Data Explorer Search Terms

- Primary terms: `historical volatility`, `historical_volatility_20`, `returns`, `vwap`, `close`
- Synonyms: `volatility regime`, `rolling std dev`, `price pressure`
- Abbreviations: `ts_std_dev`, `ts_rank`, `adv20`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `historical_volatility_20` | `Volatility Data` | Primary gate or backup signal for the new event regime | Project search pack recorded `70%` coverage and `1634` alphas | Less crowded than the price-volume fields, but sparser |
| `returns` | `Price Volume Data for Equity` | Operator-derived fallback for a volatility gate if the field-based regime is weak | `100%` coverage | Very crowded, but useful as a calculated backup |
| `close` | `Price Volume Data for Equity` | Price-pressure anchor for the signal leg | `100%` coverage | Crowded, so it needs a gate |
| `vwap` | `Price Volume Data for Equity` | Cleaner pressure comparison than raw momentum | `100%` coverage | Crowded, but useful as a normalization anchor |
| `industry` | `Universe / classification` | Cross-sectional grouping for the signal leg | Confirmed in the current session | Helps control hidden common exposure |

## Coverage And Quality Checks

- `historical_volatility_20` is sparse compared with price-volume fields, so the gate should stay simple.
- `returns` is the cleanest operator fallback if the field-based regime is too thin.
- Region / delay compatibility is already aligned with the current USA / TOP3000 / D1 session.
- The family changes information content through the event gate, not by piling on more price operators.

## Baseline Expression Ideas

1. `trade_when(ts_rank(historical_volatility_20, 20) > 0.5, group_rank(ts_zscore(close - vwap, 10), industry), -1)`
2. `trade_when(ts_rank(historical_volatility_20, 10) > 0.5, group_rank(ts_zscore(close - vwap, 10), industry), -1)`
3. `trade_when(ts_rank(ts_std_dev(returns, 5), 20) > 0.5, group_rank(ts_zscore(close - vwap, 10), industry), -1)`

## Likely First Failure

- Sharpe: the pressure leg may still be wrong in sign or too common even after gating.
- Fitness: the gate may narrow turnover, but the signal can still be noisy.
- Turnover: the gate could still be too broad if volatility is elevated too often.
- Weight: concentration can show up if the event only fires on a narrow subset of names.
- Sub-universe: still unknown until real TEST and submission-style evidence appear.
- Self-correlation: likely lower than the direct price-volume family, but not safe yet.

## Next Action

- First field/source combination to try: `historical_volatility_20` gate with `close - vwap` pressure signal.
- First baseline to simulate: `trade_when(ts_rank(historical_volatility_20, 20) > 0.5, group_rank(ts_zscore(close - vwap, 10), industry), -1)`
- Next variants: faster and slower gate windows, then a 20-day signal smoother if the gate survives.

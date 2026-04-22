# Event Trigger / Low Turnover Volume Gate Field Search Pack

## Metadata

- Date: `2026-04-22`
- Topic: `event_trigger_low_turnover_volume_gate`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`
  - official Data Explorer search results for `close`, `vwap`, `returns`, and `historical_volatility_20`

## Hypothesis

Volume spikes are the right trigger for a low-turnover event alpha, and a VWAP pressure signal may only survive once it is activated inside those regimes.

## Why This Could Matter

- The always-on price-volume family is already dead, so the only way to keep the idea alive is a real gating change.
- The forum `trade_when` pattern explicitly recommends event alphas and low-turnover alphas.
- The forum guidance on volatility suggests using `ts_rank(ts_std_dev(returns, d1), d2) > 0.5` to capture high-volatility periods.
- `volume` and `adv20` are broad 100% coverage fields for the event gate, while `close` and `vwap` anchor the pressure signal.
- `historical_volatility_20` remains a lighter fallback if the first pressure signal fails.

## Data Explorer Search Terms

- Primary terms: `volume`, `vwap`, `close`, `returns`
- Secondary terms: `historical volatility`, `average daily volume`, `price pressure`
- Abbreviations: `std dev`, `ts_std_dev`, `adv20`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `volume` | `Price Volume Data for Equity` | Primary event source for the low-turnover gate | 100% coverage, `290781` alphas | Crowded, but useful as the structural event lever |
| `adv20` | `Price Volume Data for Equity` | Normalization anchor for the volume gate | 100% coverage, `98264` alphas | Crowded, but the gate needs a volume benchmark |
| `close` | `Price Volume Data for Equity` | Price-pressure anchor for the signal leg | 100% coverage, `519483` alphas | Very crowded, so it needs a gate |
| `vwap` | `Price Volume Data for Equity` | Cleaner pressure comparison than raw close | 100% coverage, `64392` alphas | Crowded, but useful as a normalization anchor |
| `returns` | `Price Volume Data for Equity` | Backup volatility-gate source if volume proves too noisy | 100% coverage, `316257` alphas | Standalone return signals were already killed in the direct-momentum lane |
| `historical_volatility_20` | `Volatility Data` | Backup signal or alternate event source if the pressure leg is too noisy | 70% coverage, `1634` alphas | Less crowded than the price-volume fields, but sparser |

## Coverage And Quality Checks

- The price-volume fields are broad enough for balanced long/short construction.
- The volume gate should be the primary trigger because it is the cleanest low-turnover lever available on this account.
- The volatility field remains a backup, not the main path, so the first batch can stay focused on one structural change.
- The family changes information content via gating, not by adding more price operators.
- The first pass should test whether event gating rescues the VWAP-pressure signal from the dead always-on lane.

## Baseline Expression Ideas

1. `trade_when(volume > adv20, group_rank(ts_zscore(close - vwap, 10), industry), -1)`
2. `trade_when(volume > ts_mean(volume, 10), group_rank(ts_zscore(close - vwap, 10), industry), -1)`
3. `trade_when(volume > ts_mean(volume, 20), group_rank(ts_zscore(close - vwap, 10), industry), -1)`
4. `trade_when(volume > adv20, group_rank(ts_zscore(close - vwap, 20), industry), -1)`

## Likely First Failure

- Sharpe: the pressure leg may still be wrong in sign or too common.
- Fitness: event gating may reduce turnover, but the signal may still be noisy.
- Turnover: should be lower than the killed price-volume family, but the 10-day gate could still be active.
- Weight: concentration can show up if the event only fires on a narrow set of names.
- Sub-universe: still unknown until real TEST and submission-style evidence appear.
- Self-correlation: likely lower than the direct momentum family, but not safe yet.

## Next Action

- First field/source combination to try: `volume` gate with `close - vwap` pressure signal.
- First baseline to simulate: `trade_when(volume > adv20, group_rank(ts_zscore(close - vwap, 10), industry), -1)`
- Next variants: 10-day and 20-day volume gates, then a 20-day signal smoother if the first batch is alive.

# Profitability / Value Scout Field Search Pack

## Metadata

- Date: `2026-04-27`
- Topic: `profitability_value_scout`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Official search source: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=profitability&universe=TOP3000`

## Hypothesis

Profitability fields that are already price-normalized or tightly linked to capital allocation should be slower, lower-turnover, and less crowded than the dead EPS clone lanes. The best first-pass signal is likely a simple cross-sectional rank rather than a complex transform.

## Why This Could Matter

- `qfv4` is closed and should not be reopened.
- The analyst EPS and operating-income lanes in the current registry are frozen.
- Live search results show several profitability fields with high coverage and very low visible alpha counts.
- A price-normalized profitability field may give a cleaner value-style signal than another time-series clone.

## Data Explorer Search Terms

- Primary terms: `profitability`, `return on invested capital`, `earnings to price`
- Secondary terms: `cash earnings return on equity`, `ROIC`, `earnings yield`
- Control terms: `profitability ratio`, `quality`, `return on equity`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage | Visible alphas |
| --- | --- | --- | --- | ---: |
| `proforma_earnings_to_price` | `Analysts' Factor Model` | Best first probe: a price-normalized profitability field with extremely low visible crowding | `96%` | `1` |
| `return_on_invested_capital_4` | `Analysts' Factor Model` | Clean pure profitability anchor with full coverage and almost no visible crowding | `100%` | `6` |
| `cash_earnings_return_on_equity` | `Analysts' Factor Model` | Middle backup if the first two are too idiosyncratic or too conventional | `95%` | `10` |
| `mdl177_growthanalystmodel_qga_niroe_alt` | `Analysts' Factor Model` | Broader fallback control with full coverage but still much less crowded than older composite controls | `100%` | `58` |

## Coverage And Quality Checks

- All four fields are matrix outputs from the live search snapshot.
- `proforma_earnings_to_price` is the lowest-crowding price-normalized profitability field in the snapshot.
- `return_on_invested_capital_4` is the cleanest pure profitability anchor.
- `cash_earnings_return_on_equity` is the best middle backup if the first two are too idiosyncratic.
- `mdl177_growthanalystmodel_qga_niroe_alt` is a broader control and should stay behind the cleaner anchors.

## Baseline Expression Ideas

1. `ts_rank(proforma_earnings_to_price, 20)`
2. `ts_rank(return_on_invested_capital_4, 20)`
3. `ts_rank(cash_earnings_return_on_equity, 20)`
4. `ts_rank(mdl177_growthanalystmodel_qga_niroe_alt, 20)`

## Likely First Failure

- Sharpe: the profitability/value factor may be too conventional and crowded.
- Fitness: the price-normalized field may still underperform after ranking if the signal is mostly a standard value shape.
- Turnover: should be manageable if the baseline is slow, but a shorter rank window could still be noisy.
- Coverage: not a first-order problem here, but the 95%-96% fields are slightly less robust than the 100% anchor.
- Self-correlation: unknown until a real official simulation exists.

## Next Action

- Prescreen `proforma_earnings_to_price` first.
- If it fails S-1, move to `return_on_invested_capital_4`.
- If both are weak, keep the broader profitability controls on the backlog and rotate to a different source.

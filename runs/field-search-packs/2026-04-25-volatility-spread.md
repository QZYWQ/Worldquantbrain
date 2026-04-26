# Volatility Spread Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `volatility-spread`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The implied-vs-realized volatility spread may still contain a usable short-horizon signal in daily liquid US equities, but only if the raw spread fields themselves are clean enough to survive a minimal official batch. This lane is intentionally different from the frozen social-media, analyst, model-rerating, and operating-income branches.

## Why This Could Matter

- The fields are direct volatility-spread matrices from the official Data Explorer, so the family stays interpretable.
- The live official pages show one very sparse but extremely low-crowding field and one more covered sibling field, which makes a raw baseline + sign-flip probe worthwhile.
- This is a new information source rather than another lookback / smoothing / group tweak on a frozen lane.
- If the raw spread fields do not work, the family should stop immediately instead of being cosmetically reshaped.

## Data Explorer Search Terms

- Primary terms: `volatility spread`, `implied volatility`, `realized volatility`
- Synonyms: `implied-minus-realized spread`, `volatility premium`
- Abbreviations: `implied minus realized`, `vol spread`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `mdl77_2400_rmi` | `Analysts' Factor Model` / `Technical Models` | Best first baseline; the official page describes it as the spread between nearest-to-expiration at-the-money implied volatility and the stock's previous 21-day realized volatility | Live Data Explorer: `Matrix`, `83%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer: `1` visible alpha |
| `implied_minus_realized_volatility_2` | `Analysts' Factor Model` / `Technical Models` | Best sibling control; same volatility-spread theme with materially better coverage | Live Data Explorer: `Matrix`, `97%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer: `11` visible alphas |

## Coverage And Quality Checks

- Coverage: both fields are live and usable in `USA / D1 / TOP3000`; `mdl77_2400_rmi` is sparse but testable, while `implied_minus_realized_volatility_2` is more covered.
- Missingness: `mdl77_2400_rmi` is the more fragile input, so any first-batch failure there would be meaningful.
- Region / delay compatibility: confirmed on the official Data Explorer pages.
- Field type: both confirmed fields are `Matrix`.

## Baseline Expression Ideas

1. `mdl77_2400_rmi`
2. `-mdl77_2400_rmi`
3. `implied_minus_realized_volatility_2`

## Likely First Failure

- Sharpe: the raw spread may be too close to a direct risk proxy to carry fresh edge.
- Fitness: crowding is likely to show up quickly if the family is real but not distinctive.
- Turnover: should be watchable, but the main risk is probably not excessive churn.
- Weight: the sparse baseline may fail structurally if the coverage gap is too wide.
- Sub-universe: the more covered sibling should be the cleaner test here.
- Self-correlation: if the raw field is already crowded, the family may be capped early.

## Next Action

- Which field should be tried first? `mdl77_2400_rmi`
- Which baseline expression should be simulated first? `mdl77_2400_rmi`
- Which 2-3 same-family variants should follow? `-mdl77_2400_rmi`, `implied_minus_realized_volatility_2`, `-implied_minus_realized_volatility_2`

## Official Evidence

- Live Data Explorer search for `volatility spread`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=volatility%20spread&universe=TOP3000`
- Live Data Explorer field page for `mdl77_2400_rmi`: `https://platform.worldquantbrain.com/data/data-fields/mdl77_2400_rmi?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer field page for `implied_minus_realized_volatility_2`: `https://platform.worldquantbrain.com/data/data-fields/implied_minus_realized_volatility_2?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`

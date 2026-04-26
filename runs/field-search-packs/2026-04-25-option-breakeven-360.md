# Option Breakeven 360 Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `option_breakeven_360`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The 360-day combined option breakeven price may capture a slower market-implied consensus signal than the already-frozen 30d and 90d breakeven lanes. If the longer tenor is cleaner, it may survive a minimal official batch without needing cosmetic smoothing.

## Why This Could Matter

- The field is a direct official Options Analytics matrix from the live Data Explorer.
- It is a new tenor, not a sign flip or smoothing retune of the frozen `option_breakeven_30` lane.
- The live official field page shows moderate coverage and a nontrivial but not extreme alpha count, so the field is worth one cheap probe.
- A slower combined breakeven could behave differently from the shorter 30d / 90d family if the market-implied consensus is more durable at the longer horizon.

## Data Explorer Search Terms

- Primary terms: `option breakeven 360`, `360 day breakeven`, `options analytics`
- Synonyms: `combined option breakeven`, `market-implied breakeven`, `option buyer break even`
- Abbreviations: `OBE 360`, `option breakeven 360`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `option_breakeven_360` | `Options Analytics` / `Option Analytics` | Best first anchor; a slower combined breakeven tenor that may be cleaner than the shorter `30d` / `90d` lanes | Live Data Explorer: `Matrix`, `71%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer: `373` visible alphas |

## Coverage And Quality Checks

- Coverage: `option_breakeven_360` is fully date-covered and usable for a first probe.
- Missingness: coverage is good enough to test without inventing a smoothing rescue.
- Region / delay compatibility: confirmed on the live official Data Explorer page.
- Field type: confirmed `Matrix`.
- Crowding: moderate enough for a first batch, but still needs a real batch read before promotion.

## Baseline Expression Ideas

1. `group_rank(ts_rank(option_breakeven_360 / close, 20), sector)`
2. `group_rank(ts_rank(option_breakeven_360 / close, 60), sector)`
3. `group_rank(ts_rank(ts_mean(option_breakeven_360 / close, 5), 20), sector)`

## Likely First Failure

- Sharpe: the slower breakeven may still be too smooth to carry fresh edge.
- Fitness: the family may still be too crowded even at the longer tenor.
- Turnover: likely lower than shorter-horizon options families, but still worth checking.
- Weight: sector concentration may show up if only a few industries react to the long tenor.
- Sub-universe: the family still needs a real batch read before promotion.
- Self-correlation: could be the main blocker if this longer tenor is already represented in the existing alpha pool.

## Next Action

- Which field should be tried first? `option_breakeven_360`
- Which baseline expression should be simulated first? `group_rank(ts_rank(option_breakeven_360 / close, 20), sector)`
- Which 2-3 same-family variants should follow? sign flip, slower `60d` rank, and light smoothing on the ratio leg

## Official Evidence

- Live Data Explorer field page for `option_breakeven_360`: `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_360?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer search for `option4`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=option4&universe=TOP3000`

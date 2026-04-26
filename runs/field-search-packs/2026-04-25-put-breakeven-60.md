# Put Breakeven 60 Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `put-breakeven-60`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The put-breakeven price may capture a cleaner downside-demand or crash-insurance signal than the already-explored call-breakeven lane, especially on the less crowded 60-day horizon. A minimal first probe should test whether the raw put breakeven source has enough structure to survive a sector-ranked short-horizon transform.

## Why This Could Matter

- The field is a direct options analytics matrix from the official Data Explorer.
- The 60-day put breakeven horizon is materially less crowded than the 10-day sibling, which makes it a better primary source for the first batch.
- This is a fresh options family, not a replay of the frozen model, analyst, sentiment, or volatility-spread lanes.
- If the 60-day source fails, the 10-day sibling can still serve as the same-family comparison without opening a new family.

## Data Explorer Search Terms

- Primary terms: `put breakeven`, `put_breakeven_60`, `options analytics`
- Synonyms: `put buyers break even`, `downside breakeven`, `put option break-even`
- Abbreviations: `put breakeven`, `PBE`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `put_breakeven_60` | `Options Analytics` / `Option Analytics` | Best first baseline; lower crowding than the 10-day sibling and still a direct downside-demand signal | Live Data Explorer: `Matrix`, `70%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer: `309` visible alphas |
| `put_breakeven_10` | `Options Analytics` / `Option Analytics` | Best same-family sibling if the 60-day horizon is too smooth or too weak | Live Data Explorer: `Matrix`, `70%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer: `901` visible alphas |

## Coverage And Quality Checks

- Coverage: both fields are live and usable in `USA / D1 / TOP3000`.
- Missingness: both are fully date-covered, but the 60-day field is meaningfully less crowded.
- Region / delay compatibility: confirmed on the official Data Explorer pages.
- Field type: both confirmed fields are `Matrix`.

## Baseline Expression Ideas

1. `group_rank(ts_rank(put_breakeven_60 / close, 10), sector)`
2. `group_rank(ts_rank(put_breakeven_60 / close, 20), sector)`
3. `group_rank(ts_rank(put_breakeven_10 / close, 10), sector)`

## Likely First Failure

- Sharpe: the downside signal may be too smooth or too regime-dependent.
- Fitness: options crowding and turnover could cap the family early.
- Turnover: the short-horizon rank may still be noisy.
- Weight: the 10-day sibling is more crowded and may fail concentration sooner.
- Sub-universe: options signals often look cleaner on the full universe than on the sub-universe slice.
- Self-correlation: the family may be close to already-known options breakeven templates.

## Next Action

- Which field should be tried first? `put_breakeven_60`
- Which baseline expression should be simulated first? `group_rank(ts_rank(put_breakeven_60 / close, 10), sector)`
- Which 2-3 same-family variants should follow? `-baseline`, `group_rank(ts_rank(put_breakeven_10 / close, 10), sector)`, `-group_rank(ts_rank(put_breakeven_10 / close, 10), sector)`

## Official Evidence

- Live Data Explorer field page for `put_breakeven_60`: `https://platform.worldquantbrain.com/data/data-fields/put_breakeven_60?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer field page for `put_breakeven_10`: `https://platform.worldquantbrain.com/data/data-fields/put_breakeven_10?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer search for `put breakeven`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=put%20breakeven&universe=TOP3000`

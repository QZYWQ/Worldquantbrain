# Option Breakeven 30 Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `option_breakeven_30`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The combined 30-day option breakeven price may capture a cleaner market-implied expectation signal than the already-frozen social-media and EPS-close lanes, especially if the market is pricing a broad call/put consensus rather than a single-side options tilt.

## Why This Could Matter

- The field is a direct official Options Analytics matrix from the live Data Explorer.
- `option_breakeven_30` is materially less crowded than the raw call-only siblings, so it is a better first probe than a cosmetic sign flip on a frozen lane.
- The source is economically distinct from the frozen analyst, social-media, and model-rerating families because it comes from the options market rather than estimate or sentiment data.
- A combined call/put breakeven field can plausibly behave differently from the already-tried put-only and call-only lanes.

## Data Explorer Search Terms

- Primary terms: `option breakeven`, `30 day breakeven`, `options analytics`
- Synonyms: `combined option breakeven`, `option buyer break even`, `market-implied breakeven`
- Abbreviations: `OBE 30`, `option breakeven 30`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `option_breakeven_30` | `Options Analytics` / `Option Analytics` | Best first anchor; combined call+put breakeven gives the broadest consensus view in the 30-day bucket | Live Data Explorer shows `Matrix`, `71%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer shows `384` visible alphas |
| `option_breakeven_90` | `Options Analytics` / `Option Analytics` | Best same-family horizon sibling; tests whether a slower combined breakeven curve is cleaner than the 30-day anchor | Live Data Explorer search shows `Matrix`, `71%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer search shows `325` visible alphas |

## Coverage And Quality Checks

- Coverage: `option_breakeven_30` is fully date-covered and usable for a first probe.
- Missingness: coverage is good enough to test without inventing a smoothing rescue.
- Region / delay compatibility: confirmed on the live official Data Explorer page and search results.
- Field type: both candidate fields are `Matrix`.
- Crowding: the 30-day field is cleaner than the call-only sibling set and cleaner than the social-media lane.

## Baseline Expression Ideas

1. `group_rank(ts_rank(option_breakeven_30 / close, 20), sector)`
2. `group_rank(ts_rank(option_breakeven_90 / close, 20), sector)`
3. `group_rank(ts_rank(call_breakeven_30 / close, 20), sector)`

## Likely First Failure

- Sharpe:
  The combined options consensus may be too smooth or too regime-dependent.
- Fitness:
  Crowding may still cap the family even if the field itself is clean.
- Turnover:
  A short-horizon rank could still be noisy if the signal is real but unstable.
- Weight:
  Sector concentration may show up if only a few industries react to the option breakeven signal.
- Sub-universe:
  The first batch still needs a real sub-universe read before any promotion claim.
- Self-correlation:
  Could be the main blocker if the options consensus is already close to an existing alpha.

## Next Action

- Which field should be tried first? `option_breakeven_30`
- Which baseline expression should be simulated first? `group_rank(ts_rank(option_breakeven_30 / close, 20), sector)`
- Which 2-3 same-family variants should follow? sign flip, `option_breakeven_90`, sign flip of the sibling

## Official Evidence

- Live Data Explorer field page for `option_breakeven_30`: `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_30?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer search for `call breakeven`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=call%20breakeven&universe=TOP3000`
- Live Data Explorer search for `option breakeven`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=option%20breakeven&universe=TOP3000`

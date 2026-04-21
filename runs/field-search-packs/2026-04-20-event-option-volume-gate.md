# Event Option Volume Gate Field Search Pack

## Metadata

- Date: `2026-04-20`
- Topic: `event_option_volume_gate`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Official page context:
  - `platform.worldquantbrain.com/data/data-fields/pcr_vol_all?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
  - `platform.worldquantbrain.com/data/data-fields/pcr_oi_all?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`

## Hypothesis

When the put-to-call volume ratio rises above its own recent norm, option positioning is signaling a live bearish or hedging event. At those moments, a slower cross-sectional ranking on put-call ratios may produce a cleaner, lower-correlation signal than an always-on sentiment lane.

## Why This Could Matter

- This is a real information-family change away from both the submitted analyst EPS alpha and the failed sentiment buzz lane.
- The event-gated structure should reduce unnecessary always-on exposure and give the lane a clearer reason to trade.
- The confirmed option fields are less crowded than `scl12_buzz`, especially `pcr_vol_all`, so the diversification upside is still worth a first cheap batch.

## Data Explorer Search Terms

- Primary terms: `pcr`, `put call ratio`, `option volume`, `open interest`
- Synonyms: `put call`, `option analytics`, `options ratio`
- Abbreviations: `oi`, `vol`, `pcr`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `pcr_vol_all` | `Options Analytics` / `option9` | Best first gate field because it directly captures abnormal put-versus-call trading flow and has lighter visible crowding than the OI sibling | Official page in this session: `Matrix`, `70%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Official page shows `365` visible alphas |
| `pcr_oi_all` | `Options Analytics` / `option9` | Cleaner slower sibling for the ranking leg because open-interest skew can move more slowly than daily option flow | Official page in this session: `Matrix`, `71%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Official page shows `850` visible alphas |

## Coverage And Quality Checks

- Coverage:
  Both confirmed option fields are materially sparser than the submitted EPS line and the failed buzz lane, so Sub-universe risk is real from the start.
- Missingness:
  Sparse coverage is likely concentrated in names with weaker listed-options activity rather than random noise.
- Region / delay compatibility:
  Both field pages were verified in this session under `USA / D1 / TOP3000`.
- Field type:
  Both `pcr_vol_all` and `pcr_oi_all` are confirmed as `Matrix` fields.

## Baseline Expression Ideas

1. `trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-pcr_oi_all, industry), -1)`
2. `trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 10), group_rank(-pcr_oi_all, industry), -1)`
3. `trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-pcr_vol_all, industry), -1)`

## Likely First Failure

- Sharpe:
  The option thesis may still be too noisy if the gate fires on hedging flow that mean-reverts too quickly.
- Fitness:
  Event gating may keep turnover under control, but sparse coverage can still limit robustness.
- Turnover:
  Lower than the failed buzz control is the intended benefit, but the shortest gate window remains a risk.
- Weight:
  Sparse option coverage can create concentration quickly if the active names cluster.
- Sub-universe:
  This is the first structural risk because confirmed field coverage is only around `70%`.
- Self-correlation:
  Lower risk than `scl12_buzz`, but still not safe enough to assume before real checks.

## Next Action

- Which field should be tried first?
  `pcr_vol_all` as the event trigger, with `pcr_oi_all` as the slower ranking leg.
- Which baseline expression should be simulated first?
  `trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-pcr_oi_all, industry), -1)`
- Which 2-3 same-family variants should follow?
  Shorter trigger window `10d`, swap the signal leg to `pcr_vol_all`, and smooth the OI signal with `ts_mean(pcr_oi_all, 5)`.

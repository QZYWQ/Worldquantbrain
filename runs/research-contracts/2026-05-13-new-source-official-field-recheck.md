# 2026-05-13 New Source Official Field Recheck

## Scope

Purpose: re-rank the proposed new information-source directions before spending more simulation budget.

Target setup:

- Instrument: `EQUITY`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Source: official WorldQuant BRAIN API `/data-fields`
- Captured at: `2026-05-13T23:27:36+08:00`

This memo records field metadata only. It does not create real alpha metrics.

## User-Reported Inputs

- `fn_comp_options_grants_fair_value_q` with `ts_zscore(..., 5)` reportedly reached Sharpe `0.42`; combination variants are not finished.
- `mdl77` model fields are proposed as low-competition fields, especially coverage near `1.0` and `alphaCount < 10`.
- `rank(-ts_zscore(returns,5)) * rank(-ts_zscore(vwap,5))` reportedly reached Fitness `0.48` and needs optimization.

These are treated as user-reported research leads unless a current official capture confirms them.

## Official Metadata Observations

### `fn_comp_options_grants_fair_value_q`

Official field endpoint returned:

- Field: `fn_comp_options_grants_fair_value_q`
- Dataset: `fundamental2`
- Type: `MATRIX`
- Description: annual share-based compensation arrangement by share-based payment award options grants in period weighted average grant date fair value

Official search metadata for `USA / TOP3000 / D1` returned:

- Coverage: `0.2391`
- User count: `89`
- Alpha count: `320`

Interpretation: this field is valid, but it is sparse and not low-crowding. Treat the prior Sharpe `0.42` as a weak research hint, not as a reason to make this the primary lane.

Related field:

- `fn_comp_options_grants_fair_value_a`: coverage `0.5162`, user count `204`, alpha count `585`

The annual version has better coverage but higher crowding and is still not a clean low-competition source.

### `mdl77` / `model77`

The official `mdl77` search returned several current Matrix fields with high or near-full coverage and very low visible crowding.

| field | coverage | date coverage | users | alphas | note |
| --- | ---: | ---: | ---: | ---: | --- |
| `mdl77_2amv` | `0.9965` | `1.0` | `7` | `8` | equal-weighted average of Momentum Analyst and Value Analyst ranks |
| `mdl77_2deepvaluefactor_coreepsp` | `0.9835` | `1.0` | `4` | `6` | TTM core earnings-to-price |
| `mdl77_2deepvaluefactor_ttmsaleev` | `0.9579` | `1.0` | `3` | `8` | TTM sales-to-enterprise value |
| `mdl77_2deepvaluefactor_apemtt` | `0.9742` | `1.0` | `1` | `4` | relative price standardization indicator |
| `mdl77_2capacq` | `0.9204` | `1.0` | `1` | `3` | capital acquisition ratio |
| `mdl77_chgollev` | `0.9596` | `1.0` | `2` | `2` | change in operating liability leverage |
| `mdl77_growthanalystmodel_qga_iarsales` | `0.9757` | `1.0` | `4` | `4` | inventory/accounts-receivable-to-sales link |

The exhaustive `model77` dataset query hit API rate limiting before completion, so this is not a complete field inventory. Still, the returned evidence is enough to prioritize a bounded `mdl77` probe over `fn_comp` and over another price-volume rescue.

Exclude or de-prioritize:

- `mdl77_2400_rmi`: current metadata shows coverage `0.8269`, users `4`, alphas `4`, but this volatility-spread lane already failed a live first batch and has a stop memo.
- `mdl77_valueanalystmodel_qva_yoychgshares`: already failed both signs in the dilution/share-count scout.
- `mdl177_valuemomemtummodel_vm_compositesn`: already stopped after weak official results.

### Fast Price / VWAP Composite

The proposed composite is structurally close to the active `returns/vwap/volume/subindustry` family submitted on `2026-05-11` as `88Ob79jV`.

Given user-reported Fitness `0.48`, the first issue is not one missing cosmetic fix. It is weak Fitness plus likely self-correlation risk against the active price-volume pool.

## Decision

Primary next lane: `mdl77_low_crowding_model_fields`.

Secondary hold lane: `fn_comp_options_grants_fair_value_q`, but only as a sparse-field diagnostic and one sign/backfill control after the `mdl77` probe.

Drop from immediate budget: the short-horizon `returns/vwap` composite, unless a future official check shows a real self-correlation break from the active `88Ob79jV` family.

## Next Artifact Links

- Research queue: `runs/research-queues/2026-05-13-new-source-rotation-queue.json`
- First probe batch: `runs/candidate-batches/2026-05-13-mdl77-low-crowding-probe.json`

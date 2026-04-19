# Analyst Disagreement Expression Family

## Metadata

- Date: 2026-04-19
- Topic: `analyst_disagreement_dts_spe_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Lower analyst EPS disagreement may behave like a cleaner medium-horizon ranking signal than another analyst EPS-level clone, because it captures confidence dispersion rather than the absolute level of expectations.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `anl4_afv4_dts_spe`
  - `anl4_qfv4_dts_spe`
- Equivalent fallback fields:
  - none confirmed for this branch yet
- Unconfirmed assumptions:
  - Lower disagreement is the correct first-pass sign, so the initial baseline should be inverse disagreement.
  - The disagreement field can survive `Sub-universe` and `Weight` checks despite only `69%` coverage on the annual-frequency line.
  - Price normalization is not needed for the first disagreement batch.

## Baseline Expression

```text
group_rank(-ts_rank(anl4_afv4_dts_spe, 60), industry)
```

## Variant 1

- Goal:
  Keep the same inverse-disagreement thesis but test the quarterly-frequency sibling that has slightly better coverage.
- Main lever:
  Field axis from `anl4_afv4_dts_spe` to `anl4_qfv4_dts_spe`.

```text
group_rank(-ts_rank(anl4_qfv4_dts_spe, 60), industry)
```

## Variant 2

- Goal:
  Keep the annual-frequency disagreement field fixed while checking whether a slower horizon smooths out sparse updates.
- Main lever:
  Time axis from `60` to `120`.

```text
group_rank(-ts_rank(anl4_afv4_dts_spe, 120), industry)
```

## Variant 3

- Goal:
  Test whether the first-pass sign assumption is wrong before adding structural complexity.
- Main lever:
  Sign control from inverse disagreement to direct disagreement.

```text
group_rank(ts_rank(anl4_afv4_dts_spe, 60), industry)
```

## Expected First Failure

- Sharpe:
  The sign could be wrong, which is why a direct-sign control is included early.
- Fitness:
  Sparse coverage can produce a weak robustness profile even when the sign is directionally right.
- Turnover:
  Manageable for the initial batch because the structure is medium-horizon and ungated.
- Weight:
  High enough to watch immediately because the primary field only covers about two-thirds of the target universe.
- Sub-universe:
  Most likely first hard bottleneck if disagreement data is missing in weaker-coverage names.
- Self-correlation:
  Lower than another EPS-level sibling, but still inside the analyst family and therefore not automatically low.

## Optimization Order

1. Test the inverse annual-frequency baseline first to see whether the thesis sign is even viable.
2. If the sign is viable but coverage is the main issue, compare the quarterly-frequency sibling before adding any gating.
3. Only after sign and coverage are judged should the branch consider delta-style or event-gated disagreement variants.

## Next Simulation Batch

- Baseline:
  `group_rank(-ts_rank(anl4_afv4_dts_spe, 60), industry)`
- Variant 1:
  `group_rank(-ts_rank(anl4_qfv4_dts_spe, 60), industry)`
- Variant 2:
  `group_rank(-ts_rank(anl4_afv4_dts_spe, 120), industry)`
- Variant 3:
  `group_rank(ts_rank(anl4_afv4_dts_spe, 60), industry)`

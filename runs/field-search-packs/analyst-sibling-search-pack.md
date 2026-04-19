# Analyst Sibling Field Search Pack

## Metadata

- Date: 2026-04-19
- Topic: `analyst_eps_sibling_qfv4_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Quarterly analyst EPS estimate levels relative to price, ranked within industry, may preserve the first-cycle expectation-drift thesis while lowering crowding versus the annual mean baseline.

## Why This Could Matter

- The first cycle already showed the analyst-EPS relative-to-price thesis is viable, but its main bottleneck was weak holdout robustness rather than visible platform checks.
- A lower-crowding quarterly sibling can change information timing without abandoning the same interpretable expectation-drift story.
- Keeping the comparison frame fixed at industry-relative ranking makes this a true field-family test instead of a random structural rewrite.

## Data Explorer Search Terms

- Primary terms: `qfv4 eps`, `earnings per share`, `estimate median`
- Synonyms: `analyst estimate`, `estimate mean`, `analyst disagreement`
- Abbreviations: `eps`, `qfv4`, `afv4`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `anl4_qfv4_median_eps` | `analyst4` | Best immediate quarterly median sibling for the first-cycle thesis | Official platform check in this session: `MATRIX`, coverage `1.0`, dateCoverage `1.0` | Official platform check in this session: userCount `29`, alphaCount `36` |
| `anl4_qfv4_eps_mean` | `analyst4` | Same quarterly lane, but mean aggregation instead of median | Official platform check in this session: `MATRIX`, coverage `1.0` | Official platform check in this session: userCount `30`, alphaCount `32` |
| `anl4_afv4_median_eps` | `analyst4` | Annual-median control around the originally planned analyst4 lane | Official platform check in this session: `MATRIX`, coverage `1.0` | Official platform check in this session: userCount `102`, alphaCount `130`; not lower crowding than the first-cycle annual mean baseline |
| `anl4_afv4_dts_spe` | `analyst4` | Disagreement-style sibling for a later lower-correlation branch | Official platform check in this session: `MATRIX`, coverage `0.691` | Official platform check in this session: userCount `68`, alphaCount `78`; more distinct but sparser |
| `close` | `pv1` | Price normalization denominator used by the proven first-cycle thesis | Official platform check in this session: `MATRIX`, coverage `1.0` | Not a novelty source |

## Coverage And Quality Checks

- Coverage:
  `anl4_qfv4_median_eps` and `anl4_qfv4_eps_mean` both kept full coverage in the exact target setup. That makes them stronger first-pass siblings than sparse guidance fields.
- Missingness:
  No missingness warning is visible from the official field metadata for the two qfv4 level fields because both show full coverage. `anl4_afv4_dts_spe` is different and should be treated as a later branch because coverage is only `0.691`.
- Region / delay compatibility:
  All fields listed above were verified on the official platform under `USA / D1 / TOP3000` in this session.
- Field type:
  The branch candidates used for the first second-cycle batch are all `MATRIX` fields.

## Baseline Expression Ideas

1. `group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)`
2. `group_rank(ts_rank(anl4_qfv4_eps_mean/close, 60), industry)`
3. `group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)`

## Likely First Failure

- Sharpe:
  The qfv4 siblings may still be too close to the first-cycle line if quarterly versus annual timing does not change cross-sectional behavior enough.
- Fitness:
  If the qfv4 siblings only match the first-cycle baseline without improving holdout behavior, fitness may remain near-pass rather than clearly better.
- Turnover:
  Lower risk than the first-cycle 20-day fast branch because the plan keeps the `60d` horizon.
- Weight:
  Lower structural risk because the primary qfv4 level fields both have full coverage.
- Sub-universe:
  Still needs to be read from real simulation output, but the full-coverage sibling fields reduce the odds of a thin-coverage surprise.
- Self-correlation:
  Lower crowding makes this less likely than in the first cycle, but it is still a real risk because the thesis remains in the analyst EPS family.

## Next Action

- Which field should be tried first?
  `anl4_qfv4_median_eps`
- Which baseline expression should be simulated first?
  `group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)`
- Which 2-3 same-family variants should follow?
  `anl4_qfv4_eps_mean`, `anl4_afv4_median_eps`, then a later disagreement-style sibling only if the level fields prove worth extending.

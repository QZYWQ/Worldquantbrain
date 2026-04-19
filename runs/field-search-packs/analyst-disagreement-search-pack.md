# Analyst Disagreement Field Search Pack

## Metadata

- Date: 2026-04-19
- Topic: `analyst_disagreement_dts_spe_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Stocks with lower analyst EPS disagreement, measured as a lower standard deviation of analyst estimates, may rank better cross-sectionally over a medium horizon than high-disagreement names once the comparison is kept inside industry groups.

## Why This Could Matter

- The submitted line already proved the broader analyst-expectation family is viable, but the next branch needs a more meaningful information-source change than another EPS-level sibling.
- Disagreement changes the thesis from absolute expectation level to uncertainty or dispersion in the analyst view.
- This is still a medium-speed analyst signal, so the first batch should stay simple and interpretable before any gating or multi-input combinations are added.

## Data Explorer Search Terms

- Primary terms: `anl4_afv4_dts_spe`, `anl4_qfv4_dts_spe`, `standard deviation of estimations`
- Synonyms: `analyst disagreement`, `estimate dispersion`, `earnings estimate std`
- Abbreviations: `dts spe`, `eps std`, `analyst4`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `anl4_afv4_dts_spe` | `analyst4` | Primary disagreement field for the post-submit follow-up branch | Fresh official field page check in this session: `Matrix`, coverage `69%`, dateCoverage `100%` in `USA / D1 / TOP3000` | Fresh official field page check in this session: `78` alphas; less crowded than many broad analyst level lines, but not sparse enough to ignore correlation risk |
| `anl4_qfv4_dts_spe` | `analyst4` | Same disagreement thesis with quarterly-frequency sibling as the first same-family backup | Fresh official search result in this session: `Matrix`, coverage `72%`, dateCoverage `100%` in `USA / D1 / TOP3000` | Fresh official search result in this session: `102` alphas; slightly better coverage, but more crowded than the afv4 disagreement line |
| `close` | `pv1` | Optional denominator only if later tests show scale distortion and a price normalization case is needed | Not re-verified in this session because the first disagreement batch does not require price normalization | Not a novelty source |
| `<sentiment fallback field to re-verify>` | to confirm in platform | Non-analyst fallback lane if disagreement coverage or robustness fails | Not yet re-verified in this session | Keep as fallback only until official visibility is refreshed |

## Coverage And Quality Checks

- Coverage:
  `anl4_afv4_dts_spe` is usable but clearly sparser than the submitted EPS-level line. The first real concern is not Sharpe but whether 69% coverage creates a Sub-universe or weight problem in simulation.
- Missingness:
  The field page shows `100%` date coverage, but cross-sectional coverage is only `69%`. Treat missingness as a structural concern rather than random noise.
- Region / delay compatibility:
  Fresh official checks in this session confirm both disagreement fields are visible under `USA / D1 / TOP3000`.
- Field type:
  Both disagreement candidates are `Matrix` fields, so they are directly usable in the planned Fast Expression baselines.

## Baseline Expression Ideas

1. `group_rank(-ts_rank(anl4_afv4_dts_spe, 60), industry)`
2. `group_rank(-ts_rank(anl4_qfv4_dts_spe, 60), industry)`
3. `group_rank(ts_rank(anl4_afv4_dts_spe, 60), industry)`

## Likely First Failure

- Sharpe:
  The sign may be wrong, because analyst disagreement can behave either as a risk penalty or as a reward-to-attention proxy depending on the period.
- Fitness:
  Even if the sign is correct, sparse coverage can keep fitness near-pass until the distribution is better understood.
- Turnover:
  Lower risk than a short event-style branch because the first batch keeps a `60d` horizon.
- Weight:
  Real risk because `69%` coverage is materially thinner than the submitted line.
- Sub-universe:
  This is the most likely first structural failure, especially if disagreement data disappears outside the better-covered names.
- Self-correlation:
  Lower family overlap than another EPS-level clone, but still an analyst-family branch and therefore not automatically safe.

## Next Action

- Which field should be tried first?
  `anl4_afv4_dts_spe`
- Which baseline expression should be simulated first?
  `group_rank(-ts_rank(anl4_afv4_dts_spe, 60), industry)`
- Which 2-3 same-family variants should follow?
  `anl4_qfv4_dts_spe` as the first field backup, `anl4_afv4_dts_spe` with a slower `120d` horizon, then a direct-sign control before adding any gating.

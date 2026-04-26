# Actual EPS Value Close Industry Field Search Pack

## Metadata

- Date: `2026-04-24`
- Topic: `actual_eps_value_close_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Reported EPS should help same-industry peers re-rank over a slow horizon, and the live official Data Explorer search in this session found a cleaner analyst4 actual-EPS field than the broader estimate lane.

## Why This Could Matter

- The analyst EPS estimate branch already showed that a price-normalized EPS/close structure can produce a strong official candidate.
- Actual reported EPS is a different information source from analyst estimates, so it is worth one small batch before any broader promotion claim.
- The official search results show a fully covered matrix field with materially lower crowding than the generic quarterly actual-EPS alias.

## Data Explorer Search Terms

- Primary terms: `actual eps value`, `earnings per share actual value`, `eps actual`
- Sibling terms: `actual earnings per share`, `reported eps`, `quarterly eps actual`
- Distinctness terms: `eps actual value`, `actual eps quarterly`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `anl4_af_eps_value` | `analyst4` / `Analyst Estimate Data for Equity` | Best first anchor because the official search shows a fully covered matrix field and the lower-crowding actual-EPS variant in this session | Official search shows `MATRIX`, `100%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Official search shows `191` visible alphas |
| `actual_eps_value_quarterly` | `analyst4` / `Analyst Estimate Data for Equity` | Explicit quarterly actual-EPS control if the shorter analyst4 alias behaves differently in simulation | Official search shows `MATRIX`, `100%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Official search shows `308` visible alphas |
| `eps_estimate_value` | `analyst4` / `Analyst Estimate Data for Equity` | Fallback comparison control only; useful if the actual-EPS lane turns out to be too sparse or too crowded around the same signal | Official search shows `VECTOR`, `99%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Official search shows `34` visible alphas |

## Coverage And Quality Checks

- Coverage:
  `anl4_af_eps_value` and `actual_eps_value_quarterly` are both fully covered in the live search results.
- Missingness:
  The actual-EPS branch is clean enough to start a diagnostic batch without inventing extra smoothing.
- Region / delay compatibility:
  The live official Data Explorer search was `USA / D1 / TOP3000`.
- Field type:
  The primary actual-EPS fields are `MATRIX` fields, so a price-normalized form is the safest first expression.
- Crowding:
  `anl4_af_eps_value` is the cleaner primary anchor and should be tested before any broader fallback.

## Baseline Expression Ideas

1. `group_rank(ts_rank(anl4_af_eps_value / close, 60), industry)`
2. `group_rank(-ts_rank(anl4_af_eps_value / close, 60), industry)`
3. `group_rank(ts_rank(actual_eps_value_quarterly / close, 60), industry)`
4. `group_rank(ts_rank(anl4_af_eps_value / close, 120), industry)`

## Likely First Failure

- Sharpe:
  The signal may already be crowded even though the field itself is cleaner than the older estimate lanes.
- Fitness:
  A fully covered field can still look weak after grouping if the price-normalized actual-EPS move is too blunt.
- Turnover:
  This is unlikely to be the first blocker because the thesis is intentionally slow.
- Weight:
  Concentration is possible if only a few industries react strongly to the actual-EPS level.
- Sub-universe:
  This remains a real risk and must be checked with real platform evidence.
- Self-correlation:
  Unknown until a real official check exists.

## Next Action

- Which field should be tried first? `anl4_af_eps_value`
- Which baseline expression should be simulated first? `group_rank(ts_rank(anl4_af_eps_value / close, 60), industry)`
- Which 2-3 same-family variants should follow? Sign flip, quarterly alias control, then a slower 120d control.

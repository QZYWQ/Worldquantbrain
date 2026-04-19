# Primary Direction Field Search Pack

## Metadata

- Date: 2026-04-18
- Topic: `analyst_eps_price_industry`
- Region: `USA` (planned baseline, not account-verified in this session)
- Universe: `TOP3000` (planned baseline, not account-verified in this session)
- Delay: `1` (planned baseline, not account-verified in this session)

## Confirmation Boundary

### Confirmed from the local project and public-doc summaries

- The first official cycle is using `analyst_eps_price_industry` as the primary direction.
- The local knowledge base uses `est_eps` and `close` as the public example pair for this thesis.
- The local knowledge base recommends short Data Explorer queries such as `earnings per share`, `eps`, and `analyst recommendation`.
- The local workflow requires checking `coverage`, `type`, `alpha count`, `user count`, `dataset category`, and region/delay compatibility before trusting a field.

### Not confirmed in this session and must be checked on the official platform

- Whether `est_eps` is visible for the current account under `USA / Delay 1 / TOP3000`.
- Which exact analyst recommendation or earnings surprise fields are visible on the current account.
- Live `coverage`, `alpha count`, `user count`, and dataset-category values for the shortlisted fields.
- Current `Check Submission` thresholds or any account-specific submission UI behavior.

## Hypothesis

Stocks with stronger analyst earnings expectations relative to price should rank higher cross-sectionally over a medium horizon, especially after removing broad industry structure through group comparison.

## Why This Could Matter

- The signal is trying to predict medium-horizon relative strength driven by expectation drift rather than pure price action.
- Analyst expectation updates can diffuse more slowly than immediate price moves, which creates room for cross-sectional misranking.
- This is more likely a medium-speed signal than a very fast event shock, so the first baseline should stay interpretable and avoid over-gating.

## Data Explorer Search Terms

- Primary terms: `earnings per share`, `eps`, `analyst recommendation`
- Synonyms: `analyst estimate`, `earnings surprise`, `estimate revision`
- Abbreviations: `eps`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `est_eps` | analyst / estimate lane (exact dataset to confirm in platform) | Local public example for expectation change; cleanest first baseline field | Unknown until Data Explorer check under chosen region/delay/universe | Analyst lane can be crowded; inspect `alpha count` and `user count` before scaling time into it |
| `close` | price | Normalizes EPS expectation by price so the ranking is not dominated by absolute scale | Usually expected to be broad, but still verify compatibility in the target setup | Not the novelty source; only a denominator |
| `<analyst recommendation field from search results>` | to confirm in platform | Same thesis family, slower adjacent branch if raw EPS lane looks crowded | Unknown until Data Explorer confirms visibility and coverage | Potentially less crowded than the direct EPS lane, but do not assume |
| `<earnings surprise field from search results>` | to confirm in platform | Event-adjacent sibling branch if the pure estimate line has weak distinctness | Unknown until platform check | Could become a lower-correlation cousin, but only if a real field is visible |

## Coverage And Quality Checks

- Coverage:
  Compare `est_eps`, the recommendation-adjacent field, and the surprise-adjacent field under the exact target region, delay, and universe. Reject any branch whose coverage looks too sparse for balanced long/short construction.
- Missingness:
  Check whether missing values are structurally concentrated in one subset of names instead of randomly thin.
- Region / delay compatibility:
  Confirm field visibility directly in Data Explorer before writing any simulation expression that assumes availability.
- Field type:
  Confirm these are matrix-style fields usable in the planned expression. If any field is vector-style, do not proceed until the required vector-to-matrix treatment is known.

## Baseline Expression Ideas

1. `group_rank(ts_rank(est_eps/close, 60), industry)`
2. `group_rank(ts_rank(est_eps/close, 20), industry)`
3. `group_rank(ts_rank(est_eps/close, 120), industry)`

## Likely First Failure

- Sharpe:
  The thesis is plausible, but the first baseline may be too crowded to stand out if the information content is too close to well-known analyst lines.
- Fitness:
  If Sharpe is only near-pass, Fitness can lag until turnover and distribution are stabilized.
- Turnover:
  Medium risk. The 20-day branch may overreact; the 120-day branch may be too stale.
- Weight:
  Lower risk than sparse event fields if coverage is healthy, but still watch for concentration if the field is patchy.
- Sub-universe:
  Watch for weaker behavior if analyst coverage thins materially outside the most liquid slice.
- Self-correlation:
  This is the most likely first bottleneck because the analyst lane is understandable and therefore potentially crowded.

## Submission Posture

- Current posture: `keep polishing / branch`, not `submit`
- Why:
  This pack is a field-discovery and baseline-planning artifact. It does not contain live platform evidence, real metrics, or confirmed account-level field availability.
- Backup branch:
  If the analyst lane looks too crowded after the first baseline, rotate the second effort to `event_option_volume_gate` instead of endlessly micro-tuning the same line.

## Next Action

- Which field should be tried first?
  Try `est_eps` first, because it is the cleanest publicly referenced baseline field in the local project.
- Which baseline expression should be simulated first?
  Simulate `group_rank(ts_rank(est_eps/close, 60), industry)` first.
- Which 2-3 same-family variants should follow?
  Follow with the 20-day and 120-day windows, then branch into one recommendation-adjacent or surprise-adjacent field only if the platform confirms a real candidate field.

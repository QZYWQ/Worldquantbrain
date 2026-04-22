# Sentiment Buzz Stability Field Search Pack

## Metadata

- Date: `2026-04-21`
- Topic: `sentiment_buzz_stability`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Official page context:
  - `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=buzz&universe=TOP3000`

## Hypothesis

Relative sentiment volume may have a slower, steadier cross-sectional edge than the crowded analyst and profitability lanes, and a smoothed buzz/stability branch could give us a distinct non-analyst family with better correlation distance than the current operating_income ridge.

## Why This Could Matter

- This is a real information-family move away from analyst EPS and away from the crowded operating_income smoothing ridge.
- The field family is interpretable: it is still sentiment/buzz, but it changes the information source enough to matter.
- The Data page shows a compact sentiment family with multiple 100% coverage fields, so a first batch can stay simple instead of forcing a sparse or exotic signal.

## Data Explorer Search Terms

- Primary term: `buzz`
- Secondary term: `sentiment`
- Backup term: `negative sentiment`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `snt_buzz` | `Sentiment Data for Equity` / `socialmedia12` | Best first field for this lane because it is a direct sentiment-volume measure with full coverage and a manageable alpha count | `100%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `9018` visible alphas |
| `snt_value` | `Sentiment Data for Equity` / `socialmedia12` | Good backup if we want the sentiment sign rather than buzz volume | `100%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `2378` visible alphas |
| `scl12_buzz` | `Sentiment Data for Equity` / `socialmedia12` | Dataset-level buzz control if the field family needs a broader relative-volume version | `100%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `19674` visible alphas |

## Coverage And Quality Checks

- Coverage:
  `snt_buzz` and `snt_value` both show `100%` coverage and `100%` date coverage in the official Data search results for `USA / D1 / TOP3000`.
- Missingness:
  The fields are already fill-handled by the dataset, so the first batch can focus on signal shape rather than repair logic.
- Region / delay compatibility:
  The confirmed fields are visible in the official `USA / D1 / TOP3000` Data search results with `delay=1`.
- Crowding:
  `snt_buzz` is less crowded than `scl12_buzz` and stays simple enough for a first batch.

## Baseline Expression Ideas

1. `group_rank(ts_mean(snt_buzz, 63), industry)`
2. `group_rank(ts_mean(snt_buzz, 21), industry)`
3. `group_rank(ts_mean(snt_buzz, 126), industry)`

## Likely First Failure

- Sharpe:
  The sign may be noisy or the buzz signal may react too fast to be stable.
- Fitness:
  This lane may need the right smoothing window to turn raw sentiment into something robust.
- Turnover:
  If the field is too jumpy, turnover may become the first bottleneck.
- Weight:
  Concentration could still appear if only a narrow subset of names actually carries the sentiment signal.
- Sub-universe:
  Must be checked on live simulation before any packaging claim.
- Self-correlation:
  Unknown until real check evidence exists.

## Next Action

- First field to try: `snt_buzz`
- First baseline to simulate: `group_rank(ts_mean(snt_buzz, 63), industry)`
- Next same-family variants: `21d` and `126d` smoothing controls before touching neutralization or switching to `snt_value`

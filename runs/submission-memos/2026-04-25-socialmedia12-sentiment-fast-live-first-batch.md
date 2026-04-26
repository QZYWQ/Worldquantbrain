# 2026-04-25 Social Media Sentiment Fast Live First Batch

## Decision

- Freeze `socialmedia12-sentiment-fast` for the current budget.
- Do not continue to the two remaining lookback variants.
- Rotate to a new family source instead of polishing this lane.

## Official Evidence

- Field verified on the live Data Explorer page:
  - `scl12_sentiment_fast_d1`
  - Dataset: `socialmedia12` / `Sentiment Data for Equity`
  - Category: `Social Media`
  - Type: `Matrix`
  - Coverage: `97.56%` on `USA / D1 / TOP3000`
  - Date coverage: `100%`
  - Visible users: `111`
  - Visible alphas: `125`
- Live API search response confirmed the same field and crowding profile.
- Batch simulations used the official Simulate page with:
  - `region=USA`
  - `universe=TOP3000`
  - `delay=1`
  - `decay=4`
  - `neutralization=Subindustry`
  - `truncation=0.08`
  - `pasteurization=ON`
  - `unitHandling=VERIFY`
  - `nanHandling=ON`
  - `testPeriod=P1Y`

## Batch 01 Results

- Baseline `scl12_sentiment_fast_d1`
  - Simulation id: `1MijU56c74vqc7djviffdii`
  - Alpha id: `6XY6x36Y`
  - IS: `Sharpe -0.51`, `Fitness -0.13`, `Turnover 76.02%`, `Returns -5.12%`
  - IS checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `HIGH_TURNOVER=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- Sign flip `-scl12_sentiment_fast_d1`
  - Simulation id: `1Ixos426V4rNcmiFllnLkqe`
  - Alpha id: `xAm7MWbW`
  - IS: `Sharpe 0.51`, `Fitness 0.13`, `Turnover 76.02%`, `Returns 5.12%`
  - IS checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `HIGH_TURNOVER=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- Holdout/test moved against the sign flip:
  - `xAm7MWbW` test: `Sharpe -0.72`, `Fitness -0.17`, `Returns 4.40%`

## Why This Is A Freeze

- The baseline is negative, so the sign-flip control was mandatory.
- The sign-flip control does not clear the practical floor on IS and flips negative again on test.
- High turnover and concentrated weight fail on both signs.
- The remaining lookback variants would only be cosmetic continuation of a weak lane.

## Next Step

- Rotate to a different sentiment source rather than staying inside `socialmedia12`.
- Next-hop family source: `socialmedia8 / snt_social_value`.

## Status

- `freeze`
- `rotate`

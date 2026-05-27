# Assets Cap Delta Zscore Subindustry Field Search Pack

## Metadata

- Date: `2026-05-08`
- Topic: `assets_cap_delta_zscore_subindustry`
- Region: `USA` assumed from screenshot; verify on official BRAIN
- Universe: `TOP3000` assumed from screenshot; verify on official BRAIN
- Delay: `1` assumed from screenshot; verify on official BRAIN

## Hypothesis

Short-term changes in a firm's asset-to-market-cap ratio, compared inside its subindustry, may identify balance-sheet expansion / valuation compression states that the market does not immediately rank correctly.

## Why This Could Matter

- `assets / cap` is an interpretable balance-sheet-to-market-value ratio. It mixes a slow accounting numerator with a market-value denominator, so the ratio can move when fundamentals update or when price/cap changes.
- `ts_delta(..., 2)` turns the level ratio into a very short change signal, which may reduce classic value-factor crowding.
- `ts_zscore(..., 20)` makes the recent change relative to its short local history.
- `group_rank(..., subindustry)` compares firms against close business-model peers, which is important because asset intensity differs structurally by subindustry.
- The screenshot comment points to `hump()` and `ts_backfill` as repairs for low Sub-universe Sharpe, but those should be repair levers after the direct baseline and sign control are known.

## Data Explorer Search Terms

- Primary terms: `assets`, `total assets`, `cap`, `market cap`, `capitalization`
- Ratio terms: `assets to cap`, `asset to market`, `book assets`, `total assets amount`
- Sibling terms: `liabilities`, `equity`, `total_assets`, `assets_amount`, `enterprise value`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `assets` | verify in Data Explorer | Screenshot numerator; likely a broad total-assets field | Must verify current account coverage and update rhythm | Likely common and crowded |
| `cap` | verify in Data Explorer | Screenshot denominator; market-cap style size normalizer | Usually broad, but exact platform semantics must be verified | Very common denominator |
| `total_assets` / `total_assets_amount` | verify fallback | Possible cleaner or more explicit asset sibling | Unknown until searched | Unknown |
| `liabilities` / `equity` siblings | verify fallback | Can create adjacent balance-sheet ratio branches if `assets / cap` is crowded | Unknown until searched | May overlap with leverage/value factors |

## Coverage And Quality Checks

- Coverage:
  Do not assume from screenshot. Confirm `assets`, `cap`, and the ratio coverage in the current account.
- Missingness:
  `assets` may update quarterly / annually and may need `ts_backfill`; `cap` is likely daily.
- Region / delay compatibility:
  Verify `USA / TOP3000 / Delay 1` in the active platform account.
- Competition route compatibility:
  Start `D1-first` because the screenshot uses Delay 1.
- Field type:
  Confirm whether `assets` is matrix and whether any vector preprocessing is needed.

## New Dataset Quick Evaluation

Run these as diagnostics with `None` neutralization and decay `0`. Interpret `Long Count + Short Count` as field-health evidence only.

| Diagnostic | Expression | What to inspect |
| --- | --- | --- |
| Assets raw coverage | `assets` | Numerator coverage |
| Cap raw coverage | `cap` | Denominator coverage |
| Assets non-zero coverage | `assets != 0 ? 1 : 0` | Effective non-zero numerator availability |
| Ratio non-zero coverage | `(assets / cap) != 0 ? 1 : 0` | Ratio availability and denominator issues |
| Assets update frequency | `ts_std_dev(assets, 63) != 0 ? 1 : 0` | Whether the numerator is stale / quarterly-like |
| Ratio update frequency | `ts_std_dev(assets / cap, 20) != 0 ? 1 : 0` | Whether the ratio is mostly price/cap-driven |
| Ratio bounds | `abs(assets / cap) > X` | Small-cap denominator outliers |
| Ratio distribution | `X < scale_down(assets / cap) && scale_down(assets / cap) < Y` | Whether observations cluster too tightly |

## Baseline Expression Ideas

1. `group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry)`
2. `-group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry)`
3. `group_rank(ts_rank(ts_delta(assets / cap, 2), 20), subindustry)`
4. `group_rank(ts_zscore(ts_delta(ts_backfill(assets, 60) / cap, 2), 20), subindustry)`
5. `group_rank(ts_zscore(ts_delta(assets / cap, 5), 60), subindustry)`

## Likely First Failure

- Sharpe:
  Direction is ambiguous because ratio increases can mean asset growth, valuation compression, or price weakness.
- Fitness:
  Very short `2d` delta can add turnover without enough return density.
- Turnover:
  The daily `cap` denominator may make a slow fundamental idea trade too frequently.
- Weight:
  Small-cap denominator effects can concentrate weights.
- Sub-universe:
  If the edge lives in smaller names, Sub-universe Sharpe may lag even when headline Sharpe/Fitness pass.
- Self-correlation:
  Could overlap with value, leverage, or prior balance-sheet ratio families unless the delta/zscore structure is materially different.

## Next Action

- First run the field-health diagnostics if `assets` coverage is unknown.
- Then run the baseline and sign control together.
- Only use `ts_backfill` or `hump()` after the baseline shows viable Sharpe/Fitness but weak Sub-universe or turnover behavior.

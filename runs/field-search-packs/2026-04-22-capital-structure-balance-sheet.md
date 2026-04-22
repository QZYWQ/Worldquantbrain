# Capital Structure Balance Sheet Field Search Pack

## Metadata

- Date: `2026-04-22`
- Topic: `capital_structure_balance_sheet`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Firms with a stronger equity cushion relative to their asset base should be mispriced more slowly than profitability or analyst-estimate stories, so a leverage-style balance-sheet ratio may provide a lower-correlation slow alpha lane.

## Why This Could Matter

- The current operating-income ridge is now a backup lane, not the main branch.
- A balance-sheet ratio is a different information family from the earnings and analyst lines already explored.
- Industry-relative ranking should help suppress size effects and make the signal easier to compare cross-sectionally.
- The market often updates leverage and equity-cushion information only when quarterly fundamentals refresh.

## Data Explorer Search Terms

- Primary terms: `equity`, `liabilities`, `assets`
- Synonyms: `stockholders equity`, `shareholders equity`, `capital structure`, `leverage`, `current ratio`
- Abbreviations: `teq`, `liq`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `fnd6_teq` | `Company Fundamental Data for Equity` / `fundamental6` | Best first field for a leverage thesis because it is specific, interpretable, and materially less crowded than generic equity | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `1860` visible alphas |
| `assets` | `Company Fundamental Data for Equity` / `fundamental6` | Normalization anchor for an equity-to-assets ratio and a sign-control denominator | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `139739` visible alphas |
| `liabilities` | `Company Fundamental Data for Equity` / `fundamental6` | Direct leverage complement and the cleanest sign-control partner for an equity-cushion ratio | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `58422` visible alphas |
| `equity` | `Company Fundamental Data for Equity` / `fundamental6` | Backup equity field if `fnd6_teq` proves too specific or noisy | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `21438` visible alphas |
| `assets_curr` | `Company Fundamental Data for Equity` / `fundamental6` | Liquidity branch if the long-term leverage story is too stale | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `14466` visible alphas |
| `liabilities_curr` | `Company Fundamental Data for Equity` / `fundamental6` | Liquidity counterpart for a current-ratio branch | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `10165` visible alphas |

## Coverage And Quality Checks

- Coverage:
  The verified `fundamental6` balance-sheet fields all sit at `50%` coverage, so this lane starts with structural sparsity.
- Missingness:
  The sparsity looks family-wide rather than field-specific, which means expression tweaks alone will not solve Sub-universe risk.
- Region / delay compatibility:
  All candidate fields were confirmed on the official `USA / D1 / TOP3000` Data search pages in this session.
- Field type:
  All core candidates are `Matrix` fields, which keeps the ratio family easy to express.

## Baseline Expression Ideas

1. `group_rank(ts_rank(ts_mean(fnd6_teq / assets, 63), 504), industry)`
2. `group_rank(ts_rank(ts_mean(fnd6_teq / assets, 21), 504), industry)`
3. `group_rank(ts_rank(ts_mean(fnd6_teq / assets, 126), 504), industry)`

## Likely First Failure

- Sharpe:
  The ratio may simply behave like a slow value proxy with only modest edge.
- Fitness:
  Even a correct sign could still be too weak after industry neutralization.
- Turnover:
  This should probably be manageable because the inputs are slow fundamentals.
- Weight:
  Distressed names and sparse balance-sheet reporters may still concentrate the signal.
- Sub-universe:
  This remains a real risk because all core fields are only `50%` covered.
- Self-correlation:
  Likely lower than the operating-income ridge, but unknown until real checks exist.

## Next Action

- Which field should be tried first?
  `fnd6_teq`
- Which baseline expression should be simulated first?
  `group_rank(ts_rank(ts_mean(fnd6_teq / assets, 63), 504), industry)`
- Which 2-3 same-family variants should follow?
  Direct sign control with `liabilities / assets`, then the `21d` smoothing variant, then the `subindustry` structure variant before opening a liquidity fallback.

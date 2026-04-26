# Invested Capital History Position Field Search Pack

## Metadata

- Date: `2026-04-24`
- Topic: `invested_capital_history_position`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Companies sitting high in their own invested-capital history may represent a slower capital-deployment regime that can re-rank peers over a medium-slow horizon, and the live official Data Explorer check in this session confirms both a readable quarterly alias and a lower-crowding annual sibling on `fundamental6`.

## Why This Could Matter

- The current analyst-price near-neighbors in the live unsubmitted pool are blocked by self-correlation against `E5repQ81` and `d5l07rpX`, so the next research hour should move to a different information source.
- The killed `capital_structure_balance_sheet` lane was a leverage / liquidity thesis on `liabilities / assets`; this line is different because it tracks capital-deployment state rather than balance-sheet stress.
- The annual invested-capital sibling is materially less crowded than the standard quarterly alias, so it is the best first anchor for a distinct fundamentals follow-up.

## Data Explorer Search Terms

- Primary terms: `invested capital`, `capital total`, `icapt`
- Sibling terms: `working capital`, `capital expenditures`, `capex`
- Distinctness terms: `invested capital total annual`, `invested capital quarterly`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `fnd6_newa1v1300_icapt` | `fundamental6` / `Company Fundamental Data for Equity` | Best first anchor because it is the lower-crowding annual invested-capital sibling for this thesis | Live official search shows `SYMBOL`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Live official search shows `451` alphas and `221` users |
| `invested_capital` | `fundamental6` / `Company Fundamental Data for Equity` | Readable quarterly alias and the best direct sibling control for the same thesis | Live official search shows `SYMBOL`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Live official search shows `5,733` alphas and `1,559` users |
| `fnd6_newqv1300_icaptq` | `fundamental6` / `Company Fundamental Data for Equity` | Lower-crowding quarterly vendor field if the public alias is too crowded | Live official search shows `SYMBOL`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Live official search shows `674` alphas and `232` users |
| `working_capital` | `fundamental6` / `Company Fundamental Data for Equity` | Backup capital-state field only if invested-capital fails cleanly | Prior live official search in this session shows `SYMBOL`, `50%` coverage, `100%` date coverage | Prior live official search shows `5,325` alphas |

## Coverage And Quality Checks

- Coverage:
  All invested-capital siblings visible in the live official search are at `50%` coverage with `100%` date coverage, so sparse-accounting risk remains real.
- Missingness:
  This is not a full-coverage field family; the first batch should stay simple and should not assume broad coverage.
- Region / delay compatibility:
  The live official Data Explorer request was `USA / D1 / TOP3000`.
- Field type:
  The invested-capital candidates are `SYMBOL` fields on `fundamental6`.
- Crowding:
  `fnd6_newa1v1300_icapt` is meaningfully less crowded than `invested_capital`, so it should be the primary anchor while `invested_capital` serves as the sibling control.

## Baseline Expression Ideas

1. `group_rank(ts_rank(fnd6_newa1v1300_icapt, 252), industry)`
2. `group_rank(-ts_rank(fnd6_newa1v1300_icapt, 252), industry)`
3. `group_rank(ts_rank(invested_capital, 252), industry)`
4. `group_rank(ts_rank(fnd6_newa1v1300_icapt, 504), industry)`

## Likely First Failure

- Sharpe:
  The sign may still be ambiguous because higher invested capital can mean either productive reinvestment or capital bloat.
- Fitness:
  Half-coverage accounting fields can still weaken the branch after grouping.
- Turnover:
  This is unlikely to be the first blocker because the thesis is intentionally slow.
- Weight:
  Industry concentration is a real risk when only half the universe is covered.
- Sub-universe:
  This remains the main structural risk to watch before any packaging claim.
- Self-correlation:
  The family should be much farther from the submitted analyst-price pool, but the official check is still required.
- Units:
  Raw history-position transforms on accounting quantities can still emit VERIFY warnings, so the first batch must treat unit cleanliness as a real gate.

## Batch 01 Official Results

- Baseline `group_rank(ts_rank(fnd6_newa1v1300_icapt, 252), industry)` returned IS `Sharpe -0.25` / `Fitness -0.06`, failed `LOW_SHARPE`, `LOW_FITNESS`, and `LOW_SUB_UNIVERSE_SHARPE`, and emitted a `UNITS` warning.
- Sign-flip control `group_rank(-ts_rank(fnd6_newa1v1300_icapt, 252), industry)` fixed the sub-universe check, but still only reached IS `Sharpe 0.25` / `Fitness 0.06` with the same `UNITS` warning.
- Conclusion: this raw history-position family is frozen; do not spend more budget on the annual alias without a genuinely different normalization or a different capital-state source.

## Next Action

- Keep the invested-capital thesis on hold.
- If the capital-deployment idea is revisited, start from a normalized ratio or a different field family rather than continuing raw `ts_rank` polishing on the annual alias.

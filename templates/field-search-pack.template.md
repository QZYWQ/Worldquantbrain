# Field Search Pack Template

## Metadata

- Date:
- Topic:
- Region:
- Universe:
- Delay:

## Hypothesis

Write one plain-language hypothesis.

## Why This Could Matter

- What relative behavior are you trying to predict?
- Why might the market underreact, overreact, or mis-rank this information?
- Is this more likely a short-horizon or slow-horizon signal?

## Data Explorer Search Terms

- Primary terms:
- Synonyms:
- Abbreviations:

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| replace-me | replace-me | replace-me | replace-me | replace-me |

## Coverage And Quality Checks

- Coverage:
- Missingness:
- Region / delay compatibility:
- Competition route compatibility:
- Field type:

## New Dataset Quick Evaluation

Run these as diagnostic simulations with `None` neutralization and decay `0`.
Interpret `Long Count` + `Short Count` against the selected universe size; do not treat these diagnostics as alpha candidates.

| Diagnostic | Expression | What to inspect |
| --- | --- | --- |
| Raw coverage | `<datafield>` | Approximate field coverage |
| Non-zero coverage | `<datafield> != 0 ? 1 : 0` | Average daily non-zero availability |
| Update frequency | `ts_std_dev(<datafield>, N) != 0 ? 1 : 0` | Daily / weekly / monthly / quarterly update rhythm by varying `N` |
| Bounds | `abs(<datafield>) > X` | Whether values are bounded, normalized, or dominated by extremes |
| Long-window center | `ts_median(<datafield>, 1000) > X` | Five-year median / mean-style location checks |
| Distribution band | `X < scale_down(<datafield>) && scale_down(<datafield>) < Y` | Distribution mass across the normalized range |

## Baseline Expression Ideas

1. 
2. 
3. 

## Likely First Failure

- Sharpe:
- Fitness:
- Turnover:
- Weight:
- Sub-universe:
- Self-correlation:

## Next Action

- Which field should be tried first?
- Which baseline expression should be simulated first?
- Which 2-3 same-family variants should follow?

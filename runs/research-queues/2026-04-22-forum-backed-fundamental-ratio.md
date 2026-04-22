# Forum-Backed Fundamental Ratio Queue

- Date: `2026-04-22`
- Status: `active next branch`

## Current Decision

The operating-income smoothing ridge is dead on TEST, and the revenue, sentiment, capital-structure, price-volume, and pcr option branches have all been killed or downgraded to negative controls.

The next live branch should come from the forum-crawl KB candidate:

- `Fundamental / Model Slow Ratio`

## Next Live Lane

- Topic: `operating_income / sales`
- Reason: it uses two confirmed fields already available in the project evidence, and it is the simplest forum-backed slow-ratio family that has not yet been tested in this exact form.
- First batch shape: direct ratio baseline + `21d` / `63d` / `126d` smoothing variants, all with `252d` history rank and `industry` grouping.

## Branch Posture

- Keep the branch exploratory until real TEST behavior improves.
- Do not create a candidate-batch JSON unless `Check Submission` evidence appears and `subuniverse_pass` is non-null.
- If the new ratio family fails the same way as the prior operating-income ridge, kill it quickly and return to the forum crawl for a different KB candidate.


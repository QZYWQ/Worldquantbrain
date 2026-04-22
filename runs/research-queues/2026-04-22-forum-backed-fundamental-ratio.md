# Forum-Backed Fundamental Ratio Queue

- Date: `2026-04-22`
- Status: `killed / fallback pending`

## Current Decision

The operating-income / sales ratio ridge is dead on TEST, and the revenue, sentiment, capital-structure, price-volume, and pcr option branches remain killed or downgraded to negative controls.

The `event_trigger_low_turnover_volume_gate` lane has now been killed on live evidence, so the queue is no longer pointing at an active branch.

The next live branch should come from the forum-crawl KB candidates, but the exact fallback family is still pending review.

## Branch Posture

- Keep any new branch exploratory until real TEST behavior improves.
- Do not create a candidate-batch JSON unless `Check Submission` evidence appears and `subuniverse_pass` is non-null.
- Return to the forum crawl for a different KB candidate if the next fallback lane fails the same way as the prior dead lanes.

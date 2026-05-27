# Project Learning Loop: New Dataset Quick Evaluation

## Metadata

- Date: 2026-05-02
- Source post: `https://support.worldquantbrain.com/hc/en-us/community/posts/11807866133911--BRAIN-TIPS-6-ways-to-quickly-evaluate-a-new-dataset`
- Source snapshot: `runs/forum-crawl/2026-04-22-support-worldquantbrain/raw/pages/hc-en-us-community-posts-11807866133911-BRAIN-TIPS-6-ways-to-quickly-evaluate-a-new-dataset-51955fc6ac.txt`
- Snapshot fetched at: `2026-04-22T10:25:51+0800`
- Current access note: direct unauthenticated fetch redirected to restricted access; browser read was not used for any posting, form submission, or account change.

## Reusable Takeaway

Before spending a family budget on an unfamiliar datafield, run a diagnostic pack that treats the field as data to inspect, not as an alpha candidate.

Use `None` neutralization and decay `0`, then inspect `Long Count` and `Short Count` in the IS Summary:

- `<datafield>` for approximate coverage versus universe size.
- `<datafield> != 0 ? 1 : 0` for daily non-zero availability.
- `ts_std_dev(<datafield>, N) != 0 ? 1 : 0` for update frequency by varying `N`.
- `abs(<datafield>) > X` for bounds and normalization checks.
- `ts_median(<datafield>, 1000) > X` for long-window center checks.
- `X < scale_down(<datafield>) && scale_down(<datafield>) < Y` for normalized distribution bands.

## Project Changes Made

- Added the diagnostic pack to `templates/field-search-pack.template.md` under `New Dataset Quick Evaluation`.
- Added the same workflow to the WorldQuant skill reference `references/idea-generation-and-field-discovery.md`.

## Carry-Forward Rules

- A new dataset should not enter expression-family mining until the field-search pack records coverage, non-zero coverage, update rhythm, bounds, and distribution notes.
- Diagnostic expressions are not alpha candidates and should not be routed into candidate batches.
- If diagnostics show stale updates, sparse coverage, impossible bounds, or lopsided distribution, narrow the hypothesis or change fields before variant generation.
- Forum comments suggest adding skewness and kurtosis as future automation candidates, but that remains a `HOLD` item until backed by a project script or repeated use.

## Boundaries

- This does not confirm current account access to any specific field.
- This does not change official submission thresholds.
- This does not replace official simulation or Check Submission evidence.

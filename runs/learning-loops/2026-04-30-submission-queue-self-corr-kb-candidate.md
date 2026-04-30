# KB Candidate: Submission Queue And Self-Correlation Recheck

## Scope

This is candidate material for the external knowledge base. It abstracts the latest success / failure pair into submission workflow rules rather than promoting any single field as a durable alpha recipe.

## Evidence Trace

- Submitted success: `Xg2X2jxl`, `rank(ts_mean(anl4_totassets_flag, 20))`
- Stopped failure: `zqPX5OkX`, close-delta / close-volume-correlation branch
- Key failure message: `Self-correlation 0.9896 is above cutoff of 0.7 and Sharpe not better by 10.0% or more.`

## Candidate KB Rule

When building a submission queue, a candidate with all visible checks passing but `SELF_CORRELATION: PENDING` should be labeled `near-pass`, not `submit-ready`.

After each successful submission:

- treat the submitted set as changed
- re-check remaining candidates against the new submitted set
- do not assume formula-level family differences are enough
- stop branches that fail self-correlation far above the cutoff

## Candidate KB Checklist

Before submitting the second candidate in a pair:

- Is its information source genuinely different?
- Is the self-correlation check completed against the current submitted set?
- Is Sub-universe comfortably above the cutoff, or exactly at the line?
- Is Fitness robust enough, or only barely above `1.0`?
- Is the candidate just a nearby sibling of a stopped branch?

## Boundary

This rule should not be written as:

- "`anl4_totassets_flag` is always good"
- "price-volume correlation is always bad"
- "different formula family means safe to submit"

The durable method is the queue discipline: submit the stronger orthogonal candidate first, then re-check the rest.

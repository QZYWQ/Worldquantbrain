# Offline Broad Search Workflow

- Date: 2026-04-28
- Scope: workflow and shortlist design only
- Simulations run: none
- Simulation endpoint called: no
- Miner source repo: `/Users/zpdedn/Documents/github/worldquant-miner`
- Miner artifacts:
  - `manual_alphas/2026-04-28_offline_candidate_seed_pool_DO_NOT_RUN.json`
  - `manual_alphas/2026-04-28_offline_shortlist_DO_NOT_RUN.json`
  - `tools/build_offline_candidate_shortlist.py`

## Why Manual Seed Lanes Stopped

Six post-E5 exploration lanes have not produced a hopeful second alpha. The
near-E5 close/volume correlation branch is closed, and the second through sixth
manual batches each failed on Sharpe, Fitness, turnover, concentration, or
sub-universe checks. The sixth batch confirmed that single-point seeds in fresh
field families are still too quota-expensive when they are not pre-triaged.

The next useful unit of work is therefore not another three-name simulation
batch. It is a broad offline search step that creates many structurally
different expressions, removes obvious repeats and failed-family neighbors, and
leaves only a small human-review shortlist.

## What The New Miner Workflow Does

The miner now has a local-only shortlist builder:

`tools/build_offline_candidate_shortlist.py`

It accepts explicit candidates and deterministic planning templates. For this
first run, the seed pool expands to 182 candidate expressions before filtering.
The tool then performs:

- syntax and bracket sanity checks
- simple operator-shape checks
- field legality checks when `verified_fields` metadata is available
- normalized expression and fingerprint generation
- duplicate fingerprint and duplicate normalized-expression removal
- hard-negative filters for E5 neighbors and known failed families
- heuristic risk scoring
- family classification and clustering
- a cap of at most two representatives per family

The output shortlist is planning-only JSON with `do_not_run: true` and
`simulation_status: not_run`.

## What It Does Not Do

- It does not read credential files.
- It does not import or instantiate the miner simulation runner.
- It does not call Codex.
- It does not call WorldQuant endpoints.
- It does not write `ledger.csv`, `fingerprints.json`, `hopeful_alphas.json`,
  `results/`, or run logs.
- It does not create a runnable manual-alpha batch.

## Failed-Family Avoidance

The hard-negative layer rejects or blocks candidates matching:

- E5 close/volume correlation reversal neighbors
- `ts_corr(rank(close), rank(volume), 60/70/80/90)` style structures
- close60 reversal, including volatility/range or volume-ratio conditioners
- simple cashflow/assets plus revenue/assets stability
- raw `anl4_mark`
- raw single-field analyst disagreement
- raw fast social sentiment
- raw short-interest delta
- simple corporate action/debt/buyback bundles
- failed sixth-batch option forward curve slope
- failed sixth-batch Ravenpack credit/dividend aggregate
- failed sixth-batch model51 unsystematic-risk plus beta expression

The first run included explicit negative controls for those filters. They were
removed before shortlisting.

## Scoring

The heuristic score is transparent and local. It rewards:

- multi-field composites
- preferred offline families
- medium-horizon windows
- group neutralization
- decay smoothing
- non-price acceleration components
- listed verified fields

It penalizes:

- short-window turnover risk
- excessive expression complexity
- missing group neutralization
- unverified fields
- option/news coverage risk
- possible price/volume unit mixing

These are not performance metrics. They are only pre-simulation triage signals.

## First Shortlist Run

- Input candidates after template expansion: 182
- Candidates after hard filters and dedupe: 176
- Shortlisted after family caps: 14
- Simulations run: none

The top shortlist families are:

- accruals / asset growth / balance-sheet acceleration
- forecast dispersion and earnings revision
- valuation plus quality acceleration
- option positioning / volatility
- insider or ownership proxy
- Ravenpack slow aggregate
- risk-model composite with non-risk overlay

## Later Manual Simulation Conversion

When simulation budget is explicitly approved in a future task:

1. Review `manual_alphas/2026-04-28_offline_shortlist_DO_NOT_RUN.json`.
2. Pick at most three expressions.
3. Prefer different families rather than adjacent variants inside one family.
4. Create a new manual seed batch JSON with an `alphas` list.
5. Keep the batch capped at three names.
6. Run the existing manual runner only in that future approved task.
7. Stop the family if no candidate reaches the hopeful threshold.

Do not use the DO_NOT_RUN shortlist file directly as runner input.

## Recommendation

Use the shortlist as the next review queue, not as a run queue. The next useful
step is to manually choose one representative each from valuation/quality,
forecast-dispersion, and one fresh alternative family, then prepare a tiny
future batch only after explicit approval to spend simulation quota.

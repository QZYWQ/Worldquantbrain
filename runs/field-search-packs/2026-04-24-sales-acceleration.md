# Sales Acceleration Field Search Pack

## Metadata

- Date: `2026-04-24`
- Topic: `sales_acceleration`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-21-sales-delta-fundamental.md`
  - `./runs/simulation-captures/2026-04-21-sales-delta-fundamental-batch-02.json`
  - `./runs/submission-memos/2026-04-24-capital-structure-ratio-closure.md`

## Hypothesis

A second-difference top-line signal may capture acceleration in sales growth earlier than a simple delta or smoothing lane, and that shape could be distinct enough to justify one small batch after the raw revenue-delta branch and the smoothed revenue branch both failed to reach candidate quality.

## Why This Could Matter

- This is a real lever change, not just more smoothing on a dead revenue line.
- The first-difference top-line family was weak, so testing the second derivative is the cleanest way to decide whether "acceleration" adds anything new.
- If the market already prices raw sales changes, the change in the change may be the only part left with a usable cross-sectional edge.
- The branch is still interpretable and stays inside the same slow fundamentals regime, which makes it easier to debug than a broader operator redesign.

## Data Explorer Search Terms

- Primary terms: `sales`, `revenue`, `top line`
- Mechanics terms: `acceleration`, `second difference`, `delta delta`, `growth change`
- Sibling terms: `operating income`, `net sales`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `revenue` | `Company Fundamental Data for Equity` / `fundamental6` | Best first anchor because the prior sales-delta family already confirmed this field and showed it is less crowded than `sales` | Earlier official search in this session showed `Matrix`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Earlier official search showed `12460` visible alphas |
| `sales` | `Company Fundamental Data for Equity` / `fundamental6` | Direct synonym control if the revenue acceleration branch is noisy or oddly shaped | Earlier official search in this session showed `Matrix`, `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | Earlier official search showed `34724` visible alphas, materially more crowded than `revenue` |

## Coverage And Quality Checks

- Coverage:
  The already-confirmed top-line fields sit at `50%` coverage, so this branch still has structural sparsity risk.
- Missingness:
  This is still a sparse fundamentals family, so the first batch should stay compact and diagnostic.
- Region / delay compatibility:
  The confirmed top-line field search was `USA / D1 / TOP3000`.
- Field type:
  Both candidate fields are `Matrix` fields on `fundamental6`.
- Distinctness:
  This family differs from the dead revenue-smoothing lane because it tests second-difference structure, not just a different window.

## Baseline Expression Ideas

1. `group_rank(ts_delta(ts_delta(revenue, 63), 63), industry)`
2. `group_rank(ts_delta(revenue, 63), industry)`
3. `group_rank(ts_delta(ts_delta(revenue, 21), 21), industry)`
4. `group_rank(ts_delta(ts_delta(revenue, 126), 126), industry)`

## Likely First Failure

- Sharpe:
  The acceleration term may be too noisy and simply collapse into a weak momentum proxy.
- Fitness:
  Even if the sign is right, the family may still be too weak after industry neutralization.
- Turnover:
  This should remain low if the signal is real, so turnover is probably not the first blocker.
- Weight:
  Sparse top-line reporters may still concentrate the signal in a small set of industries.
- Sub-universe:
  Still a live risk because the confirmed top-line fields are only half covered.
- Self-correlation:
  Unknown until a real official check exists.

## Next Action

- Open the family with the 63d second-difference baseline.
- Test the first-difference control immediately after that.
- If neither line is materially better than the dead revenue family, kill the acceleration lane quickly and move on.

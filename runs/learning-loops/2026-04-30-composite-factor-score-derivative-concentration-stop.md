# Composite Factor Score Derivative Concentration Stop

## Metadata
- Date: 2026-04-30
- Scope: project-level stop / learning-loop note
- Evidence source: user-provided official WorldQuant BRAIN screenshots, cached Data Explorer field metadata, and fresh official API recheck
- Fresh API recheck: run on 2026-04-30 against `https://api.worldquantbrain.com/users/self/alphas?status=UNSUBMITTED`
- Official API recheck scope: 905 unsubmitted alphas, 23 matching `composite_factor_score_derivative`

## Expression

```text
ts_zscore(composite_factor_score_derivative, 20)
```

## Field Metadata

Cached official Data Explorer metadata from `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`:

- Field: `composite_factor_score_derivative`
- Description: Change in overall composite factor score from the prior period.
- Dataset: `model16` / Fundamental Scores
- Category: Model / Valuation Models
- Type: MATRIX
- Coverage: `1.0`
- Date coverage: `1.0`
- Visible users: `76`
- Visible alphas: `113`

The field itself is not sparse. The problem is the expression's resulting portfolio shape.

## Observed Runs

### Current visible run

Settings shown by user:

- USA / TOP3000 / Fast Expression
- Decay: `0`
- Delay: `1`
- Truncation: `0.08`
- Neutralization: `Sector`
- Pasteurization: `On`

Metrics:

- Sharpe: `2.50`
- Fitness: `5.22`
- Returns: `54.46%`
- Turnover: `7.87%`
- Drawdown: `7.98%`
- Margin: `138.40 bps-equivalent display`

Official visible checks:

- `LOW_SHARPE`: PASS
- `LOW_FITNESS`: PASS
- `LOW_TURNOVER`: PASS
- `HIGH_TURNOVER`: PASS
- `MATCHES_COMPETITION`: PASS
- `CONCENTRATED_WEIGHT`: FAIL, `50% > 10%`
- `LOW_SUB_UNIVERSE_SHARPE`: FAIL, `0.87 / 1.08`
- `SELF_CORRELATION`: PENDING

Year-level warning sign:

- 2019 has only `0` long and `5` short names.
- 2020-2023 show effectively `0 / 0` long-short counts in the visible table.

This is not a broad alpha. It is a tiny concentrated short basket with strong aggregate metrics.

### Earlier stronger-looking run

Earlier user screenshot of the same expression with different settings:

- Decay: `5`
- Truncation: `0.05`
- Neutralization: `Sector`

Metrics:

- Sharpe: `3.78`
- Fitness: `9.54`
- Returns: `79.58%`
- Turnover: `10.63%`
- Drawdown: `2.55%`

Visible failure:

- `CONCENTRATED_WEIGHT`: FAIL, `50% > 10%`

Sub-universe passed in that run, but the hard concentration failure remained. The 2019-only / very few-name behavior was still visible.

### Truncation 0.01 follow-up

The user also checked a lower truncation variant. It improved or preserved headline aggregate metrics but did not change the core decision: the line remained structurally unsuitable because the signal concentrates into too few instruments.

### Fresh official API recheck

On 2026-04-30, a fresh official API recheck found 23 unsubmitted variants containing `composite_factor_score_derivative`. This shows the lane has already had a broad rescue attempt, not just one or two UI checks.

High Sharpe / high Fitness variants all kept failing concentration:

| Alpha | Expression | Main settings | Sharpe | Fitness | Returns | Turnover | Breadth | Key failure |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `RR2XQ89d` | `ts_zscore(composite_factor_score_derivative, 20)` | Decay 5, Trunc 0.05, Sector | 3.78 | 9.54 | 79.58% | 10.63% | 1 long / 11 short | `CONCENTRATED_WEIGHT` 0.50 / 0.10 |
| `9qaomYb9` | `ts_zscore(composite_factor_score_derivative, 20)` | Decay 0, Trunc 0.08, Sector | 2.50 | 5.22 | 54.46% | 7.87% | 0 long / 11 short | `CONCENTRATED_WEIGHT` 0.50 / 0.10; Sub-universe 0.87 / 1.08 |
| `RR2XMnlb` | `ts_zscore(composite_factor_score_derivative, 20)` | Decay 0, Trunc 0.08, Industry | 2.31 | 4.75 | 52.81% | 8.06% | 0 long / 4 short | `CONCENTRATED_WEIGHT` 0.50 / 0.10 |
| `ZY2ZMKRn` | `ts_zscore(composite_factor_score_derivative, 20)` | Decay 0, Trunc 0.05, Industry | 2.31 | 4.75 | 52.95% | 8.08% | 0 long / 4 short | `CONCENTRATED_WEIGHT` 0.50 / 0.10 |

Breadth/rank attempts did not solve the hard failure:

| Alpha | Expression | Sharpe | Fitness | Breadth | Key failure |
| --- | --- | ---: | ---: | --- | --- |
| `akAJeKo2` | `rank(ts_zscore(ts_backfill(composite_factor_score_derivative, 252), 20))` | 3.97 | 10.25 | 1 long / 11 short | `CONCENTRATED_WEIGHT` 0.50 / 0.10 |
| `QP2eOklr` | same expression, lower truncation | 3.93 | 10.07 | 1 long / 11 short | `CONCENTRATED_WEIGHT` 0.50 / 0.10 |
| `qMPbYbjE` | `group_rank(ts_zscore(ts_backfill(composite_factor_score_derivative, 252), 20), industry)` | 3.88 | 8.86 | 3 long / 8 short | `CONCENTRATED_WEIGHT` 0.50 / 0.10; Sub-universe 1.02 / 1.68 |
| `rKJkLzVJ` | `rank(ts_zscore(composite_factor_score_derivative, 20))` | 1.27 | 1.48 | 1 long / 5 short | `CONCENTRATED_WEIGHT` 0.50 / 0.10; Sub-universe 0.42 / 0.55 |

Other transforms either kept concentration or killed performance:

- `sign(ts_zscore(...)) * ts_mean(abs(ts_zscore(...)), 10)` improved concentration from `0.50` to about `0.347`, but still failed the `0.10` cutoff.
- `quantile(composite_factor_score_derivative, driver="uniform", sigma=1.0)` passed concentration with broad breadth, but Sharpe `-0.76` and Fitness `-0.51`.
- `ts_mean(composite_factor_score_derivative, 180)` passed concentration with broad breadth, but Sharpe `-0.74`, Fitness `-0.45`, and low turnover `0.54%`.
- `ts_zscore(rank(composite_factor_score_derivative), 20)` created broad long/short counts, but Sharpe `-0.36` and Fitness `-0.12`.

### Final max-position diagnostic

A final official diagnostic attempted to submit the best baseline with `maxPosition: ON`:

```json
{
  "regular": "ts_zscore(composite_factor_score_derivative, 20)",
  "settings": {
    "decay": 5,
    "neutralization": "SECTOR",
    "truncation": 0.05,
    "maxPosition": "ON"
  }
}
```

The platform accepted the simulation request (`201`) as simulation `23KzC03VS4iEcmEwIq5z7mt`, but the completed official response normalized `maxPosition` back to `OFF` and returned existing alpha `RR2XQ89d`. Therefore `maxPosition` was not a usable rescue lever for this line.

Two additional max-position rescue submissions were blocked by the official API with `CONCURRENT_SIMULATION_LIMIT_EXCEEDED` (`429`), so no further official budget was spent after the first diagnostic proved that the setting was normalized away.

## Diagnosis

This is a high-metric but non-submittable concentration artifact.

The issue is not field coverage and not ordinary Sharpe / Fitness weakness. The output portfolio is too narrow:

- weight concentration reaches `50%`, far above the `10%` cutoff
- long / short counts collapse to a handful of names
- most years have no meaningful breadth
- changing truncation / decay did not produce a broad portfolio
- rank, backfill, group rank, sign/abs, quantile, smoothing, and final max-position diagnostics did not produce a passable broad positive alpha

High Sharpe and high Fitness here are misleading because the alpha is not distributed across the universe.

## Decision

Stop this expression as a submission candidate.

Stop the broader `composite_factor_score_derivative` rescue lane as well. The current official evidence is:

- concentrated high-performance versions are not submittable
- broad versions lose Sharpe/Fitness or turnover
- the last setting-level rescue path was normalized away by the platform
- additional same-family submissions are a poor use of official simulation budget

Do not spend more rescue budget on cosmetic variants of:

```text
ts_zscore(composite_factor_score_derivative, N)
```

Do not treat higher Sharpe / Fitness variants as improvements unless they first fix:

1. `CONCENTRATED_WEIGHT`
2. Long / short breadth
3. Sub-universe Sharpe

## Reopen Criteria

Do not reopen this exact lane unless there is a genuinely new mechanism, not a cosmetic same-field edit. Acceptable reopen triggers:

- a different field in the same model16 family that has natural cross-sectional breadth
- a new data source that explains the same thesis without the tiny-name concentration
- a platform setting or operator path that demonstrably changes concentration without reverting to the old result

The already-tested breadth controls are no longer enough reason to reopen.

## Reusable Lesson

For WQB research, a high Sharpe / high Fitness alpha with:

- `CONCENTRATED_WEIGHT` failure,
- `50%` single-name or small-basket weight,
- very low long / short counts,
- and multi-year zero breadth

should be treated as a structural concentration failure, not as a near-pass candidate.

Do not rank such lines above lower-Sharpe alphas that have real breadth and pass concentration.

If a field has full coverage but the expression produces only a handful of active names, treat the failure as portfolio-shape structural, not as field coverage. The rescue rule is:

1. Try breadth-forcing normalization once or twice.
2. If concentration still fails, stop.
3. If concentration passes only when Sharpe/Fitness collapse, stop.
4. Move budget to an orthogonal family instead of chasing headline Sharpe.

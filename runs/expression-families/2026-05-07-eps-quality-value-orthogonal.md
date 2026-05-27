# 2026-05-07 EPS Quality Value Orthogonal Family

## Metadata

- Date: `2026-05-07`
- Topic: `eps_quality_value_orthogonal`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Source line: `multiply(add(eps, 50), 50, filter=true)`

## Hypothesis

The warning line suggests that raw `eps` value is not the clean edge. The useful signal may be that companies with more complete EPS coverage and stronger earnings yield are easier for the market to re-rank inside industry groups.

This family therefore avoids direct scalar addition to `eps` and tests unit-clean components:

- EPS earnings yield: `eps / close`
- EPS information quality: `-ts_count_nans(eps, 252)`
- Industry-relative ranking after time-series normalization

## Prior Evidence

- Original warning line `xAPrqaxg`: Sharpe `1.31`, Fitness `1.43`, Sub-universe Sharpe `0.87`, Self-correlation `0.5611`, with `UNITS` warning.
- Unit-clean raw EPS controls failed: `multiply(eps, 50, filter=true)` and `multiply(ts_backfill(eps, 252), 50, filter=true)` both failed low Sharpe / Fitness.
- Explicit EPS completeness `group_rank(-ts_count_nans(eps, 252), industry)` had Sharpe `1.53` and Fitness `1.60`, but failed Sub-universe Sharpe.
- Older actual-EPS price-normalized family had viable IS shapes but was blocked by self-correlation, so this batch avoids `anl4_af_eps_value / close` near-neighbors.

## Settings

- Instrument type: `EQUITY`
- Region: `USA`
- Universe: `TOP3000`
- Language: `FASTEXPR`
- Decay: `0`
- Delay: `1`
- Truncation: `0.08`
- Neutralization: `INDUSTRY`
- Pasteurization: `ON`
- Unit handling: `VERIFY`
- NaN handling: `OFF`
- Max Trade: `OFF`
- Max Position: `OFF`
- Test period: `P5Y0M0D`

## Baseline

Test whether built-in `eps` becomes viable after price normalization.

```text
group_rank(ts_rank(eps / close, 60), industry)
```

## Sign Control

Confirm thesis direction before spending more budget.

```text
group_rank(-ts_rank(eps / close, 60), industry)
```

## Variant 1

Combine EPS completeness with earnings yield. This is the direct follow-up to the warning insight.

```text
group_rank(multiply(ts_rank(eps / close, 60), -ts_count_nans(eps, 252)), industry)
```

## Variant 2

Test improving earnings yield rather than level. This is more orthogonal to the older actual-EPS level family.

```text
group_rank(ts_rank(ts_delta(eps / close, 63), 252), industry)
```

## Expected First Failure

- Sharpe / Fitness: built-in `eps` may remain weaker than dedicated actual-EPS fields.
- Sub-universe: completeness signals have already shown sub-universe fragility.
- Self-correlation: the earnings-yield baseline may still overlap existing value/EPS alphas.
- Units: this batch should avoid the scalar-addition warning, but live checks must confirm.

## Decision Rule

- If all four fail Sharpe/Fitness, stop the built-in `eps / close` branch.
- If baseline is negative, compare only against the sign control before any extra variants.
- If one variant passes IS but fails Sub-universe, allow at most two targeted rescue variants.
- If one variant passes all visible gates but self-correlation fails, branch to a materially different mechanism instead of 60/120d polishing.

## Rescue Batch

The first live batch found one strong but non-submittable candidate:

```text
group_rank(multiply(ts_rank(eps / close, 60), -ts_count_nans(eps, 252)), industry)
```

Live result: Sharpe `1.54`, Fitness `1.57`, Turnover `12.30%`, but Sub-universe Sharpe `0.37 / 0.67` failed.

The most likely issue is scale/skew from multiplying a 0-1 rank by a raw missing-count value. The rescue therefore changes only the combination normalization:

```text
group_rank(multiply(group_rank(ts_rank(eps / close, 60), industry), group_rank(-ts_count_nans(eps, 252), industry)), industry)
```

```text
group_rank(add(group_rank(ts_rank(eps / close, 60), industry), group_rank(-ts_count_nans(eps, 252), industry)), industry)
```

## Fitness Repair Batch

The additive ranked rescue completed after the first polling window:

```text
group_rank(add(group_rank(ts_rank(eps / close, 60), industry), group_rank(-ts_count_nans(eps, 252), industry)), industry)
```

Live result: Sharpe `1.59`, Fitness `0.83`, Turnover `27.68%`, Sub-universe Sharpe `1.30 / 0.69`. The only hard failure is now `LOW_FITNESS`.

Fitness repair is bounded to two low-turnover levers:

- Increase the earnings-yield rank window from `60` to `120`.
- Keep the expression fixed but set simulation `decay` to `4`.

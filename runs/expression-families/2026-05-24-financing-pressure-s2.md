# Financing Pressure S2 Expression Family

## Hypothesis

Within comparable industries, firms with heavier debt burden, rising accrued liabilities, near-term maturity pressure, or costly debt issuance should underperform firms with lighter obligation pressure. The signal should be slow, balance-sheet driven, and low-turnover.

## Competition Route

`D1-first`.

Reason: all current project evidence for this family is USA / TOP3000 / Delay 1. Delay 0 has been blocked or account-sensitive in prior lanes, so the 24h batch should first improve the verified D1 lane.

## Source Evidence

- `runs/overnight-mining/2026-05-23-financing-pressure-24h/report.md`
- `runs/overnight-mining/2026-05-23-financing-pressure-24h/upgrade-potential-candidates.json`
- `runs/research-queues/2026-05-24-financing-pressure-upgrade-favorite/report.md`
- `runs/submission-memos/2026-05-24-submit-best-and-postcheck.md`

## Confirmed Anchor

`E5kobRlG`

```text
group_rank(reverse(ts_rank(divide(winsorize(ts_backfill(debt_carrying_value, 252), std=4), add(abs(winsorize(ts_backfill(assets, 252), std=4)), 1)), 126)), subindustry)
```

Recorded metrics from the project artifact:

- Sharpe `1.58`
- Fitness `1.13`
- Turnover `0.0406`
- Sub-universe Sharpe `1.05`
- Self-correlation `0.6147`
- Check posture: 8/8 PASS before this planning memo

## Field Plan

Primary fields:

- `debt_carrying_value`: debt burden level
- `current_accrued_liabilities`: short-term obligation pressure
- `current_accrued_liabilities_total`: short-term obligation pressure alternate
- `accrued_liabilities_total`: broader accrued obligation pressure
- `debt_maturities_repayments_year2`: maturity wall pressure
- `debt_issuance_costs_total`: financing friction
- `taxes_payable_total_value`: near-term tax payable burden

Use `assets` as the baseline denominator, then `sales` as the first economically meaningful denominator branch. Use `cap` only for low-crowding exploratory branches because it changes the mechanism into market-value pressure.

## Baseline Shape

```text
group_rank(reverse(ts_rank(debt_or_obligation_pressure / assets, 126)), subindustry)
```

Implementation guardrails:

- Always use `winsorize(ts_backfill(field, 252), std=4)` before ratio construction.
- Normalize by `add(abs(denominator), 1)` to avoid unstable division.
- Rank before combining fields.
- Do not mix more than two balance-sheet inputs in one alpha.

## Variant Axes

### Axis 1: Debt Level

Purpose: test whether the anchor survives a longer ranking window, different denominator, or different group frame.

- `debt_carrying_value / assets`, rank `168`, subindustry
- `debt_carrying_value / assets`, rank `252`, subindustry
- `debt_carrying_value / sales`, rank `168`, industry
- `debt_carrying_value / sales`, rank `168`, subindustry

### Axis 2: Pressure Change

Purpose: test whether rising obligation pressure is stronger than static debt level.

- `current_accrued_liabilities / assets`, smoothed `66`, delta `252`, z-score `90/120/150`, industry
- `debt_issuance_costs_total / assets`, smoothed `66`, delta `252`, z-score `120`, industry
- `taxes_payable_total_value / assets`, smoothed `66`, delta `252`, z-score `120`, industry

### Axis 3: Mechanism Confirmation

Purpose: lower self-correlation by requiring two related but distinct obligations to agree.

- debt carrying value + accrued liabilities total
- debt carrying value + current accrued liabilities
- maturity wall + current accrued liabilities
- debt issuance costs + taxes payable

### Axis 4: Group Frame

Purpose: test whether the signal is industry-relative or subindustry-relative.

- Use `subindustry` for debt level, because the anchor passed there.
- Use `industry` first for pressure-change variants, because current-accrued-liability pressure was near-pass there.
- Try the alternate group only after the first group is not structurally weak.

## Main Risks

- Self-correlation: `E5kobRlG` is already at `0.6147`, leaving limited room.
- Fitness: `d5deq8bX` was near-pass but Fitness `0.99`, so targeted rescue must be bounded.
- Sub-universe: composite obligation branches can pass Sharpe but have weak SubU; do not hide that with same-source tweaks.
- Coverage: several liability fields are sparse; field-health diagnostics are evidence about data quality, not candidate quality.

## Optimization Order

1. Run untested upgrade candidates from the previous blocked run.
2. If a branch is negative, immediately simulate the final-expression sign flip.
3. If Sharpe passes but Fitness is below `1.0`, try one smoothing/window rescue.
4. If SubU fails, try one group-frame rescue.
5. If self-correlation fails against `E5kobRlG` or later submitted debt-burden line, branch to a new obligation field rather than changing windows.

## Stop Rules

- Stop any field branch after two targeted rescues with the same dominant failure.
- Do not mine operating-profitability/FCF siblings inside this 24h run.
- Do not use price-only rows as rescue candidates for this family.
- Do not submit from the batch runner; submission requires a separate memo and fresh official checks.

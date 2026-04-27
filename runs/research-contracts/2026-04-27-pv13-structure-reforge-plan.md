# pv13 Structural Reforge Plan

## Goal

Test whether the pv13 customer-centrality lane can recover Sharpe by adding the structural layers identified in RECURVE round 2:
- peer context via `group_rank`
- state construction via `ts_mean` or a ratio form before the final rank

## Baseline To Beat

- Current working best: `ts_rank(pv13_ustomergraphrank_page_rank, 150)`
- Best known metrics: TEST Sharpe `1.01`, Fitness `1.77`
- Failure mode: official E-stage rejected the lane on `LOW_SHARPE`

## Candidate Queue

| Priority | Expression | Intent | Dedupe result |
|---|---|---|---|
| P0 | `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 150), industry)` | Minimum-change peer context overlay | PASS; no exact/normalized/structural duplicate found |
| P1 | `group_rank(ts_rank(ts_mean(pv13_ustomergraphrank_page_rank, 63), 252), industry)` | Slow state construction before peer ranking | PASS; no exact/normalized/structural duplicate found |
| P2 | `ts_rank(group_rank(pv13_ustomergraphrank_page_rank / pv13_com_page_rank, industry), 90)` | Ratio-style relationship strength plus peer context | PASS; no exact/normalized/structural duplicate found |

## Platform Settings

- Region: USA
- Universe: TOP3000
- Delay: 1
- Neutralization: None
- Language: Fast Expression
- Test period: 1Y
- Pasteurization: On
- Unit handling: Verify
- Nan handling: On
- Decay: default page value (currently 0 in the live simulate UI)

## Execution Order

1. Run P0 first.
2. If P0 improves TEST Sharpe by at least 0.1 and keeps Fitness at or above 1.4, treat it as a meaningful improvement and continue with P1.
3. Run P1 next.
4. Run P2 last.
5. If any variant shows Sharpe lift but Fitness drops by more than 0.2, consider one decay micro-tweak on that branch only, capped so total simulations stay within budget.

## Stop Rules

- If a candidate falls below TEST Sharpe 0.8, stop that branch.
- If a candidate triggers high turnover or another hard risk label, stop that branch.
- Do not introduce any field outside pv13.

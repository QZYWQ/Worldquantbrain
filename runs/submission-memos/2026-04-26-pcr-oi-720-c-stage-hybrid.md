# 2026-04-26 pcr_oi_720 C-Stage Hybrid Review

## Decision

- Advance `pcr_oi_720` to D stage.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.
- Use the 60d analyst-horizon hybrid as the branch lead for the next stage.

## Official Evidence

- `runs/expression-families/2026-04-26-pcr-oi-720-c-stage.md`
- `runs/submission-memos/2026-04-26-pcr-oi-720-b-stage-advance.md`
- `runs/simulation-captures/2026-04-26-pcr-oi-720-c-stage-anl4-af-eps-batch-01.json`
- Official Data Explorer search result for `anl4_af_eps_value`
  - `https://platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=anl4_af_eps_value&universe=TOP3000`

## C-Stage Results

- 20d analyst-horizon hybrid `group_rank(ts_rank(signed_power(ts_rank(pcr_oi_720, 20), 2), 20) + ts_rank(anl4_af_eps_value / close, 20), industry)`
  - IS: `Sharpe 1.09 / Fitness 0.46`
  - TEST: `Sharpe 0.91 / Fitness 0.31`
- 60d analyst-horizon hybrid `group_rank(ts_rank(signed_power(ts_rank(pcr_oi_720, 20), 2), 20) + ts_rank(anl4_af_eps_value / close, 60), industry)`
  - IS: `Sharpe 1.32 / Fitness 0.64`
  - TEST: `Sharpe 0.99 / Fitness 0.37`
- 120d analyst-horizon hybrid `group_rank(ts_rank(signed_power(ts_rank(pcr_oi_720, 20), 2), 20) + ts_rank(anl4_af_eps_value / close, 120), industry)`
  - IS: `Sharpe 1.08 / Fitness 0.48`
  - TEST: `Sharpe 0.77 / Fitness 0.24`

## Conclusion

- The orthogonal analyst-estimate leg clearly improves the B-stage leader.
- The 60d variant is the best continuation by TEST Sharpe and also has the strongest IS read in the batch.
- All three variants clear the C-stage TEST floor, but the 60d variant is the branch lead.
- No multi-test correction script is present locally, so the comparison was manual.

## Next Hop

- Prepare the D-stage delay / robustness scan from the 60d winner.
- Keep the lane interpretable and avoid touching unrelated smoothing levers yet.

## Status

- `advance`
- `continue`

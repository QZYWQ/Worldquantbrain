# Qwen vs MiniMax Offline Comparison

No WorldQuant API calls were made in this comparison. Only local cached fields/operators and LLM/API generation were used.

## Summary Table

| Metric | Qwen3.6 27B local | MiniMax-M2.7 API |
|---|---:|---:|
| Candidates parsed | 24 | 24 |
| Unique expressions | 24 | 24 |
| Field family count | 2 | 2 |
| Operator count | 16 | 14 |
| Unsupported operator candidates | 0 | 6 |
| vec_avg on non-VECTOR fields | 16 | 0 |
| Existing scorecard best score | 34.76 | 34.84 |

## Interpretation

- MiniMax was much faster after `reasoning_effort=low`, and its expression style stayed simpler.
- MiniMax violated operator constraints by using unsupported `sign` and `neg` in 6 candidates, and returned JSON despite the line-label format instruction.
- Qwen followed the labeled output format better and avoided unsupported operator names, but made a serious unit/type mistake by applying `vec_avg()` to non-VECTOR fields in 14 candidates.
- Both models over-concentrated in only two field families, so neither solved the family-diversity problem from prompt alone.
- The conservative existing scorecard selected 0/24 for both; this is expected because these are detached offline generations without family docs or simulation metrics, but it still flags weak structural fit.

## Current Judgment

MiniMax-M2.7 is usable as an API generation backend, but not yet safe to plug straight into the live mining chain without a post-generation repair/validation pass. For alpha quality infrastructure, MiniMax is currently preferable to local Qwen for speed and coherence, while Qwen is preferable for exact label-format obedience. The decisive fix is not model choice alone: enforce static compile-safety and family-diversity after generation before spending any WorldQuant simulation budget.

## Files

- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/minimax_candidates.jsonl`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/minimax_scored.csv`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/qwen_candidates.jsonl`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/qwen_scored.csv`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/model_ab_comparison.json`

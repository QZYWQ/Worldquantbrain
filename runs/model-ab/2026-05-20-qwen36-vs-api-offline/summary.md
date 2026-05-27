# Offline Model A/B Status

## Account / Platform Safety
- WorldQuant API was not called.
- No `/alphas/{id}/check`, `/simulations`, browser automation, or mining loop was started.
- Platform-side Check Submission release was not probed because probing requires another check request.

## Qwen Local Leg
- Status: ok
- Endpoint: /api/chat
- Elapsed: 125.22 sec
- Candidates: 24
- Unique expressions: 24
- Hypotheses: 8
- Field family count: 2
- Operator count: 16

## Static Quality
- Unknown fields: 0
- Direct VECTOR into ts_*: 0
- Invalid group calls after nested-arg parse: 0
- Exact duplicates: 0
- Main weakness: field-family diversity is still low; output concentrated in `model16:model:model-valuation-models` and `fundamental2:fundamental:fundamental-footnotes`.

## Existing Scorecard
- Existing `candidate_scorecard.py` selected 0/24. Treat this as a conservative structural warning, not official alpha quality, because these candidates are not attached to an existing family doc.
- Best local score: 34.76 (drop)
- Best expression: `ts_mean(multiply(earnings_certainty_rank_derivative, vec_avg(fnd2_dfdtxastxdfdexprssaccrs)), 10)`

## API Leg
- Executed: no
- Reason: No recognized API model key is set in the current environment; API leg not executed.

## Files
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/prompt.txt`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/field_pool.json`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/operator_pool.json`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/qwen_chat_payload.json`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/qwen_chat_response.json`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/qwen_candidates.jsonl`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/qwen_scored.csv`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/qwen_scorecard_summary.md`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/offline_static_summary.json`
- `/Users/zpdedn/Documents/project/Worldquantbrain/runs/model-ab/2026-05-20-qwen36-vs-api-offline/api_status.json`

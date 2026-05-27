# 2026-05-24 Upgrade And Favorite Record

- Mode: simulation / official check / favorite only.
- Submit endpoint: not used.
- Generated UTC: `2026-05-24T04:27:50.650113+00:00`
- Upgrade candidates simulated: `1`
- Upgrade hard 8-pass: `0`
- Final favorite candidates: `16`
- Upgrade limitation: the first targeted upgrade simulation was rejected by the platform with `POST_FAIL_429` / `CONCURRENT_SIMULATION_LIMIT_EXCEEDED`; the remaining generated upgrade candidates are preserved in `results.json` but were not submitted to simulation in this run.

## Upgrade Results

| Alpha | Name | Sharpe | Fitness | Turnover | Check | SelfCorr | Logic |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- |
| `-` | d5-current-accrued-assets-s84-delta252-z120-industry-d3 | None | None | None | - | None | rising current accrued-liability pressure relative to assets |

Simulation status: `POST_FAIL_429`; body: `{"detail":"CONCURRENT_SIMULATION_LIMIT_EXCEEDED"}`.

## Final Ranked Favorite Candidates

| Rank | Alpha | Final | Econ | LowCorr | Metric | Sharpe | Fitness | Turnover | SubU | SelfCorr | Favorite | Origin |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `j21QzK9E` | 91.7 | 92.0 | 100.0 | 76.49 | 1.48 | 1.04 | 0.0367 | 1.15 | 0.3718 | True | independent operating-profitability S2 result |
| 2 | `GrkvkVqZ` | 88.75 | 88.0 | 92.0 | 80.75 | 1.55 | 1.06 | 0.0355 | 1.4 | 0.4722 | True | 2026-05-23 near-pass rescue |
| 3 | `np30b6rw` | 88.6 | 88.0 | 92.0 | 79.98 | 1.53 | 1.05 | 0.0347 | 1.4 | 0.4727 | True | 2026-05-23 long-run potential upgrade |
| 4 | `A1k6KQQd` | 88.48 | 88.0 | 92.0 | 79.39 | 1.56 | 1.08 | 0.0398 | 1.13 | 0.4882 | True | 2026-05-23 long-run potential upgrade |
| 5 | `kqQRRQ2k` | 88.16 | 88.0 | 92.0 | 77.82 | 1.53 | 1.04 | 0.0361 | 1.21 | 0.4675 | True | 2026-05-23 long-run potential upgrade |
| 6 | `9qJQadYd` | 88.01 | 88.0 | 92.0 | 77.06 | 1.51 | 1.05 | 0.0377 | 1.11 | 0.4961 | True | 2026-05-23 near-pass rescue |
| 7 | `mLZOOpK9` | 87.77 | 88.0 | 92.0 | 75.84 | 1.48 | 1.0 | 0.0331 | 1.28 | 0.476 | True | 2026-05-23 long-run potential upgrade |
| 8 | `P0vEXzgK` | 87.75 | 88.0 | 92.0 | 75.77 | 1.48 | 1.04 | 0.036 | 1.07 | 0.4918 | True | 2026-05-23 near-pass rescue |
| 9 | `0mzWQbPK` | 87.23 | 88.0 | 82.0 | 85.65 | 1.64 | 1.18 | 0.0394 | 1.18 | 0.5297 | True | 2026-05-23 near-pass rescue |
| 10 | `MPkAX0LM` | 87.14 | 88.0 | 82.0 | 85.18 | 1.65 | 1.18 | 0.0398 | 1.11 | 0.5359 | True | 2026-05-23 near-pass rescue |
| 11 | `88nqa60q` | 86.81 | 88.0 | 82.0 | 83.54 | 1.61 | 1.15 | 0.0391 | 1.15 | 0.5192 | True | 2026-05-23 near-pass rescue |
| 12 | `qMgbqzPV` | 86.58 | 88.0 | 82.0 | 82.38 | 1.6 | 1.12 | 0.0411 | 1.19 | 0.5137 | True | 2026-05-23 long-run potential upgrade |
| 13 | `E5kobRlG` | 86.0 | 95.0 | 68.0 | 81.26 | 1.58 | 1.13 | 0.0406 | 1.05 | 0.6147 | True | 2026-05-23 financing-pressure 24h |
| 14 | `pw8gne5q` | 86.0 | 88.0 | 82.0 | 79.52 | 1.59 | 1.11 | 0.041 | 0.94 | 0.5348 | True | 2026-05-23 near-pass rescue |
| 15 | `GrkvMPbO` | 85.24 | 88.0 | 82.0 | 75.7 | 1.47 | 1.03 | 0.0364 | 1.13 | 0.5033 | True | 2026-05-23 near-pass rescue |
| 16 | `e7LAJmdN` | 85.16 | 88.0 | 82.0 | 75.28 | 1.54 | 1.04 | 0.0435 | 0.91 | 0.5229 | True | 2026-05-23 long-run potential upgrade |

## Files

- Results JSON: `/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-24-financing-pressure-upgrade-favorite/results.json`
- Final JSON: `/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-24-financing-pressure-upgrade-favorite/final-ranked-favorite-candidates.json`
- Events JSONL: `/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-24-financing-pressure-upgrade-favorite/events.jsonl`

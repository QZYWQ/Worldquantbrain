# 2026-04-27 worldquant-miner Deep Analysis

## Scope And Method

- Read-only analysis of the local reference repo at `/Users/zpdedn/Documents/github/worldquant-miner`.
- No network access or platform API calls were used.
- Large text / binary files over 1 MB were skipped and noted below.
- The repo is a bundle of overlapping experiments, not a single coherent miner.

### Skipped Large Or Binary Files

| File | Reason | Size |
| --- | --- | --- |
| `generation_one/consultant-templates-ollama/dynamic_personas.json` | >1 MB text | 11,163,029 bytes |
| `generation_one/consultant-templates-ollama/alpha_tracking.json` | >1 MB text | 7,903,733 bytes |
| `generation_one/agent-dify-web/public/vs/language/typescript/tsWorker.js` | >1 MB text | 5,034,373 bytes |
| `generation_one/agent-dify-web/public/vs/editor/editor.main.js` | >1 MB text | 3,520,739 bytes |
| `generation_one/agent-dify-web/public/pdf.worker.min.mjs` | >1 MB text | 1,360,963 bytes |
| `generation_one/consultant-templates-ollama/field_usage_analysis.png` | binary image | 1,053,710 bytes |

### Repository Scale

- Total files: about 5,968.
- Top-level concentration:
  - `generation_one`: 5,631 files
  - `generation_two`: 106 files
  - `tradr-platform`: 84 files
  - `polymarket`: 57 files
  - `stone_age`: 36 files
  - `mini-quant`: 9 files
- Conclusion: `generation_one` is the dominant historical archive; `generation_two` is the cleanest modular core; `polymarket` is the cleanest pipeline pattern.

## 1. Architecture Snapshot

### Condensed Directory Tree

```text
worldquant-miner/
├── generation_two/
│   ├── core/
│   │   ├── config/
│   │   ├── mining/
│   │   ├── recorder/
│   │   └── utils/
│   ├── data_fetcher/
│   ├── evolution/
│   ├── gui/
│   ├── ollama/
│   ├── self_evolution/
│   └── storage/
├── generation_one/
│   ├── consultant-naive-ollama/
│   ├── consultant-multi-arm-bandit-ollama/
│   ├── consultant-templates-api/
│   ├── consultant-templates-ollama/
│   ├── consultant-templates-bruteforce-ollama/
│   ├── consultant-atom-up/
│   ├── alpha-icu/
│   ├── agent-next/workers/
│   ├── agent-dify-api/
│   ├── agent-n8n/
│   ├── naive-ollama/
│   └── stone_age/{python,rust}
├── mini-quant/
├── polymarket/
│   └── polymarket_core/{adapters,alpha,backtest,cycle,data,engine,execution,pipeline,portfolio,storage,web}
└── tradr-platform/
    ├── backend/src/{auth,game,matches,progression,ranking,trading,websocket,prisma}
    ├── frontend/{app,src}
    └── pdac/{src,examples}
```

### Primary Entry Points

| File | Role | Notes |
| --- | --- | --- |
| `README.md` | Top-level project overview | Recommends `naive-ollama` as the default path; also describes `generation_two` and `mini-quant` |
| `generation_two/gui/run_gui.py` | Generation Two launcher | Python GUI entrypoint |
| `generation_one/consultant-naive-ollama/start.sh` | Naive Ollama orchestrator | Starts Ollama, submitter, and continuous mining |
| `generation_one/consultant-multi-arm-bandit-ollama/start.sh` | Bandit orchestrator | Starts model-fleet-aware mining loop |
| `generation_one/consultant-templates-api/run_generator.py` | DeepSeek template generator | Simple region template generation |
| `generation_one/consultant-templates-ollama/run_enhanced_generator_v2.py` | Ollama multi-arm runner | Continuous explore/exploit loop |
| `generation_one/consultant-atom-up/run_enhanced_multi_threaded_atom_tester.py` | Atom tester | Multi-threaded operator-combination tester |
| `generation_one/alpha-icu/main.py` | Alpha ICU orchestrator | Fetch/analyze/correlation filter pipeline |
| `polymarket/scripts/run_full_cycle.py` | Polymarket cycle runner | Research -> backtest -> optional execution |
| `tradr-platform/pdac/src/cli.ts` | PDaC CLI | Compile / validate / docs commands |
| `stone_age/rust/src/main.rs` | Legacy Rust miner | Hopeful-alpha loop with parameter variations |

### Documentation Claims And Tech Stack

| Source | Main claim | Tech stack / signals |
| --- | --- | --- |
| `README.md` | `naive-ollama` is recommended; claims 3-5x faster generation, real-time dashboard, GPU acceleration, and 24/7 automation | Python + Ollama + Flask + Docker Compose |
| `IMPLEMENTATION_SUMMARY.md` | Generation Two expected discovery rate 2.3% -> 8-12%, avg Sharpe 1.28 -> 1.6-1.8, success rate 45% -> 65-75%, stability 85%+ | Aspirational numbers; not validated by run logs |
| `generation_two/README.md` / `DOCUMENTATION.md` | Modular alpha mining system with self-optimization, genetic evolution, AST validation, expression compiler, continuous mining | Python 3.8+, requests, tkinter |
| `polymarket/README.md` | Research -> backtest -> execution pipeline with artifact persistence and guarded live mode | Python 3.10+, Flask, py-clob-client |
| `tradr-platform/README.md` and `pdac/` | Spec-driven trading-game stack with PDaC DSL, React/NestJS generation, validation, and docs | Next.js 14, React 18, NestJS, Prisma, TypeScript |
| `mini-quant/README.md` | Complete research -> backtest -> pool -> execution lifecycle | Python, pandas, numpy, yfinance |

### Configuration Surfaces

| File | Key configuration | Meaning |
| --- | --- | --- |
| `generation_two/pyproject.toml` | Python 3.8+, `generation-two = generation_two.gui.run_gui:main`, package data for constants / GUI / core | Main packaged app surface |
| `generation_two/core/config/config_manager.py` | `retry`, `request`, `simulation`, `evolution`, `template_generation`, `advanced_bandits`, `recording` sections | Central runtime defaults |
| `polymarket/polymarket_core/config.py` | `lookback=20`, `min_liquidity=1000`, `max_position=0.10`, `signal_threshold=0.05`, `cycle_backtest_scenarios=80`, `cycle_min_avg_return=0.02`, `cycle_min_worst_return=-0.05` | Deterministic research gate settings |
| `tradr-platform/backend/package.json` | NestJS / Prisma / Socket.io scripts | Backend service orchestration |
| `tradr-platform/pdac/package.json` | `pdac` CLI build / compile / validate | DSL tooling surface |
| `generation_one/*/.env.example` and `docker-compose*.yml` | API keys, model names, GPU containers, credentials paths | Deployment-time parameters |

## 2. Core Module Breakdown

### A. Alpha Generation Modules

| File(s) | Strategy | Inputs / Outputs | Core Logic |
| --- | --- | --- | --- |
| `generation_two/core/template_generator.py` | LLM-first generation | Inputs: prompt, region, available operators/fields, duplicate context. Output: FASTEXPR template string. | Ollama first, DeepSeek fallback, then heuristic fallback. It also enriches prompts with region themes, fetches operator/field context, and rejects duplicates before returning. |
| `generation_two/core/algorithmic_template_generator.py` | Algorithmic placeholder generation | Inputs: operators, data fields. Output: placeholder expression like `OPERATOR1(DATA_FIELD1)`. | Generates `random_walk`, `brownian`, `tree`, and `linear` placeholder structures, then leaves actual semantic filling to the LLM layer. |
| `generation_one/consultant-templates-api/template_generator.py` | DeepSeek prompt generation | Inputs: region, sampled operators, sampled fields. Output: 10 region templates. | Builds a prompt from sampled operators/fields, sends it to DeepSeek, parses line-by-line expressions, and stores operator/field usage metadata. |
| `generation_one/consultant-templates-ollama/enhanced_template_generator_v2.py` and `...-lts/` | Bandit-driven prompt generation | Inputs: persona / region / feedback. Output: templates plus performance metadata. | Explore/exploit routing, persona scoring, retry loops, validation, and multi-simulate support. |
| `generation_one/consultant-multi-arm-bandit-ollama/alpha_generator_ollama.py` | Prompt-based bulk generation | Inputs: operator categories and data fields. Output: 100 cleaned expressions per call. | Builds a large prompt, samples operators by category, cleans model output, and can multi-simulate batches. |
| `generation_one/consultant-naive-ollama/alpha_generator_ollama.py` | Prompt-based bulk generation with retries | Same as above, plus hopeful alpha logging. | Adds retry queue, model downgrades, cleanup, multi-simulate batching, and hopeful-alpha tracking. |
| `generation_one/consultant-templates-bruteforce-ollama/bruteforce_template_generator.py` | Brute-force atom testing | Inputs: one atom template, all fields, all regions. Output: stored per-field results. | One lightweight template at a time; tests across every field/region pair and uses simple success thresholds. |
| `generation_one/consultant-atom-up/enhanced_multi_threaded_atom_tester.py` | Operator-combination generation | Inputs: data field + operator stack depth. Output: tested atom combinations. | Uses Ollama to propose operator stacks of depth 0-3, then batches them with threaded simulation. |
| `mini-quant/quant_research_module.py` | Hypothesis-to-alpha ideation | Inputs: market condition + research focus. Output: simple alpha expressions. | Placeholder hypothesis generator with fallback expressions like `ts_rank(close, 20)` and `delta(volume, 1)`. |
| `polymarket/polymarket_core/alpha/factors.py` | Market-factor scoring | Inputs: market records. Output: scored opportunities. | Scores by edge, momentum, volume, and liquidity penalty; not a WorldQuant alpha generator, but a clean scoring engine. |
| `tradr-platform/pdac/src/generator.ts` | Spec-to-code generation | Inputs: PDaC AST. Output: React / NestJS / TS files. | Converts declarative spec nodes into code files; useful as an architectural pattern, not as a WQ alpha engine. |

### B. Simulation And Backtest Modules

| File(s) | Mechanism | Inputs / Outputs | Core Logic |
| --- | --- | --- | --- |
| `generation_two/core/simulator_tester.py` | Simulation submit + monitor | Inputs: template, region, simulation settings. Output: `SimulationResult`. | POSTs to `/simulations`, retries auth on 401, handles `PENDING/CREATED/SUBMITTED/QUEUED/RUNNING/COMPLETE/FAILED/ERROR`, then fetches alpha details and extracts Sharpe, Fitness, Turnover, returns, drawdown, margin, long/short counts, PnL, volatility, max drawdown, win rate, avg return, correlations, checks, and raw JSON. |
| `generation_two/core/simulation_counter.py` | Daily limit enforcement | Inputs: current date. Output: count, warning, limit status. | Tracks EST day counts in SQLite; hard cap 5000/day, warning at 4000/day. |
| `generation_two/core/slot_manager.py` | Concurrent slot allocator | Inputs: template + region. Output: slot IDs and status. | Manages 8 simulation slots; GLB uses 2 slots, others use 1. Keeps recent logs and progress per slot. |
| `generation_two/storage/backtest_storage.py` | Result ledger | Inputs: simulation/backtest results. Output: SQLite records, stats, templates, AST patterns. | Persists all metrics, raw data, and compiler knowledge. Similarity gate uses `TemplateSimilarityChecker` with threshold 0.7 and only recent templates for performance. |
| `generation_one/consultant-naive-ollama/improved_alpha_submitter.py` | Submission gate | Inputs: `hopeful_alphas.json` or `/users/self/alphas`. Output: submissions + log file. | Requires `is.sharpe > 1.25`, `is.fitness > 1`, filters FAIL checks, waits 30s between submissions and 120s between batches, and runs on a 24h interval. |
| `generation_one/consultant-multi-arm-bandit-ollama/alpha_generator_ollama.py` | Batch sim / monitor | Inputs: alpha list. Output: simulation results and hopeful-alpha log. | Can multi-simulate in pools, reauth on 401, retry `SIMULATION_LIMIT_EXCEEDED`, and logs hopeful alphas when fitness is above a threshold. |
| `generation_one/alpha-icu/alpha_analyzer.py` | Metrics filter | Inputs: alpha JSON. Output: `AlphaMetrics` and success decision. | Success requires Sharpe > 1.2, margin > 8 bps, no FAIL checks, and max production correlation <= 0.7. |
| `generation_one/alpha-icu/correlation_checker.py` | Correlation risk gate | Inputs: correlation API data. Output: risk level and recommendations. | Buckets correlations into >0.5, 0.2-0.5, -0.2-0.2, and < -0.2, with HIGH/MEDIUM/LOW risk levels. |
| `mini-quant/alpha_backtesting_system.py` | Multi-region toy backtest | Inputs: alpha expression, date range. Output: per-region Sharpe, returns, drawdown, win rate. | Uses placeholder random signals rather than a real expression evaluator, so it is structurally useful but not production-grade. |
| `polymarket/polymarket_core/backtest/scenario_backtester.py` | Scenario robustness gate | Inputs: positions, shock count, shock size. Output: avg/min/max expected returns. | Perturbs expected edges across scenarios and produces a deterministic backtest summary. |
| `polymarket/polymarket_core/engine/simulator.py` | Paper simulator | Inputs: position intents. Output: expected return, exposure, position count. | Expected-value simulator for research loops. |

### C. Screening And Submission Modules

| File(s) | Gate | Thresholds / Behavior | Notes |
| --- | --- | --- | --- |
| `generation_two/core/template_validator.py` | Syntax + repair gate | AST off by default; basic parenthesis and event-input compatibility checks. With AST on, it parses and compiles. | Refeed loop retries indefinitely for event-input, input-count, and unexpected-character errors. Learns from simulation errors and stores compiler knowledge + AST patterns in SQLite. |
| `generation_two/core/template_similarity.py` | Duplicate / similarity gate | Similarity = 40% string + 30% operator overlap + 20% field overlap + 10% structural similarity. | Default similarity threshold is 0.7. |
| `generation_two/core/mining/duplicate_detector.py` | Exact / hash / similarity dedupe | Checks template exact match, template hash, then similarity to recent successful templates. | Region-aware and cache-friendly. |
| `generation_one/alpha-icu/main.py` + `alpha_analyzer.py` | Success filter | `min_sharpe=1.2`, `min_margin=0.0005`, `max_prod_correlation=0.7`. | Warnings are tolerated; FAIL checks reject. |
| `generation_one/consultant-naive-ollama/successful_alpha_submitter.py` | Submission filter | `is.sharpe > 1.25`, `is.fitness > 1`, FAIL checks rejected, 50 hopeful-alpha minimum. | Has long retry, 24h loop, and cleanup logic for `hopeful_alphas.json`. |
| `mini-quant/alpha_pool_storage.py` | Pool qualification | `min_sharpe=1.5`, `min_positive_regions=3`, `max_drawdown=-15%`, `min_win_rate=55%`, `min_trades=50`. | Composite score weights: sharpe 0.4, consistency 0.3, robustness 0.2, recency 0.1. |
| `generation_two/evolution/alpha_quality_monitor.py` | Degradation detector | Recent 10 Sharpe average < older average * 0.8. | 30-day history window; health score blends stability and trend. |
| `polymarket/polymarket_core/portfolio/risk.py` | Position gate | `signal_threshold=0.05`, `max_position=0.10`, min liquidity from config. | Keeps a simple, deterministic risk posture. |
| `polymarket/polymarket_core/cycle/full_cycle_runner.py` | Cycle gate | Backtest approves only if `avg_expected_return >= 0.02` and `min_expected_return >= -0.05`. | Live execution still requires confirmation and credentials. |

### D. Genetic / Evolution / Bandit Modules

| File(s) | Method | Parameters | Assessment |
| --- | --- | --- | --- |
| `generation_two/evolution/alpha_evolution_engine.py` | Tournament selection + crossover + mutation | Population 50, mutation 0.1, crossover 0.7, top 10% elitism. | The cleanest alpha-evolution code in the repo. Fitness = 0.5 Sharpe + 0.3 Fitness + 0.2 inverse turnover. |
| `generation_two/evolution/self_optimizer.py` | Adaptive parameter tuning | Optimize every 100 samples. | Success rate <0.3 increases exploration; >0.6 increases exploitation. Low/high Sharpe nudges exploration as well. |
| `generation_two/evolution/on_the_fly_tester.py` | Immediate testing | Uses 1-year test period for speed. | Simple but useful for feedback loops. |
| `generation_two/evolution/alpha_quality_monitor.py` | Health monitoring | 30-day rolling window. | Detects 20% Sharpe degradation. |
| `generation_one/consultant-templates-ollama/enhanced_template_generator_v2.py` | Persona bandit | Explore/exploit and persona scoring. | Interesting routing logic, but large and domain-specific. |
| `generation_one/consultant-multi-arm-bandit-ollama/alpha_orchestrator.py` | Model fleet manager | Model downgrade after repeated VRAM errors; state persisted in JSON. | Good operational resilience pattern, but still tightly coupled to local Ollama deployment. |
| `generation_two/self_evolution/{code_generator,code_evaluator,evolution_executor}.py` | Self-modifying code loop | Generates modules, compiles them, executes them in an isolated namespace, and tries to integrate winners. | High-risk; see reject section below. |

### E. Automation And Scheduling

| File(s) | Scheduler / Orchestrator | Behavior | Notes |
| --- | --- | --- | --- |
| `generation_two/core/mining/mining_coordinator.py` | Continuous mining coordinator | Enforces 5000/day limit, generates templates when queue is low, selects low-correlation candidates first. | Background thread, queue-based workflow. |
| `generation_two/core/mining/search_strategy.py` | BFS / DFS / Hybrid strategy | Rotates across regions and retains successful templates for deep exploration. | Good as a simple strategy switch. |
| `generation_two/core/mining/correlation_tracker.py` | Low-correlation selection | Uses absolute correlations against successful alphas. | Good for diversity control. |
| `generation_one/consultant-naive-ollama/start.sh` | Shell orchestration | Starts Ollama, then submitter, then continuous mining. | Batches 10, max concurrent 5. |
| `generation_one/consultant-multi-arm-bandit-ollama/start.sh` | Shell orchestration | Starts Ollama, submits hopeful alphas if >=50, then runs continuous mining. | Batches 3, max concurrent 3. |
| `generation_one/consultant-naive-ollama/improved_alpha_submitter.py` | Submission loop | 24h loop with exponential backoff and batch pacing. | More robust than earlier submitters. |
| `generation_one/consultant-multi-arm-bandit-ollama/integrated_alpha_miner.py` | Dual-session miner | Adaptive mining + generator sessions every 6h. | Good example of cycle separation. |
| `polymarket/polymarket_core/cycle/full_cycle_runner.py` | Deterministic cycle runner | Research -> backtest -> optional execution -> persisted cycle artifact. | Best artifact/cycle boundary in the repo. |
| `tradr-platform/pdac/src/cli.ts` | Spec tooling | `compile`, `validate`, `docs` commands. | Spec-driven development pattern only. |

## 3. Success Rate And Bottlenecks

### Observed Run Artifacts

| Artifact | What it shows | Interpretation |
| --- | --- | --- |
| `generation_one/consultant-atom-up/enhanced_atom_results.json` | 20 entries, all `status = failed`, all with `Submission failed: 405`, no valid Sharpe / Fitness values | Strong evidence of a broken submit path or endpoint mismatch; no real success signal found |
| `generation_one/consultant-templates-bruteforce-ollama/bruteforce_progress.json` | 8 simulations, `successful_simulations = 8`, but all Sharpe / Fitness / turnover / returns are `0.0`, and `success_criteria_met = 0` | Looks like placeholder or non-productive simulation output, not a real profitable run |
| `generation_one/consultant-atom-up/atom_test_progress.json` | 50 completed tests out of 7,100 planned | Progress only; not enough to infer performance |

### Real Bottlenecks

1. **Submission fragility**: many loops are built around 401 / 405 / 429 handling, which suggests the repo has spent a lot of effort fighting auth and endpoint drift.
2. **Operational coupling**: the generation-one stacks are tightly coupled to local Ollama, GPU availability, and file-based submission state.
3. **Low-quality fallback risk**: `generation_two/core/template_generator.py` falls back from Ollama to DeepSeek to a heuristic template, which is good for throughput but can hide quality regression.
4. **Validation is optional in the strongest sense**: `generation_two` initializes `TemplateValidator(..., use_ast=False)` by default, so the most rigorous checks are off unless explicitly enabled.
5. **Self-evolution safety risk**: `generation_two/self_evolution` uses generated code plus `exec`-style evaluation with only shallow dangerous-pattern checks. That is not a safe integration target.
6. **Known code defect**: `generation_two/core/enhanced_template_generator_v3.py` defines `run_self_evolution()` but never initializes `self.evolution_executor`, so that path is broken.
7. **Dead or unreachable code**: `generation_two/core/template_generator.py` returns before a duplicate DeepSeek branch, leaving unreachable legacy code in place.
8. **Domain drift**: much of `generation_one` is a historical pile of overlapping heuristics, prompt experiments, and UI shells, not a single stable architecture.

### Bottom Line On Success Rate

- The repo contains many heuristics for rate limiting, retries, and hopeful-alpha logging, but very little trustworthy evidence of a sustained profitable acceptance rate.
- The available artifacts are mostly either progress snapshots or failed submissions, so the safest reading is: **the system is operationally active, but the evidence of durable alpha quality is weak**.

## 4. Integration Decision

### Directly Integrable

| Mechanism | Why it is worth integrating | Safe form |
| --- | --- | --- |
| `generation_two/core/template_similarity.py` + `generation_two/storage/backtest_storage.py` | Deterministic, low-risk, immediately useful for dedupe and result history | Wrap as a pre-simulation hygiene layer with a local SQLite / JSON ledger |
| `generation_two/core/template_generator.py` / `data_fetcher/` / `config_manager.py` | Clear separation of generation, data lookup, and configuration | Reuse the boundary pattern, not the whole runtime |
| `polymarket/polymarket_core/storage/{cycle_store,run_store}.py` | Excellent artifact persistence pattern | Copy the artifact writer pattern for cycle / run outputs |
| `polymarket/polymarket_core/cycle/full_cycle_runner.py` | Clean research -> backtest gate -> execution separation | Adapt the gating pattern to our own candidate lifecycle |

### Integrate Only After Refactor

| Mechanism | What must change first | Why |
| --- | --- | --- |
| `generation_one/consultant-naive-ollama/improved_alpha_submitter.py` | Remove hard-coded live submission assumptions and turn the retries into a pluggable service | Good retry/backoff logic, but too coupled to direct API submission |
| `generation_one/consultant-multi-arm-bandit-ollama/alpha_orchestrator.py` | Strip the model-fleet / VRAM / local-Ollama assumptions from core logic | Useful operational resilience pattern, but not portable as-is |
| `mini-quant/*` | Replace toy backtests, placeholder signals, and toy broker execution with real evaluators | Good lifecycle design, but implementation quality is demonstrative rather than production-grade |
| `tradr-platform/pdac/*` | Repurpose the DSL idea for WQ workflow specs; do not adopt the game runtime | Strong spec-driven pattern, wrong domain and stack |
| `generation_two/self_evolution/*` | Require real sandboxing, policy gates, and non-arbitrary code boundaries | High risk as currently implemented |

### Reject

| Mechanism | Reject reason |
| --- | --- |
| `generation_two/self_evolution` direct code generation / execution loop | Unsafe, weak sandbox, and not aligned with a disciplined WQ research harness |
| `stone_age` as a primary integration source | Legacy / prototype-heavy, with duplicated ideas and less coherent design |
| `tradr-platform` game runtime | Orthogonal product domain; only the spec-driven tooling is reusable |

### One Concrete Pilot Recommendation

If we only trial one mechanism next, I would pilot **the duplicate gate plus result ledger pattern** from `generation_two/core/template_similarity.py` and `generation_two/storage/backtest_storage.py`.

Why this first:
- low risk
- no platform API changes
- directly reduces candidate churn and duplicate simulations
- easy to run locally against existing batches
- gives us a durable history layer before any more expensive simulation work

## Conclusion

- The strongest integration seed is `generation_two`: it is the most modular, the most internally consistent, and the easiest to adapt into a safe harness.
- The strongest pipeline pattern is `polymarket`: artifact-first, deterministic, and guarded execution.
- `generation_one` is best treated as a tactics library: useful for retry/backoff, submit pacing, model-fleet resilience, and batch orchestration, but not as a whole-archive transplant.
- `tradr-platform` and `stone_age` are mostly adjacent or legacy; borrow ideas, not runtimes.

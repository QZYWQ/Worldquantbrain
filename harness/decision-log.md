# Harness Decision Log

## 2026-04-18 | HARNESS-DECISION-001 | Keep harness v1 local-only

**Context**: The project needs a reliable long-running agent harness, but the current root project is still in early execution setup.

**Decision**: Version 1 of the harness will orchestrate only local project work, state, evidence, and local scripts. It will not automate WorldQuant browser actions or submission steps.

**Rationale**: This keeps the first version stable and lets the project solve the hardest immediate problems first: session continuity, truth sources, evidence, and resumable work.

**Alternatives Considered**:
- Immediate browser automation for WorldQuant platform flows: rejected because it would add too much moving complexity too early.

**Consequences**:
- Agents must still use official pages manually or interactively for platform facts and real simulation outputs.
- The harness remains extensible for future platform-aware verification modes.

## 2026-04-18 | HARNESS-DECISION-002 | Use JSON for task truth and Markdown for session truth

**Context**: Long-running agents need stable task mutation and readable session summaries.

**Decision**: Use JSON for `feature_list.json` and Markdown with frontmatter for `progress.md`.

**Rationale**: JSON is safer for structured status mutation. Markdown keeps session context readable for both humans and agents.

**Alternatives Considered**:
- Single Markdown file for everything: rejected because mutable task state and freeform notes get mixed.
- Single JSON file for everything: rejected because session readability becomes worse.

**Consequences**:
- Shell helpers must support both JSON parsing and frontmatter rewriting.

## 2026-04-18 | HARNESS-DECISION-003 | Move from singleton task file to active-cycle pointer

**Context**: The harness needs to support repeated official alpha cycles without rewriting the same `feature_list.json` by hand each time.

**Decision**: Keep `./harness/feature_list.json` as the legacy default first cycle, but resolve task truth through `./harness/active-cycle.txt`. New cycles are created under `./harness/cycles/`.

**Rationale**: This preserves backward compatibility while removing the hardest singleton bottleneck in the current v1 design.

**Alternatives Considered**:
- Immediate full migration away from `feature_list.json`: rejected because it adds unnecessary migration churn for v1.2.

**Consequences**:
- Runtime helpers must resolve the active cycle instead of assuming one hardcoded task file.
- Future sessions can create or switch cycles without replacing the original first-cycle file.

## 2026-04-18 | HARNESS-DECISION-004 | Externalize local machine paths through config.env

**Context**: The harness currently assumes one exact external knowledge-base path and one exact local script root.

**Decision**: Load `EXTERNAL_KB_ROOT` and `WQB_SCRIPT_ROOT` from `./harness/config.env`, with defaults documented in `./harness/config.env.example`.

**Rationale**: This improves portability across machines, worktrees, and directory changes while keeping the runtime simple.

**Alternatives Considered**:
- Keep paths hardcoded in shell: rejected because it keeps local portability too fragile.

**Consequences**:
- Preflight now validates config-driven paths.
- Users and future agents have one clear place to adjust environment-specific settings.

## 2026-04-18 | HARNESS-DECISION-005 | Separate bootstrap cycle from formal creation template

**Context**: The harness now supports active cycle switching, but new cycle creation should not depend on whichever active cycle happens to be selected.

**Decision**: Keep `./harness/feature_list.json` as the bootstrap fallback cycle, but create new cycles from `./harness/templates/cycle-template.json`.

**Rationale**: This preserves compatibility while preventing mutated active cycles from becoming accidental templates.

**Alternatives Considered**:
- Continue cloning the active cycle: rejected because it leaks operator mutations into future cycles.

**Consequences**:
- `cycle-create` is now deterministic.
- The bootstrap file remains available as a safe fallback, not the canonical creation source.

## 2026-04-18 | HARNESS-DECISION-006 | Add explicit cycle summary and archive lifecycle

**Context**: Repeated cycles need a compact handoff view and a formal way to leave the active working surface once finished.

**Decision**: Add `cycle-summary` for compact status output and `cycle-archive` for moving completed cycles into `./harness/archive/`.

**Rationale**: This reduces operator ambiguity and keeps the active cycle area cleaner as cycle count grows.

**Alternatives Considered**:
- Rely only on raw JSON inspection and manual file moves: rejected because it scales poorly and is too easy to misuse.

**Consequences**:
- Future agents can read one compact summary before deciding the next action.
- Completed cycles can be archived without deleting the bootstrap fallback cycle.

## 2026-04-18 | HARNESS-DECISION-007 | Separate cycle close/report from archive

**Context**: A cycle can be moved to the archive directory even when operators still need a durable closure artifact and an explicit readiness check.

**Decision**: Add `cycle-report` for deterministic markdown reports under `./harness/reports/` and `cycle-close` for terminal-state validation. Keep `cycle-archive` as a separate later step.

**Rationale**: Closure and file movement solve different problems. The harness should first prove that a cycle is terminal, then optionally move the raw JSON out of the active area.

**Alternatives Considered**:
- Auto-archive during `cycle-close`: rejected because it couples validation, reporting, and file movement too early.

**Consequences**:
- Closed cycles now leave a durable markdown handoff artifact.
- Operators can inspect the final report before choosing whether to archive the JSON.

## 2026-04-18 | HARNESS-DECISION-008 | Add read-only resume brief artifacts for next-session handoff

**Context**: The harness now has cycle summaries and cycle reports, but the next AI session still has to manually merge current task state, progress, decisions, and the latest report.

**Decision**: Add `resume-brief` as a read-only command that writes a deterministic markdown handoff artifact under `./harness/reports/` without mutating cycle or progress state.

**Rationale**: Cross-session continuity improves when the next operator can open one file and immediately see doctor state, current recommendation, focus feature details, and recent decisions.

**Alternatives Considered**:
- Keep relying on `status` only: rejected because it is too broad and not durable enough for handoff.
- Auto-start the next feature while generating the brief: rejected because v1.5 should stay read-only.

**Consequences**:
- The harness now distinguishes operational dashboard output from handoff artifacts.
- Future versions can build on `resume-brief` for note scaffolding or semi-automatic orchestration without changing the current state model.

## 2026-04-18 | HARNESS-DECISION-009 | Add session-open as the bridge from handoff to execution

**Context**: `resume-brief` now gives the next session a strong handoff artifact, but operators still need one more manual step to translate that handoff into a concrete execution package.

**Decision**: Add `session-open` as a read-only command that writes a deterministic session brief under `./runs/session-briefs/` for the selected feature or current actionable target.

**Rationale**: Session-start artifacts belong in the real project output tree, not only inside harness state folders. This also keeps `daily-note` reserved for post-work records instead of premature placeholders.

**Alternatives Considered**:
- Generate `daily-note` at session start: rejected because it pushes placeholder content into a file that should reflect real completed work.
- Extend `resume-brief` to carry all execution details: rejected because handoff understanding and execution startup are different jobs.

**Consequences**:
- The harness now has a clear bridge from state awareness to concrete execution setup.
- Future versions can derive richer post-work records from session briefs without changing the evidence-first start model.

## 2026-04-18 | HARNESS-DECISION-010 | Separate static cycle definitions from mutable runtime state

**Context**: The harness currently mutates the same cycle JSON for both reusable planning data and per-session runtime state, which increases coupling and makes template reuse harder.

**Decision**: Keep `./harness/feature_list.json` and `./harness/cycles/*.json` as static cycle definitions. Store mutable `status`, `passes`, `evidence`, and `last_verified_at` in synced runtime copies under `./harness/state/`.

**Rationale**: This keeps definitions reusable and reviewable while preserving the current command interface and report behavior through generated runtime state files.

**Alternatives Considered**:
- Keep mutating the definition files directly: rejected because it couples planning data to runtime execution too tightly.
- Store only per-feature runtime deltas: rejected for v1.6 because it would require a larger read-path refactor all at once.

**Consequences**:
- Harness commands now sync runtime state from the selected cycle definition before reading or mutating feature state.
- Tests and reports now treat `./harness/state/` as the mutable task source, while `active-cycle.txt` still points at static definitions.

## 2026-04-18 | HARNESS-DECISION-011 | Split diagnostics and report generation out of state helpers

**Context**: `state-helpers.sh` had grown into a mixed module that handled cycle mutation, progress mutation, doctor checks, and multiple read-only report and brief generators.

**Decision**: Move doctor diagnostics into `./harness/lib/state-doctor.sh` and move report and brief generation into `./harness/lib/reporting.sh`. Keep `./harness/lib/state-helpers.sh` focused on cycle state operations, progress mutation, and feature-level state helpers.

**Rationale**: This lowers change amplification for future harness work. Read-only reporting and diagnostics can now evolve without increasing the mutation module's responsibility surface.

**Alternatives Considered**:
- Keep all helpers inside one large file: rejected because the file had already become too broad for low-risk iteration.
- Do a larger full module taxonomy rewrite in one step: rejected because it would add unnecessary migration risk for v1.6.

**Consequences**:
- `init.sh` and `coding-session.sh` now source `state-doctor.sh` and `reporting.sh` explicitly.
- Future work can refactor verification-mode registration separately without reopening the state-mutation module boundary.

## 2026-04-18 | HARNESS-DECISION-012 | Use a declarative verification mode registry

**Context**: Verification mode support had started to drift across `verify-dispatcher.sh`, `content-validator.py`, and `reporting.sh`, which increased the number of places that needed edits for every new mode.

**Decision**: Add `./harness/verification-modes.json` as the single declarative registry for verification mode metadata. Keep execution, content validation, and reporting in separate modules, but make them all read mode metadata from the registry.

**Rationale**: This reduces change amplification without collapsing all behavior into one oversized implementation module. The registry becomes the truth source for supported modes, while the surrounding modules keep their separate responsibilities.

**Alternatives Considered**:
- Keep hardcoded mode lists in each module: rejected because it keeps mode additions unnecessarily error-prone.
- Collapse all verification behavior into one monolithic module: rejected because it would over-concentrate responsibilities and make the harness less maintainable.

**Consequences**:
- Adding a new verification mode now starts with one registry entry instead of multiple scattered metadata edits.
- The harness still keeps execution checks, content-quality checks, and reporting hints in separate layers for robustness.

## 2026-04-18 | HARNESS-DECISION-013 | Write runtime state files atomically

**Context**: Multiple read-only harness commands can run close together and each one currently refreshes runtime state from static definitions. Direct overwrite writes risk exposing partially written JSON to concurrent readers.

**Decision**: Change runtime state sync to write through a temporary file and atomically replace the target state file.

**Rationale**: This preserves the current sync-on-read model while removing torn-write risk for concurrent report, brief, and summary commands.

**Alternatives Considered**:
- Add a global lock to every read-only harness command: rejected because it would add unnecessary coordination overhead for simple reporting workflows.
- Leave direct file overwrite in place: rejected because it creates an avoidable consistency hazard under concurrent command use.

**Consequences**:
- Concurrent read-only commands are less likely to observe invalid runtime JSON.
- The harness keeps its simple file-based state model without introducing a heavier coordination layer.

## 2026-04-18 | HARNESS-DECISION-014 | Centralize cycle analysis logic in a shared Python module

**Context**: Actionable-pending selection, dependency readiness, and focus-feature selection logic were duplicated across `state-helpers.sh` and `reporting.sh`.

**Decision**: Add `./harness/lib/cycle_analysis.py` as the shared read-only analysis module for cycle overview, dependency readiness, next actionable feature selection, and focus-feature selection.

**Rationale**: This removes repeated analytical logic without merging mutation code, reporting code, and shell orchestration into one place. The harness keeps balanced boundaries while reducing drift risk.

**Alternatives Considered**:
- Keep duplicated analysis snippets in multiple heredocs: rejected because behavior drift had already become likely.
- Move all reporting and shell query behavior into one Python application: rejected because it would over-concentrate responsibilities for the current harness version.

**Consequences**:
- `cycle-summary`, `next`, dependency checks, `cycle-report`, `resume-brief`, and `session-open` now rely on one shared analysis implementation.
- Future changes to actionable-feature logic now have one primary implementation point instead of several parallel copies.

## 2026-04-18 | HARNESS-DECISION-015 | Extract report document rendering into a dedicated Python module

**Context**: `reporting.sh` had become a large mixed module that handled shell orchestration, cycle read preparation, doctor-state branching, and several hundred lines of embedded Python document rendering.

**Decision**: Keep `reporting.sh` as the shell orchestration boundary, but move cycle report, resume brief, and session brief rendering into `./harness/lib/report_documents.py`.

**Rationale**: This keeps the reporting layer cohesive without over-centralizing unrelated harness behavior. Shell remains responsible for command orchestration and project-path resolution, while Python handles structured document rendering and markdown assembly.

**Alternatives Considered**:
- Leave the embedded heredocs inside `reporting.sh`: rejected because the file had become too large and change-prone.
- Collapse reporting, cycle analysis, and state mutation into one larger Python application: rejected because it would over-concentrate responsibilities and weaken the current layered design.

**Consequences**:
- `reporting.sh` is now smaller and easier to review for orchestration behavior.
- Report and brief rendering can grow independently without re-inflating the shell boundary.

## 2026-04-18 | HARNESS-DECISION-016 | Separate read-only state queries from state mutation helpers

**Context**: After the reporting-layer extraction, `state-helpers.sh` was still mixing active-cycle mutations, archive operations, progress mutations, feature state mutation, and a large set of read-only feature and cycle query helpers.

**Decision**: Add `./harness/lib/state-queries.sh` for read-only cycle and feature queries, close-readiness checks, and operator-facing state summaries. Keep `./harness/lib/state-helpers.sh` focused on cycle mutation, archive movement, feature state mutation, and progress mutation.

**Rationale**: This reduces change amplification in the state layer without over-splitting the harness into too many tiny modules. Read-only query logic and write paths now have clearer boundaries, which improves maintainability and lowers accidental coupling.

**Alternatives Considered**:
- Keep all query and mutation helpers in one file: rejected because the mixed responsibility surface had grown too broad.
- Split into several more granular files immediately: rejected because it would add unnecessary module sprawl for the current harness version.

**Consequences**:
- `coding-session.sh` and `init.sh` now source `state-queries.sh` alongside `state-helpers.sh`.
- Future refactors can target read-only query behavior and mutation behavior independently without reopening the same mixed file.

## 2026-04-18 | HARNESS-DECISION-017 | Move read-only state query execution into a dedicated Python runner

**Context**: Even after separating `state-queries.sh`, that file still contained a large amount of embedded Python logic for cycle inspection, feature lookup, dependency checks, and operator-facing summaries.

**Decision**: Keep `state-queries.sh` as the shell wrapper boundary, but move the read-only query execution into `./harness/lib/state_query_runner.py`.

**Rationale**: This keeps the shell query layer thin and deterministic while preserving the overall layered design: shell for orchestration, Python for structured query execution, and separate mutation modules for write paths.

**Alternatives Considered**:

## 2026-04-19 | ALPHA-DECISION-018 | Pivot the post-submit cycle to analyst disagreement first

**Context**: `E5repQ81` is already submitted and locked. A fresh official re-check on `2026-04-19 12:14 CST` still shows `ACTV` with `OS Testing Status = 4 PENDING`, so there is no resolved OS outcome yet. The next research hour should therefore go to a lower-correlation follow-up branch instead of re-opening submission review or spending more time on EPS-level clones.

**Decision**: Create `official-alpha-cycle-03` around two immediate jobs: keep monitoring the submitted line's OS status, and open the next primary branch on analyst disagreement with `anl4_afv4_dts_spe`. Use a simple inverse-disagreement baseline first. Keep a non-analyst lane ready as fallback, but do not let it displace the disagreement branch before field quality is checked.

**Rationale**: This keeps the current submitted alpha untouched while using the next cycle to create a more distinct family. The disagreement field changes the information source meaningfully, which is a stronger correlation-reduction move than continuing EPS-level sibling polishing.

**Alternatives Considered**:
- Return immediately to `qMm6xPVv` or `QP59baMg`: rejected because they are same-family backups, not the highest expected-value next branch.
- Open a non-analyst lane first: rejected for now because the continuation plan explicitly prefers the disagreement branch unless coverage or robustness fails quickly.

**Consequences**:
- The new cycle tracks an OS-status memo plus the disagreement branch planning artifacts before any new simulation capture.
- The first disagreement experiments should stay simple: inverse sign, one field change at a time, and no unnecessary gating before the first bottleneck is known.
- Leave large Python heredocs inside `state-queries.sh`: rejected because it kept the query boundary bulky and harder to review.
- Merge query execution into the reporting renderer or mutation helper modules: rejected because it would reintroduce cross-layer coupling.

**Consequences**:
- `state-queries.sh` now serves mainly as a stable command adapter.
- Read-only query behavior can evolve without expanding the shell boundary again.

## 2026-04-18 | HARNESS-DECISION-018 | Standardize Codex App and git integration boundaries

**Context**: The project harness is designed for long-running agent work, but Codex App expects a normal git-backed project with a standard root `AGENTS.md` file and a clean commit surface.

**Decision**: Standardize the project root on `./AGENTS.md`, initialize the project as a git repository, and keep runtime harness state and session-start artifacts out of the default version-controlled surface through `.gitignore`.

**Rationale**: This allows Codex App's built-in git workflow to coexist with the harness without mixing transient operational state into ordinary code or research commits.

**Alternatives Considered**:
- Keep the lowercase root `agents.md` and no repository git hygiene layer: rejected because Codex App compatibility would remain partial and commit surfaces would stay noisy.
- Track all harness runtime files in git by default: rejected because it would create unnecessary branch noise and state conflicts.

**Consequences**:
- The project now has a standard root `AGENTS.md` entrypoint for agent discovery.
- Git commits can focus on intentional code, rules, and research outputs instead of transient harness state.

## 2026-04-18 | HARNESS-DECISION-019 | Add a machine-readable workspace surface contract

**Context**: Codex App readiness, `.gitignore`, tracked README skeletons, and harness git hygiene rules all described the same workspace boundaries in separate places, which increased drift risk whenever a new runtime or output path was introduced.

**Decision**: Add `./harness/project-surfaces.json` as the machine-readable contract for runtime-local, ephemeral, and durable tracked workspace surfaces. Keep `.gitignore`, docs, and readiness tests, but validate them against this shared contract.

**Rationale**: This lowers change amplification without collapsing project rules, git policy, and shell behavior into one oversized implementation module. The contract becomes the canonical boundary map, while docs remain human-readable and tests enforce alignment.

**Alternatives Considered**:
- Keep duplicating the same surface list in docs, tests, and ignore rules: rejected because it makes future evolution too easy to drift.
- Move all workspace policy into shell code only: rejected because git and documentation still need a stable non-executable truth source.

**Consequences**:
- The project now has one durable source of truth for git-facing workspace boundaries.
- Future surface changes must update the contract and will be caught quickly if `.gitignore` or tracked directory skeletons drift.

## 2026-04-24 | ALPHA-DECISION-020 | Freeze the capex estimate close-normalized branch after batch 01

**Context**: The logged-in official WorldQuant BRAIN API resolved the new capex baseline `group_rank(ts_rank(capital_expenditure_amount / close, 84), industry)` as alpha `om9kLgo6` from simulation `348RZu4P94Kx95O12rbWB4kg`. The alpha stayed `UNSUBMITTED`, with IS Sharpe `0.75`, Fitness `0.53`, and `SELF_CORRELATION` still `PENDING`, while TEST was stronger but not enough to rescue the branch.

**Decision**: Freeze `capital_expenditure_amount_close_industry` after batch 01. Do not spend more budget on same-axis polishing of the 84d close-normalized variant; move future research to a different normalization or a different field family.

**Rationale**: The branch is below the submission floor on the official IS gates, and the drawdown is too high to treat it as a near-pass. The low-crowding field is worth remembering, but the current formulation is not a submission candidate.

**Consequences**:
- `runs/simulation-captures/2026-04-24-capital-expenditure-amount-close-industry-batch-01.json` records the official capture.
- `runs/expression-families/2026-04-24-capital-expenditure-amount-close-industry.md` now carries the batch result and frozen posture.
- The current research posture remains: no submit-ready alpha yet.

## 2026-04-26 | ALPHA-DECISION-021 | Adopt incubation protocol v0.3

**decision_id**: `incubation-protocol-adopted-v0.3`

**Context**: The project had a strong stop / freeze posture, but it lacked a protected mid-layer for families that need minimum-depth exploration before a permanent kill or freeze. That gap was causing shallow families to be terminated before the B / C / D / E path could finish.

**Decision**: Adopt `harness/incubation-protocol.json` as the canonical incubation rule source for the project. The new state machine is `S-1 -> S0 -> A -> B -> C -> D -> E -> exploit / hold / kill`, with `screen_kill` reserved for S-1 / S0 pure-noise exits only.

**Key Rules**:
- Inhibition Rule: if `min_depth_completed == false`, do not write a permanent stop memo and do not mark the family as a permanent `freeze` or `kill`.
- Cold-pool reclaim: reclaimed budget stays in `cold_pool` until a family completes an incubation cycle or the release window opens, then it is released by priority to new scouting candidates first.
- Causal template: every E-stage alpha must carry a short causal statement, mechanism class, falsifier, reverse-event test, and literature tags.
- Global corr proxy: use the three anchor pools plus the anchor-diversity penalty and periodic calibration; do not treat a shallow anchor pool as low risk.
- Sign-flip control still applies through A, B, C, and D whenever the baseline or first simple control is negative.

**Rationale**: The new protocol preserves the existing front-door gate and sign-flip discipline while adding a protected middle layer that can carry families to a minimum evidence depth before any permanent stop decision.

**Consequences**:
- New family work can be incubated without weakening the existing freeze / kill discipline.
- Budget reclaim and release are now explicit, rather than being handled as an implicit side effect of a stop memo.
- Future helpers must read the ledger and protocol before they decide whether a family is eligible for a permanent stop.

## 2026-04-26 | ALPHA-DECISION-022 | Close the `pcr_oi_720` session and open the qfv4 scout queue

**decision_id**: `pcr_oi_720-session-close`

**Context**: `pcr_oi_720` completed the protected A/B/C path and the final E-stage repair sweep, but the ledger still keeps the family on hold and `harness/progress.md` had not yet been cleared back to idle.

**Decision**: Mark the session idle, leave the ledger state untouched, and pivot the next research hour to the analyst qfv4 sibling scout queue.

**Summary**: `pcr_oi_720` 已完成 A/B/C/E 阶段及三轮 E 阶段修复，最佳候选 `ZYWOgoMY`（TEST Sharpe `1.24` / Fitness `0.60`），因 `LOW_FITNESS` 持续未通过，家族转为 hold，会话收尾。

**Consequences**:
- `harness/progress.md` now shows no active feature and idle session status.
- `runs/research-queues/2026-04-26-s1-analyst-qfv4-scout.md` records the next S-1 scout queue.
- Fresh windows should treat the qfv4 analyst sibling pair as the next live source probe, not the retired `pcr_oi_720` lane.

## 2026-04-27 | ALPHA-DECISION-023 | Pivot from the closed qfv4 scout to a profitability / value scout

**decision_id**: `s1-profitability-value-scout`

**Context**: The qfv4 scout batch is now closed with all three candidates failing TEST on the simple S0 baseline, while the live Data Explorer search surfaced a cleaner low-crowding profitability/value cluster with higher coverage than the frozen EPS and operating-income lanes.

**Decision**: Start the next S-1 scout on `proforma_earnings_to_price`, with `return_on_invested_capital_4` as the primary pure-fundamental backup and `cash_earnings_return_on_equity` / `mdl177_growthanalystmodel_qga_niroe_alt` as controls. Keep `harness/progress.md` idle and do not touch the ledger until a field clears S0.

**Rationale**: The profitability/value cluster offers lower visible crowding and better coverage than the dead qfv4 branch, while staying outside the options / sentiment lanes the current session should avoid.

**Consequences**:
- `harness/progress.md` and `runs/research-contracts/current-incubation-summary.md` now point to the profitability / value scout.
- The next S-1 baseline should be the simple `ts_rank(<field>, 20)` shape, not more qfv4 polishing.
- The ledger remains untouched until a candidate earns a real S0 result.
## 2026-04-27 | ALPHA-DECISION-024 | Retire `proforma_earnings_to_price` after failed sign-flip and rotate to cash fallback

**decision_id**: `proforma-earnings-to-price-signflip-fail`

**Context**: The official Simulate control `-ts_rank(proforma_earnings_to_price, 20)` completed as alpha `QP21klOp`, but the TEST period turned negative.

**Decision**: Retire `proforma_earnings_to_price`, do not register an incubate family, and pivot the next research hour to `cash_earnings_return_on_equity`.

**Summary**: `QP21klOp` came back IS Sharpe `0.93` / Fitness `0.32`, TEST Sharpe `-0.57` / Fitness `-0.13`.

**Consequences**:
- `runs/submission-memos/2026-04-27-proforma-earnings-to-price-signflip.md` records the official result.
- `runs/research-contracts/current-incubation-summary.md`, `runs/research-queues/2026-04-27-s1-profitability-value-scout.md`, and `harness/progress.md` pivot the queue to `cash_earnings_return_on_equity`.
- The ledger stays unchanged because no field cleared S0 into incubate.
## 2026-04-27 | ALPHA-DECISION-025 | Retire `cash_earnings_return_on_equity` after weak sign-flip and rotate to mdl177 fallback

**decision_id**: `cash-earnings-return-on-equity-signflip-fail`

**Context**: The official Simulate baseline `ts_rank(cash_earnings_return_on_equity, 20)` came back weak and negative on TEST. The mandatory sign-flip recovered TEST sign, but the line still failed the continuation floor on IS Sharpe and Fitness.

**Decision**: Retire `cash_earnings_return_on_equity` for the current budget and pivot the next research hour to `mdl177_growthanalystmodel_qga_niroe_alt`.

**Summary**: `A1gRMvZd` came back IS Sharpe `-0.05` / Fitness `0`, TEST Sharpe `-0.47` / Fitness `-0.09`; `0meb06eK` came back IS Sharpe `0.05` / Fitness `0`, TEST Sharpe `0.47` / Fitness `0.09`.

**Consequences**:
- `runs/research-contracts/2026-04-27-cash-earnings-return-on-equity-prescreen-results.md` records the official result.
- `runs/research-queues/2026-04-27-s1-profitability-value-scout.md`, `runs/research-contracts/current-incubation-summary.md`, and `harness/progress.md` now pivot to `mdl177_growthanalystmodel_qga_niroe_alt`.
- The ledger stays unchanged because no field cleared S0 into incubate.
## 2026-04-27 | ALPHA-DECISION-026 | Close the profitability/value scout after mdl177 stays too weak and pivot to growth potential rerating

**decision_id**: `profitability-value-scout-close-after-mdl177`

**Context**: The last profitability/value fallback `mdl177_growthanalystmodel_qga_niroe_alt` was tested after the earlier cash/proforma/ROI fallback chain failed. The official baseline `ts_rank(mdl177_growthanalystmodel_qga_niroe_alt, 20)` came back positive but still too weak to justify opening incubate.

**Decision**: Close the profitability/value family for the current budget, leave the ledger untouched, and pivot the next research hour to `growth_potential_rank_derivative`.

**Summary**: `leQLXVle` came back IS Sharpe `0.34` / Fitness `0.06`, TEST Sharpe `0.66` / Fitness `0.18`, Turnover `42.25%`.

**Consequences**:
- `runs/research-contracts/2026-04-27-mdl177-growthanalystmodel-qga-niroe-alt-prescreen-results.md` records the official result.
- `runs/research-contracts/current-incubation-summary.md`, `runs/research-queues/2026-04-27-s1-profitability-value-scout.md`, and `harness/progress.md` now mark the profitability/value lane as closed and point the next session to `growth_potential_rank_derivative`.
- The ledger stays unchanged because no field cleared S0 into incubate.

## 2026-04-27 | ALPHA-DECISION-027 | Record S-1 Data Explorer verification rule outside the protocol JSON schema

**decision_id**: `s1-precheck-dataexplorer-verification-note`

**Context**: `harness/incubation-protocol.json` already exposes the S-1 threshold block, but it does not provide a dedicated extension slot for the new precheck flag without risking schema drift.

**Decision**: Keep `protocol_version` at `0.3` for now and record the new rule here instead of mutating the JSON schema.

**Rule to carry forward**: S-1 scouting must verify the field in Data Explorer before scout generation; a search miss should be treated as `pending_verification`, not `source_missing`.

**Consequences**: A future protocol revision can add `s1_precheck_require_dataexplorer_verification: true` and the matching verification note once the schema layer is ready.

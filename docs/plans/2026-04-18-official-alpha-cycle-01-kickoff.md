# Official Alpha Cycle 01 Kickoff Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Kick off `official-alpha-cycle-01` with a real research queue and the first primary-direction field-search pack, with harness state and verification kept consistent.

**Architecture:** Use the harness cycle as task truth, write durable research artifacts under `runs/`, and keep official platform facts separated from local hypotheses. The first cycle prioritizes one interpretable primary direction (`analyst_eps_price_industry`) plus backup lanes, instead of pretending field availability or submission thresholds are already verified on the live platform.

**Tech Stack:** Markdown, JSON, project templates under `templates/`, harness shell scripts under `harness/`, and `research_queue_builder.py` from `/Users/zpdedn/.codex/skills/worldquant-brain-alpha-engineering/scripts/`

---

### Task 1: Lock The Research Queue Input

**Files:**
- Create: `docs/plans/2026-04-18-official-alpha-cycle-01-kickoff.md`
- Create: `runs/research-queues/official-alpha-cycle-01.json`
- Read: `templates/research-queue.template.json`
- Read: `harness/cycles/official-alpha-cycle-01.json`
- Read: `/Users/zpdedn/Documents/Obsidian Vault/个人项目/Worldquantbrain/03-研究方法/05-首批真实候选池.md`
- Read: `/Users/zpdedn/Documents/Obsidian Vault/个人项目/Worldquantbrain/03-研究方法/06-首批真实候选优先级.md`

**Step 1: Choose the primary direction and backlog shape**

Pick one primary line for the first formal cycle and keep at least three backup lanes in the queue. Use `analyst_eps_price_industry` as the default primary direction unless local evidence shows a stronger first-cycle choice.

**Step 2: Write the real queue JSON**

Create `runs/research-queues/official-alpha-cycle-01.json` with at least these directions:

- `analyst_eps_price_industry`
- `event_option_volume_gate`
- `sentiment_buzz_stability`
- `sales_delta_fundamental`

Also keep lower-priority hold or drop lanes so the queue has real opportunity-cost ordering.

**Step 3: Record verification boundaries in the JSON metadata**

Add metadata that says live WorldQuant Learn pages currently redirect to sign-in in this session, so account-specific field visibility and current submission thresholds still need platform confirmation.

**Step 4: Verify the JSON is script-compatible**

Run:

```bash
python3 /Users/zpdedn/.codex/skills/worldquant-brain-alpha-engineering/scripts/research_queue_builder.py \
  --input /Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/official-alpha-cycle-01.json \
  --format json
```

Expected: exit `0` and ranked JSON on stdout.

### Task 2: Render The Ranked Queue Markdown

**Files:**
- Create: `runs/research-queues/official-alpha-cycle-01.md`
- Read: `runs/research-queues/official-alpha-cycle-01.json`

**Step 1: Generate Markdown from the queue JSON**

Run:

```bash
python3 /Users/zpdedn/.codex/skills/worldquant-brain-alpha-engineering/scripts/research_queue_builder.py \
  --input /Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/official-alpha-cycle-01.json \
  --format markdown \
  --output /Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/official-alpha-cycle-01.md
```

Expected: the Markdown file exists and contains a ranked table.

**Step 2: Read the rendered queue**

Confirm the top of queue matches the intended first-cycle order and does not accidentally promote the crowded control line.

### Task 3: Create The Primary Field-Search Pack

**Files:**
- Create: `runs/field-search-packs/primary-direction-search-pack.md`
- Read: `templates/field-search-pack.template.md`
- Read: `/Users/zpdedn/Documents/Obsidian Vault/个人项目/Worldquantbrain/02-平台基础/07-Data Explorer 与字段研究工作流.md`
- Read: `/Users/zpdedn/Documents/Obsidian Vault/个人项目/Worldquantbrain/02-平台基础/05-数据字段、覆盖率与数据体检.md`

**Step 1: State confirmed facts versus hypotheses**

The pack must explicitly separate:

- confirmed from local project or public-doc summary
- assumed working settings
- account-specific facts that still need WorldQuant platform confirmation

**Step 2: Write the search pack for `analyst_eps_price_industry`**

Include:

- one plain-language hypothesis
- short Data Explorer search terms
- candidate fields or placeholders
- coverage and crowding checks
- one baseline expression plus same-family follow-ups
- the most likely first failure

**Step 3: Keep fake certainty out**

Do not claim current field availability, coverage numbers, or live submission thresholds unless they were verified on the official platform in this session.

**Step 4: Verify the Markdown file exists and is non-empty**

Run:

```bash
test -s /Users/zpdedn/Documents/project/Worldquantbrain/runs/field-search-packs/primary-direction-search-pack.md
```

Expected: exit `0`.

### Task 4: Sync Harness State And Next Work

**Files:**
- Read: `harness/state/cycles/official-alpha-cycle-01.json`
- Update through command: `./harness/coding-session.sh finish ALPHA-QUEUE-001 --summary "..."`
- Next command: `./harness/coding-session.sh start ALPHA-FIELD-001`

**Step 1: Finish the queue feature only after fresh verification**

Run:

```bash
./harness/coding-session.sh finish ALPHA-QUEUE-001 --summary "Created the first official research queue JSON and ranked Markdown for official-alpha-cycle-01."
```

Expected: harness verification succeeds for `research-queue-json`.

**Step 2: Start the field-pack feature**

Run:

```bash
./harness/coding-session.sh start ALPHA-FIELD-001
```

Expected: `ALPHA-FIELD-001` becomes the active feature.

**Step 3: Finish the field-pack feature only if the Markdown verification is fresh**

Run:

```bash
./harness/coding-session.sh finish ALPHA-FIELD-001 --summary "Created the primary-direction field-search pack with confirmed-versus-assumed boundaries."
```

Expected: harness verification succeeds for `markdown-file`.

# KB Promotion Candidate

## Promotion Guardrail
- This file is a promotion candidate, not automatic truth.
- Only move items into the external KB after they look reusable beyond one cycle and stay valid without account-specific platform state.
- Source cycle: `./harness/cycles/official-alpha-cycle-04.json`
- Source artifacts:
  - `./runs/learning-loops/official-alpha-cycle-03-kb-candidate.md`
  - `./runs/learning-loops/official-alpha-cycle-03-promotion-gate.md`
  - `./runs/learning-loops/official-alpha-cycle-03-project-lessons.md`
  - `./runs/submission-memos/analyst-sibling-submission-memo.md`
  - `./runs/submission-memos/analyst_afv4MedEPS_close_ts120_indrank_us3k_d1_v1-os-status-2026-04-21.md`
  - `./runs/notes/daily/official-alpha-cycle-day-04.md`

## Candidate Heuristics
- After a submitted alpha is locked, keep OS monitoring separate from the next research lane and do not reopen manual submission review for that locked alpha.
- Give each new family a cheap direct-sign or control test before candidate packaging, same-family polishing, or deeper branching.
- If real `subuniverse_pass` or submission-check evidence is missing, record a blocked memo instead of backfilling a candidate-batch JSON with placeholders.
- Use the first simple batch as a fast-kill gate: if the direct control remains far below candidate quality, demote the family and switch lanes instead of polishing by inertia.

## Not Ready For Promotion
- Do not promote one-cycle family verdicts as universal truths.
- Do not promote field-specific availability claims without fresh official verification.
- Do not treat temporary UI states or current alpha status labels as durable knowledge-basis guidance.

## Why This Belongs In KB Review
- These rules recur across the post-submit monitoring path, the non-analyst branch, and the operating-income follow-up branch.
- The repeated pattern is about workflow discipline, evidence gating, and branch selection, not about one field family.
- The heuristics are usable as durable operating guidance even when the specific alpha, field, or cycle changes.

## Supporting Outputs
- `./runs/submission-memos/analyst-sibling-submission-memo.md`
- `./runs/submission-memos/analyst_afv4MedEPS_close_ts120_indrank_us3k_d1_v1-os-status-2026-04-21.md`
- `./runs/notes/daily/official-alpha-cycle-day-03.md`
- `./runs/notes/daily/official-alpha-cycle-day-04.md`
- `./runs/learning-loops/official-alpha-cycle-03-project-lessons.md`
- `./runs/learning-loops/official-alpha-cycle-03-promotion-gate.md`

## Promotion Posture
- Status: `REVIEW`
- Destination guidance: promote only after a deliberate KB pass confirms these remain valid as reusable project guidance.

## KB 落地判断

- 已经落到外部 KB 的页：
  - `kb://05-资源与来源/04-外部论文与书目补充.md`
  - `kb://03-研究方法/03-低相关与稳健性.md`
  - `kb://04-专题技巧/04-提升 Sharpe 的实战方法.md`
  - `kb://04-专题技巧/05-提升 Returns 与控制 Turnover.md`
- 项目侧回链：
  - `kb://01-外部知识库映射.md`
- Skill 结论：
  - 暂时不需要把这些内容再做成 skill。
  - 这批材料是长期研究方法论，适合放知识库；如果以后要把其中某条变成强制门禁，再考虑规则层或 skill 层。

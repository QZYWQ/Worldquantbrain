#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cycle_analysis import build_cycle_overview


def timestamp_now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def cycle_rel_stem(cycle_rel: str) -> PurePosixPath:
    return PurePosixPath(cycle_rel.replace("./", "", 1))


def project_lessons_rel_path(cycle_rel: str) -> str:
    rel = cycle_rel_stem(cycle_rel)
    return f"./runs/learning-loops/{rel.stem}-project-lessons.md"


def kb_candidate_rel_path(cycle_rel: str) -> str:
    rel = cycle_rel_stem(cycle_rel)
    return f"./runs/learning-loops/{rel.stem}-kb-candidate.md"


def skill_candidate_rel_path(cycle_rel: str) -> str:
    rel = cycle_rel_stem(cycle_rel)
    return f"./runs/learning-loops/{rel.stem}-skill-candidate.md"


def promotion_gate_rel_path(cycle_rel: str) -> str:
    rel = cycle_rel_stem(cycle_rel)
    return f"./runs/learning-loops/{rel.stem}-promotion-gate.md"


def kb_promotion_draft_rel_path(cycle_rel: str) -> str:
    rel = cycle_rel_stem(cycle_rel)
    return f"./runs/learning-loops/{rel.stem}-kb-promotion-draft.md"


def skill_promotion_draft_rel_path(cycle_rel: str) -> str:
    rel = cycle_rel_stem(cycle_rel)
    return f"./runs/learning-loops/{rel.stem}-skill-promotion-draft.md"


def render_list(items, fallback: str = "- none") -> list[str]:
    if not items:
        return [fallback]
    rendered = []
    for item in items:
        text = str(item).strip()
        if not text:
            continue
        rendered.append(text if text.startswith("- ") else f"- {text}")
    return rendered or [fallback]


def unique_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def feature_line(feature: dict) -> str:
    summary = feature.get("evidence", {}).get("summary")
    target = feature.get("verification", {}).get("target")
    parts = [f"`{feature.get('id', 'unknown')}`", feature.get("title", "untitled")]
    if summary:
        parts.append(summary)
    elif target:
        parts.append(f"target: `{target}`")
    return "- " + " | ".join(parts)


def feature_targets(features: list[dict]) -> list[str]:
    targets = []
    for feature in features:
        target = feature.get("verification", {}).get("target")
        if isinstance(target, str) and target.strip():
            targets.append(f"- `{target}`")
    return unique_preserve_order(targets)


def feature_status_lines(features: list[dict]) -> list[str]:
    return [feature_line(feature) for feature in features]


def path_suffix_flags(features: list[dict]) -> set[str]:
    flags: set[str] = set()
    for feature in features:
        target = str(feature.get("verification", {}).get("target", ""))
        if "/submission-memos/" in target:
            flags.add("submission-memo")
        if "/field-search-packs/" in target:
            flags.add("field-search-pack")
        if "/expression-families/" in target:
            flags.add("expression-family")
        if "/simulation-captures/" in target:
            flags.add("simulation-capture")
        if "/candidate-batches/" in target:
            flags.add("candidate-batch")
        if "/research-queues/" in target:
            flags.add("research-queue")
    return flags


def parse_recent_decisions(text: str, limit: int = 3) -> list[tuple[str, str]]:
    parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    decisions: list[tuple[str, str]] = []
    for part in parts:
        lines = [line.rstrip() for line in part.strip().splitlines() if line.strip()]
        if not lines or not lines[0].startswith("## "):
            continue
        heading = lines[0][3:]
        decision_line = next(
            (
                line.replace("**Decision**: ", "", 1)
                for line in lines
                if line.startswith("**Decision**: ")
            ),
            "Decision summary missing.",
        )
        decisions.append((heading, decision_line))
    return decisions[-limit:]


def recent_decision_lines(decision_log_path: Path, limit: int = 3) -> list[str]:
    if not decision_log_path.is_file():
        return ["- Decision log not found."]
    decisions = parse_recent_decisions(decision_log_path.read_text(encoding="utf-8"), limit=limit)
    return render_list([f"`{heading}`: {summary}" for heading, summary in decisions], "- No recent decisions found.")


def build_kb_candidates(overview: dict) -> list[str]:
    completed_flags = path_suffix_flags(overview["completed"])
    blocked_flags = path_suffix_flags(overview["blocked"])
    items: list[str] = []

    if "submission-memo" in completed_flags:
        items.append(
            "Post-submit cycles should treat the submitted alpha as locked while OS remains unresolved, and move follow-up research to a separate branch."
        )

    if {"field-search-pack", "expression-family", "simulation-capture"}.issubset(completed_flags):
        items.append(
            "A new family should get a cheap first sign/control test before spending more time on candidate packaging or same-family polishing."
        )

    if "candidate-batch" in blocked_flags:
        items.append(
            "If real subuniverse or submission-check evidence is missing, record a blocked memo instead of backfilling a candidate-batch JSON with placeholders."
        )

    return render_list(unique_preserve_order(items), "- No durable KB candidates were inferred automatically.")


def build_skill_candidates(overview: dict) -> list[str]:
    completed_flags = path_suffix_flags(overview["completed"])
    blocked_flags = path_suffix_flags(overview["blocked"])
    items: list[str] = []

    if "submission-memo" in completed_flags:
        items.append(
            "Add a post-submit operating rule: keep OS monitoring separate from the next research lane, and do not reopen manual submission review for a locked submitted alpha."
        )

    if "candidate-batch" in blocked_flags:
        items.append(
            "Add a hard gate before candidate-batch generation: require non-null real submission-check or subuniverse evidence; otherwise block the feature instead of fabricating a batch."
        )

    if {"field-search-pack", "expression-family", "simulation-capture"}.issubset(completed_flags) and "candidate-batch" in blocked_flags:
        items.append(
            "Add a fast-kill heuristic for fresh families: if the direct-sign control remains far below candidate quality after the first simple batch, demote the family and switch lanes."
        )

    return render_list(unique_preserve_order(items), "- No stable skill-update candidates were inferred automatically.")


def is_fallback_lines(lines: list[str]) -> bool:
    return len(lines) == 1 and lines[0].startswith("- No ")


def blocked_carry_forward_lines(overview: dict) -> list[str]:
    lines = []
    for feature in overview["blocked"]:
        summary = feature.get("evidence", {}).get("summary")
        if summary:
            lines.append(summary)
    return render_list(unique_preserve_order(lines), "- No blocked carry-forward items.")


def render_project_lessons(
    overview: dict,
    cycle_rel: str,
    report_rel: str,
    decision_log_path: Path,
) -> str:
    counts = overview["counts"]
    lines = [
        "# Project Learning Loop",
        "",
        "## Metadata",
        f"- Generated at: {timestamp_now()}",
        f"- Cycle path: {cycle_rel}",
        f"- Source report: `{report_rel}`",
        "",
        "## Cycle Snapshot",
        f"- Goal: {overview['project_goal']}",
        f"- Cycle type: {overview['cycle_type']}",
        f"- Cycle profile: {overview['cycle_profile']}",
        f"- Feature total: {overview['feature_total']}",
        f"- Completed: {counts.get('completed', 0)}",
        f"- Blocked: {counts.get('blocked', 0)}",
        f"- Pending: {counts.get('pending', 0)}",
        "",
        "## Completed Outputs",
        *feature_targets(overview["completed"]),
        "",
        "## Blocked Or Unresolved",
        *feature_status_lines(overview["blocked"] + overview["actionable_pending"] + overview["in_progress"]),
        "",
        "## Carry-Forward Notes",
        *blocked_carry_forward_lines(overview),
        "",
        "## Recent Decisions",
        *recent_decision_lines(decision_log_path),
        "",
    ]
    return "\n".join(lines) + "\n"


def render_kb_candidate(
    overview: dict,
    cycle_rel: str,
    report_rel: str,
) -> str:
    lines = [
        "# KB Promotion Candidate",
        "",
        "## Promotion Guardrail",
        "- This file is a promotion candidate, not automatic truth. Only move items into the external KB after they look reusable beyond one cycle.",
        f"- Source cycle: `{cycle_rel}`",
        f"- Source report: `{report_rel}`",
        "",
        "## Candidate Heuristics",
        *build_kb_candidates(overview),
        "",
        "## Not Ready For Promotion",
        "- Do not promote one-cycle family verdicts as universal truths.",
        "- Do not promote field-specific availability claims without fresh official verification.",
        "",
        "## Supporting Outputs",
        *feature_targets(overview["completed"] + overview["blocked"]),
        "",
    ]
    return "\n".join(lines) + "\n"


def kb_gate_status(overview: dict, kb_lines: list[str]) -> tuple[str, list[str]]:
    support_count = len(feature_targets(overview["completed"] + overview["blocked"]))
    if is_fallback_lines(kb_lines):
        return "HOLD", [
            "- No reusable KB heuristics were inferred from this cycle.",
        ]
    if support_count < 2:
        return "HOLD", [
            "- Durable supporting outputs are still too thin for a KB promotion recommendation.",
        ]
    return "REVIEW", [
        "- Candidate heuristics exist and the cycle left at least two durable outputs.",
        "- Keep the scope at method-level guidance, not family-level verdicts.",
    ]


def skill_gate_status(overview: dict, skill_lines: list[str]) -> tuple[str, list[str]]:
    support_count = len(feature_targets(overview["completed"] + overview["blocked"]))
    blocked_count = len(overview["blocked"])
    if is_fallback_lines(skill_lines):
        return "HOLD", [
            "- No stable workflow heuristics were inferred from this cycle.",
        ]
    if support_count < 2:
        return "HOLD", [
            "- Skill promotion needs broader durable evidence than this cycle currently exposes.",
        ]
    if blocked_count == 0:
        return "HOLD", [
            "- This cycle did not expose enough failure discipline to justify a new skill rule yet.",
        ]
    return "REVIEW", [
        "- Candidate items are workflow-level and supported by durable outputs plus real blocking evidence.",
        "- Promotion should still update the skill conservatively, as a process rule rather than a signal verdict.",
    ]


def render_promotion_gate(
    overview: dict,
    cycle_rel: str,
    report_rel: str,
) -> str:
    kb_lines = build_kb_candidates(overview)
    skill_lines = build_skill_candidates(overview)
    kb_status, kb_rationale = kb_gate_status(overview, kb_lines)
    skill_status, skill_rationale = skill_gate_status(overview, skill_lines)

    lines = [
        "# Promotion Gate",
        "",
        "## Metadata",
        f"- Generated at: {timestamp_now()}",
        f"- Source cycle: `{cycle_rel}`",
        f"- Source report: `{report_rel}`",
        "",
        "## Promotion Ladder",
        "- `project-lessons`: keep project-specific facts and carry-forward conclusions.",
        "- `kb-candidate`: only promote method-level heuristics that look reusable beyond one cycle.",
        "- `skill-candidate`: only promote workflow-level rules that improve future research discipline.",
        "",
        "## KB Gate",
        f"- Status: `{kb_status}`",
        "- Minimum bar:",
        "- Statement is not a current-platform fact that belongs to official verification.",
        "- Statement is not just a one-field or one-family verdict.",
        "- Statement is backed by durable project outputs and can plausibly generalize across cycles.",
        "- Current readout:",
        *kb_rationale,
        "- Candidate items:",
        *kb_lines,
        "",
        "## Skill Gate",
        f"- Status: `{skill_status}`",
        "- Minimum bar:",
        "- Rule is workflow-level, not alpha-family-specific.",
        "- Rule tightens evidence, prioritization, or branch-kill discipline.",
        "- Rule does not weaken existing hard rules in the WorldQuant skill.",
        "- Current readout:",
        *skill_rationale,
        "- Candidate items:",
        *skill_lines,
        "",
        "## Explicit Do-Not-Promote Cases",
        "- Current account-specific field availability claims.",
        "- One-cycle verdicts like 'family X is always bad'.",
        "- Temporary UI or OS-status states that belong to official re-check, not long-term method knowledge.",
        "",
        "## Next Action",
        "- If status is `REVIEW`, inspect the candidate file and decide whether to promote it into the external KB or the skill in a separate deliberate change.",
        "- If status is `HOLD`, keep the lesson in the project layer and wait for repeated evidence from later cycles.",
        "",
    ]
    return "\n".join(lines) + "\n"


def render_kb_promotion_draft(
    overview: dict,
    cycle_rel: str,
    report_rel: str,
) -> str:
    kb_lines = build_kb_candidates(overview)
    kb_status, kb_rationale = kb_gate_status(overview, kb_lines)
    lines = [
        "# KB Promotion Draft",
        "",
        "## Promotion Posture",
        f"- Status: `{kb_status}`",
        f"- Source cycle: `{cycle_rel}`",
        f"- Source report: `{report_rel}`",
        "",
        "## Candidate Content",
        *kb_lines,
        "",
        "## Why This Is Or Is Not Ready",
        *kb_rationale,
        "",
        "## Destination Guidance",
        "- Promote into the external WorldQuant knowledge base only if the statement is method-level and still looks valid beyond one cycle.",
        "- Keep account-specific facts, UI states, and family verdicts out of the KB.",
        "",
        "## Promotion Checklist",
        "- Rewrite each item as durable research guidance, not as a report recap.",
        "- Remove or soften claims that depend on one field, one family, or one temporary platform state.",
        "- Link back to the originating cycle artifacts for auditability.",
        "",
    ]
    return "\n".join(lines) + "\n"


def render_skill_promotion_draft(
    overview: dict,
    cycle_rel: str,
    report_rel: str,
) -> str:
    skill_lines = build_skill_candidates(overview)
    skill_status, skill_rationale = skill_gate_status(overview, skill_lines)
    lines = [
        "# Skill Promotion Draft",
        "",
        "## Promotion Posture",
        f"- Status: `{skill_status}`",
        f"- Source cycle: `{cycle_rel}`",
        f"- Source report: `{report_rel}`",
        "",
        "## Candidate Rules",
        *skill_lines,
        "",
        "## Why This Is Or Is Not Ready",
        *skill_rationale,
        "",
        "## Destination Guidance",
        "- Promote only workflow-level rules into the WorldQuant skill.",
        "- Keep signal-specific claims, field judgments, and current platform facts out of the skill body.",
        "",
        "## Promotion Checklist",
        "- Rewrite each item as a stable execution rule or gating rule.",
        "- Check that the new rule tightens rigor without slowing trivial work unnecessarily.",
        "- Verify the rule does not conflict with existing hard rules in the skill.",
        "",
    ]
    return "\n".join(lines) + "\n"


def render_skill_candidate(
    overview: dict,
    cycle_rel: str,
    report_rel: str,
) -> str:
    lines = [
        "# Skill Promotion Candidate",
        "",
        "## Scope Guardrail",
        "- Only promote workflow-level heuristics into the WorldQuant skill.",
        "- Do not encode one family, one field, or one cycle outcome as a permanent skill rule.",
        f"- Source cycle: `{cycle_rel}`",
        f"- Source report: `{report_rel}`",
        "",
        "## Candidate Skill Rules",
        *build_skill_candidates(overview),
        "",
        "## Explicit Non-Rules",
        "- Do not turn a weak branch result into a global statement that the whole family is always bad.",
        "- Do not weaken evidence requirements just because a branch feels promising.",
        "",
        "## Blocking Evidence To Keep In Mind",
        *blocked_carry_forward_lines(overview),
        "",
    ]
    return "\n".join(lines) + "\n"


def write_learning_loop_bundle(
    cycle_path: Path,
    cycle_rel: str,
    project_out: Path,
    kb_out: Path,
    skill_out: Path,
    promotion_out: Path,
    kb_draft_out: Path,
    skill_draft_out: Path,
    report_rel: str,
    decision_log_path: Path,
) -> None:
    payload = read_json(cycle_path)
    overview = build_cycle_overview(payload, cycle_rel)

    write_text(project_out, render_project_lessons(overview, cycle_rel, report_rel, decision_log_path))
    write_text(kb_out, render_kb_candidate(overview, cycle_rel, report_rel))
    write_text(skill_out, render_skill_candidate(overview, cycle_rel, report_rel))
    write_text(promotion_out, render_promotion_gate(overview, cycle_rel, report_rel))
    write_text(kb_draft_out, render_kb_promotion_draft(overview, cycle_rel, report_rel))
    write_text(skill_draft_out, render_skill_promotion_draft(overview, cycle_rel, report_rel))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate deterministic learning-loop artifacts from a WorldQuant harness cycle."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in [
        "project-lessons-path",
        "kb-candidate-path",
        "skill-candidate-path",
        "promotion-gate-path",
        "kb-promotion-draft-path",
        "skill-promotion-draft-path",
    ]:
        sub = subparsers.add_parser(command)
        sub.add_argument("cycle_rel")

    write_bundle = subparsers.add_parser("write-bundle")
    write_bundle.add_argument("cycle_path")
    write_bundle.add_argument("cycle_rel")
    write_bundle.add_argument("project_out")
    write_bundle.add_argument("kb_out")
    write_bundle.add_argument("skill_out")
    write_bundle.add_argument("promotion_out")
    write_bundle.add_argument("kb_draft_out")
    write_bundle.add_argument("skill_draft_out")
    write_bundle.add_argument("report_rel")
    write_bundle.add_argument("decision_log_path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "project-lessons-path":
        sys.stdout.write(project_lessons_rel_path(args.cycle_rel) + "\n")
        return 0
    if args.command == "kb-candidate-path":
        sys.stdout.write(kb_candidate_rel_path(args.cycle_rel) + "\n")
        return 0
    if args.command == "skill-candidate-path":
        sys.stdout.write(skill_candidate_rel_path(args.cycle_rel) + "\n")
        return 0
    if args.command == "promotion-gate-path":
        sys.stdout.write(promotion_gate_rel_path(args.cycle_rel) + "\n")
        return 0
    if args.command == "kb-promotion-draft-path":
        sys.stdout.write(kb_promotion_draft_rel_path(args.cycle_rel) + "\n")
        return 0
    if args.command == "skill-promotion-draft-path":
        sys.stdout.write(skill_promotion_draft_rel_path(args.cycle_rel) + "\n")
        return 0
    if args.command == "write-bundle":
        write_learning_loop_bundle(
            Path(args.cycle_path),
            args.cycle_rel,
            Path(args.project_out),
            Path(args.kb_out),
            Path(args.skill_out),
            Path(args.promotion_out),
            Path(args.kb_draft_out),
            Path(args.skill_draft_out),
            args.report_rel,
            Path(args.decision_log_path),
        )
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

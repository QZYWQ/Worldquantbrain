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

from cycle_analysis import build_cycle_overview, build_focus_selection, build_session_brief_rel_path


def timestamp_now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def rel_path_stem(cycle_rel: str) -> PurePosixPath:
    return PurePosixPath(cycle_rel.replace("./", "", 1))


def cycle_report_rel_path(cycle_rel: str) -> str:
    rel = rel_path_stem(cycle_rel)
    return f"./harness/reports/{rel.stem}-report.md"


def resume_brief_rel_path(cycle_rel: str) -> str:
    rel = rel_path_stem(cycle_rel)
    return f"./harness/reports/{rel.stem}-resume-brief.md"


def session_brief_rel_path(cycle_path: Path, cycle_rel: str) -> str:
    payload = read_json(cycle_path)
    overview = build_cycle_overview(payload, cycle_rel)
    selection = build_focus_selection(overview)
    return build_session_brief_rel_path(cycle_rel, selection["focus_feature"])


def project_root_from_cycle_path(cycle_path: Path) -> Path:
    resolved = cycle_path.resolve()
    for parent in resolved.parents:
        if parent.name == "harness":
            return parent.parent
    return resolved.parent


def latest_evolution_bootstrap_report_path(cycle_path: Path) -> Path | None:
    project_root = project_root_from_cycle_path(cycle_path)
    report_dir = project_root / "runs" / "research-contracts"
    if not report_dir.exists():
        return None

    cycle_stem = cycle_path.stem or "bootstrap"
    matches = sorted(
        report_dir.glob(f"*-{cycle_stem}-evolution-bootstrap.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def render_list(items, fallback: str = "- none"):
    if not items:
        return [fallback]

    rendered = []
    for item in items:
        stripped = str(item).strip()
        rendered.append(stripped if stripped.startswith("- ") else f"- {stripped}")
    return rendered


def fresh_window_protocol_lines() -> list[str]:
    return [
        "## Fresh-Window Protocol",
        "",
        "- Reload the project truth in this order: `./AGENTS.md`, `./00-项目总索引.md`, `./02-工作流索引.md`, `./harness/AGENTS.md`, `./runs/research-contracts/window-bootstrap-and-signflip-protocol.md`, then the latest family registry, next-step decision, freeze / stop / closure memo, official live recheck / submission memo, and simulation capture.",
        "- Treat chat memory as advisory only; the project files are binding when they exist.",
        "- If baseline or first simple control Sharpe is negative, flip the final executable expression before any lookback, smoothing, neutralization, or group retune.",
        "- When you write a simulation capture that needs that flip, set `batch_policy.required_sign_flip_source_index` to `0` or `1` and capture the sign-flipped control immediately after the negative source control.",
        "",
    ]


def normalize_source_ref(ref, external_kb_root: Path) -> str:
    text = str(ref).strip()
    if not text:
        return text
    if text.startswith("kb://") or text.startswith("./") or text.startswith("../"):
        return text

    candidate = Path(text).expanduser()
    try:
        relative = candidate.resolve().relative_to(external_kb_root)
    except Exception:
        return text
    return f"kb://{relative.as_posix()}"


def parse_frontmatter(text: str):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    result = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def extract_markdown_section(text: str, title: str):
    pattern = rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        return []
    lines = [line.rstrip() for line in match.group(1).strip().splitlines()]
    return [line for line in lines if line.strip()]


def parse_recent_decisions(text: str, limit: int = 3):
    parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    decisions = []
    for part in parts:
        lines = [line.rstrip() for line in part.strip().splitlines() if line.strip()]
        if not lines or not lines[0].startswith("## "):
            continue
        heading = lines[0][3:]
        decision_line = next(
            (line.replace("**Decision**: ", "", 1) for line in lines if line.startswith("**Decision**: ")),
            "Decision summary missing.",
        )
        decisions.append((heading, decision_line))
    return decisions[-limit:]


def render_focus_feature(feature, external_kb_root: Path):
    if feature is None:
        return ["- none"]

    lines = [
        f"- ID: {feature.get('id', 'unknown')}",
        f"- Title: {feature.get('title', 'untitled')}",
        f"- Priority: {feature.get('priority', 'unknown')}",
        f"- Category: {feature.get('category', 'unknown')}",
        f"- Status: {feature.get('status', 'unknown')}",
        f"- Description: {feature.get('description', '')}",
        "- Dependencies:",
    ]

    dependencies = feature.get("dependencies", [])
    if dependencies:
        lines.extend(f"  - {item}" for item in dependencies)
    else:
        lines.append("  - none")

    lines.append("- Acceptance Criteria:")
    criteria = feature.get("acceptance_criteria", [])
    if criteria:
        lines.extend(f"  - {item}" for item in criteria)
    else:
        lines.append("  - none")

    verification = feature.get("verification", {})
    lines.extend(
        [
            f"- Verification mode: {verification.get('mode', 'unknown')}",
            f"- Verification target: {verification.get('target', 'unknown')}",
            "- Source Refs:",
        ]
    )

    source_refs = feature.get("source_refs", [])
    if source_refs:
        lines.extend(f"  - {normalize_source_ref(item, external_kb_root)}" for item in source_refs)
    else:
        lines.append("  - none")

    return lines


def match_template(feature, mode_registry):
    if feature is None:
        return None
    for ref in feature.get("source_refs", []):
        if str(ref).startswith("./templates/"):
            return ref
    mode = feature.get("verification", {}).get("mode", "")
    mode_config = mode_registry.get(mode, {})
    template_hint = mode_config.get("template_hint")
    return template_hint if isinstance(template_hint, str) and template_hint else None


def match_script(feature, mode_registry):
    if feature is None:
        return None
    mode = feature.get("verification", {}).get("mode", "")
    mode_config = mode_registry.get(mode, {})
    script_hint = mode_config.get("script_hint")
    return script_hint if isinstance(script_hint, str) and script_hint else None


def expected_outputs(feature, mode_registry):
    if feature is None:
        return ["- none"]

    verification_target = feature.get("verification", {}).get("target")
    outputs = []
    if verification_target:
        outputs.append(verification_target)

    mode = feature.get("verification", {}).get("mode", "")
    mode_config = mode_registry.get(mode, {})
    extra_output_hints = mode_config.get("extra_output_hints", [])
    if isinstance(extra_output_hints, list):
        outputs.extend(item for item in extra_output_hints if isinstance(item, str) and item.strip())
    return render_list(outputs)


def dependency_lines(feature, by_id):
    if feature is None:
        return ["- none"]

    dependencies = feature.get("dependencies", [])
    if not dependencies:
        return ["- none"]

    lines = []
    for dep in dependencies:
        dep_feature = by_id.get(dep)
        status = dep_feature.get("status", "missing") if dep_feature else "missing"
        lines.append(f"- {dep}: {status}")
    return lines


def write_cycle_report_document(
    cycle_path: Path,
    cycle_rel: str,
    report_path: Path,
    doctor_status: str,
    doctor_output: str,
) -> None:
    payload = read_json(cycle_path)
    overview = build_cycle_overview(payload, cycle_rel)
    counts = overview["counts"]
    completed = overview["completed"]
    blocked = overview["blocked"]
    project_root = project_root_from_cycle_path(cycle_path)
    bootstrap_report = latest_evolution_bootstrap_report_path(cycle_path)
    if bootstrap_report is not None:
        try:
            bootstrap_rel = f"./{bootstrap_report.relative_to(project_root).as_posix()}"
        except Exception:
            bootstrap_rel = bootstrap_report.as_posix()
    else:
        bootstrap_rel = "none"

    def render_feature(feature):
        parts = [
            feature.get("id", "unknown"),
            feature.get("title", "untitled"),
        ]
        summary = feature.get("evidence", {}).get("summary")
        if summary:
            parts.append(f"summary: {summary}")
        return "- " + " | ".join(parts)

    lines = [
        "# Cycle Report",
        "",
        "## Metadata",
        "",
        f"- Generated at: {timestamp_now()}",
        f"- Cycle path: {cycle_rel}",
        f"- Cycle type: {overview['cycle_type']}",
        f"- Cycle profile: {overview['cycle_profile']}",
    ]

    if overview["is_bootstrap"]:
        lines.append("- Note: Report generated from bootstrap fallback state.")

    lines.extend(
        [
            f"- Project goal: {overview['project_goal']}",
            f"- Feature total: {overview['feature_total']}",
            "",
            "## Status Counts",
            "",
        ]
    )

    for key in ["pending", "in_progress", "blocked", "completed"]:
        lines.append(f"- {key}: {counts.get(key, 0)}")

    lines.extend(
        [
            "",
            "## Next Actionable Feature",
            "",
            f"- {overview['next_id']}",
            "",
            "## Evolution Bootstrap Summary",
            "",
            f"- Latest report: {bootstrap_rel}",
            "- Purpose: offline lineage-aware seed generation for the next candidate batch.",
            "",
            "## Doctor",
            "",
            f"- Status: {doctor_status}",
            "",
            "```text",
            doctor_output,
            "```",
            "",
            "## Completed Features",
            "",
        ]
    )

    if completed:
        lines.extend(render_feature(feature) for feature in completed)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Blocked Features",
            "",
        ]
    )

    if blocked:
        lines.extend(render_feature(feature) for feature in blocked)
    else:
        lines.append("- none")

    write_text(report_path, "\n".join(lines) + "\n")


def write_resume_brief_document(
    cycle_path: Path,
    cycle_rel: str,
    brief_path: Path,
    progress_path: Path,
    decision_log_path: Path,
    report_rel: str,
    report_path: Path,
    doctor_status: str,
    doctor_output: str,
    external_kb_root: Path,
) -> None:
    payload = read_json(cycle_path)
    progress_text = progress_path.read_text(encoding="utf-8")
    decision_log_text = decision_log_path.read_text(encoding="utf-8")

    progress_frontmatter = parse_frontmatter(progress_text)
    recent_activity = extract_markdown_section(progress_text, "Recent Activity")
    resume_checklist = extract_markdown_section(progress_text, "Resume Checklist")
    recent_decisions = parse_recent_decisions(decision_log_text)

    overview = build_cycle_overview(payload, cycle_rel)
    selection = build_focus_selection(overview)
    counts = overview["counts"]
    blocked = overview["blocked"]
    focus_feature = selection["focus_feature"]
    recommendation_heading = selection["recommendation_heading"]
    execution_suggestion = selection.get("execution_suggestion")
    execution_reason = selection.get("execution_reason")
    report_status = "present" if report_path.exists() else "missing"
    bootstrap_warning = "This is the bootstrap fallback cycle, not a formal official alpha cycle."
    project_root = project_root_from_cycle_path(cycle_path)
    bootstrap_report = latest_evolution_bootstrap_report_path(cycle_path)
    if bootstrap_report is not None:
        try:
            bootstrap_rel = f"./{bootstrap_report.relative_to(project_root).as_posix()}"
        except Exception:
            bootstrap_rel = bootstrap_report.as_posix()
    else:
        bootstrap_rel = "none"

    lines = [
        "# Resume Brief",
        "",
        "## Metadata",
        "",
        f"- Generated at: {timestamp_now()}",
        f"- Cycle path: {cycle_rel}",
        f"- Cycle type: {overview['cycle_type']}",
        f"- Cycle profile: {overview['cycle_profile']}",
        f"- Project goal: {payload.get('project_goal', 'unknown')}",
        "",
    ]

    if overview["is_bootstrap"]:
        lines.extend(
            [
                "## Warning",
                "",
                f"- {bootstrap_warning}",
                "",
            ]
        )

    lines.extend(fresh_window_protocol_lines())

    lines.extend(
        [
            "## Current Cycle Snapshot",
            "",
        ]
    )

    for key in ["pending", "in_progress", "blocked", "completed"]:
        lines.append(f"- {key}: {counts.get(key, 0)}")

    lines.extend(
        [
            f"- Feature total: {overview['feature_total']}",
            "",
            "## Doctor",
            "",
            f"- Status: {doctor_status}",
            "",
            "```text",
            doctor_output,
            "```",
            "",
            "## Session Snapshot",
            "",
            f"- Current session: {progress_frontmatter.get('current_session', 'unknown')}",
            f"- Active feature: {progress_frontmatter.get('active_feature', 'unknown')}",
            f"- Active status: {progress_frontmatter.get('active_status', 'unknown')}",
            f"- Last verified feature: {progress_frontmatter.get('last_verified_feature', 'unknown')}",
            f"- Last verified at: {progress_frontmatter.get('last_verified_at', 'unknown')}",
            f"- Current branch: {progress_frontmatter.get('current_branch', 'unknown')}",
            f"- Current head: {progress_frontmatter.get('current_head', 'unknown')}",
            "Recent activity:",
        ]
    )

    lines.extend(render_list(recent_activity))
    lines.extend(
        [
            "Resume checklist:",
        ]
    )
    lines.extend(render_list(resume_checklist))
    lines.extend(
        [
            "",
            "## Recommended Next Action",
            "",
            f"- {recommendation_heading}",
        ]
    )

    if execution_suggestion:
        lines.extend(
            [
                "",
                "## Execution Suggestion",
                "",
                f"- Command: {execution_suggestion}",
            ]
        )
        if execution_reason:
            lines.append(f"- Reason: {execution_reason}")

    lines.extend(
        [
            "",
            "## Evolution Bootstrap",
            "",
            f"- Latest report: {bootstrap_rel}",
            "- When the winner archive is ready, run `./harness/coding-session.sh evolution-bootstrap` to seed the next batch.",
            "- The bootstrap run stays offline, records lineage-aware generation artifacts under `runs/evolution/`, and writes a readable summary under `runs/research-contracts/`.",
            "",
            "## Focus Feature",
            "",
        ]
    )
    lines.extend(render_focus_feature(focus_feature, external_kb_root))
    lines.extend(
        [
            "",
            "## Blocked Features",
            "",
        ]
    )

    if blocked:
        lines.extend(
            f"- {feature.get('id', 'unknown')} | {feature.get('title', 'untitled')}"
            for feature in blocked
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Recent Harness Decisions",
            "",
        ]
    )

    if recent_decisions:
        lines.extend(f"- {heading} | {decision}" for heading, decision in recent_decisions)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Latest Cycle Report Reference",
            "",
            f"- Path: {report_rel}",
            f"- Status: {report_status}",
            "",
            "## Key File Pointers",
            "",
            f"- Cycle JSON: {cycle_rel}",
            "- Progress: ./harness/progress.md",
            "- Decision log: ./harness/decision-log.md",
            f"- Cycle report: {report_rel}",
            f"- Resume brief: ./{brief_path.relative_to(brief_path.parents[2]).as_posix()}",
        ]
    )

    write_text(brief_path, "\n".join(lines) + "\n")


def write_session_open_document(
    cycle_path: Path,
    cycle_rel: str,
    brief_path: Path,
    brief_rel: str,
    doctor_status: str,
    doctor_output: str,
    external_kb_root: Path,
    registry_path: Path,
) -> None:
    payload = read_json(cycle_path)
    registry_payload = read_json(registry_path)
    mode_registry = registry_payload.get("modes", {})

    overview = build_cycle_overview(payload, cycle_rel)
    selection = build_focus_selection(overview)
    focus_feature = selection["focus_feature"]
    verification = focus_feature.get("verification", {}) if focus_feature else {}
    template_path = match_template(focus_feature, mode_registry)
    script_hint = match_script(focus_feature, mode_registry)
    bootstrap_warning = "This is the bootstrap fallback cycle, not a formal official alpha cycle."

    lines = [
        "# Session Brief",
        "",
        "## Metadata",
        "",
        f"- Generated at: {timestamp_now()}",
        f"- Cycle path: {cycle_rel}",
        f"- Cycle type: {overview['cycle_type']}",
        f"- Cycle profile: {overview['cycle_profile']}",
        f"- Session brief path: {brief_rel}",
        f"- Doctor status: {doctor_status}",
        "",
    ]

    if overview["is_bootstrap"]:
        lines.extend(
            [
                "## Warning",
                "",
                f"- {bootstrap_warning}",
                "",
            ]
        )

    lines.extend(fresh_window_protocol_lines())

    lines.extend(
        [
            "## Selected Feature",
            "",
        ]
    )

    if focus_feature is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- ID: {focus_feature.get('id', 'unknown')}",
                f"- Title: {focus_feature.get('title', 'untitled')}",
                f"- Priority: {focus_feature.get('priority', 'unknown')}",
                f"- Category: {focus_feature.get('category', 'unknown')}",
                f"- Status: {focus_feature.get('status', 'unknown')}",
                f"- Description: {focus_feature.get('description', '')}",
            ]
        )

    lines.extend(
        [
            "",
            "## Why This Feature Now",
            "",
            f"- {selection['selection_reason']}",
            "",
            "## Prerequisite Check",
            "",
        ]
    )
    lines.extend(dependency_lines(focus_feature, overview["by_id"]))
    lines.extend(
        [
            "",
            "## Source Reading List",
            "",
        ]
    )

    if focus_feature is None:
        lines.append("- none")
    else:
        lines.extend(
            render_list(
                [normalize_source_ref(item, external_kb_root) for item in focus_feature.get("source_refs", [])]
            )
        )

    lines.extend(
        [
            "",
            "## Execution Inputs",
            "",
            f"- Cycle JSON: {cycle_rel}",
            f"- Template: {template_path if template_path else 'none'}",
            f"- Local script: {script_hint if script_hint else 'none'}",
            f"- Verification mode: {verification.get('mode', 'unknown') if focus_feature else 'none'}",
            f"- Verification target: {verification.get('target', 'unknown') if focus_feature else 'none'}",
            "",
            "## Expected Outputs",
            "",
        ]
    )
    lines.extend(expected_outputs(focus_feature, mode_registry))
    lines.extend(
        [
            "",
            "## Verification Plan",
            "",
        ]
    )

    if focus_feature is None:
        lines.append("- No verification plan because no actionable feature was selected.")
    else:
        lines.extend(
            [
                f"- Verification mode: {verification.get('mode', 'unknown')}",
                f"- Verification target: {verification.get('target', 'unknown')}",
                f"- Finish command: ./harness/coding-session.sh finish {focus_feature.get('id')} --summary \"...\"",
                f"- Block command: ./harness/coding-session.sh block {focus_feature.get('id')} --summary \"...\"",
            ]
        )

    lines.extend(
        [
            "",
            "## Evolution Bootstrap",
            "",
            "- When the winner archive is ready, run `./harness/coding-session.sh evolution-bootstrap` to seed the next batch.",
            "- The bootstrap run stays offline, records lineage-aware generation artifacts under `runs/evolution/`, and writes a readable summary under `runs/research-contracts/`.",
            "",
            "## Completion Handoff",
            "",
            "- Claim the feature explicitly with `./harness/coding-session.sh start <FEATURE_ID>` before doing execution work.",
            "- Finish or block the feature through harness commands instead of editing state by hand.",
            "- Attach evidence under `./harness/artifacts/` when the verification mode needs it.",
            "- Write the formal daily note only after the work and evidence are real.",
            "",
            "## Doctor Detail",
            "",
            "```text",
            doctor_output,
            "```",
        ]
    )

    write_text(brief_path, "\n".join(lines) + "\n")


def build_parser():
    parser = argparse.ArgumentParser(description="Render harness report and brief documents.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cycle_report_path_parser = subparsers.add_parser("cycle-report-path")
    cycle_report_path_parser.add_argument("cycle_rel")

    resume_brief_path_parser = subparsers.add_parser("resume-brief-path")
    resume_brief_path_parser.add_argument("cycle_rel")

    session_brief_path_parser = subparsers.add_parser("session-brief-path")
    session_brief_path_parser.add_argument("cycle_path")
    session_brief_path_parser.add_argument("cycle_rel")

    write_cycle_report_parser = subparsers.add_parser("write-cycle-report")
    write_cycle_report_parser.add_argument("cycle_path")
    write_cycle_report_parser.add_argument("cycle_rel")
    write_cycle_report_parser.add_argument("report_path")
    write_cycle_report_parser.add_argument("doctor_status")
    write_cycle_report_parser.add_argument("doctor_output")

    write_resume_brief_parser = subparsers.add_parser("write-resume-brief")
    write_resume_brief_parser.add_argument("cycle_path")
    write_resume_brief_parser.add_argument("cycle_rel")
    write_resume_brief_parser.add_argument("brief_path")
    write_resume_brief_parser.add_argument("progress_path")
    write_resume_brief_parser.add_argument("decision_log_path")
    write_resume_brief_parser.add_argument("report_rel")
    write_resume_brief_parser.add_argument("report_path")
    write_resume_brief_parser.add_argument("doctor_status")
    write_resume_brief_parser.add_argument("doctor_output")
    write_resume_brief_parser.add_argument("external_kb_root")

    write_session_open_parser = subparsers.add_parser("write-session-open")
    write_session_open_parser.add_argument("cycle_path")
    write_session_open_parser.add_argument("cycle_rel")
    write_session_open_parser.add_argument("brief_path")
    write_session_open_parser.add_argument("brief_rel")
    write_session_open_parser.add_argument("doctor_status")
    write_session_open_parser.add_argument("doctor_output")
    write_session_open_parser.add_argument("external_kb_root")
    write_session_open_parser.add_argument("registry_path")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.command == "cycle-report-path":
        print(cycle_report_rel_path(args.cycle_rel))
        return 0

    if args.command == "resume-brief-path":
        print(resume_brief_rel_path(args.cycle_rel))
        return 0

    if args.command == "session-brief-path":
        print(session_brief_rel_path(Path(args.cycle_path), args.cycle_rel))
        return 0

    if args.command == "write-cycle-report":
        write_cycle_report_document(
            cycle_path=Path(args.cycle_path),
            cycle_rel=args.cycle_rel,
            report_path=Path(args.report_path),
            doctor_status=args.doctor_status,
            doctor_output=args.doctor_output,
        )
        return 0

    if args.command == "write-resume-brief":
        write_resume_brief_document(
            cycle_path=Path(args.cycle_path),
            cycle_rel=args.cycle_rel,
            brief_path=Path(args.brief_path),
            progress_path=Path(args.progress_path),
            decision_log_path=Path(args.decision_log_path),
            report_rel=args.report_rel,
            report_path=Path(args.report_path),
            doctor_status=args.doctor_status,
            doctor_output=args.doctor_output,
            external_kb_root=Path(args.external_kb_root).expanduser().resolve(),
        )
        return 0

    if args.command == "write-session-open":
        write_session_open_document(
            cycle_path=Path(args.cycle_path),
            cycle_rel=args.cycle_rel,
            brief_path=Path(args.brief_path),
            brief_rel=args.brief_rel,
            doctor_status=args.doctor_status,
            doctor_output=args.doctor_output,
            external_kb_root=Path(args.external_kb_root).expanduser().resolve(),
            registry_path=Path(args.registry_path),
        )
        return 0

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

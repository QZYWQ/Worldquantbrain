#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path, PurePosixPath


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cycle_analysis import build_cycle_overview, build_feature_index, dependencies_done, missing_dependencies


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def parse_frontmatter(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}

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


def format_scalar(value, default="none") -> str:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return format(value, "g")
    return str(value)


def format_stage_budget(stage_budget) -> str:
    if not isinstance(stage_budget, dict):
        return "n/a"

    parts = []
    for stage in ["S-1", "S0", "A", "B", "C", "D", "E"]:
        value = stage_budget.get(stage, 0)
        if value:
            parts.append(f"{stage}={format_scalar(value, '0')}")
    return ", ".join(parts) if parts else "none"


def command_list_cycle_rel_paths(project_root: Path, active_cycle: str) -> int:
    root = project_root.resolve()
    paths = ["./harness/feature_list.json"]

    cycles_dir = root / "harness" / "cycles"
    if cycles_dir.exists():
        paths.extend("./" + path.relative_to(root).as_posix() for path in sorted(cycles_dir.glob("*.json")))

    seen = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        prefix = "*" if path == active_cycle else " "
        print(f"{prefix} {path}")
    return 0


def command_cycle_summary(feature_path: Path, active_cycle: str, progress_path: Path) -> int:
    payload = read_json(feature_path)
    overview = build_cycle_overview(payload, active_cycle)
    counts = overview["counts"]

    print(f"Active cycle: {active_cycle}")
    print(f"Cycle type: {overview['cycle_type']}")
    print(f"Cycle profile: {overview['cycle_profile']}")
    if overview["is_bootstrap"]:
        print("Warning: active cycle is bootstrap fallback state.")
    print(f"Project goal: {overview['project_goal']}")
    print("Status counts:")
    for key in ["pending", "in_progress", "blocked", "completed"]:
        print(f"- {key}: {counts.get(key, 0)}")
    print(f"Next actionable feature: {overview['next_id']}")
    print(f"Feature total: {overview['feature_total']}")
    print(f"Progress file: {progress_path}")
    return 0


def command_cycle_validate_close_readiness(cycle_path: Path, cycle_rel: str) -> int:
    payload = read_json(cycle_path)

    pending = []
    in_progress = []
    invalid = []

    for feature in payload.get("features", []):
        feature_id = feature.get("id", "unknown")
        status = feature.get("status")
        if status == "pending":
            pending.append(feature_id)
        elif status == "in_progress":
            in_progress.append(feature_id)
        elif status not in {"completed", "blocked"}:
            invalid.append(f"{feature_id}:{status}")

    if invalid:
        print(f"Cycle contains unsupported statuses and cannot be closed: {cycle_rel}")
        print(", ".join(invalid))
        return 1

    if in_progress:
        print(f"Cycle still has in_progress features and cannot be closed: {cycle_rel}")
        print(", ".join(in_progress))
        return 1

    if pending:
        print(f"Cycle still has pending features and cannot be closed: {cycle_rel}")
        print(", ".join(pending))
        return 1

    return 0


def command_cycle_archive_path(cycle_rel: str) -> int:
    rel = PurePosixPath(cycle_rel.replace("./", "", 1))
    print("./harness/archive/" + rel.name)
    return 0


def command_cycle_can_archive(cycle_path: Path) -> int:
    payload = read_json(cycle_path)
    for feature in payload.get("features", []):
        if feature.get("status") == "in_progress":
            return 1
    return 0


def command_next_feature_id(feature_path: Path) -> int:
    payload = read_json(feature_path)
    next_id = build_cycle_overview(payload, "")["next_id"]
    if next_id != "none":
        print(next_id)
    return 0


def command_feature_exists(feature_path: Path, feature_id: str) -> int:
    payload = read_json(feature_path)
    exists = any(feature.get("id") == feature_id for feature in payload.get("features", []))
    return 0 if exists else 1


def command_feature_status(feature_path: Path, feature_id: str) -> int:
    payload = read_json(feature_path)
    for feature in payload.get("features", []):
        if feature.get("id") == feature_id:
            print(feature.get("status", ""))
            break
    return 0


def command_feature_dependencies_met(feature_path: Path, feature_id: str) -> int:
    payload = read_json(feature_path)
    features = payload.get("features", [])
    by_id = build_feature_index(features)

    for feature in features:
        if feature.get("id") != feature_id:
            continue
        return 0 if dependencies_done(feature, by_id) else 1
    return 1


def command_feature_missing_dependencies(feature_path: Path, feature_id: str) -> int:
    payload = read_json(feature_path)
    features = payload.get("features", [])
    by_id = build_feature_index(features)

    for feature in features:
        if feature.get("id") != feature_id:
            continue
        for dep in missing_dependencies(feature, by_id):
            print(dep)
        break
    return 0


def command_in_progress_feature_ids(feature_path: Path) -> int:
    payload = read_json(feature_path)
    for feature in payload.get("features", []):
        if feature.get("status") == "in_progress":
            print(feature.get("id", ""))
    return 0


def command_feature_verification_mode(feature_path: Path, feature_id: str) -> int:
    payload = read_json(feature_path)
    for feature in payload.get("features", []):
        if feature.get("id") == feature_id:
            print(feature.get("verification", {}).get("mode", ""))
            break
    return 0


def command_feature_verification_target(feature_path: Path, feature_id: str) -> int:
    payload = read_json(feature_path)
    for feature in payload.get("features", []):
        if feature.get("id") == feature_id:
            print(feature.get("verification", {}).get("target", ""))
            break
    return 0


def command_print_feature_brief(feature_path: Path, feature_id: str, external_kb_root: Path) -> int:
    payload = read_json(feature_path)
    external_kb = external_kb_root.expanduser().resolve()

    for feature in payload.get("features", []):
        if feature.get("id") != feature_id:
            continue
        print(f"ID: {feature.get('id')}")
        print(f"Priority: {feature.get('priority')}")
        print(f"Category: {feature.get('category')}")
        print(f"Title: {feature.get('title')}")
        print(f"Description: {feature.get('description')}")
        print("Dependencies:")
        for dep in feature.get("dependencies", []):
            print(f"- {dep}")
        if not feature.get("dependencies"):
            print("- none")
        print("Acceptance Criteria:")
        for item in feature.get("acceptance_criteria", []):
            print(f"- {item}")
        print("Source Refs:")
        for item in feature.get("source_refs", []):
            print(f"- {normalize_source_ref(item, external_kb)}")
        verification = feature.get("verification", {})
        print("Verification:")
        print(f"- mode: {verification.get('mode')}")
        print(f"- target: {verification.get('target')}")
        break
    return 0


def command_print_pending_summary(feature_path: Path) -> int:
    payload = read_json(feature_path)
    for feature in payload.get("features", []):
        print(f"{feature.get('id')} | {feature.get('priority')} | {feature.get('status')} | {feature.get('title')}")
    return 0


def command_incubation_summary(ledger_path: Path, progress_path: Path) -> int:
    ledger = read_json(ledger_path)
    policy = ledger.get("policy", {})
    summary = ledger.get("summary", {})
    counts = summary.get("registry_state_counts", {})
    progress = parse_frontmatter(progress_path)

    active_lanes = [
        entry
        for entry in ledger.get("entries", [])
        if entry.get("budget_action") == "incubate"
    ]
    active_lanes.sort(key=lambda entry: (entry.get("priority", 999), entry.get("family_key", "")))

    print(f"- Mode: {format_scalar(policy.get('mode'), 'unknown')}")
    print(f"- Active main: {format_scalar(policy.get('active_main'))}")
    print(f"- Active challenger: {format_scalar(policy.get('active_challenger'))}")
    print(f"- Cold pool balance: {format_scalar(policy.get('cold_pool_balance'))}")
    print(f"- Emergency reserve slots: {format_scalar(policy.get('emergency_reserve_slots'))}")
    print(
        "- Registry states: "
        f"branch={counts.get('branch', 0)}, hold={counts.get('hold', 0)}, kill={counts.get('kill', 0)}"
    )
    print(f"- Submit-ready families: {format_scalar(policy.get('submit_ready_families', 0), '0')}")
    print(
        "- Progress snapshot: "
        f"active_feature={format_scalar(progress.get('active_feature'))}, "
        f"active_status={format_scalar(progress.get('active_status'), 'idle')}, "
        f"last_verified_feature={format_scalar(progress.get('last_verified_feature'))}"
    )
    if not active_lanes:
        print("- Active incubation lanes: none")
    else:
        print("- Active incubation lanes:")
        for entry in active_lanes:
            stop_eligible = entry.get("stop_eligible")
            if stop_eligible is None:
                stop_eligible = entry.get("min_depth_completed", False)
            print(
                "  - "
                f"{entry.get('family_key')} | stage={entry.get('incubation_stage')} | "
                f"stage_budget={format_stage_budget(entry.get('stage_budget'))} | "
                f"screen={format_scalar(entry.get('screen_result'))} | "
                f"min_depth_completed={format_scalar(entry.get('min_depth_completed', False), 'false')} | "
                f"stop_eligible={format_scalar(stop_eligible, 'false')}"
            )
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Run read-only harness state queries.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_cycle_rel_paths = subparsers.add_parser("list-cycle-rel-paths")
    list_cycle_rel_paths.add_argument("project_root")
    list_cycle_rel_paths.add_argument("active_cycle")

    cycle_summary = subparsers.add_parser("cycle-summary")
    cycle_summary.add_argument("feature_path")
    cycle_summary.add_argument("active_cycle")
    cycle_summary.add_argument("progress_path")

    cycle_validate = subparsers.add_parser("cycle-validate-close-readiness")
    cycle_validate.add_argument("cycle_path")
    cycle_validate.add_argument("cycle_rel")

    cycle_archive_path = subparsers.add_parser("cycle-archive-path")
    cycle_archive_path.add_argument("cycle_rel")

    cycle_can_archive = subparsers.add_parser("cycle-can-archive")
    cycle_can_archive.add_argument("cycle_path")

    next_feature_id = subparsers.add_parser("next-feature-id")
    next_feature_id.add_argument("feature_path")

    feature_exists = subparsers.add_parser("feature-exists")
    feature_exists.add_argument("feature_path")
    feature_exists.add_argument("feature_id")

    feature_status = subparsers.add_parser("feature-status")
    feature_status.add_argument("feature_path")
    feature_status.add_argument("feature_id")

    feature_dependencies_met = subparsers.add_parser("feature-dependencies-met")
    feature_dependencies_met.add_argument("feature_path")
    feature_dependencies_met.add_argument("feature_id")

    feature_missing_dependencies = subparsers.add_parser("feature-missing-dependencies")
    feature_missing_dependencies.add_argument("feature_path")
    feature_missing_dependencies.add_argument("feature_id")

    in_progress_feature_ids = subparsers.add_parser("in-progress-feature-ids")
    in_progress_feature_ids.add_argument("feature_path")

    feature_verification_mode = subparsers.add_parser("feature-verification-mode")
    feature_verification_mode.add_argument("feature_path")
    feature_verification_mode.add_argument("feature_id")

    feature_verification_target = subparsers.add_parser("feature-verification-target")
    feature_verification_target.add_argument("feature_path")
    feature_verification_target.add_argument("feature_id")

    print_feature_brief = subparsers.add_parser("print-feature-brief")
    print_feature_brief.add_argument("feature_path")
    print_feature_brief.add_argument("feature_id")
    print_feature_brief.add_argument("external_kb_root")

    print_pending_summary = subparsers.add_parser("print-pending-summary")
    print_pending_summary.add_argument("feature_path")

    incubation_summary = subparsers.add_parser("incubation-summary")
    incubation_summary.add_argument("ledger_path")
    incubation_summary.add_argument("progress_path")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.command == "list-cycle-rel-paths":
        return command_list_cycle_rel_paths(Path(args.project_root), args.active_cycle)
    if args.command == "cycle-summary":
        return command_cycle_summary(Path(args.feature_path), args.active_cycle, Path(args.progress_path))
    if args.command == "cycle-validate-close-readiness":
        return command_cycle_validate_close_readiness(Path(args.cycle_path), args.cycle_rel)
    if args.command == "cycle-archive-path":
        return command_cycle_archive_path(args.cycle_rel)
    if args.command == "cycle-can-archive":
        return command_cycle_can_archive(Path(args.cycle_path))
    if args.command == "next-feature-id":
        return command_next_feature_id(Path(args.feature_path))
    if args.command == "feature-exists":
        return command_feature_exists(Path(args.feature_path), args.feature_id)
    if args.command == "feature-status":
        return command_feature_status(Path(args.feature_path), args.feature_id)
    if args.command == "feature-dependencies-met":
        return command_feature_dependencies_met(Path(args.feature_path), args.feature_id)
    if args.command == "feature-missing-dependencies":
        return command_feature_missing_dependencies(Path(args.feature_path), args.feature_id)
    if args.command == "in-progress-feature-ids":
        return command_in_progress_feature_ids(Path(args.feature_path))
    if args.command == "feature-verification-mode":
        return command_feature_verification_mode(Path(args.feature_path), args.feature_id)
    if args.command == "feature-verification-target":
        return command_feature_verification_target(Path(args.feature_path), args.feature_id)
    if args.command == "print-feature-brief":
        return command_print_feature_brief(Path(args.feature_path), args.feature_id, Path(args.external_kb_root))
    if args.command == "print-pending-summary":
        return command_print_pending_summary(Path(args.feature_path))
    if args.command == "incubation-summary":
        return command_incubation_summary(Path(args.ledger_path), Path(args.progress_path))

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

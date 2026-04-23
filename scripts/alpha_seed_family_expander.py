#!/usr/bin/env python3
"""Build a seed-family priority manifest for local alpha mining.

The expander stays local and evidence-aware:

- it reads existing family docs plus field-search packs
- it optionally folds in success-state memory when capture inputs are provided
- it emits a conservative shortlist for the daily runner to consume

It does not write candidate-batch JSON or trigger official WorldQuant actions.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from alpha_success_core import build_success_rate_state, normalize_family_key


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACT_ROOT = Path("harness/artifacts/alpha-seed-expander")
DEFAULT_PUBLISH_ROOT = Path("runs/learning-loops")
DEFAULT_ALLOWED_STATES = ("exploit", "branch", "explore")
STATE_PRIORITY = {"exploit": 0, "branch": 1, "explore": 2, "hold": 3, "kill": 4}
SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
METADATA_RE = re.compile(r"^\s*-\s+([^:]+):\s*(.*)$")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
PRIMARY_HINT_RE = re.compile(
    r"\b(primary|first item|first branch|best first|best immediate|try .* first|should be tried first|should be the first item)\b",
    re.IGNORECASE,
)
SECONDARY_HINT_RE = re.compile(r"\b(secondary|backup|control|later branch|later)\b", re.IGNORECASE)
DIVERSITY_HINT_RE = re.compile(
    r"\b(lower crowding|less crowded|different family|distinct|diversification|materially different)\b",
    re.IGNORECASE,
)
OFFICIAL_HINT_RE = re.compile(r"\b(official|verified|confirmed in this session|platform check)\b", re.IGNORECASE)


@dataclass(frozen=True)
class FieldSearchPackDoc:
    path: Path
    title: str
    topic: str
    family_key: str
    metadata: dict[str, str]
    hypothesis: str
    why_lines: tuple[str, ...]
    baseline_ideas: tuple[str, ...]
    next_action_codes: tuple[str, ...]
    candidate_fields: tuple[str, ...]
    raw_text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a priority shortlist of seed families.")
    parser.add_argument(
        "--family-dir",
        type=Path,
        default=Path("runs/expression-families"),
        help="Directory containing expression-family markdown docs.",
    )
    parser.add_argument(
        "--field-search-pack-dir",
        type=Path,
        default=Path("runs/field-search-packs"),
        help="Directory containing field-search-pack markdown docs.",
    )
    parser.add_argument(
        "--capture-dir",
        type=Path,
        default=None,
        help="Optional simulation-capture directory used to fold real outcomes into the seed ranking.",
    )
    parser.add_argument(
        "--candidate-batch-dir",
        type=Path,
        default=None,
        help="Optional durable candidate-batch directory used as read-only evidence input.",
    )
    parser.add_argument(
        "--candidate-check-dir",
        type=Path,
        default=None,
        help="Optional candidate-check artifact directory used as read-only evidence input.",
    )
    parser.add_argument(
        "--success-policy",
        type=Path,
        default=Path("harness/alpha-success-policy.json"),
        help="Success-policy JSON used for hard-exclude topic patterns.",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=DEFAULT_ARTIFACT_ROOT,
        help="Parent directory for the generated seed-family manifest bundle.",
    )
    parser.add_argument(
        "--publish-root",
        type=Path,
        default=DEFAULT_PUBLISH_ROOT,
        help="Durable output root used for the emitted manifest copy.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="",
        help="Optional run id override. Defaults to <YYYY-MM-DD>-alpha-seed-expander.",
    )
    parser.add_argument(
        "--shortlist-limit",
        type=int,
        default=8,
        help="Maximum number of non-excluded families to keep in the priority shortlist.",
    )
    parser.add_argument(
        "--allowed-state",
        action="append",
        default=[],
        help="Eligible family states for the shortlist. Can be repeated.",
    )
    return parser.parse_args()


def default_run_id(args: argparse.Namespace) -> str:
    if args.run_id:
        return args.run_id
    return f"{datetime.now().strftime('%Y-%m-%d')}-alpha-seed-expander"


def _allowed_states(args: argparse.Namespace) -> tuple[str, ...]:
    states = [state.strip() for state in args.allowed_state if state.strip()]
    if states:
        return tuple(dict.fromkeys(states))
    return DEFAULT_ALLOWED_STATES


def _normalize_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    resolved = path if path.is_absolute() else (PROJECT_ROOT / path)
    return resolved.resolve(strict=False)


def _default_optional_input(
    args_path: Path | None,
    default_path: Path,
    *,
    family_dir: Path,
) -> Path | None:
    if args_path is not None:
        return _normalize_path(args_path)
    default_resolved = _normalize_path(default_path)
    family_dir_default = _normalize_path(Path("runs/expression-families"))
    if family_dir == family_dir_default and default_resolved and default_resolved.exists():
        return default_resolved
    return None


def load_success_policy(path: Path) -> dict[str, Any]:
    resolved = _normalize_path(path)
    if resolved is None or not resolved.exists():
        return {}
    data = json.loads(resolved.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        heading = SECTION_HEADING_RE.match(line)
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _strip_inline_code(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        return value[1:-1].strip()
    return value


def _parse_metadata(section_text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in section_text.splitlines():
        match = METADATA_RE.match(line)
        if not match:
            continue
        key = normalize_family_key(match.group(1).replace(" ", "_"))
        value = _strip_inline_code(match.group(2))
        if value:
            metadata[key] = value
    return metadata


def _extract_bullets(section_text: str) -> tuple[str, ...]:
    bullets: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return tuple(bullets)


def _extract_numbered_inline_codes(section_text: str) -> tuple[str, ...]:
    items: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("|"):
            continue
        if re.match(r"^\d+\.\s+", stripped):
            items.extend(code.strip() for code in INLINE_CODE_RE.findall(stripped) if code.strip())
    return tuple(dict.fromkeys(items))


def _extract_candidate_fields(section_text: str) -> tuple[str, ...]:
    fields: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not TABLE_ROW_RE.match(stripped):
            continue
        if stripped.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or cells[0].lower() == "field":
            continue
        field_cell = cells[0]
        matches = INLINE_CODE_RE.findall(field_cell)
        field_name = matches[0].strip() if matches else field_cell.strip()
        if field_name:
            fields.append(field_name)
    return tuple(dict.fromkeys(fields))


def parse_field_search_pack(path: Path) -> FieldSearchPackDoc:
    raw_text = path.read_text(encoding="utf-8")
    sections = _split_sections(raw_text)
    metadata = _parse_metadata(sections.get("Metadata", ""))
    title_match = TITLE_RE.search(raw_text)
    title = title_match.group(1).strip() if title_match else path.stem
    topic = metadata.get("topic") or normalize_family_key(path.stem)
    family_key = normalize_family_key(topic)
    hypothesis = sections.get("Hypothesis", "").strip()
    why_lines = _extract_bullets(sections.get("Why This Could Matter", ""))
    baseline_ideas = _extract_numbered_inline_codes(sections.get("Baseline Expression Ideas", ""))
    next_action_codes = tuple(
        dict.fromkeys(code.strip() for code in INLINE_CODE_RE.findall(sections.get("Next Action", "")) if code.strip())
    )
    candidate_fields = _extract_candidate_fields(sections.get("Candidate Fields", ""))
    return FieldSearchPackDoc(
        path=path,
        title=title,
        topic=topic,
        family_key=family_key,
        metadata=metadata,
        hypothesis=hypothesis,
        why_lines=why_lines,
        baseline_ideas=baseline_ideas,
        next_action_codes=next_action_codes,
        candidate_fields=candidate_fields,
        raw_text=raw_text,
    )


def load_field_search_packs(source: Path) -> list[FieldSearchPackDoc]:
    if not source.exists():
        return []
    docs: list[FieldSearchPackDoc] = []
    for path in sorted(source.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        docs.append(parse_field_search_pack(path))
    return docs


def _state_rank(state: str) -> int:
    return STATE_PRIORITY.get(state, 99)


def _float_value(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _matches_any_pattern(texts: Iterable[str], patterns: Sequence[re.Pattern[str]]) -> bool:
    haystack = "\n".join(texts)
    return any(pattern.search(haystack) for pattern in patterns)


def _compile_policy_excludes(policy: dict[str, Any]) -> tuple[re.Pattern[str], ...]:
    compiled: list[re.Pattern[str]] = []
    for pattern in policy.get("hard_exclude_topic_patterns", []):
        if isinstance(pattern, str) and pattern.strip():
            compiled.append(re.compile(pattern, re.IGNORECASE))
    return tuple(compiled)


def _pack_score_components(pack: FieldSearchPackDoc) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if pack.candidate_fields:
        component = min(len(pack.candidate_fields) * 2.0, 10.0)
        score += component
        reasons.append(f"field-pack exposes {len(pack.candidate_fields)} candidate fields")
    if pack.baseline_ideas:
        component = min(len(pack.baseline_ideas) * 1.5, 6.0)
        score += component
        reasons.append(f"field-pack provides {len(pack.baseline_ideas)} baseline ideas")
    if pack.next_action_codes:
        component = min(len(pack.next_action_codes), 4)
        score += float(component)
        reasons.append("field-pack already names concrete next-action expressions/fields")

    if PRIMARY_HINT_RE.search(pack.raw_text):
        score += 10.0
        reasons.append("field-pack explicitly marks this lane as the first or primary seed")
    if SECONDARY_HINT_RE.search(pack.raw_text):
        score -= 2.0
        reasons.append("field-pack frames part of the lane as secondary/control only")
    if DIVERSITY_HINT_RE.search(pack.raw_text):
        score += 4.0
        reasons.append("field-pack argues for diversification or material distinctness")
    if OFFICIAL_HINT_RE.search(pack.raw_text):
        score += 4.0
        reasons.append("field-pack contains explicit official/verified language")
    return score, reasons


def _family_score_components(row: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    state = str(row.get("state") or "")
    state_bonus = {
        "exploit": 40.0,
        "branch": 28.0,
        "explore": 20.0,
        "hold": -20.0,
        "kill": -120.0,
    }.get(state, 0.0)
    if state_bonus:
        score += state_bonus
        reasons.append(f"family state contributes {state_bonus:+.0f} from `{state}`")

    submit_ready_count = int(row.get("submit_ready_count", 0) or 0)
    if submit_ready_count:
        component = min(submit_ready_count * 12.0, 24.0)
        score += component
        reasons.append(f"family has {submit_ready_count} submit-ready outcomes")

    full_gate_count = int(row.get("full_gate_outcome_count", 0) or 0)
    if full_gate_count:
        component = min(full_gate_count * 4.0, 12.0)
        score += component
        reasons.append(f"family has {full_gate_count} full gate records")

    official_count = int(row.get("official_outcome_count", 0) or 0)
    if official_count:
        component = min(official_count * 1.5, 6.0)
        score += component
        reasons.append(f"family has {official_count} official outcomes")

    best_metrics = (row.get("best_outcome") or {}).get("metrics") or {}
    best_fitness = _float_value(best_metrics.get("fitness") or best_metrics.get("is_fitness"), default=0.0)
    best_sharpe = _float_value(best_metrics.get("sharpe") or best_metrics.get("is_sharpe"), default=0.0)
    if best_fitness > 0:
        component = min(best_fitness * 2.0, 6.0)
        score += component
        reasons.append(f"best recorded fitness contributes {component:.2f}")
    elif best_sharpe > 0:
        component = min(best_sharpe, 4.0)
        score += component
        reasons.append(f"best recorded sharpe contributes {component:.2f}")
    return score, reasons


def build_priority_manifest(
    *,
    run_id: str,
    success_state: dict[str, Any],
    field_packs: Sequence[FieldSearchPackDoc],
    success_policy: dict[str, Any],
    allowed_states: Sequence[str],
    shortlist_limit: int,
) -> dict[str, Any]:
    rows_by_family = {
        str(row.get("family_key") or ""): dict(row)
        for row in success_state.get("family_registry_summary", [])
        if str(row.get("family_key") or "")
    }
    packs_by_family: dict[str, list[FieldSearchPackDoc]] = {}
    for pack in field_packs:
        packs_by_family.setdefault(pack.family_key, []).append(pack)

    exclude_patterns = _compile_policy_excludes(success_policy)
    all_family_keys = sorted(set(rows_by_family) | set(packs_by_family))
    family_records: list[dict[str, Any]] = []
    for family_key in all_family_keys:
        row = rows_by_family.get(
            family_key,
            {
                "family_key": family_key,
                "state": "explore",
                "reason": "field-search pack exists but no family registry row was found",
                "topics": [family_key],
                "doc_paths": [],
                "capture_paths": [],
                "baseline_expressions": [],
                "decision_lines": [],
                "explicit_state_hints": [],
                "official_outcome_count": 0,
                "candidate_outcome_count": 0,
                "full_gate_outcome_count": 0,
                "submit_ready_count": 0,
                "strong_candidate_evidence_count": 0,
                "failing_gate_histogram": {},
                "pending_gate_histogram": {},
                "best_outcome": None,
            },
        )
        packs = packs_by_family.get(family_key, [])
        pack_score = 0.0
        pack_reasons: list[str] = []
        for pack in packs:
            component, reasons = _pack_score_components(pack)
            pack_score += component
            pack_reasons.extend(reasons)

        family_score, family_reasons = _family_score_components(row)
        total_score = family_score + pack_score

        match_texts = [
            family_key,
            *(str(topic) for topic in row.get("topics", [])),
            *(str(path) for path in row.get("doc_paths", [])),
            *(str(pack.path) for pack in packs),
            *(pack.title for pack in packs),
        ]
        hard_excluded = _matches_any_pattern(match_texts, exclude_patterns) if exclude_patterns else False
        if hard_excluded:
            total_score -= 200.0
            pack_reasons.append("hard exclude topic pattern matched this family")

        candidate_fields = tuple(dict.fromkeys(field for pack in packs for field in pack.candidate_fields))
        baseline_ideas = tuple(dict.fromkeys(expr for pack in packs for expr in pack.baseline_ideas))
        next_action_codes = tuple(dict.fromkeys(code for pack in packs for code in pack.next_action_codes))
        priority_reasons = tuple(dict.fromkeys([*family_reasons, *pack_reasons]))
        family_records.append(
            {
                "family_key": family_key,
                "state": row.get("state") or "explore",
                "reason": row.get("reason") or "",
                "priority_score": round(total_score, 4),
                "hard_excluded": hard_excluded,
                "topics": list(row.get("topics", [])),
                "doc_paths": list(row.get("doc_paths", [])),
                "field_pack_paths": [pack.path.as_posix() for pack in packs],
                "official_outcome_count": int(row.get("official_outcome_count", 0) or 0),
                "full_gate_outcome_count": int(row.get("full_gate_outcome_count", 0) or 0),
                "submit_ready_count": int(row.get("submit_ready_count", 0) or 0),
                "candidate_field_count": len(candidate_fields),
                "candidate_fields": list(candidate_fields),
                "baseline_idea_count": len(baseline_ideas),
                "baseline_ideas": list(baseline_ideas),
                "next_action_code_count": len(next_action_codes),
                "next_action_codes": list(next_action_codes),
                "priority_reasons": list(priority_reasons),
            }
        )

    family_records.sort(
        key=lambda item: (
            1 if item.get("hard_excluded") else 0,
            0 if str(item.get("state") or "") in allowed_states else 1,
            -_float_value(item.get("priority_score"), default=-9999.0),
            _state_rank(str(item.get("state") or "")),
            str(item.get("family_key") or ""),
        )
    )

    shortlist = [
        item
        for item in family_records
        if not item.get("hard_excluded") and str(item.get("state") or "") in allowed_states
    ][:shortlist_limit]
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "run_id": run_id,
        "objective": "prioritize materially different seed families before daily local mining",
        "settings": {
            "allowed_states": list(allowed_states),
            "shortlist_limit": shortlist_limit,
            "hard_exclude_topic_patterns": [
                pattern
                for pattern in success_policy.get("hard_exclude_topic_patterns", [])
                if isinstance(pattern, str)
            ],
        },
        "priority_family_keys": [item["family_key"] for item in shortlist],
        "shortlist": shortlist,
        "all_families": family_records,
        "counts": {
            "family_registry_count": len(success_state.get("family_registry_summary", [])),
            "field_pack_count": len(field_packs),
            "family_count": len(family_records),
            "shortlist_count": len(shortlist),
        },
    }


def render_manifest_md(manifest: dict[str, Any]) -> str:
    lines = [
        "# Alpha Seed Family Expander",
        "",
        f"- Run id: {manifest['run_id']}",
        f"- Objective: {manifest['objective']}",
        f"- Shortlist count: {manifest.get('counts', {}).get('shortlist_count', 0)}",
        f"- Family count: {manifest.get('counts', {}).get('family_count', 0)}",
        "",
        "## Priority Family Keys",
        "",
    ]
    priority_keys = manifest.get("priority_family_keys", [])
    if not priority_keys:
        lines.append("- No family survived the current seed-family filters.")
    else:
        for family_key in priority_keys:
            lines.append(f"- {family_key}")

    lines.extend(["", "## Shortlist", ""])
    shortlist = manifest.get("shortlist", [])
    if not shortlist:
        lines.append("- Shortlist is empty.")
    else:
        for item in shortlist:
            lines.append(
                f"- {item['family_key']} [{item['state']}] score={item['priority_score']} "
                f"fields={item['candidate_field_count']} baselines={item['baseline_idea_count']}"
            )
            for reason in item.get("priority_reasons", [])[:4]:
                lines.append(f"  - {reason}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    run_id = default_run_id(args)
    allowed_states = _allowed_states(args)

    family_dir = _normalize_path(args.family_dir)
    field_pack_dir = _normalize_path(args.field_search_pack_dir)
    if family_dir is None or not family_dir.exists():
        raise SystemExit(f"Family dir not found: {args.family_dir}")
    if field_pack_dir is None or not field_pack_dir.exists():
        raise SystemExit(f"Field-search-pack dir not found: {args.field_search_pack_dir}")

    capture_dir = _default_optional_input(
        args.capture_dir,
        Path("runs/simulation-captures"),
        family_dir=family_dir,
    )
    candidate_batch_dir = _default_optional_input(
        args.candidate_batch_dir,
        Path("runs/candidate-batches"),
        family_dir=family_dir,
    )
    candidate_check_dir = _default_optional_input(
        args.candidate_check_dir,
        Path("harness/artifacts"),
        family_dir=family_dir,
    )

    success_state = build_success_rate_state(
        family_dir=family_dir,
        capture_dir=capture_dir if capture_dir is not None and capture_dir.exists() else [],
        candidate_batch_dir=(candidate_batch_dir if candidate_batch_dir is not None and candidate_batch_dir.exists() else None),
        candidate_check_dir=(candidate_check_dir if candidate_check_dir is not None and candidate_check_dir.exists() else None),
    )
    success_policy = load_success_policy(args.success_policy)
    field_packs = load_field_search_packs(field_pack_dir)
    manifest = build_priority_manifest(
        run_id=run_id,
        success_state=success_state,
        field_packs=field_packs,
        success_policy=success_policy,
        allowed_states=allowed_states,
        shortlist_limit=args.shortlist_limit,
    )
    manifest_text = render_manifest_md(manifest)

    artifact_root = _normalize_path(args.artifact_root)
    publish_root = _normalize_path(args.publish_root)
    if artifact_root is None or publish_root is None:
        raise SystemExit("Invalid output root.")
    output_root = artifact_root / run_id
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "manifest.json"
    manifest_md_path = output_root / "manifest.md"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_md_path.write_text(manifest_text, encoding="utf-8")

    publish_root.mkdir(parents=True, exist_ok=True)
    published_json = publish_root / f"{run_id}.json"
    published_md = publish_root / f"{run_id}.md"
    published_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    published_md.write_text(manifest_text, encoding="utf-8")

    print(f"Seed-family bundle: {output_root}")
    print(f"Seed-family manifest: {published_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

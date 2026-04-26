#!/usr/bin/env python3
"""Shared field-readiness parsing and gating helpers for local alpha research."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from alpha_success_core import normalize_family_key


SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
METADATA_RE = re.compile(r"^\s*-\s+([^:]+):\s*(.*)$")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
INVALID_FIELD_RE = re.compile(r'invalid data field[^A-Za-z0-9_`"\']*[`"\']?([A-Za-z_][A-Za-z0-9_]*)', re.IGNORECASE)
UNKNOWN_VARIABLE_RE = re.compile(r'unknown variable[^A-Za-z0-9_`"\']*[`"\']?([A-Za-z_][A-Za-z0-9_]*)', re.IGNORECASE)
MISSING_VARIABLE_RE = re.compile(r'variable[^A-Za-z0-9_`"\']*[`"\']?([A-Za-z_][A-Za-z0-9_]*)[`"\']?\s+not found', re.IGNORECASE)

DEFAULT_COVERAGE_FLOOR_PCT = 70.0


@dataclass(frozen=True)
class CandidateFieldRow:
    name: str
    dataset: str
    why_it_might_fit: str
    coverage_notes: str
    crowding_notes: str


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
    candidate_rows: tuple[CandidateFieldRow, ...]
    candidate_fields: tuple[str, ...]
    quality_checks: dict[str, str]
    raw_text: str


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


def _extract_candidate_rows(section_text: str) -> tuple[CandidateFieldRow, ...]:
    rows: list[CandidateFieldRow] = []
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
        if not field_name:
            continue
        dataset = cells[1] if len(cells) > 1 else ""
        why = cells[2] if len(cells) > 2 else ""
        coverage_notes = cells[3] if len(cells) > 3 else ""
        crowding_notes = cells[4] if len(cells) > 4 else ""
        rows.append(
            CandidateFieldRow(
                name=field_name,
                dataset=dataset,
                why_it_might_fit=why,
                coverage_notes=coverage_notes,
                crowding_notes=crowding_notes,
            )
        )
    return tuple(rows)


def parse_field_search_pack(path: Path) -> FieldSearchPackDoc:
    raw_text = path.read_text(encoding="utf-8")
    sections = _split_sections(raw_text)
    metadata = _parse_metadata(sections.get("Metadata", ""))
    title_match = TITLE_RE.search(raw_text)
    title = title_match.group(1).strip() if title_match else path.stem
    topic = metadata.get("topic") or normalize_family_key(path.stem)
    family_key = normalize_family_key(topic)
    candidate_rows = _extract_candidate_rows(sections.get("Candidate Fields", ""))
    candidate_fields = tuple(dict.fromkeys(row.name for row in candidate_rows))
    return FieldSearchPackDoc(
        path=path,
        title=title,
        topic=topic,
        family_key=family_key,
        metadata=metadata,
        hypothesis=sections.get("Hypothesis", "").strip(),
        why_lines=_extract_bullets(sections.get("Why This Could Matter", "")),
        baseline_ideas=_extract_numbered_inline_codes(sections.get("Baseline Expression Ideas", "")),
        next_action_codes=tuple(
            dict.fromkeys(code.strip() for code in INLINE_CODE_RE.findall(sections.get("Next Action", "")) if code.strip())
        ),
        candidate_rows=candidate_rows,
        candidate_fields=candidate_fields,
        quality_checks=_parse_metadata(sections.get("Coverage And Quality Checks", "")),
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


def _coverage_percent(value: str) -> float | None:
    match = PERCENT_RE.search(value or "")
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _field_referenced(expressions: Iterable[str], field_name: str) -> bool:
    pattern = re.compile(rf"\b{re.escape(field_name)}\b")
    return any(pattern.search(expression or "") for expression in expressions)


def _family_texts_by_key(family_docs: Sequence[Any]) -> dict[str, list[str]]:
    texts: dict[str, list[str]] = {}
    for doc in family_docs:
        family_key = normalize_family_key(str(getattr(doc, "topic", "") or getattr(doc, "path", "")))
        texts.setdefault(family_key, []).append(str(getattr(doc, "raw_text", "") or ""))
    return texts


def _family_paths_by_key(family_docs: Sequence[Any]) -> dict[str, list[str]]:
    paths: dict[str, list[str]] = {}
    for doc in family_docs:
        family_key = normalize_family_key(str(getattr(doc, "topic", "") or getattr(doc, "path", "")))
        raw_path = getattr(doc, "path", None)
        if raw_path is None:
            continue
        path_text = str(raw_path)
        if path_text not in paths.setdefault(family_key, []):
            paths[family_key].append(path_text)
    return paths


def _collect_blocked_field_reasons(
    candidate_fields: Sequence[str],
    raw_texts: Sequence[str],
) -> dict[str, list[str]]:
    blocked: dict[str, list[str]] = {field: [] for field in candidate_fields}
    patterns = (
        (INVALID_FIELD_RE, "invalid_data_field"),
        (UNKNOWN_VARIABLE_RE, "unknown_variable"),
        (MISSING_VARIABLE_RE, "missing_variable"),
    )
    for raw_text in raw_texts:
        for pattern, reason_code in patterns:
            for match in pattern.findall(raw_text or ""):
                field_name = match.strip()
                if field_name in blocked and reason_code not in blocked[field_name]:
                    blocked[field_name].append(reason_code)
    return {field: reasons for field, reasons in blocked.items() if reasons}


def build_field_readiness_report(
    *,
    field_packs: Sequence[FieldSearchPackDoc],
    family_docs: Sequence[Any],
    coverage_floor_pct: float = DEFAULT_COVERAGE_FLOOR_PCT,
) -> dict[str, Any]:
    family_texts = _family_texts_by_key(family_docs)
    family_paths = _family_paths_by_key(family_docs)
    packs_by_family: dict[str, list[FieldSearchPackDoc]] = {}
    for pack in field_packs:
        packs_by_family.setdefault(pack.family_key, []).append(pack)

    all_family_keys = sorted(set(family_texts) | set(packs_by_family))
    items: list[dict[str, Any]] = []
    for family_key in all_family_keys:
        packs = packs_by_family.get(family_key, [])
        candidate_rows = [row for pack in packs for row in pack.candidate_rows]
        candidate_fields = list(dict.fromkeys(row.name for row in candidate_rows))
        raw_texts = [*(pack.raw_text for pack in packs), *family_texts.get(family_key, [])]
        blocked_reasons = _collect_blocked_field_reasons(candidate_fields, raw_texts)
        usable_candidate_fields = [field for field in candidate_fields if field not in blocked_reasons]
        blocked_reference_fields = sorted(
            field
            for field in blocked_reasons
            if any(
                _field_referenced(
                    [*(pack.baseline_ideas), *(pack.next_action_codes)],
                    field,
                )
                for pack in packs
            )
        )

        coverage_by_field: dict[str, float | None] = {}
        for row in candidate_rows:
            coverage_by_field.setdefault(row.name, _coverage_percent(row.coverage_notes))

        usable_coverages = [
            value
            for field, value in coverage_by_field.items()
            if field in usable_candidate_fields and isinstance(value, (int, float))
        ]
        coverage_floor = min(usable_coverages) if usable_coverages else None

        quality_checks: dict[str, str] = {}
        for pack in packs:
            for key, value in pack.quality_checks.items():
                quality_checks.setdefault(key, value)

        reasons: list[str] = []
        if not packs:
            reasons.append("no field-search pack is linked to this family")
        if not candidate_fields:
            reasons.append("no candidate fields were found in the linked field-search packs")
        if blocked_reference_fields:
            reasons.append(
                "baseline ideas or next actions still reference blocked fields: "
                + ", ".join(blocked_reference_fields)
            )
        if candidate_fields and not usable_candidate_fields:
            reasons.append("all candidate fields are blocked by account-usage evidence")
        if usable_candidate_fields and not usable_coverages:
            reasons.append("usable candidate fields do not have parseable coverage percentages")
        if coverage_floor is not None and coverage_floor < coverage_floor_pct:
            reasons.append(
                f"usable candidate-field coverage floor {coverage_floor:.1f}% is below the required {coverage_floor_pct:.1f}%"
            )

        if not candidate_fields or (candidate_fields and not usable_candidate_fields):
            gate_status = "block"
        elif blocked_reference_fields or not usable_coverages or (
            coverage_floor is not None and coverage_floor < coverage_floor_pct
        ):
            gate_status = "hold"
        else:
            gate_status = "pass"

        account_usable_status = "blocked"
        if usable_candidate_fields and blocked_reasons:
            account_usable_status = "partially_blocked"
        elif usable_candidate_fields:
            account_usable_status = "usable"

        if not usable_candidate_fields:
            coverage_status = "not_applicable"
        elif not usable_coverages:
            coverage_status = "unknown"
        elif coverage_floor is not None and coverage_floor < coverage_floor_pct:
            coverage_status = "below_floor"
        else:
            coverage_status = "pass"

        missingness_value = quality_checks.get("missingness", "")
        region_delay_value = quality_checks.get("region_delay_compatibility", "")
        nan_strategy_status = "reviewed" if missingness_value else "unknown"
        missingness_risk = "documented" if missingness_value else "unknown"
        update_frequency_status = "documented" if region_delay_value else "unknown"

        items.append(
            {
                "family_key": family_key,
                "source_field_pack_paths": [str(pack.path) for pack in packs],
                "family_doc_paths": family_paths.get(family_key, []),
                "candidate_fields": candidate_fields,
                "usable_candidate_fields": usable_candidate_fields,
                "blocked_candidate_fields": [
                    {"field": field, "reasons": reasons_for_field}
                    for field, reasons_for_field in sorted(blocked_reasons.items())
                ],
                "coverage_by_field": coverage_by_field,
                "quality_checks": quality_checks,
                "assessment": {
                    "gate_status": gate_status,
                    "account_usable_status": account_usable_status,
                    "coverage_status": coverage_status,
                    "missingness_risk": missingness_risk,
                    "update_frequency_status": update_frequency_status,
                    "nan_strategy_status": nan_strategy_status,
                    "coverage_floor_pct": coverage_floor,
                    "reasons": reasons or ["field-readiness gate passed"],
                },
            }
        )

    counts = {
        "family_count": len(items),
        "pass_count": sum(1 for item in items if item["assessment"]["gate_status"] == "pass"),
        "hold_count": sum(1 for item in items if item["assessment"]["gate_status"] == "hold"),
        "block_count": sum(1 for item in items if item["assessment"]["gate_status"] == "block"),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "objective": "gate local mining on field readiness before family expansion or queue promotion",
        "coverage_floor_pct": coverage_floor_pct,
        "counts": counts,
        "items": items,
    }


def index_field_readiness(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family_key") or ""): item
        for item in report.get("items", [])
        if str(item.get("family_key") or "")
    }


def render_field_readiness_md(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Field Readiness Gate",
        "",
        f"- Objective: {report.get('objective', 'field readiness gate')}",
        f"- Coverage floor: {float(report.get('coverage_floor_pct', DEFAULT_COVERAGE_FLOOR_PCT)):.1f}%",
        f"- Families: {counts.get('family_count', 0)}",
        f"- Pass: {counts.get('pass_count', 0)}",
        f"- Hold: {counts.get('hold_count', 0)}",
        f"- Block: {counts.get('block_count', 0)}",
        "",
        "| family | gate | usable fields | blocked fields | coverage floor | reasons |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        blocked_fields = ", ".join(entry["field"] for entry in item.get("blocked_candidate_fields", [])) or "-"
        coverage_floor = assessment.get("coverage_floor_pct")
        lines.append(
            "| {family_key} | {gate_status} | {usable_count} | {blocked_fields} | {coverage_floor} | {reasons} |".format(
                family_key=item.get("family_key"),
                gate_status=assessment.get("gate_status"),
                usable_count=len(item.get("usable_candidate_fields", [])),
                blocked_fields=blocked_fields,
                coverage_floor=(
                    f"{float(coverage_floor):.1f}%"
                    if isinstance(coverage_floor, (int, float))
                    else "-"
                ),
                reasons="; ".join(assessment.get("reasons", [])[:2]),
            )
        )
    lines.append("")
    lines.append("## Reasons")
    lines.append("")
    for item in report.get("items", []):
        assessment = item.get("assessment", {})
        lines.append(f"- `{item.get('family_key')}` -> `{assessment.get('gate_status')}`")
        for reason in assessment.get("reasons", []):
            lines.append(f"  - {reason}")
    lines.append("")
    return "\n".join(lines)

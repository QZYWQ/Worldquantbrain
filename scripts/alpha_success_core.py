#!/usr/bin/env python3
"""Success-rate state helpers for WorldQuant alpha mining.

This module is intentionally stdlib-only and read-only with respect to the
project tree. It parses existing family markdown docs, simulation capture JSON
files, and durable candidate-evidence artifacts into conservative state
surfaces:

- family registry summary
- official outcome memory
- submit-ready ledger

The helpers do not fabricate metrics or implied submission readiness. An alpha
is only marked submit-ready when the capture exposes the full known submission
gate set, none of those gates fail, and SELF_CORRELATION is resolved
non-failing.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


KNOWN_SUBMISSION_GATES = (
    "LOW_SHARPE",
    "LOW_FITNESS",
    "LOW_TURNOVER",
    "HIGH_TURNOVER",
    "CONCENTRATED_WEIGHT",
    "LOW_SUB_UNIVERSE_SHARPE",
    "SELF_CORRELATION",
    "MATCHES_COMPETITION",
)
SELF_CORRELATION_GATE = "SELF_CORRELATION"
NON_FAIL_RESULTS = {"PASS"}
FAIL_RESULTS = {"FAIL"}
PENDING_RESULTS = {"PENDING", "QUEUED", "RUNNING"}
FAMILY_STATES = ("explore", "branch", "hold", "kill", "exploit")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_GATE_ALIASES = {
    "concentrated_weight": "CONCENTRATED_WEIGHT",
    "max_weight_check": "CONCENTRATED_WEIGHT",
    "self_correlation": "SELF_CORRELATION",
    "self_corr_check": "SELF_CORRELATION",
    "low_fitness": "LOW_FITNESS",
    "low_sub_universe_sharpe": "LOW_SUB_UNIVERSE_SHARPE",
}
CANDIDATE_METRIC_FIELDS = (
    "sharpe",
    "fitness",
    "turnover",
    "returns",
    "drawdown",
    "margin",
    "max_weight",
    "self_corr",
    "is_sharpe",
    "is_fitness",
)
STRONG_CANDIDATE_REQUIRED_GATES = (
    "CONCENTRATED_WEIGHT",
    "SELF_CORRELATION",
    "LOW_FITNESS",
    "LOW_SUB_UNIVERSE_SHARPE",
)
CANDIDATE_TEST_FIELDS = (
    "subuniverse_pass",
    "test_period_pass",
    "check_submission_pass",
)
MERGE_SOURCE_PRIORITY = {
    "candidate-batch": 1,
    "candidate-check-status": 2,
    "network-api": 3,
}

SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
METADATA_RE = re.compile(r"^\s*-\s+([^:]+):\s*(.*)$")
CODE_BLOCK_RE = re.compile(r"```(?:[A-Za-z0-9_-]+)?\n(.*?)```", re.DOTALL)
DATE_PREFIX_RE = re.compile(r"^\d{4}[_-]\d{2}[_-]\d{2}[_-]?")
TRAILING_BATCH_RE = re.compile(r"_batch_\d+$")
TRAILING_API_SUFFIX_RE = re.compile(r"_api_checks$")
TRAILING_BASELINE_SUFFIXES = (
    "_structural_follow_up",
    "_follow_up",
    "_baselines",
    "_baseline",
)


@dataclass(frozen=True)
class GateCheck:
    name: str
    result: str
    limit: Any | None
    value: Any | None


@dataclass(frozen=True)
class ExpressionFamilyDoc:
    path: Path
    title: str
    topic: str
    family_key: str
    metadata: dict[str, str]
    baseline_expression: str | None
    expressions: tuple[str, ...]
    decision_lines: tuple[str, ...]
    explicit_state_hints: tuple[str, ...]
    raw_text: str


@dataclass(frozen=True)
class OfficialAlphaOutcome:
    family_key: str
    family_topic: str
    family_doc_path: str | None
    capture_path: str
    capture_id: str
    capture_topic: str
    capture_mode: str | None
    alpha_name: str | None
    alpha_id: str | None
    simulation_id: str | None
    expression: str
    classification: str | None
    status: str | None
    metrics: dict[str, Any]
    tests: dict[str, Any]
    gate_results: dict[str, str | None]
    passing_gates: tuple[str, ...]
    failing_gates: tuple[str, ...]
    pending_gates: tuple[str, ...]
    missing_gates: tuple[str, ...]
    evidence_level: str
    has_full_gate_coverage: bool
    submit_ready: bool
    notes: tuple[str, ...]


def _unique(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = DATE_PREFIX_RE.sub("", lowered)
    lowered = lowered.replace("-", "_")
    lowered = re.sub(r"[^a-z0-9_]+", "_", lowered)
    lowered = re.sub(r"_+", "_", lowered).strip("_")
    return lowered


def normalize_family_key(value: str) -> str:
    normalized = _slugify(value)
    normalized = TRAILING_API_SUFFIX_RE.sub("", normalized)
    normalized = TRAILING_BATCH_RE.sub("", normalized)
    changed = True
    while changed:
        changed = False
        for suffix in TRAILING_BASELINE_SUFFIXES:
            if normalized.endswith(suffix):
                normalized = normalized[: -len(suffix)]
                changed = True
    return normalized or "unknown_family"


KNOWN_SUBMISSION_GATE_LOOKUP = {
    _slugify(gate): gate for gate in KNOWN_SUBMISSION_GATES
}


def _normalize_submission_gate_name(value: Any) -> str | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    upper = raw.upper()
    if upper in KNOWN_SUBMISSION_GATES:
        return upper
    slug = _slugify(raw)
    if slug in CANDIDATE_GATE_ALIASES:
        return CANDIDATE_GATE_ALIASES[slug]
    return KNOWN_SUBMISSION_GATE_LOOKUP.get(slug)


def _first_title(text: str, fallback: str) -> str:
    match = TITLE_RE.search(text)
    if match:
        return match.group(1).strip()
    return fallback


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
        key = _slugify(match.group(1))
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
    if bullets:
        return tuple(bullets)
    lines = [line.strip() for line in section_text.splitlines() if line.strip()]
    return tuple(lines)


def _looks_like_expression(block: str) -> bool:
    stripped = block.strip()
    if not stripped:
        return False
    if len(stripped.splitlines()) > 6:
        return False
    if any(marker in stripped for marker in ('"', "{", "}", ":")):
        return False
    return "(" in stripped and ")" in stripped


def _extract_code_blocks(text: str) -> tuple[str, ...]:
    blocks: list[str] = []
    for block in CODE_BLOCK_RE.findall(text):
        cleaned = block.strip()
        if cleaned and _looks_like_expression(cleaned):
            blocks.append(cleaned)
    return tuple(blocks)


def _infer_doc_state_hints(decision_lines: Sequence[str]) -> tuple[str, ...]:
    hints: list[str] = []
    for line in decision_lines:
        lowered = line.strip().lower()
        if lowered.startswith("branch:") or "family in `branch`" in lowered or "family in branch" in lowered:
            hints.append("branch")
        if lowered.startswith("hold:") or "family in `hold`" in lowered or "family in hold" in lowered:
            hints.append("hold")
        if lowered.startswith("kill:") or lowered.startswith("kill ") or "kill the" in lowered:
            hints.append("kill")
        if lowered.startswith("exploit:") or "family in `exploit`" in lowered or "family in exploit" in lowered:
            hints.append("exploit")
        if lowered.startswith("explore:") or "family in `explore`" in lowered or "family in explore" in lowered:
            hints.append("explore")
    ordered = [state for state in FAMILY_STATES if state in hints]
    return tuple(ordered)


def parse_expression_family_doc(path: Path | str) -> ExpressionFamilyDoc:
    doc_path = Path(path)
    raw_text = doc_path.read_text(encoding="utf-8")
    sections = _split_sections(raw_text)
    metadata = _parse_metadata(sections.get("Metadata", ""))
    title = _first_title(raw_text, doc_path.stem)
    topic = metadata.get("topic") or normalize_family_key(doc_path.stem)
    family_key = normalize_family_key(topic)
    decision_lines = _extract_bullets(sections.get("Decision", ""))
    expressions = _extract_code_blocks(raw_text)
    baseline_blocks = _extract_code_blocks(sections.get("Baseline Expression", ""))
    baseline_expression = baseline_blocks[0] if baseline_blocks else (expressions[0] if expressions else None)
    return ExpressionFamilyDoc(
        path=doc_path,
        title=title,
        topic=topic,
        family_key=family_key,
        metadata=metadata,
        baseline_expression=baseline_expression,
        expressions=expressions,
        decision_lines=decision_lines,
        explicit_state_hints=_infer_doc_state_hints(decision_lines),
        raw_text=raw_text,
    )


def _iter_paths(
    source: Path | str | Iterable[Path | str],
    suffix: str,
    *,
    recursive: bool = False,
) -> Iterator[Path]:
    if isinstance(source, (str, Path)):
        source_path = Path(source)
        if source_path.is_dir():
            iterator = source_path.rglob(f"*{suffix}") if recursive else source_path.glob(f"*{suffix}")
            yield from sorted(path for path in iterator if path.is_file())
        else:
            yield source_path
        return
    for item in source:
        yield Path(item)


def load_expression_family_docs(source: Path | str | Iterable[Path | str]) -> list[ExpressionFamilyDoc]:
    docs: list[ExpressionFamilyDoc] = []
    for path in _iter_paths(source, ".md"):
        if path.name.lower() == "readme.md":
            continue
        docs.append(parse_expression_family_doc(path))
    return docs


def load_success_policy(path: Path | str = Path("harness/alpha-success-policy.json")) -> dict[str, Any]:
    policy_path = Path(path)
    if not policy_path.exists():
        return {}
    data = json.loads(policy_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    return {}


def _coerce_gate_result(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        upper = value.strip().upper()
        return upper or None
    return str(value).strip().upper() or None


def _parse_checks(raw_checks: Any) -> dict[str, GateCheck]:
    checks: dict[str, GateCheck] = {}
    if not isinstance(raw_checks, list):
        return checks
    for item in raw_checks:
        if not isinstance(item, dict):
            continue
        name = _normalize_submission_gate_name(item.get("name"))
        if not name:
            continue
        checks[name] = GateCheck(
            name=name,
            result=_coerce_gate_result(item.get("result")) or "UNKNOWN",
            limit=item.get("limit"),
            value=item.get("value"),
        )
    return checks


def _coerce_tests(raw_tests: Any) -> dict[str, Any]:
    if isinstance(raw_tests, dict):
        return dict(raw_tests)
    return {}


def _coerce_metrics(raw_metrics: Any) -> dict[str, Any]:
    if isinstance(raw_metrics, dict):
        return dict(raw_metrics)
    return {}


def _resolve_reference_path(raw_ref: Any, base_path: Path) -> Path | None:
    if not isinstance(raw_ref, str) or not raw_ref.strip():
        return None
    ref_path = Path(raw_ref.strip())
    if ref_path.is_absolute():
        return ref_path
    if ref_path.parts and ref_path.parts[0] == ".":
        return PROJECT_ROOT.joinpath(*ref_path.parts[1:])
    return (base_path.parent / ref_path).resolve(strict=False)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    if isinstance(data, dict):
        return data
    return None


def _candidate_family_reference(
    data: dict[str, Any],
    source_path: Path,
) -> tuple[str | None, str, str]:
    topic = str(data.get("topic") or source_path.stem)
    source_capture_path = _resolve_reference_path(data.get("source_capture"), source_path)
    if source_capture_path and source_capture_path.is_file():
        capture_data = _load_json_dict(source_capture_path)
        if capture_data is not None:
            family_doc_path, family_key = _family_reference_from_capture(capture_data, source_capture_path)
            capture_topic = str(capture_data.get("topic") or topic)
            family_topic = _family_topic_from_doc_ref(family_doc_path, capture_topic)
            return family_doc_path, family_key, family_topic
    family_key = normalize_family_key(topic)
    return None, family_key, family_key


def _iter_candidate_payloads(data: dict[str, Any]) -> Iterator[dict[str, Any]]:
    for key in ("candidates", "alphas"):
        raw_items = data.get(key)
        if not isinstance(raw_items, list):
            continue
        for item in raw_items:
            if isinstance(item, dict):
                yield item


def _candidate_metrics(candidate_payload: dict[str, Any]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for key in CANDIDATE_METRIC_FIELDS:
        if key in candidate_payload:
            metrics[key] = candidate_payload.get(key)
    return metrics


def _candidate_tests(candidate_payload: dict[str, Any]) -> dict[str, Any]:
    tests: dict[str, Any] = {}
    for key in CANDIDATE_TEST_FIELDS:
        if key in candidate_payload:
            tests[key] = candidate_payload.get(key)
    return tests


def _candidate_notes(
    candidate_payload: dict[str, Any],
    parent_notes: Sequence[str],
    blocking_reason: str | None = None,
) -> tuple[str, ...]:
    notes: list[str] = [item for item in parent_notes if item]
    if blocking_reason:
        notes.append(blocking_reason)
    raw_notes = candidate_payload.get("notes")
    if isinstance(raw_notes, str) and raw_notes.strip():
        notes.append(raw_notes.strip())
    observation = candidate_payload.get("test_period_observation")
    if isinstance(observation, str) and observation.strip():
        notes.append(observation.strip())
    return _unique(notes)


def _parse_candidate_checks(candidate_payload: dict[str, Any]) -> dict[str, GateCheck]:
    checks: dict[str, GateCheck] = {}
    raw_checks = candidate_payload.get("checks")
    if isinstance(raw_checks, dict):
        for raw_name, raw_result in raw_checks.items():
            name = _normalize_submission_gate_name(raw_name)
            if not name:
                continue
            checks[name] = GateCheck(
                name=name,
                result=_coerce_gate_result(raw_result) or "UNKNOWN",
                limit=None,
                value=None,
            )
    elif isinstance(raw_checks, list):
        checks.update(_parse_checks(raw_checks))

    for raw_name, raw_value in candidate_payload.items():
        name = _normalize_submission_gate_name(raw_name)
        if not name or raw_value is None:
            continue
        checks[name] = GateCheck(
            name=name,
            result=_coerce_gate_result(raw_value) or "UNKNOWN",
            limit=None,
            value=None,
        )
    return checks


def _extract_notes(alpha_payload: dict[str, Any], capture_evidence: dict[str, Any]) -> tuple[str, ...]:
    notes: list[str] = []
    alpha_notes = alpha_payload.get("notes")
    if isinstance(alpha_notes, str) and alpha_notes.strip():
        notes.append(alpha_notes.strip())
    evidence_notes = capture_evidence.get("notes")
    if isinstance(evidence_notes, list):
        for item in evidence_notes:
            if isinstance(item, str) and item.strip():
                notes.append(item.strip())
    return _unique(notes)


def _family_reference_from_capture(data: dict[str, Any], capture_path: Path) -> tuple[str | None, str]:
    evidence = data.get("evidence")
    if isinstance(evidence, dict):
        family_ref = evidence.get("expression_family")
        if isinstance(family_ref, str) and family_ref.strip():
            family_path = Path(family_ref)
            family_key = normalize_family_key(family_path.stem)
            return family_ref, family_key
    topic = str(data.get("topic") or capture_path.stem)
    return None, normalize_family_key(topic)


def _family_topic_from_doc_ref(family_doc_path: str | None, capture_topic: str) -> str:
    if family_doc_path:
        return normalize_family_key(Path(family_doc_path).stem)
    return normalize_family_key(capture_topic)


def _evidence_level_for_alpha(checks: dict[str, GateCheck], tests: dict[str, Any]) -> str:
    if checks:
        if all(gate in checks for gate in KNOWN_SUBMISSION_GATES):
            return "full_submission_gates"
        return "partial_gate_checks"
    if tests:
        return "partial_tests"
    return "metrics_only"


def _gate_result_map(checks: dict[str, GateCheck]) -> dict[str, str | None]:
    results = {gate: None for gate in KNOWN_SUBMISSION_GATES}
    for gate, check in checks.items():
        if gate in results:
            results[gate] = check.result
    return results


def _has_strong_candidate_evidence(
    gate_results: dict[str, str | None],
    tests: dict[str, Any],
) -> bool:
    if tests.get("subuniverse_pass") is not True:
        return False

    for gate in STRONG_CANDIDATE_REQUIRED_GATES:
        result = gate_results.get(gate)
        if result is None or result in FAIL_RESULTS or result in PENDING_RESULTS:
            return False

    low_sharpe = gate_results.get("LOW_SHARPE")
    if low_sharpe in FAIL_RESULTS:
        return False

    low_turnover = gate_results.get("LOW_TURNOVER")
    if low_turnover in FAIL_RESULTS:
        return False

    high_turnover = gate_results.get("HIGH_TURNOVER")
    if high_turnover in FAIL_RESULTS:
        return False

    return True


def _is_submit_ready_from_gate_results(gate_results: dict[str, str | None]) -> bool:
    if any(gate_results.get(gate) is None for gate in KNOWN_SUBMISSION_GATES):
        return False
    if any(gate_results.get(gate) in FAIL_RESULTS for gate in KNOWN_SUBMISSION_GATES):
        return False
    self_corr = gate_results.get(SELF_CORRELATION_GATE)
    if self_corr is None or self_corr in PENDING_RESULTS:
        return False
    return self_corr in NON_FAIL_RESULTS


def parse_simulation_capture(path: Path | str) -> list[OfficialAlphaOutcome]:
    capture_path = Path(path)
    data = json.loads(capture_path.read_text(encoding="utf-8"))
    capture_id = str(data.get("capture_id") or capture_path.stem)
    capture_topic = str(data.get("topic") or capture_path.stem)
    capture_mode = data.get("capture_mode")
    family_doc_path, family_key = _family_reference_from_capture(data, capture_path)
    family_topic = _family_topic_from_doc_ref(family_doc_path, capture_topic)
    evidence = data.get("evidence")
    evidence_dict = evidence if isinstance(evidence, dict) else {}

    outcomes: list[OfficialAlphaOutcome] = []
    for alpha in data.get("alphas", []):
        if not isinstance(alpha, dict):
            continue
        checks = _parse_checks(alpha.get("checks"))
        tests = _coerce_tests(alpha.get("tests"))
        metrics = _coerce_metrics(alpha.get("metrics"))
        gate_results = _gate_result_map(checks)
        passing_gates = tuple(gate for gate, result in gate_results.items() if result in NON_FAIL_RESULTS)
        failing_gates = tuple(gate for gate, result in gate_results.items() if result in FAIL_RESULTS)
        pending_gates = tuple(gate for gate, result in gate_results.items() if result in PENDING_RESULTS)
        missing_gates = tuple(gate for gate, result in gate_results.items() if result is None)
        evidence_level = _evidence_level_for_alpha(checks, tests)
        has_full_gate_coverage = evidence_level == "full_submission_gates"
        submit_ready = has_full_gate_coverage and _is_submit_ready_from_gate_results(gate_results)

        simulation_id = alpha.get("simulation_id")
        if simulation_id is None and isinstance(evidence_dict, dict):
            simulation_id = evidence_dict.get("simulation_id")
        alpha_id = alpha.get("alpha_id")
        if alpha_id is None and isinstance(evidence_dict, dict):
            alpha_id = evidence_dict.get("alpha_id")

        outcomes.append(
            OfficialAlphaOutcome(
                family_key=family_key,
                family_topic=family_topic,
                family_doc_path=family_doc_path,
                capture_path=capture_path.as_posix(),
                capture_id=capture_id,
                capture_topic=capture_topic,
                capture_mode=str(capture_mode) if capture_mode is not None else None,
                alpha_name=str(alpha.get("name")) if alpha.get("name") is not None else None,
                alpha_id=str(alpha_id) if alpha_id is not None else None,
                simulation_id=str(simulation_id) if simulation_id is not None else None,
                expression=str(alpha.get("expression") or ""),
                classification=str(alpha.get("classification")) if alpha.get("classification") is not None else None,
                status=str(alpha.get("status")) if alpha.get("status") is not None else None,
                metrics=metrics,
                tests=tests,
                gate_results=gate_results,
                passing_gates=passing_gates,
                failing_gates=failing_gates,
                pending_gates=pending_gates,
                missing_gates=missing_gates,
                evidence_level=evidence_level,
                has_full_gate_coverage=has_full_gate_coverage,
                submit_ready=submit_ready,
                notes=_extract_notes(alpha, evidence_dict),
            )
        )
    return outcomes


def load_simulation_captures(source: Path | str | Iterable[Path | str]) -> list[OfficialAlphaOutcome]:
    outcomes: list[OfficialAlphaOutcome] = []
    for path in _iter_paths(source, ".json"):
        outcomes.extend(parse_simulation_capture(path))
    return outcomes


def parse_candidate_check_artifact(path: Path | str) -> list[OfficialAlphaOutcome]:
    artifact_path = Path(path)
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    capture_id = str(data.get("capture_id") or artifact_path.stem)
    capture_topic = str(data.get("topic") or artifact_path.stem)
    family_doc_path, family_key, family_topic = _candidate_family_reference(data, artifact_path)
    batch_status = data.get("batch_status")
    blocking_reason = str(data.get("blocking_reason")).strip() if data.get("blocking_reason") else None
    parent_notes = _extract_notes({}, data)

    outcomes: list[OfficialAlphaOutcome] = []
    for candidate in _iter_candidate_payloads(data):
        metrics = _candidate_metrics(candidate)
        checks = _parse_candidate_checks(candidate)
        tests = _candidate_tests(candidate)
        gate_results = _gate_result_map(checks)
        passing_gates = tuple(gate for gate, result in gate_results.items() if result in NON_FAIL_RESULTS)
        failing_gates = tuple(gate for gate, result in gate_results.items() if result in FAIL_RESULTS)
        pending_gates = tuple(gate for gate, result in gate_results.items() if result in PENDING_RESULTS)
        missing_gates = tuple(gate for gate, result in gate_results.items() if result is None)
        evidence_level = _evidence_level_for_alpha(checks, tests)
        has_full_gate_coverage = evidence_level == "full_submission_gates"
        submit_ready = has_full_gate_coverage and _is_submit_ready_from_gate_results(gate_results)

        name = candidate.get("candidate_name")
        if name is None:
            name = candidate.get("name")

        outcomes.append(
            OfficialAlphaOutcome(
                family_key=family_key,
                family_topic=family_topic,
                family_doc_path=family_doc_path,
                capture_path=artifact_path.as_posix(),
                capture_id=capture_id,
                capture_topic=capture_topic,
                capture_mode="candidate-check-status",
                alpha_name=str(name) if name is not None else None,
                alpha_id=str(candidate.get("alpha_id")) if candidate.get("alpha_id") is not None else None,
                simulation_id=str(candidate.get("simulation_id")) if candidate.get("simulation_id") is not None else None,
                expression=str(candidate.get("expression") or ""),
                classification=None,
                status=str(candidate.get("page_status") or batch_status) if (candidate.get("page_status") or batch_status) is not None else None,
                metrics=metrics,
                tests=tests,
                gate_results=gate_results,
                passing_gates=passing_gates,
                failing_gates=failing_gates,
                pending_gates=pending_gates,
                missing_gates=missing_gates,
                evidence_level=evidence_level,
                has_full_gate_coverage=has_full_gate_coverage,
                submit_ready=submit_ready,
                notes=_candidate_notes(candidate, parent_notes, blocking_reason),
            )
        )
    return outcomes


def load_candidate_check_artifacts(source: Path | str | Iterable[Path | str]) -> list[OfficialAlphaOutcome]:
    outcomes: list[OfficialAlphaOutcome] = []
    candidate_check_name = "candidate-check-status.json"
    if isinstance(source, (str, Path)):
        source_path = Path(source)
        if source_path.is_dir():
            paths = sorted(path for path in source_path.rglob(candidate_check_name) if path.is_file())
        else:
            paths = [source_path]
    else:
        paths = [Path(item) for item in source]

    for path in paths:
        if path.is_dir():
            continue
        if isinstance(source, (str, Path)) and Path(source).is_dir() and path.name != candidate_check_name:
            continue
        outcomes.extend(parse_candidate_check_artifact(path))
    return outcomes


def parse_candidate_batch(path: Path | str, *, include_linked_artifact: bool = True) -> list[OfficialAlphaOutcome]:
    batch_path = Path(path)
    data = json.loads(batch_path.read_text(encoding="utf-8"))
    capture_id = str(data.get("batch_id") or data.get("capture_id") or batch_path.stem)
    capture_topic = str(data.get("topic") or batch_path.stem)
    family_doc_path, family_key, family_topic = _candidate_family_reference(data, batch_path)
    parent_notes = _extract_notes({}, data)

    outcomes: list[OfficialAlphaOutcome] = []
    for candidate in _iter_candidate_payloads(data):
        metrics = _candidate_metrics(candidate)
        checks = _parse_candidate_checks(candidate)
        tests = _candidate_tests(candidate)
        gate_results = _gate_result_map(checks)
        passing_gates = tuple(gate for gate, result in gate_results.items() if result in NON_FAIL_RESULTS)
        failing_gates = tuple(gate for gate, result in gate_results.items() if result in FAIL_RESULTS)
        pending_gates = tuple(gate for gate, result in gate_results.items() if result in PENDING_RESULTS)
        missing_gates = tuple(gate for gate, result in gate_results.items() if result is None)
        evidence_level = _evidence_level_for_alpha(checks, tests)
        has_full_gate_coverage = evidence_level == "full_submission_gates"
        submit_ready = has_full_gate_coverage and _is_submit_ready_from_gate_results(gate_results)

        outcomes.append(
            OfficialAlphaOutcome(
                family_key=family_key,
                family_topic=family_topic,
                family_doc_path=family_doc_path,
                capture_path=batch_path.as_posix(),
                capture_id=capture_id,
                capture_topic=capture_topic,
                capture_mode="candidate-batch",
                alpha_name=str(candidate.get("name")) if candidate.get("name") is not None else None,
                alpha_id=str(candidate.get("alpha_id")) if candidate.get("alpha_id") is not None else None,
                simulation_id=str(candidate.get("simulation_id")) if candidate.get("simulation_id") is not None else None,
                expression=str(candidate.get("expression") or ""),
                classification=None,
                status=str(candidate.get("page_status")) if candidate.get("page_status") is not None else None,
                metrics=metrics,
                tests=tests,
                gate_results=gate_results,
                passing_gates=passing_gates,
                failing_gates=failing_gates,
                pending_gates=pending_gates,
                missing_gates=missing_gates,
                evidence_level=evidence_level,
                has_full_gate_coverage=has_full_gate_coverage,
                submit_ready=submit_ready,
                notes=_candidate_notes(candidate, parent_notes),
            )
        )

    if include_linked_artifact:
        evidence_path = _resolve_reference_path(data.get("evidence_path"), batch_path)
        if evidence_path and evidence_path.is_file():
            outcomes.extend(parse_candidate_check_artifact(evidence_path))
    return outcomes


def load_candidate_batches(
    source: Path | str | Iterable[Path | str],
    *,
    include_linked_artifact: bool = True,
) -> list[OfficialAlphaOutcome]:
    outcomes: list[OfficialAlphaOutcome] = []
    for path in _iter_paths(source, ".json"):
        outcomes.extend(
            parse_candidate_batch(
                path,
                include_linked_artifact=include_linked_artifact,
            )
        )
    return outcomes


def _coerce_outcome_objects(
    captures: Sequence[OfficialAlphaOutcome] | Path | str | Iterable[Path | str],
) -> list[OfficialAlphaOutcome]:
    if isinstance(captures, (str, Path)):
        return load_simulation_captures(captures)
    if isinstance(captures, Sequence):
        if not captures:
            return []
        sample = captures[0]
        if isinstance(sample, OfficialAlphaOutcome):
            return list(captures)
    return load_simulation_captures(captures)


def _coerce_outcome_records(
    captures: Sequence[OfficialAlphaOutcome] | Sequence[dict[str, Any]] | Path | str | Iterable[Path | str],
) -> list[dict[str, Any]]:
    if isinstance(captures, (str, Path)):
        return build_official_outcome_memory(captures)
    if isinstance(captures, Sequence):
        if not captures:
            return []
        sample = captures[0]
        if isinstance(sample, OfficialAlphaOutcome):
            return [_outcome_to_record(outcome) for outcome in captures]
        if isinstance(sample, dict):
            return [dict(item) for item in captures]
    return build_official_outcome_memory(captures)


def _coerce_doc_objects(
    family_docs: Sequence[ExpressionFamilyDoc] | Path | str | Iterable[Path | str],
) -> list[ExpressionFamilyDoc]:
    if isinstance(family_docs, (str, Path)):
        return load_expression_family_docs(family_docs)
    if isinstance(family_docs, Sequence):
        if not family_docs:
            return []
        sample = family_docs[0]
        if isinstance(sample, ExpressionFamilyDoc):
            return list(family_docs)
    return load_expression_family_docs(family_docs)


def _doc_to_record(doc: ExpressionFamilyDoc) -> dict[str, Any]:
    return {
        "path": doc.path.as_posix(),
        "title": doc.title,
        "topic": doc.topic,
        "family_key": doc.family_key,
        "metadata": dict(doc.metadata),
        "baseline_expression": doc.baseline_expression,
        "expressions": list(doc.expressions),
        "decision_lines": list(doc.decision_lines),
        "explicit_state_hints": list(doc.explicit_state_hints),
    }


def _outcome_to_record(outcome: OfficialAlphaOutcome) -> dict[str, Any]:
    strong_candidate_evidence = (
        outcome.capture_mode in {"candidate-batch", "candidate-check-status"}
        and _has_strong_candidate_evidence(outcome.gate_results, outcome.tests)
    )
    return {
        "family_key": outcome.family_key,
        "family_topic": outcome.family_topic,
        "family_doc_path": outcome.family_doc_path,
        "capture_path": outcome.capture_path,
        "capture_id": outcome.capture_id,
        "capture_topic": outcome.capture_topic,
        "capture_mode": outcome.capture_mode,
        "alpha_name": outcome.alpha_name,
        "alpha_id": outcome.alpha_id,
        "simulation_id": outcome.simulation_id,
        "expression": outcome.expression,
        "classification": outcome.classification,
        "status": outcome.status,
        "metrics": dict(outcome.metrics),
        "tests": dict(outcome.tests),
        "gate_results": dict(outcome.gate_results),
        "passing_gates": list(outcome.passing_gates),
        "failing_gates": list(outcome.failing_gates),
        "pending_gates": list(outcome.pending_gates),
        "missing_gates": list(outcome.missing_gates),
        "evidence_level": outcome.evidence_level,
        "has_full_gate_coverage": outcome.has_full_gate_coverage,
        "submit_ready": outcome.submit_ready,
        "strong_candidate_evidence": strong_candidate_evidence,
        "notes": list(outcome.notes),
        "evidence_sources": [outcome.capture_mode] if outcome.capture_mode else [],
        "supporting_paths": [outcome.capture_path],
        "supporting_capture_ids": [outcome.capture_id],
    }


def build_official_outcome_memory(
    captures: Sequence[OfficialAlphaOutcome] | Path | str | Iterable[Path | str],
) -> list[dict[str, Any]]:
    outcomes = _coerce_outcome_objects(captures)
    memory = [_outcome_to_record(outcome) for outcome in outcomes]
    memory.sort(
        key=lambda item: (
            item["family_key"],
            item["capture_id"],
            item["expression"],
        )
    )
    return memory


def build_candidate_outcome_memory(
    *,
    candidate_batches: Path | str | Iterable[Path | str] | None = None,
    candidate_check_artifacts: Path | str | Iterable[Path | str] | None = None,
) -> list[dict[str, Any]]:
    outcomes: list[OfficialAlphaOutcome] = []
    if candidate_batches is not None:
        outcomes.extend(load_candidate_batches(candidate_batches))
    if candidate_check_artifacts is not None:
        outcomes.extend(load_candidate_check_artifacts(candidate_check_artifacts))
    memory = [_outcome_to_record(outcome) for outcome in outcomes]
    return _merge_outcome_records(memory)


def _record_identity(record: dict[str, Any]) -> tuple[str, str]:
    alpha_id = record.get("alpha_id")
    if alpha_id:
        return ("alpha_id", str(alpha_id))
    simulation_id = record.get("simulation_id")
    if simulation_id:
        return ("simulation_id", str(simulation_id))
    expression = str(record.get("expression") or "").strip()
    family_key = str(record.get("family_key") or "")
    if expression:
        return ("expression", f"{family_key}::{expression}")
    alpha_name = str(record.get("alpha_name") or "").strip()
    if alpha_name:
        return ("alpha_name", f"{family_key}::{alpha_name}")
    return (
        "capture",
        "::".join(
            (
                family_key,
                str(record.get("capture_path") or ""),
                str(record.get("capture_id") or ""),
            )
        ),
    )


def _merge_priority(record: dict[str, Any]) -> tuple[int, int, int, int, int, int]:
    gate_results = record.get("gate_results", {})
    resolved_gate_count = sum(
        1 for gate in KNOWN_SUBMISSION_GATES
        if isinstance(gate_results, dict) and gate_results.get(gate) is not None
    )
    return (
        1 if record.get("submit_ready") else 0,
        1 if record.get("strong_candidate_evidence") else 0,
        1 if record.get("has_full_gate_coverage") else 0,
        resolved_gate_count,
        -len(record.get("failing_gates", [])),
        -len(record.get("pending_gates", [])),
        MERGE_SOURCE_PRIORITY.get(str(record.get("capture_mode") or ""), 0),
    )


def _best_non_empty(records: Sequence[dict[str, Any]], field_name: str) -> Any:
    for record in reversed(records):
        value = record.get(field_name)
        if value in (None, "", []):
            continue
        return value
    return None


def _is_synthetic_family_value(value: Any) -> bool:
    if value in (None, "", []):
        return False
    normalized = normalize_family_key(str(value))
    return normalized in {"candidate_check_status", "unknown", "unknown_family"}


def _preferred_family_value(records: Sequence[dict[str, Any]], field_name: str) -> Any:
    for record in reversed(records):
        value = record.get(field_name)
        if value in (None, "", []):
            continue
        if not _is_synthetic_family_value(value):
            return value
    return _best_non_empty(records, field_name)


def _merge_nested_dicts(records: Sequence[dict[str, Any]], field_name: str) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for record in records:
        nested = record.get(field_name)
        if not isinstance(nested, dict):
            continue
        for key, value in nested.items():
            if key not in merged or value is not None:
                merged[key] = value
    return merged


def _merge_outcome_records(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(_record_identity(record), []).append(dict(record))

    merged_records: list[dict[str, Any]] = []
    for group_records in grouped.values():
        ordered = sorted(group_records, key=_merge_priority)
        primary = dict(ordered[-1])
        merged_gate_results = {gate: None for gate in KNOWN_SUBMISSION_GATES}
        for record in ordered:
            raw_gate_results = record.get("gate_results")
            if not isinstance(raw_gate_results, dict):
                continue
            for gate in KNOWN_SUBMISSION_GATES:
                result = raw_gate_results.get(gate)
                if result is not None:
                    merged_gate_results[gate] = result

        merged_metrics = _merge_nested_dicts(ordered, "metrics")
        merged_tests = _merge_nested_dicts(ordered, "tests")
        passing_gates = [gate for gate, result in merged_gate_results.items() if result in NON_FAIL_RESULTS]
        failing_gates = [gate for gate, result in merged_gate_results.items() if result in FAIL_RESULTS]
        pending_gates = [gate for gate, result in merged_gate_results.items() if result in PENDING_RESULTS]
        missing_gates = [gate for gate, result in merged_gate_results.items() if result is None]
        has_full_gate_coverage = not missing_gates
        submit_ready = has_full_gate_coverage and _is_submit_ready_from_gate_results(merged_gate_results)
        evidence_level = _evidence_level_for_alpha(
            {
                gate: GateCheck(name=gate, result=result, limit=None, value=None)
                for gate, result in merged_gate_results.items()
                if result is not None
            },
            merged_tests,
        )

        primary["family_key"] = _preferred_family_value(ordered, "family_key") or primary.get("family_key")
        primary["family_topic"] = _preferred_family_value(ordered, "family_topic") or primary.get("family_topic")
        primary["family_doc_path"] = _best_non_empty(ordered, "family_doc_path")
        primary["alpha_name"] = _best_non_empty(ordered, "alpha_name")
        primary["alpha_id"] = _best_non_empty(ordered, "alpha_id")
        primary["simulation_id"] = _best_non_empty(ordered, "simulation_id")
        primary["expression"] = _best_non_empty(ordered, "expression") or ""
        primary["classification"] = _best_non_empty(ordered, "classification")
        primary["status"] = _best_non_empty(ordered, "status")
        primary["metrics"] = merged_metrics
        primary["tests"] = merged_tests
        primary["gate_results"] = merged_gate_results
        primary["passing_gates"] = passing_gates
        primary["failing_gates"] = failing_gates
        primary["pending_gates"] = pending_gates
        primary["missing_gates"] = missing_gates
        primary["evidence_level"] = evidence_level
        primary["has_full_gate_coverage"] = has_full_gate_coverage
        primary["submit_ready"] = submit_ready
        primary["strong_candidate_evidence"] = any(
            bool(record.get("strong_candidate_evidence"))
            for record in ordered
        ) or (
            str(primary.get("capture_mode") or "") in {"candidate-batch", "candidate-check-status"}
            and _has_strong_candidate_evidence(merged_gate_results, merged_tests)
        )
        primary["notes"] = list(
            _unique(
                note
                for record in ordered
                for note in record.get("notes", [])
                if isinstance(note, str) and note.strip()
            )
        )
        primary["evidence_sources"] = list(
            _unique(
                source
                for record in ordered
                for source in record.get("evidence_sources", [])
                if isinstance(source, str) and source
            )
        )
        primary["supporting_paths"] = list(
            _unique(
                path
                for record in ordered
                for path in record.get("supporting_paths", [])
                if isinstance(path, str) and path
            )
        )
        primary["supporting_capture_ids"] = list(
            _unique(
                capture_id
                for record in ordered
                for capture_id in record.get("supporting_capture_ids", [])
                if isinstance(capture_id, str) and capture_id
            )
        )
        merged_records.append(primary)

    merged_records.sort(
        key=lambda item: (
            item["family_key"],
            item.get("alpha_id") or "",
            item.get("simulation_id") or "",
            item["capture_id"],
            item["expression"],
        )
    )
    return merged_records


def build_combined_outcome_memory(
    captures: Sequence[OfficialAlphaOutcome] | Sequence[dict[str, Any]] | Path | str | Iterable[Path | str],
    *,
    candidate_batches: Path | str | Iterable[Path | str] | None = None,
    candidate_check_artifacts: Path | str | Iterable[Path | str] | None = None,
) -> list[dict[str, Any]]:
    official_memory = _coerce_outcome_records(captures)
    candidate_memory = build_candidate_outcome_memory(
        candidate_batches=candidate_batches,
        candidate_check_artifacts=candidate_check_artifacts,
    )
    return _merge_outcome_records([*official_memory, *candidate_memory])


def build_submit_ready_ledger(
    captures: Sequence[OfficialAlphaOutcome] | Sequence[dict[str, Any]] | Path | str | Iterable[Path | str],
    *,
    candidate_batches: Path | str | Iterable[Path | str] | None = None,
    candidate_check_artifacts: Path | str | Iterable[Path | str] | None = None,
) -> list[dict[str, Any]]:
    if candidate_batches is None and candidate_check_artifacts is None:
        memory = _coerce_outcome_records(captures)
    else:
        memory = build_combined_outcome_memory(
            captures,
            candidate_batches=candidate_batches,
            candidate_check_artifacts=candidate_check_artifacts,
        )
    ledger = [item for item in memory if item.get("submit_ready")]
    ledger.sort(key=lambda item: (item["family_key"], item["capture_id"], item["expression"]))
    return ledger


def _metric_float(metrics: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.strip().replace("%", "").replace("‱", "")
            try:
                return float(cleaned)
            except ValueError:
                continue
    return None


def _best_outcome_record(records: Sequence[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None

    def sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
        metrics = item.get("metrics", {})
        return (
            0 if item.get("submit_ready") else 1,
            0 if item.get("has_full_gate_coverage") else 1,
            len(item.get("failing_gates", [])),
            len(item.get("pending_gates", [])),
            len(item.get("missing_gates", [])),
            -len(item.get("passing_gates", [])),
            -(_metric_float(metrics, "is_sharpe", "sharpe") or -9999.0),
            -(_metric_float(metrics, "is_fitness", "fitness") or -9999.0),
            item.get("capture_id", ""),
            item.get("expression", ""),
        )

    return min(records, key=sort_key)


def _family_state_from_hints_and_memory(
    explicit_hints: set[str],
    family_outcomes: Sequence[dict[str, Any]],
    submit_ready_entries: Sequence[dict[str, Any]],
) -> tuple[str, str]:
    if submit_ready_entries:
        return "exploit", "at least one official outcome is submit-ready"
    if "branch" in explicit_hints:
        return "branch", "family docs explicitly keep this family in branch"
    if "hold" in explicit_hints:
        return "hold", "family docs explicitly hold this family"
    if "kill" in explicit_hints:
        return "kill", "family docs explicitly kill this family"
    if any(item.get("strong_candidate_evidence") for item in family_outcomes):
        return "branch", "candidate evidence is clean on the common subset, but full submission gates are still missing"
    if any(item.get("tests", {}).get("subuniverse_pass") is True for item in family_outcomes):
        return "branch", "family has non-null sub-universe evidence but no full submit-ready gate record yet"
    if family_outcomes:
        return "hold", "official evidence exists but no submit-ready outcome is recorded"
    return "explore", "no official outcomes or explicit hold/kill decision found"


def build_family_registry_summary(
    family_docs: Sequence[ExpressionFamilyDoc] | Path | str | Iterable[Path | str],
    captures: Sequence[OfficialAlphaOutcome] | Sequence[dict[str, Any]] | Path | str | Iterable[Path | str],
    *,
    candidate_batches: Path | str | Iterable[Path | str] | None = None,
    candidate_check_artifacts: Path | str | Iterable[Path | str] | None = None,
) -> list[dict[str, Any]]:
    docs = _coerce_doc_objects(family_docs)
    if candidate_batches is None and candidate_check_artifacts is None:
        memory = _coerce_outcome_records(captures)
    else:
        memory = build_combined_outcome_memory(
            captures,
            candidate_batches=candidate_batches,
            candidate_check_artifacts=candidate_check_artifacts,
        )

    docs_by_family: dict[str, list[ExpressionFamilyDoc]] = {}
    for doc in docs:
        docs_by_family.setdefault(doc.family_key, []).append(doc)

    outcomes_by_family: dict[str, list[dict[str, Any]]] = {}
    for record in memory:
        outcomes_by_family.setdefault(str(record["family_key"]), []).append(record)

    all_family_keys = sorted(set(docs_by_family) | set(outcomes_by_family))
    summary: list[dict[str, Any]] = []
    for family_key in all_family_keys:
        family_docs_for_key = docs_by_family.get(family_key, [])
        family_outcomes = outcomes_by_family.get(family_key, [])
        submit_ready_entries = [item for item in family_outcomes if item.get("submit_ready")]
        explicit_hints = {
            hint
            for doc in family_docs_for_key
            for hint in doc.explicit_state_hints
        }
        state, reason = _family_state_from_hints_and_memory(explicit_hints, family_outcomes, submit_ready_entries)
        best_outcome = _best_outcome_record(family_outcomes)

        failing_hist: dict[str, int] = {}
        pending_hist: dict[str, int] = {}
        for item in family_outcomes:
            for gate in item.get("failing_gates", []):
                failing_hist[gate] = failing_hist.get(gate, 0) + 1
            for gate in item.get("pending_gates", []):
                pending_hist[gate] = pending_hist.get(gate, 0) + 1

        summary.append(
            {
                "family_key": family_key,
                "state": state,
                "reason": reason,
                "topics": sorted(_unique(doc.topic for doc in family_docs_for_key)),
                "doc_paths": [doc.path.as_posix() for doc in family_docs_for_key],
                "capture_paths": sorted(_unique(item["capture_path"] for item in family_outcomes)),
                "baseline_expressions": [
                    doc.baseline_expression
                    for doc in family_docs_for_key
                    if doc.baseline_expression
                ],
                "decision_lines": [
                    line
                    for doc in family_docs_for_key
                    for line in doc.decision_lines
                ],
                "explicit_state_hints": sorted(explicit_hints),
                "official_outcome_count": len(family_outcomes),
                "candidate_outcome_count": sum(1 for item in family_outcomes if item.get("capture_mode") in {"candidate-batch", "candidate-check-status"}),
                "full_gate_outcome_count": sum(1 for item in family_outcomes if item.get("has_full_gate_coverage")),
                "submit_ready_count": len(submit_ready_entries),
                "strong_candidate_evidence_count": sum(1 for item in family_outcomes if item.get("strong_candidate_evidence")),
                "failing_gate_histogram": dict(sorted(failing_hist.items())),
                "pending_gate_histogram": dict(sorted(pending_hist.items())),
                "best_outcome": best_outcome,
            }
        )

    summary.sort(key=lambda item: (item["state"], item["family_key"]))
    return summary


def build_success_rate_state(
    *,
    family_dir: Path | str | Iterable[Path | str],
    capture_dir: Path | str | Iterable[Path | str],
    candidate_batch_dir: Path | str | Iterable[Path | str] | None = None,
    candidate_check_dir: Path | str | Iterable[Path | str] | None = None,
) -> dict[str, Any]:
    docs = load_expression_family_docs(family_dir)
    outcomes = load_simulation_captures(capture_dir)
    outcome_memory = build_official_outcome_memory(outcomes)
    candidate_outcome_memory = build_candidate_outcome_memory(
        candidate_batches=candidate_batch_dir,
        candidate_check_artifacts=candidate_check_dir,
    )
    combined_outcome_memory = build_combined_outcome_memory(
        outcome_memory,
        candidate_batches=candidate_batch_dir,
        candidate_check_artifacts=candidate_check_dir,
    )
    submit_ready = build_submit_ready_ledger(combined_outcome_memory)
    family_registry = build_family_registry_summary(docs, combined_outcome_memory)
    return {
        "family_docs": [_doc_to_record(doc) for doc in docs],
        "official_outcome_memory": outcome_memory,
        "candidate_outcome_memory": candidate_outcome_memory,
        "combined_outcome_memory": combined_outcome_memory,
        "submit_ready_ledger": submit_ready,
        "family_registry_summary": family_registry,
    }


__all__ = [
    "ExpressionFamilyDoc",
    "FAMILY_STATES",
    "GateCheck",
    "KNOWN_SUBMISSION_GATES",
    "OfficialAlphaOutcome",
    "SELF_CORRELATION_GATE",
    "build_candidate_outcome_memory",
    "build_combined_outcome_memory",
    "build_family_registry_summary",
    "build_official_outcome_memory",
    "build_submit_ready_ledger",
    "build_success_rate_state",
    "load_candidate_batches",
    "load_candidate_check_artifacts",
    "load_expression_family_docs",
    "load_success_policy",
    "load_simulation_captures",
    "normalize_family_key",
    "parse_candidate_batch",
    "parse_candidate_check_artifact",
    "parse_expression_family_doc",
    "parse_simulation_capture",
]

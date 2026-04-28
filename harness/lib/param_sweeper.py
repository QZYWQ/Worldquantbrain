"""Parameter sweep generator for BRAIN_LAB expression families.

This module performs local-only sweep generation and writes provenance-tagged
candidate batches under `runs/candidate-batches/`.

Negative-Sharpe gate:
- `sweep_params(..., is_sharpe_negative=True)` is treated as a hard stop unless
  `allow_negative_sharpe=True` is supplied explicitly.
- The default behavior is to block further parameter expansion for lanes that
  are already known to be negative Sharpe, so sign-flip control must happen
  before any new sweep is emitted.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from compiler import canonicalize_expression, compile_alpha, extract_numeric_literals, replace_source_span

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "runs" / "candidate-batches"

DEFAULT_PARAM_RANGES: dict[str, Any] = {
    "windows": [5, 10, 20, 30, 60, 120, 252],
    "decays": [2, 4, 8, 16, 32, 64],
    "thresholds": [0.05, 0.1, 0.2, 0.5, 1.0, 1.5],
    "literals": [0.5, 1, 1.5, 2, 3, 5],
    "max_total_variants": 128,
    "max_variants_per_literal": 8,
    "validate_variants": True,
    "keep_original": False,
}

SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")
LOGGER = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    slug = SLUG_RE.sub("-", text).strip("-")
    return slug or "expression"


def _project_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def _merge_ranges(user_ranges: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_PARAM_RANGES)
    if not isinstance(user_ranges, dict):
        return merged
    for key, value in user_ranges.items():
        if value is None:
            continue
        merged[key] = value
    return merged


def _numeric_bucket(literal: dict[str, Any]) -> str:
    role = str(literal.get("role") or "scalar")
    value = literal.get("value")
    call_name = str(literal.get("call_name") or "")
    if role in {"window", "decay", "threshold"}:
        return role
    if isinstance(value, int) and 2 <= value <= 252:
        if any(token in call_name for token in ("delay", "rank", "mean", "std", "corr", "cov", "delta", "backfill", "decay")):
            return "window"
        return "window"
    if isinstance(value, float) and 0.0 < abs(value) <= 2.0:
        return "threshold"
    return "scalar"


def _candidate_values(bucket: str, ranges: dict[str, Any]) -> list[Any]:
    if bucket == "window":
        values = ranges.get("windows", [])
    elif bucket == "decay":
        values = ranges.get("decays", [])
    elif bucket == "threshold":
        values = ranges.get("thresholds", [])
    else:
        values = ranges.get("literals", [])
    if not isinstance(values, list):
        return []
    seen: set[str] = set()
    ordered: list[Any] = []
    for value in values:
        key = repr(value)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(value)
    return ordered


def _format_numeric(value: Any, original_text: str) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric.is_integer():
        return str(int(numeric))
    if "." in original_text:
        decimals = len(original_text.split(".", 1)[1].rstrip("0"))
        if decimals > 0:
            return f"{numeric:.{decimals}f}".rstrip("0").rstrip(".")
    return f"{numeric:.12g}"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _comment_markers(text: str) -> list[str]:
    markers: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("//"):
            markers.append(stripped)
    return markers


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _provenance_header(manifest: dict[str, Any], literal: dict[str, Any], candidate_value: Any) -> str:
    lines = [
        f"# provenance: {json.dumps(manifest, ensure_ascii=False, sort_keys=True)}",
        f"# sweep_role: {literal.get('role') or 'scalar'}",
        f"# source_literal: {literal.get('text')}",
        f"# candidate_literal: {_format_numeric(candidate_value, str(literal.get('text') or ''))}",
        f"# literal_location: line {literal.get('line')}, column {literal.get('col')}",
        "",
    ]
    return "\n".join(lines)


def _format_variant_id(source_stem: str, index: int, literal: dict[str, Any], candidate_value: Any) -> str:
    bucket = _numeric_bucket(literal)
    original = _format_numeric(literal.get("value"), str(literal.get("text") or ""))
    candidate = _format_numeric(candidate_value, str(literal.get("text") or ""))
    suffix = _slugify(f"{bucket}-{literal.get('line', 0)}-{literal.get('col', 0)}-{original}-to-{candidate}")
    return f"{_slugify(source_stem)}__v{index:03d}__{suffix}"


def _build_manifest(
    *,
    batch_id: str,
    source_path: Path,
    source_text: str,
    ranges: dict[str, Any],
    variants: list[dict[str, Any]],
    rejected_variants: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "batch_id": batch_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "keep_original": bool(ranges.get("keep_original", False)),
        "max_total_variants": ranges.get("max_total_variants"),
        "max_variants_per_literal": ranges.get("max_variants_per_literal"),
        "param_overrides": {
            "decays": list(ranges.get("decays", [])),
            "neutralizations": list(ranges.get("neutralizations", [])) if isinstance(ranges.get("neutralizations"), list) else [],
        },
        "source_expr_path": _project_relative(source_path),
        "source_sha256": _sha256_text(source_text),
        "source_markers": _comment_markers(source_text),
        "template_overrides": [variant["wqb_expression"] for variant in variants],
        "variants": variants,
        "rejected_variants": rejected_variants,
    }


def sweep_params(
    expr_file_path: str,
    param_ranges: dict[str, Any] | None = None,
    *,
    allow_negative_sharpe: bool = False,
    is_sharpe_negative: bool | None = None,
) -> list[dict[str, Any]]:
    """Generate provenance-tagged parameter variants from a source expression file.

    Args:
        expr_file_path: Source `.expr` file to sweep.
        param_ranges: Optional override ranges for windows/decays/thresholds.
        allow_negative_sharpe: Explicit override for lanes known to have negative
            Sharpe. Keep this False by default to enforce sign-flip discipline.
        is_sharpe_negative: Optional signal from the caller or ledger context
            indicating the baseline is negative Sharpe. When True and
            `allow_negative_sharpe` is False, this function raises `ValueError`
            instead of generating new variants.

    Returns:
        A list of validated variant records. Returns an empty list only when no
        eligible numeric literals are found or all candidate variants are
        filtered out.
    """
    if is_sharpe_negative is True and not allow_negative_sharpe:
        message = (
            "negative-Sharpe lanes must be sign-flipped before parameter sweeping; "
            "pass allow_negative_sharpe=True only after explicit review"
        )
        LOGGER.warning(message)
        raise ValueError(message)

    ranges = _merge_ranges(param_ranges)
    source_path = Path(expr_file_path).expanduser()
    if not source_path.is_absolute():
        source_path = (PROJECT_ROOT / source_path).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"expression file not found: {source_path}")

    source_text = source_path.read_text(encoding="utf-8")
    literals = extract_numeric_literals(source_text)
    batch_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{_slugify(source_path.stem)}-sweep"
    batch_root = DEFAULT_OUTPUT_ROOT / batch_id
    variant_root = batch_root / "variants"
    batch_root.mkdir(parents=True, exist_ok=True)
    variant_root.mkdir(parents=True, exist_ok=True)

    validated_variants: list[dict[str, Any]] = []
    rejected_variants: list[dict[str, Any]] = []
    seen_expressions: set[str] = set()
    total_limit = int(ranges.get("max_total_variants") or 0) or 0
    per_literal_limit = int(ranges.get("max_variants_per_literal") or 0) or 0
    validate_variants = bool(ranges.get("validate_variants", True))

    variant_index = 0
    for literal_index, literal in enumerate(literals, start=1):
        bucket = _numeric_bucket(literal)
        candidate_values = _candidate_values(bucket, ranges)
        if not candidate_values:
            continue

        emitted_for_literal = 0
        for candidate_value in candidate_values:
            if repr(candidate_value) == repr(literal.get("value")):
                continue
            if per_literal_limit and emitted_for_literal >= per_literal_limit:
                break
            if total_limit and len(validated_variants) >= total_limit:
                break

            variant_index += 1
            emitted_for_literal += 1
            variant_text = replace_source_span(
                source_text,
                int(literal["start"]),
                int(literal["end"]),
                _format_numeric(candidate_value, str(literal.get("text") or "")),
            )
            normalized = canonicalize_expression(variant_text)
            if not normalized or normalized in seen_expressions:
                continue

            compile_result = compile_alpha(variant_text) if validate_variants else {"valid": True, "warnings": [], "error": "", "wqb_expression": normalized}
            base_record = {
                "variant_id": _format_variant_id(source_path.stem, variant_index, literal, candidate_value),
                "literal_index": literal_index,
                "role": bucket,
                "original_value": literal.get("value"),
                "candidate_value": candidate_value,
                "source_literal": literal.get("text"),
                "line": literal.get("line"),
                "column": literal.get("col"),
                "call_name": literal.get("call_name"),
                "arg_index": literal.get("arg_index"),
                "wqb_expression": compile_result.get("wqb_expression") or normalized,
                "valid": bool(compile_result.get("valid")),
                "warnings": list(compile_result.get("warnings") or []),
            }

            if not base_record["valid"]:
                rejected_variants.append({**base_record, "error": str(compile_result.get("error") or "compile failed")})
                continue

            seen_expressions.add(normalized)
            manifest_stub = {
                "batch_id": batch_id,
                "source_expr_path": _project_relative(source_path),
                "source_sha256": _sha256_text(source_text),
                "variant_id": base_record["variant_id"],
                "role": base_record["role"],
                "original_value": base_record["original_value"],
                "candidate_value": base_record["candidate_value"],
                "line": base_record["line"],
                "column": base_record["column"],
            }
            file_name = f"{base_record['variant_id']}.expr"
            file_path = variant_root / file_name
            header = _provenance_header(manifest_stub, literal, candidate_value)
            _write_text(file_path, header + variant_text.rstrip() + "\n")

            record = {
                **base_record,
                "candidate_file": _project_relative(file_path),
                "candidate_path": str(file_path),
                "template_override": base_record["wqb_expression"],
            }
            validated_variants.append(record)

    manifest = _build_manifest(
        batch_id=batch_id,
        source_path=source_path,
        source_text=source_text,
        ranges=ranges,
        variants=validated_variants,
        rejected_variants=rejected_variants,
    )
    manifest_path = batch_root / "manifest.json"
    root_manifest_path = DEFAULT_OUTPUT_ROOT / f"{batch_id}.json"
    _write_text(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    _write_text(root_manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    readme = batch_root / "README.md"
    if not readme.exists():
        _write_text(
            readme,
            "\n".join(
                [
                    "# Candidate Batch",
                    "",
                    f"- batch_id: {batch_id}",
                    f"- source: {_project_relative(source_path)}",
                    f"- variants: {len(validated_variants)}",
                    f"- rejected: {len(rejected_variants)}",
                ]
            )
            + "\n",
        )

    return validated_variants


__all__ = ["sweep_params"]

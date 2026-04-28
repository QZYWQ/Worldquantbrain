from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

try:  # pragma: no cover - dual import path for script/package execution
    from harness.lib.compiler import compile_alpha, extract_components, load_compiler_config
except ImportError:  # pragma: no cover
    from compiler import compile_alpha, extract_components, load_compiler_config

from .models import AlphaCandidate, WinnerRecord


LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "evolution_config.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runs" / "evolution" / "generations"
DEFAULT_LOG_PATH = PROJECT_ROOT / "runs" / "evolution" / "evolution_log.jsonl"


def _resolve_project_path(path: str | Path) -> Path:
    resolved = Path(path).expanduser()
    if resolved.is_absolute():
        return resolved
    return (PROJECT_ROOT / resolved).resolve()


def _resolve_db_path(db_path: str | Path) -> Path:
    return _resolve_project_path(db_path)


def _slugify(value: str) -> str:
    cleaned = []
    for char in value:
        if char.isalnum() or char in {"-", "_", "."}:
            cleaned.append(char)
        else:
            cleaned.append("-")
    text = "".join(cleaned).strip("-_.")
    return text or "candidate"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def structural_fingerprint(expr: str) -> str:
    """Return a coarse structural fingerprint for duplicate filtering.

    The fingerprint intentionally ignores literal formatting and ordering noise
    by canonicalizing the expression first, then reducing it to sorted unique
    operator and field sets.
    """

    compile_result = compile_alpha(expr)
    source = str(compile_result.get("wqb_expression") or expr or "").strip()
    if not source:
        return "|"

    component_result = extract_components(source)
    operators = sorted({str(item) for item in component_result.get("operators") or [] if str(item)})
    fields = sorted({str(item) for item in component_result.get("fields") or [] if str(item)})
    return f"{','.join(operators)}|{','.join(fields)}"


def _candidate_to_dict(candidate: AlphaCandidate) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "generation": candidate.generation,
        "rank": candidate.rank,
        "expression": candidate.expression,
        "wqb_expression": candidate.wqb_expression,
        "lineage": _json_safe(candidate.lineage),
        "operators": list(candidate.operators),
        "fields": list(candidate.fields),
        "parameters": [dict(item) for item in candidate.parameters],
        "surrogate_score": candidate.surrogate_score,
        "expected_sharpe_estimate": candidate.expected_sharpe_estimate,
        "metadata": _json_safe(candidate.metadata),
    }


def _candidate_batch_field(candidate: AlphaCandidate, priority: str) -> dict[str, Any]:
    metadata = candidate.metadata if isinstance(candidate.metadata, dict) else {}
    return {
        "name": candidate.candidate_id,
        "source_domain": str(metadata.get("source_domain") or "evolution"),
        "type": str(metadata.get("type") or "evolution_candidate"),
        "coverage": 1.0,
        "user_count": 1,
        "alpha_count": 1,
        "priority": priority,
        "description": str(metadata.get("description") or candidate.lineage.get("method") or "evolution candidate"),
        "template_overrides": [candidate.wqb_expression],
        "param_overrides": {"decays": [0], "neutralizations": [None]},
        "metadata": _json_safe(metadata),
        "lineage": _json_safe(candidate.lineage),
        "expression": candidate.wqb_expression,
    }


def _write_expr_file(path: Path, candidate: AlphaCandidate, generation: int, created_at: str) -> None:
    provenance = {
        "candidate_id": candidate.candidate_id,
        "generation": generation,
        "created_at": created_at,
        "lineage": _json_safe(candidate.lineage),
        "surrogate_score": candidate.surrogate_score,
    }
    lines = [
        "# provenance: brain_evolution_engine",
        f"# data: {json.dumps(provenance, ensure_ascii=False, sort_keys=True)}",
        candidate.wqb_expression,
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _generation_summary(population: list[AlphaCandidate]) -> dict[str, Any]:
    if not population:
        return {
            "candidate_count": 0,
            "unique_expression_count": 0,
            "avg_surrogate_score": 0.0,
            "max_surrogate_score": 0.0,
            "min_surrogate_score": 0.0,
        }
    scores = [float(candidate.surrogate_score) for candidate in population]
    unique_expressions = {candidate.wqb_expression for candidate in population}
    return {
        "candidate_count": len(population),
        "unique_expression_count": len(unique_expressions),
        "avg_surrogate_score": sum(scores) / len(scores),
        "max_surrogate_score": max(scores),
        "min_surrogate_score": min(scores),
    }


def _load_output_config(config: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}
    output_cfg = config.get("output")
    return output_cfg if isinstance(output_cfg, dict) else {}


def _elite_cutoff(population: list[AlphaCandidate], config: dict[str, Any] | None) -> int:
    if not population:
        return 0
    elite_fraction = 0.1
    if isinstance(config, dict):
        elite_fraction = float(config.get("elite_fraction") or elite_fraction)
    if elite_fraction <= 0:
        return 0
    return max(1, int(round(len(population) * elite_fraction)))


def _resolve_output_root(config: dict[str, Any] | None) -> Path:
    output_cfg = _load_output_config(config)
    root = output_cfg.get("root") if isinstance(output_cfg.get("root"), (str, Path)) else DEFAULT_OUTPUT_DIR
    return _resolve_project_path(root)


def _resolve_log_path(config: dict[str, Any] | None) -> Path:
    output_cfg = _load_output_config(config)
    log_path = output_cfg.get("log_path") if isinstance(output_cfg.get("log_path"), (str, Path)) else DEFAULT_LOG_PATH
    return _resolve_project_path(log_path)


def _write_generation_log(log_path: Path, record: dict[str, Any]) -> None:
    _ensure_directory(log_path.parent)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(record), ensure_ascii=False, sort_keys=True) + "\n")


def _resolve_generation_paths(generation: int, config: dict[str, Any] | None = None) -> tuple[Path, Path, Path, Path, Path]:
    root = _resolve_output_root(config)
    generation_dir = root / f"gen_{generation:03d}"
    expr_dir = generation_dir / "expr"
    canonical_path = root / f"gen_{generation:03d}.json"
    batch_path = root / f"gen_{generation:03d}.batch.json"
    return root, generation_dir, expr_dir, canonical_path, batch_path


def _candidate_batch_priority(index: int, elite_count: int) -> str:
    return "high" if index <= elite_count else "medium"


def _candidate_filename(index: int, candidate: AlphaCandidate) -> str:
    return f"{index:03d}-{_slugify(candidate.candidate_id)}.expr"


def _canonical_generation_payload(
    *,
    generation: int,
    created_at: str,
    population: list[AlphaCandidate],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    summary = _generation_summary(population)
    return {
        "source": "brain_evolution_engine",
        "generation": generation,
        "created_at": created_at,
        "population_size": len(population),
        "elite_count": _elite_cutoff(population, config),
        "summary": summary,
        "candidates": [_candidate_to_dict(candidate) for candidate in population],
    }


def _batch_view_payload(
    *,
    generation: int,
    created_at: str,
    population: list[AlphaCandidate],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    elite_count = _elite_cutoff(population, config)
    fields = [
        _candidate_batch_field(candidate, _candidate_batch_priority(index, elite_count))
        for index, candidate in enumerate(population, start=1)
    ]
    return {
        "source": "brain_evolution_engine",
        "generation": generation,
        "created_at": created_at,
        "fields": fields,
        "param_overrides": {"decays": [0], "neutralizations": [None]},
    }


def _append_generation_log(
    *,
    generation: int,
    created_at: str,
    population: list[AlphaCandidate],
    canonical_path: Path,
    batch_path: Path | None,
    expr_dir: Path,
    metrics: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    summary = _generation_summary(population)
    log_record = {
        "generation": generation,
        "created_at": created_at,
        "candidate_count": summary["candidate_count"],
        "unique_expression_count": summary["unique_expression_count"],
        "avg_surrogate_score": summary["avg_surrogate_score"],
        "max_surrogate_score": summary["max_surrogate_score"],
        "min_surrogate_score": summary["min_surrogate_score"],
        "canonical_path": str(canonical_path),
        "batch_path": str(batch_path) if batch_path is not None else None,
        "expr_dir": str(expr_dir),
    }
    if isinstance(metrics, dict) and metrics:
        log_record.update(_json_safe(metrics))
    _write_generation_log(_resolve_log_path(config), log_record)
    return log_record


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number == number else default


def _parse_tags(raw_tags: Any) -> tuple[str, ...]:
    if raw_tags in (None, ""):
        return ()
    if isinstance(raw_tags, (list, tuple, set)):
        return tuple(str(tag) for tag in raw_tags if tag not in (None, ""))
    if isinstance(raw_tags, str):
        text = raw_tags.strip()
        if not text:
            return ()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, list):
            return tuple(str(tag) for tag in payload if tag not in (None, ""))
        return tuple(part.strip() for part in text.split(",") if part.strip())
    return (str(raw_tags),)


def _score_row(sharpe: float, fitness: float, turnover: float) -> float:
    return 0.5 * sharpe + 0.3 * fitness + 0.2 * (1.0 / (1.0 + max(turnover, 0.0)))


def load_winners_from_ledger(db_path: str | Path, config: dict[str, Any] | None = None) -> list[WinnerRecord]:
    """Load winner records from the ledger and return the top scored rows."""

    cfg = config if isinstance(config, dict) else {}
    winner_query = cfg.get("winner_query") if isinstance(cfg.get("winner_query"), dict) else {}
    status_values = winner_query.get("status_values") if isinstance(winner_query.get("status_values"), list) else ["passed"]
    status_values_normalized = {str(value).strip().lower() for value in status_values if str(value).strip()}
    min_sharpe = _safe_float(winner_query.get("min_sharpe"), 0.0)
    limit = int(cfg.get("population_size") or winner_query.get("limit") or 50)
    dedupe_key = str(winner_query.get("dedupe_key") or "expression_normalized")

    resolved_db = _resolve_db_path(db_path)
    if not resolved_db.exists():
        LOGGER.warning("winner ledger missing db=%s", resolved_db)
        return []

    try:
        connection = sqlite3.connect(str(resolved_db))
    except sqlite3.DatabaseError as exc:
        LOGGER.warning("winner ledger connect failed db=%s error=%s", resolved_db, exc)
        return []

    connection.row_factory = sqlite3.Row
    try:
        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    alpha_id,
                    expression,
                    expression_normalized,
                    field_name,
                    source,
                    stage,
                    decay,
                    neutralization,
                    is_sharpe,
                    is_fitness,
                    turnover,
                    status,
                    tags,
                    timestamp,
                    raw_json,
                    capture_id,
                    file_path,
                    test_period,
                    region,
                    universe
                FROM simulations
                WHERE is_sharpe IS NOT NULL
                ORDER BY COALESCE(is_sharpe, -1e9) DESC, COALESCE(is_fitness, -1e9) DESC, COALESCE(turnover, 1e9) ASC, id ASC
                """
            ).fetchall()
        except sqlite3.DatabaseError as exc:
            LOGGER.warning("winner ledger query failed db=%s error=%s", resolved_db, exc)
            return []
    finally:
        connection.close()

    best_by_key: dict[str, WinnerRecord] = {}
    archive_fingerprints: set[str] = set()
    known_fields: set[str] = set()
    skipped_invalid = 0
    skipped_ineligible = 0

    for row in rows:
        raw_expression = str(row["expression"] or "").strip()
        field_name = str(row["field_name"] or "").strip()
        if field_name:
            known_fields.add(field_name)
        if not raw_expression:
            skipped_invalid += 1
            continue

        status = str(row["status"] or "").strip().lower()
        sharpe = _safe_float(row["is_sharpe"], 0.0)
        fitness = _safe_float(row["is_fitness"], 0.0)
        turnover = _safe_float(row["turnover"], 0.0)
        if status_values_normalized and status not in status_values_normalized and sharpe <= min_sharpe:
            skipped_ineligible += 1
            continue
        if sharpe <= min_sharpe and status not in status_values_normalized:
            skipped_ineligible += 1
            continue

        compile_result = compile_alpha(raw_expression)
        if not bool(compile_result.get("valid")):
            skipped_invalid += 1
            LOGGER.warning(
                "skip invalid winner row_id=%s alpha_id=%s error=%s",
                row["id"],
                row["alpha_id"],
                compile_result.get("error"),
            )
            continue

        normalized_expression = str(compile_result.get("wqb_expression") or raw_expression).strip()
        component_result = extract_components(raw_expression)
        operators = tuple(str(item) for item in component_result.get("operators") or [])
        fields = tuple(str(item) for item in component_result.get("fields") or [])
        parameters = tuple(
            dict(item) for item in (component_result.get("parameters") or []) if isinstance(item, dict)
        )
        score = _score_row(sharpe, fitness, turnover)
        winner_id = f"winner-{int(row['id'])}"
        alpha_id = str(row["alpha_id"] or "")
        metadata = {
            "compiler_warnings": list(compile_result.get("warnings") or []),
            "compile_error": compile_result.get("error"),
            "component_warnings": list(component_result.get("warnings") or []),
            "capture_id": row["capture_id"],
            "file_path": row["file_path"],
            "test_period": row["test_period"],
            "region": row["region"],
            "universe": row["universe"],
            "stage": row["stage"],
            "decay": row["decay"],
            "neutralization": row["neutralization"],
            "raw_json": row["raw_json"],
        }

        record = WinnerRecord(
            winner_id=winner_id,
            ledger_row_id=int(row["id"]),
            alpha_id=alpha_id or None,
            expression=raw_expression,
            wqb_expression=normalized_expression,
            sharpe=sharpe,
            fitness=fitness,
            turnover=turnover,
            status=status or "unknown",
            tags=_parse_tags(row["tags"]),
            timestamp=str(row["timestamp"] or ""),
            field_name=str(row["field_name"] or "") or None,
            source=str(row["source"] or "") or None,
            metadata=metadata,
            operators=operators,
            fields=fields,
            parameters=parameters,
            score=score,
        )

        archive_fingerprints.add(structural_fingerprint(normalized_expression))

        dedupe_value = getattr(record, dedupe_key, None)
        if dedupe_value in (None, ""):
            dedupe_value = record.wqb_expression
        dedupe_key_value = str(dedupe_value)
        existing = best_by_key.get(dedupe_key_value)
        if existing is None or record.score > existing.score:
            best_by_key[dedupe_key_value] = record

    winners = sorted(
        best_by_key.values(),
        key=lambda item: (-float(item.score), -float(item.sharpe), -float(item.fitness), float(item.turnover), item.ledger_row_id),
    )
    if limit > 0:
        winners = winners[:limit]

    if not known_fields:
        fallback_fields = load_compiler_config().get("known_fields") or []
        for item in fallback_fields:
            if isinstance(item, str) and item.strip():
                known_fields.add(item.strip())

    cfg["known_fields"] = sorted(known_fields)
    cfg["archive_fingerprints"] = sorted(archive_fingerprints)

    LOGGER.info(
        "loaded winners db=%s total_rows=%d loaded=%d skipped_invalid=%d skipped_ineligible=%d limit=%d",
        resolved_db,
        len(rows),
        len(winners),
        skipped_invalid,
        skipped_ineligible,
        limit,
    )
    return winners


def export_generation(
    generation: int,
    population: list[AlphaCandidate],
    metrics: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write generation artifacts to runs/evolution/."""

    created_at = datetime.now().isoformat(timespec="seconds")
    root, generation_dir, expr_dir, canonical_path, batch_path = _resolve_generation_paths(generation, config)
    _ensure_directory(root)
    _ensure_directory(generation_dir)
    _ensure_directory(expr_dir)

    output_cfg = _load_output_config(config)
    write_expr_files = True
    write_batch_view = True
    if isinstance(output_cfg.get("write_expr_files"), bool):
        write_expr_files = output_cfg["write_expr_files"]
    if isinstance(output_cfg.get("write_batch_view"), bool):
        write_batch_view = output_cfg["write_batch_view"]

    canonical_payload = _canonical_generation_payload(
        generation=generation,
        created_at=created_at,
        population=population,
        config=config,
    )
    canonical_path.write_text(
        json.dumps(_json_safe(canonical_payload), indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )

    batch_payload = _batch_view_payload(
        generation=generation,
        created_at=created_at,
        population=population,
        config=config,
    )
    if write_batch_view:
        batch_path.write_text(
            json.dumps(_json_safe(batch_payload), indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
    else:
        batch_path = None

    if write_expr_files:
        for index, candidate in enumerate(population, start=1):
            expr_path = expr_dir / _candidate_filename(index, candidate)
            _write_expr_file(expr_path, candidate, generation, created_at)

    log_record = _append_generation_log(
        generation=generation,
        created_at=created_at,
        population=population,
        canonical_path=canonical_path,
        batch_path=batch_path,
        expr_dir=expr_dir,
        metrics=metrics,
        config=config,
    )
    return {
        "generation": generation,
        "created_at": created_at,
        "root": str(root),
        "generation_dir": str(generation_dir),
        "expr_dir": str(expr_dir),
        "canonical_path": str(canonical_path),
        "batch_path": str(batch_path) if batch_path is not None else None,
        "candidate_count": len(population),
        "log_record": log_record,
    }

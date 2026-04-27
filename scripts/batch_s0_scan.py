#!/usr/bin/env python3
"""Batch S0 scan script (offline skeleton version).

This version is intentionally offline.

- Default mode is dry-run and prints a plan only.
- Live mode is a placeholder shell for future client integration.
- All project-relative paths are resolved from BRAIN_PROJECT_ROOT when set,
  otherwise from the repository root derived from this file.
- Platform interaction points are marked with explicit PLACEHOLDER comments.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from dedupe_gate import DedupeGate
from result_ledger import ResultLedger

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ModuleNotFoundError:  # pragma: no cover - requests is only needed for real live runs
    requests = None
    HTTPBasicAuth = None

DEFAULT_TEMPLATES = [
    "ts_rank({field}, {decay})",
    "ts_zscore({field}, {decay})",
    "ts_mean({field}, {decay})",
    "ts_rank(ts_mean({field}, 63), {decay})",
]
DEFAULT_DECAYS = [20, 60, 120]
DEFAULT_NEUTRALIZATIONS = ["", "Market"]
DEFAULT_SORT_WEIGHTS = {
    "alpha_count": 0.5,
    "coverage": 0.3,
    "template_complexity": 0.2,
}

# ---------- Live 模式配置（需用户填写或通过 config.env 提供）----------
API_BASE_URL = None  # from WQ_API_BASE or config.env
AUTH_TOKEN = None  # from WQ_AUTH_TOKEN or config.env
SIMULATION_POLL_INTERVAL = 30  # seconds
SIMULATION_POLL_MAX_RETRIES = 20
DAILY_SIMULATION_LIMIT = 4000
DAILY_SIMULATION_WARN_AT = 3800
PROGRESS_FILE = "runs/evidence/batch_progress.json"
TEST_MODE_DUMMY_ALPHA_ID = "TEST_MODE_DUMMY_ALPHA_ID"
TEST_MODE_DUMMY_SIMULATION_ID = "TEST_MODE_DUMMY_SIMULATION_ID"
LIVE_REQUEST_TIMEOUT_SECONDS = 60
HTTP_429_RETRY_WAIT_SECONDS = 300
HTTP_429_MAX_RETRIES = 3
HTTP_401_REAUTH_RETRIES = 1
DEFAULT_LIVE_SETTINGS = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "MARKET",
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "ON",
    "language": "FASTEXPR",
    "visualization": False,
}
TOP_FIELD_CAP = 2


def get_project_root() -> Path:
    """Resolve the repository root from the explicit environment variable or file path."""
    env_root = os.environ.get("BRAIN_PROJECT_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def resolve_project_path(*parts: str | Path) -> Path:
    return get_project_root().joinpath(*(Path(part) for part in parts))


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_neutralization(value: Any) -> str | None:
    if value in (None, "", "None"):
        return None
    return str(value)


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def field_rank_factor(field_rank: int) -> float:
    if field_rank <= 1:
        return 1.0
    if field_rank == 2:
        return 0.5
    return 0.2


def _first_present(data: Any, keys: Iterable[str]) -> Any:
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[7:].lstrip()
        if "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            continue
        if len(raw_value) >= 2 and raw_value[0] == raw_value[-1] and raw_value[0] in {'"', "'"}:
            raw_value = raw_value[1:-1]
        values[key] = raw_value
    return values


def _load_json_object(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    normalized: dict[str, str] = {}
    for key, value in data.items():
        if value is None:
            continue
        normalized[str(key)] = str(value)
    return normalized


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", []):
            return value
    return None


def _mask_secret(value: Any) -> str:
    if value in (None, ""):
        return "<missing>"
    text = str(value)
    if len(text) <= 8:
        return "***"
    return f"{text[:4]}...{text[-4:]}"


def _normalize_live_neutralization(value: Any) -> str:
    if value in (None, "", "None"):
        return "NONE"
    return str(value).upper()


def _extract_metric_value(data: Any, *keys: str) -> Any:
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def _flatten_result_metrics(result: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for candidate in (result.get("metrics"), result.get("performance"), result.get("result"), result.get("alpha"), result):
        if isinstance(candidate, dict):
            merged.update(candidate)
    return merged


def _normalize_result_status(result: dict[str, Any]) -> str:
    for source in (result, result.get("alpha"), result.get("result"), result.get("performance")):
        if isinstance(source, dict):
            value = _first_present(source, ("status", "state", "submissionStatus", "submission_status"))
            if value:
                return str(value)
    return "UNKNOWN"


def _extract_result_alpha_id(result: dict[str, Any]) -> str:
    alpha_obj = result.get("alpha")
    if isinstance(alpha_obj, dict):
        value = _first_present(alpha_obj, ("id", "alpha_id", "alphaId", "name"))
        if value:
            return str(value)
    elif alpha_obj not in (None, ""):
        return str(alpha_obj)

    value = _first_present(result, ("id", "alpha_id", "alphaId"))
    if value:
        return str(value)
    return "UNKNOWN"


def _build_default_live_record(
    *,
    candidate: dict[str, Any],
    result: dict[str, Any],
    submission_ref: str,
    alpha_id: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    flat_metrics = _flatten_result_metrics(result)
    test_block = result.get("test") if isinstance(result.get("test"), dict) else {}
    train_block = result.get("train") if isinstance(result.get("train"), dict) else {}
    payload = {
        "alpha_id": alpha_id,
        "expression": candidate["expression"],
        "expression_normalized": candidate["expression"],
        "field_name": candidate["field"],
        "source": candidate["source_domain"],
        "stage": "S0-live",
        "decay": as_int(candidate.get("decay"), 0),
        "neutralization": _normalize_live_neutralization(candidate.get("neut")),
        "is_sharpe": as_float(_extract_metric_value(flat_metrics, "sharpe", "Sharpe"), 0.0),
        "is_fitness": as_float(_extract_metric_value(flat_metrics, "fitness", "Fitness"), 0.0),
        "test_sharpe": as_float(
            _extract_metric_value(test_block, "sharpe", "Sharpe", "test_sharpe", "testSharpe")
            or _extract_metric_value(flat_metrics, "test_sharpe", "testSharpe", "testSharpe")
            or _extract_metric_value(flat_metrics, "sharpe", "Sharpe"),
            0.0,
        ),
        "test_fitness": as_float(
            _extract_metric_value(test_block, "fitness", "Fitness", "test_fitness", "testFitness")
            or _extract_metric_value(flat_metrics, "test_fitness", "testFitness", "testFitness")
            or _extract_metric_value(flat_metrics, "fitness", "Fitness"),
            0.0,
        ),
        "turnover": as_float(
            _extract_metric_value(test_block, "turnover", "Turnover", "test_turnover", "testTurnover")
            or _extract_metric_value(flat_metrics, "turnover", "Turnover", "test_turnover", "testTurnover"),
            0.0,
        ),
        "status": _normalize_result_status(result),
        "tags": ["batch_s0", "live"],
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "raw_json": result,
        "capture_id": candidate["candidate_id"],
        "file_path": str(resolve_project_path(PROGRESS_FILE)),
        "test_period": _coalesce(
            _extract_metric_value(result.get("platform_settings"), "testPeriod", "test_period"),
            _extract_metric_value(flat_metrics, "test_period", "testPeriod"),
            _extract_metric_value(train_block, "testPeriod", "test_period"),
        ),
        "region": _coalesce(
            _extract_metric_value(result.get("platform_settings"), "region"),
            config.get("region"),
        ),
        "universe": _coalesce(
            _extract_metric_value(result.get("platform_settings"), "universe"),
            config.get("universe"),
        ),
        "simulation_id": _coalesce(
            _extract_metric_value(result, "simulation_id", "simulationId"),
            submission_ref,
        ),
    }
    return payload


def load_config() -> dict[str, Any]:
    project_root = get_project_root()
    config_path = project_root / "harness/config.env"
    file_values = _read_env_file(config_path)

    def pick(*names: str) -> str | None:
        for name in names:
            env_value = os.environ.get(name)
            if env_value not in (None, ""):
                return env_value
            file_value = file_values.get(name)
            if file_value not in (None, ""):
                return file_value
        return None

    auth_headers = _load_json_object(
        _coalesce(
            pick("WQ_AUTH_HEADERS"),
            pick("AUTH_HEADERS"),
            pick("BRAIN_AUTH_HEADERS"),
        )
    )
    session_cookie = _coalesce(
        pick("WQ_SESSION_COOKIE"),
        pick("SESSION_COOKIE"),
        pick("BRAIN_SESSION_COOKIE"),
    )
    if isinstance(session_cookie, str) and session_cookie.lower().startswith("cookie:"):
        session_cookie = session_cookie.split(":", 1)[1].strip()
    username = _coalesce(
        pick("WQ_USERNAME"),
        pick("BRAIN_USERNAME"),
    )
    password = _coalesce(
        pick("WQ_PASSWORD"),
        pick("BRAIN_PASSWORD"),
    )

    config = {
        "config_path": str(config_path),
        "api_base_url": _coalesce(
            pick("WQ_API_BASE"),
            pick("API_BASE_URL"),
            pick("WQ_API_BASE_URL"),
        ),
        "auth_token": _coalesce(
            pick("WQ_AUTH_TOKEN"),
            pick("AUTH_TOKEN"),
        ),
        "auth_headers": auth_headers,
        "session_cookie": session_cookie,
        "username": username,
        "password": password,
        "region": _coalesce(
            pick("WQ_REGION"),
            pick("REGION"),
            "USA",
        ),
        "universe": _coalesce(
            pick("WQ_UNIVERSE"),
            pick("UNIVERSE"),
            "TOP3000",
        ),
    }

    if config["auth_token"]:
        config["auth_mode"] = "token"
    elif config["auth_headers"]:
        config["auth_mode"] = "headers"
    elif config["session_cookie"]:
        config["auth_mode"] = "cookie"
    elif config["username"] and config["password"]:
        config["auth_mode"] = "basic"
    else:
        config["auth_mode"] = "none"

    missing: list[str] = []
    if not config["api_base_url"]:
        missing.append("API_BASE_URL")
    if not (
        config["auth_token"]
        or config["auth_headers"]
        or config["session_cookie"]
        or (config["username"] and config["password"])
    ):
        missing.append("AUTHENTICATION_METHOD")
    config["missing_config"] = missing
    config["has_effective_auth"] = bool(
        config["auth_token"]
        or config["auth_headers"]
        or config["session_cookie"]
        or (config["username"] and config["password"])
    )
    return config


def default_progress_state() -> dict[str, Any]:
    return {
        "version": 1,
        "updated_at": None,
        "completed_alpha_ids": [],
        "completed_candidate_ids": [],
        "records": [],
        "daily_submissions": {},
    }


def load_progress(path: str | Path | None = None) -> dict[str, Any]:
    progress_path = Path(path or PROGRESS_FILE)
    if not progress_path.is_absolute():
        progress_path = resolve_project_path(progress_path)
    if not progress_path.exists():
        return default_progress_state()

    try:
        payload = json.loads(progress_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default_progress_state()

    if not isinstance(payload, dict):
        return default_progress_state()

    progress = default_progress_state()
    progress.update({key: value for key, value in payload.items() if key in progress})
    records = payload.get("records")
    if isinstance(records, list):
        progress["records"] = [item for item in records if isinstance(item, dict)]

    completed_alpha_ids = payload.get("completed_alpha_ids")
    if isinstance(completed_alpha_ids, list):
        progress["completed_alpha_ids"] = [str(item) for item in completed_alpha_ids if item not in (None, "")]

    completed_candidate_ids = payload.get("completed_candidate_ids")
    if isinstance(completed_candidate_ids, list):
        progress["completed_candidate_ids"] = [str(item) for item in completed_candidate_ids if item not in (None, "")]

    daily = payload.get("daily_submissions")
    if isinstance(daily, dict):
        progress["daily_submissions"] = {str(key): as_int(value, 0) for key, value in daily.items()}

    derived_completed_alpha_ids: list[str] = []
    derived_completed_candidate_ids: list[str] = []
    for record in progress["records"]:
        status = str(record.get("status") or "").lower()
        candidate_id = record.get("candidate_id")
        alpha_id = record.get("alpha_id")
        if status == "completed":
            if candidate_id not in (None, ""):
                derived_completed_candidate_ids.append(str(candidate_id))
            if alpha_id not in (None, ""):
                derived_completed_alpha_ids.append(str(alpha_id))

    if derived_completed_alpha_ids:
        progress["completed_alpha_ids"] = dedupe_preserve_order(
            [str(item) for item in progress["completed_alpha_ids"]] + derived_completed_alpha_ids
        )
    if derived_completed_candidate_ids:
        progress["completed_candidate_ids"] = dedupe_preserve_order(
            [str(item) for item in progress["completed_candidate_ids"]] + derived_completed_candidate_ids
        )

    return progress


def save_progress(
    progress: dict[str, Any],
    path: str | Path | None = None,
    *,
    test_mode: bool = False,
    logger: logging.Logger | None = None,
) -> Path:
    progress_path = Path(path or PROGRESS_FILE)
    if not progress_path.is_absolute():
        progress_path = resolve_project_path(progress_path)

    records = progress.setdefault("records", [])
    if not isinstance(records, list):
        records = []
        progress["records"] = records

    completed_alpha_ids: list[str] = []
    completed_candidate_ids: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        status = str(record.get("status") or "").lower()
        candidate_id = record.get("candidate_id")
        alpha_id = record.get("alpha_id")
        if status == "completed":
            if candidate_id not in (None, ""):
                completed_candidate_ids.append(str(candidate_id))
            if alpha_id not in (None, ""):
                completed_alpha_ids.append(str(alpha_id))

    progress["completed_alpha_ids"] = dedupe_preserve_order(completed_alpha_ids)
    progress["completed_candidate_ids"] = dedupe_preserve_order(completed_candidate_ids)
    progress["updated_at"] = datetime.now().isoformat(timespec="seconds")

    if test_mode:
        latest_record = records[-1] if records else {}
        summary = {
            "records": len(records),
            "completed_alpha_ids": len(progress["completed_alpha_ids"]),
            "completed_candidate_ids": len(progress["completed_candidate_ids"]),
            "path": str(progress_path),
            "mode": "test-mode-print-only",
            "last_record": {
                "candidate_id": str(latest_record.get("candidate_id") or ""),
                "status": str(latest_record.get("status") or ""),
                "alpha_id": str(latest_record.get("alpha_id") or ""),
                "submission_id": str(latest_record.get("submission_id") or ""),
            }
            if isinstance(latest_record, dict)
            else {},
        }
        if logger is not None:
            logger.info("TEST MODE: progress update would be saved: %s", json.dumps(summary, ensure_ascii=False, sort_keys=True))
        else:
            print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return progress_path

    ensure_parent_dir(progress_path)
    progress_path.write_text(json.dumps(progress, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    if logger is not None:
        logger.info("progress saved path=%s records=%d", progress_path, len(records))
    return progress_path


def count_daily_submissions(progress: dict[str, Any], day_key: str | None = None) -> int:
    target_day = day_key or datetime.now().date().isoformat()
    count = 0
    for record in progress.get("records", []):
        if not isinstance(record, dict):
            continue
        submitted_at = str(record.get("submitted_at") or record.get("updated_at") or record.get("timestamp") or "")
        if not submitted_at.startswith(target_day):
            continue
        if record.get("submission_id"):
            count += 1
    return count


def upsert_progress_record(progress: dict[str, Any], record: dict[str, Any]) -> None:
    records = progress.setdefault("records", [])
    if not isinstance(records, list):
        progress["records"] = [record]
        return

    candidate_id = record.get("candidate_id")
    submission_id = record.get("submission_id")
    alpha_id = record.get("alpha_id")
    keys = [str(item) for item in (candidate_id, submission_id, alpha_id) if item not in (None, "")]

    for index, existing in enumerate(records):
        if not isinstance(existing, dict):
            continue
        existing_keys = [
            str(item)
            for item in (
                existing.get("candidate_id"),
                existing.get("submission_id"),
                existing.get("alpha_id"),
            )
            if item not in (None, "")
        ]
        if keys and existing_keys and any(key in existing_keys for key in keys):
            records[index] = record
            return

    records.append(record)


def progress_completed_candidate_ids(progress: dict[str, Any]) -> set[str]:
    completed = set()
    for record in progress.get("records", []):
        if not isinstance(record, dict):
            continue
        if str(record.get("status") or "").lower() != "completed":
            continue
        candidate_id = record.get("candidate_id")
        if candidate_id not in (None, ""):
            completed.add(str(candidate_id))
    return completed


def progress_active_candidate_ids(progress: dict[str, Any]) -> set[str]:
    active = set(progress_completed_candidate_ids(progress))
    for record in progress.get("records", []):
        if not isinstance(record, dict):
            continue
        if str(record.get("status") or "").lower() != "submitted":
            continue
        candidate_id = record.get("candidate_id")
        if candidate_id not in (None, ""):
            active.add(str(candidate_id))
    return active


def progress_pending_records(progress: dict[str, Any]) -> list[dict[str, Any]]:
    pending: list[dict[str, Any]] = []
    for record in progress.get("records", []):
        if not isinstance(record, dict):
            continue
        if str(record.get("status") or "").lower() == "submitted" and record.get("submission_id"):
            pending.append(record)
    return pending


def _candidate_progress_record(
    candidate: dict[str, Any],
    *,
    status: str,
    submission_id: str | None = None,
    alpha_id: str | None = None,
    result: dict[str, Any] | None = None,
    error: str | None = None,
    submitted_at: str | None = None,
    completed_at: str | None = None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    record = {
        "candidate_id": candidate.get("candidate_id"),
        "batch_id": candidate.get("batch_id"),
        "batch_source": candidate.get("batch_source"),
        "source_report": candidate.get("source_report"),
        "field": candidate.get("field"),
        "source_domain": candidate.get("source_domain"),
        "type": candidate.get("type"),
        "coverage": candidate.get("coverage"),
        "user_count": candidate.get("user_count"),
        "alpha_count": candidate.get("alpha_count"),
        "priority": candidate.get("priority"),
        "template": candidate.get("template"),
        "template_index": candidate.get("template_index"),
        "template_complexity": candidate.get("template_complexity"),
        "decay": candidate.get("decay"),
        "neut": candidate.get("neut"),
        "expression": candidate.get("expression"),
        "status": status,
        "submission_id": submission_id,
        "alpha_id": alpha_id,
        "submitted_at": submitted_at,
        "completed_at": completed_at,
        "updated_at": updated_at or completed_at or submitted_at or datetime.now().isoformat(timespec="seconds"),
    }

    if result is not None:
        flat_metrics = _flatten_result_metrics(result)
        test_block = result.get("test") if isinstance(result.get("test"), dict) else {}
        record["result_status"] = _normalize_result_status(result)
        record["test_sharpe"] = as_float(
            _extract_metric_value(test_block, "sharpe", "Sharpe", "test_sharpe", "testSharpe")
            or _extract_metric_value(flat_metrics, "test_sharpe", "testSharpe", "sharpe", "Sharpe"),
            0.0,
        )
        record["test_fitness"] = as_float(
            _extract_metric_value(test_block, "fitness", "Fitness", "test_fitness", "testFitness")
            or _extract_metric_value(flat_metrics, "test_fitness", "testFitness", "fitness", "Fitness"),
            0.0,
        )
        record["turnover"] = as_float(
            _extract_metric_value(test_block, "turnover", "Turnover", "test_turnover", "testTurnover")
            or _extract_metric_value(flat_metrics, "turnover", "Turnover", "test_turnover", "testTurnover"),
            0.0,
        )
        record["raw_json"] = result

    if error is not None:
        record["error"] = error

    return record


def _candidate_from_progress_record(
    record: dict[str, Any],
    candidate_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    candidate_id = str(record.get("candidate_id") or "")
    candidate = dict(candidate_lookup.get(candidate_id, {}))
    if candidate:
        return candidate

    expression = record.get("expression")
    field = record.get("field")
    if expression in (None, "") or field in (None, ""):
        return None

    reconstructed = {
        "candidate_id": candidate_id or f"resume:{field}",
        "batch_id": record.get("batch_id"),
        "batch_source": record.get("batch_source"),
        "source_report": record.get("source_report"),
        "field": field,
        "source_domain": record.get("source_domain") or record.get("batch_source") or "",
        "type": record.get("type") or "",
        "coverage": record.get("coverage") or 0.0,
        "user_count": record.get("user_count") or 0,
        "alpha_count": record.get("alpha_count") or 0,
        "priority": record.get("priority") or "medium",
        "description": record.get("description") or "",
        "template": record.get("template") or "",
        "template_index": record.get("template_index") or 0,
        "template_complexity": record.get("template_complexity") or 2,
        "decay": record.get("decay") or 0,
        "neut": normalize_neutralization(record.get("neut")),
        "expression": expression,
    }
    return reconstructed


def _is_auth_failure_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "authentication failed" in message or "auth failed" in message or "reauth" in message


def ledger_has_alpha_id(ledger: ResultLedger, alpha_id: str) -> bool:
    try:
        row = ledger.conn.execute("SELECT 1 FROM simulations WHERE alpha_id = ? LIMIT 1", (alpha_id,)).fetchone()
    except sqlite3.DatabaseError:
        return False
    return row is not None


def _build_request_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    settings = dict(DEFAULT_LIVE_SETTINGS)
    settings["neutralization"] = _normalize_live_neutralization(candidate.get("neut"))
    settings["decay"] = as_int(candidate.get("decay"), 0)
    payload = {
        "type": "REGULAR",
        "settings": settings,
        "regular": candidate["expression"],
    }
    return payload


def _resolve_api_base_url(config: dict[str, Any]) -> str | None:
    return _coalesce(API_BASE_URL, config.get("api_base_url"))


def _request_url(api_base_url: str | None, suffix: str) -> str:
    if not api_base_url:
        return f"<missing API_BASE_URL>{suffix}"
    return f"{api_base_url.rstrip('/')}{suffix}"


def _initialize_live_runtime(scanner: "BatchS0Scanner", config: dict[str, Any], progress: dict[str, Any], ledger: ResultLedger | None) -> None:
    LIVE_RUNTIME.clear()
    LIVE_RUNTIME.update(
        {
            "scanner": scanner,
            "config": config,
            "progress": progress,
            "ledger": ledger,
            "session": None,
            "current_candidate": None,
            "submission_locations": {},
            "reauth_attempts": 0,
            "test_mode": scanner.test_mode,
            "logger": scanner.logger,
            "progress_path": scanner.progress_path,
            "ledger_path": scanner.ledger_path,
        }
    )


LIVE_RUNTIME: dict[str, Any] = {}


def _live_logger() -> logging.Logger:
    logger = LIVE_RUNTIME.get("logger")
    if isinstance(logger, logging.Logger):
        return logger
    return logging.getLogger("batch_s0_scan.live")


def _ensure_requests_available() -> None:
    if requests is None or HTTPBasicAuth is None:
        raise RuntimeError("requests is required for live mode. Install it in the active Python environment.")


def _build_live_session(config: dict[str, Any]) -> "requests.Session":
    _ensure_requests_available()
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )

    auth_headers = config.get("auth_headers")
    if isinstance(auth_headers, dict):
        session.headers.update(auth_headers)

    auth_token = config.get("auth_token")
    if auth_token:
        session.headers["Authorization"] = f"Bearer {auth_token}"

    session_cookie = config.get("session_cookie")
    if session_cookie:
        session.headers["Cookie"] = str(session_cookie)

    username = config.get("username")
    password = config.get("password")
    if not auth_token and not auth_headers and not session_cookie and username and password:
        api_base_url = _resolve_api_base_url(config)
        if not api_base_url:
            raise RuntimeError("API_BASE_URL is required before username/password authentication can be used.")
        auth_url = _request_url(api_base_url, "/authentication")
        response = session.post(auth_url, timeout=LIVE_REQUEST_TIMEOUT_SECONDS, auth=HTTPBasicAuth(str(username), str(password)))
        if response.status_code >= 400:
            raise RuntimeError(f"authentication failed with status {response.status_code}: {response.text[:200]}")

    return session


def _refresh_live_session() -> "requests.Session":
    config = LIVE_RUNTIME.get("config")
    if not isinstance(config, dict):
        raise RuntimeError("live runtime is not initialized")
    session = _build_live_session(config)
    LIVE_RUNTIME["session"] = session
    return session


def _sleep_live(seconds: int, reason: str) -> None:
    logger = _live_logger()
    if LIVE_RUNTIME.get("test_mode"):
        logger.info("TEST MODE: skipping sleep %ss (%s)", seconds, reason)
        return
    time.sleep(seconds)


def _resolve_submission_ref_to_url(submission_ref: str) -> str:
    config = LIVE_RUNTIME.get("config")
    api_base_url = _resolve_api_base_url(config if isinstance(config, dict) else {})
    if submission_ref.startswith("http://") or submission_ref.startswith("https://"):
        return submission_ref
    if submission_ref.startswith("/"):
        return _request_url(api_base_url, submission_ref)
    if api_base_url:
        return _request_url(api_base_url, f"/simulations/{submission_ref}")
    return submission_ref


def _response_body_preview(response: Any, limit: int = 300) -> str:
    text = getattr(response, "text", "")
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def _build_masked_headers(config: dict[str, Any]) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    auth_headers = config.get("auth_headers")
    if isinstance(auth_headers, dict):
        headers.update(auth_headers)
    auth_token = config.get("auth_token")
    if auth_token:
        headers["Authorization"] = f"Bearer {_mask_secret(auth_token)}"
    session_cookie = config.get("session_cookie")
    if session_cookie:
        headers["Cookie"] = _mask_secret(session_cookie)

    sensitive_keys = {"authorization", "cookie", "x-api-key", "api-key", "token", "auth", "auth-token"}
    for key in list(headers.keys()):
        normalized_key = str(key).lower()
        if normalized_key in sensitive_keys or "authorization" in normalized_key or "cookie" in normalized_key or "token" in normalized_key:
            headers[key] = _mask_secret(headers[key])
    return headers


def _print_test_request(method: str, url: str, headers: dict[str, Any], body: dict[str, Any]) -> None:
    logger = _live_logger()
    logger.info("[TEST MODE] request method=%s url=%s", method, url)
    logger.info("[TEST MODE] request headers=%s", json.dumps(headers, ensure_ascii=False, sort_keys=True))
    logger.info("[TEST MODE] request body=%s", json.dumps(body, ensure_ascii=False, sort_keys=True))


def _extract_submission_ref(response: Any) -> str | None:
    location = getattr(response, "headers", {}).get("Location")
    if location:
        return str(location)
    try:
        payload = response.json()
    except Exception:
        payload = None
    if isinstance(payload, dict):
        value = _first_present(payload, ("alpha_id", "alphaId", "id", "simulation_id", "simulationId"))
        if value:
            return str(value)
    return None


def submit_simulation(expression: str, neutralization: Any) -> str | None:
    runtime = LIVE_RUNTIME
    config = runtime.get("config")
    logger = _live_logger()
    if not isinstance(config, dict):
        raise RuntimeError("live runtime is not initialized")

    candidate = runtime.get("current_candidate")
    if not isinstance(candidate, dict):
        candidate = {"expression": expression, "neut": neutralization, "decay": 0, "candidate_id": "manual"}

    api_base_url = _resolve_api_base_url(config)
    url = _request_url(api_base_url, "/simulations")
    payload = _build_request_payload(candidate)
    payload["regular"] = expression

    if runtime.get("test_mode"):
        masked_headers = _build_masked_headers(config)
        _print_test_request("POST", url, masked_headers, payload)
        test_submission_ref = f"{TEST_MODE_DUMMY_ALPHA_ID}:{candidate.get('candidate_id') or 'candidate'}"
        runtime.setdefault("submission_locations", {})[test_submission_ref] = test_submission_ref
        return test_submission_ref

    if not api_base_url:
        raise RuntimeError("API_BASE_URL is required for live submissions")
    _ensure_requests_available()
    session = runtime.get("session")
    if session is None:
        session = _refresh_live_session()

    reauth_attempted = False
    retry_429_count = 0
    while True:
        response = session.post(url, json=payload, timeout=LIVE_REQUEST_TIMEOUT_SECONDS)
        status_code = response.status_code

        if status_code == 401:
            if reauth_attempted:
                raise RuntimeError(f"authentication failed after retry: {status_code} {_response_body_preview(response)}")
            reauth_attempted = True
            runtime["session"] = _refresh_live_session()
            session = runtime["session"]
            continue

        if status_code == 429:
            retry_429_count += 1
            if retry_429_count > HTTP_429_MAX_RETRIES:
                logger.error("submission hit 429 too many times candidate=%s", candidate.get("candidate_id"))
                return None
            retry_after = response.headers.get("Retry-After")
            wait_seconds = HTTP_429_RETRY_WAIT_SECONDS
            if retry_after:
                try:
                    wait_seconds = max(wait_seconds, int(float(retry_after)))
                except ValueError:
                    pass
            logger.warning(
                "submission 429 candidate=%s retry=%d wait_seconds=%d",
                candidate.get("candidate_id"),
                retry_429_count,
                wait_seconds,
            )
            _sleep_live(wait_seconds, "HTTP 429 retry")
            continue

        if status_code >= 400:
            raise RuntimeError(
                f"submission failed status={status_code} candidate={candidate.get('candidate_id')} body={_response_body_preview(response)}"
            )

        submission_ref = _extract_submission_ref(response)
        if not submission_ref:
            logger.warning(
                "submission response missing Location/id candidate=%s body=%s",
                candidate.get("candidate_id"),
                _response_body_preview(response),
            )
            submission_ref = f"{TEST_MODE_DUMMY_SIMULATION_ID}:{candidate.get('candidate_id') or 'candidate'}"
        runtime.setdefault("submission_locations", {})[submission_ref] = submission_ref
        return submission_ref


def _result_has_ready_metrics(result: dict[str, Any]) -> bool:
    flat_metrics = _flatten_result_metrics(result)
    for key in ("test_sharpe", "testSharpe", "sharpe", "fitness", "turnover"):
        value = flat_metrics.get(key)
        if value not in (None, ""):
            return True
    return isinstance(result.get("test"), dict) or isinstance(result.get("metrics"), dict) or isinstance(result.get("performance"), dict)


def poll_result(alpha_id: str) -> dict[str, Any] | None:
    runtime = LIVE_RUNTIME
    config = runtime.get("config")
    logger = _live_logger()
    if not isinstance(config, dict):
        raise RuntimeError("live runtime is not initialized")

    if runtime.get("test_mode"):
        candidate = runtime.get("current_candidate") if isinstance(runtime.get("current_candidate"), dict) else {}
        test_result = {
            "TEST_MODE_DUMMY": True,
            "status": "TEST_MODE_DUMMY",
            "alpha": {
                "id": alpha_id,
                "alpha_id": alpha_id,
            },
            "metrics": {
                "sharpe": 0.42,
                "fitness": 0.24,
                "turnover": 0.12,
            },
            "test": {
                "sharpe": 0.42,
                "fitness": 0.24,
                "turnover": 0.12,
            },
            "expression": candidate.get("expression"),
            "candidate_id": candidate.get("candidate_id"),
        }
        logger.info("[TEST MODE] poll_result alpha_id=%s -> TEST_MODE_DUMMY", alpha_id)
        return test_result

    _ensure_requests_available()
    session = runtime.get("session")
    if session is None:
        session = _refresh_live_session()

    submission_ref = str(alpha_id)
    url = _resolve_submission_ref_to_url(submission_ref)
    reauth_attempted = False
    retry_429_count = 0

    for attempt in range(1, SIMULATION_POLL_MAX_RETRIES + 1):
        response = session.get(url, timeout=LIVE_REQUEST_TIMEOUT_SECONDS)
        status_code = response.status_code

        if status_code == 401:
            if reauth_attempted:
                raise RuntimeError(f"poll authentication failed after retry: {status_code} {_response_body_preview(response)}")
            reauth_attempted = True
            runtime["session"] = _refresh_live_session()
            session = runtime["session"]
            continue

        if status_code == 429:
            retry_429_count += 1
            if retry_429_count > HTTP_429_MAX_RETRIES:
                logger.error("poll hit 429 too many times alpha_id=%s", alpha_id)
                return None
            retry_after = response.headers.get("Retry-After")
            wait_seconds = HTTP_429_RETRY_WAIT_SECONDS
            if retry_after:
                try:
                    wait_seconds = max(wait_seconds, int(float(retry_after)))
                except ValueError:
                    pass
            logger.warning(
                "poll 429 alpha_id=%s retry=%d wait_seconds=%d attempt=%d",
                alpha_id,
                retry_429_count,
                wait_seconds,
                attempt,
            )
            _sleep_live(wait_seconds, "HTTP 429 poll retry")
            continue

        if status_code in (202, 204):
            _sleep_live(SIMULATION_POLL_INTERVAL, "poll pending response")
            continue

        if status_code >= 400:
            raise RuntimeError(f"poll failed status={status_code} alpha_id={alpha_id} body={_response_body_preview(response)}")

        try:
            payload = response.json()
        except Exception:
            payload = {"status": getattr(response, "text", ""), "raw_text": getattr(response, "text", "")}

        if not isinstance(payload, dict):
            payload = {"raw_payload": payload}

        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                retry_after_value = float(retry_after)
            except ValueError:
                retry_after_value = 0.0
            if retry_after_value > 0:
                _sleep_live(int(retry_after_value), "Retry-After poll delay")
                continue

        status = str(_normalize_result_status(payload)).lower()
        if status in {"queued", "pending", "processing", "running", "in_progress"} and attempt < SIMULATION_POLL_MAX_RETRIES:
            _sleep_live(SIMULATION_POLL_INTERVAL, f"poll status={status}")
            continue

        if not _result_has_ready_metrics(payload) and attempt < SIMULATION_POLL_MAX_RETRIES:
            _sleep_live(SIMULATION_POLL_INTERVAL, "poll missing ready metrics")
            continue

        return payload

    logger.warning("poll timed out alpha_id=%s after %d retries", alpha_id, SIMULATION_POLL_MAX_RETRIES)
    return None


def write_result_to_ledger(candidate: dict[str, Any], submission_ref: str, result: dict[str, Any]) -> int | None:
    runtime = LIVE_RUNTIME
    logger = _live_logger()
    config = runtime.get("config")
    ledger = runtime.get("ledger")
    if not isinstance(config, dict):
        raise RuntimeError("live runtime is not initialized")

    alpha_id = _extract_result_alpha_id(result)
    if alpha_id in (None, "", "UNKNOWN"):
        alpha_id = submission_ref

    payload = _build_default_live_record(
        candidate=candidate,
        result=result,
        submission_ref=submission_ref,
        alpha_id=str(alpha_id),
        config=config,
    )
    payload["raw_json"] = result

    if runtime.get("test_mode"):
        logger.info("[TEST MODE] would insert result into ledger: %s", json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return None

    if not isinstance(ledger, ResultLedger):
        raise RuntimeError("result ledger is not initialized")

    if ledger_has_alpha_id(ledger, str(alpha_id)):
        logger.info("ledger already contains alpha_id=%s, skipping duplicate insert", alpha_id)
        return None

    row_id = ledger.insert_result(payload)
    logger.info("ledger insert complete row_id=%s alpha_id=%s", row_id, alpha_id)
    return row_id


class BatchS0Scanner:
    def __init__(
        self,
        fields_path: str | Path,
        top: int = 3,
        max_simulations: int = 50,
        run_mode: str = "dry",
        test_mode: bool = False,
    ) -> None:
        self.project_root = get_project_root()
        self.fields_path = self._resolve_path(fields_path)
        self.top = top
        self.max_simulations = max_simulations
        self.run_mode = run_mode
        self.test_mode = test_mode
        self.ledger_path = self._resolve_path("runs/evidence/result_ledger.db")
        self.log_path = self._resolve_path("runs/evidence/batch_s0_scan.log")
        self.progress_path = self._resolve_path(PROGRESS_FILE)
        self.templates = list(DEFAULT_TEMPLATES)
        self.decays = list(DEFAULT_DECAYS)
        self.neutralizations = list(DEFAULT_NEUTRALIZATIONS)
        self.sort_weights = dict(DEFAULT_SORT_WEIGHTS)
        self.scan_spec: dict[str, Any] = {}
        self.logger = self._configure_logging()

    def _resolve_path(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return self.project_root / candidate

    def _configure_logging(self) -> logging.Logger:
        ensure_parent_dir(self.log_path)
        logger = logging.getLogger(f"batch_s0_scan.{id(self)}")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
        logger.propagate = False
        return logger

    def load_fields(self) -> dict[str, Any]:
        path = self.fields_path
        if not path.exists():
            raise FileNotFoundError(f"field candidate file not found: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("field candidate file must contain a JSON object")
        fields = payload.get("fields")
        if not isinstance(fields, list):
            raise ValueError("field candidate file must contain a fields array")

        self.scan_spec = payload
        self.templates = dedupe_preserve_order(
            self._override_list(payload.get("template_overrides"), DEFAULT_TEMPLATES)
        )
        params = payload.get("param_overrides") if isinstance(payload.get("param_overrides"), dict) else {}
        self.decays = [as_int(item) for item in params.get("decays", DEFAULT_DECAYS)] or list(DEFAULT_DECAYS)
        self.neutralizations = [normalize_neutralization(item) or "" for item in params.get("neutralizations", DEFAULT_NEUTRALIZATIONS)] or list(DEFAULT_NEUTRALIZATIONS)
        sort_weights = params.get("sort_weights") if isinstance(params.get("sort_weights"), dict) else {}
        merged_weights = dict(DEFAULT_SORT_WEIGHTS)
        for key, value in sort_weights.items():
            if key in merged_weights:
                merged_weights[key] = as_float(value, merged_weights[key])
        self.sort_weights = merged_weights
        return payload

    def _override_list(self, override_value: Any, default_values: list[str]) -> list[str]:
        if isinstance(override_value, list) and override_value:
            return [str(item) for item in override_value]
        return list(default_values)

    def ledger_row_count(self) -> int:
        if not self.ledger_path.exists():
            return 0
        try:
            with sqlite3.connect(str(self.ledger_path)) as connection:
                row = connection.execute("SELECT COUNT(*) FROM simulations").fetchone()
        except sqlite3.DatabaseError:
            return 0
        if not row:
            return 0
        return as_int(row[0], 0)

    def _template_complexity(self, template: str) -> int:
        return 1 if template.count("(") <= 1 else 2

    def _field_templates(self, field: dict[str, Any]) -> list[str]:
        override = field.get("template_overrides")
        if isinstance(override, list) and override:
            return [str(item) for item in override]
        return list(self.templates)

    def _field_decays(self, field: dict[str, Any]) -> list[int]:
        override = field.get("param_overrides")
        if isinstance(override, dict) and isinstance(override.get("decays"), list) and override.get("decays"):
            return [as_int(item) for item in override["decays"]]
        return list(self.decays)

    def _field_neutralizations(self, field: dict[str, Any]) -> list[str | None]:
        override = field.get("param_overrides")
        if isinstance(override, dict) and isinstance(override.get("neutralizations"), list) and override.get("neutralizations"):
            return [normalize_neutralization(item) for item in override["neutralizations"]]
        return [normalize_neutralization(item) for item in self.neutralizations]

    def generate_candidates(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        batch_id = str(payload.get("batch_id") or "batch")
        batch_source = str(payload.get("source") or "batch_s0_scan")
        source_report = str(payload.get("source_report") or "")

        for field in payload.get("fields", []):
            if not isinstance(field, dict):
                continue
            field_name = str(field.get("name") or "").strip()
            if not field_name:
                continue
            field_source_domain = str(field.get("source_domain") or batch_source)
            field_type = str(field.get("type") or "")
            coverage = as_float(field.get("coverage"), 0.0)
            user_count = as_int(field.get("user_count"), 0)
            alpha_count = as_int(field.get("alpha_count"), 0)
            priority = str(field.get("priority") or "medium")
            description = str(field.get("description") or "")
            templates = self._field_templates(field)
            decays = self._field_decays(field)
            neutralizations = self._field_neutralizations(field)

            for template_index, template in enumerate(templates, start=1):
                template_complexity = self._template_complexity(template)
                for decay in decays:
                    expression = template.format(field=field_name, decay=decay)
                    for neutralization in neutralizations:
                        neutralization_label = neutralization if neutralization is not None else "None"
                        candidate = {
                            "candidate_id": f"{batch_id}:{field_name}:{template_index}:{decay}:{neutralization_label}",
                            "batch_id": batch_id,
                            "batch_source": batch_source,
                            "source_report": source_report,
                            "field": field_name,
                            "source_domain": field_source_domain,
                            "type": field_type,
                            "coverage": coverage,
                            "user_count": user_count,
                            "alpha_count": alpha_count,
                            "priority": priority,
                            "description": description,
                            "template": template,
                            "template_index": template_index,
                            "template_complexity": template_complexity,
                            "decay": decay,
                            "neut": neutralization,
                            "expression": expression,
                        }
                        candidates.append(candidate)
        return candidates

    def check_duplicates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        gate = DedupeGate(self.ledger_path)
        filtered: list[dict[str, Any]] = []
        duplicate_count = 0
        warning_count = 0

        for candidate in candidates:
            result = gate.check(
                candidate["expression"],
                candidate["field"],
                candidate["source_domain"],
            )
            candidate = dict(candidate)
            candidate["dedupe_result"] = result
            candidate["dedupe_is_duplicate"] = bool(result.get("is_duplicate"))
            candidate["dedupe_similarity_score"] = as_float(result.get("similarity_score"), 0.0)
            candidate["dedupe_match_level"] = result.get("match_level")

            if result.get("warning"):
                warning_count += 1
                self.logger.warning(
                    "similarity warning candidate=%s score=%.3f match_level=%s",
                    candidate["candidate_id"],
                    candidate["dedupe_similarity_score"],
                    candidate["dedupe_match_level"],
                )

            if candidate["dedupe_is_duplicate"]:
                duplicate_count += 1
                self.logger.info(
                    "duplicate skipped candidate=%s match_level=%s score=%.3f",
                    candidate["candidate_id"],
                    candidate["dedupe_match_level"],
                    candidate["dedupe_similarity_score"],
                )
                continue

            filtered.append(candidate)

        self.logger.info(
            "dedupe summary total=%d duplicates=%d warnings=%d remaining=%d",
            len(candidates),
            duplicate_count,
            warning_count,
            len(filtered),
        )
        return filtered

    def sort_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        weighted: list[dict[str, Any]] = []
        for candidate in candidates:
            alpha_count = max(as_int(candidate.get("alpha_count"), 0), 0)
            coverage = max(min(as_float(candidate.get("coverage"), 0.0), 1.0), 0.0)
            template_complexity = as_int(candidate.get("template_complexity"), 2)
            complexity_score = 1.0 if template_complexity == 1 else 0.5
            raw_score = (
                self.sort_weights["alpha_count"] * (1.0 / (alpha_count + 1))
                + self.sort_weights["coverage"] * coverage
                + self.sort_weights["template_complexity"] * complexity_score
            )
            record = dict(candidate)
            record["final_score"] = round(raw_score, 6)
            record["complexity_score"] = complexity_score
            weighted.append(record)

        weighted.sort(
            key=lambda item: (
                int(item.get("template_complexity", 2)),
                -float(item["final_score"]),
                -float(item.get("coverage", 0.0)),
                int(item.get("alpha_count", 0)),
                str(item.get("candidate_id", "")),
            )
        )

        field_counts: dict[str, int] = {}
        diversified: list[tuple[float, dict[str, Any]]] = []
        for candidate in weighted:
            field = str(candidate.get("field") or "")
            field_rank = field_counts.get(field, 0) + 1
            field_counts[field] = field_rank
            adjusted_score = float(candidate["final_score"]) * field_rank_factor(field_rank)
            diversified.append((adjusted_score, candidate))

        diversified.sort(
            key=lambda item: (
                -item[0],
                int(item[1].get("template_complexity", 2)),
                -float(item[1]["final_score"]),
                -float(item[1].get("coverage", 0.0)),
                int(item[1].get("alpha_count", 0)),
                str(item[1].get("candidate_id", "")),
            )
        )
        return [candidate for _, candidate in diversified]

    def _select_top_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        field_counts: dict[str, int] = {}

        for candidate in candidates:
            field = str(candidate.get("field") or "")
            if field_counts.get(field, 0) >= TOP_FIELD_CAP:
                continue
            selected.append(candidate)
            field_counts[field] = field_counts.get(field, 0) + 1
            if len(selected) >= self.top:
                break

        return selected

    def print_dry_run_plan(self, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        planned = candidates[: self.max_simulations]
        top_recommendations = self._select_top_candidates(planned)

        self.logger.info("dry-run plan start")
        self.logger.info("project_root=%s", self.project_root)
        self.logger.info("fields_file=%s", self.fields_path)
        self.logger.info("ledger_rows=%d", self.ledger_row_count())
        self.logger.info("templates=%s", ", ".join(self.templates))
        self.logger.info("decays=%s", ", ".join(str(item) for item in self.decays))
        self.logger.info(
            "neutralizations=%s",
            ", ".join(item if item else "None" for item in self.neutralizations),
        )
        self.logger.info("planned_candidates=%d", len(planned))
        self.logger.info("top_recommendations=%d", len(top_recommendations))
        self.logger.info("top_field_cap=%d", TOP_FIELD_CAP)
        self.logger.info("--- ranked plan ---")
        self.logger.info(
            "%-4s %-28s %-5s %-10s %-4s %-8s %-6s %-11s %-9s %s",
            "rank",
            "field",
            "decay",
            "neutralization",
            "tmp",
            "alpha_cnt",
            "coverage",
            "complexity",
            "score",
            "expression",
        )
        for index, candidate in enumerate(planned, start=1):
            self.logger.info(
                "%-4d %-28s %-5s %-10s %-4d %-8d %-6.3f %-11d %-9.3f %s",
                index,
                candidate["field"][:28],
                candidate["decay"],
                (candidate["neut"] if candidate["neut"] is not None else "None")[:10],
                candidate["template_index"],
                candidate["alpha_count"],
                candidate["coverage"],
                candidate["template_complexity"],
                candidate.get("final_score", 0.0),
                candidate["expression"],
        )
        if top_recommendations:
            self.logger.info("--- top %d (field-capped) ---", self.top)
            for index, candidate in enumerate(top_recommendations, start=1):
                self.logger.info(
                    "top=%d candidate=%s score=%.3f expr=%s",
                    index,
                    candidate["candidate_id"],
                    candidate["final_score"],
                    candidate["expression"],
                )
        self.logger.info("dry-run plan end")
        return {
            "mode": "dry",
            "planned": len(planned),
            "top": len(top_recommendations),
            "total_after_dedupe": len(candidates),
        }

    def run_live(self, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        planned = list(candidates[: self.max_simulations])
        candidate_lookup = {str(candidate.get("candidate_id") or ""): candidate for candidate in planned if candidate.get("candidate_id") not in (None, "")}
        config = load_config()
        progress = load_progress(self.progress_path)
        missing_config = list(config.get("missing_config", []))
        ledger: ResultLedger | None = None

        if not self.test_mode:
            if not config.get("api_base_url"):
                raise RuntimeError("API_BASE_URL is required for live mode")
            if not config.get("has_effective_auth"):
                raise RuntimeError("No authentication method configured for live mode")
            ledger = ResultLedger(self.ledger_path)

        _initialize_live_runtime(self, config, progress, ledger)
        day_key = datetime.now().date().isoformat()
        daily_count = count_daily_submissions(progress, day_key)
        resumed_count = 0
        submitted_count = 0
        completed_count = 0
        skipped_completed = 0
        skipped_active = 0
        failed_count = 0

        self.logger.info("live mode start")
        self.logger.info("planned_candidates=%d", len(planned))
        self.logger.info("project_root=%s", self.project_root)
        self.logger.info("fields_file=%s", self.fields_path)
        self.logger.info("ledger_path=%s", self.ledger_path)
        self.logger.info("progress_path=%s", self.progress_path)
        self.logger.info("run_mode=%s test_mode=%s", self.run_mode, self.test_mode)
        self.logger.info("api_base_url=%s", config.get("api_base_url") or API_BASE_URL or "<missing>")
        self.logger.info("auth_mode=%s", config.get("auth_mode") or "none")
        self.logger.info("missing_config=%s", ", ".join(missing_config) if missing_config else "none")
        self.logger.info("daily_count=%d warn_at=%d limit=%d", daily_count, DAILY_SIMULATION_WARN_AT, DAILY_SIMULATION_LIMIT)

        pending_records = progress_pending_records(progress)
        if pending_records:
            self.logger.info("resuming_pending=%d", len(pending_records))
            for record in pending_records:
                candidate = _candidate_from_progress_record(record, candidate_lookup)
                if candidate is None:
                    self.logger.warning(
                        "resume skipped missing candidate data candidate_id=%s submission_id=%s",
                        record.get("candidate_id"),
                        record.get("submission_id"),
                    )
                    continue

                submission_ref = str(record.get("submission_id") or record.get("alpha_id") or "")
                if not submission_ref:
                    self.logger.warning("resume skipped empty submission reference candidate=%s", candidate.get("candidate_id"))
                    continue

                try:
                    LIVE_RUNTIME["current_candidate"] = candidate
                    result = poll_result(submission_ref)
                    if result is None:
                        self.logger.info("resume still pending candidate=%s submission=%s", candidate.get("candidate_id"), submission_ref)
                        continue

                    alpha_id = _extract_result_alpha_id(result)
                    if alpha_id in (None, "", "UNKNOWN"):
                        alpha_id = submission_ref
                    if not self.test_mode:
                        write_result_to_ledger(candidate, submission_ref, result)

                    completed_record = _candidate_progress_record(
                        candidate,
                        status="completed",
                        submission_id=submission_ref,
                        alpha_id=str(alpha_id),
                        result=result,
                        submitted_at=str(record.get("submitted_at") or record.get("timestamp") or ""),
                        completed_at=datetime.now().isoformat(timespec="seconds"),
                    )
                    upsert_progress_record(progress, completed_record)
                    resumed_count += 1
                    completed_count += 1
                except Exception as exc:
                    failed_count += 1
                    self.logger.exception(
                        "resume failed candidate=%s submission=%s",
                        candidate.get("candidate_id"),
                        submission_ref,
                    )
                    error_record = _candidate_progress_record(
                        candidate,
                        status="error",
                        submission_id=submission_ref,
                        alpha_id=str(record.get("alpha_id") or ""),
                        error=str(exc),
                        submitted_at=str(record.get("submitted_at") or record.get("timestamp") or ""),
                    )
                    upsert_progress_record(progress, error_record)
                    if _is_auth_failure_error(exc):
                        raise

        active_candidate_ids = progress_active_candidate_ids(progress)
        completed_candidate_ids = progress_completed_candidate_ids(progress)

        try:
            for candidate in planned:
                candidate_id = str(candidate.get("candidate_id") or "")
                if not candidate_id:
                    self.logger.warning("skip candidate with empty candidate_id expression=%s", candidate.get("expression"))
                    continue

                if candidate_id in completed_candidate_ids:
                    skipped_completed += 1
                    self.logger.info("skip completed candidate=%s", candidate_id)
                    continue

                if candidate_id in active_candidate_ids:
                    skipped_active += 1
                    self.logger.info("skip active candidate=%s", candidate_id)
                    continue

                daily_count = count_daily_submissions(progress, day_key)
                if daily_count >= DAILY_SIMULATION_LIMIT:
                    self.logger.warning(
                        "daily simulation limit reached day=%s count=%d limit=%d",
                        day_key,
                        daily_count,
                        DAILY_SIMULATION_LIMIT,
                    )
                    break
                if daily_count >= DAILY_SIMULATION_WARN_AT:
                    self.logger.warning(
                        "daily simulation count approaching limit day=%s count=%d warn_at=%d limit=%d",
                        day_key,
                        daily_count,
                        DAILY_SIMULATION_WARN_AT,
                        DAILY_SIMULATION_LIMIT,
                    )

                LIVE_RUNTIME["current_candidate"] = candidate
                submission_ref: str | None = None
                try:
                    submission_ref = submit_simulation(candidate["expression"], candidate.get("neut"))
                    if not submission_ref:
                        failed_count += 1
                        self.logger.warning("submission returned no reference candidate=%s", candidate_id)
                        error_record = _candidate_progress_record(
                            candidate,
                            status="submission_failed",
                            error="submit_simulation returned no submission reference",
                        )
                        upsert_progress_record(progress, error_record)
                        save_progress(progress, self.progress_path, test_mode=self.test_mode, logger=self.logger)
                        continue

                    submitted_count += 1
                    submitted_at = datetime.now().isoformat(timespec="seconds")
                    submission_record = _candidate_progress_record(
                        candidate,
                        status="submitted",
                        submission_id=submission_ref,
                        submitted_at=submitted_at,
                    )
                    upsert_progress_record(progress, submission_record)
                    progress.setdefault("daily_submissions", {})[day_key] = count_daily_submissions(progress, day_key)
                    save_progress(progress, self.progress_path, test_mode=self.test_mode, logger=self.logger)

                    _sleep_live(SIMULATION_POLL_INTERVAL, "post-submission poll wait")
                    result = poll_result(submission_ref)
                    if result is None:
                        self.logger.warning(
                            "poll timeout or pending result candidate=%s submission=%s",
                            candidate_id,
                            submission_ref,
                        )
                        pending_record = _candidate_progress_record(
                            candidate,
                            status="submitted",
                            submission_id=submission_ref,
                            submitted_at=submission_record["submitted_at"],
                            updated_at=datetime.now().isoformat(timespec="seconds"),
                        )
                        upsert_progress_record(progress, pending_record)
                        save_progress(progress, self.progress_path, test_mode=self.test_mode, logger=self.logger)
                        continue

                    alpha_id = _extract_result_alpha_id(result)
                    if alpha_id in (None, "", "UNKNOWN"):
                        alpha_id = submission_ref

                    if not self.test_mode:
                        write_result_to_ledger(candidate, submission_ref, result)

                    completed_record = _candidate_progress_record(
                        candidate,
                        status="completed",
                        submission_id=submission_ref,
                        alpha_id=str(alpha_id),
                        result=result,
                        submitted_at=submission_record["submitted_at"],
                        completed_at=datetime.now().isoformat(timespec="seconds"),
                    )
                    upsert_progress_record(progress, completed_record)
                    completed_count += 1
                    progress.setdefault("daily_submissions", {})[day_key] = count_daily_submissions(progress, day_key)
                    save_progress(progress, self.progress_path, test_mode=self.test_mode, logger=self.logger)
                    self.logger.info(
                        "candidate completed candidate=%s alpha_id=%s status=%s",
                        candidate_id,
                        alpha_id,
                        completed_record.get("result_status", "UNKNOWN"),
                    )

                    active_candidate_ids.add(candidate_id)
                    completed_candidate_ids.add(candidate_id)

                    if submitted_count % 5 == 0:
                        _sleep_live(120, "batch pause after every 5 submissions")
                except Exception as exc:
                    failed_count += 1
                    self.logger.exception("live candidate failed candidate=%s", candidate_id)
                    error_record = _candidate_progress_record(
                        candidate,
                        status="error",
                        submission_id=submission_ref,
                        error=str(exc),
                        submitted_at=datetime.now().isoformat(timespec="seconds") if submission_ref else None,
                    )
                    upsert_progress_record(progress, error_record)
                    save_progress(progress, self.progress_path, test_mode=self.test_mode, logger=self.logger)
                    if _is_auth_failure_error(exc):
                        raise
                    continue
        finally:
            save_progress(progress, self.progress_path, test_mode=self.test_mode, logger=self.logger)
            if ledger is not None:
                ledger.close()

        summary = {
            "mode": "live" if not self.test_mode else "live-test-mode",
            "planned": len(planned),
            "resumed": resumed_count,
            "submitted": submitted_count,
            "completed": completed_count,
            "failed": failed_count,
            "skipped_completed": skipped_completed,
            "skipped_active": skipped_active,
            "daily_count": count_daily_submissions(progress, day_key),
            "missing_config": missing_config,
            "test_mode": self.test_mode,
        }
        self.logger.info("live mode end summary=%s", json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return summary

    def run(self) -> dict[str, Any]:
        payload = self.load_fields()
        self.logger.info("loaded field candidate file=%s", self.fields_path)
        self.logger.info("batch_id=%s", payload.get("batch_id"))
        self.logger.info("field_count=%d", len(payload.get("fields", [])))

        candidates = self.generate_candidates(payload)
        self.logger.info("generated_candidates=%d", len(candidates))
        candidates = self.check_duplicates(candidates)
        candidates = self.sort_candidates(candidates)
        candidates = candidates[: self.max_simulations]

        if self.run_mode == "dry":
            return self.print_dry_run_plan(candidates)
        if self.run_mode == "live":
            return self.run_live(candidates)
        raise ValueError(f"unsupported run mode: {self.run_mode}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Batch S0 scan pipeline (offline skeleton).")
    parser.add_argument(
        "--run-mode",
        choices=["dry", "live"],
        default="dry",
        help="dry: generate plan and print it; live: placeholder for future submission client",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="When used with --run-mode live, print requests and progress updates without consuming quota",
    )
    parser.add_argument(
        "--fields",
        required=True,
        help="Path to field candidates JSON file, relative to the project root unless absolute",
    )
    parser.add_argument("--top", type=int, default=3, help="Number of top candidates to surface")
    parser.add_argument(
        "--max-simulations",
        type=int,
        default=50,
        help="Maximum number of candidates to keep after ranking",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    scanner = BatchS0Scanner(
        fields_path=args.fields,
        top=args.top,
        max_simulations=args.max_simulations,
        run_mode=args.run_mode,
        test_mode=args.test_mode,
    )
    summary = scanner.run()
    scanner.logger.info("summary=%s", json.dumps(summary, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

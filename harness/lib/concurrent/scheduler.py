"""Task scheduler built on top of the file-backed slot manager."""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from slot_manager import SlotManager, _file_lock

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TASK_LOG_PATH = PROJECT_ROOT / "runs" / "state" / "scheduler_tasks.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalize_region(region: str | None) -> str:
    text = str(region or "").strip().upper()
    return text or "UNKNOWN"


def _preview_expression(expression: str, limit: int = 120) -> str:
    text = " ".join(str(expression or "").split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _safe_json(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_safe_json(item) for item in value]
    return repr(value)


def _extract_submission_id(result: Any) -> str | None:
    if isinstance(result, dict):
        for key in ("submission_id", "simulation_id", "alpha_id", "id"):
            value = result.get(key)
            if value not in (None, ""):
                return str(value)
    if result not in (None, ""):
        return str(result)
    return None


class Scheduler:
    """Dispatch tasks through a SlotManager without blocking the caller."""

    def __init__(
        self,
        slot_manager: SlotManager,
        submit_func: Callable[..., Any] | None = None,
        task_log_path: str | Path = DEFAULT_TASK_LOG_PATH,
    ) -> None:
        self.slot_manager = slot_manager
        self.submit_func = submit_func
        self.task_log_path = Path(task_log_path)
        if not self.task_log_path.is_absolute():
            self.task_log_path = (PROJECT_ROOT / self.task_log_path).resolve()
        self.task_lock_path = self.task_log_path.with_suffix(self.task_log_path.suffix + ".lock")
        self._tasks: dict[str, dict[str, Any]] = {}
        self._threads: list[threading.Thread] = []
        self._lock = threading.Lock()

    def _append_task_record(self, record: dict[str, Any]) -> None:
        self.task_log_path.parent.mkdir(parents=True, exist_ok=True)
        with _file_lock(self.task_lock_path, non_blocking=False) as acquired:
            if not acquired:
                return
            with self.task_log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _record_task(self, task_id: str, **updates: Any) -> dict[str, Any]:
        with self._lock:
            task = self._tasks.setdefault(task_id, {"task_id": task_id, "created_at": _utc_now()})
            task.update(updates)
            task["updated_at"] = _utc_now()
            snapshot = dict(task)
        self._append_task_record(_safe_json(snapshot))
        return snapshot

    def _run_task(self, task_id: str, alpha_expr: str, region: str, kwargs: dict[str, Any]) -> None:
        self._record_task(task_id, status="running", message="task started")
        result: Any = None
        error_message: str | None = None
        try:
            if self.submit_func is None:
                self._record_task(task_id, status="reserved", message="slot reserved without submit function")
                return
            result = self.submit_func(alpha_expr, region, **kwargs)
            self._record_task(
                task_id,
                status="completed",
                message="task finished",
                result=_safe_json(result),
                submission_id=_extract_submission_id(result),
            )
        except Exception as exc:  # pragma: no cover - surfaced in task log
            error_message = str(exc)
            self._record_task(task_id, status="failed", message=error_message, error=error_message)
        finally:
            self.slot_manager.release_slot(region)
            self._record_task(
                task_id,
                status=self._tasks.get(task_id, {}).get("status", "unknown"),
                message=self._tasks.get(task_id, {}).get("message", "finished"),
                finished_at=_utc_now(),
                error=error_message,
                result=_safe_json(result),
            )

    def schedule(self, alpha_expr: str, region: str, **kwargs: Any) -> dict[str, Any]:
        """Attempt to schedule a task without blocking the caller."""

        region_key = _normalize_region(region)
        if not self.slot_manager.acquire_slot(region_key):
            record = self._record_task(
                uuid.uuid4().hex,
                status="rejected",
                region=region_key,
                message=f"no slot available for {region_key}",
                alpha_expr=_preview_expression(alpha_expr),
                kwargs_summary=_safe_json(kwargs),
            )
            return {
                "status": "rejected",
                "message": record["message"],
                "region": region_key,
                "available_slots": self.slot_manager.get_available_slots(region_key),
            }

        task_id = uuid.uuid4().hex
        task_record = {
            "region": region_key,
            "alpha_expr": _preview_expression(alpha_expr),
            "kwargs_summary": _safe_json(kwargs),
            "status": "scheduled",
            "message": "slot acquired",
            "created_at": _utc_now(),
        }
        self._record_task(task_id, **task_record)

        if self.submit_func is None:
            return {
                "status": "scheduled",
                "message": "slot reserved; no submit function provided",
                "task_id": task_id,
                "region": region_key,
                "available_slots": self.slot_manager.get_available_slots(region_key),
            }

        thread = threading.Thread(
            target=self._run_task,
            args=(task_id, alpha_expr, region_key, dict(kwargs)),
            daemon=True,
            name=f"scheduler-{task_id[:8]}",
        )
        with self._lock:
            self._threads.append(thread)
        thread.start()

        return {
            "status": "scheduled",
            "message": "task dispatched",
            "task_id": task_id,
            "region": region_key,
            "available_slots": self.slot_manager.get_available_slots(region_key),
        }

    def wait_all(self) -> list[dict[str, Any]]:
        """Wait for all currently dispatched tasks and return their records."""

        while True:
            with self._lock:
                threads = [thread for thread in self._threads if thread.is_alive()]
            if not threads:
                break
            for thread in threads:
                thread.join()
        with self._lock:
            return [dict(task) for task in self._tasks.values()]


__all__ = ["Scheduler"]

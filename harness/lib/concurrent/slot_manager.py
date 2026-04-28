"""File-backed slot manager for BRAIN_LAB concurrent live runs.

This module keeps concurrency state outside the source tree in
`runs/state/slot_status.json` and uses a real inter-process lock so multiple Python
processes can coordinate without relying on threading alone.
"""

from __future__ import annotations

import errno
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

try:  # POSIX
    import fcntl  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - Windows fallback
    fcntl = None  # type: ignore[assignment]

try:  # Windows
    import msvcrt  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - POSIX fallback
    msvcrt = None  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_PATH = PROJECT_ROOT / "harness" / "incubation-protocol.json"
DEFAULT_STATE_PATH = PROJECT_ROOT / "runs" / "state" / "slot_status.json"
DEFAULT_LOCK_PATH = PROJECT_ROOT / "runs" / "state" / "slot_status.lock"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalize_region(region: str | None) -> str:
    text = str(region or "").strip().upper()
    return text or "UNKNOWN"


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def _read_json_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _load_protocol_default_max_slots() -> int:
    payload = _read_json_file(PROTOCOL_PATH)
    parallel_limits = payload.get("parallel_limits")
    if isinstance(parallel_limits, dict):
        return _coerce_positive_int(parallel_limits.get("default_max_parallel_families"), 2)
    return 2


@contextmanager
def _file_lock(lock_path: Path, non_blocking: bool = False) -> Iterator[bool]:
    """Acquire an inter-process lock using the platform's stdlib primitives."""

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+", encoding="utf-8")
    acquired = False

    try:
        if fcntl is not None:  # POSIX
            flags = fcntl.LOCK_EX | (fcntl.LOCK_NB if non_blocking else 0)
            try:
                fcntl.flock(handle.fileno(), flags)
            except OSError as exc:
                if isinstance(exc, BlockingIOError) or exc.errno in {errno.EACCES, errno.EAGAIN}:
                    handle.close()
                    yield False
                    return
                handle.close()
                raise
            acquired = True
        elif msvcrt is not None:  # pragma: no cover - Windows fallback
            mode = msvcrt.LK_NBLCK if non_blocking else msvcrt.LK_LOCK
            try:
                msvcrt.locking(handle.fileno(), mode, 1)
            except OSError:
                handle.close()
                yield False
                return
            acquired = True
        else:  # pragma: no cover - very small fallback for exotic runtimes
            if non_blocking and lock_path.exists():
                handle.close()
                yield False
                return
            acquired = True

        yield True
    finally:
        if acquired:
            try:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                elif msvcrt is not None:  # pragma: no cover - Windows fallback
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        try:
            handle.close()
        except OSError:
            pass


class SlotManager:
    """Coordinate concurrent simulation slots across processes.

    Args:
        max_slots: Global ceiling for concurrently active slots. If omitted,
            the protocol default is used.
        region_quotas: Optional per-region ceilings. Unknown regions fall back
            to the global max.
        state_path: Where the slot state JSON is persisted. Defaults to
            `runs/state/slot_status.json`.
    """

    def __init__(
        self,
        max_slots: int | None = None,
        region_quotas: dict[str, int] | None = None,
        state_path: str | Path = DEFAULT_STATE_PATH,
        lock_path: str | Path | None = None,
    ) -> None:
        self.protocol_default_max_slots = _load_protocol_default_max_slots()
        self.max_slots = _coerce_positive_int(max_slots, self.protocol_default_max_slots)
        self.state_path = Path(state_path)
        if not self.state_path.is_absolute():
            self.state_path = (PROJECT_ROOT / self.state_path).resolve()
        self.lock_path = Path(lock_path) if lock_path is not None else DEFAULT_LOCK_PATH
        if not self.lock_path.is_absolute():
            self.lock_path = (PROJECT_ROOT / self.lock_path).resolve()
        self.region_quotas = {
            _normalize_region(region): _coerce_positive_int(quota, self.max_slots)
            for region, quota in (region_quotas or {}).items()
        }
        self._ensure_state()

    def _default_state(self) -> dict[str, Any]:
        regions = {
            region: {"quota": quota, "active": 0}
            for region, quota in sorted(self.region_quotas.items())
        }
        return {
            "schema_version": 1,
            "max_slots": self.max_slots,
            "protocol_default_max_slots": self.protocol_default_max_slots,
            "region_quotas": dict(sorted(self.region_quotas.items())),
            "regions": regions,
            "total_active": 0,
            "recent_events": [],
            "updated_at": _utc_now(),
        }

    def _normalize_loaded_state(self, payload: dict[str, Any]) -> dict[str, Any]:
        state = self._default_state()
        state["schema_version"] = _coerce_positive_int(payload.get("schema_version"), 1)
        state["max_slots"] = _coerce_positive_int(payload.get("max_slots"), self.max_slots)
        state["protocol_default_max_slots"] = _coerce_positive_int(
            payload.get("protocol_default_max_slots"),
            self.protocol_default_max_slots,
        )

        loaded_region_quotas = payload.get("region_quotas")
        if isinstance(loaded_region_quotas, dict):
            merged_quotas = {
                _normalize_region(region): _coerce_positive_int(quota, state["max_slots"])
                for region, quota in loaded_region_quotas.items()
            }
        else:
            merged_quotas = {}
        merged_quotas.update(state["region_quotas"])
        state["region_quotas"] = dict(sorted(merged_quotas.items()))

        regions = payload.get("regions")
        if isinstance(regions, dict):
            for region, info in regions.items():
                region_key = _normalize_region(region)
                quota = state["region_quotas"].get(region_key, state["max_slots"])
                active = 0
                if isinstance(info, dict):
                    active = _coerce_positive_int(info.get("active"), 0)
                    quota = _coerce_positive_int(info.get("quota"), quota)
                state["regions"][region_key] = {"quota": quota, "active": active}

        total_active = _coerce_positive_int(payload.get("total_active"), 0)
        if total_active <= 0:
            total_active = sum(info["active"] for info in state["regions"].values())
        state["total_active"] = min(total_active, state["max_slots"])

        recent_events = payload.get("recent_events")
        if isinstance(recent_events, list):
            state["recent_events"] = [event for event in recent_events if isinstance(event, dict)][-100:]

        state["updated_at"] = str(payload.get("updated_at") or _utc_now())
        return state

    def _ensure_state(self) -> None:
        if not self.state_path.exists():
            _write_json_atomic(self.state_path, self._default_state())
            return
        loaded = self._read_state()
        if not loaded:
            _write_json_atomic(self.state_path, self._default_state())
            return
        # Re-save to ensure the schema is normalized and future reads are stable.
        _write_json_atomic(self.state_path, self._normalize_loaded_state(loaded))

    def _read_state(self) -> dict[str, Any]:
        payload = _read_json_file(self.state_path)
        if not payload:
            return {}
        return self._normalize_loaded_state(payload)

    def _save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = _utc_now()
        state["region_quotas"] = dict(sorted(state.get("region_quotas", {}).items()))
        state["regions"] = dict(sorted(state.get("regions", {}).items()))
        state["recent_events"] = list(state.get("recent_events", []))[-100:]
        _write_json_atomic(self.state_path, state)

    def _ensure_region(self, state: dict[str, Any], region: str) -> dict[str, Any]:
        region_key = _normalize_region(region)
        quota = state["region_quotas"].get(region_key, self.max_slots)
        region_state = state["regions"].get(region_key)
        if not isinstance(region_state, dict):
            region_state = {"quota": quota, "active": 0}
        else:
            region_state = {
                "quota": _coerce_positive_int(region_state.get("quota"), quota),
                "active": _coerce_positive_int(region_state.get("active"), 0),
            }
        state["regions"][region_key] = region_state
        return region_state

    def _available_for_region(self, state: dict[str, Any], region: str) -> int:
        region_key = _normalize_region(region)
        region_state = state.get("regions", {}).get(region_key)
        if not isinstance(region_state, dict):
            region_state = self._ensure_region(state, region_key)
        quota = _coerce_positive_int(region_state.get("quota"), self.max_slots)
        active = _coerce_positive_int(region_state.get("active"), 0)
        total_active = _coerce_positive_int(state.get("total_active"), 0)
        global_available = max(0, self.max_slots - total_active)
        region_available = max(0, quota - active)
        return min(global_available, region_available)

    def _append_event(self, state: dict[str, Any], *, action: str, region: str, available_before: int, available_after: int) -> None:
        events = state.setdefault("recent_events", [])
        if not isinstance(events, list):
            events = []
            state["recent_events"] = events
        events.append(
            {
                "timestamp": _utc_now(),
                "action": action,
                "region": _normalize_region(region),
                "available_before": available_before,
                "available_after": available_after,
                "total_active": _coerce_positive_int(state.get("total_active"), 0),
            }
        )
        state["recent_events"] = events[-100:]

    def acquire_slot(self, region: str) -> bool:
        """Try to reserve one slot for `region` without blocking."""

        with _file_lock(self.lock_path, non_blocking=True) as acquired:
            if not acquired:
                return False

            state = self._read_state()
            if not state:
                state = self._default_state()
            region_state = self._ensure_region(state, region)
            available_before = self._available_for_region(state, region)
            if available_before <= 0:
                self._append_event(state, action="acquire_rejected", region=region, available_before=available_before, available_after=available_before)
                self._save_state(state)
                return False

            region_state["active"] = _coerce_positive_int(region_state.get("active"), 0) + 1
            state["total_active"] = _coerce_positive_int(state.get("total_active"), 0) + 1
            available_after = self._available_for_region(state, region)
            self._append_event(state, action="acquire", region=region, available_before=available_before, available_after=available_after)
            self._save_state(state)
            return True

    def release_slot(self, region: str) -> None:
        """Release one slot for `region` and persist the updated state."""

        with _file_lock(self.lock_path, non_blocking=False) as acquired:
            if not acquired:
                return

            state = self._read_state()
            if not state:
                state = self._default_state()

            region_key = _normalize_region(region)
            region_state = state.get("regions", {}).get(region_key)
            if not isinstance(region_state, dict):
                available_before = max(0, self.max_slots - _coerce_positive_int(state.get("total_active"), 0))
                self._append_event(
                    state,
                    action="release_miss",
                    region=region_key,
                    available_before=available_before,
                    available_after=available_before,
                )
                self._save_state(state)
                return

            region_state = self._ensure_region(state, region_key)
            available_before = self._available_for_region(state, region_key)
            if region_state["active"] <= 0:
                self._append_event(
                    state,
                    action="release_miss",
                    region=region_key,
                    available_before=available_before,
                    available_after=available_before,
                )
                self._save_state(state)
                return

            region_state["active"] -= 1
            state["total_active"] = max(0, _coerce_positive_int(state.get("total_active"), 0) - 1)
            available_after = self._available_for_region(state, region_key)
            self._append_event(state, action="release", region=region_key, available_before=available_before, available_after=available_after)
            self._save_state(state)

    def get_available_slots(self, region: str) -> int:
        """Return the number of slots still available for `region`."""

        state = self._read_state()
        if not state:
            state = self._default_state()
        return self._available_for_region(state, region)

    def get_status(self) -> dict[str, Any]:
        """Return a monitoring-friendly snapshot of slot usage."""

        state = self._read_state()
        if not state:
            state = self._default_state()

        regions: dict[str, dict[str, int]] = {}
        for region, info in state.get("regions", {}).items():
            if not isinstance(info, dict):
                continue
            quota = _coerce_positive_int(info.get("quota"), self.max_slots)
            active = _coerce_positive_int(info.get("active"), 0)
            regions[region] = {
                "quota": quota,
                "active": active,
                "available": max(0, min(self.max_slots - _coerce_positive_int(state.get("total_active"), 0), quota - active)),
            }

        return {
            "state_path": str(self.state_path),
            "lock_path": str(self.lock_path),
            "schema_version": _coerce_positive_int(state.get("schema_version"), 1),
            "max_slots": self.max_slots,
            "protocol_default_max_slots": self.protocol_default_max_slots,
            "total_active": _coerce_positive_int(state.get("total_active"), 0),
            "available_total": max(0, self.max_slots - _coerce_positive_int(state.get("total_active"), 0)),
            "region_quotas": dict(sorted(state.get("region_quotas", {}).items())),
            "regions": regions,
            "recent_events": list(state.get("recent_events", []))[-20:],
            "updated_at": state.get("updated_at"),
        }


__all__ = ["SlotManager"]

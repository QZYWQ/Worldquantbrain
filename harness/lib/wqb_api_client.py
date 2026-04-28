"""Offline-safe WorldQuant BRAIN API client.

All network methods are guarded by ``WQB_API_ENABLED``. When the switch is not
explicitly enabled, the module stays offline and raises immediately instead of
sending any request.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # Optional dependency; only required when API is enabled.
    import requests  # type: ignore[import-not-found]
    from requests.auth import HTTPBasicAuth  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - offline environments may not ship requests
    requests = None  # type: ignore[assignment]
    HTTPBasicAuth = None  # type: ignore[assignment]

try:
    from zoneinfo import ZoneInfo
except ModuleNotFoundError:  # pragma: no cover - very old Python fallback
    ZoneInfo = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "wqb_config.json"
DEFAULT_COUNTER_DB_PATH = PROJECT_ROOT / "runs" / "state" / "wqb_counter.db"

DEFAULT_CONFIG = {
    "base_url": "https://api.worldquantbrain.com",
    "daily_limit": 4000,
    "poll_interval_seconds": 30,
    "timezone": "America/New_York",
    "warning_threshold": 3200,
}


def _env_enabled() -> bool:
    value = os.environ.get("WQB_API_ENABLED")
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _coerce_int(value: Any, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def _coerce_non_negative_int(value: Any, default: int = 0) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number >= 0 else default


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load client configuration from JSON, falling back to safe defaults."""

    path = Path(config_path)
    if not path.is_absolute():
        path = path.resolve()
    payload = _read_json(path)
    config = dict(DEFAULT_CONFIG)
    for key in config:
        if key in payload and payload[key] not in (None, ""):
            config[key] = payload[key]
    config["base_url"] = str(config.get("base_url") or DEFAULT_CONFIG["base_url"]).rstrip("/")
    config["daily_limit"] = _coerce_int(config.get("daily_limit"), DEFAULT_CONFIG["daily_limit"])
    config["warning_threshold"] = _coerce_int(
        config.get("warning_threshold"),
        int(config["daily_limit"] * 0.8),
    )
    if config["warning_threshold"] > config["daily_limit"]:
        config["warning_threshold"] = int(config["daily_limit"] * 0.8)
    config["poll_interval_seconds"] = _coerce_int(config.get("poll_interval_seconds"), DEFAULT_CONFIG["poll_interval_seconds"])
    config["timezone"] = str(config.get("timezone") or DEFAULT_CONFIG["timezone"])
    return config


def _new_york_now(tz_name: str) -> datetime:
    if ZoneInfo is None:  # pragma: no cover - fallback for old Python
        LOGGER.warning("zoneinfo unavailable; falling back to UTC-5 for daily counter")
        from datetime import timedelta

        return datetime.now(timezone(timedelta(hours=-5)))
    try:
        tz = ZoneInfo(tz_name)
    except Exception:  # pragma: no cover - invalid config fallback
        tz = ZoneInfo("America/New_York")
    return datetime.now(tz)


@dataclass
class SimulationCounter:
    """Local SQLite counter that enforces the daily submission cap."""

    db_path: Path = DEFAULT_COUNTER_DB_PATH
    daily_limit: int = DEFAULT_CONFIG["daily_limit"]
    warning_threshold: int = DEFAULT_CONFIG["warning_threshold"]
    timezone_name: str = DEFAULT_CONFIG["timezone"]

    def __post_init__(self) -> None:
        self.db_path = Path(self.db_path)
        if not self.db_path.is_absolute():
            self.db_path = (PROJECT_ROOT / self.db_path).resolve()
        self.daily_limit = _coerce_int(self.daily_limit, DEFAULT_CONFIG["daily_limit"])
        if self.warning_threshold <= 0:
            self.warning_threshold = int(self.daily_limit * 0.8)
        self.warning_threshold = min(_coerce_int(self.warning_threshold, int(self.daily_limit * 0.8)), self.daily_limit)
        self._lock = threading.Lock()
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_counts (
                    day_key TEXT PRIMARY KEY,
                    count INTEGER NOT NULL DEFAULT 0,
                    warning_sent INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _today_key(self) -> str:
        return _new_york_now(self.timezone_name).strftime("%Y-%m-%d")

    def get_today_count(self) -> int:
        day_key = self._today_key()
        with self._connect() as conn:
            cursor = conn.execute("SELECT count FROM daily_counts WHERE day_key = ?", (day_key,))
            row = cursor.fetchone()
            return int(row["count"]) if row is not None else 0

    def increment_count(self) -> dict[str, Any]:
        day_key = self._today_key()
        with self._lock:
            previous_count = self.get_today_count()
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO daily_counts(day_key, count, warning_sent, updated_at)
                    VALUES (?, 1, CASE WHEN 1 >= ? THEN 1 ELSE 0 END, ?)
                    ON CONFLICT(day_key) DO UPDATE SET
                        count = count + 1,
                        warning_sent = CASE
                            WHEN count + 1 >= ? THEN 1
                            ELSE warning_sent
                        END,
                        updated_at = excluded.updated_at
                    """,
                    (day_key, self.warning_threshold, _utc_now(), self.warning_threshold),
                )
                conn.commit()
                row = conn.execute(
                    "SELECT count, warning_sent FROM daily_counts WHERE day_key = ?",
                    (day_key,),
                ).fetchone()

        count = int(row["count"]) if row is not None else 0
        warning_needed = previous_count < self.warning_threshold <= count
        if warning_needed:
            LOGGER.warning(
                "WQB daily count reached warning threshold day=%s count=%d threshold=%d",
                day_key,
                count,
                self.warning_threshold,
            )
        return {
            "day_key": day_key,
            "count": count,
            "limit": self.daily_limit,
            "warning_threshold": self.warning_threshold,
            "warning_needed": warning_needed,
            "can_simulate": count < self.daily_limit,
            "limit_reached": count >= self.daily_limit,
        }

    def can_simulate(self) -> bool:
        return self.get_today_count() < self.daily_limit

    def get_status(self) -> dict[str, Any]:
        count = self.get_today_count()
        return {
            "day_key": self._today_key(),
            "count": count,
            "limit": self.daily_limit,
            "remaining": max(0, self.daily_limit - count),
            "warning_threshold": self.warning_threshold,
            "warning_needed": count >= self.warning_threshold,
            "can_simulate": count < self.daily_limit,
            "limit_reached": count >= self.daily_limit,
        }


class WQBApiClient:
    """Small WQB API client with an explicit offline guard."""

    def __init__(
        self,
        config_path: str | Path = DEFAULT_CONFIG_PATH,
        counter_db_path: str | Path = DEFAULT_COUNTER_DB_PATH,
    ) -> None:
        self.config_path = Path(config_path)
        self.config = load_config(self.config_path)
        self.counter = SimulationCounter(
            db_path=counter_db_path,
            daily_limit=int(self.config["daily_limit"]),
            warning_threshold=int(self.config["warning_threshold"]),
            timezone_name=str(self.config.get("timezone") or "America/New_York"),
        )
        self._session: requests.Session | None = None if requests is not None else None
        self._credentials: tuple[str, str] | None = None
        self._lock = threading.Lock()

    @staticmethod
    def _require_enabled() -> None:
        if not _env_enabled():
            raise RuntimeError("WQB API is disabled")

    def set_credentials(self, email: str, password: str) -> None:
        """Store login credentials for the next enabled session."""

        with self._lock:
            self._credentials = (str(email), str(password))
            self._session = None

    def get_session(self):
        """Return a logged-in requests session when the API switch is enabled."""

        self._require_enabled()
        if requests is None or HTTPBasicAuth is None:
            raise RuntimeError("requests is required when WQB API is enabled")

        with self._lock:
            if self._session is not None:
                return self._session

            session = requests.Session()
            session.trust_env = False
            session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

            if self._credentials is not None:
                login_url = f"{self.config['base_url']}/authentication"
                response = session.post(
                    login_url,
                    timeout=30,
                    auth=HTTPBasicAuth(self._credentials[0], self._credentials[1]),
                )
                if response.status_code >= 400:
                    raise RuntimeError(f"authentication failed: {response.status_code} {response.text[:200]}")

            self._session = session
            return session

    def _build_payload(
        self,
        expression: str,
        region: str,
        universe: str,
        delay: int = 1,
        neutralization: str = "NONE",
        decay: int = 0,
    ) -> dict[str, Any]:
        return {
            "type": "REGULAR",
            "settings": {
                "instrumentType": "EQUITY",
                "region": str(region).upper(),
                "universe": str(universe).upper(),
                "delay": int(delay),
                "decay": _coerce_non_negative_int(decay, 0),
                "neutralization": str(neutralization or "NONE").upper(),
                "truncation": 0.08,
                "pasteurization": "ON",
                "unitHandling": "VERIFY",
                "nanHandling": "ON",
                "language": "FASTEXPR",
                "visualization": False,
            },
            "regular": expression,
        }

    def submit_simulation(
        self,
        expression: str,
        region: str,
        universe: str,
        delay: int = 1,
        neutralization: str = "NONE",
        decay: int = 0,
    ) -> dict[str, Any]:
        """Submit a simulation request when enabled; otherwise fail fast."""

        self._require_enabled()
        if not self.counter.can_simulate():
            status = self.counter.get_status()
            return {
                "error": "daily limit reached",
                "limit": status["limit"],
                "count": status["count"],
                "warning_threshold": status["warning_threshold"],
                "can_simulate": False,
            }

        session = self.get_session()
        payload = self._build_payload(
            expression,
            region,
            universe,
            delay=delay,
            neutralization=neutralization,
            decay=decay,
        )
        url = f"{self.config['base_url']}/simulations"
        response = session.post(url, json=payload, timeout=60)

        if response.status_code in {200, 201, 202}:
            simulation_id = _extract_simulation_id(response)
            if not simulation_id:
                return {
                    "error": "missing simulation id in response",
                    "status_code": response.status_code,
                    "response": _safe_response_payload(response),
                }
            counter_result = self.counter.increment_count()
            return {
                "simulation_id": simulation_id,
                "status_code": response.status_code,
                "location": response.headers.get("Location"),
                "count": counter_result["count"],
                "warning_needed": counter_result["warning_needed"],
                "response": _safe_response_payload(response),
            }

        return {
            "error": f"submit failed with status {response.status_code}",
            "status_code": response.status_code,
            "response": _safe_response_payload(response),
        }

    def get_daily_status(self) -> dict[str, Any]:
        """Return the current day key and quota snapshot for the local counter."""

        self._require_enabled()
        status = self.counter.get_status()
        warning_at = int(status.get("warning_threshold", self.config.get("warning_threshold", 0)) or 0)
        return {
            "day_key": status.get("day_key"),
            "count": int(status.get("count", 0) or 0),
            "limit": int(status.get("limit", self.config.get("daily_limit", 0)) or 0),
            "warning_at": warning_at,
            "warning_threshold": warning_at,
            "can_simulate": bool(status.get("can_simulate")),
            "limit_reached": bool(status.get("limit_reached")),
        }

    def poll_result(self, simulation_id: str, max_wait: int = 300) -> dict[str, Any]:
        """Poll a simulation result until completion or timeout."""

        self._require_enabled()
        session = self.get_session()
        url = f"{self.config['base_url']}/simulations/{simulation_id}"
        deadline = time.time() + max(1, int(max_wait))
        poll_interval = max(1, int(self.config.get("poll_interval_seconds", 30)))

        while True:
            response = session.get(url, timeout=60)
            if response.status_code == 401:
                return {
                    "error": "authentication required",
                    "status_code": response.status_code,
                    "simulation_id": simulation_id,
                    "response": _safe_response_payload(response),
                }
            if response.status_code >= 400:
                return {
                    "error": f"poll failed with status {response.status_code}",
                    "status_code": response.status_code,
                    "simulation_id": simulation_id,
                    "response": _safe_response_payload(response),
                }

            payload = _safe_response_payload(response)
            status = str(payload.get("status") or payload.get("state") or "").lower()
            if status in {"completed", "complete", "done", "finished", "failed", "error"}:
                payload["simulation_id"] = simulation_id
                return payload
            if any(key in payload for key in ("alpha_id", "sharpe", "fitness", "test_sharpe", "test_fitness")):
                payload["simulation_id"] = simulation_id
                return payload

            if time.time() >= deadline:
                return {
                    "error": "poll timeout",
                    "simulation_id": simulation_id,
                    "status_code": response.status_code,
                    "response": payload,
                }
            time.sleep(min(poll_interval, max(1, int(deadline - time.time()))))


def _safe_response_payload(response: Any) -> dict[str, Any]:
    try:
        payload = response.json()
    except Exception:
        payload = {"raw_text": getattr(response, "text", "")}
    if isinstance(payload, dict):
        return payload
    return {"raw_payload": payload, "raw_text": getattr(response, "text", "")}


def _extract_simulation_id(response: Any) -> str | None:
    location = getattr(response, "headers", {}).get("Location")
    if location:
        text = str(location).rstrip("/")
        if "/" in text:
            return text.rsplit("/", 1)[-1] or text
        return text
    payload = _safe_response_payload(response)
    for key in ("simulation_id", "simulationId", "alpha_id", "alphaId", "id"):
        value = payload.get(key)
        if value not in (None, ""):
            return str(value)
    return None


_DEFAULT_CLIENT: WQBApiClient | None = None


def _client() -> WQBApiClient:
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None:
        _DEFAULT_CLIENT = WQBApiClient()
    return _DEFAULT_CLIENT


def set_credentials(email: str, password: str) -> None:
    _client().set_credentials(email, password)


def get_session():
    return _client().get_session()


def submit_simulation(
    expression: str,
    region: str,
    universe: str,
    delay: int = 1,
    neutralization: str = "NONE",
    decay: int = 0,
) -> dict[str, Any]:
    return _client().submit_simulation(
        expression=expression,
        region=region,
        universe=universe,
        delay=delay,
        neutralization=neutralization,
        decay=decay,
    )


def poll_result(simulation_id: str, max_wait: int = 300) -> dict[str, Any]:
    return _client().poll_result(simulation_id=simulation_id, max_wait=max_wait)


def get_daily_status() -> dict[str, Any]:
    return _client().get_daily_status()


def get_daily_count() -> int:
    return _client().counter.get_today_count()


def increment_count() -> dict[str, Any]:
    return _client().counter.increment_count()


def can_simulate() -> bool:
    return _client().counter.can_simulate()


__all__ = [
    "SimulationCounter",
    "WQBApiClient",
    "can_simulate",
    "get_daily_count",
    "get_daily_status",
    "get_session",
    "increment_count",
    "load_config",
    "poll_result",
    "set_credentials",
    "submit_simulation",
]

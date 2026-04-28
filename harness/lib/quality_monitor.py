"""Ledger-backed quality monitor for alpha degradation detection."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric != numeric:  # NaN guard
        return None
    return numeric


def _normalize_alpha_id(alpha_id: str | None) -> str:
    text = str(alpha_id or "").strip()
    return text


class AlphaQualityMonitor:
    """Inspect historical ledger rows and flag large Sharpe regressions."""

    def __init__(
        self,
        db_path: str = "runs/evidence/result_ledger.db",
        window_size: int = 10,
        degradation_threshold: float = 0.2,
    ) -> None:
        self.db_path = Path(db_path)
        if not self.db_path.is_absolute():
            self.db_path = (PROJECT_ROOT / self.db_path).resolve()
        self.window_size = max(1, int(window_size))
        self.degradation_threshold = max(0.0, float(degradation_threshold))

    def _connect(self) -> sqlite3.Connection | None:
        if not self.db_path.exists():
            return None
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _mean(values: list[float]) -> float | None:
        if not values:
            return None
        return sum(values) / len(values)

    def _fetch_alpha_rows(self, conn: sqlite3.Connection, alpha_id: str) -> list[dict[str, Any]]:
        cursor = conn.execute(
            """
            SELECT id, alpha_id, is_sharpe, timestamp
            FROM simulations
            WHERE alpha_id = ?
              AND is_sharpe IS NOT NULL
            ORDER BY timestamp ASC, id ASC
            """,
            (alpha_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def check_alpha(self, alpha_id: str) -> dict[str, Any] | None:
        """Return a degradation alert for one alpha, or None if healthy."""

        normalized_id = _normalize_alpha_id(alpha_id)
        if not normalized_id:
            return None

        conn = self._connect()
        if conn is None:
            LOGGER.warning("quality monitor skipped missing ledger db=%s", self.db_path)
            return None

        try:
            rows = self._fetch_alpha_rows(conn, normalized_id)
        finally:
            conn.close()

        if len(rows) < self.window_size:
            return None

        recent_rows = rows[-self.window_size :]
        historical_rows = rows[:-self.window_size]
        recent_values = [_safe_float(row.get("is_sharpe")) for row in recent_rows]
        historical_values = [_safe_float(row.get("is_sharpe")) for row in historical_rows]
        recent_values = [value for value in recent_values if value is not None]
        historical_values = [value for value in historical_values if value is not None]

        if len(recent_values) < self.window_size or not historical_values:
            return None

        recent_avg = self._mean(recent_values)
        historical_avg = self._mean(historical_values)
        if recent_avg is None or historical_avg is None:
            return None
        if historical_avg <= 0:
            return None

        drop_ratio = max(0.0, (historical_avg - recent_avg) / historical_avg)
        if drop_ratio <= self.degradation_threshold:
            return None

        return {
            "alpha_id": normalized_id,
            "recent_avg_sharpe": round(recent_avg, 6),
            "historical_avg_sharpe": round(historical_avg, 6),
            "drop_ratio": round(drop_ratio, 6),
            "window_size": self.window_size,
            "recent_count": len(recent_values),
            "historical_count": len(historical_values),
            "status": "degraded",
        }

    def check_all_alphas(self) -> list[dict[str, Any]]:
        """Scan the ledger and return all degradation alerts."""

        conn = self._connect()
        if conn is None:
            LOGGER.warning("quality monitor skipped missing ledger db=%s", self.db_path)
            return []

        try:
            cursor = conn.execute(
                """
                SELECT DISTINCT alpha_id
                FROM simulations
                WHERE alpha_id IS NOT NULL
                  AND TRIM(alpha_id) != ''
                ORDER BY alpha_id
                """
            )
            alpha_ids = [str(row[0]) for row in cursor.fetchall() if row[0] not in (None, "")]
        finally:
            conn.close()

        alerts: list[dict[str, Any]] = []
        for alpha_id in alpha_ids:
            alert = self.check_alpha(alpha_id)
            if alert is not None:
                alerts.append(alert)
        return alerts

    def save_alerts(self, alerts: list[dict[str, Any]], output_path: str = "runs/state/degradation_alerts.json") -> Path:
        """Persist alert output under runs/state/ without touching source files."""

        output = Path(output_path)
        if not output.is_absolute():
            output = (PROJECT_ROOT / output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "generated_at": _utc_now(),
            "generated_by": "harness.lib.quality_monitor.AlphaQualityMonitor",
            "provenance": {
                "db_path": str(self.db_path),
                "source": "runs/evidence/result_ledger.db",
                "window_size": self.window_size,
                "degradation_threshold": self.degradation_threshold,
            },
            "db_path": str(self.db_path),
            "window_size": self.window_size,
            "degradation_threshold": self.degradation_threshold,
            "alert_count": len(alerts),
            "alerts": alerts,
        }
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        LOGGER.info("saved degradation alerts path=%s count=%d", output, len(alerts))
        return output


def check_and_report(db_path: str = "runs/evidence/result_ledger.db") -> list[dict[str, Any]]:
    """Convenience helper: scan all alphas and write runs/state/degradation_alerts.json."""

    monitor = AlphaQualityMonitor(db_path=db_path)
    alerts = monitor.check_all_alphas()
    monitor.save_alerts(alerts)
    return alerts


__all__ = ["AlphaQualityMonitor", "check_and_report"]

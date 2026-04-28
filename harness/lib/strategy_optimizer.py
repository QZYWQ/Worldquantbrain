from __future__ import annotations

import copy
import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_PATH = PROJECT_ROOT / "runs" / "state" / "optimizer_state.json"
DEFAULT_PARAMETERS = {
    "exploration_rate": 0.3,
    "temperature": 0.7,
    "mutation_rate": 0.1,
}


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _resolve_state_path(state_path: str | Path) -> Path:
    path = Path(state_path).expanduser()
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _coerce_parameters(raw: Any) -> dict[str, float]:
    params = copy.deepcopy(DEFAULT_PARAMETERS)
    if not isinstance(raw, dict):
        return params
    for key in params:
        try:
            params[key] = float(raw.get(key, params[key]))
        except (TypeError, ValueError):
            continue
    return params


class StrategyOptimizer:
    def __init__(self, state_path: str | Path = "runs/state/optimizer_state.json") -> None:
        self.state_path = _resolve_state_path(state_path)
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                payload = json.loads(self.state_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    return {
                        "version": int(payload.get("version", 1)),
                        "window_size": int(payload.get("window_size", 5) or 5),
                        "current_parameters": _coerce_parameters(
                            payload.get("current_parameters") or payload.get("current_params")
                        ),
                        "history": list(payload.get("history", [])) if isinstance(payload.get("history"), list) else [],
                        "optimization_count": int(payload.get("optimization_count", 0) or 0),
                        "last_success_rate": float(payload.get("last_success_rate", 0.0) or 0.0),
                        "last_reason": str(payload.get("last_reason", "") or ""),
                        "updated_at": str(payload.get("updated_at", "") or ""),
                    }
            except (OSError, json.JSONDecodeError, ValueError):
                LOGGER.warning("strategy optimizer state is unreadable; starting fresh", exc_info=True)
        return {
            "version": 1,
            "window_size": 5,
            "current_parameters": copy.deepcopy(DEFAULT_PARAMETERS),
            "history": [],
            "optimization_count": 0,
            "last_success_rate": 0.0,
            "last_reason": "",
            "updated_at": "",
        }

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = copy.deepcopy(self.state)
        payload["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.state_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def get_current_parameters(self) -> dict[str, float]:
        return copy.deepcopy(self.state["current_parameters"])

    def reset(self) -> None:
        self.state = {
            "version": 1,
            "window_size": 5,
            "current_parameters": copy.deepcopy(DEFAULT_PARAMETERS),
            "history": [],
            "optimization_count": 0,
            "last_success_rate": 0.0,
            "last_reason": "reset",
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self._save_state()

    def _append_history(self, success_rate: float, reason: str) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "success_rate": round(success_rate, 6),
            "parameters": copy.deepcopy(self.state["current_parameters"]),
            "reason": reason,
        }
        history = self.state.setdefault("history", [])
        if not isinstance(history, list):
            history = []
            self.state["history"] = history
        history.append(entry)
        self.state["history"] = history[-200:]

    def _recent_average(self) -> float:
        history = self.state.get("history", [])
        if not history:
            return 0.0
        window_size = max(1, int(self.state.get("window_size", 5) or 5))
        recent = history[-window_size:]
        values = [float(item.get("success_rate", 0.0) or 0.0) for item in recent if isinstance(item, dict)]
        return sum(values) / len(values) if values else 0.0

    def _apply_adjustment(self, success_rate: float, average_success: float) -> tuple[dict[str, float], str]:
        current = copy.deepcopy(self.state["current_parameters"])
        reason = "stable"

        if average_success < 0.3 or success_rate < 0.25:
            current["exploration_rate"] = _clamp(current["exploration_rate"] * 1.15, 0.1, 0.7)
            current["temperature"] = _clamp(current["temperature"] * 1.10, 0.4, 1.4)
            current["mutation_rate"] = _clamp(current["mutation_rate"] * 1.20, 0.02, 0.4)
            reason = "increase_exploration"
        elif average_success > 0.6 or success_rate > 0.7:
            current["exploration_rate"] = _clamp(current["exploration_rate"] * 0.90, 0.05, 0.7)
            current["temperature"] = _clamp(current["temperature"] * 0.95, 0.35, 1.2)
            current["mutation_rate"] = _clamp(current["mutation_rate"] * 0.90, 0.01, 0.3)
            reason = "increase_exploitation"
        else:
            drift = success_rate - average_success
            if drift < -0.05:
                current["exploration_rate"] = _clamp(current["exploration_rate"] * 1.05, 0.05, 0.7)
                current["mutation_rate"] = _clamp(current["mutation_rate"] * 1.05, 0.01, 0.35)
                reason = "mild_exploration"
            elif drift > 0.05:
                current["exploration_rate"] = _clamp(current["exploration_rate"] * 0.97, 0.05, 0.7)
                current["mutation_rate"] = _clamp(current["mutation_rate"] * 0.97, 0.01, 0.35)
                reason = "mild_exploitation"
            current["temperature"] = _clamp(
                current["temperature"] * (0.99 if drift > 0 else 1.01),
                0.35,
                1.4,
            )

        for key in DEFAULT_PARAMETERS:
            if not math.isfinite(current[key]):
                current[key] = DEFAULT_PARAMETERS[key]
        return current, reason

    def optimize(self, current_success_rate: float) -> dict[str, float]:
        try:
            success_rate = float(current_success_rate)
        except (TypeError, ValueError):
            success_rate = 0.0
        if not math.isfinite(success_rate):
            success_rate = 0.0
        success_rate = _clamp(success_rate, 0.0, 1.0)

        self._append_history(success_rate, "batch_complete")
        average_success = self._recent_average()
        optimized, reason = self._apply_adjustment(success_rate, average_success)

        self.state["current_parameters"] = optimized
        self.state["optimization_count"] = int(self.state.get("optimization_count", 0) or 0) + 1
        self.state["last_success_rate"] = round(success_rate, 6)
        self.state["last_reason"] = reason
        self._save_state()

        LOGGER.info(
            "strategy optimizer updated rate=%.3f avg=%.3f reason=%s params=%s",
            success_rate,
            average_success,
            reason,
            json.dumps(optimized, sort_keys=True),
        )
        return copy.deepcopy(optimized)


__all__ = ["StrategyOptimizer"]

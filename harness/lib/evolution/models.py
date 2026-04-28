from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WinnerRecord:
    winner_id: str
    ledger_row_id: int
    alpha_id: str | None
    expression: str
    wqb_expression: str
    sharpe: float
    fitness: float
    turnover: float
    status: str
    tags: tuple[str, ...]
    timestamp: str
    field_name: str | None = None
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    operators: tuple[str, ...] = ()
    fields: tuple[str, ...] = ()
    parameters: tuple[dict[str, Any], ...] = ()
    score: float = 0.0


@dataclass(frozen=True)
class AlphaCandidate:
    candidate_id: str
    generation: int
    rank: int
    expression: str
    wqb_expression: str
    lineage: dict[str, Any]
    operators: tuple[str, ...]
    fields: tuple[str, ...]
    parameters: tuple[dict[str, Any], ...]
    surrogate_score: float
    expected_sharpe_estimate: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

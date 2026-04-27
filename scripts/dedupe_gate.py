#!/usr/bin/env python3
"""Local duplicate gate for candidate expressions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from result_ledger import (
    DEFAULT_LEDGER_PATH,
    ResultLedger,
    compare_expression_similarity,
    normalize_expression,
)


class DedupeGate:
    """Three-tier duplicate gate built on the local result ledger."""

    def __init__(self, ledger_path: Path = DEFAULT_LEDGER_PATH, structural_threshold: float = 0.7, recent_limit: int = 1000):
        self.ledger = ResultLedger(ledger_path)
        self.structural_threshold = structural_threshold
        self.recent_limit = recent_limit

    def _pick_match(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not rows:
            return {}
        for row in rows:
            if row.get("alpha_id"):
                return row
        return rows[0]

    def _exact_result(self, rows: List[Dict[str, Any]], candidate_expression: str, candidate_norm: str, field_name: str, source: str) -> Dict[str, Any]:
        matched = self._pick_match(rows)
        return {
            "is_duplicate": True,
            "matched_alpha_id": matched.get("alpha_id"),
            "similarity_score": 1.0,
            "match_level": "exact" if any(row.get("expression") == candidate_expression for row in rows) else "normalized",
            "recommendation": "skip",
            "warning": None,
            "candidate_expression": candidate_expression,
            "candidate_expression_normalized": candidate_norm,
            "field_name": field_name,
            "source": source,
            "matched_expression": matched.get("expression"),
            "matched_expression_normalized": matched.get("expression_normalized"),
            "matched_source": matched.get("source"),
        }

    def check(self, expression: str, field_name: str, source: str) -> Dict[str, Any]:
        candidate_norm = normalize_expression(expression)
        exact_rows = self.ledger.get_by_expression(expression)
        if exact_rows:
            return self._exact_result(exact_rows, expression, candidate_norm, field_name, source)

        normalized_rows = self.ledger.get_by_normalized_expression(candidate_norm)
        if normalized_rows:
            return self._exact_result(normalized_rows, expression, candidate_norm, field_name, source)

        best_row: Optional[Dict[str, Any]] = None
        best_breakdown: Optional[Dict[str, float]] = None
        best_score = -1.0
        for row in self.ledger.get_recent_expressions(limit=self.recent_limit):
            breakdown = compare_expression_similarity(expression, str(row.get("expression") or ""))
            score = breakdown["score"]
            if score > best_score:
                best_score = score
                best_breakdown = breakdown
                best_row = row

        if best_row is not None and best_breakdown is not None and best_score >= self.structural_threshold:
            warning = (
                "structural similarity {:.3f} >= {:.2f}; review before promoting".format(
                    best_score,
                    self.structural_threshold,
                )
            )
            return {
                "is_duplicate": False,
                "matched_alpha_id": best_row.get("alpha_id"),
                "similarity_score": round(best_score, 6),
                "match_level": "structural",
                "recommendation": "proceed",
                "warning": warning,
                "candidate_expression": expression,
                "candidate_expression_normalized": candidate_norm,
                "field_name": field_name,
                "source": source,
                "matched_expression": best_row.get("expression"),
                "matched_expression_normalized": best_row.get("expression_normalized"),
                "matched_source": best_row.get("source"),
                "similarity_breakdown": best_breakdown,
            }

        return {
            "is_duplicate": False,
            "matched_alpha_id": best_row.get("alpha_id") if best_row else None,
            "similarity_score": round(max(best_score, 0.0), 6),
            "match_level": "none",
            "recommendation": "proceed",
            "warning": None,
            "candidate_expression": expression,
            "candidate_expression_normalized": candidate_norm,
            "field_name": field_name,
            "source": source,
            "matched_expression": best_row.get("expression") if best_row else None,
            "matched_expression_normalized": best_row.get("expression_normalized") if best_row else None,
            "matched_source": best_row.get("source") if best_row else None,
            "similarity_breakdown": best_breakdown,
        }

    def add_to_ledger(self, expression: str, field_name: str, result_data: Dict[str, Any]) -> int:
        payload = dict(result_data or {})
        payload.setdefault("expression", expression)
        payload.setdefault("expression_normalized", normalize_expression(expression))
        payload.setdefault("field_name", field_name)
        return self.ledger.insert_result(payload)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local dedupe gate.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Check whether an expression is a duplicate.")
    check.add_argument("--expression", required=True)
    check.add_argument("--field", required=True)
    check.add_argument("--source", default="manual")
    check.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    check.add_argument("--recent-limit", type=int, default=1000)

    add = subparsers.add_parser("add", help="Insert a post-S0 result into the ledger.")
    add.add_argument("--expression", required=True)
    add.add_argument("--field", required=True)
    add.add_argument("--source", default="manual")
    add.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    add.add_argument("--result-json", default="{}", help="JSON object containing additional result fields.")

    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    if args.command == "check":
        gate = DedupeGate(args.ledger, recent_limit=args.recent_limit)
        result = gate.check(args.expression, args.field, args.source)
        print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "add":
        try:
            result_data = json.loads(args.result_json)
        except json.JSONDecodeError as exc:
            raise SystemExit("--result-json must be valid JSON: %s" % exc)
        if not isinstance(result_data, dict):
            raise SystemExit("--result-json must decode to an object")
        gate = DedupeGate(args.ledger)
        row_id = gate.add_to_ledger(args.expression, args.field, result_data)
        print(json.dumps({"inserted_id": row_id, "ledger": str(args.ledger)}, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

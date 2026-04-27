#!/usr/bin/env python3
"""SQLite result ledger for local alpha research."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_LEDGER_PATH = Path(os.environ.get("RESULT_LEDGER_PATH", "runs/evidence/result_ledger.db"))
UNKNOWN_EXPR_PLACEHOLDER = "__expression_incomplete__"
RESERVED_WORDS = {
    "and",
    "or",
    "not",
    "if",
    "else",
    "true",
    "false",
    "null",
}
TOKEN_RE = re.compile(r"==|!=|<=|>=|[A-Za-z_][A-Za-z0-9_]*|[0-9]+(?:\.[0-9]+)?|[+\-*/^<>,()]")
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
OPERATOR_SYMBOLS = {"+", "-", "*", "/", "^", "<", ">", "<=", ">=", "==", "!=", ","}


def _ensure_path(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _is_balanced_wrapper(expr: str) -> bool:
    depth = 0
    for index, char in enumerate(expr):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return False
            if depth == 0 and index != len(expr) - 1:
                return False
    return depth == 0


def _strip_outer_parens(expr: str) -> str:
    while len(expr) >= 2 and expr.startswith("(") and expr.endswith(")"):
        inner = expr[1:-1]
        if not inner:
            break
        if _is_balanced_wrapper(inner):
            expr = inner
            continue
        break
    return expr


def normalize_expression(expression: str) -> str:
    """Canonicalize a Fast Expression enough for duplicate checks."""
    expr = (expression or "").strip()
    if not expr:
        return UNKNOWN_EXPR_PLACEHOLDER
    expr = re.sub(r"\s+", "", expr)
    expr = _strip_outer_parens(expr)
    expr = re.sub(r"^\-1\*", "-", expr)
    expr = re.sub(r"^\+1\*", "", expr)
    expr = re.sub(r"^1\*", "", expr)
    expr = _strip_outer_parens(expr)
    return expr


def tokenize_expression(expression: str) -> List[str]:
    return TOKEN_RE.findall(normalize_expression(expression))


def _is_identifier(token: str) -> bool:
    return bool(IDENT_RE.match(token))


def extract_operator_tokens(tokens: Sequence[str]) -> List[str]:
    operators: List[str] = []
    for index, token in enumerate(tokens):
        next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
        if _is_identifier(token) and next_token == "(":
            operators.append(token)
        elif token in OPERATOR_SYMBOLS:
            operators.append(token)
    return operators


def extract_field_tokens(tokens: Sequence[str]) -> List[str]:
    fields: List[str] = []
    for index, token in enumerate(tokens):
        next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
        if not _is_identifier(token):
            continue
        if next_token == "(":
            continue
        if token in RESERVED_WORDS:
            continue
        fields.append(token)
    return fields


def extract_structure_signature(tokens: Sequence[str]) -> Tuple[List[str], int]:
    sequence: List[str] = []
    paren_depth = 0
    max_depth = 0
    index = 0
    while index < len(tokens):
        token = tokens[index]
        next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
        if _is_identifier(token) and next_token == "(":
            sequence.append(f"{paren_depth}:{token}")
            paren_depth += 1
            max_depth = max(max_depth, paren_depth)
            index += 2
            continue
        if token == "(":
            paren_depth += 1
            max_depth = max(max_depth, paren_depth)
        elif token == ")":
            paren_depth = max(paren_depth - 1, 0)
        index += 1
    return sequence, max_depth


def _sequence_edit_distance(a: Sequence[str], b: Sequence[str]) -> int:
    if not a:
        return len(b)
    if not b:
        return len(a)
    previous = list(range(len(b) + 1))
    for i, token_a in enumerate(a, start=1):
        current = [i]
        for j, token_b in enumerate(b, start=1):
            cost = 0 if token_a == token_b else 1
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost))
        previous = current
    return previous[-1]


def _sequence_similarity(a: Sequence[str], b: Sequence[str]) -> float:
    if not a and not b:
        return 1.0
    denominator = float(max(len(a), len(b), 1))
    return max(0.0, 1.0 - (_sequence_edit_distance(a, b) / denominator))


def _lcs_length(a: str, b: str) -> int:
    if not a or not b:
        return 0
    previous = [0] * (len(b) + 1)
    for char_a in a:
        current = [0]
        for index, char_b in enumerate(b, start=1):
            if char_a == char_b:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[-1]))
        previous = current
    return previous[-1]


def _string_similarity(candidate_norm: str, existing_norm: str) -> float:
    if not candidate_norm and not existing_norm:
        return 1.0
    denominator = float(len(candidate_norm) + len(existing_norm))
    if denominator == 0:
        return 1.0
    return (2.0 * _lcs_length(candidate_norm, existing_norm)) / denominator


def _jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set and not right_set:
        return 1.0
    union = left_set | right_set
    if not union:
        return 1.0
    return len(left_set & right_set) / float(len(union))


def _depth_similarity(left_depth: int, right_depth: int) -> float:
    if left_depth == 0 and right_depth == 0:
        return 1.0
    denominator = float(max(left_depth, right_depth, 1))
    return max(0.0, 1.0 - abs(left_depth - right_depth) / denominator)


def compare_expression_similarity(candidate_expression: str, existing_expression: str) -> Dict[str, float]:
    candidate_norm = normalize_expression(candidate_expression)
    existing_norm = normalize_expression(existing_expression)
    candidate_tokens = tokenize_expression(candidate_expression)
    existing_tokens = tokenize_expression(existing_expression)
    candidate_ops = extract_operator_tokens(candidate_tokens)
    existing_ops = extract_operator_tokens(existing_tokens)
    candidate_fields = extract_field_tokens(candidate_tokens)
    existing_fields = extract_field_tokens(existing_tokens)
    candidate_struct, candidate_depth = extract_structure_signature(candidate_tokens)
    existing_struct, existing_depth = extract_structure_signature(existing_tokens)

    string_similarity = _string_similarity(candidate_norm, existing_norm)
    operator_similarity = _jaccard(candidate_ops, existing_ops)
    field_similarity = _jaccard(candidate_fields, existing_fields)
    structural_sequence_similarity = _sequence_similarity(candidate_struct, existing_struct)
    structural_depth_similarity = _depth_similarity(candidate_depth, existing_depth)
    structural_similarity = (0.7 * structural_sequence_similarity) + (0.3 * structural_depth_similarity)
    score = (
        0.4 * string_similarity
        + 0.3 * operator_similarity
        + 0.2 * field_similarity
        + 0.1 * structural_similarity
    )
    return {
        "string_similarity": round(string_similarity, 6),
        "operator_similarity": round(operator_similarity, 6),
        "field_similarity": round(field_similarity, 6),
        "structural_similarity": round(structural_similarity, 6),
        "score": round(score, 6),
    }


def _first_present(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return value
    return None


def _nested_metric(alpha: Dict[str, Any], keys: Sequence[str], nested_sources: Sequence[str]) -> Any:
    for source_name in nested_sources:
        source = alpha.get(source_name)
        if isinstance(source, dict):
            value = _first_present(*[source.get(key) for key in keys])
            if value is not None:
                return value
    return _first_present(*[alpha.get(key) for key in keys])


def _normalize_stage(raw_stage: Any, topic: str, capture_id: str, file_path: Path) -> Optional[str]:
    if raw_stage is not None and str(raw_stage).strip():
        stage = str(raw_stage).strip().upper()
        if stage == "IS":
            return "S0"
        if stage in {"S0", "B", "C", "D", "E"}:
            return stage
        if stage in {"SCREEN_KILL", "KILL"}:
            return "E"
    text = " ".join([topic or "", capture_id or "", file_path.stem]).lower()
    if "delay0" in text or "delay-0" in text or "d-stage" in text:
        return "D"
    if "e-stage" in text or "repair" in text or "rescue" in text:
        return "E"
    if "c-stage" in text or "hybrid" in text:
        return "C"
    if "b-stage" in text or "branch" in text:
        return "B"
    if "baseline" in text or "s0" in text or "prescreen" in text or "recheck" in text or "probe" in text:
        return "S0"
    return None


def _normalize_status(alpha: Dict[str, Any], capture: Dict[str, Any], text_blob: str) -> str:
    raw_status = str(alpha.get("status") or capture.get("status") or "").strip().upper()
    tests = alpha.get("tests") if isinstance(alpha.get("tests"), dict) else {}
    decision = str(capture.get("decision") or "").strip().upper()
    if raw_status in {"SCREEN_KILL", "KILL"} or "screen kill" in text_blob:
        return "screen_kill"
    if raw_status in {"BLOCKED"} or "unknown variable" in text_blob or "delay0" in text_blob or "delay-0" in text_blob:
        return "hold"
    if raw_status in {"PASS", "SUBMIT_READY", "READY"}:
        return "pass"
    if tests.get("check_submission_pass") is True:
        return "pass"
    if bool(alpha.get("submit_ready")) is True:
        return "pass"
    if decision in {"PASS", "READY", "SUBMIT_READY"}:
        return "pass"
    if raw_status in {"FAILED", "FAIL"}:
        return "fail"
    if tests.get("check_submission_pass") is False:
        return "fail"
    failing_gates = alpha.get("failing_gates")
    if isinstance(failing_gates, list) and failing_gates:
        return "fail"
    if isinstance(failing_gates, tuple) and failing_gates:
        return "fail"
    return "hold"


def _metric_summary(alpha: Dict[str, Any]) -> Dict[str, Optional[float]]:
    metrics = alpha.get("metrics") if isinstance(alpha.get("metrics"), dict) else {}
    train = alpha.get("train") if isinstance(alpha.get("train"), dict) else {}
    test = alpha.get("test") if isinstance(alpha.get("test"), dict) else {}
    return {
        "is_sharpe": _safe_float(_nested_metric(alpha, ("is_sharpe", "sharpe"), ("metrics", "train"))),
        "is_fitness": _safe_float(_nested_metric(alpha, ("is_fitness", "fitness"), ("metrics", "train"))),
        "test_sharpe": _safe_float(_nested_metric(alpha, ("test_sharpe", "sharpe"), ("metrics", "test"))),
        "test_fitness": _safe_float(_nested_metric(alpha, ("test_fitness", "fitness"), ("metrics", "test"))),
        "turnover": _safe_float(_nested_metric(alpha, ("test_turnover", "is_turnover", "turnover"), ("metrics", "test", "train"))),
        "max_weight": _safe_float(_nested_metric(alpha, ("max_weight",), ("metrics", "test", "train"))),
        "self_corr": _safe_float(_nested_metric(alpha, ("self_corr",), ("metrics", "test", "train"))),
        "is_returns": _safe_float(_nested_metric(alpha, ("is_returns", "returns"), ("metrics", "train"))),
        "test_returns": _safe_float(_nested_metric(alpha, ("test_returns", "returns"), ("metrics", "test"))),
    }


def _infer_risk_tags(alpha: Dict[str, Any], capture: Dict[str, Any], text_blob: str) -> List[str]:
    tags = set()
    metrics = _metric_summary(alpha)
    tests = alpha.get("tests") if isinstance(alpha.get("tests"), dict) else {}
    if any(value is not None and value < 1.0 for key, value in metrics.items() if key in {"is_fitness", "test_fitness"}):
        tags.add("LOW_FITNESS")
    if any(value is not None and value < 0.5 for key, value in metrics.items() if key in {"is_sharpe", "test_sharpe"}):
        tags.add("LOW_SHARPE")
    if metrics.get("turnover") is not None and metrics["turnover"] > 0.8:
        tags.add("HIGH_TURNOVER")
    if metrics.get("max_weight") is not None and metrics["max_weight"] > 0.15:
        tags.add("HIGH_WEIGHT")
    if metrics.get("self_corr") is not None and metrics["self_corr"] > 0.7:
        tags.add("SELF_CORR_RISK")
    if tests.get("subuniverse_pass") is False:
        tags.add("COVERAGE_RISK")
    if tests.get("check_submission_pass") is False:
        tags.add("CHECK_SUBMISSION_FAIL")
    if "delay0" in text_blob or "delay-0" in text_blob:
        tags.add("DELAY_0_BLOCKED")
    if "unknown variable" in text_blob:
        tags.add("UNKNOWN_VARIABLE")
    if alpha.get("error"):
        tags.add("EXECUTION_ERROR")
    if "coverage" in text_blob and ("low" in text_blob or "insufficient" in text_blob or "missing" in text_blob):
        tags.add("COVERAGE_RISK")
    if "low fitness" in text_blob:
        tags.add("LOW_FITNESS")
    if "high turnover" in text_blob:
        tags.add("HIGH_TURNOVER")
    if alpha.get("status") == "SCREEN_KILL" or capture.get("decision") == "screen-kill":
        tags.add("SCREEN_KILL")
    return sorted(tags)


class ResultLedger:
    """SQLite store for historical simulation results."""

    def __init__(self, db_path: Path = DEFAULT_LEDGER_PATH):
        self.db_path = Path(db_path)
        _ensure_path(self.db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "ResultLedger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _ensure_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alpha_id TEXT,
                expression TEXT NOT NULL,
                expression_normalized TEXT NOT NULL,
                field_name TEXT,
                source TEXT,
                stage TEXT,
                decay INTEGER,
                neutralization TEXT,
                is_sharpe REAL,
                is_fitness REAL,
                test_sharpe REAL,
                test_fitness REAL,
                turnover REAL,
                status TEXT,
                tags TEXT,
                timestamp TEXT DEFAULT (datetime('now')),
                raw_json TEXT,
                capture_id TEXT,
                file_path TEXT,
                test_period TEXT,
                region TEXT,
                universe TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_simulations_expression ON simulations(expression);
            CREATE INDEX IF NOT EXISTS idx_simulations_expression_norm ON simulations(expression_normalized);
            CREATE INDEX IF NOT EXISTS idx_simulations_field_name ON simulations(field_name);
            CREATE INDEX IF NOT EXISTS idx_simulations_stage ON simulations(stage);
            CREATE INDEX IF NOT EXISTS idx_simulations_status ON simulations(status);
            CREATE INDEX IF NOT EXISTS idx_simulations_timestamp ON simulations(timestamp);
            """
        )
        self.conn.commit()

    def reset(self) -> None:
        self.conn.execute("DELETE FROM simulations")
        self.conn.commit()

    def insert_result(self, data: Dict[str, Any]) -> int:
        expression = str(data.get("expression") or UNKNOWN_EXPR_PLACEHOLDER)
        expression_normalized = str(data.get("expression_normalized") or normalize_expression(expression))
        tags_value = data.get("tags")
        if isinstance(tags_value, str):
            tags_text = tags_value
        elif tags_value is None:
            tags_text = _json_text([])
        else:
            tags_text = _json_text(tags_value)
        raw_json_value = data.get("raw_json")
        if isinstance(raw_json_value, str):
            raw_json_text = raw_json_value
        elif raw_json_value is None:
            raw_json_text = None
        else:
            raw_json_text = _json_text(raw_json_value)

        payload = {
            "alpha_id": data.get("alpha_id"),
            "expression": expression,
            "expression_normalized": expression_normalized,
            "field_name": data.get("field_name"),
            "source": data.get("source"),
            "stage": data.get("stage"),
            "decay": _safe_int(data.get("decay")),
            "neutralization": data.get("neutralization"),
            "is_sharpe": _safe_float(data.get("is_sharpe")),
            "is_fitness": _safe_float(data.get("is_fitness")),
            "test_sharpe": _safe_float(data.get("test_sharpe")),
            "test_fitness": _safe_float(data.get("test_fitness")),
            "turnover": _safe_float(data.get("turnover")),
            "status": data.get("status"),
            "tags": tags_text,
            "timestamp": data.get("timestamp") or datetime.now().isoformat(timespec="seconds"),
            "raw_json": raw_json_text,
            "capture_id": data.get("capture_id"),
            "file_path": data.get("file_path"),
            "test_period": data.get("test_period"),
            "region": data.get("region"),
            "universe": data.get("universe"),
        }
        cursor = self.conn.execute(
            """
            INSERT INTO simulations (
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
                test_sharpe,
                test_fitness,
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
            ) VALUES (
                :alpha_id,
                :expression,
                :expression_normalized,
                :field_name,
                :source,
                :stage,
                :decay,
                :neutralization,
                :is_sharpe,
                :is_fitness,
                :test_sharpe,
                :test_fitness,
                :turnover,
                :status,
                :tags,
                :timestamp,
                :raw_json,
                :capture_id,
                :file_path,
                :test_period,
                :region,
                :universe
            )
            """,
            payload,
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def _fetch_rows(self, query: str, params: Sequence[Any]) -> List[Dict[str, Any]]:
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_by_expression(self, expr: str) -> List[Dict[str, Any]]:
        return self._fetch_rows(
            "SELECT * FROM simulations WHERE expression = ? ORDER BY id DESC",
            (expr,),
        )

    def get_by_normalized_expression(self, expr_norm: str) -> List[Dict[str, Any]]:
        return self._fetch_rows(
            "SELECT * FROM simulations WHERE expression_normalized = ? ORDER BY id DESC",
            (expr_norm,),
        )

    def get_by_field(self, field: str) -> List[Dict[str, Any]]:
        return self._fetch_rows(
            "SELECT * FROM simulations WHERE field_name = ? ORDER BY id DESC",
            (field,),
        )

    def get_recent_expressions(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._fetch_rows(
            "SELECT * FROM simulations ORDER BY id DESC LIMIT ?",
            (int(limit),),
        )

    def get_stats(self) -> Dict[str, Any]:
        cursor = self.conn.execute("SELECT status, stage, tags FROM simulations")
        rows = cursor.fetchall()
        total = len(rows)
        status_counts = Counter()
        stage_counts = Counter()
        tag_counts = Counter()
        for row in rows:
            status_counts[str(row["status"] or "unknown")] += 1
            stage_counts[str(row["stage"] or "unknown")] += 1
            tags_raw = row["tags"]
            if tags_raw:
                try:
                    tags = json.loads(tags_raw)
                    if isinstance(tags, list):
                        tag_counts.update(str(tag) for tag in tags)
                except (TypeError, ValueError, json.JSONDecodeError):
                    continue
        pass_count = status_counts.get("pass", 0)
        return {
            "total_records": total,
            "pass_count": pass_count,
            "pass_rate": round((pass_count / total) if total else 0.0, 6),
            "status_distribution": dict(status_counts),
            "stage_distribution": dict(stage_counts),
            "tag_distribution": dict(tag_counts),
            "db_path": str(self.db_path),
        }

    def backfill_capture_dir(self, capture_dir: Path, reset: bool = False) -> Dict[str, Any]:
        capture_dir = Path(capture_dir)
        if reset:
            self.reset()
        capture_files = sorted(capture_dir.rglob("*.json"))
        summary = {
            "capture_dir": str(capture_dir),
            "capture_files": 0,
            "alpha_rows": 0,
            "inserted_rows": 0,
            "skipped_rows": 0,
            "parse_errors": [],
            "status_distribution": {},
            "stage_distribution": {},
        }
        status_counter = Counter()
        stage_counter = Counter()
        inserted = 0
        skipped = 0

        for path in capture_files:
            summary["capture_files"] += 1
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:  # pragma: no cover - summarized in return payload
                summary["parse_errors"].append({"file": str(path), "error": str(exc)})
                skipped += 1
                continue
            if not isinstance(payload, dict):
                summary["parse_errors"].append({"file": str(path), "error": "top-level JSON is not an object"})
                skipped += 1
                continue
            alphas = payload.get("alphas")
            if not isinstance(alphas, list):
                summary["parse_errors"].append({"file": str(path), "error": "missing alphas list"})
                skipped += 1
                continue
            capture_id = str(payload.get("capture_id") or path.stem)
            topic = str(payload.get("topic") or capture_id)
            capture_mode = payload.get("capture_mode")
            platform_settings = payload.get("platform_settings") if isinstance(payload.get("platform_settings"), dict) else {}
            test_period = platform_settings.get("testPeriod") or platform_settings.get("test_period")
            region = platform_settings.get("region")
            universe = platform_settings.get("universe")
            decay = _safe_int(platform_settings.get("decay"))
            neutralization = platform_settings.get("neutralization")
            captured_at = payload.get("captured_at")

            for index, alpha in enumerate(alphas):
                summary["alpha_rows"] += 1
                if not isinstance(alpha, dict):
                    skipped += 1
                    continue
                expression = str(alpha.get("expression") or "").strip()
                if not expression:
                    expression = UNKNOWN_EXPR_PLACEHOLDER
                metrics = _metric_summary(alpha)
                text_blob = " ".join(
                    str(part)
                    for part in (
                        payload.get("topic"),
                        payload.get("capture_id"),
                        path.stem,
                        alpha.get("name"),
                        alpha.get("status"),
                        alpha.get("error"),
                        payload.get("decision"),
                        payload.get("capture_mode"),
                        json.dumps(payload.get("evidence"), ensure_ascii=False) if payload.get("evidence") is not None else "",
                        json.dumps(alpha.get("notes"), ensure_ascii=False) if alpha.get("notes") is not None else "",
                    )
                    if part is not None
                ).lower()
                row = {
                    "alpha_id": alpha.get("alpha_id"),
                    "expression": expression,
                    "expression_normalized": normalize_expression(expression),
                    "field_name": topic,
                    "source": capture_id,
                    "stage": _normalize_stage(alpha.get("stage"), topic, capture_id, path),
                    "decay": decay,
                    "neutralization": neutralization,
                    "is_sharpe": metrics["is_sharpe"],
                    "is_fitness": metrics["is_fitness"],
                    "test_sharpe": metrics["test_sharpe"],
                    "test_fitness": metrics["test_fitness"],
                    "turnover": metrics["turnover"],
                    "status": _normalize_status(alpha, payload, text_blob),
                    "tags": _infer_risk_tags(alpha, payload, text_blob),
                    "timestamp": captured_at or datetime.now().isoformat(timespec="seconds"),
                    "raw_json": {"capture": payload, "alpha": alpha, "file_path": str(path), "capture_mode": capture_mode},
                    "capture_id": capture_id,
                    "file_path": str(path),
                    "test_period": test_period,
                    "region": region,
                    "universe": universe,
                }
                inserted += 1
                status_counter[row["status"]] += 1
                stage_counter[str(row["stage"] or "unknown")] += 1
                self.insert_result(row)
        summary["inserted_rows"] = inserted
        summary["skipped_rows"] = skipped
        summary["status_distribution"] = dict(status_counter)
        summary["stage_distribution"] = dict(stage_counter)
        return summary


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Result ledger helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backfill = subparsers.add_parser("backfill", help="Backfill the SQLite ledger from simulation captures.")
    backfill.add_argument("--capture-dir", type=Path, default=Path("runs/simulation-captures"))
    backfill.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    backfill.add_argument("--reset", action="store_true", help="Clear the ledger before inserting rows.")

    stats = subparsers.add_parser("stats", help="Print basic ledger statistics.")
    stats.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)

    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    if args.command == "backfill":
        with ResultLedger(args.ledger) as ledger:
            summary = ledger.backfill_capture_dir(args.capture_dir, reset=args.reset)
            summary["ledger"] = str(args.ledger)
            print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "stats":
        with ResultLedger(args.ledger) as ledger:
            print(json.dumps(ledger.get_stats(), indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

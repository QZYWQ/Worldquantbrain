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
from pathlib import Path
from typing import Any, Iterable

from dedupe_gate import DedupeGate

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


class BatchS0Scanner:
    def __init__(
        self,
        fields_path: str | Path,
        top: int = 3,
        max_simulations: int = 50,
        run_mode: str = "dry",
    ) -> None:
        self.project_root = get_project_root()
        self.fields_path = self._resolve_path(fields_path)
        self.top = top
        self.max_simulations = max_simulations
        self.run_mode = run_mode
        self.ledger_path = self._resolve_path("runs/evidence/result_ledger.db")
        self.log_path = self._resolve_path("runs/evidence/batch_s0_scan.log")
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
            final_score = (
                self.sort_weights["alpha_count"] * (1.0 / (alpha_count + 1))
                + self.sort_weights["coverage"] * coverage
                + self.sort_weights["template_complexity"] * complexity_score
            )
            record = dict(candidate)
            record["final_score"] = round(final_score, 6)
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
        return weighted

    def print_dry_run_plan(self, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        planned = candidates[: self.max_simulations]
        top_recommendations = planned[: self.top]

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
            self.logger.info("--- top %d ---", self.top)
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
        planned = candidates[: self.max_simulations]
        self.logger.info("live mode placeholder start")
        self.logger.info("planned_candidates=%d", len(planned))
        self.logger.info("submit cadence: wait 30s before each submission, add 120s after every 5th submission")

        for index, candidate in enumerate(planned, start=1):
            self.logger.info(
                "[LIVE PLACEHOLDER] candidate=%s rank=%d expr=%s neut=%s",
                candidate["candidate_id"],
                index,
                candidate["expression"],
                candidate["neut"] if candidate["neut"] is not None else "None",
            )
            # PLACEHOLDER: submit_single_simulation(expression, neutralization)
            # PLACEHOLDER: parse_simulation_response(response)
            # PLACEHOLDER: write_result_to_result_ledger(alpha_id, result)
            # PLACEHOLDER: handle_429_rate_limit()
            # PLACEHOLDER: handle_401_reauth()
            # PLACEHOLDER: time.sleep(30) before each submission
            # PLACEHOLDER: time.sleep(120) after every 5th submission
        self.logger.info("live mode placeholder end")
        return {
            "mode": "live-placeholder",
            "planned": len(planned),
            "submitted": 0,
            "top": min(self.top, len(planned)),
        }

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
    )
    summary = scanner.run()
    scanner.logger.info("summary=%s", json.dumps(summary, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

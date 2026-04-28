from __future__ import annotations

import ast
import json
import random
from dataclasses import replace
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

try:  # pragma: no cover - dual import path for script/package execution
    from harness.lib.compiler import canonicalize_expression, compile_alpha, extract_components
except ImportError:  # pragma: no cover
    from compiler import canonicalize_expression, compile_alpha, extract_components

from .crossover import crossover as crossover_expression
from .models import AlphaCandidate, WinnerRecord
from .mutation import mutate as mutate_expression
from .population import export_generation, load_winners_from_ledger, structural_fingerprint
from .selection import rank_population, tournament_select


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class BrainEvolutionEngine:
    def __init__(
        self,
        db_path: str = "runs/evidence/result_ledger.db",
        population_size: int = 20,
        elite_fraction: float = 0.1,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        output_dir: str = "runs/evolution/generations",
        config_path: str = "harness/lib/evolution/evolution_config.json",
        seed: int | None = None,
    ) -> None:
        self.db_path = self._resolve_path(db_path)
        self.population_size = int(population_size)
        self.elite_fraction = float(elite_fraction)
        self.mutation_rate = float(mutation_rate)
        self.crossover_rate = float(crossover_rate)
        self.output_dir = self._resolve_path(output_dir)
        self.config_path = self._resolve_path(config_path)
        self.config = self._load_config()
        self.config["population_size"] = self.population_size
        self.config["elite_fraction"] = self.elite_fraction
        self.config["mutation_rate"] = self.mutation_rate
        self.config["crossover_rate"] = self.crossover_rate
        self.config.setdefault("output", {})
        self.config["output"]["root"] = str(self.output_dir)
        if seed is None and self.config.get("seed") is not None:
            seed = self.config.get("seed")
        self.seed = seed
        if self.seed is not None:
            self.config["seed"] = self.seed
        self.rng = random.Random(self.seed)
        self.winners: list[WinnerRecord] = []
        self.population: list[AlphaCandidate] = []
        self.known_fields: tuple[str, ...] = ()
        self._archive_fingerprints: set[str] = set()
        self._population_fingerprints: set[str] = set()
        self._archive_exact_expressions: set[str] = set()
        self._population_exact_expressions: set[str] = set()
        self._last_generation_metrics: dict[str, Any] = {}
        self.generation = 0

    def _resolve_path(self, path: str | Path) -> Path:
        candidate = Path(path).expanduser()
        if candidate.is_absolute():
            return candidate
        return (PROJECT_ROOT / candidate).resolve()

    def _load_config(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def load_winners(self) -> list[WinnerRecord]:
        self.winners = load_winners_from_ledger(self.db_path, self.config)
        self.known_fields = tuple(
            str(item).strip()
            for item in (self.config.get("known_fields") or [])
            if isinstance(item, str) and str(item).strip()
        )
        self._archive_fingerprints = {
            str(item).strip()
            for item in (self.config.get("archive_fingerprints") or [])
            if isinstance(item, str) and str(item).strip()
        }
        self._archive_exact_expressions = {
            str(winner.wqb_expression or winner.expression).strip()
            for winner in self.winners
            if str(winner.wqb_expression or winner.expression).strip()
        }
        return list(self.winners)

    def _candidate_id(
        self,
        *,
        generation: int,
        expression: str,
        method: str,
        parent_ids: tuple[str, ...],
    ) -> str:
        digest_input = "|".join(
            [
                str(generation),
                method,
                expression,
                *[item for item in parent_ids if item],
            ]
        )
        digest = sha256(digest_input.encode("utf-8")).hexdigest()[:12]
        return f"gen{generation:03d}-{digest}"

    def _fingerprint_token_set(self, fingerprint: str) -> set[str]:
        if not fingerprint:
            return set()
        operator_key, _, field_key = fingerprint.partition("|")
        tokens = {f"op:{item}" for item in operator_key.split(",") if item}
        tokens.update({f"field:{item}" for item in field_key.split(",") if item})
        return tokens

    def _structural_similarity(self, candidate_tokens: set[str], fingerprint: str) -> float:
        reference_tokens = self._fingerprint_token_set(fingerprint)
        if not candidate_tokens and not reference_tokens:
            return 1.0
        union = candidate_tokens | reference_tokens
        if not union:
            return 1.0
        return len(candidate_tokens & reference_tokens) / len(union)

    def _score_weights(self) -> dict[str, float]:
        weights = self.config.get("score_weights") if isinstance(self.config.get("score_weights"), dict) else {}
        return {
            "base": max(0.0, float(weights.get("base") or 0.4)),
            "novelty": max(0.0, float(weights.get("novelty") or 0.3)),
            "complexity": max(0.0, float(weights.get("complexity") or 0.2)),
            "risk": max(0.0, float(weights.get("risk") or 0.1)),
        }

    def _complexity_weights(self) -> dict[str, float]:
        weights = self.config.get("complexity_weights") if isinstance(self.config.get("complexity_weights"), dict) else {}
        return {
            "operator": max(0.0, float(weights.get("operator") or 0.1)),
            "field": max(0.0, float(weights.get("field") or 0.05)),
            "parameter": max(0.0, float(weights.get("parameter") or 0.02)),
        }

    def _has_trivial_identity_operation(self, expression: str) -> bool:
        source = canonicalize_expression(expression)
        if not source:
            return False
        try:
            tree = ast.parse(source, mode="eval")
        except SyntaxError:
            return False

        for node in ast.walk(tree):
            if not isinstance(node, ast.BinOp):
                continue
            if not isinstance(node.op, (ast.Div, ast.Sub)):
                continue
            try:
                left = ast.unparse(node.left).strip()
                right = ast.unparse(node.right).strip()
            except Exception:
                continue
            if left and left == right:
                return True
        return False

    def _compute_novelty(
        self,
        expression: str,
        *,
        component_result: dict[str, Any] | None = None,
        archive_fingerprints: set[str] | None = None,
        population_fingerprints: set[str] | None = None,
    ) -> float:
        if component_result is None:
            component_result = extract_components(expression)
        operators = {str(item) for item in (component_result.get("operators") or []) if str(item)}
        fields = {str(item) for item in (component_result.get("fields") or []) if str(item)}
        candidate_tokens = {f"op:{item}" for item in operators} | {f"field:{item}" for item in fields}
        references = list(archive_fingerprints or self._archive_fingerprints)
        if not references:
            references = list(population_fingerprints or self._population_fingerprints)
        if not references:
            return 1.0
        max_similarity = max(self._structural_similarity(candidate_tokens, fingerprint) for fingerprint in references)
        return max(0.0, 1.0 - max_similarity)

    def _complexity_penalty(
        self,
        operators: tuple[str, ...],
        fields: tuple[str, ...],
        parameters: tuple[dict[str, Any], ...],
        expression: str,
    ) -> float:
        weights = self._complexity_weights()
        operator_count = len(operators)
        field_count = len(fields)
        parameter_count = len(parameters)
        return (
            operator_count * weights["operator"]
            + field_count * weights["field"]
            + parameter_count * weights["parameter"]
        )

    def _risk_penalty(self, method: str) -> float:
        method_key = str(method or "").lower()
        if method_key == "elite":
            return 0.0
        if "mutation" in method_key:
            return 0.15
        if "crossover" in method_key:
            return 0.08
        if "seed" in method_key:
            return 0.02
        return 0.05

    def _base_score(self, parents: tuple[AlphaCandidate, ...], source: WinnerRecord | None = None) -> float:
        if parents:
            scores = [float(parent.surrogate_score) for parent in parents if parent is not None]
            if scores:
                return sum(scores) / len(scores)
        if source is not None:
            return float(source.score)
        return 0.0

    def _refresh_population_indexes(self, population: list[AlphaCandidate]) -> None:
        self._population_fingerprints = {
            structural_fingerprint(candidate.wqb_expression or candidate.expression)
            for candidate in population
            if (candidate.wqb_expression or candidate.expression)
        }
        self._population_exact_expressions = {
            str(candidate.wqb_expression or candidate.expression).strip()
            for candidate in population
            if str(candidate.wqb_expression or candidate.expression).strip()
        }

    def _build_candidate(
        self,
        *,
        expression: str,
        generation: int,
        rank: int,
        method: str,
        parents: tuple[AlphaCandidate, ...] = (),
        reference_population: list[AlphaCandidate] | None = None,
        source_winner: WinnerRecord | None = None,
        novelty_adjustment: float = 0.0,
        apply_novelty_gate: bool = False,
        metrics: dict[str, Any] | None = None,
    ) -> AlphaCandidate | None:
        compile_result = compile_alpha(expression)
        if not bool(compile_result.get("valid")):
            return None

        normalized_expression = str(compile_result.get("wqb_expression") or expression).strip()
        if self._has_trivial_identity_operation(normalized_expression):
            return None
        component_result = extract_components(normalized_expression)
        operators = tuple(str(item) for item in component_result.get("operators") or [])
        fields = tuple(str(item) for item in component_result.get("fields") or [])
        parameters = tuple(
            dict(item)
            for item in (component_result.get("parameters") or [])
            if isinstance(item, dict)
        )

        parent_ids = tuple(parent.candidate_id for parent in parents if parent is not None)
        parent_scores = [float(parent.surrogate_score) for parent in parents if parent is not None]
        base_score = self._base_score(parents, source_winner)
        reference_fingerprints = (
            {
                structural_fingerprint(candidate.wqb_expression or candidate.expression)
                for candidate in reference_population
                if (candidate.wqb_expression or candidate.expression)
            }
            if reference_population
            else None
        )
        novelty = self._compute_novelty(
            normalized_expression,
            component_result=component_result,
            population_fingerprints=reference_fingerprints,
        )
        novelty_floor = float(self.config.get("archive_novelty_min") or 0.0)
        if apply_novelty_gate and method not in {"seed", "elite", "carryover"} and novelty < novelty_floor:
            if isinstance(metrics, dict):
                metrics["novelty_rejected"] = int(metrics.get("novelty_rejected") or 0) + 1
            return None
        score_weights = self._score_weights()
        novelty_bonus = novelty * score_weights["novelty"] + float(novelty_adjustment)
        complexity = self._complexity_penalty(operators, fields, parameters, normalized_expression)
        risk = self._risk_penalty(method)
        surrogate_score = (
            score_weights["base"] * base_score
            + novelty_bonus
            - score_weights["complexity"] * complexity
            - score_weights["risk"] * risk
        )

        lineage = {
            "parent_a": parent_ids[0] if len(parent_ids) >= 1 else (source_winner.winner_id if source_winner else None),
            "parent_b": parent_ids[1] if len(parent_ids) >= 2 else None,
            "method": method,
            "generation": generation,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        metadata = {
            "source_method": method,
            "source_expression": expression,
            "normalized_expression": normalized_expression,
            "compiler_warnings": list(compile_result.get("warnings") or []),
            "component_warnings": list(component_result.get("warnings") or []),
            "parent_scores": parent_scores,
            "novelty": novelty,
            "novelty_floor": novelty_floor,
            "novelty_bonus": novelty_bonus,
            "novelty_adjustment": float(novelty_adjustment),
            "complexity_penalty": complexity,
            "risk_penalty": risk,
        }
        if source_winner is not None:
            metadata.update(
                {
                    "source_winner_id": source_winner.winner_id,
                    "ledger_row_id": source_winner.ledger_row_id,
                    "alpha_id": source_winner.alpha_id,
                    "winner_score": source_winner.score,
                    "source_tags": list(source_winner.tags),
                    "source_timestamp": source_winner.timestamp,
                }
            )

        candidate_id = self._candidate_id(
            generation=generation,
            expression=normalized_expression,
            method=method,
            parent_ids=parent_ids,
        )
        return AlphaCandidate(
            candidate_id=candidate_id,
            generation=generation,
            rank=rank,
            expression=expression,
            wqb_expression=normalized_expression,
            lineage=lineage,
            operators=operators,
            fields=fields,
            parameters=parameters,
            surrogate_score=surrogate_score,
            expected_sharpe_estimate=None,
            metadata=metadata,
        )

    def _clone_ranked_population(self, population: list[AlphaCandidate]) -> list[AlphaCandidate]:
        ranked = rank_population(population)
        return [replace(candidate, rank=index) for index, candidate in enumerate(ranked, start=1)]

    def initialize_population(self, winners: list[WinnerRecord] | None = None) -> list[AlphaCandidate]:
        winner_pool = list(winners if winners is not None else (self.winners or self.load_winners()))
        if not winner_pool:
            self.population = []
            self.generation = 0
            return []

        if not self._archive_fingerprints:
            self._archive_fingerprints = {
                structural_fingerprint(winner.wqb_expression or winner.expression)
                for winner in winner_pool
                if (winner.wqb_expression or winner.expression)
            }
        if not self._archive_exact_expressions:
            self._archive_exact_expressions = {
                str(winner.wqb_expression or winner.expression).strip()
                for winner in winner_pool
                if str(winner.wqb_expression or winner.expression).strip()
            }

        selected: list[WinnerRecord] = self.rng.sample(winner_pool, k=min(len(winner_pool), self.population_size))

        population: list[AlphaCandidate] = []
        self._population_fingerprints = set()
        self._population_exact_expressions = set()
        for index, winner in enumerate(selected, start=1):
            candidate = self._build_candidate(
                expression=winner.wqb_expression,
                generation=0,
                rank=index,
                method="seed",
                parents=(),
                source_winner=winner,
            )
            if candidate is None:
                continue
            candidate = replace(
                candidate,
                metadata={
                    **candidate.metadata,
                    "seed_rank": index,
                    "seed_source": winner.winner_id,
                },
            )
            population.append(candidate)
            self._population_fingerprints.add(structural_fingerprint(candidate.wqb_expression))
            self._population_exact_expressions.add(candidate.wqb_expression)

        self.population = self._clone_ranked_population(population)
        self._refresh_population_indexes(self.population)
        self.generation = 0
        return list(self.population)

    def select_parents(self, population: list[AlphaCandidate] | None = None) -> tuple[AlphaCandidate, AlphaCandidate]:
        active_population = population if population is not None else self.population
        if not active_population:
            raise ValueError("population is empty")
        tournament_size = int(self.config.get("tournament_size") or 3)
        return tournament_select(active_population, self.rng, tournament_size=tournament_size)

    def crossover(self, parent_a: AlphaCandidate, parent_b: AlphaCandidate) -> str | None:
        return crossover_expression(parent_a, parent_b, self.rng, self.config)

    def mutate(self, expression: str) -> str | None:
        return mutate_expression(expression, self.rng, self.config)

    def evolve_generation(self, current_population: list[AlphaCandidate] | None = None) -> list[AlphaCandidate]:
        active_population = current_population if current_population is not None else self.population
        if not active_population:
            active_population = self.initialize_population()
        if not active_population:
            self._last_generation_metrics = {}
            return []

        current_generation = max(candidate.generation for candidate in active_population)
        next_generation = current_generation + 1
        ranked_current = self._clone_ranked_population(active_population)
        self._refresh_population_indexes(ranked_current)
        elite_count = max(1, int(round(len(ranked_current) * self.elite_fraction))) if ranked_current else 0

        next_population: list[AlphaCandidate] = []
        seen_expressions: set[str] = set(self._archive_exact_expressions) | set(self._population_exact_expressions)
        seen_fingerprints: set[str] = set(self._archive_fingerprints) | set(self._population_fingerprints)
        metrics: dict[str, Any] = {
            "children_generated": 0,
            "children_valid": 0,
            "children_rejected": 0,
            "novelty_rejected": 0,
            "duplicate_rejected": 0,
            "duplicate_rejected_exact": 0,
            "duplicate_rejected_structural": 0,
            "crossover_attempts": 0,
            "crossover_fallbacks": 0,
            "rescue_mutations": 0,
            "elite_retained": 0,
        }

        for index, elite in enumerate(ranked_current[:elite_count], start=1):
            clone = self._build_candidate(
                expression=elite.wqb_expression,
                generation=next_generation,
                rank=index,
                method="elite",
                parents=(elite,),
                reference_population=ranked_current,
            )
            metrics["children_generated"] += 1
            if clone is None:
                metrics["children_rejected"] += 1
                continue
            clone_fingerprint = structural_fingerprint(clone.wqb_expression)
            if clone.wqb_expression in seen_expressions:
                metrics["duplicate_rejected"] += 1
                metrics["duplicate_rejected_exact"] += 1
                continue
            if clone_fingerprint in seen_fingerprints:
                metrics["duplicate_rejected"] += 1
                metrics["duplicate_rejected_structural"] += 1
                continue
            next_population.append(clone)
            seen_expressions.add(clone.wqb_expression)
            seen_fingerprints.add(clone_fingerprint)
            metrics["children_valid"] += 1
            metrics["elite_retained"] += 1

        max_attempts = int(self.config.get("max_child_attempts") or 16)
        max_crossover_attempts = int(self.config.get("max_crossover_attempts") or 5)
        attempts = 0
        while len(next_population) < self.population_size and attempts < max_attempts * max(1, self.population_size):
            parent_a, parent_b = self.select_parents(ranked_current)
            child_expression: str | None = None
            method = "crossover"
            novelty_adjustment = 0.0
            used_fallback = False
            if self.rng.random() < self.crossover_rate:
                for _ in range(max_crossover_attempts):
                    metrics["crossover_attempts"] += 1
                    child_expression = self.crossover(parent_a, parent_b)
                    if child_expression is not None:
                        break
            if child_expression is None:
                used_fallback = True
                metrics["crossover_fallbacks"] += 1
                method = "mutation_fallback"
                source_expression = parent_a.wqb_expression if self.rng.random() < 0.5 else parent_b.wqb_expression
                child_expression = self.mutate(source_expression)
                novelty_adjustment = 0.05
            if child_expression is None:
                metrics["children_rejected"] += 1
                attempts += 1
                continue
            if self.rng.random() < self.mutation_rate:
                mutated_expression = self.mutate(child_expression)
                if mutated_expression:
                    child_expression = mutated_expression
                    method = f"{method}+mutation"
                    if used_fallback:
                        novelty_adjustment = max(novelty_adjustment, 0.05)

            candidate = self._build_candidate(
                expression=child_expression,
                generation=next_generation,
                rank=len(next_population) + 1,
                method=method,
                parents=(parent_a, parent_b),
                reference_population=ranked_current,
                novelty_adjustment=novelty_adjustment,
                apply_novelty_gate=True,
                metrics=metrics,
            )
            metrics["children_generated"] += 1
            if candidate is None:
                metrics["children_rejected"] += 1
                attempts += 1
                continue
            candidate_fingerprint = structural_fingerprint(candidate.wqb_expression)
            if candidate.wqb_expression in seen_expressions:
                metrics["duplicate_rejected"] += 1
                metrics["duplicate_rejected_exact"] += 1
                attempts += 1
                continue
            if candidate_fingerprint in seen_fingerprints:
                metrics["duplicate_rejected"] += 1
                metrics["duplicate_rejected_structural"] += 1
                attempts += 1
                continue
            next_population.append(candidate)
            seen_expressions.add(candidate.wqb_expression)
            seen_fingerprints.add(candidate_fingerprint)
            metrics["children_valid"] += 1
            attempts += 1

        if len(next_population) < self.population_size:
            rescue_attempts = int(self.config.get("max_rescue_attempts") or (max(self.population_size, len(ranked_current)) * 2))
            while len(next_population) < self.population_size and rescue_attempts > 0:
                rescue_attempts -= 1
                fallback = self.rng.choice(ranked_current or active_population)
                child_expression = self.mutate(fallback.wqb_expression)
                if child_expression is None:
                    metrics["children_rejected"] += 1
                    continue
                candidate = self._build_candidate(
                    expression=child_expression,
                    generation=next_generation,
                    rank=len(next_population) + 1,
                    method="rescue-mutation",
                    parents=(fallback,),
                    reference_population=ranked_current,
                    novelty_adjustment=0.05,
                    apply_novelty_gate=True,
                    metrics=metrics,
                )
                metrics["children_generated"] += 1
                if candidate is None:
                    metrics["children_rejected"] += 1
                    continue
                candidate_fingerprint = structural_fingerprint(candidate.wqb_expression)
                if candidate.wqb_expression in seen_expressions:
                    metrics["duplicate_rejected"] += 1
                    metrics["duplicate_rejected_exact"] += 1
                    continue
                if candidate_fingerprint in seen_fingerprints:
                    metrics["duplicate_rejected"] += 1
                    metrics["duplicate_rejected_structural"] += 1
                    continue
                next_population.append(candidate)
                seen_expressions.add(candidate.wqb_expression)
                seen_fingerprints.add(candidate_fingerprint)
                metrics["children_valid"] += 1
                metrics["rescue_mutations"] += 1

        if not next_population and ranked_current:
            fallback = ranked_current[0]
            clone = self._build_candidate(
                expression=fallback.wqb_expression,
                generation=next_generation,
                rank=1,
                method="carryover",
                parents=(fallback,),
                reference_population=ranked_current,
            )
            if clone is not None:
                next_population.append(clone)

        self.population = self._clone_ranked_population(next_population)
        self._refresh_population_indexes(self.population)
        self.generation = next_generation
        self._last_generation_metrics = {
            **metrics,
            "elite_count": elite_count,
            "input_population_size": len(ranked_current),
            "output_population_size": len(self.population),
            "generation": next_generation,
            "crossover_rate": self.crossover_rate,
            "mutation_rate": self.mutation_rate,
            "archive_fingerprint_count": len(self._archive_fingerprints),
            "population_fingerprint_count": len(self._population_fingerprints),
        }
        return list(self.population)

    def run(self, generations: int = 10) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be at least 1")

        if not self.winners:
            self.load_winners()
        if not self.population:
            self.initialize_population(self.winners)
        if not self.population:
            return {
                "status": "empty",
                "generations": 0,
                "population_size": 0,
                "artifacts": [],
            }

        artifacts: list[dict[str, Any]] = []
        current_population = list(self.population)

        for generation_index in range(1, generations + 1):
            current_population = self.evolve_generation(current_population)
            artifacts.append(
                export_generation(
                    generation_index,
                    current_population,
                    metrics=self._last_generation_metrics,
                    config=self.config,
                )
            )

        self.population = current_population
        self.generation = max(candidate.generation for candidate in current_population) if current_population else 0
        return {
            "status": "ok",
            "generations": len(artifacts),
            "population_size": len(current_population),
            "seed": self.seed,
            "artifacts": artifacts,
            "last_generation_metrics": self._last_generation_metrics,
        }

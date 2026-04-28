from __future__ import annotations

import ast
from random import Random
from typing import Any

try:  # pragma: no cover - dual import path for script/package execution
    from harness.lib.compiler import (
        canonicalize_expression,
        compile_alpha,
        extract_numeric_literals,
        load_compiler_config,
        replace_source_span,
    )
except ImportError:  # pragma: no cover
    from compiler import canonicalize_expression, compile_alpha, extract_numeric_literals, load_compiler_config, replace_source_span


def _build_parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    parent_map: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent_map[child] = node
    return parent_map


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    running = 0
    for line in text.splitlines(keepends=True):
        running += len(line)
        offsets.append(running)
    return offsets


def _absolute_offset(text: str, line: int, col: int) -> int:
    offsets = _line_offsets(text)
    index = max(0, min(line - 1, len(offsets) - 1))
    return offsets[index] + col


def _node_span(text: str, node: ast.AST) -> tuple[int, int]:
    if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
        return 0, 0
    start = _absolute_offset(text, int(node.lineno), int(node.col_offset))
    end = _absolute_offset(text, int(node.end_lineno), int(node.end_col_offset))
    return start, end


def _collect_calls_and_fields(expression: str) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    source = canonicalize_expression(expression)
    if not source:
        return "", [], []

    tree = ast.parse(source, mode="eval")
    parent_map = _build_parent_map(tree)
    reserved_words = {str(item) for item in load_compiler_config().get("reserved_words", set())}
    calls: list[dict[str, Any]] = []
    fields: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        parent = parent_map.get(node)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            call_start, call_end = _node_span(source, node)
            func_start, func_end = _node_span(source, node.func)
            if call_start == call_end or func_start == func_end:
                continue
            calls.append(
                {
                    "name": node.func.id,
                    "arity": len(node.args),
                    "call_start": call_start,
                    "call_end": call_end,
                    "func_start": func_start,
                    "func_end": func_end,
                    "text": ast.get_source_segment(source, node) or source[call_start:call_end],
                }
            )
            continue

        if isinstance(node, ast.Name) and not (isinstance(parent, ast.Call) and parent.func is node):
            if node.id in reserved_words:
                continue
            start, end = _node_span(source, node)
            if start == end:
                continue
            fields.append(
                {
                    "name": node.id,
                    "start": start,
                    "end": end,
                    "text": ast.get_source_segment(source, node) or source[start:end],
                }
            )

    calls.sort(key=lambda item: (item["call_start"], item["call_end"], item["name"]))
    fields.sort(key=lambda item: (item["start"], item["end"], item["name"]))
    return source, calls, fields


def _format_numeric(value: float | int) -> str:
    if isinstance(value, bool):
        return "0"
    if isinstance(value, int):
        return str(value)
    numeric = float(value)
    if numeric.is_integer():
        return str(int(numeric))
    return f"{numeric:.12g}"


def _operator_group_lookup(config: dict[str, Any] | None) -> dict[str, str]:
    cfg = config if isinstance(config, dict) else {}
    mutation_cfg = cfg.get("mutation") if isinstance(cfg.get("mutation"), dict) else {}
    operator_groups = mutation_cfg.get("operator_groups") if isinstance(mutation_cfg.get("operator_groups"), dict) else {}
    lookup: dict[str, str] = {}
    for group_name, operators in operator_groups.items():
        if not isinstance(operators, list):
            continue
        for operator in operators:
            if isinstance(operator, str) and operator:
                lookup[operator] = str(group_name)
    return lookup


def _operator_replacements(
    operator: str,
    arity: int,
    rng: Random,
    config: dict[str, Any] | None = None,
) -> list[str]:
    cfg = config if isinstance(config, dict) else {}
    mutation_cfg = cfg.get("mutation") if isinstance(cfg.get("mutation"), dict) else {}
    operator_groups = mutation_cfg.get("operator_groups") if isinstance(mutation_cfg.get("operator_groups"), dict) else {}
    group_lookup = _operator_group_lookup(cfg)
    group_name = group_lookup.get(operator)
    compiler_config = load_compiler_config()
    specs = compiler_config.get("function_specs") or {}
    global_pool: list[str] = []
    same_group_pool: list[str] = []

    for target, spec in specs.items():
        if not isinstance(target, str) or target == operator:
            continue
        min_args = spec.get("min_args")
        max_args = spec.get("max_args")
        if min_args is not None and arity < int(min_args):
            continue
        if max_args is not None and arity > int(max_args):
            continue
        global_pool.append(target)

    if group_name:
        for target in operator_groups.get(group_name, []):
            if not isinstance(target, str) or target == operator:
                continue
            spec = specs.get(target) or {}
            min_args = spec.get("min_args")
            max_args = spec.get("max_args")
            if min_args is not None and arity < int(min_args):
                continue
            if max_args is not None and arity > int(max_args):
                continue
            same_group_pool.append(target)

    if same_group_pool:
        same_group_probability = 0.8
        if isinstance(mutation_cfg, dict):
            same_group_probability = float(mutation_cfg.get("operator_group_same_probability") or same_group_probability)
        if rng.random() < max(0.0, min(1.0, same_group_probability)):
            return same_group_pool
    if same_group_pool:
        return global_pool
    return global_pool


def _mutate_numeric(expression: str, rng: Random, config: dict[str, Any] | None = None) -> str | None:
    cfg = config if isinstance(config, dict) else {}
    mutation_cfg = cfg.get("mutation") if isinstance(cfg.get("mutation"), dict) else {}
    delta_pct = float(mutation_cfg.get("numeric_delta_pct") or 0.2)
    step_values = mutation_cfg.get("numeric_step_values") if isinstance(mutation_cfg.get("numeric_step_values"), list) else [1, 2]
    literals = extract_numeric_literals(expression)
    if not literals:
        return None

    literal = rng.choice(literals)
    original_value = literal.get("value")
    if isinstance(original_value, bool):
        return None

    numeric_candidates: list[float | int] = []
    if isinstance(original_value, int) or (isinstance(original_value, float) and float(original_value).is_integer()):
        base = int(round(float(original_value)))
        for step in step_values:
            try:
                step_value = abs(int(step))
            except (TypeError, ValueError):
                continue
            if step_value <= 0:
                continue
            numeric_candidates.append(base + step_value)
            numeric_candidates.append(base - step_value)
        delta = max(1, int(round(abs(base) * delta_pct)))
        numeric_candidates.append(base + delta)
        numeric_candidates.append(base - delta)
        numeric_candidates.append(int(round(base * (1.0 + delta_pct))))
        numeric_candidates.append(int(round(base * (1.0 - delta_pct))))
        numeric_candidates.append(int(round(base * rng.uniform(0.8, 1.2))))
    else:
        base = float(original_value)
        delta = abs(base) * delta_pct or delta_pct
        numeric_candidates.extend(
            [
                base + delta,
                base - delta,
                base * (1.0 + delta_pct),
                base * (1.0 - delta_pct),
                base * rng.uniform(0.8, 1.2),
            ]
        )

    role = str(literal.get("role") or "scalar")
    call_name = str(literal.get("call_name") or "")
    positive_integer_only = role == "window" or "decay" in call_name or "threshold" in role

    rng.shuffle(numeric_candidates)
    chosen: float | int | None = None
    for candidate in numeric_candidates:
        if isinstance(candidate, float) and candidate.is_integer():
            candidate = int(candidate)
        if positive_integer_only:
            try:
                candidate_int = int(round(float(candidate)))
            except (TypeError, ValueError):
                continue
            if candidate_int <= 0:
                continue
            candidate = candidate_int
        if candidate != original_value:
            chosen = candidate
            break

    if chosen is None:
        return None

    source = canonicalize_expression(expression)
    mutated = replace_source_span(source, int(literal["start"]), int(literal["end"]), _format_numeric(chosen))
    return mutated if mutated != source else None


def _mutate_operator(expression: str, rng: Random, config: dict[str, Any] | None = None) -> str | None:
    source, calls, _ = _collect_calls_and_fields(expression)
    if not source or not calls:
        return None

    mutable_calls = [call for call in calls if _operator_replacements(call["name"], int(call["arity"]), rng, config)]
    if not mutable_calls:
        return None

    rng.shuffle(mutable_calls)
    for call in mutable_calls:
        replacements = _operator_replacements(call["name"], int(call["arity"]), rng, config)
        if not replacements:
            continue
        replacement = rng.choice(replacements)
        mutated = replace_source_span(source, int(call["func_start"]), int(call["func_end"]), replacement)
        if mutated != source:
            return mutated
    return None


def _mutate_field(expression: str, rng: Random, config: dict[str, Any] | None = None) -> str | None:
    source, _, fields = _collect_calls_and_fields(expression)
    if not source or not fields:
        return None

    mutation_cfg = (config or {}).get("mutation") if isinstance((config or {}).get("mutation"), dict) else {}
    observed_only = bool((mutation_cfg.get("field_groups") or {}).get("observed_only", True))

    field_pool = {fragment["name"] for fragment in fields if fragment["name"]}
    known_fields: list[Any] = []
    if isinstance(config, dict) and isinstance(config.get("known_fields"), list):
        known_fields.extend(config.get("known_fields") or [])
    compiler_known_fields = load_compiler_config().get("known_fields") or []
    known_fields.extend(compiler_known_fields)
    for field_name in known_fields:
        if isinstance(field_name, str) and field_name:
            field_pool.add(field_name)

    if observed_only and len(field_pool) < 2:
        # If the current expression is narrow, fall back to the broader ledger vocabulary.
        for field_name in known_fields:
            if isinstance(field_name, str) and field_name:
                field_pool.add(field_name)

    if len(field_pool) < 2:
        return None

    candidates = list(fields)
    rng.shuffle(candidates)
    for fragment in candidates:
        alternatives = [name for name in sorted(field_pool) if name != fragment["name"]]
        if not alternatives:
            continue
        mutated = replace_source_span(source, int(fragment["start"]), int(fragment["end"]), rng.choice(alternatives))
        if mutated != source:
            return mutated
    return None


def _mutate_wrapper(expression: str, rng: Random, config: dict[str, Any] | None = None) -> str | None:
    source = canonicalize_expression(expression)
    if not source:
        return None

    tree = ast.parse(source, mode="eval")
    if isinstance(tree.body, ast.Call) and isinstance(tree.body.func, ast.Name):
        outer_name = tree.body.func.id
        if outer_name in {"rank", "zscore", "demean"} and len(tree.body.args) == 1:
            inner = ast.get_source_segment(source, tree.body.args[0])
            if inner and inner != source:
                return inner

    mutation_cfg = (config or {}).get("mutation") if isinstance((config or {}).get("mutation"), dict) else {}
    window_values = mutation_cfg.get("wrapper_windows") if isinstance(mutation_cfg.get("wrapper_windows"), list) else [20, 60, 120]
    wrappers = [
        ("rank", 1),
        ("zscore", 1),
        ("demean", 1),
        ("abs", 1),
        ("sqrt", 1),
        ("log", 1),
        ("ts_rank", 2),
        ("ts_zscore", 2),
        ("ts_mean", 2),
        ("ts_std", 2),
        ("ts_decay_linear", 2),
    ]
    wrapper, arity = rng.choice(wrappers)
    if arity == 1:
        wrapped = f"{wrapper}({source})"
        return wrapped if wrapped != source else None

    valid_windows = []
    for value in window_values:
        try:
            candidate = max(1, int(value))
        except (TypeError, ValueError):
            continue
        valid_windows.append(candidate)
    if not valid_windows:
        valid_windows = [20, 60, 120]
    wrapped = f"{wrapper}({source}, {rng.choice(valid_windows)})"
    return wrapped if wrapped != source else None


def mutate(expression: str, rng: Random, config: dict[str, Any] | None = None) -> str | None:
    """Mutate a WQB expression using numeric, operator, field, and wrapper edits."""

    source = canonicalize_expression(expression)
    if not source:
        return None

    cfg = config if isinstance(config, dict) else {}
    max_attempts = int(cfg.get("max_child_attempts") or 16)
    strategies = [_mutate_numeric, _mutate_operator, _mutate_field, _mutate_wrapper]

    for _ in range(max_attempts):
        rng.shuffle(strategies)
        for strategy in strategies:
            candidate = strategy(source, rng, cfg)
            if not candidate:
                continue
            compile_result = compile_alpha(candidate)
            if bool(compile_result.get("valid")):
                return str(compile_result.get("wqb_expression") or candidate)
    return None

from __future__ import annotations

import ast
from collections import defaultdict
from random import Random
from typing import Any

try:  # pragma: no cover - dual import path for script/package execution
    from harness.lib.compiler import canonicalize_expression, compile_alpha, replace_source_span
except ImportError:  # pragma: no cover
    from compiler import canonicalize_expression, compile_alpha, replace_source_span

from .models import AlphaCandidate


_KIND_PRIORITY = ("call", "field", "constant", "compound")


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
    line_offsets = _line_offsets(text)
    index = max(0, min(line - 1, len(line_offsets) - 1))
    return line_offsets[index] + col


def _node_span(text: str, node: ast.AST) -> tuple[int, int]:
    if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
        return 0, 0
    start = _absolute_offset(text, int(node.lineno), int(node.col_offset))
    end = _absolute_offset(text, int(node.end_lineno), int(node.end_col_offset))
    return start, end


def _node_kind(node: ast.AST, parent: ast.AST | None) -> str | None:
    if isinstance(node, ast.Call):
        return "call"
    if isinstance(node, ast.Name):
        if isinstance(parent, ast.Call) and parent.func is node:
            return None
        return "field"
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return "constant"
    if isinstance(node, (ast.BinOp, ast.BoolOp, ast.Compare, ast.UnaryOp)):
        return "compound"
    return None


def _collect_fragments(expression: str) -> tuple[str, dict[str, list[dict[str, Any]]]]:
    source = canonicalize_expression(expression)
    if not source:
        return "", {}

    tree = ast.parse(source, mode="eval")
    parent_map = _build_parent_map(tree)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for node in ast.walk(tree):
        kind = _node_kind(node, parent_map.get(node))
        if not kind:
            continue
        segment = ast.get_source_segment(source, node)
        if not segment:
            continue
        start, end = _node_span(source, node)
        if start == end:
            continue
        groups[kind].append(
            {
                "kind": kind,
                "text": segment,
                "start": start,
                "end": end,
                "node_type": type(node).__name__,
            }
        )

    for fragments in groups.values():
        fragments.sort(key=lambda item: (item["start"], item["end"], item["text"]))
    return source, dict(groups)


def _flatten_fragments(groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    fragments: list[dict[str, Any]] = []
    for kind in _KIND_PRIORITY:
        fragments.extend(groups.get(kind, []))
    for kind, values in groups.items():
        if kind not in _KIND_PRIORITY:
            fragments.extend(values)
    return fragments


def crossover(
    parent_a: AlphaCandidate,
    parent_b: AlphaCandidate,
    rng: Random,
    config: dict[str, Any] | None = None,
) -> str | None:
    """Create a child expression from two parents.

    This uses a conservative AST-span swap so we can keep the implementation
    structure-aware without waiting for the compiler-level component extractor.
    """

    cfg = config if isinstance(config, dict) else {}
    max_attempts = int(cfg.get("max_parent_attempts") or 8)
    expr_a, groups_a = _collect_fragments(parent_a.wqb_expression or parent_a.expression)
    expr_b, groups_b = _collect_fragments(parent_b.wqb_expression or parent_b.expression)
    if not expr_a or not expr_b or not groups_a or not groups_b:
        return None

    shared_kinds = [kind for kind in _KIND_PRIORITY if groups_a.get(kind) and groups_b.get(kind)]
    fallback_kinds = [kind for kind in _KIND_PRIORITY if groups_a.get(kind)]
    if not shared_kinds and not fallback_kinds:
        return None

    strategies: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]] = []
    if shared_kinds:
        for kind in shared_kinds:
            strategies.append((kind, groups_a[kind], groups_b[kind]))
    elif fallback_kinds:
        for kind in fallback_kinds:
            strategies.append((kind, groups_a[kind], _flatten_fragments(groups_b)))

    for _ in range(max_attempts):
        if not strategies:
            break
        kind, fragments_a, fragments_b = rng.choice(strategies)
        candidate_a = rng.choice(fragments_a)
        candidate_b = rng.choice(fragments_b)
        child_expression = replace_source_span(expr_a, int(candidate_a["start"]), int(candidate_a["end"]), candidate_b["text"])
        if child_expression in {expr_a, expr_b}:
            continue

        compile_result = compile_alpha(child_expression)
        if bool(compile_result.get("valid")):
            return str(compile_result.get("wqb_expression") or child_expression)

        # Second attempt: swap a different fragment from the same structural kind.
        if len(fragments_a) > 1 and len(fragments_b) > 1:
            alt_a = rng.choice([fragment for fragment in fragments_a if fragment is not candidate_a] or fragments_a)
            alt_b = rng.choice([fragment for fragment in fragments_b if fragment is not candidate_b] or fragments_b)
            alt_expression = replace_source_span(expr_a, int(alt_a["start"]), int(alt_a["end"]), alt_b["text"])
            if alt_expression not in {expr_a, expr_b}:
                compile_result = compile_alpha(alt_expression)
                if bool(compile_result.get("valid")):
                    return str(compile_result.get("wqb_expression") or alt_expression)

    return None

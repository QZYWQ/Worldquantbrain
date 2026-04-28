from __future__ import annotations

import ast
import copy
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = PACKAGE_DIR / "compiler_config.json"

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
COMMENT_LINE_RE = re.compile(r"^(?P<indent>\s*)//(?P<body>.*)$")
INLINE_HASH_COMMENT_RE = re.compile(r"(?<!\S)#.*$")
WHITESPACE_RE = re.compile(r"\s+")
COMMA_SPACING_RE = re.compile(r"\s*,\s*")
OPEN_PAREN_SPACING_RE = re.compile(r"\(\s+")
CLOSE_PAREN_SPACING_RE = re.compile(r"\s+\)")

DEFAULT_FUNCTION_SPECS: dict[str, dict[str, Any]] = {
    "abs": {"min_args": 1, "max_args": 1},
    "bucket": {"min_args": 2, "max_args": 4},
    "clip": {"min_args": 3, "max_args": 3},
    "demean": {"min_args": 1, "max_args": 2},
    "delta": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "delay": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "group_mean": {"min_args": 2, "max_args": 2},
    "group_neutralize": {"min_args": 2, "max_args": 2},
    "group_rank": {"min_args": 2, "max_args": 2},
    "group_sum": {"min_args": 2, "max_args": 2},
    "group_zscore": {"min_args": 2, "max_args": 2},
    "if_else": {"min_args": 3, "max_args": 3},
    "log": {"min_args": 1, "max_args": 1},
    "mad": {"min_args": 1, "max_args": 2},
    "max": {"min_args": 2, "max_args": None},
    "mean": {"min_args": 1, "max_args": None},
    "min": {"min_args": 2, "max_args": None},
    "multiply": {"min_args": 2, "max_args": None},
    "neutralize": {"min_args": 2, "max_args": 2},
    "power": {"min_args": 2, "max_args": 2},
    "rank": {"min_args": 1, "max_args": 1},
    "scale": {"min_args": 1, "max_args": 2},
    "signed_power": {"min_args": 2, "max_args": 2},
    "sqrt": {"min_args": 1, "max_args": 1},
    "subtract": {"min_args": 2, "max_args": 2},
    "sum": {"min_args": 1, "max_args": None},
    "trade_when": {"min_args": 3, "max_args": 3},
    "ts_argmax": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_argmin": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_av_diff": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_backfill": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_corr": {"min_args": 3, "max_args": 3, "window_args": [2]},
    "ts_cov": {"min_args": 3, "max_args": 3, "window_args": [2]},
    "ts_count_nans": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_decay_linear": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_delta": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_delay": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_mean": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_median": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_min": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_product": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_quantile": {"min_args": 3, "max_args": 3, "window_args": [1]},
    "ts_rank": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_regression": {"min_args": 4, "max_args": 4, "window_args": [2]},
    "ts_scale": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_std": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_sum": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "ts_zscore": {"min_args": 2, "max_args": 2, "window_args": [1]},
    "winsorize": {"min_args": 2, "max_args": 2},
    "zscore": {"min_args": 1, "max_args": 1},
}

DEFAULT_CONFIG: dict[str, Any] = {
    "allowed_identifier_pattern": IDENTIFIER_RE.pattern,
    "comment_markers": ["#", "//"],
    "field_pattern": IDENTIFIER_RE.pattern,
    "function_prefix_allowlist": ["group_", "ts_"],
    "function_specs": DEFAULT_FUNCTION_SPECS,
    "known_fields": [],
    "require_known_field_list": False,
    "strict_unknown_function_policy": "error",
    "numeric_limits": {"min": -1_000_000_000.0, "max": 1_000_000_000.0},
    "reserved_words": ["and", "or", "not", "True", "False", "None"],
}


@dataclass(frozen=True)
class NumericLiteral:
    value: int | float
    text: str
    role: str
    start: int
    end: int
    line: int
    col: int
    end_line: int
    end_col: int
    call_name: str | None = None
    arg_index: int | None = None


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_compiler_config(config_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.is_absolute():
        path = (PACKAGE_DIR / path).resolve()

    config = copy.deepcopy(DEFAULT_CONFIG)
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                config = _deep_merge(config, payload)
        except (OSError, json.JSONDecodeError):
            pass

    function_specs = config.get("function_specs")
    if not isinstance(function_specs, dict):
        function_specs = {}
    config["function_specs"] = {
        str(name): dict(spec)
        for name, spec in function_specs.items()
        if isinstance(spec, dict)
    }

    config["known_fields"] = [
        str(item)
        for item in config.get("known_fields", [])
        if isinstance(item, (str, int, float))
    ]
    config["function_prefix_allowlist"] = [
        str(item)
        for item in config.get("function_prefix_allowlist", [])
        if isinstance(item, str) and item
    ]
    config["reserved_words"] = {
        str(item)
        for item in config.get("reserved_words", [])
        if isinstance(item, str) and item
    }
    return config


def _strip_inline_hash_comment(line: str) -> str:
    return INLINE_HASH_COMMENT_RE.sub("", line).rstrip()


def _prepare_source_for_ast(expression: str) -> str:
    normalized_lines: list[str] = []
    for raw_line in (expression or "").splitlines():
        match = COMMENT_LINE_RE.match(raw_line)
        if match:
            normalized_lines.append(f"{match.group('indent')}##{match.group('body')}")
            continue
        normalized_lines.append(raw_line)
    return "\n".join(normalized_lines)


def _strip_comment_lines(expression: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in (expression or "").splitlines():
        stripped = raw_line.lstrip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        cleaned_lines.append(_strip_inline_hash_comment(raw_line))
    return "\n".join(cleaned_lines)


def _strip_outer_parens(expr: str) -> str:
    text = expr.strip()
    while len(text) >= 2 and text.startswith("(") and text.endswith(")"):
        inner = text[1:-1].strip()
        if not inner:
            break
        depth = 0
        balanced = True
        for index, char in enumerate(inner):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    balanced = False
                    break
            if depth == 0 and index != len(inner) - 1:
                balanced = False
                break
        if balanced and depth == 0:
            text = inner
        else:
            break
    return text


def canonicalize_expression(expression: str) -> str:
    text = _strip_comment_lines(expression)
    text = text.replace("\r\n", "\n")
    text = WHITESPACE_RE.sub(" ", text)
    text = COMMA_SPACING_RE.sub(", ", text)
    text = OPEN_PAREN_SPACING_RE.sub("(", text)
    text = CLOSE_PAREN_SPACING_RE.sub(")", text)
    text = text.strip()
    return _strip_outer_parens(text)


def _build_parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    parent_map: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent_map[child] = node
    return parent_map


def _get_call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    return None


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    running = 0
    for line in text.splitlines(keepends=True):
        running += len(line)
        offsets.append(running)
    return offsets


def _absolute_offset(text: str, line: int, col: int) -> int:
    line_offsets = _line_offsets(text)
    if line - 1 < 0 or line - 1 >= len(line_offsets):
        return 0
    return line_offsets[line - 1] + col


def _node_span(text: str, node: ast.AST) -> tuple[int, int]:
    if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
        return 0, 0
    start = _absolute_offset(text, int(node.lineno), int(node.col_offset))
    end = _absolute_offset(text, int(node.end_lineno), int(node.end_col_offset))
    return start, end


def _number_text(value: int | float) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if float(value).is_integer():
        return str(int(value))
    text = f"{float(value):.12g}"
    return text


def _iter_numeric_nodes(tree: ast.AST) -> Iterator[ast.Constant]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            yield node


def _collect_identifier_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
    return names


def _validate_constant(node: ast.Constant, issues: list[str], config: dict[str, Any]) -> None:
    value = node.value
    if isinstance(value, bool) or value is None:
        return
    if not isinstance(value, (int, float)):
        issues.append(
            f"unsupported constant type at line {getattr(node, 'lineno', '?')}: {type(value).__name__}"
        )
        return
    if not math.isfinite(float(value)):
        issues.append(f"non-finite numeric literal at line {getattr(node, 'lineno', '?')}")
        return
    numeric_limits = config.get("numeric_limits") or {}
    minimum = numeric_limits.get("min")
    maximum = numeric_limits.get("max")
    numeric_value = float(value)
    if minimum is not None and numeric_value < float(minimum):
        issues.append(f"numeric literal {value} is below the configured minimum {minimum}")
    if maximum is not None and numeric_value > float(maximum):
        issues.append(f"numeric literal {value} exceeds the configured maximum {maximum}")


def _validate_call(node: ast.Call, issues: list[str], warnings: list[str], config: dict[str, Any]) -> None:
    call_name = _get_call_name(node)
    if call_name is None:
        issues.append(f"unsupported function syntax at line {getattr(node, 'lineno', '?')}")
        return

    if node.keywords:
        issues.append(f"keyword arguments are not supported in call '{call_name}'")
        return

    function_specs = config.get("function_specs") or {}
    prefix_allowlist = tuple(config.get("function_prefix_allowlist") or [])
    unknown_policy = str(config.get("strict_unknown_function_policy") or "error").lower()

    spec = function_specs.get(call_name)
    if spec is None:
        if any(call_name.startswith(prefix) for prefix in prefix_allowlist):
            warnings.append(f"function '{call_name}' accepted by prefix allowlist")
        elif unknown_policy == "error":
            issues.append(f"unknown function '{call_name}'")
        else:
            warnings.append(f"unknown function '{call_name}' accepted in permissive mode")
        return

    min_args = spec.get("min_args")
    max_args = spec.get("max_args")
    arg_count = len(node.args)
    if min_args is not None and arg_count < int(min_args):
        issues.append(f"function '{call_name}' expects at least {min_args} arguments, got {arg_count}")
    if max_args is not None and arg_count > int(max_args):
        issues.append(f"function '{call_name}' expects at most {max_args} arguments, got {arg_count}")

    window_args = spec.get("window_args") or []
    for index in window_args:
        if index >= arg_count:
            continue
        arg = node.args[int(index)]
        if not isinstance(arg, ast.Constant) or not isinstance(arg.value, (int, float)) or isinstance(arg.value, bool):
            continue
        numeric_value = float(arg.value)
        if not numeric_value.is_integer():
            issues.append(f"window argument {index + 1} of '{call_name}' must be an integer")
        if numeric_value <= 0:
            issues.append(f"window argument {index + 1} of '{call_name}' must be positive")


def _validate_name(
    node: ast.Name,
    parent: ast.AST | None,
    issues: list[str],
    warnings: list[str],
    config: dict[str, Any],
    known_functions: set[str],
) -> None:
    name = node.id
    if isinstance(parent, ast.Call) and parent.func is node:
        return
    if name in config.get("reserved_words", set()):
        return
    if not IDENTIFIER_RE.match(name):
        issues.append(f"invalid identifier '{name}'")
        return

    known_fields = {field for field in config.get("known_fields", []) if isinstance(field, str)}
    require_known_fields = bool(config.get("require_known_field_list")) and bool(known_fields)
    if name in known_functions:
        warnings.append(f"identifier '{name}' matches a known function name but is used as a bare symbol")
        return
    if require_known_fields and name not in known_fields:
        issues.append(f"unknown variable '{name}'")
        return
    if known_fields and name not in known_fields:
        warnings.append(f"identifier '{name}' is not in the configured known field list")


def _analyze_expression(expression_str: str, collect_components: bool = False) -> dict[str, Any]:
    config = load_compiler_config()
    original = expression_str or ""
    warnings: list[str] = []
    issues: list[str] = []

    cleaned = canonicalize_expression(original)
    base_result: dict[str, Any] = {
        "valid": False,
        "error": "",
        "warnings": warnings,
        "wqb_expression": cleaned,
    }

    if not cleaned:
        if collect_components:
            base_result.update({"operators": [], "fields": [], "parameters": []})
        base_result["error"] = "empty expression"
        return base_result

    prepared = _prepare_source_for_ast(original)
    try:
        tree = ast.parse(prepared, mode="eval")
    except SyntaxError as exc:
        location = f"line {exc.lineno}, column {exc.offset}" if exc.lineno and exc.offset else "unknown location"
        message = exc.msg or "syntax error"
        base_result["error"] = f"{message} at {location}"
        if collect_components:
            base_result.update({"operators": [], "fields": [], "parameters": []})
        return base_result

    allowed_node_types = (
        ast.Expression,
        ast.BinOp,
        ast.BoolOp,
        ast.Call,
        ast.Compare,
        ast.Constant,
        ast.Load,
        ast.Name,
        ast.UnaryOp,
    )
    allowed_operator_types = (
        ast.Add,
        ast.And,
        ast.BitXor,
        ast.Div,
        ast.Eq,
        ast.FloorDiv,
        ast.Gt,
        ast.GtE,
        ast.Invert,
        ast.Lt,
        ast.LtE,
        ast.Mod,
        ast.Mult,
        ast.Not,
        ast.NotEq,
        ast.Or,
        ast.Pow,
        ast.Sub,
        ast.UAdd,
        ast.USub,
    )
    known_functions = set((config.get("function_specs") or {}).keys())
    parent_map = _build_parent_map(tree)
    reserved_words = {str(item) for item in config.get("reserved_words", set())}
    known_fields = {field for field in config.get("known_fields", []) if isinstance(field, str)}
    require_known_fields = bool(config.get("require_known_field_list")) and bool(known_fields)

    operator_records: list[tuple[int, str]] = []
    field_records: list[tuple[int, str]] = []
    parameter_records: list[NumericLiteral] = []

    for node in ast.walk(tree):
        if not isinstance(node, allowed_node_types + allowed_operator_types):
            issues.append(f"unsupported syntax element: {type(node).__name__}")
            continue

        if isinstance(node, ast.Call):
            _validate_call(node, issues, warnings, config)
            if collect_components:
                call_name = _get_call_name(node)
                if call_name:
                    start, end = _node_span(prepared, node)
                    if start != end:
                        operator_records.append((start, call_name))
        elif isinstance(node, ast.Name):
            parent = parent_map.get(node)
            _validate_name(node, parent, issues, warnings, config, known_functions)
            if collect_components:
                if isinstance(parent, ast.Call) and parent.func is node:
                    continue
                if node.id in reserved_words or node.id in known_functions:
                    continue
                if require_known_fields and node.id not in known_fields:
                    continue
                start, end = _node_span(prepared, node)
                if start != end:
                    field_records.append((start, node.id))
        elif isinstance(node, ast.Constant):
            _validate_constant(node, issues, config)
            if collect_components and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                parent = parent_map.get(node)
                role = "scalar"
                call_name: str | None = None
                arg_index: int | None = None
                if isinstance(parent, ast.Call):
                    call_name = _get_call_name(parent)
                    if call_name:
                        try:
                            arg_index = parent.args.index(node)
                        except ValueError:
                            arg_index = None
                        spec = (config.get("function_specs") or {}).get(call_name) or {}
                        if arg_index is not None and arg_index in set(spec.get("window_args") or []):
                            role = "window"
                        elif "decay" in call_name:
                            role = "decay"
                        elif "threshold" in call_name:
                            role = "threshold"
                elif isinstance(parent, ast.Compare):
                    role = "threshold"
                elif isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Pow):
                    role = "exponent"

                start, end = _node_span(prepared, node)
                value = node.value
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                parameter_records.append(
                    NumericLiteral(
                        value=value,
                        text=ast.get_source_segment(prepared, node) or _number_text(value),
                        role=role,
                        start=start,
                        end=end,
                        line=int(getattr(node, "lineno", 1)),
                        col=int(getattr(node, "col_offset", 0)),
                        end_line=int(getattr(node, "end_lineno", getattr(node, "lineno", 1))),
                        end_col=int(getattr(node, "end_col_offset", getattr(node, "col_offset", 0))),
                        call_name=call_name,
                        arg_index=arg_index,
                    )
                )

    result: dict[str, Any] = {
        "valid": not issues,
        "error": "; ".join(dict.fromkeys(issues)),
        "warnings": list(dict.fromkeys(warnings)),
        "wqb_expression": cleaned,
    }

    if collect_components:
        operator_names: list[str] = []
        seen_operators: set[str] = set()
        for _, name in sorted(operator_records, key=lambda item: (item[0], item[1])):
            if name not in seen_operators:
                seen_operators.add(name)
                operator_names.append(name)

        field_names: list[str] = []
        seen_fields: set[str] = set()
        for _, name in sorted(field_records, key=lambda item: (item[0], item[1])):
            if name not in seen_fields:
                seen_fields.add(name)
                field_names.append(name)

        parameters = [literal.__dict__ for literal in sorted(parameter_records, key=lambda item: (item.start, item.end))]
        result.update(
            {
                "operators": operator_names,
                "fields": field_names,
                "parameters": parameters,
            }
        )

    return result


def extract_numeric_literals(expression: str) -> list[dict[str, Any]]:
    config = load_compiler_config()
    prepared = _prepare_source_for_ast(expression)
    tree = ast.parse(prepared, mode="eval")
    parent_map = _build_parent_map(tree)
    function_specs = config.get("function_specs") or {}

    literals: list[NumericLiteral] = []
    for node in _iter_numeric_nodes(tree):
        parent = parent_map.get(node)
        role = "scalar"
        call_name: str | None = None
        arg_index: int | None = None
        if isinstance(parent, ast.Call):
            call_name = _get_call_name(parent)
            if call_name:
                try:
                    arg_index = parent.args.index(node)
                except ValueError:
                    arg_index = None
                spec = function_specs.get(call_name) or {}
                if arg_index is not None and arg_index in set(spec.get("window_args") or []):
                    role = "window"
                elif "decay" in call_name:
                    role = "decay"
                elif "threshold" in call_name:
                    role = "threshold"
        elif isinstance(parent, ast.Compare):
            role = "threshold"
        elif isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Pow):
            role = "exponent"

        start, end = _node_span(prepared, node)
        value = node.value
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        literals.append(
            NumericLiteral(
                value=value,
                text=ast.get_source_segment(prepared, node) or _number_text(value),
                role=role,
                start=start,
                end=end,
                line=int(getattr(node, "lineno", 1)),
                col=int(getattr(node, "col_offset", 0)),
                end_line=int(getattr(node, "end_lineno", getattr(node, "lineno", 1))),
                end_col=int(getattr(node, "end_col_offset", getattr(node, "col_offset", 0))),
                call_name=call_name,
                arg_index=arg_index,
            )
        )
    return [literal.__dict__ for literal in sorted(literals, key=lambda item: (item.start, item.end))]


def replace_source_span(source: str, start: int, end: int, replacement: str) -> str:
    return source[:start] + replacement + source[end:]


def compile_alpha(expression_str: str) -> dict[str, Any]:
    return _analyze_expression(expression_str, collect_components=False)


def extract_components(expression_str: str) -> dict[str, Any]:
    """Return compiler validation results plus structured expression components."""

    result = _analyze_expression(expression_str, collect_components=True)
    result.setdefault("operators", [])
    result.setdefault("fields", [])
    result.setdefault("parameters", [])
    return result


__all__ = [
    "NumericLiteral",
    "canonicalize_expression",
    "compile_alpha",
    "extract_components",
    "extract_numeric_literals",
    "load_compiler_config",
    "replace_source_span",
]

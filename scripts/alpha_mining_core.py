#!/usr/bin/env python3
"""Shared helpers for the local WorldQuant alpha-mining scripts.

This module keeps the generator, scorecard, and queue builder loosely coupled:

- parsing lives here
- expression transforms live here
- heuristics and scoring primitives live here
- the CLI scripts stay thin

The goal is to favor a healthy, convergent search loop:

- keep the search local to each family
- penalize excessive operator depth and category mixing
- avoid reusing dead branches
- preserve enough novelty for useful exploration
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from hashlib import sha1
import json
import re
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


DEFAULT_WINDOW_GRID = (5, 10, 20, 21, 30, 63, 72, 78, 81, 84, 90, 126, 252, 504)
DEFAULT_THRESHOLD_GRID = (0.35, 0.45, 0.5, 0.55, 0.65)
DEFAULT_GROUP_VARIANTS = ("industry", "subindustry")
DEFAULT_KILL_MARKERS = (
    "branch away",
    "branch to a new",
    "branch to another",
    "dead",
    "do not continue",
    "kill",
    "stop polishing",
)

WINDOW_FUNCTIONS = {
    "ts_av_diff",
    "ts_backfill",
    "ts_delta",
    "ts_max",
    "ts_mean",
    "ts_min",
    "ts_rank",
    "ts_std_dev",
    "ts_sum",
    "ts_zscore",
    "decay_linear",
}

FUNCTIONS_THAT_SIGNAL_STABILITY = {
    "group_neutralize",
    "group_rank",
    "ts_mean",
    "ts_zscore",
    "ts_std_dev",
    "trade_when",
}

CATEGORY_KEYWORDS = {
    "sentiment_news": (
        "buzz",
        "news",
        "nws",
        "relevance",
        "novelty",
        "sentiment",
        "snt",
        "bee",
        "social",
    ),
    "fundamental": (
        "assets",
        "asset",
        "cash",
        "debt",
        "equity",
        "income",
        "liabilities",
        "margin",
        "operating",
        "profit",
        "revenue",
        "sales",
    ),
    "price_volume": (
        "adv",
        "close",
        "high",
        "low",
        "open",
        "price",
        "returns",
        "turnover",
        "volume",
        "vwap",
    ),
    "volatility_risk": (
        "beta",
        "delta",
        "gamma",
        "iv",
        "options",
        "risk",
        "skew",
        "vol",
        "volatility",
    ),
    "event_trigger": (
        "entry",
        "event",
        "exit",
        "trade_when",
        "trigger",
    ),
    "model_analyst": (
        "afv",
        "analyst",
        "consensus",
        "disagreement",
        "eps",
        "est",
        "estimate",
        "forecast",
        "mdl",
        "model",
        "qfv",
        "spe",
    ),
}

FUNCTION_CALL_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\(")
NUMBER_RE = re.compile(r"(?<![A-Za-z_])(-?\d+(?:\.\d+)?)")
COMPARATOR_NUMBER_RE = re.compile(r"([<>]=?|==|!=)\s*(-?\d+(?:\.\d+)?)")
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|-?\d+(?:\.\d+)?|>=|<=|==|!=|[(),*/+\-<>]")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"```(?:[a-zA-Z0-9_-]+)?\n(.*?)```", re.DOTALL)
METADATA_BULLET_RE = re.compile(r"^\s*-\s+([^:]+):\s*(.*)$")


@dataclass(frozen=True)
class ParsedFamilyDoc:
    path: Path
    title: str
    topic: str
    region: str
    universe: str
    delay: str
    category: str
    hypothesis: str
    confirmed_inputs: tuple[str, ...]
    upstream_evidence: tuple[str, ...]
    optimization_order: tuple[str, ...]
    baseline_expression: str | None
    variant_expressions: tuple[str, ...]
    all_expressions: tuple[str, ...]
    is_dead: bool
    raw_text: str


@dataclass(frozen=True)
class ParsedCapture:
    path: Path
    capture_id: str
    topic: str
    expressions: tuple[str, ...]
    is_dead: bool
    has_check_submission: bool
    raw_text: str


@dataclass(frozen=True)
class FunctionCall:
    name: str
    args: tuple[str, ...]
    start: int
    end: int
    raw: str


@dataclass(frozen=True)
class MutationPlan:
    kind: str
    description: str
    payload: dict[str, Any]
    priority: float = 0.0


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def is_probably_expression_block(block: str) -> bool:
    stripped = block.strip()
    if not stripped:
        return False
    if len(stripped.splitlines()) > 6:
        return False
    if any(marker in stripped for marker in ("{", "}", "\"", ":")):
        return False
    return "(" in stripped and ")" in stripped


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return ""

    start = match.end()
    next_match = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def extract_bullets(section_text: str) -> tuple[str, ...]:
    bullets: list[str] = []
    for line in section_text.splitlines():
        match = METADATA_BULLET_RE.match(line)
        if match:
            value = match.group(2).strip()
            if value:
                bullets.append(value)
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            if value:
                bullets.append(value)
    return tuple(bullets)


def extract_code_blocks(text: str) -> tuple[str, ...]:
    blocks = []
    for block in CODE_BLOCK_RE.findall(text):
        cleaned = block.strip()
        if cleaned:
            blocks.append(cleaned)
    return tuple(blocks)


def find_first_heading(text: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def infer_category(text: str) -> str:
    lower = text.lower()
    best_category = "general"
    best_score = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(lower.count(keyword) for keyword in keywords)
        if score > best_score:
            best_score = score
            best_category = category
    return best_category


def has_kill_marker(text: str, markers: Sequence[str] = DEFAULT_KILL_MARKERS) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in markers)


def parse_family_doc(path: Path) -> ParsedFamilyDoc:
    raw_text = read_text_if_exists(path)
    title = find_first_heading(raw_text) or path.stem
    metadata_section = extract_section(raw_text, "Metadata")
    hypothesis_section = extract_section(raw_text, "Hypothesis")
    confirmed_section = extract_section(raw_text, "Confirmed Or Assumed Inputs")
    optimization_section = extract_section(raw_text, "Optimization Order")

    metadata_lines = {
        "Date": "",
        "Topic": "",
        "Region": "",
        "Universe": "",
        "Delay": "",
    }
    for line in metadata_section.splitlines():
        match = METADATA_BULLET_RE.match(line)
        if not match:
            continue
        label = match.group(1).strip()
        value = match.group(2).strip().strip("`")
        if label in metadata_lines:
            metadata_lines[label] = value

    code_blocks = extract_code_blocks(raw_text)
    baseline_expression = code_blocks[0] if code_blocks else None
    variant_expressions = tuple(code_blocks[1:]) if len(code_blocks) > 1 else tuple()

    confirmed_inputs = extract_bullets(confirmed_section)
    upstream_evidence = extract_bullets(metadata_section)
    optimization_order = extract_bullets(optimization_section)

    category_text = " ".join(
        (
            title,
            metadata_lines["Topic"],
            hypothesis_section,
            confirmed_section,
            baseline_expression or "",
            " ".join(variant_expressions),
        )
    )

    return ParsedFamilyDoc(
        path=path,
        title=title,
        topic=metadata_lines["Topic"] or path.stem,
        region=metadata_lines["Region"],
        universe=metadata_lines["Universe"],
        delay=metadata_lines["Delay"],
        category=infer_category(category_text),
        hypothesis=hypothesis_section,
        confirmed_inputs=confirmed_inputs,
        upstream_evidence=upstream_evidence,
        optimization_order=optimization_order,
        baseline_expression=baseline_expression,
        variant_expressions=variant_expressions,
        all_expressions=tuple(dict.fromkeys(code_blocks)),
        is_dead=has_kill_marker(raw_text),
        raw_text=raw_text,
    )


def load_family_docs(root: Path, include_dead: bool = True) -> tuple[ParsedFamilyDoc, ...]:
    docs: list[ParsedFamilyDoc] = []
    if root.is_file():
        candidate_paths = [root]
    else:
        candidate_paths = sorted(
            path
            for path in root.rglob("*.md")
            if path.name.lower() != "readme.md"
            and "template" not in path.name.lower()
        )
    for path in candidate_paths:
        doc = parse_family_doc(path)
        if include_dead or not doc.is_dead:
            docs.append(doc)
    return tuple(docs)


def parse_capture_json(path: Path) -> ParsedCapture:
    raw_text = read_text_if_exists(path)
    data = json.loads(raw_text)
    capture_id = str(data.get("capture_id") or path.stem)
    topic = str(data.get("topic") or "")
    expressions: list[str] = []
    for alpha in data.get("alphas", []):
        if isinstance(alpha, dict):
            expr = alpha.get("expression")
            if expr:
                expressions.append(str(expr))

    evidence = data.get("evidence") if isinstance(data.get("evidence"), dict) else {}
    notes: list[str] = []
    if isinstance(evidence, dict):
        raw_notes = evidence.get("notes")
        if isinstance(raw_notes, list):
            notes.extend(str(note) for note in raw_notes)
    has_check_submission = False
    for alpha in data.get("alphas", []):
        if not isinstance(alpha, dict):
            continue
        tests = alpha.get("tests")
        if isinstance(tests, dict) and tests.get("check_submission_pass") is not None:
            has_check_submission = True
            break

    raw_lower = raw_text.lower()
    is_dead = has_kill_marker(raw_lower) or has_kill_marker(" ".join(notes))
    return ParsedCapture(
        path=path,
        capture_id=capture_id,
        topic=topic,
        expressions=tuple(dict.fromkeys(expressions)),
        is_dead=is_dead,
        has_check_submission=has_check_submission,
        raw_text=raw_text,
    )


def load_captures(root: Path) -> tuple[ParsedCapture, ...]:
    if root.is_file():
        paths = [root]
    else:
        paths = sorted(root.rglob("*.json"))
    captures: list[ParsedCapture] = []
    for path in paths:
        try:
            capture = parse_capture_json(path)
        except Exception:
            continue
        captures.append(capture)
    return tuple(captures)


def canonicalize_expression(expression: str) -> str:
    text = expression.strip()
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*,\s*", ", ", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s*([+\-*/<>!=]=?|==)\s*", r"\1", text)
    return text.strip()


def abstract_expression(expression: str) -> str:
    text = canonicalize_expression(expression)
    text = NUMBER_RE.sub("<NUM>", text)
    text = re.sub(r"\b(industry|subindustry)\b", "<GROUP>", text)
    return text


def expression_signature(expression: str) -> str:
    return sha1(canonicalize_expression(expression).encode("utf-8")).hexdigest()


def tokenize_expression(expression: str) -> tuple[str, ...]:
    return tuple(TOKEN_RE.findall(canonicalize_expression(expression)))


def parse_function_calls(expression: str, *, _offset: int = 0) -> tuple[FunctionCall, ...]:
    text = canonicalize_expression(expression)
    calls: list[FunctionCall] = []
    index = 0
    while index < len(text):
        if not (text[index].isalpha() or text[index] == "_"):
            index += 1
            continue

        start = index
        while index < len(text) and (text[index].isalnum() or text[index] == "_"):
            index += 1
        name = text[start:index]
        if index >= len(text) or text[index] != "(":
            continue

        open_index = index
        depth = 1
        index += 1
        while index < len(text) and depth > 0:
            char = text[index]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            index += 1
        if depth != 0:
            break

        end = index - 1
        inner = text[open_index + 1 : end]
        args = split_top_level_args(inner)
        calls.append(
            FunctionCall(
                name=name,
                args=args,
                start=_offset + start,
                end=_offset + end,
                raw=text[start : end + 1],
            )
        )
        nested_calls = parse_function_calls(inner, _offset=_offset + open_index + 1)
        calls.extend(nested_calls)

    return tuple(sorted(calls, key=lambda call: (call.start, call.end, call.name)))


def split_top_level_args(argument_text: str) -> tuple[str, ...]:
    text = argument_text.strip()
    if not text:
        return tuple()

    args: list[str] = []
    depth = 0
    chunk_start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            args.append(text[chunk_start:index].strip())
            chunk_start = index + 1
    args.append(text[chunk_start:].strip())
    return tuple(args)


def count_function_calls(expression: str) -> int:
    return len(parse_function_calls(expression))


def max_parenthesis_depth(expression: str) -> int:
    depth = 0
    max_depth = 0
    for char in canonicalize_expression(expression):
        if char == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == ")":
            depth = max(0, depth - 1)
    return max_depth


def collect_window_values(expression: str) -> tuple[float, ...]:
    windows: list[float] = []
    for call in parse_function_calls(expression):
        if call.name not in WINDOW_FUNCTIONS:
            continue
        if len(call.args) < 2:
            continue
        try:
            windows.append(float(call.args[1]))
        except ValueError:
            continue
    return tuple(windows)


def collect_threshold_values(expression: str) -> tuple[float, ...]:
    thresholds: list[float] = []
    for _, value in COMPARATOR_NUMBER_RE.findall(canonicalize_expression(expression)):
        try:
            thresholds.append(float(value))
        except ValueError:
            continue
    return tuple(thresholds)


def infer_expression_categories(expression: str) -> tuple[str, ...]:
    text = canonicalize_expression(expression).lower()
    categories: list[str] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)
    return tuple(categories)


def family_keyword_score(family: ParsedFamilyDoc, expression: str) -> float:
    text = f"{family.title} {family.topic} {family.hypothesis} {' '.join(family.confirmed_inputs)} {family.raw_text}".lower()
    expr = canonicalize_expression(expression).lower()
    keywords = CATEGORY_KEYWORDS.get(family.category, ())
    if not keywords:
        keywords = CATEGORY_KEYWORDS["fundamental"]
    hits = sum(1 for keyword in keywords if keyword in text and keyword in expr)
    return clamp((hits / max(len(keywords), 1)) * 100.0, 0.0, 100.0)


def normalize_numeric_literals(expression: str) -> str:
    return NUMBER_RE.sub("<NUM>", canonicalize_expression(expression))


def similarity_score(left: str, right: str) -> float:
    left_c = canonicalize_expression(left)
    right_c = canonicalize_expression(right)
    left_a = normalize_numeric_literals(left)
    right_a = normalize_numeric_literals(right)
    raw = SequenceMatcher(None, left_c, right_c).ratio()
    abstract = SequenceMatcher(None, left_a, right_a).ratio()
    return (0.65 * raw) + (0.35 * abstract)


def best_similarity(candidate: str, population: Sequence[str]) -> float:
    if not population:
        return 0.0
    best = 0.0
    for other in population:
        score = similarity_score(candidate, other)
        if score > best:
            best = score
    return best


def build_expression_bank(
    family_docs: Sequence[ParsedFamilyDoc],
    captures: Sequence[ParsedCapture] | None = None,
) -> dict[str, list[str]]:
    seeds: list[str] = []
    dead: list[str] = []
    history: list[str] = []
    live_capture_exprs: list[str] = []

    for doc in family_docs:
        exprs = [expr for expr in doc.all_expressions if expr]
        if doc.is_dead:
            dead.extend(exprs)
        else:
            seeds.extend(exprs)

    for capture in captures or ():
        exprs = [expr for expr in capture.expressions if expr]
        history.extend(exprs)
        if capture.is_dead:
            dead.extend(exprs)
        else:
            live_capture_exprs.extend(exprs)

    return {
        "seeds": dedupe_strings(seeds),
        "dead": dedupe_strings(dead),
        "history": dedupe_strings(history),
        "live_capture_exprs": dedupe_strings(live_capture_exprs),
    }


def dedupe_strings(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        canonical = canonicalize_expression(value)
        if canonical in seen:
            continue
        seen.add(canonical)
        deduped.append(canonical)
    return deduped


def load_token_replacements(path: Path | None) -> tuple[dict[str, Any], ...]:
    if path is None:
        return tuple()
    data = json.loads(path.read_text(encoding="utf-8"))
    rules: list[dict[str, Any]] = []
    if isinstance(data, dict):
        for pattern, replacements in data.items():
            if isinstance(replacements, str):
                replacements = [replacements]
            rules.append({"pattern": str(pattern), "replacements": list(replacements)})
    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            pattern = item.get("pattern")
            replacements = item.get("replacements", [])
            if isinstance(replacements, str):
                replacements = [replacements]
            if pattern:
                rules.append({"pattern": str(pattern), "replacements": list(replacements)})
    return tuple(rules)


def _replace_first(pattern: str, replacement: str, text: str) -> str | None:
    compiled = re.compile(pattern)

    def _sub(match: re.Match[str]) -> str:
        return replacement

    new_text, count = compiled.subn(_sub, text, count=1)
    if count == 0:
        return None
    return new_text


def apply_group_mutation(expression: str, from_group: str, to_group: str) -> str | None:
    if from_group == to_group:
        return None
    pattern = rf"\b{re.escape(from_group)}\b"
    return _replace_first(pattern, to_group, expression)


def apply_token_mutation(expression: str, pattern: str, replacement: str) -> str | None:
    return _replace_first(pattern, replacement, expression)


def apply_threshold_mutation(expression: str, old_value: float | str, new_value: float | str) -> str | None:
    old_text = str(old_value)
    new_text = str(new_value)
    pattern = rf"([<>]=?|==|!=)\s*{re.escape(old_text)}\b"
    return _replace_first(pattern, rf"\1 {new_text}", expression)


def apply_window_mutation(
    expression: str,
    function_name: str,
    old_value: float | str,
    new_value: float | str,
) -> str | None:
    old_text = str(old_value)
    new_text = str(new_value)
    text = canonicalize_expression(expression)
    calls = parse_function_calls(text)
    for call in calls:
        if call.name != function_name or len(call.args) < 2:
            continue
        if canonicalize_expression(call.args[1]) != canonicalize_expression(old_text):
            continue
        new_args = list(call.args)
        new_args[1] = new_text
        replacement = f"{call.name}({', '.join(new_args)})"
        return canonicalize_expression(text[: call.start] + replacement + text[call.end + 1 :])
    return None


def primitive_mutations(
    expression: str,
    window_grid: Sequence[int] = DEFAULT_WINDOW_GRID,
    threshold_grid: Sequence[float] = DEFAULT_THRESHOLD_GRID,
    group_variants: Sequence[str] = DEFAULT_GROUP_VARIANTS,
    token_rules: Sequence[dict[str, Any]] = (),
) -> tuple[MutationPlan, ...]:
    plans: list[MutationPlan] = []
    canonical = canonicalize_expression(expression)

    for call in parse_function_calls(canonical):
        if call.name not in WINDOW_FUNCTIONS or len(call.args) < 2:
            continue
        current_value = call.args[1]
        try:
            current_numeric = float(current_value)
        except ValueError:
            continue
        ordered_windows = sorted(
            {
                int(window)
                for window in window_grid
                if int(window) != int(current_numeric)
            },
            key=lambda window: (abs(window - current_numeric), window),
        )
        for window in ordered_windows:
            priority = 1.0 / (1.0 + abs(window - current_numeric))
            plans.append(
                MutationPlan(
                    kind="window",
                    description=f"{call.name}[{current_value}->{window}]",
                    payload={
                        "function_name": call.name,
                        "old_value": current_value,
                        "new_value": window,
                    },
                    priority=priority,
                )
            )

    for match in COMPARATOR_NUMBER_RE.finditer(canonical):
        current_value = match.group(2)
        try:
            current_numeric = float(current_value)
        except ValueError:
            continue
        ordered_thresholds = sorted(
            {
                float(threshold)
                for threshold in threshold_grid
                if float(threshold) != current_numeric
            },
            key=lambda threshold: (abs(threshold - current_numeric), threshold),
        )
        for threshold in ordered_thresholds:
            priority = 1.0 / (1.0 + abs(threshold - current_numeric))
            plans.append(
                MutationPlan(
                    kind="threshold",
                    description=f"threshold[{current_value}->{threshold}]",
                    payload={"old_value": current_value, "new_value": threshold},
                    priority=priority,
                )
            )

    for group in group_variants:
        if group == "industry" and "subindustry" in canonical:
            plan = MutationPlan(
                kind="group",
                description="group[subindustry->industry]",
                payload={"from_group": "subindustry", "to_group": "industry"},
                priority=0.8,
            )
            plans.append(plan)
        elif group == "subindustry" and "industry" in canonical:
            plan = MutationPlan(
                kind="group",
                description="group[industry->subindustry]",
                payload={"from_group": "industry", "to_group": "subindustry"},
                priority=0.8,
            )
            plans.append(plan)

    for rule in token_rules:
        pattern = rule.get("pattern")
        replacements = rule.get("replacements", [])
        if not pattern or not replacements:
            continue
        compiled = re.compile(str(pattern))
        if not compiled.search(canonical):
            continue
        for replacement in replacements:
            if compiled.subn(str(replacement), canonical, count=1)[1] == 0:
                continue
            plans.append(
                MutationPlan(
                    kind="token",
                    description=f"token[{pattern}->{replacement}]",
                    payload={"pattern": str(pattern), "replacement": str(replacement)},
                    priority=0.6,
                )
            )

    ordered = sorted(
        plans,
        key=lambda plan: (-plan.priority, plan.kind, plan.description),
    )
    unique: list[MutationPlan] = []
    seen: set[str] = set()
    for plan in ordered:
        key = json.dumps(plan.payload, sort_keys=True) + f"|{plan.kind}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(plan)
    return tuple(unique)


def apply_mutation(expression: str, plan: MutationPlan) -> str | None:
    if plan.kind == "window":
        return apply_window_mutation(
            expression,
            str(plan.payload["function_name"]),
            plan.payload["old_value"],
            plan.payload["new_value"],
        )
    if plan.kind == "threshold":
        return apply_threshold_mutation(
            expression,
            plan.payload["old_value"],
            plan.payload["new_value"],
        )
    if plan.kind == "group":
        return apply_group_mutation(
            expression,
            str(plan.payload["from_group"]),
            str(plan.payload["to_group"]),
        )
    if plan.kind == "token":
        return apply_token_mutation(
            expression,
            str(plan.payload["pattern"]),
            str(plan.payload["replacement"]),
        )
    return None


def mutation_chain_label(chain: Sequence[MutationPlan]) -> str:
    if not chain:
        return "baseline"
    return " | ".join(plan.description for plan in chain)


def quality_metrics(
    candidate_expression: str,
    family: ParsedFamilyDoc | None = None,
    seed_population: Sequence[str] = (),
    dead_population: Sequence[str] = (),
    history_population: Sequence[str] = (),
) -> dict[str, Any]:
    canonical = canonicalize_expression(candidate_expression)
    abstract = abstract_expression(candidate_expression)
    function_calls = parse_function_calls(canonical)
    windows = collect_window_values(canonical)
    thresholds = collect_threshold_values(canonical)
    categories = infer_expression_categories(canonical)
    category_count = len(categories)
    op_count = len(function_calls)
    depth = max_parenthesis_depth(canonical)

    seed_similarity = best_similarity(canonical, seed_population)
    dead_similarity = best_similarity(canonical, dead_population)
    history_similarity = best_similarity(canonical, history_population)
    family_keyword = family_keyword_score(family, canonical) if family else 0.0
    family_category = family.category if family else infer_category(canonical)

    health_score = 100.0
    health_score -= max(0, op_count - 6) * 5.0
    health_score -= max(0, depth - 6) * 6.0
    health_score -= max(0, len(windows) - 4) * 7.0
    health_score -= max(0, len(thresholds) - 2) * 4.0
    health_score -= max(0, category_count - 1) * 18.0
    if op_count == 0:
        health_score -= 20.0
    if op_count in {1, 2, 3, 4}:
        health_score += 8.0
    if any(call.name in FUNCTIONS_THAT_SIGNAL_STABILITY for call in function_calls):
        health_score += 6.0
    if family and family.category != "general" and family.category in categories:
        health_score += 8.0
    health_score = clamp(health_score, 0.0, 100.0)

    convergence_target = 0.78
    convergence_score = clamp(100.0 - abs(seed_similarity - convergence_target) * 180.0, 0.0, 100.0)

    novelty_score = clamp(100.0 * (1.0 - max(history_similarity, dead_similarity)), 0.0, 100.0)
    family_fit_score = clamp(0.7 * seed_similarity * 100.0 + 0.3 * family_keyword, 0.0, 100.0)

    stability_score = 30.0
    if any(call.name in {"ts_mean", "ts_zscore"} for call in function_calls):
        stability_score += 18.0
    if any(call.name in {"group_neutralize", "group_rank"} for call in function_calls):
        stability_score += 14.0
    if any(call.name == "trade_when" for call in function_calls):
        stability_score += 10.0
    if len(windows) <= 2:
        stability_score += 8.0
    if len(windows) > 4:
        stability_score -= (len(windows) - 4) * 4.0
    if family and family.category in {"sentiment_news", "fundamental", "event_trigger"}:
        stability_score += 6.0
    stability_score = clamp(stability_score, 0.0, 100.0)

    overfit_risk = 0.0
    overfit_risk += max(0, op_count - 5) * 7.0
    overfit_risk += max(0, depth - 5) * 7.0
    overfit_risk += max(0, len(windows) - 3) * 8.0
    overfit_risk += max(0, len(thresholds) - 2) * 6.0
    overfit_risk += max(0, category_count - 1) * 16.0
    if seed_similarity < 0.35:
        overfit_risk += 18.0
    if dead_similarity > 0.55:
        overfit_risk += (dead_similarity - 0.55) * 100.0
    overfit_risk = clamp(overfit_risk, 0.0, 100.0)

    coupling_risk = 0.0
    coupling_risk += max(0, category_count - 1) * 24.0
    if family and family.category != "general" and family.category not in categories:
        coupling_risk += 18.0
    coupling_risk = clamp(coupling_risk, 0.0, 100.0)

    raw_score = (
        0.22 * health_score
        + 0.20 * convergence_score
        + 0.18 * novelty_score
        + 0.18 * family_fit_score
        + 0.12 * stability_score
        - 0.20 * overfit_risk
        - 0.15 * coupling_risk
    )
    final_score = clamp(raw_score, 0.0, 100.0)

    if dead_similarity > 0.82 or (seed_similarity < 0.25 and family_fit_score < 20.0):
        decision = "drop"
    elif overfit_risk > 70.0 or coupling_risk > 60.0:
        decision = "drop"
    elif final_score >= 62.0 and overfit_risk <= 55.0 and coupling_risk <= 45.0:
        decision = "keep"
    else:
        decision = "review"

    return {
        "canonical_expression": canonical,
        "abstract_expression": abstract,
        "signature": expression_signature(canonical),
        "function_call_count": op_count,
        "parenthesis_depth": depth,
        "window_values": windows,
        "threshold_values": thresholds,
        "categories": categories,
        "category_count": category_count,
        "family_category": family_category,
        "seed_similarity": round(seed_similarity, 4),
        "dead_similarity": round(dead_similarity, 4),
        "history_similarity": round(history_similarity, 4),
        "family_keyword_score": round(family_keyword, 2),
        "health_score": round(health_score, 2),
        "convergence_score": round(convergence_score, 2),
        "novelty_score": round(novelty_score, 2),
        "family_fit_score": round(family_fit_score, 2),
        "stability_score": round(stability_score, 2),
        "overfit_risk": round(overfit_risk, 2),
        "coupling_risk": round(coupling_risk, 2),
        "score": round(final_score, 2),
        "decision": decision,
    }


def candidate_from_expression(
    expression: str,
    family: ParsedFamilyDoc,
    source_expression: str,
    source_doc: str,
    chain: Sequence[MutationPlan],
    seed_population: Sequence[str],
    dead_population: Sequence[str],
    history_population: Sequence[str],
) -> dict[str, Any]:
    metrics = quality_metrics(
        expression,
        family=family,
        seed_population=seed_population,
        dead_population=dead_population,
        history_population=history_population,
    )
    return {
        "candidate_id": sha1(
            f"{family.topic}|{metrics['signature']}|{mutation_chain_label(chain)}".encode("utf-8")
        ).hexdigest()[:16],
        "family_topic": family.topic,
        "family_category": family.category,
        "source_doc": source_doc,
        "source_expression": canonicalize_expression(source_expression),
        "expression": canonicalize_expression(expression),
        "mutations": [plan.description for plan in chain],
        "mutation_depth": len(chain),
        "scorecard": metrics,
    }


def write_jsonl(records: Iterable[dict[str, Any]], path: Path | None) -> None:
    text = "\n".join(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records)
    if path is None:
        print(text)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def read_jsonl(path: Path) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return tuple()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return tuple(records)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarise_family(doc: ParsedFamilyDoc) -> dict[str, Any]:
    return {
        "path": str(doc.path),
        "title": doc.title,
        "topic": doc.topic,
        "region": doc.region,
        "universe": doc.universe,
        "delay": doc.delay,
        "category": doc.category,
        "baseline_expression": doc.baseline_expression,
        "variant_count": len(doc.variant_expressions),
        "expression_count": len(doc.all_expressions),
        "is_dead": doc.is_dead,
    }


def summarise_capture(capture: ParsedCapture) -> dict[str, Any]:
    return {
        "path": str(capture.path),
        "capture_id": capture.capture_id,
        "topic": capture.topic,
        "expression_count": len(capture.expressions),
        "is_dead": capture.is_dead,
        "has_check_submission": capture.has_check_submission,
    }

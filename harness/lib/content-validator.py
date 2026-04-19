#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parents[1] / "verification-modes.json"

PLACEHOLDER_FRAGMENTS = [
    "replace-me",
    "replace me",
    "replace this",
    "replace with real",
    "write one plain-language hypothesis",
    "write the plain-language hypothesis",
    "write the real result summary",
    "write the first real bottleneck",
    "summarize the main research focus of the week",
]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(21)


def contains_placeholder(text: str) -> bool:
    lowered = text.lower()
    return any(fragment in lowered for fragment in PLACEHOLDER_FRAGMENTS)


def walk_strings(node, path: str = "root") -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "_instructions":
                fail(f"Template metadata key is not allowed in run output: {path}._instructions")
            walk_strings(value, f"{path}.{key}")
        return
    if isinstance(node, list):
        for index, value in enumerate(node):
            walk_strings(value, f"{path}[{index}]")
        return
    if isinstance(node, str) and contains_placeholder(node):
        fail(f"Placeholder content detected at {path}")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_registry() -> dict:
    payload = load_json(REGISTRY_PATH)
    modes = payload.get("modes")
    require(isinstance(modes, dict) and modes, f"Invalid verification mode registry: {REGISTRY_PATH}")
    return modes


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate_markdown(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    require(not contains_placeholder(text), f"Placeholder content detected in markdown file: {path}")

    non_empty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    require(len(non_empty_lines) >= 5, f"Markdown file is too small to count as a real work product: {path}")
    require(len(" ".join(non_empty_lines)) >= 80, f"Markdown file is too short to count as a real work product: {path}")


def validate_research_queue(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)

    items = payload.get("items")
    require(isinstance(items, list) and len(items) >= 2, "Research queue must contain at least two items.")
    for index, item in enumerate(items):
        require(bool(item.get("name")), f"Queue item {index} is missing a name.")
        require(bool(item.get("current_status")), f"Queue item {index} is missing current_status.")
        require(bool(item.get("next_step")), f"Queue item {index} is missing next_step.")


def validate_candidate_batch(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)

    candidates = payload.get("candidates")
    require(isinstance(candidates, list) and candidates, "Candidate batch must contain at least one candidate.")
    required_fields = [
        "name",
        "delay",
        "sharpe",
        "fitness",
        "turnover",
        "max_weight",
        "self_corr",
        "subuniverse_pass",
        "test_period_pass",
        "notes",
    ]
    real_required_fields = [
        "sharpe",
        "fitness",
        "turnover",
        "subuniverse_pass",
    ]
    optional_fallback_fields = {
        "max_weight": ["max_weight_check"],
        "self_corr": ["self_corr_check"],
        "test_period_pass": ["test_period_observation"],
    }
    for index, candidate in enumerate(candidates):
        for field in required_fields:
            require(field in candidate, f"Candidate {index} is missing required field {field}.")
        for field in real_required_fields:
            require(candidate.get(field) is not None, f"Candidate {index} is missing real value for {field}.")
        require(bool(candidate.get("notes")), f"Candidate {index} must include notes.")
        for field, fallback_fields in optional_fallback_fields.items():
            if candidate.get(field) is not None:
                continue
            require(
                any(candidate.get(fallback_field) not in (None, "") for fallback_field in fallback_fields),
                (
                    f"Candidate {index} is missing both {field} and its fallback explanation "
                    f"({', '.join(fallback_fields)})."
                ),
            )


def validate_daily_note(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)
    require(bool(payload.get("result_summary")), "Daily note result_summary is required.")
    require(bool(payload.get("first_failure")), "Daily note first_failure is required.")
    next_experiments = payload.get("next_experiments")
    require(isinstance(next_experiments, list) and next_experiments, "Daily note must include next_experiments.")


def validate_weekly_review(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)
    require(bool(payload.get("focus")), "Weekly review focus is required.")
    require(isinstance(payload.get("wins"), list) and payload.get("wins"), "Weekly review wins are required.")
    require(isinstance(payload.get("lessons"), list) and payload.get("lessons"), "Weekly review lessons are required.")


def validate_simulation_capture(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)

    require(bool(payload.get("capture_id")), "Simulation capture_id is required.")
    require(bool(payload.get("topic")), "Simulation topic is required.")
    alphas = payload.get("alphas")
    require(isinstance(alphas, list) and alphas, "Simulation capture must contain at least one alpha.")
    for index, alpha in enumerate(alphas):
        metrics = alpha.get("metrics", {})
        numeric_fields = ["sharpe", "fitness", "turnover", "returns", "max_weight"]
        require(
            any(metrics.get(field) is not None for field in numeric_fields),
            f"Simulation alpha {index} must include at least one real metric.",
        )


VALIDATORS = {
    "validate_research_queue": validate_research_queue,
    "validate_candidate_batch": validate_candidate_batch,
    "validate_daily_note": validate_daily_note,
    "validate_weekly_review": validate_weekly_review,
    "validate_markdown": validate_markdown,
    "validate_simulation_capture": validate_simulation_capture,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True)
    parser.add_argument("--path", required=True)
    args = parser.parse_args()

    path = Path(args.path)
    mode = args.mode
    registry = load_registry()
    mode_config = registry.get(mode)
    require(isinstance(mode_config, dict), f"Unsupported content validation mode: {mode}")
    validator_name = mode_config.get("validator")
    require(isinstance(validator_name, str) and validator_name, f"Verification mode {mode} is missing a validator.")
    validator = VALIDATORS.get(validator_name)
    require(validator is not None, f"Verification mode {mode} references unknown validator: {validator_name}")
    validator(path)


if __name__ == "__main__":
    main()

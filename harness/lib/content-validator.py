#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
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


def _canonicalize_expression(expression: str) -> str:
    text = expression.strip().replace("\r\n", "\n")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*,\s*", ", ", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s*([+\-*/<>!=]=?|==)\s*", r"\1", text)
    return text.strip()


def _strip_wrapping_parentheses(expression: str) -> str:
    text = expression.strip()
    while text.startswith("(") and text.endswith(")") and len(text) >= 2:
        inner = text[1:-1].strip()
        depth = 0
        balanced = True
        for char in inner:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    balanced = False
                    break
        if not balanced or depth != 0:
            break
        text = inner
    return text


def _is_sign_flip_expression(candidate: str, source: str) -> bool:
    source_text = _strip_wrapping_parentheses(_canonicalize_expression(source))
    if not source_text:
        return False

    candidate_text = _canonicalize_expression(candidate)
    expected_forms = {
        f"-{source_text}",
        f"-1*{source_text}",
        f"-({source_text})",
        f"-1*({source_text})",
    }
    return candidate_text in expected_forms


def _alpha_metric_value(alpha: dict, *field_names: str) -> float | None:
    metrics = alpha.get("metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}

    for field_name in field_names:
        for source in (metrics, alpha):
            value = source.get(field_name) if isinstance(source, dict) else None
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return None


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

    batch_policy = payload.get("batch_policy")
    if batch_policy is not None:
        require(isinstance(batch_policy, dict), "Simulation batch_policy must be a JSON object when present.")
        required_sign_flip_source_index = batch_policy.get("required_sign_flip_source_index")
        if required_sign_flip_source_index is not None:
            require(
                isinstance(required_sign_flip_source_index, int) and required_sign_flip_source_index in {0, 1},
                "Simulation batch_policy.required_sign_flip_source_index must be 0 or 1 when present.",
            )
            required_sign_flip_reason = batch_policy.get("required_sign_flip_reason")
            require(
                isinstance(required_sign_flip_reason, str) and required_sign_flip_reason.strip(),
                "Simulation batch_policy.required_sign_flip_reason is required when sign-flip control is mandatory.",
            )
            source_index = required_sign_flip_source_index
            flip_index = source_index + 1
            require(
                flip_index < len(alphas),
                "Simulation capture must include the mandatory sign-flip control immediately after the negative source control.",
            )
            source_alpha = alphas[source_index]
            flip_alpha = alphas[flip_index]
            source_sharpe = _alpha_metric_value(source_alpha, "sharpe", "is_sharpe")
            require(
                source_sharpe is not None and source_sharpe < 0,
                f"Simulation batch_policy points to alpha {source_index}, but its Sharpe is not negative.",
            )
            source_expression = str(source_alpha.get("expression") or "")
            flip_expression = str(flip_alpha.get("expression") or "")
            require(
                _is_sign_flip_expression(flip_expression, source_expression),
                (
                    "Simulation capture must place the sign-flipped final executable expression "
                    f"immediately after the negative source control at index {source_index}."
                ),
            )


def validate_field_readiness(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)

    items = payload.get("items")
    require(isinstance(items, list), "Field readiness payload must include an items list.")
    counts = payload.get("counts")
    require(isinstance(counts, dict), "Field readiness payload must include counts.")
    require(
        int(counts.get("family_count", 0)) == len(items),
        "Field readiness family_count must match the number of items.",
    )

    allowed_statuses = {"pass", "hold", "block"}
    for index, item in enumerate(items):
        require(bool(item.get("family_key")), f"Field readiness item {index} is missing family_key.")
        require(
            isinstance(item.get("candidate_fields"), list),
            f"Field readiness item {index} must include candidate_fields.",
        )
        require(
            isinstance(item.get("usable_candidate_fields"), list),
            f"Field readiness item {index} must include usable_candidate_fields.",
        )
        require(
            isinstance(item.get("blocked_candidate_fields"), list),
            f"Field readiness item {index} must include blocked_candidate_fields.",
        )
        require(
            isinstance(item.get("coverage_by_field"), dict),
            f"Field readiness item {index} must include coverage_by_field.",
        )
        assessment = item.get("assessment")
        require(isinstance(assessment, dict), f"Field readiness item {index} is missing assessment.")
        gate_status = assessment.get("gate_status")
        require(
            gate_status in allowed_statuses,
            f"Field readiness item {index} has invalid gate_status {gate_status!r}.",
        )
        reasons = assessment.get("reasons")
        require(
            isinstance(reasons, list) and reasons,
            f"Field readiness item {index} must include non-empty assessment reasons.",
        )


def validate_account_capability(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)

    items = payload.get("items")
    require(isinstance(items, list), "Account-capability payload must include an items list.")
    counts = payload.get("counts")
    require(isinstance(counts, dict), "Account-capability payload must include counts.")
    require(
        int(counts.get("family_count", 0)) == len(items),
        "Account-capability family_count must match the number of items.",
    )

    allowed_statuses = {"pass", "hold", "block"}
    observed_counts = {status: 0 for status in allowed_statuses}
    for index, item in enumerate(items):
        require(bool(item.get("family_key")), f"Account-capability item {index} is missing family_key.")
        required_scope = item.get("required_scope")
        require(
            isinstance(required_scope, dict),
            f"Account-capability item {index} must include required_scope.",
        )
        for field_name in ("region", "delay", "universe", "data_category"):
            require(
                field_name in required_scope,
                f"Account-capability item {index} is missing required_scope.{field_name}.",
            )
        snapshot = item.get("capability_snapshot")
        require(
            isinstance(snapshot, dict),
            f"Account-capability item {index} must include capability_snapshot.",
        )
        observed_combo_count = snapshot.get("observed_combo_count")
        require(
            isinstance(observed_combo_count, int) and observed_combo_count >= 0,
            (
                f"Account-capability item {index} must include non-negative integer "
                f"observed_combo_count, got {observed_combo_count!r}."
            ),
        )
        for field_name in (
            "observed_regions",
            "observed_delays",
            "observed_universes",
            "observed_categories",
            "public_tier_notes",
        ):
            require(
                isinstance(snapshot.get(field_name), list),
                f"Account-capability item {index} must include list field capability_snapshot.{field_name}.",
            )
        matching_combo = snapshot.get("matching_combo")
        require(
            matching_combo is None or isinstance(matching_combo, dict),
            f"Account-capability item {index} has invalid matching_combo payload.",
        )
        assessment = item.get("assessment")
        require(isinstance(assessment, dict), f"Account-capability item {index} is missing assessment.")
        gate_status = assessment.get("gate_status")
        require(
            gate_status in allowed_statuses,
            f"Account-capability item {index} has invalid gate_status {gate_status!r}.",
        )
        reasons = assessment.get("reasons")
        require(
            isinstance(reasons, list) and reasons,
            f"Account-capability item {index} must include non-empty assessment reasons.",
        )
        observed_counts[gate_status] += 1

    for status, observed_count in observed_counts.items():
        require(
            int(counts.get(f"{status}_count", 0)) == observed_count,
            (
                f"Account-capability count mismatch for {status}: "
                f"expected {observed_count}, got {counts.get(f'{status}_count')!r}."
            ),
        )


def validate_research_contract(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)

    items = payload.get("items")
    require(isinstance(items, list), "Research-contract payload must include an items list.")
    counts = payload.get("counts")
    require(isinstance(counts, dict), "Research-contract payload must include counts.")
    require(
        int(counts.get("family_count", 0)) == len(items),
        "Research-contract family_count must match the number of items.",
    )

    allowed_statuses = {"pass", "hold", "block"}
    for index, item in enumerate(items):
        require(bool(item.get("family_key")), f"Research-contract item {index} is missing family_key.")
        require(
            isinstance(item.get("source_family_doc_paths"), list),
            f"Research-contract item {index} must include source_family_doc_paths.",
        )
        require(
            isinstance(item.get("contract"), dict),
            f"Research-contract item {index} must include a contract object.",
        )
        assessment = item.get("assessment")
        require(isinstance(assessment, dict), f"Research-contract item {index} is missing assessment.")
        gate_status = assessment.get("gate_status")
        require(
            gate_status in allowed_statuses,
            f"Research-contract item {index} has invalid gate_status {gate_status!r}.",
        )
        reasons = assessment.get("reasons")
        require(
            isinstance(reasons, list) and reasons,
            f"Research-contract item {index} must include non-empty assessment reasons.",
        )


def validate_evidence_ladder(path: Path) -> None:
    payload = load_json(path)
    walk_strings(payload)

    items = payload.get("items")
    require(isinstance(items, list), "Evidence-ladder payload must include an items list.")
    counts = payload.get("counts")
    require(isinstance(counts, dict), "Evidence-ladder payload must include counts.")
    require(
        int(counts.get("family_count", 0)) == len(items),
        "Evidence-ladder family_count must match the number of items.",
    )

    allowed_levels = {
        "E0_front_gate_only",
        "E1_local_support",
        "E2_partial_official",
        "E3_full_is",
        "E4_submit_ready",
    }
    allowed_ceilings = {"explore", "branch", "exploit"}
    allowed_effective_states = {"explore", "branch", "exploit", "hold", "kill"}
    observed_level_counts = {level: 0 for level in allowed_levels}
    for index, item in enumerate(items):
        require(bool(item.get("family_key")), f"Evidence-ladder item {index} is missing family_key.")
        require(
            isinstance(item.get("counts"), dict),
            f"Evidence-ladder item {index} must include counts.",
        )
        assessment = item.get("assessment")
        require(isinstance(assessment, dict), f"Evidence-ladder item {index} is missing assessment.")
        evidence_level = assessment.get("evidence_level")
        require(
            evidence_level in allowed_levels,
            f"Evidence-ladder item {index} has invalid evidence_level {evidence_level!r}.",
        )
        promotion_ceiling = assessment.get("promotion_ceiling")
        require(
            promotion_ceiling in allowed_ceilings,
            f"Evidence-ladder item {index} has invalid promotion_ceiling {promotion_ceiling!r}.",
        )
        effective_state = assessment.get("effective_state")
        require(
            effective_state in allowed_effective_states,
            f"Evidence-ladder item {index} has invalid effective_state {effective_state!r}.",
        )
        require(
            isinstance(assessment.get("evidence_source"), str) and bool(assessment.get("evidence_source")),
            f"Evidence-ladder item {index} must include evidence_source.",
        )
        branch_budget_remaining = assessment.get("branch_budget_remaining")
        require(
            isinstance(branch_budget_remaining, int) and branch_budget_remaining >= 0,
            (
                f"Evidence-ladder item {index} must include non-negative integer "
                f"branch_budget_remaining, got {branch_budget_remaining!r}."
            ),
        )
        official_budget_cap = assessment.get("official_budget_cap")
        require(
            isinstance(official_budget_cap, int) and official_budget_cap >= 1,
            (
                f"Evidence-ladder item {index} must include integer official_budget_cap >= 1, "
                f"got {official_budget_cap!r}."
            ),
        )
        reasons = assessment.get("reasons")
        require(
            isinstance(reasons, list) and reasons,
            f"Evidence-ladder item {index} must include non-empty assessment reasons.",
        )
        observed_level_counts[evidence_level] += 1

    for level, observed_count in observed_level_counts.items():
        require(
            int(counts.get(level, 0)) == observed_count,
            (
                f"Evidence-ladder count mismatch for {level}: "
                f"expected {observed_count}, got {counts.get(level)!r}."
            ),
        )


VALIDATORS = {
    "validate_research_queue": validate_research_queue,
    "validate_candidate_batch": validate_candidate_batch,
    "validate_daily_note": validate_daily_note,
    "validate_weekly_review": validate_weekly_review,
    "validate_markdown": validate_markdown,
    "validate_simulation_capture": validate_simulation_capture,
    "validate_field_readiness": validate_field_readiness,
    "validate_account_capability": validate_account_capability,
    "validate_research_contract": validate_research_contract,
    "validate_evidence_ladder": validate_evidence_ladder,
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

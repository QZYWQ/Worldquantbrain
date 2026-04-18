#!/usr/bin/env python3

from collections import Counter
from datetime import datetime
from pathlib import PurePosixPath
import re


PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def build_feature_index(features):
    return {feature.get("id"): feature for feature in features if feature.get("id")}


def dependencies_done(feature, by_id) -> bool:
    for dep in feature.get("dependencies", []):
        dep_feature = by_id.get(dep)
        if dep_feature is None or dep_feature.get("status") != "completed":
            return False
    return True


def missing_dependencies(feature, by_id):
    missing = []
    for dep in feature.get("dependencies", []):
        dep_feature = by_id.get(dep)
        if dep_feature is None or dep_feature.get("status") != "completed":
            missing.append(dep)
    return missing


def actionable_pending_features(features, by_id):
    pending = [
        feature for feature in features
        if feature.get("status") == "pending" and dependencies_done(feature, by_id)
    ]
    pending.sort(key=lambda item: (PRIORITY_RANK.get(item.get("priority", "P9"), 9), item.get("id", "")))
    return pending


def is_bootstrap_cycle(payload, cycle_rel: str) -> bool:
    return payload.get("cycle_type") == "bootstrap" or cycle_rel == "./harness/feature_list.json"


def build_cycle_overview(payload, cycle_rel: str):
    features = payload.get("features", [])
    by_id = build_feature_index(features)
    actionable_pending = actionable_pending_features(features, by_id)
    in_progress = [feature for feature in features if feature.get("status") == "in_progress"]
    blocked = [feature for feature in features if feature.get("status") == "blocked"]
    completed = [feature for feature in features if feature.get("status") == "completed"]

    return {
        "cycle_type": payload.get("cycle_type", "unknown"),
        "cycle_profile": payload.get("cycle_profile", "unknown"),
        "project_goal": payload.get("project_goal", "unknown"),
        "is_bootstrap": is_bootstrap_cycle(payload, cycle_rel),
        "counts": Counter(feature.get("status", "unknown") for feature in features),
        "feature_total": len(features),
        "features": features,
        "by_id": by_id,
        "actionable_pending": actionable_pending,
        "next_id": actionable_pending[0].get("id", "none") if actionable_pending else "none",
        "in_progress": in_progress,
        "blocked": blocked,
        "completed": completed,
    }


def build_focus_selection(overview):
    in_progress = overview["in_progress"]
    actionable_pending = overview["actionable_pending"]
    focus_feature = None
    recommendation_heading = "No actionable feature available."
    selection_reason = "No actionable feature is currently available."
    selection_state = "none"

    if len(in_progress) == 1:
        focus_feature = in_progress[0]
        recommendation_heading = (
            f"Resume in-progress feature: {focus_feature.get('id')} | {focus_feature.get('title')}"
        )
        selection_reason = (
            "This feature is already in progress and should be resumed: "
            f"{focus_feature.get('id')} | {focus_feature.get('title')}"
        )
        selection_state = "resume"
    elif len(in_progress) > 1:
        ids = ", ".join(feature.get("id", "unknown") for feature in in_progress)
        recommendation_heading = f"No safe recommendation because multiple in-progress features exist: {ids}"
        selection_reason = (
            "Multiple in-progress features exist, so no safe automatic execution target is available: "
            f"{ids}"
        )
        selection_state = "ambiguous"
    elif actionable_pending:
        focus_feature = actionable_pending[0]
        recommendation_heading = (
            f"Start next actionable feature: {focus_feature.get('id')} | {focus_feature.get('title')}"
        )
        selection_reason = (
            "This is the highest-priority actionable pending feature with dependencies satisfied: "
            f"{focus_feature.get('id')} | {focus_feature.get('title')}"
        )
        selection_state = "next"

    return {
        "focus_feature": focus_feature,
        "recommendation_heading": recommendation_heading,
        "selection_reason": selection_reason,
        "selection_state": selection_state,
    }


def build_session_brief_rel_path(cycle_rel: str, focus_feature=None) -> str:
    rel = PurePosixPath(cycle_rel.replace("./", "", 1))
    feature_id = focus_feature.get("id", "") if focus_feature else ""
    slug_source = feature_id if feature_id else rel.stem
    slug = re.sub(r"[^a-z0-9]+", "-", slug_source.lower()).strip("-") or "session"
    today = datetime.now().astimezone().strftime("%Y-%m-%d")
    return f"./runs/session-briefs/{today}-{slug}.md"

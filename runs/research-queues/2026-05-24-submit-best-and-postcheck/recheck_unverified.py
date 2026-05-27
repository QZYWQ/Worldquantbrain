#!/usr/bin/env python3
"""Recheck only candidates whose post-submit check returned empty/unverified."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("submit_best_and_postcheck.py")
spec = importlib.util.spec_from_file_location("submit_best_and_postcheck", SCRIPT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load {SCRIPT_PATH}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main() -> None:
    payload = json.loads(module.OUTPUT_JSON.read_text(encoding="utf-8"))
    session = module.login()
    selected_alpha_id = payload["selected_alpha_id"]
    updated = []

    for record in payload["post_submit_candidate_checks"]:
        cls = record.get("postcheck_classification") or {}
        if cls.get("category") != "check_unverified":
            updated.append(record)
            continue

        alpha_id = str(record["alpha_id"])
        alpha_detail = module.fetch_alpha(session, alpha_id)
        check = module.check_alpha(session, alpha_id)
        candidate = next(
            item
            for item in module.load_ranked_candidates()
            if item.get("alpha_id") == alpha_id
        )
        refreshed = module.live_record(candidate, alpha_detail, check)
        refreshed["postcheck_classification"] = module.classify_postcheck(selected_alpha_id, refreshed)
        refreshed["recheck_of_previous_unverified"] = True
        updated.append(refreshed)
        print(
            f"{alpha_id} {refreshed['postcheck_classification']['category']} "
            f"{refreshed['live_check'].get('pass_count')}/{refreshed['live_check'].get('check_count')} "
            f"selfcorr={refreshed['live_check'].get('self_correlation')}"
        )
        time.sleep(1)

    payload["post_submit_candidate_checks"] = updated
    payload["summary"] = module.build_summary(updated)
    payload["unverified_recheck_timestamp_utc"] = module.utc_now()
    module.dump_json(module.OUTPUT_JSON, payload)
    module.OUTPUT_MD.write_text(module.render_md(payload), encoding="utf-8")


if __name__ == "__main__":
    main()

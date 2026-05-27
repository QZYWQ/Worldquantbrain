#!/usr/bin/env python3
"""Resume a bounded WorldQuant BRAIN probe batch through logged-in Chrome CDP."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from wqb_probe_batch import (
    ChromeApiSession,
    compact_checks,
    compact_metrics,
    extract_alpha_id,
    merged_settings,
    utc_now,
)


SIMULATION_URL_RE = re.compile(r"https://api\.worldquantbrain\.com/simulations/[A-Za-z0-9]+")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return data


def find_existing(existing: dict[str, Any], name: str) -> dict[str, Any] | None:
    alphas = existing.get("alphas")
    if not isinstance(alphas, list):
        return None
    for item in alphas:
        if isinstance(item, dict) and item.get("name") == name:
            return item
    return None


def extract_simulation_url(record: dict[str, Any] | None) -> str | None:
    if not isinstance(record, dict):
        return None
    location = record.get("submit_location")
    if isinstance(location, str) and location:
        return location
    error = record.get("error")
    if isinstance(error, str):
        match = SIMULATION_URL_RE.search(error)
        if match:
            return match.group(0)
    return None


def failed_checks(record: dict[str, Any]) -> list[str]:
    checks = record.get("checks")
    if not isinstance(checks, list):
        return []
    names: list[str] = []
    for check in checks:
        if isinstance(check, dict) and check.get("result") == "FAIL":
            names.append(str(check.get("name")))
    return names


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resume a WQB probe capture using Chrome CDP.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--existing", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--profile-directory", default="Profile 1")
    parser.add_argument("--max-polls", type=int, default=45)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    batch = load_json(args.input)
    existing = load_json(args.existing) if args.existing.exists() else {}
    candidates = batch.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise SystemExit("input must contain a non-empty candidates array")

    records: list[dict[str, Any]] = []
    with ChromeApiSession(args.profile_directory, True) as session:
        for index, candidate in enumerate(candidates, start=1):
            if not isinstance(candidate, dict):
                continue
            name = str(candidate.get("name") or f"candidate_{index}")
            previous = find_existing(existing, name)
            if previous and previous.get("alpha_id") and isinstance(previous.get("metrics"), dict):
                records.append(previous)
                print(f"[{index}/{len(candidates)}] keep {name} alpha={previous.get('alpha_id')}", flush=True)
                continue

            expression = str(candidate.get("expression") or "").strip()
            settings = merged_settings(candidate)
            record: dict[str, Any] = dict(previous or {})
            record.update(
                {
                    "name": name,
                    "expression": expression,
                    "settings": settings,
                    "source": "chrome_cdp_resume",
                    "submitted_at": record.get("submitted_at") or utc_now(),
                }
            )

            try:
                location = extract_simulation_url(previous)
                if location:
                    print(f"[{index}/{len(candidates)}] poll {name}", flush=True)
                else:
                    print(f"[{index}/{len(candidates)}] submit {name}", flush=True)
                    location = session.submit_simulation(expression, settings)
                record["submit_location"] = location
                simulation = session.wait_for_simulation(location, args.max_polls)
                record["simulation_result"] = simulation
                alpha_id = extract_alpha_id(simulation)
                record["alpha_id"] = alpha_id
                if alpha_id:
                    alpha_detail = session.fetch_alpha_detail(alpha_id)
                    record["alpha_detail"] = alpha_detail
                    record["metrics"] = compact_metrics(alpha_detail)
                    record["checks"] = compact_checks(alpha_detail)
                    record.pop("error", None)
                else:
                    status = simulation.get("status") if isinstance(simulation, dict) else None
                    record["error"] = f"simulation finished without alpha id; status={status}"
            except Exception as exc:  # noqa: BLE001
                record["error"] = str(exc)
            record["completed_at"] = utc_now()
            records.append(record)

            metrics = record.get("metrics") if isinstance(record.get("metrics"), dict) else {}
            print(
                "  alpha={alpha} sharpe={sharpe} fitness={fitness} turnover={turnover} returns={returns} fail={fail}".format(
                    alpha=record.get("alpha_id") or "-",
                    sharpe=metrics.get("sharpe", "-"),
                    fitness=metrics.get("fitness", "-"),
                    turnover=metrics.get("turnover", "-"),
                    returns=metrics.get("returns", "-"),
                    fail=",".join(failed_checks(record)) or "-",
                ),
                flush=True,
            )

            output = {
                "capture_id": batch.get("capture_id") or args.output.stem,
                "topic": batch.get("topic"),
                "source": "official_worldquantbrain_api",
                "auth_mode": "chrome_cdp_resume",
                "captured_at": utc_now(),
                "candidates_source": str(args.input),
                "resumed_from": str(args.existing),
                "alphas": records,
            }
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

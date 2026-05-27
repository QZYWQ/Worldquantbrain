#!/usr/bin/env python3
"""S2 composite rescue for operating profitability.

Simulation only. No /submit call exists in this file.
"""

from __future__ import annotations

import importlib.util
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
S1_PATH = PROJECT_ROOT / "runs/research-queues/2026-05-23-operating-profitability-s1-rescue.py"
OUT_DIR = PROJECT_ROOT / "runs/research-queues/2026-05-23-operating-profitability-s2-composite"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_JSON = OUT_DIR / "results.json"
REPORT_MD = OUT_DIR / "report.md"

spec = importlib.util.spec_from_file_location("s1_rescue", S1_PATH)
s1 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(s1)


OP_ASSETS = "ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252)"
FCF_MAX = "ts_rank(ts_mean(free_cashflow_max,126),252)"
FCF_ACTUAL = "ts_rank(ts_mean(anl4_fs_actuals_advanced_qf_nd_fcf_value,63),252)"

CANDIDATES = [
    {
        "name": "subindustry-op-assets-fcf-max-70-30",
        "expression": f"group_rank(0.7 * {OP_ASSETS} + 0.3 * {FCF_MAX}, subindustry)",
        "decay": 3,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "name": "subindustry-op-assets-fcf-max-50-50",
        "expression": f"group_rank(0.5 * {OP_ASSETS} + 0.5 * {FCF_MAX}, subindustry)",
        "decay": 3,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "name": "subindustry-op-assets-fcf-actual-70-30",
        "expression": f"group_rank(0.7 * {OP_ASSETS} + 0.3 * {FCF_ACTUAL}, subindustry)",
        "decay": 3,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "name": "subindustry-op-assets-fcf-actual-50-50",
        "expression": f"group_rank(0.5 * {OP_ASSETS} + 0.5 * {FCF_ACTUAL}, subindustry)",
        "decay": 3,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "name": "subindustry-op-assets-rank504",
        "expression": "group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),504), subindustry)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
    {
        "name": "subindustry-op-assets-rank126",
        "expression": "group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),126), subindustry)",
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
    },
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_report(payload: dict[str, Any]) -> str:
    ranked = sorted(payload["results"], key=s1.score, reverse=True)
    lines = [
        "# 2026-05-23 Operating Profitability S2 Composite",
        "",
        "- Mode: SIMULATION ONLY. No alpha was submitted.",
        "- Goal: test whether subindustry peer grouping plus cash-flow confirmation lifts Fitness over 1.0.",
        "",
        "| Rank | Alpha | Name | Posture | Score | Sharpe | Fitness | Turnover | SubU | Check | Expression |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for idx, item in enumerate(ranked, 1):
        metrics = item.get("metrics") or {}
        check = item.get("official_check") or {}
        check_text = (
            f"{check.get('pass_count')}/{check.get('check_count')}"
            if check.get("status") == "CHECKED"
            else check.get("status", "not_checked")
        )
        lines.append(
            f"| {idx} | {item.get('alpha_id')} | {item['name']} | {item.get('posture')} | {s1.score(item)} | "
            f"{metrics.get('sharpe')} | {metrics.get('fitness')} | {metrics.get('turnover')} | "
            f"{metrics.get('subUniverseSharpe')} | {check_text} | `{item['expression']}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    session = s1.login()
    payload: dict[str, Any] = {
        "mode": "SIMULATION_ONLY_NO_SUBMIT",
        "started_at_utc": now_utc(),
        "candidates": CANDIDATES,
        "results": [],
    }
    for idx, candidate in enumerate(CANDIDATES, 1):
        print(f"[{idx}/{len(CANDIDATES)}] {candidate['name']}", flush=True)
        location, error = s1.post_simulation(session, candidate)
        if error or not location:
            record = {**candidate, "status": "POST_FAILED", "error": error}
            payload["results"].append(record)
            save_json(RESULTS_JSON, payload)
            continue
        sim = s1.poll(session, location)
        alpha_id = sim.get("alpha")
        record = {**candidate, "simulation_location": location, "simulation": sim, "status": sim.get("status")}
        if alpha_id:
            alpha = s1.fetch_alpha(session, alpha_id)
            record["alpha_id"] = alpha_id
            record["alpha_detail"] = alpha
            record["metrics"] = s1.metric_dict(alpha)
            metrics = record["metrics"]
            print(f"  {alpha_id} S={metrics.get('sharpe')} F={metrics.get('fitness')} TVR={metrics.get('turnover')}", flush=True)
            if (metrics.get("sharpe") or 0) >= 1.25 and (metrics.get("fitness") or 0) >= 1.0 and (metrics.get("turnover") or 0) <= 0.7:
                record["official_check"] = s1.run_check(session, alpha_id)
            else:
                record["official_check"] = {"status": "NOT_CHECKED_METRIC_FILTER"}
            record["posture"] = s1.posture(record)
        payload["results"].append(record)
        payload["updated_at_utc"] = now_utc()
        save_json(RESULTS_JSON, payload)
        REPORT_MD.write_text(render_report(payload), encoding="utf-8")
        time.sleep(2)
    payload["finished_at_utc"] = now_utc()
    save_json(RESULTS_JSON, payload)
    REPORT_MD.write_text(render_report(payload), encoding="utf-8")
    print(f"results={RESULTS_JSON}")
    print(f"report={REPORT_MD}")


if __name__ == "__main__":
    main()

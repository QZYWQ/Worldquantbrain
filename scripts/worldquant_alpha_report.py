#!/usr/bin/env python3
"""Batch WorldQuant BRAIN simulation runner and report formatter.

This script submits a list of alpha expressions, waits for the final result,
and writes a markdown report that is easy to screenshot.

Credentials are read from one of:
- ~/brain_credentials.txt  (JSON dict or list)
- BRAIN_USERNAME / BRAIN_PASSWORD environment variables
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests
from requests.auth import HTTPBasicAuth

API_BASE = "https://api.worldquantbrain.com"
DEFAULT_OUTPUT = Path("~/Downloads/worldquant_alpha_report.md").expanduser()
DEFAULT_ALPHA_FILE = Path("alphas.txt")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "MARKET",
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "ON",
    "language": "FASTEXPR",
    "visualization": False,
}

DEFAULT_ALPHAS: List[str] = [
    "rank(ts_sum(vec_avg(nws12_afterhsz_sl), 60))",
    "rank(ts_av_diff(vec_avg(nws12_afterhsz_sl), 20))",
    "trade_when(rank(ts_sum(vec_sum(scl12_alltype_buzzvec), 20)) > 0.9, rank(ts_sum(vec_avg(nws12_afterhsz_sl), 60)), -1)",
]


def load_credentials() -> tuple[str, str]:
    cred_path = Path.home() / "brain_credentials.txt"
    if cred_path.exists():
        raw = cred_path.read_text(encoding="utf-8").strip()
        if raw:
            data = json.loads(raw)
            if isinstance(data, dict):
                username = data.get("username") or data.get("user")
                password = data.get("password")
                if username and password:
                    return str(username), str(password)
            elif isinstance(data, list) and len(data) >= 2:
                return str(data[0]), str(data[1])

    username = os.environ.get("BRAIN_USERNAME")
    password = os.environ.get("BRAIN_PASSWORD")
    if username and password:
        return username, password

    print("Missing BRAIN credentials.", file=sys.stderr)
    username = input("BRAIN username: ").strip()
    password = getpass.getpass("BRAIN password: ")
    if not username or not password:
        raise SystemExit("Username or password is empty.")
    return username, password


def load_alpha_expressions(path: Optional[Path]) -> List[str]:
    if path is None:
        return list(DEFAULT_ALPHAS)

    if not path.exists():
        raise SystemExit(f"Alpha input file not found: {path}")

    alphas: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        alphas.append(stripped)
    return alphas


def load_settings(path: Optional[Path]) -> Dict[str, Any]:
    if path is None:
        return dict(DEFAULT_SETTINGS)

    if not path.exists():
        raise SystemExit(f"Settings file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Settings file must contain a JSON object.")

    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def authenticate_session(session: requests.Session, username: str, password: str) -> None:
    session.auth = HTTPBasicAuth(username, password)
    resp = session.post(f"{API_BASE}/authentication", timeout=60)
    resp.raise_for_status()


def submit_simulation(session: requests.Session, expression: str, settings: Dict[str, Any]) -> str:
    payload = {
        "type": "REGULAR",
        "settings": settings,
        "regular": expression,
    }
    resp = session.post(f"{API_BASE}/simulations", json=payload, timeout=60)
    resp.raise_for_status()
    location = resp.headers.get("Location")
    if not location:
        raise RuntimeError(f"Missing Location header for expression: {expression}")
    return location


def wait_for_final_result(session: requests.Session, location: str) -> Dict[str, Any]:
    while True:
        resp = session.get(location, timeout=60)
        resp.raise_for_status()
        retry_after = resp.headers.get("Retry-After", "0")
        try:
            retry_after_seconds = float(retry_after)
        except ValueError:
            retry_after_seconds = 0.0

        if retry_after_seconds > 0:
            time.sleep(retry_after_seconds)
            continue

        return resp.json()


def _first_present(data: Any, keys: Iterable[str]) -> Any:
    if not isinstance(data, dict):
        return None
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return None


def extract_alpha_id(result: Dict[str, Any]) -> str:
    alpha_obj = result.get("alpha")
    if isinstance(alpha_obj, dict):
        value = _first_present(alpha_obj, ("id", "alpha_id", "alphaId", "name"))
        if value:
            return str(value)
    elif alpha_obj not in (None, ""):
        return str(alpha_obj)

    value = _first_present(result, ("id", "alpha_id", "alphaId"))
    if value:
        return str(value)
    return "UNKNOWN"


def extract_status(result: Dict[str, Any]) -> str:
    sources: List[Any] = [result, result.get("alpha"), result.get("result"), result.get("performance")]
    for source in sources:
        if isinstance(source, dict):
            value = _first_present(
                source,
                (
                    "status",
                    "state",
                    "submissionStatus",
                    "submission_status",
                ),
            )
            if value:
                return str(value)
    return "UNKNOWN"


def extract_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    candidates: List[Any] = [
        result.get("metrics"),
        result.get("performance"),
        result.get("result"),
        result.get("alpha"),
        result,
    ]
    merged: Dict[str, Any] = {}
    for candidate in candidates:
        if isinstance(candidate, dict):
            merged.update(candidate)
    return merged


def format_metric_value(value: Any) -> str:
    if isinstance(value, float):
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        return text if text else "0"
    return str(value)


def format_metrics(metrics: Dict[str, Any]) -> str:
    preferred_groups = [
        ("Sharpe", ("sharpe", "Sharpe")),
        ("Fitness", ("fitness", "Fitness")),
        ("Turnover", ("turnover", "Turnover")),
        ("Returns", ("returns", "Returns")),
        ("Weight", ("weight", "Weight")),
        ("Sub-universe", ("subuniverse_pass", "subUniversePass", "sub_universe_pass", "Sub-universe")),
        ("Check Submission", ("check_submission", "checkSubmission", "Check Submission")),
        ("Self-correlation", ("self_correlation", "selfCorrelation", "Self-correlation")),
        ("Test Period", ("test_period", "testPeriod", "Test Period")),
    ]

    parts: List[str] = []
    for label, aliases in preferred_groups:
        value = _first_present(metrics, aliases)
        if value is not None:
            parts.append(f"{label}={format_metric_value(value)}")

    if not parts:
        return "Metrics: N/A"
    return "Metrics: " + ", ".join(parts)


def format_result(index: int, location: str, result: Dict[str, Any]) -> str:
    stamp = datetime.now().strftime("%d日 %H:%M:%S")
    alpha_id = extract_alpha_id(result)
    status = extract_status(result)
    metrics = extract_metrics(result)

    lines = [
        f"{index}----- Alpha location get successfully: {location} time: {stamp}",
        f"{index}----- [ALPHA_ID: {alpha_id}] | Status: {status}",
        format_metrics(metrics),
    ]
    return "\n".join(lines)


def build_report(results: List[str]) -> str:
    body = "\n\n".join(results)
    return f"# WorldQuant alpha batch report\n\n```text\n{body}\n```\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and format WorldQuant BRAIN alpha simulations.")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional text file with one alpha expression per line.",
    )
    parser.add_argument(
        "--settings",
        type=Path,
        default=None,
        help="Optional JSON file overriding default simulation settings.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Markdown report path. Defaults to ~/Downloads/worldquant_alpha_report.md.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit on how many expressions to submit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned report without calling the API.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = load_settings(args.settings)

    input_path = args.input
    if input_path is None and DEFAULT_ALPHA_FILE.exists():
        input_path = DEFAULT_ALPHA_FILE

    alphas = load_alpha_expressions(input_path)
    if args.limit and args.limit > 0:
        alphas = alphas[: args.limit]
    if not alphas:
        raise SystemExit("No alpha expressions found.")

    if args.dry_run:
        formatted_results: List[str] = []
        for idx, _expression in enumerate(alphas, start=1):
            formatted_results.append(
                "\n".join(
                    [
                        f"{idx}----- Alpha location get successfully: <dry-run> time: {datetime.now().strftime('%d日 %H:%M:%S')}",
                        f"{idx}----- [ALPHA_ID: <dry-run>] | Status: <dry-run>",
                        "Metrics: Sharpe=<dry-run>, Fitness=<dry-run>, Turnover=<dry-run>",
                    ]
                )
            )
        report = build_report(formatted_results)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(report)
        return 0

    username, password = load_credentials()
    session = requests.Session()
    authenticate_session(session, username, password)

    formatted_results: List[str] = []
    for idx, expression in enumerate(alphas, start=1):
        location = submit_simulation(session, expression, settings)
        result = wait_for_final_result(session, location)
        formatted_results.append(format_result(idx, location, result))
        print(formatted_results[-1])
        print()

    report = build_report(formatted_results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

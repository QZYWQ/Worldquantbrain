#!/usr/bin/env python3
"""Run a small WorldQuant BRAIN probe batch and capture alpha details.

Input JSON:
{
  "capture_id": "...",
  "topic": "...",
  "candidates": [
    {"name": "...", "expression": "...", "settings": {...}}
  ]
}
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from worldquant_forum_crawler import (
    ChromeDevToolsClient,
    ChromeLauncher,
    DEFAULT_BROWSER_BINARY,
    DEFAULT_CHROME_ROOT,
    build_profile_bundle,
)


API_BASE = "https://api.worldquantbrain.com"
DEFAULT_SETTINGS: dict[str, Any] = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "INDUSTRY",
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "OFF",
    "language": "FASTEXPR",
    "visualization": False,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return data


def load_credentials() -> tuple[str, str] | None:
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
            if isinstance(data, list) and len(data) >= 2:
                return str(data[0]), str(data[1])

    username = os.environ.get("BRAIN_USERNAME") or os.environ.get("WQ_USERNAME")
    password = os.environ.get("BRAIN_PASSWORD") or os.environ.get("WQ_PASSWORD")
    if username and password:
        return username, password
    return None


def load_json_env(name: str) -> dict[str, str]:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit(f"{name} must be a JSON object")
    return {str(key): str(value) for key, value in data.items() if value is not None}


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    auth_headers = load_json_env("BRAIN_AUTH_HEADERS")
    if auth_headers:
        session.headers.update(auth_headers)

    cookie = os.environ.get("BRAIN_SESSION_COOKIE", "").strip()
    if cookie.lower().startswith("cookie:"):
        cookie = cookie.split(":", 1)[1].strip()
    if cookie:
        session.headers["Cookie"] = cookie

    if auth_headers or cookie:
        return session

    credentials = load_credentials()
    if credentials is None:
        username = input("BRAIN username: ").strip()
        password = getpass.getpass("BRAIN password: ")
        credentials = (username, password)
    username, password = credentials
    response = session.post(f"{API_BASE}/authentication", timeout=60, auth=HTTPBasicAuth(username, password))
    response.raise_for_status()
    return session


def merged_settings(candidate: dict[str, Any]) -> dict[str, Any]:
    settings = dict(DEFAULT_SETTINGS)
    overrides = candidate.get("settings")
    if isinstance(overrides, dict):
        settings.update(overrides)
    return settings


def submit_simulation(session: requests.Session, expression: str, settings: dict[str, Any]) -> str:
    payload = {"type": "REGULAR", "settings": settings, "regular": expression}
    response = session.post(f"{API_BASE}/simulations", json=payload, timeout=60)
    response.raise_for_status()
    location = response.headers.get("Location")
    if not location:
        raise RuntimeError("simulation response did not include a Location header")
    return location


def wait_for_simulation(session: requests.Session, location: str, max_polls: int) -> dict[str, Any]:
    for _ in range(max_polls):
        try:
            response = session.get(location, timeout=60)
        except requests.exceptions.ReadTimeout:
            time.sleep(20)
            continue
        response.raise_for_status()
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                delay = float(retry_after)
            except ValueError:
                delay = 0.0
            if delay > 0:
                time.sleep(delay)
                continue
        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("simulation response was not a JSON object")
        status = str(payload.get("status") or "").upper()
        if status in {"COMPLETE", "ERROR", "WARNING"}:
            return payload
        time.sleep(20)
    raise TimeoutError(f"simulation did not finish after {max_polls} polls: {location}")


def extract_alpha_id(simulation: dict[str, Any]) -> str | None:
    alpha = simulation.get("alpha")
    if isinstance(alpha, str) and alpha:
        return alpha
    if isinstance(alpha, dict):
        value = alpha.get("id") or alpha.get("alpha_id") or alpha.get("alphaId")
        if value:
            return str(value)
    return None


def fetch_alpha_detail(session: requests.Session, alpha_id: str) -> dict[str, Any]:
    response = session.get(f"{API_BASE}/alphas/{alpha_id}", timeout=60)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"alpha detail was not an object for {alpha_id}")
    return payload


class ChromeApiSession:
    def __init__(self, profile_directory: str | None, refresh_profile_copy: bool) -> None:
        self.profile_bundle = build_profile_bundle(
            profile_root=DEFAULT_CHROME_ROOT,
            profile_directory=profile_directory,
            cache_parent=Path("/private/tmp/worldquant-brain-cdp-profile"),
            refresh_profile_copy=refresh_profile_copy,
        )
        self.launcher = ChromeLauncher(
            browser_binary=DEFAULT_BROWSER_BINARY,
            profile_bundle=self.profile_bundle,
            headless=False,
        )
        self.client: ChromeDevToolsClient | None = None
        self.session_id: str | None = None

    def __enter__(self) -> "ChromeApiSession":
        self.launcher.launch()
        if self.launcher.port is None or self.launcher.ws_path is None:
            raise RuntimeError("Chrome did not expose a DevTools endpoint")
        self.client = ChromeDevToolsClient("127.0.0.1", self.launcher.port, self.launcher.ws_path)
        target = self.client.send("Target.createTarget", {"url": f"{API_BASE}/"})
        session = self.client.send("Target.attachToTarget", {"targetId": target["targetId"], "flatten": True})
        self.session_id = session["sessionId"]
        self.client.send("Runtime.enable", session_id=self.session_id)
        self.client.send("Page.enable", session_id=self.session_id)
        self.client.send("Page.navigate", {"url": f"{API_BASE}/"}, session_id=self.session_id)
        time.sleep(3)
        return self

    def __exit__(self, *_exc: object) -> None:
        if self.client is not None:
            self.client.close()
        self.launcher.stop()

    def fetch_json(self, url: str, *, method: str = "GET", body: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.client is None or self.session_id is None:
            raise RuntimeError("Chrome API session is not active")
        js = f"""
        (async () => {{
          const response = await fetch({json.dumps(url)}, {{
            method: {json.dumps(method)},
            credentials: 'include',
            headers: {{'Accept': 'application/json', 'Content-Type': 'application/json'}},
            body: {json.dumps(json.dumps(body)) if body is not None else "undefined"}
          }});
          const text = await response.text();
          let parsed = null;
          try {{ parsed = text ? JSON.parse(text) : null; }} catch (error) {{}}
          return {{
            status: response.status,
            ok: response.ok,
            headers: Object.fromEntries(response.headers.entries()),
            text,
            json: parsed
          }};
        }})()
        """
        result = self.client.send(
            "Runtime.evaluate",
            {"expression": js, "returnByValue": True, "awaitPromise": True},
            session_id=self.session_id,
        )
        value = result.get("result", {}).get("value")
        if not isinstance(value, dict):
            raise RuntimeError(f"Chrome fetch returned unexpected value for {url}")
        if int(value.get("status") or 0) >= 400:
            preview = str(value.get("text") or "")[:300]
            raise RuntimeError(f"Chrome fetch failed status={value.get('status')} url={url} body={preview}")
        return value

    def submit_simulation(self, expression: str, settings: dict[str, Any]) -> str:
        response = self.fetch_json(
            f"{API_BASE}/simulations",
            method="POST",
            body={"type": "REGULAR", "settings": settings, "regular": expression},
        )
        headers = response.get("headers")
        location = None
        if isinstance(headers, dict):
            location = headers.get("location") or headers.get("Location")
        if not location:
            payload = response.get("json")
            if isinstance(payload, dict):
                value = payload.get("id") or payload.get("simulation_id") or payload.get("simulationId")
                if value:
                    location = f"{API_BASE}/simulations/{value}"
        if not location:
            raise RuntimeError("Chrome simulation response did not include a Location header")
        return str(location)

    def wait_for_simulation(self, location: str, max_polls: int) -> dict[str, Any]:
        for _ in range(max_polls):
            response = self.fetch_json(location)
            headers = response.get("headers")
            retry_after = headers.get("retry-after") if isinstance(headers, dict) else None
            if retry_after:
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = 0.0
                if delay > 0:
                    time.sleep(delay)
                    continue
            payload = response.get("json")
            if not isinstance(payload, dict):
                raise RuntimeError("Chrome simulation poll returned non-object JSON")
            status = str(payload.get("status") or "").upper()
            if status in {"COMPLETE", "ERROR", "WARNING"}:
                return payload
            time.sleep(20)
        raise TimeoutError(f"simulation did not finish after {max_polls} polls: {location}")

    def fetch_alpha_detail(self, alpha_id: str) -> dict[str, Any]:
        response = self.fetch_json(f"{API_BASE}/alphas/{alpha_id}")
        payload = response.get("json")
        if not isinstance(payload, dict):
            raise RuntimeError(f"Chrome alpha detail returned non-object JSON for {alpha_id}")
        return payload


def compact_metrics(alpha_detail: dict[str, Any]) -> dict[str, Any]:
    is_block = alpha_detail.get("is")
    if not isinstance(is_block, dict):
        return {}
    return {
        "sharpe": is_block.get("sharpe"),
        "fitness": is_block.get("fitness"),
        "turnover": is_block.get("turnover"),
        "returns": is_block.get("returns"),
        "drawdown": is_block.get("drawdown"),
        "margin": is_block.get("margin"),
        "longCount": is_block.get("longCount"),
        "shortCount": is_block.get("shortCount"),
    }


def compact_checks(alpha_detail: dict[str, Any]) -> list[dict[str, Any]]:
    is_block = alpha_detail.get("is")
    if not isinstance(is_block, dict):
        return []
    checks = is_block.get("checks")
    return checks if isinstance(checks, list) else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded WorldQuant BRAIN probe batch.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-polls", type=int, default=30)
    parser.add_argument("--auth-mode", choices=["requests", "chrome"], default="requests")
    parser.add_argument("--profile-directory", default=None)
    parser.add_argument("--refresh-profile-copy", action="store_true")
    return parser.parse_args()


def run_candidates(
    *,
    candidates: list[Any],
    session: requests.Session | None,
    chrome_session: ChromeApiSession | None,
    max_polls: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            continue
        name = str(candidate.get("name") or f"candidate_{index}")
        expression = str(candidate.get("expression") or "").strip()
        if not expression:
            raise SystemExit(f"{name} is missing expression")
        settings = merged_settings(candidate)
        print(f"[{index}/{len(candidates)}] submit {name}", flush=True)

        record: dict[str, Any] = {
            "name": name,
            "expression": expression,
            "settings": settings,
            "source": "new_simulation",
            "submitted_at": utc_now(),
        }
        try:
            if chrome_session is not None:
                location = chrome_session.submit_simulation(expression, settings)
            elif session is not None:
                location = submit_simulation(session, expression, settings)
            else:
                raise RuntimeError("no API session available")
            record["submit_location"] = location
            if chrome_session is not None:
                simulation = chrome_session.wait_for_simulation(location, max_polls)
            elif session is not None:
                simulation = wait_for_simulation(session, location, max_polls)
            alpha_id = extract_alpha_id(simulation)
            record["simulation_result"] = simulation
            record["alpha_id"] = alpha_id
            if alpha_id:
                alpha_detail = (
                    chrome_session.fetch_alpha_detail(alpha_id)
                    if chrome_session is not None
                    else fetch_alpha_detail(session, alpha_id)  # type: ignore[arg-type]
                )
                record["alpha_detail"] = alpha_detail
                record["metrics"] = compact_metrics(alpha_detail)
                record["checks"] = compact_checks(alpha_detail)
            else:
                record["error"] = "simulation completed without alpha id"
        except Exception as exc:
            record["error"] = str(exc)
        record["completed_at"] = utc_now()
        records.append(record)

        metrics = record.get("metrics") if isinstance(record.get("metrics"), dict) else {}
        failed = [
            check.get("name")
            for check in record.get("checks", [])
            if isinstance(check, dict) and check.get("result") == "FAIL"
        ]
        print(
            f"  alpha={record.get('alpha_id')} sharpe={metrics.get('sharpe')} "
            f"fitness={metrics.get('fitness')} turnover={metrics.get('turnover')} "
            f"returns={metrics.get('returns')} fail={','.join(str(item) for item in failed) or '-'}",
            flush=True,
        )

    return records


def main() -> int:
    args = parse_args()
    batch = load_json_object(args.input)
    candidates = batch.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise SystemExit("input must contain a non-empty candidates array")

    if args.auth_mode == "chrome":
        with ChromeApiSession(args.profile_directory, args.refresh_profile_copy) as chrome_session:
            records = run_candidates(
                candidates=candidates,
                session=None,
                chrome_session=chrome_session,
                max_polls=args.max_polls,
            )
    else:
        session = build_session()
        records = run_candidates(
            candidates=candidates,
            session=session,
            chrome_session=None,
            max_polls=args.max_polls,
        )

    output = {
        "capture_id": batch.get("capture_id") or args.output.stem,
        "topic": batch.get("topic"),
        "source": "official_worldquantbrain_api",
        "auth_mode": args.auth_mode,
        "captured_at": utc_now(),
        "candidates_source": str(args.input),
        "alphas": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

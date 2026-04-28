#!/usr/bin/env python3
"""Lightweight durable task queue for the Worldquantbrain control repo.

The runner stores only JSON/JSONL files under runs/tasks. It does not call
worldquant-miner, read credentials, or run WQ simulations.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


STATUSES = ("queued", "claimed", "running", "done", "failed", "expired")
ACTIVE_STATUSES = {"claimed", "running", "expired"}
DEFAULT_CLAIMED_BY = "codex"
DEFAULT_LEASE_MINUTES = 90
SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(credential|password|secret|token|api[_-]?key)\b\s*[:=]\s*[^,\s]+"
)
SENSITIVE_WORD_RE = re.compile(
    r"(?i)\b(credential|password|secret|token|api[_-]?key)\b"
)


def default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_local() -> datetime:
    return datetime.now().astimezone()


def isoformat(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def max_timestamp() -> datetime:
    return datetime.max.replace(tzinfo=now_local().tzinfo)


def scrub_text(value: Any) -> Any:
    if value is None:
        return None
    text = str(value)
    text = SENSITIVE_ASSIGNMENT_RE.sub("<redacted-sensitive-field>", text)
    return SENSITIVE_WORD_RE.sub("<redacted-sensitive-label>", text)


class TaskStore:
    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        self.tasks_dir = self.root / "runs" / "tasks"
        self.queue_path = self.tasks_dir / "queue.jsonl"
        self.active_dir = self.tasks_dir / "active"
        self.done_dir = self.tasks_dir / "done"
        self.failed_dir = self.tasks_dir / "failed"
        self.locks_dir = self.tasks_dir / "locks"
        self.logs_dir = self.tasks_dir / "logs"
        self.state_path = self.tasks_dir / "task_state.json"

    def init(self) -> None:
        for path in (
            self.tasks_dir,
            self.active_dir,
            self.done_dir,
            self.failed_dir,
            self.locks_dir,
            self.logs_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)
        if not self.queue_path.exists():
            self.atomic_write_text(self.queue_path, "")
        self.update_state()

    def atomic_write_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(text)
            os.replace(tmp_name, path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def write_json(self, path: Path, payload: dict[str, Any]) -> None:
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        self.atomic_write_text(path, text)

    def read_json_file(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object in {path}")
        return payload

    def read_queue(self) -> list[dict[str, Any]]:
        if not self.queue_path.exists():
            return []
        tasks: list[dict[str, Any]] = []
        with self.queue_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSONL in {self.queue_path}:{line_number}: {exc}"
                    ) from exc
                if not isinstance(payload, dict):
                    raise ValueError(
                        f"Expected JSON object in {self.queue_path}:{line_number}"
                    )
                tasks.append(payload)
        return tasks

    def write_queue(self, tasks: list[dict[str, Any]]) -> None:
        lines = [json.dumps(task, ensure_ascii=False) for task in tasks]
        text = "\n".join(lines)
        if text:
            text += "\n"
        self.atomic_write_text(self.queue_path, text)

    def append_log(
        self, task: dict[str, Any], event: str, details: dict[str, Any] | None = None
    ) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        record: dict[str, Any] = {
            "timestamp": isoformat(now_local()),
            "event": event,
            "task_id": task.get("id"),
            "type": task.get("type"),
            "status": task.get("status"),
        }
        if details:
            for key, value in details.items():
                if key in {"summary", "error", "reason"}:
                    record[key] = scrub_text(value)
                else:
                    record[key] = value
        log_path = self.logs_dir / f"{task['id']}.log"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def lock_path(self, task_id: str) -> Path:
        return self.locks_dir / f"{task_id}.lock.json"

    def active_path(self, task_id: str) -> Path:
        return self.active_dir / f"{task_id}.json"

    def done_path(self, task_id: str) -> Path:
        return self.done_dir / f"{task_id}.json"

    def failed_path(self, task_id: str) -> Path:
        return self.failed_dir / f"{task_id}.json"

    def load_json_tasks(self, directory: Path) -> list[dict[str, Any]]:
        if not directory.exists():
            return []
        tasks: list[dict[str, Any]] = []
        for path in sorted(directory.glob("*.json")):
            tasks.append(self.read_json_file(path))
        return tasks

    def all_tasks(self) -> list[dict[str, Any]]:
        by_id: dict[str, dict[str, Any]] = {}
        for task in self.read_queue():
            by_id[task["id"]] = task
        for directory in (self.active_dir, self.done_dir, self.failed_dir):
            for task in self.load_json_tasks(directory):
                by_id[task["id"]] = task
        return list(by_id.values())

    def read_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {}
        return self.read_json_file(self.state_path)

    def update_state(
        self,
        *,
        last_claimed_task: str | None = None,
        last_completed_task: str | None = None,
    ) -> dict[str, Any]:
        previous = self.read_state()
        counts = {status: 0 for status in STATUSES}
        for task in self.all_tasks():
            status = task.get("status", "queued")
            counts.setdefault(status, 0)
            counts[status] += 1

        state = {
            "updated_at": isoformat(now_local()),
            "counts": counts,
            "last_claimed_task": (
                last_claimed_task
                if last_claimed_task is not None
                else previous.get("last_claimed_task")
            ),
            "last_completed_task": (
                last_completed_task
                if last_completed_task is not None
                else previous.get("last_completed_task")
            ),
        }
        self.write_json(self.state_path, state)
        return state

    def active_task(self, task_id: str) -> tuple[dict[str, Any], Path] | None:
        path = self.active_path(task_id)
        if path.exists():
            return self.read_json_file(path), path
        return None

    def remove_from_queue(self, task_id: str) -> dict[str, Any] | None:
        queue = self.read_queue()
        removed: dict[str, Any] | None = None
        remaining: list[dict[str, Any]] = []
        for task in queue:
            if task.get("id") == task_id and removed is None:
                removed = task
            else:
                remaining.append(task)
        if removed is not None:
            self.write_queue(remaining)
        return removed

    def locate_task(self, task_id: str) -> tuple[dict[str, Any], str, Path | None]:
        queued = self.remove_from_queue(task_id)
        if queued is not None:
            return queued, "queue", None

        for source, path in (
            ("active", self.active_path(task_id)),
            ("done", self.done_path(task_id)),
            ("failed", self.failed_path(task_id)),
        ):
            if path.exists():
                return self.read_json_file(path), source, path

        raise KeyError(f"Task not found: {task_id}")

    def expire_active_tasks(self) -> list[str]:
        expired: list[str] = []
        now = now_local()
        for task in self.load_json_tasks(self.active_dir):
            if task.get("status") not in {"claimed", "running"}:
                continue
            lease_expires_at = parse_timestamp(task.get("lease_expires_at"))
            if lease_expires_at is None or lease_expires_at >= now:
                continue

            task["status"] = "expired"
            task["updated_at"] = isoformat(now)
            self.write_json(self.active_path(task["id"]), task)
            lock_path = self.lock_path(task["id"])
            if lock_path.exists():
                lock = self.read_json_file(lock_path)
                lock["released_at"] = isoformat(now)
                lock["release_reason"] = "expired"
                self.write_json(lock_path, lock)
            self.append_log(task, "expired")
            expired.append(task["id"])
        return expired


def load_external_json(path: Path) -> dict[str, Any]:
    with path.expanduser().open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def sanitize_id_part(value: str | None, fallback: str) -> str:
    if not value:
        return fallback
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return cleaned[:32] or fallback


def make_task_id(store: TaskStore, task_type: str, parent: str | None) -> str:
    today = now_local().strftime("%Y%m%d")
    type_part = sanitize_id_part(task_type, "task")
    parent_part = sanitize_id_part(parent, "root")
    sequence = len(
        [
            task
            for task in store.all_tasks()
            if str(task.get("id", "")).startswith(f"task_{today}_{type_part}_")
        ]
    ) + 1
    token = uuid.uuid4().hex[:8]
    return f"task_{today}_{type_part}_{parent_part}_{token}_{sequence:03d}"


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected true/false, got: {value}")


def build_budget(args: argparse.Namespace, embedded: dict[str, Any]) -> dict[str, Any]:
    budget = {
        "max_simulations": 0,
        "max_runtime_minutes": 0,
        "allow_real_wq": False,
    }
    budget.update(embedded)
    if args.max_simulations is not None:
        budget["max_simulations"] = args.max_simulations
    if args.max_runtime_minutes is not None:
        budget["max_runtime_minutes"] = args.max_runtime_minutes
    if args.allow_real_wq is not None:
        budget["allow_real_wq"] = args.allow_real_wq
    return budget


def public_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": task.get("id"),
        "type": task.get("type"),
        "status": task.get("status"),
        "priority": task.get("priority"),
        "parent": task.get("parent"),
        "attempts": task.get("attempts"),
        "claimed_by": task.get("claimed_by"),
        "claimed_at": task.get("claimed_at"),
        "lease_expires_at": task.get("lease_expires_at"),
        "completed_at": task.get("completed_at"),
        "failed_at": task.get("failed_at"),
        "summary": scrub_text(task.get("summary")),
        "error": scrub_text(task.get("error")),
    }


def cmd_init(args: argparse.Namespace) -> int:
    store = TaskStore(args.root)
    store.init()
    print(f"Initialized task store at {store.tasks_dir}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    store = TaskStore(args.root)
    store.init()

    embedded: dict[str, Any] = {}
    if args.payload_file:
        embedded = load_external_json(args.payload_file)
    if args.payload_json:
        embedded = json.loads(args.payload_json)
        if not isinstance(embedded, dict):
            raise ValueError("--payload-json must be a JSON object")

    payload = embedded.get("payload", embedded)
    if not isinstance(payload, dict):
        raise ValueError("Task payload must be a JSON object")

    parent = args.parent if args.parent is not None else embedded.get("parent")
    budget = build_budget(args, embedded.get("budget", {}))
    task_id = make_task_id(store, args.type, parent)
    timestamp = isoformat(now_local())
    task = {
        "id": task_id,
        "type": args.type,
        "status": "queued",
        "priority": args.priority,
        "created_at": timestamp,
        "updated_at": timestamp,
        "parent": parent,
        "budget": budget,
        "payload": payload,
        "attempts": 0,
        "claimed_by": None,
        "claimed_at": None,
        "lease_expires_at": None,
        "completed_at": None,
        "failed_at": None,
        "summary": None,
        "error": None,
    }

    queue = store.read_queue()
    queue.append(task)
    store.write_queue(queue)
    store.append_log(task, "created")
    store.update_state()
    print(json.dumps({"created": task_id, "status": "queued"}, ensure_ascii=False))
    return 0


def sort_tasks_for_claim(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        tasks,
        key=lambda task: (
            -int(task.get("priority", 0)),
            parse_timestamp(task.get("created_at")) or max_timestamp(),
            str(task.get("id", "")),
        ),
    )


def cmd_claim_next(args: argparse.Namespace) -> int:
    store = TaskStore(args.root)
    store.init()
    expired = store.expire_active_tasks()

    queue = [task for task in store.read_queue() if task.get("status") == "queued"]
    if not queue:
        store.update_state()
        print(
            json.dumps(
                {
                    "claimed": None,
                    "expired": expired,
                    "message": "No queued tasks available.",
                },
                ensure_ascii=False,
            )
        )
        return 0

    task = sort_tasks_for_claim(queue)[0]
    remaining = [candidate for candidate in queue if candidate["id"] != task["id"]]
    store.write_queue(remaining)

    now = now_local()
    lease_expires_at = now + timedelta(minutes=args.lease_minutes)
    task["status"] = "claimed"
    task["claimed_by"] = args.claimed_by
    task["claimed_at"] = isoformat(now)
    task["lease_expires_at"] = isoformat(lease_expires_at)
    task["updated_at"] = isoformat(now)
    task["attempts"] = int(task.get("attempts", 0)) + 1
    task["completed_at"] = None
    task["failed_at"] = None
    task["summary"] = None
    task["error"] = None

    store.write_json(store.active_path(task["id"]), task)
    lock = {
        "task_id": task["id"],
        "claimed_by": args.claimed_by,
        "claimed_at": task["claimed_at"],
        "lease_minutes": args.lease_minutes,
        "heartbeat_at": task["claimed_at"],
        "lease_expires_at": task["lease_expires_at"],
    }
    store.write_json(store.lock_path(task["id"]), lock)
    store.append_log(task, "claimed", {"lease_expires_at": task["lease_expires_at"]})
    store.update_state(last_claimed_task=task["id"])

    print(
        json.dumps(
            {
                "claimed": public_task(task),
                "expired": expired,
                "lock": str(store.lock_path(task["id"]).relative_to(store.root)),
            },
            ensure_ascii=False,
        )
    )
    return 0


def cmd_heartbeat(args: argparse.Namespace) -> int:
    store = TaskStore(args.root)
    store.init()
    active = store.active_task(args.task_id)
    if active is None:
        raise KeyError(f"Active task not found: {args.task_id}")

    task, _ = active
    if task.get("status") not in {"claimed", "running"}:
        raise ValueError(
            f"Task {args.task_id} is not heartbeatable, status={task.get('status')}"
        )

    now = now_local()
    lease_expires_at = now + timedelta(minutes=args.lease_minutes)
    task["status"] = "running"
    task["updated_at"] = isoformat(now)
    task["lease_expires_at"] = isoformat(lease_expires_at)
    store.write_json(store.active_path(args.task_id), task)

    lock_path = store.lock_path(args.task_id)
    lock = store.read_json_file(lock_path) if lock_path.exists() else {}
    lock.update(
        {
            "task_id": args.task_id,
            "claimed_by": task.get("claimed_by") or args.claimed_by,
            "claimed_at": task.get("claimed_at"),
            "lease_minutes": args.lease_minutes,
            "heartbeat_at": isoformat(now),
            "lease_expires_at": task["lease_expires_at"],
        }
    )
    store.write_json(lock_path, lock)
    store.append_log(task, "heartbeat", {"lease_expires_at": task["lease_expires_at"]})
    store.update_state()
    print(json.dumps({"heartbeat": public_task(task)}, ensure_ascii=False))
    return 0


def release_lock(store: TaskStore, task_id: str) -> None:
    lock_path = store.lock_path(task_id)
    if lock_path.exists():
        lock_path.unlink()


def cmd_complete(args: argparse.Namespace) -> int:
    store = TaskStore(args.root)
    store.init()
    task, source, path = store.locate_task(args.task_id)
    if source == "done":
        print(json.dumps({"completed": public_task(task)}, ensure_ascii=False))
        return 0
    if source == "failed":
        raise ValueError(f"Task {args.task_id} is already failed")

    now = isoformat(now_local())
    task["status"] = "done"
    task["updated_at"] = now
    task["completed_at"] = now
    task["failed_at"] = None
    task["summary"] = scrub_text(args.summary)
    task["error"] = None

    if path is not None and path.exists():
        path.unlink()
    store.write_json(store.done_path(args.task_id), task)
    release_lock(store, args.task_id)
    store.append_log(task, "completed", {"summary": args.summary})
    store.update_state(last_completed_task=args.task_id)
    print(json.dumps({"completed": public_task(task)}, ensure_ascii=False))
    return 0


def cmd_fail(args: argparse.Namespace) -> int:
    store = TaskStore(args.root)
    store.init()
    task, source, path = store.locate_task(args.task_id)
    if source == "failed":
        print(json.dumps({"failed": public_task(task)}, ensure_ascii=False))
        return 0
    if source == "done":
        raise ValueError(f"Task {args.task_id} is already done")

    now = isoformat(now_local())
    task["status"] = "failed"
    task["updated_at"] = now
    task["failed_at"] = now
    task["completed_at"] = None
    task["summary"] = None
    task["error"] = scrub_text(args.reason)

    if path is not None and path.exists():
        path.unlink()
    store.write_json(store.failed_path(args.task_id), task)
    release_lock(store, args.task_id)
    store.append_log(task, "failed", {"reason": args.reason})
    store.update_state()
    print(json.dumps({"failed": public_task(task)}, ensure_ascii=False))
    return 0


def format_table(tasks: list[dict[str, Any]]) -> str:
    if not tasks:
        return "No tasks."
    rows = [
        [
            task.get("id", ""),
            task.get("status", ""),
            task.get("type", ""),
            str(task.get("priority", "")),
            str(task.get("parent") or ""),
            str(task.get("attempts", "")),
            str(task.get("claimed_by") or ""),
            str(task.get("lease_expires_at") or ""),
        ]
        for task in tasks
    ]
    headers = [
        "id",
        "status",
        "type",
        "priority",
        "parent",
        "attempts",
        "claimed_by",
        "lease_expires_at",
    ]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    lines = [
        "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        "  ".join("-" * width for width in widths),
    ]
    for row in rows:
        lines.append(
            "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        )
    return "\n".join(lines)


def cmd_list(args: argparse.Namespace) -> int:
    store = TaskStore(args.root)
    store.init()
    tasks = store.all_tasks()
    if args.status:
        tasks = [task for task in tasks if task.get("status") == args.status]
    tasks = sorted(
        tasks,
        key=lambda task: (
            task.get("status", ""),
            -int(task.get("priority", 0)),
            parse_timestamp(task.get("created_at")) or max_timestamp(),
            str(task.get("id", "")),
        ),
    )
    if args.json:
        print(json.dumps([public_task(task) for task in tasks], indent=2))
    else:
        print(format_table(tasks))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    store = TaskStore(args.root)
    store.init()
    state = store.update_state()
    lock_count = len(list(store.locks_dir.glob("*.lock.json")))
    payload = {
        **state,
        "task_root": str(store.tasks_dir),
        "active_locks": lock_count,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage lightweight Worldquantbrain tasks."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root(),
        help="Worldquantbrain root. Defaults to the parent of tools/.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create task directories/state.")
    init_parser.set_defaults(func=cmd_init)

    add_parser = subparsers.add_parser("add", help="Add a queued task.")
    add_parser.add_argument("--type", required=True, help="Task type.")
    add_parser.add_argument("--priority", type=int, default=50, help="Task priority.")
    add_parser.add_argument("--parent", default=None, help="Optional parent id.")
    add_parser.add_argument(
        "--payload-file", type=Path, default=None, help="JSON payload or task spec."
    )
    add_parser.add_argument(
        "--payload-json", default=None, help="Inline JSON payload or task spec."
    )
    add_parser.add_argument("--max-simulations", type=int, default=None)
    add_parser.add_argument("--max-runtime-minutes", type=int, default=None)
    add_parser.add_argument("--allow-real-wq", type=parse_bool, default=None)
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="List known tasks.")
    list_parser.add_argument("--status", choices=STATUSES, default=None)
    list_parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    list_parser.set_defaults(func=cmd_list)

    claim_parser = subparsers.add_parser("claim-next", help="Claim the next task.")
    claim_parser.add_argument("--claimed-by", default=DEFAULT_CLAIMED_BY)
    claim_parser.add_argument(
        "--lease-minutes", type=int, default=DEFAULT_LEASE_MINUTES
    )
    claim_parser.set_defaults(func=cmd_claim_next)

    heartbeat_parser = subparsers.add_parser("heartbeat", help="Refresh a task lease.")
    heartbeat_parser.add_argument("--task-id", required=True)
    heartbeat_parser.add_argument("--claimed-by", default=DEFAULT_CLAIMED_BY)
    heartbeat_parser.add_argument(
        "--lease-minutes", type=int, default=DEFAULT_LEASE_MINUTES
    )
    heartbeat_parser.set_defaults(func=cmd_heartbeat)

    complete_parser = subparsers.add_parser("complete", help="Complete a task.")
    complete_parser.add_argument("--task-id", required=True)
    complete_parser.add_argument("--summary", required=True)
    complete_parser.set_defaults(func=cmd_complete)

    fail_parser = subparsers.add_parser("fail", help="Fail a task.")
    fail_parser.add_argument("--task-id", required=True)
    fail_parser.add_argument("--reason", required=True)
    fail_parser.set_defaults(func=cmd_fail)

    status_parser = subparsers.add_parser("status", help="Print task state summary.")
    status_parser.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"task_runner error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

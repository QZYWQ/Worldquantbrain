#!/usr/bin/env python3
"""Import the latest worldquant-miner batch into this research repository.

The importer is intentionally read-only toward the miner repository. It copies
batch artifacts into dated run folders and records only file metadata in logs so
credential-like content is never printed by this tool.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEDGER_TAIL_ROWS = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import the latest worldquant-miner batch into Worldquantbrain."
    )
    parser.add_argument(
        "--miner-root",
        required=True,
        type=Path,
        help="Path to the worldquant-miner repository.",
    )
    parser.add_argument(
        "--brain-root",
        default=Path.cwd(),
        type=Path,
        help="Path to this research repository. Defaults to the current directory.",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_metadata(path: Path, root: Path | None = None) -> dict[str, Any]:
    stat = path.stat()
    display_path = path
    if root is not None:
        try:
            display_path = path.relative_to(root)
        except ValueError:
            display_path = path
    return {
        "path": str(display_path),
        "size_bytes": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "sha256": sha256_file(path),
    }


def latest_batch(results_dir: Path) -> Path:
    if not results_dir.is_dir():
        raise FileNotFoundError(f"Missing miner results directory: {results_dir}")

    batch_files = [path for path in results_dir.glob("batch_*.json") if path.is_file()]
    if not batch_files:
        raise FileNotFoundError(f"No batch_*.json files found under: {results_dir}")

    return max(batch_files, key=lambda path: (path.stat().st_mtime_ns, path.name))


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path

    for index in range(2, 1000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate

    raise RuntimeError(f"Unable to find a unique artifact path for: {path}")


def copy_file(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    final_dest = unique_path(dest)
    shutil.copy2(src, final_dest)
    return final_dest


def read_ledger_tail(ledger_path: Path) -> tuple[list[list[str]], int]:
    if not ledger_path.is_file():
        raise FileNotFoundError(f"Missing miner ledger: {ledger_path}")

    with ledger_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return [], 0

        tail_rows: deque[list[str]] = deque(maxlen=LEDGER_TAIL_ROWS)
        for row in reader:
            tail_rows.append(row)

    return [header, *tail_rows], len(tail_rows)


def write_ledger_tail(src: Path, dest: Path) -> tuple[Path, int]:
    rows, tail_count = read_ledger_tail(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    final_dest = unique_path(dest)
    with final_dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return final_dest, tail_count


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    final_path = unique_path(path)
    with final_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return final_path


def append_daily_note(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# {manifest['date']} Daily Note\n\n", encoding="utf-8")

    artifacts = manifest["artifacts"]
    fingerprints = artifacts.get("fingerprints_snapshot")
    fingerprints_line = (
        f"- Fingerprints snapshot: `{fingerprints['path']}`"
        if fingerprints
        else "- Fingerprints snapshot: not present in miner root"
    )

    # This note intentionally records artifact paths and hashes, not file bodies.
    entry = "\n".join(
        [
            f"## Miner Import {manifest['local_time']}",
            "",
            f"- Source batch: `{manifest['source']['latest_batch']['path']}`",
            f"- Candidate batch copy: `{artifacts['candidate_batch']['path']}`",
            f"- Ledger tail snapshot: `{artifacts['ledger_tail_snapshot']['path']}`",
            f"- Ledger tail rows captured: {manifest['ledger_tail_rows']}",
            fingerprints_line,
            f"- Manifest: `{artifacts['manifest']['path']}`",
            "",
        ]
    )

    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def relative_metadata(path: Path, root: Path) -> dict[str, Any]:
    return file_metadata(path, root=root)


def main() -> int:
    args = parse_args()
    miner_root = args.miner_root.expanduser().resolve()
    brain_root = args.brain_root.expanduser().resolve()

    if not miner_root.is_dir():
        raise NotADirectoryError(f"Miner root is not a directory: {miner_root}")
    if not brain_root.is_dir():
        raise NotADirectoryError(f"Brain root is not a directory: {brain_root}")

    now = datetime.now().astimezone()
    date_str = now.date().isoformat()
    stamp = now.strftime("%H%M%S")

    candidate_dir = brain_root / "runs" / "candidate-batches" / date_str
    capture_dir = brain_root / "runs" / "simulation-captures" / date_str
    daily_note = brain_root / "runs" / "notes" / "daily" / f"{date_str}.md"

    batch_src = latest_batch(miner_root / "results")
    ledger_src = miner_root / "ledger.csv"
    fingerprints_src = miner_root / "fingerprints.json"

    batch_dest = copy_file(batch_src, candidate_dir / f"{stamp}_{batch_src.name}")
    ledger_dest, ledger_tail_rows = write_ledger_tail(
        ledger_src,
        capture_dir / f"{stamp}_ledger_last10.csv",
    )

    fingerprints_dest: Path | None = None
    if fingerprints_src.is_file():
        fingerprints_dest = copy_file(
            fingerprints_src,
            capture_dir / f"{stamp}_fingerprints.json",
        )

    manifest: dict[str, Any] = {
        "imported_at": now.isoformat(),
        "date": date_str,
        "local_time": now.strftime("%H:%M:%S %Z"),
        "miner_root": str(miner_root),
        "brain_root": str(brain_root),
        "source": {
            "latest_batch": file_metadata(batch_src, root=miner_root),
            "ledger": file_metadata(ledger_src, root=miner_root),
            "fingerprints": (
                file_metadata(fingerprints_src, root=miner_root)
                if fingerprints_src.is_file()
                else None
            ),
        },
        "ledger_tail_rows": ledger_tail_rows,
        "artifacts": {
            "candidate_batch": relative_metadata(batch_dest, root=brain_root),
            "ledger_tail_snapshot": relative_metadata(ledger_dest, root=brain_root),
            "fingerprints_snapshot": (
                relative_metadata(fingerprints_dest, root=brain_root)
                if fingerprints_dest is not None
                else None
            ),
        },
    }

    manifest_path = write_json(capture_dir / f"{stamp}_manifest.json", manifest)
    manifest["artifacts"]["manifest"] = {
        "path": str(manifest_path.relative_to(brain_root))
    }
    # Rewrite once after the manifest path is known.
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    append_daily_note(daily_note, manifest)

    print(f"Imported miner batch: {batch_src.name}")
    print(f"Candidate batch: {batch_dest.relative_to(brain_root)}")
    print(f"Ledger tail snapshot: {ledger_dest.relative_to(brain_root)}")
    if fingerprints_dest is not None:
        print(f"Fingerprints snapshot: {fingerprints_dest.relative_to(brain_root)}")
    else:
        print("Fingerprints snapshot: skipped (not found)")
    print(f"Manifest: {manifest_path.relative_to(brain_root)}")
    print(f"Daily note: {daily_note.relative_to(brain_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

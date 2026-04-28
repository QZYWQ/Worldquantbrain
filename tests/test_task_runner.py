import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_RUNNER = REPO_ROOT / "tools" / "task_runner.py"


class TaskRunnerCliTest(unittest.TestCase):
    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TASK_RUNNER), "--root", str(root), *args],
            check=True,
            text=True,
            capture_output=True,
        )

    def add_task(self, root: Path) -> str:
        payload_path = root / "payload.json"
        payload_path.write_text(
            json.dumps(
                {
                    "parent": "demo",
                    "budget": {
                        "max_simulations": 0,
                        "max_runtime_minutes": 1,
                        "allow_real_wq": False,
                    },
                    "payload": {"goal": "smoke", "variants": []},
                }
            ),
            encoding="utf-8",
        )
        result = self.run_cli(
            root,
            "add",
            "--type",
            "smoke",
            "--priority",
            "10",
            "--payload-file",
            str(payload_path),
        )
        return json.loads(result.stdout)["created"]

    def test_init_add_claim_heartbeat_complete_and_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            self.run_cli(root, "init")
            for relative in (
                "runs/tasks/active",
                "runs/tasks/done",
                "runs/tasks/failed",
                "runs/tasks/locks",
                "runs/tasks/logs",
            ):
                self.assertTrue((root / relative).is_dir())

            complete_id = self.add_task(root)
            list_output = self.run_cli(root, "list").stdout
            self.assertIn(complete_id, list_output)

            claim = json.loads(self.run_cli(root, "claim-next").stdout)
            self.assertEqual(complete_id, claim["claimed"]["id"])
            self.assertTrue(
                (root / "runs" / "tasks" / "locks" / f"{complete_id}.lock.json").is_file()
            )

            heartbeat = json.loads(
                self.run_cli(root, "heartbeat", "--task-id", complete_id).stdout
            )
            self.assertEqual("running", heartbeat["heartbeat"]["status"])

            self.run_cli(
                root,
                "complete",
                "--task-id",
                complete_id,
                "--summary",
                "smoke complete",
            )
            self.assertTrue((root / "runs" / "tasks" / "done" / f"{complete_id}.json").is_file())
            self.assertFalse(
                (root / "runs" / "tasks" / "locks" / f"{complete_id}.lock.json").exists()
            )

            fail_id = self.add_task(root)
            self.run_cli(root, "claim-next")
            self.run_cli(root, "fail", "--task-id", fail_id, "--reason", "smoke fail")
            self.assertTrue((root / "runs" / "tasks" / "failed" / f"{fail_id}.json").is_file())


if __name__ == "__main__":
    unittest.main()

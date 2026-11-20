"""Behavioral tests for the verify-skill-app order CLI."""

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OrderCliTests(unittest.TestCase):
    def invoke(self, db_path: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "src.orders", "--db", str(db_path), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_create_is_idempotent_and_rejects_item_mismatch(self):
        with TemporaryDirectory() as tmp:
            db = Path(tmp) / "orders.json"
            first = self.invoke(db, "create", "--id", "A1", "--item", "notebook")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue(json.loads(first.stdout)["created"])

            replay = self.invoke(db, "create", "--id", "A1", "--item", "notebook")
            self.assertEqual(replay.returncode, 0, replay.stderr)
            self.assertFalse(json.loads(replay.stdout)["created"])

            conflict = self.invoke(db, "create", "--id", "A1", "--item", "pen")
            self.assertEqual(conflict.returncode, 1)

    def test_cancel_transitions_open_to_cancelled_idempotently(self):
        with TemporaryDirectory() as tmp:
            db = Path(tmp) / "orders.json"
            self.assertEqual(self.invoke(db, "create", "--id", "B1", "--item", "lamp").returncode, 0)
            first = self.invoke(db, "cancel", "--id", "B1")
            self.assertEqual(first.returncode, 0, first.stderr)
            first_data = json.loads(first.stdout)
            self.assertTrue(first_data["changed"])
            self.assertEqual(first_data["record"]["status"], "cancelled")

            replay = self.invoke(db, "cancel", "--id", "B1")
            self.assertEqual(replay.returncode, 0, replay.stderr)
            self.assertFalse(json.loads(replay.stdout)["changed"])


if __name__ == "__main__":
    unittest.main()

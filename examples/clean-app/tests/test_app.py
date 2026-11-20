import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.api import OrderService
from src.ui import cli


class CleanAppTests(unittest.TestCase):
    def test_idempotent_export_transitions_once(self):
        service = OrderService()
        csv_1, changed_1 = service.export_csv("b1")
        csv_2, changed_2 = service.export_csv("b1")
        self.assertEqual(changed_1, 2)
        self.assertEqual(changed_2, 0)
        self.assertEqual(csv_1, csv_2)
        self.assertIn("ord-101,2500,exported", csv_1)

    def test_cli_export_entrypoint(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["export", "--batch", "b2"])
        self.assertEqual(code, 0)
        self.assertIn("changed=2", buf.getvalue())


if __name__ == "__main__":
    unittest.main()

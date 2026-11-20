import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app import run_sample
from src.legacy.parser import parse_legacy_line


class LegacyParserTests(unittest.TestCase):
    def test_parse_legacy_line(self):
        self.assertEqual(parse_legacy_line('"inv-01", "1200"'), ["inv-01", "1200"])

    def test_run_sample(self):
        result = run_sample()
        self.assertEqual(result["rows"], 2)


if __name__ == "__main__":
    unittest.main()

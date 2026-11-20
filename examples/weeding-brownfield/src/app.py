"""Entrypoint for the brownfield billing parser."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.legacy.parser import parse_legacy_line


def run_sample() -> dict:
    sample_lines = ['"inv-01", "1200"', '"inv-02", "800"']
    parsed = [parse_legacy_line(line) for line in sample_lines]
    return {"rows": len(parsed), "items": parsed}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    print(json.dumps(run_sample(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

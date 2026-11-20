"""User-facing CLI entrypoint; imports only src.core.api."""

import argparse
import json
import sys

from src.core.api import OrderService


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean app order export CLI")
    parser.add_argument("command", choices=("export", "summary"))
    parser.add_argument("--batch", default="2026-11-20")
    args = parser.parse_args(argv)

    service = OrderService()
    if args.command == "export":
        csv_text, changed = service.export_csv(args.batch)
        print(csv_text)
        print(f"changed={changed}")
        return 0
    print(json.dumps(service.summary(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

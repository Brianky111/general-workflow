"""Minimal order CLI and store demonstrating a sharded verify-<app> skill."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class OrderError(ValueError):
    """Domain validation or invalid state transition error."""


class OrderStore:
    """File-backed order state machine with idempotent create and cancel operations."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.db_path.is_file():
            return {}
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def _save(self, records: dict[str, dict[str, str]]) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def create(self, order_id: str, item: str) -> tuple[dict[str, str], bool]:
        if not order_id.strip() or not item.strip():
            raise OrderError("order_id and item must be non-empty")
        records = self._load()
        existing = records.get(order_id)
        if existing is not None:
            if existing["item"] != item:
                raise OrderError(f"order {order_id} already exists with different item")
            return existing, False
        record = {"order_id": order_id, "item": item, "status": "open"}
        records[order_id] = record
        self._save(records)
        return record, True

    def cancel(self, order_id: str) -> tuple[dict[str, str], bool]:
        records = self._load()
        record = records.get(order_id)
        if record is None:
            raise OrderError(f"order {order_id} not found")
        if record["status"] == "cancelled":
            return record, False
        record["status"] = "cancelled"
        self._save(records)
        return record, True

    def get(self, order_id: str) -> dict[str, str] | None:
        return self._load().get(order_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Order CLI")
    parser.add_argument("--db", required=True, help="path to JSON store file")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--id", required=True)
    p_create.add_argument("--item", required=True)

    p_cancel = sub.add_parser("cancel")
    p_cancel.add_argument("--id", required=True)

    p_show = sub.add_parser("show")
    p_show.add_argument("--id", required=True)

    args = parser.parse_args(argv)
    store = OrderStore(Path(args.db))
    try:
        if args.cmd == "create":
            rec, created = store.create(args.id, args.item)
            print(json.dumps({"record": rec, "created": created}, ensure_ascii=False))
        elif args.cmd == "cancel":
            rec, changed = store.cancel(args.id)
            print(json.dumps({"record": rec, "changed": changed}, ensure_ascii=False))
        elif args.cmd == "show":
            rec = store.get(args.id)
            if rec is None:
                print(json.dumps({"error": f"order {args.id} not found"}))
                return 1
            print(json.dumps({"record": rec}, ensure_ascii=False))
    except OrderError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

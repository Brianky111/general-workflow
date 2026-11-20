"""Reusable verification driver for verify-skill-app."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_cli(db_path: Path, *cli_args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "src.orders", "--db", str(db_path), *cli_args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    payload = proc.stdout.strip() or proc.stderr.strip() or "{}"
    return proc.returncode, json.loads(payload)


def run_doctor() -> int:
    if not (ROOT / "src" / "orders.py").is_file():
        print("doctor: FAIL missing src/orders.py", file=sys.stderr)
        return 1
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "src.orders", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        print(f"doctor: FAIL {proc.stderr}", file=sys.stderr)
        return 1
    print("doctor: OK python+orders CLI ready")
    return 0


def run_create(out_dir: Path) -> Path:
    with tempfile.TemporaryDirectory(prefix="verify-orders-create-") as tmp:
        db = Path(tmp) / "orders.json"
        c1, out1 = run_cli(db, "create", "--id", "ORD-101", "--item", "keyboard")
        c2, out2 = run_cli(db, "create", "--id", "ORD-101", "--item", "keyboard")
        c3, view = run_cli(db, "show", "--id", "ORD-101")
        assert c1 == 0 and out1["created"] is True
        assert c2 == 0 and out2["created"] is False
        assert c3 == 0 and view["record"]["status"] == "open"
    artifact = out_dir / "create-order.txt"
    artifact.write_text(
        f"first={json.dumps(out1)}\nreplay={json.dumps(out2)}\nshow={json.dumps(view)}\n",
        encoding="utf-8",
    )
    return artifact


def run_cancel(out_dir: Path) -> Path:
    with tempfile.TemporaryDirectory(prefix="verify-orders-cancel-") as tmp:
        db = Path(tmp) / "orders.json"
        c0, _ = run_cli(db, "create", "--id", "ORD-102", "--item", "mouse")
        c1, out1 = run_cli(db, "cancel", "--id", "ORD-102")
        c2, out2 = run_cli(db, "cancel", "--id", "ORD-102")
        c3, view = run_cli(db, "show", "--id", "ORD-102")
        assert c0 == 0
        assert c1 == 0 and out1["changed"] is True and out1["record"]["status"] == "cancelled"
        assert c2 == 0 and out2["changed"] is False
        assert c3 == 0 and view["record"]["status"] == "cancelled"
    artifact = out_dir / "cancel-order.txt"
    artifact.write_text(
        f"cancel={json.dumps(out1)}\nreplay={json.dumps(out2)}\nshow={json.dumps(view)}\n",
        encoding="utf-8",
    )
    return artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Drive and verify verify-skill-app")
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=("doctor", "create", "cancel", "all"),
    )
    args = parser.parse_args(argv)
    if args.target == "doctor":
        return run_doctor()
    if run_doctor() != 0:
        return 1
    out_dir = ROOT / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.target in ("all", "create"):
        run_create(out_dir)
    if args.target in ("all", "cancel"):
        run_cancel(out_dir)
    print(f"artifacts written under {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

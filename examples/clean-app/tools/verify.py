"""Reusable verification CLI that invokes the real entrypoint and writes artifacts."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.api import OrderService


def run_export_check(out_dir: Path) -> Path:
    service = OrderService()
    first_csv, first_changed = service.export_csv("batch-verify")
    second_csv, second_changed = service.export_csv("batch-verify")
    assert first_csv == second_csv and first_changed == 2 and second_changed == 0
    target = out_dir / "export-csv.txt"
    target.write_text(
        f"{first_csv}\nfirst_changed={first_changed}\nreplay_changed={second_changed}\n",
        encoding="utf-8",
    )
    return target


def run_state_chart(out_dir: Path) -> Path:
    target = out_dir / "state-chart.md"
    target.write_text(
        "\n".join([
            "# Order Export State Chart",
            "",
            "```mermaid",
            "stateDiagram-v2",
            "    [*] --> draft",
            "    draft --> exported: export_csv(batch_key)",
            "    exported --> exported: replay same batch_key (changed=0)",
            "```",
            "",
        ]),
        encoding="utf-8",
    )
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify clean-app user paths")
    parser.add_argument("target", nargs="?", default="all", choices=("all", "export", "state-chart"))
    args = parser.parse_args(argv)
    out_dir = ROOT / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.target in ("all", "export"):
        run_export_check(out_dir)
    if args.target in ("all", "state-chart"):
        run_state_chart(out_dir)
    print(f"artifacts written under {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Report and check the sharded workflow state of a project using this workflow.

Run this inside a target project, not inside the skill repository:

    python workflow_status.py [--root PATH] [--json]

It answers the two questions the prose gates cannot answer on their own -- who
is working on what, and how much of the current scope is still owed -- and it
fails with a non-zero exit code when the state contradicts itself. That exit
code is the point: every other gate in this workflow is prose an agent judges
itself against, and self-assessment is not a gate.

Expected layout (see references/99-state-and-handoff.md):

    docs/workflow/
      project.md          lifecycle, tier, path, sources, decisions
      backlog.md          which slice owns each A-ID, or unclaimed/deferred/dropped
      slices/S-01.md      owner, claimed, stage, acceptance status, evidence
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

STATE_DIR = Path("docs") / "workflow"
# Horizontal whitespace only: \s would match the newline and let an empty value
# swallow the following line.
FIELD = re.compile(r"(?m)^-[^\S\n]*([a-z_]+):[^\S\n]*(.*)$")
UNSET = {"", "-", "none", "n/a", "tbd"}
TERMINAL = {"deferred", "dropped"}
IN_FLIGHT = "in-slice"
DELIVERED = "delivered"


@dataclass
class Slice:
    id: str
    owner: str = ""
    claimed: str = ""
    stage: str = ""
    write_scope: list[str] = field(default_factory=list)
    acceptance: list[tuple[str, str, str]] = field(default_factory=list)


def table_rows(text: str, section: str | None = None) -> list[list[str]]:
    """Return the data rows of a markdown table, minus header and separator."""
    if section is not None:
        match = re.search(rf"(?ms)^##\s+{re.escape(section)}\s*\n(.*?)(?=^## |\Z)", text)
        if not match:
            return []
        text = match.group(1)

    rows: list[list[str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or all(set(cell) <= {"-", ":"} for cell in cells if cell):
            continue
        rows.append(cells)
    return rows[1:] if rows else rows


def fields_of(text: str) -> dict[str, str]:
    return {name: value.strip() for name, value in FIELD.findall(text)}


def is_set(value: str) -> bool:
    return value.strip().lower() not in UNSET


def normalize(path: str) -> str:
    return path.strip().replace("\\", "/").rstrip("/")


def overlaps(a: str, b: str) -> bool:
    """Two write scopes collide when one contains the other."""
    a, b = normalize(a), normalize(b)
    if not a or not b:
        return False
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def load_slices(root: Path, errors: list[str]) -> list[Slice]:
    slices: list[Slice] = []
    for path in sorted((root / STATE_DIR / "slices").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        values = fields_of(text)
        item = Slice(
            id=path.stem,
            owner=values.get("owner", ""),
            claimed=values.get("claimed", ""),
            stage=values.get("stage", ""),
            write_scope=[p for p in re.split(r"[,;]| {2,}", values.get("write_scope", "")) if p.strip()],
        )
        for row in table_rows(text, "Acceptance"):
            if len(row) >= 3:
                item.acceptance.append((row[0], row[1].lower(), row[2]))
            else:
                errors.append(f"{path.name}: acceptance row has fewer than 3 columns: {row}")
        slices.append(item)
    return slices


def check(root: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    state = root / STATE_DIR

    project = fields_of((state / "project.md").read_text(encoding="utf-8"))
    backlog: dict[str, tuple[str, str]] = {}
    for row in table_rows((state / "backlog.md").read_text(encoding="utf-8")):
        if len(row) < 2:
            errors.append(f"backlog.md: row has fewer than 2 columns: {row}")
            continue
        aid, assignment, note = row[0], row[1], (row[2] if len(row) > 2 else "")
        if aid in backlog:
            errors.append(f"backlog.md: {aid} listed twice")
        backlog[aid] = (assignment, note)

    slices = load_slices(root, errors)
    by_id = {item.id: item for item in slices}

    # A slice claimed by nobody, or claimed without a date, cannot be handed over.
    for item in slices:
        if is_set(item.owner) != is_set(item.claimed):
            errors.append(f"{item.id}: owner and claimed must be set together")

    seen: dict[str, str] = {}
    for item in slices:
        for aid, status, evidence in item.acceptance:
            if aid in seen:
                errors.append(f"{aid} appears in both {seen[aid]} and {item.id}")
            seen[aid] = item.id
            if aid not in backlog:
                errors.append(f"{item.id}: {aid} is not listed in backlog.md")
            elif backlog[aid][0] != item.id:
                errors.append(
                    f"{aid}: backlog assigns it to '{backlog[aid][0]}' but it lives in {item.id}"
                )
            if status == DELIVERED and not is_set(evidence):
                errors.append(f"{item.id}: {aid} is delivered with no evidence pointer")
            if status not in {DELIVERED, IN_FLIGHT}:
                errors.append(f"{item.id}: {aid} has status '{status}'; expected in-slice or delivered")

    for aid, (assignment, note) in backlog.items():
        if assignment in TERMINAL:
            if not is_set(note):
                errors.append(f"backlog.md: {aid} is {assignment} without a change record")
        elif is_set(assignment):
            if assignment not in by_id:
                errors.append(f"backlog.md: {aid} points at unknown slice '{assignment}'")
            elif aid not in {row[0] for row in by_id[assignment].acceptance}:
                errors.append(f"backlog.md: {aid} claims {assignment}, which does not list it")

    # Two live slices writing the same paths collide in code, not just on paper.
    live = [item for item in slices if any(s == IN_FLIGHT for _, s, _ in item.acceptance)]
    for i, one in enumerate(live):
        for other in live[i + 1:]:
            for a in one.write_scope:
                for b in other.write_scope:
                    if overlaps(a, b):
                        errors.append(
                            f"write_scope overlap: {one.id} ({a.strip()}) and {other.id} ({b.strip()})"
                        )

    unclaimed = sorted(aid for aid, (assign, _) in backlog.items() if not is_set(assign))
    in_flight = sorted(aid for item in slices for aid, s, _ in item.acceptance if s == IN_FLIGHT)
    delivered = sorted(aid for item in slices for aid, s, _ in item.acceptance if s == DELIVERED)
    terminal = sorted(aid for aid, (assign, _) in backlog.items() if assign in TERMINAL)

    report = {
        "lifecycle": project.get("lifecycle", "?"),
        "tier": project.get("tier", "?"),
        "path": project.get("path", "?"),
        "slices": [
            {
                "id": item.id,
                "owner": item.owner or "unclaimed",
                "stage": item.stage,
                "delivered": [a for a, s, _ in item.acceptance if s == DELIVERED],
                "in_slice": [a for a, s, _ in item.acceptance if s == IN_FLIGHT],
            }
            for item in slices
        ],
        "unclaimed": unclaimed,
        "in_flight": in_flight,
        "delivered": delivered,
        "deferred_or_dropped": terminal,
        "scope_complete": not unclaimed and not in_flight,
        "errors": errors,
    }
    return report, errors


def render(report: dict) -> None:
    print(f"lifecycle {report['lifecycle']} | tier {report['tier']} | path {report['path']}")
    for item in report["slices"]:
        done, live = len(item["delivered"]), len(item["in_slice"])
        print(f"  {item['id']}  owner={item['owner']}  stage={item['stage']}  "
              f"delivered={done} in-slice={live}")
    if report["unclaimed"]:
        print(f"  unclaimed: {', '.join(report['unclaimed'])}")
    if report["deferred_or_dropped"]:
        print(f"  deferred/dropped: {', '.join(report['deferred_or_dropped'])}")
    owed = len(report["unclaimed"]) + len(report["in_flight"])
    print("scope complete: no remaining, no in-slice" if report["scope_complete"]
          else f"still owed: {owed} acceptance ids")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="project root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state = root / STATE_DIR
    missing = [name for name in ("project.md", "backlog.md") if not (state / name).is_file()]
    if missing:
        # Not an error: the router builds this at the end of the first round.
        print(f"no workflow state at {state} (missing {', '.join(missing)})")
        print("derive the stage per 00-progress-router.md and create it this round")
        return 0

    report, errors = check(root)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        render(report)
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

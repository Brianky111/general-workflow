#!/usr/bin/env python3
"""Report and check the sharded workflow state of a project using this workflow.

Use the script from the installed skill and explicitly select the target project:

    python /path/to/general-workflow/scripts/workflow_status.py --root PATH [--json]

Check ownership, write conflicts, evidence pointers, and coverage of the
authoritative acceptance table. Scope completion is not release or task
completion; the delivery target and actual evidence still govern closeout.

Expected layout (see references/99-state-and-handoff.md):

    docs/workflow/
      project.md          lifecycle, tier, path, sources, decisions
      backlog.md          which slice owns each A-ID, or unclaimed/deferred/dropped
      slices/S-01.md      owner, claimed, stage, acceptance status, evidence
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path, PureWindowsPath

STATE_DIR = Path("docs") / "workflow"
# Horizontal whitespace only: \s would match the newline and let an empty value
# swallow the following line.
FIELD = re.compile(r"(?m)^-[^\S\n]*([a-z_]+):[^\S\n]*(.*)$")
UNSET = {"", "-", "none", "n/a", "tbd"}
TERMINAL = {"deferred", "dropped"}
IN_FLIGHT = "in-slice"
DELIVERED = "delivered"
A_ID = re.compile(r"A-[A-Za-z0-9][A-Za-z0-9._-]*")


@dataclass
class Slice:
    id: str
    owner: str = ""
    claimed: str = ""
    stage: str = ""
    write_scope: list[str] = field(default_factory=list)
    acceptance: list[tuple[str, str, str]] = field(default_factory=list)


def table_rows(text: str, section: str | None = None) -> list[list[str]]:
    """Read A-ID tables in an optional exact heading, ignoring fenced examples."""
    lines: list[str] = []
    fence = ""
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = ""
            continue
        if marker:
            fence = marker[1]
            continue
        lines.append(line)

    if section is not None:
        headings = [
            (i, len(match[1]), match[2].strip().rstrip("#").strip())
            for i, line in enumerate(lines)
            if (match := re.match(r"^(#{1,6})\s+(.+)$", line))
        ]
        selected = [(i, depth) for i, depth, title in headings if title == section]
        if len(selected) != 1:
            return []
        start, depth = selected[0]
        end = next((i for i, level, _ in headings if i > start and level <= depth), len(lines))
        lines = lines[start + 1:end]

    rows: list[list[str]] = []
    active = False
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            active = False
            continue
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip("|"))]
        if cells[0].strip("`") == "A-ID":
            active = True
            continue
        if not cells or all(set(cell) <= {"-", ":"} for cell in cells if cell):
            continue
        if active:
            cells[0] = cells[0].strip("`")
            rows.append(cells)
    return rows


def fields_of(text: str) -> dict[str, str]:
    return {name: value.strip() for name, value in FIELD.findall(text)}


def is_set(value: str) -> bool:
    value = value.strip()
    return value.lower() not in UNSET and not (value.startswith("<") and value.endswith(">"))


def normalize(root: Path, path: str) -> Path:
    """Resolve literal project-relative paths, including existing symlinks."""
    path = path.strip().replace("\\", "/")
    if not is_set(path) or any(char in path for char in "*?[]"):
        raise ValueError("expected a literal project-relative path (no globs)")
    if Path(path).is_absolute() or PureWindowsPath(path).drive:
        raise ValueError("expected a project-relative path")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("path escapes the project root")
    return Path(os.path.normcase(str(resolved)))


def overlaps(a: Path, b: Path) -> bool:
    """Two write scopes collide when one contains the other."""
    return a == b or a in b.parents or b in a.parents


def acceptance_ids(root: Path, pointer: str, errors: list[str]) -> set[str] | None:
    """Load the approved source itself; do not derive expected IDs from backlog."""
    filename, separator, section = pointer.partition("#")
    try:
        source = normalize(root, filename)
        if source.is_relative_to((root / STATE_DIR).resolve()):
            raise ValueError("must reference acceptance outside docs/workflow/")
        text = source.read_text(encoding="utf-8-sig")
    except (OSError, ValueError) as exc:
        errors.append(f"acceptance_source: {exc}")
        return None
    rows = table_rows(text, section if separator else None)
    if not rows:
        errors.append("acceptance_source: expected a nonempty A-ID table in the selected source/heading")
        return None
    ids: set[str] = set()
    valid = True
    for row in rows:
        aid = row[0]
        if not A_ID.fullmatch(aid) or aid in ids:
            errors.append(f"acceptance_source: invalid or duplicate A-ID '{aid}'")
            valid = False
        ids.add(aid)
    return ids if valid else None


def load_slices(root: Path, errors: list[str]) -> list[Slice]:
    slices: list[Slice] = []
    for path in sorted((root / STATE_DIR / "slices").glob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        values = fields_of(text)
        item = Slice(
            id=path.stem,
            owner=values.get("owner", ""),
            claimed=values.get("claimed", ""),
            stage=values.get("stage", ""),
            write_scope=[p.strip() for p in re.split(r"[,;]", values.get("write_scope", "")) if p.strip()],
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

    project = fields_of((state / "project.md").read_text(encoding="utf-8-sig"))
    backlog: dict[str, tuple[str, str]] = {}
    for row in table_rows((state / "backlog.md").read_text(encoding="utf-8-sig")):
        if len(row) < 2:
            errors.append(f"backlog.md: row has fewer than 2 columns: {row}")
            continue
        aid, assignment, note = row[0], row[1], (row[2] if len(row) > 2 else "")
        if aid in backlog:
            errors.append(f"backlog.md: {aid} listed twice")
        backlog[aid] = (assignment, note)

    slices = load_slices(root, errors)
    by_id = {item.id: item for item in slices}

    pointer = project.get("acceptance_source", "")
    expected = acceptance_ids(root, pointer, errors) if is_set(pointer) else None
    if not is_set(pointer) and (backlog or slices or project.get("lifecycle") not in {"IDEA", "DEFINED"}):
        errors.append("project.md: acceptance_source is required before tracking or completing scope")
    if expected is not None:
        for aid in sorted(expected - backlog.keys()):
            errors.append(f"backlog.md: missing authoritative A-ID {aid}")
        for aid in sorted(backlog.keys() - expected):
            errors.append(f"backlog.md: {aid} is not in acceptance_source")
    scope_verified = expected is not None and set(backlog) == expected

    live = [item for item in slices if any(s == IN_FLIGHT for _, s, _ in item.acceptance)]
    owners: dict[str, str] = {}
    scopes: dict[str, list[Path]] = {}
    for item in slices:
        if is_set(item.owner) != is_set(item.claimed):
            errors.append(f"{item.id}: owner and claimed must be set together")
    for item in live:
        if not is_set(item.owner):
            errors.append(f"{item.id}: live slice requires an owner")
        else:
            owner = item.owner.casefold()
            if owner in owners:
                errors.append(f"owner '{item.owner}' holds two live slices: {owners[owner]} and {item.id}")
            owners[owner] = item.id
        try:
            claimed_date = item.claimed.split(" / ", 1)[0]
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", claimed_date):
                raise ValueError("expected YYYY-MM-DD")
            date.fromisoformat(claimed_date)
        except ValueError:
            errors.append(f"{item.id}: live slice requires a valid claimed date (YYYY-MM-DD)")
        scopes[item.id] = []
        if not item.write_scope:
            errors.append(f"{item.id}: live slice requires write_scope")
        for scope in item.write_scope:
            try:
                scopes[item.id].append(normalize(root, scope))
            except (OSError, ValueError) as exc:
                errors.append(f"{item.id}: invalid write_scope '{scope}': {exc}")

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
    for i, one in enumerate(live):
        for other in live[i + 1:]:
            for a in scopes[one.id]:
                for b in scopes[other.id]:
                    if overlaps(a, b):
                        errors.append(
                            f"write_scope overlap: {one.id} ({a}) and {other.id} ({b})"
                        )

    unclaimed = sorted(aid for aid, (assign, _) in backlog.items() if not is_set(assign))
    in_flight = sorted(aid for item in slices for aid, s, _ in item.acceptance if s == IN_FLIGHT)
    delivered = sorted(aid for item in slices for aid, s, _ in item.acceptance if s == DELIVERED)
    terminal = sorted(aid for aid, (assign, _) in backlog.items() if assign in TERMINAL)

    report = {
        "state_status": "invalid" if errors else "ready",
        "lifecycle": project.get("lifecycle", "?"),
        "tier": project.get("tier", "?"),
        "path": project.get("path", "?"),
        "delivery_target": project.get("delivery_target", "?"),
        "acceptance_source": pointer,
        "scope_verified": scope_verified,
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
        "scope_complete": scope_verified and not errors and not unclaimed and not in_flight,
        "errors": errors,
    }
    return report, errors


def render(report: dict) -> None:
    if report["state_status"] == "uninitialized":
        print("no workflow state; derive the stage per 00-progress-router.md and create it this round")
        return
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
    if report["errors"] or not report["scope_verified"]:
        print("scope completion unavailable: fix errors or define the authoritative acceptance scope")
    elif report["scope_complete"]:
        print("scope complete; verify the delivery target and evidence before task closeout")
    else:
        print(f"still owed: {owed} acceptance ids")
    print(f"delivery target: {report['delivery_target']}")


def incomplete_report(status: str, errors: list[str]) -> dict:
    return {
        "state_status": status, "lifecycle": "?", "tier": "?", "path": "?",
        "delivery_target": "?", "acceptance_source": "", "scope_verified": False,
        "slices": [], "unclaimed": [], "in_flight": [], "delivered": [],
        "deferred_or_dropped": [], "scope_complete": False, "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="project root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state = root / STATE_DIR
    missing = [name for name in ("project.md", "backlog.md") if not (state / name).is_file()]
    if missing:
        # An absent directory is a new project; partial state is a broken gate.
        errors = [f"missing workflow state file: {name}" for name in missing] if state.exists() else []
        report = incomplete_report("invalid" if errors else "uninitialized", errors)
    else:
        try:
            report, errors = check(root)
        except (OSError, ValueError) as exc:
            errors = [f"cannot read workflow state: {exc}"]
            report = incomplete_report("invalid", errors)
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

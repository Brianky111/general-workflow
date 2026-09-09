#!/usr/bin/env python3
"""Report and check the sharded workflow state of a project using this workflow.

Use the script from the installed skill and explicitly select the target project:

    python /path/to/general-workflow/scripts/workflow_status.py --root PATH [--json]

Check ownership, write conflicts, evidence pointers, and coverage of the
authoritative acceptance table. Scope completion is not release or task
completion; the delivery target and actual evidence still govern closeout.

State written before this layout lives in one file: docs/workflow-state.md, or
WORKFLOW-STATE.md at the root. When there is no docs/workflow/ but one of those
is present, the report is state_status "legacy" with the files listed in
legacy_state, and the exit code stays 0 -- nothing is broken, the file just has
to be split per references/99-state-and-handoff.md before any gate here means
anything. "legacy" is deliberately a fourth value rather than "uninitialized":
that is the reading that makes the next agent build an empty state beside a full
ledger. "uninitialized", "invalid" and "ready" keep their meanings, and
legacy_state is [] in the "uninitialized" and "ready" reports; an "invalid"
one still lists an old file found beside a half-built docs/workflow/.

Expected layout (see references/99-state-and-handoff.md):

    docs/workflow/
      project.md          state_version, lifecycle, tier, path, next_action, sources
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
# Where state lived before the shards. Its presence is the difference between a
# project that has nothing and a project whose whole ledger is in the other file.
LEGACY_STATE = (Path("docs") / "workflow-state.md", Path("WORKFLOW-STATE.md"))
# Horizontal whitespace only: \s would match the newline and let an empty value
# swallow the following line.
FIELD = re.compile(r"(?m)^-[^\S\n]*([a-z_]+):[^\S\n]*(.*)$")
# Empty-value markers in both languages the templates are written in. A value
# that only says "nothing here yet" must not satisfy a gate that wants evidence.
UNSET = {
    "", "-", "--", "—", "–", "?", "none", "na", "n/a", "tbd", "todo", "pending",
    "无", "暂无", "待补", "待定", "未定", "未知",
}
# Words that name no place. UNSET answers a different question -- "has this field
# been filled in at all" -- so widening it here would make '- owner: later' read
# as an empty owner and skip every check that only runs on a filled field.
# The list is open-ended by nature: it can only reject the vague words someone
# has already been caught writing. '@ 回头再说吧' is the same empty promise and
# passes, because no table enumerates a language. It buys back the cheap cases
# and nothing more -- the real check is a human reading the row.
PLACEHOLDER_REF = UNSET | {
    "later", "soon", "asap", "someday", "x", "xx", "xxx", "wip", "tbc",
    "todos", "uncommitted", "unpushed", "unknown",
    "以后", "之后", "稍后", "回头", "过后", "后补", "再说", "以后再说",
    "待补充", "待补全", "回头补", "之后补", "稍后补", "后面补", "补上",
    "见下", "见上", "见下文", "同上", "未提交", "未推送", "最新提交",
}
# next_action must name the next executable action. These only say that the work
# continues, which the file already said by not being finished.
NO_ACTION = PLACEHOLDER_REF | {
    "继续", "继续做", "继续推进", "继续实现", "下一步", "下一步继续", "推进",
    "往下走", "接着做", "看情况", "视情况", "边做边看",
    "continue", "next", "next step", "keep going", "carry on", "proceed",
    "move on", "in progress", "ongoing",
}
TERMINAL = {"deferred", "dropped"}
IN_FLIGHT = "in-slice"
DELIVERED = "delivered"
A_ID = re.compile(r"A-[A-Za-z0-9][A-Za-z0-9._-]*")
# The shape this script knows how to read. A file written for an older layout is
# not half-valid; it has to be migrated before any gate below means anything.
STATE_VERSION = "2"
# The three fields ship as a menu of values. An unedited line still lists every
# option, so a value containing " | " is an untouched placeholder, not a choice.
LIFECYCLES = ("IDEA", "DEFINED", "ARCHITECTURE-READY", "BOOTSTRAPPED", "SLICE-READY",
              "BUILDING", "RELEASE-CANDIDATE", "OPERATING", "PAUSED", "CANCELLED")
TIERS = ("LEAN", "STANDARD", "HIGH-RISK")
PATHS = ("lean", "full")
# delivery_target is "<pointer> / <endpoint>"; only the endpoint decides where
# closeout stops, and it must be one of the three the workflow defines. A prose
# ending such as "roughly done" leaves closeout to whoever reads it last.
ENDPOINT = re.compile(r"implementation-and-tests|release-ready|deployed:\S+")
# Evidence has to say what came back, not only what was run. A command that was
# executed proves an assertion held; it does not prove the entrypoint could be
# called and returned the promised result, which is what delivered claims.
RESULT = re.compile(r"->|=>|→|⇒")
# The result also has to be findable again, and the anchor has to sit where a
# reader looks for it: at the end of the result half. A search over the whole
# string let the invocation anchor itself -- 'curl https://api.example.com/orders
# -> 200 OK' passed on the URL it called, and so did the same row with '@ later'
# still attached, or with no anchor at all. That is not one bad row; every HTTP
# entrypoint carries a URL in every call, so the check was free for a whole class
# of projects, and it is the one part of delivered that prose cannot stand in for.
# The anchor is only the tail, though: what came back has to survive its removal.
# 'cmd -> @ abc123' and 'curl <url> -> <that same url>' both fill the two halves
# and both end in something findable, and neither records one observed result.
TRAILING_REF = re.compile(r"(?:^|\s)@\s*(\S+)\s*$")
TRAILING_LINK = re.compile(r"(?:^|\s)(https?://\S+)\s*$")
# Ref-shaped but moving. HEAD resolves to whatever was committed last, not to the
# commit this call ran against, so checking it out in six months runs different
# code while the row still reads as anchored. The long-lived branch names have the
# same defect; they are kept out of PLACEHOLDER_REF because the reason differs --
# these do name a place, just not the one that was observed. Same ceiling as the
# word table: '@ dev' and '@ feature/x' move too and pass.
MOVING_REF = re.compile(r"(?:\w+/)?(?:head|master|main|trunk|latest|tip)(?:[~^@].*)?", re.I)
# A change record must be locatable: an id such as C-03, a document path, or a
# link. Bare hyphenated words are not ids: "follow-up" once passed as a decision.
# Neither is a bare slash: while any string containing one counted as a path,
# "ask/bob" and "推迟到 v2/以后" passed as change records. delivery_target's
# pointer half reuses this: closeout checks that half off item by item, so it has
# to reach a real place too.
POINTER = re.compile(
    r"https?://\S+"
    r"|\S+\.(?:markdown|md|txt|rst|adoc)(?![A-Za-z0-9])(?:#\S+)?"
    r"|(?<![A-Za-z0-9])C-\d+"
)


@dataclass
class Slice:
    id: str
    owner: str = ""
    claimed: str = ""
    stage: str = ""
    write_scope: list[str] = field(default_factory=list)
    acceptance: list[tuple[str, str, str]] = field(default_factory=list)


def visible_lines(text: str) -> list[str]:
    """Drop fenced blocks so template examples cannot be read as real state."""
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
    return lines


def header_lines(text: str) -> list[str]:
    """The field block only: everything above the first section heading.

    Fields stop at the first heading so that prose further down cannot redefine
    them -- a handover note in Blockers reading "- owner: waiting on alice" is
    narrative, not a claim, and must not silently become the slice's owner.
    """
    lines: list[str] = []
    for line in visible_lines(text):
        if re.match(r"^#{2,6}\s", line):
            break
        lines.append(line)
    return lines


class TableProblem(ValueError):
    """Why a table could not be read, worded so the fix is unambiguous.

    'No table here' and 'that heading exists twice' need different repairs, so
    they must not arrive as the same sentence.
    """


def section_lines(lines: list[str], section: str) -> list[str]:
    """The body under one exact heading, up to the next heading of its level."""
    headings = [
        (i, len(match[1]), match[2].strip().rstrip("#").strip())
        for i, line in enumerate(lines)
        if (match := re.match(r"^(#{1,6})\s+(.+)$", line))
    ]
    selected = [(i, depth) for i, depth, title in headings if title == section]
    if not selected:
        raise TableProblem(
            f"no heading '{section}' in the source; write the heading text as it appears, "
            "not a URL slug"
        )
    if len(selected) > 1:
        raise TableProblem(
            f"heading '{section}' appears {len(selected)} times; one pointer must select one "
            "table, so make the heading unique or point at a deeper one"
        )
    start, depth = selected[0]
    end = next((i for i, level, _ in headings if i > start and level <= depth), len(lines))
    return lines[start + 1:end]


def rows_in(lines: list[str]) -> list[list[str]]:
    """Rows of every Markdown table whose first column header is A-ID."""
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


def table_rows(text: str, section: str | None = None) -> list[list[str]]:
    """Read A-ID tables in an optional exact heading, ignoring fenced examples."""
    lines = visible_lines(text)
    if section is not None:
        try:
            lines = section_lines(lines, section)
        except TableProblem:
            return []
    return rows_in(lines)


def fields_of(text: str, errors: list[str] | None = None, source: str = "") -> dict[str, str]:
    values: dict[str, str] = {}
    for line in header_lines(text):
        match = FIELD.match(line)
        if not match:
            continue
        name = match[1]
        if name in values:
            if errors is not None:
                errors.append(f"{source}: '{name}' is set twice; one field, one value")
            continue
        values[name] = match[2].strip()
    return values


def is_set(value: str) -> bool:
    value = value.strip()
    return value.casefold() not in UNSET and not (value.startswith("<") and value.endswith(">"))


def normalized(value: str) -> str:
    """Casefold and drop the punctuation people wrap a single word in.

    '@ 稍后。' and '@ later,' are the same promise as the bare word; a word table
    that only matches the bare form is trivially stepped around.
    """
    return value.strip().strip("`\"'“”‘’()（）[]【】<>《》.,;:!?、。，；：！？…-— ").casefold()


def is_placeholder(value: str) -> bool:
    """True when the value is a promise to name a place, not a place."""
    word = normalized(value)
    if not is_set(value) or word in PLACEHOLDER_REF:
        return True
    # 'someday-soon' and 'todo_later' are the same promise with a joiner in the
    # middle. Every part has to be one, so 'release-later' and 'v1.4.0-rc1' stay.
    parts = [part for part in re.split(r"[-_/\s]+", word) if part]
    return len(parts) > 1 and all(part in PLACEHOLDER_REF for part in parts)


def anchors(ref: str) -> bool:
    """Does this ref still resolve to this run when someone reads the row later?"""
    return not is_placeholder(ref) and not MOVING_REF.fullmatch(normalized(ref))


def split_anchor(result: str) -> tuple[str, str] | None:
    """Split the observed-result half into what came back and the ref ending it.

    Takes that half alone, and this is the only place that half is picked out.
    Read against the whole line the invocation anchors itself: 'curl <url> ->
    200 OK' passes on the URL it called, and 'cmd -> @ abc123' keeps 'cmd ->' as
    the thing that came back.

    '@ later' and '@ 稍后' say an anchor will exist; they do not say where. The
    only reason a delivered row carries one is so the call can be checked out and
    re-run, and there is nothing here to check out. The URL a request was sent to
    is not that either: it says the entrypoint exists, not that this run does.
    """
    tail = result.strip()
    match = TRAILING_REF.search(tail) or TRAILING_LINK.search(tail)
    return (tail[:match.start()].strip(), match[1]) if match else None


def normalize(root: Path, path: str) -> Path:
    """Resolve literal project-relative paths, including existing symlinks."""
    path = path.strip().replace("\\", "/")
    if not is_set(path) or any(char in path for char in "*?[]"):
        raise ValueError("expected a literal project-relative path (no globs)")
    if any(char in path for char in "<>`#"):
        raise ValueError("expected a literal path, not template or markup text")
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
    """Load the approved source itself; do not derive expected IDs from backlog.

    Each way of failing gets its own sentence: a missing file, a heading that is
    not there, a heading that is there twice, and a selection holding no table
    all need different repairs, and one shared message sends people to the
    wrong one.
    """
    filename, separator, section = pointer.partition("#")
    try:
        source = normalize(root, filename)
        if source.is_relative_to((root / STATE_DIR).resolve()):
            raise ValueError("must reference acceptance outside docs/workflow/")
        text = source.read_text(encoding="utf-8-sig")
    except OSError as exc:
        errors.append(f"acceptance_source '{pointer}': cannot read '{filename}': {exc.strerror or exc}")
        return None
    except ValueError as exc:
        errors.append(f"acceptance_source '{pointer}': {exc}")
        return None
    try:
        lines = visible_lines(text)
        if separator:
            lines = section_lines(lines, section)
        rows = rows_in(lines)
        if not rows:
            raise TableProblem(
                "the selection has no A-ID table; the authoritative rows are a Markdown table "
                "whose first column header is A-ID"
            )
    except TableProblem as exc:
        errors.append(f"acceptance_source '{pointer}': {exc}")
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


def check_declaration(project: dict[str, str], errors: list[str]) -> None:
    """Reject a header this script would otherwise have to guess at.

    Every gate below reads these fields. A typo such as BUILDNG used to pass
    untouched and then decide nothing, which reads as "the state is fine".
    """
    version = project.get("state_version", "")
    if not is_set(version):
        errors.append(
            f"project.md: state_version is missing; add the line '- state_version: {STATE_VERSION}'"
        )
    elif version.strip() != STATE_VERSION:
        errors.append(
            f"project.md: state_version '{version.strip()}' is not the layout this script reads; "
            f"migrate the files per references/99-state-and-handoff.md, then write "
            f"'- state_version: {STATE_VERSION}'"
        )
    for name, allowed in (("lifecycle", LIFECYCLES), ("tier", TIERS), ("path", PATHS)):
        value = project.get(name, "").strip()
        options = " | ".join(allowed)
        if " | " in value:
            errors.append(f"project.md: {name} still lists every option; keep one of {options}")
        elif not is_set(value):
            errors.append(f"project.md: {name} is missing; expected one of {options}")
        elif value not in allowed:
            errors.append(f"project.md: {name} '{value}' is not a known value; expected one of {options}")


def load_slices(root: Path, errors: list[str]) -> list[Slice]:
    slices: list[Slice] = []
    for path in sorted((root / STATE_DIR / "slices").glob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        values = fields_of(text, errors, path.name)
        # Validate before splitting: the unedited placeholder contains the
        # separators it documents, so splitting first turns one rejected value
        # into fragments that each pass as a plausible path.
        raw_scope = values.get("write_scope", "")
        item = Slice(
            id=path.stem,
            owner=values.get("owner", ""),
            claimed=values.get("claimed", ""),
            stage=values.get("stage", ""),
            write_scope=[p.strip() for p in re.split(r"[,;；，]", raw_scope) if p.strip()]
            if is_set(raw_scope) else [],
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

    project = fields_of((state / "project.md").read_text(encoding="utf-8-sig"), errors, "project.md")
    check_declaration(project, errors)
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
    # Undefined draft scope is allowed; tracked scope must name both what is
    # promised and where the handover ends, or closeout has nothing to check.
    tracking = bool(backlog or slices) or project.get("lifecycle") not in {"IDEA", "DEFINED"}
    if not is_set(pointer) and tracking:
        errors.append("project.md: acceptance_source is required before tracking or completing scope")
    target = project.get("delivery_target", "")
    if not is_set(target):
        if tracking:
            errors.append("project.md: delivery_target is required before tracking or completing scope")
    else:
        # The template is "<pointer> / <endpoint>". The endpoint says where
        # closeout stops; the pointer says what closeout checks off item by item.
        # 'release-ready' on its own passed while only the endpoint was read, and
        # then closeout had nothing to compare the work against. The pointer half
        # contains slashes of its own, so split on the last separator. It also has
        # to have the shape of a place: '随便 / release-ready' and '见合同 /
        # release-ready' cleared a not-a-placeholder test and still opened nothing.
        pointer_half, separator, endpoint = target.rpartition(" / ")
        endpoint = endpoint.strip()
        if not separator or is_placeholder(pointer_half) or not POINTER.search(pointer_half):
            errors.append(
                "project.md: delivery_target has no pointer to the completion boundary; write "
                "'<pointer> / <endpoint>', where the pointer reaches the list closeout has to "
                "check off item by item: a document path such as 'docs/contract.md#完成边界', "
                "a link, or a change id such as C-03"
            )
        if not ENDPOINT.fullmatch(endpoint):
            errors.append(
                f"project.md: delivery_target ends with '{endpoint}', which names no completion "
                "boundary; write '<pointer> / implementation-and-tests', '<pointer> / release-ready' "
                "or '<pointer> / deployed:<environment>'"
            )
    if expected is not None:
        for aid in sorted(expected - backlog.keys()):
            errors.append(f"backlog.md: missing authoritative A-ID {aid}")
        for aid in sorted(backlog.keys() - expected):
            errors.append(f"backlog.md: {aid} is not in acceptance_source")
    scope_verified = expected is not None and set(backlog) == expected

    def in_flight(item: Slice) -> bool:
        """A slice holds its owner and paths from claim until every row lands.

        Claiming happens before the acceptance rows are written, so an owner
        alone is enough to be in flight; a slice whose rows are all delivered is
        finished and releases its paths to the next claim.
        """
        if any(status == IN_FLIGHT for _, status, _ in item.acceptance):
            return True
        return is_set(item.owner) and not any(
            status == DELIVERED for _, status, _ in item.acceptance
        )

    live = [item for item in slices if in_flight(item)]
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
                errors.append(
                    f"owner '{item.owner}' holds two live slices: {owners[owner]} and {item.id}; "
                    "returning a slice means clearing its owner and claimed as well as its "
                    "unfinished rows, or the next claim by that owner lands here again"
                )
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
            elif backlog[aid][0] in TERMINAL:
                errors.append(
                    f"{aid}: backlog marks it {backlog[aid][0]}; drop its row from {item.id} so "
                    "the ledger keeps one status"
                )
            elif backlog[aid][0] != item.id:
                errors.append(
                    f"{aid}: backlog assigns it to '{backlog[aid][0]}' but it lives in {item.id}"
                )
            if status == DELIVERED:
                sides = [side.strip() for side in RESULT.split(evidence, maxsplit=1)]
                if not is_set(evidence):
                    errors.append(f"{item.id}: {aid} is delivered with no evidence pointer")
                elif len(sides) < 2 or not all(sides):
                    errors.append(
                        f"{item.id}: {aid} evidence records no observed result; write it as "
                        "'<invocation> -> <what came back>' from a real call against the "
                        "entrypoint, not a command on its own"
                    )
                elif (found := split_anchor(sides[1])) is None or not anchors(found[1]):
                    errors.append(
                        f"{item.id}: {aid} evidence cannot be located again; end the result "
                        "half with '@ <commit or ref>' or the run's link. A URL inside the "
                        "call is not an anchor, and neither is a placeholder ('@ later') or a "
                        "moving ref ('@ HEAD'); nobody can re-run the call being trusted"
                    )
                elif is_placeholder(found[0]):
                    errors.append(
                        f"{item.id}: {aid} evidence puts an anchor where the result belongs; "
                        "write what came back to the right of the arrow. The trailing "
                        "'@ <ref>' or link is extra -- it says where to find that run again, "
                        "and neither a placeholder ('见上') nor the URL the call was sent "
                        "to, copied back into that half, records anything observed"
                    )
            if status not in {DELIVERED, IN_FLIGHT}:
                errors.append(f"{item.id}: {aid} has status '{status}'; expected in-slice or delivered")

    for aid, (assignment, note) in backlog.items():
        if assignment in TERMINAL:
            if not is_set(note):
                errors.append(f"backlog.md: {aid} is {assignment} without a change record")
            elif not POINTER.search(note):
                errors.append(
                    f"backlog.md: {aid} is {assignment} but its note does not point at a change "
                    "record (an id such as C-03, a path, or a link)"
                )
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

    # Something has to say where the next hand lands. While a slice is in flight
    # its own stage is that cursor; with no slice open and scope still owed,
    # project.md is the only place left to carry it.
    next_action = project.get("next_action", "")
    scope_owed = not (scope_verified and not unclaimed and not in_flight)
    # The limit of this check: it can reject words that name no action at all.
    # Whether a concrete action is the right next one, and whether the command
    # beside it really verifies it, is not decidable here -- that stays with the
    # person writing the line and the stage gate that reads it.
    if is_set(next_action):
        if normalized(next_action) in NO_ACTION:
            errors.append(
                f"project.md: next_action '{next_action.strip()}' names no action; the file "
                "already says the work continues. Write the next executable action and the "
                "command that verifies it"
            )
    elif tracking and not live and scope_owed:
        errors.append(
            "project.md: next_action is required while no slice is in flight; name the next "
            "executable action and the command that verifies it"
        )

    report = {
        "state_status": "invalid" if errors else "ready",
        "legacy_state": [],
        "state_version": project.get("state_version", "?"),
        "lifecycle": project.get("lifecycle", "?"),
        "tier": project.get("tier", "?"),
        "path": project.get("path", "?"),
        "delivery_target": project.get("delivery_target", "?"),
        "next_action": next_action,
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
    if report["state_status"] == "legacy":
        print(f"workflow state predates this layout: {', '.join(report['legacy_state'])}")
        print("this is not a new project. Split that file into docs/workflow/ per the layout in "
              "references/99-state-and-handoff.md, carrying over every A-ID, owner, claim and "
              "evidence line, then run this again. Do not start a fresh state beside it")
        return
    if report["legacy_state"]:
        print("  an older single-file state sits beside this one: "
              f"{', '.join(report['legacy_state'])}; split it per "
              "references/99-state-and-handoff.md before trusting what follows")
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
    print(f"next action: {report['next_action'] or '-'}")


def incomplete_report(status: str, errors: list[str], legacy: list[str] | None = None) -> dict:
    return {
        "state_status": status, "legacy_state": legacy or [],
        "state_version": "?", "lifecycle": "?", "tier": "?", "path": "?",
        "delivery_target": "?", "next_action": "", "acceptance_source": "", "scope_verified": False,
        "slices": [], "unclaimed": [], "in_flight": [], "delivered": [],
        "deferred_or_dropped": [], "scope_complete": False, "errors": errors,
    }


def main() -> int:
    # A console that cannot encode the state files turns a readable report into
    # UnicodeEncodeError and exit 1, which reads as "the state is invalid".
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="backslashreplace")
            except (OSError, ValueError):
                pass

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="project root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state = root / STATE_DIR
    missing = [name for name in ("project.md", "backlog.md") if not (state / name).is_file()]
    if missing:
        # Partial state is a broken gate. An absent directory is a new project --
        # unless the pre-shard single file is lying beside it, and then reporting
        # "new project" is how a ledger with every A-ID and its evidence gets
        # replaced by an empty one while nobody reads the old file.
        legacy = [path.as_posix() for path in LEGACY_STATE if (root / path).is_file()]
        errors = [f"missing workflow state file: {name}" for name in missing] if state.exists() else []
        status = "invalid" if errors else "legacy" if legacy else "uninitialized"
        report = incomplete_report(status, errors, legacy)
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

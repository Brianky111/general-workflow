#!/usr/bin/env python3
"""Consistency checks for the general-workflow skill package.

Checks:
1. references/*.md and the SKILL.md Reference Map match one-to-one.
2. Every backticked reference-style mention (NN-kebab-name.md) in SKILL.md and
   references/ resolves to an existing file under references/.
3. Reachability: every reference file is reachable from the router
   (00-progress-router.md) or from SKILL.md operating rules via mention links.
   Unreachable files are reported as warnings (the Reference Map alone does not
   count as reachable).
4. Critical cross-stage policy anchors for production-node identity, reuse,
   sparse/risk-triggered test mapping, red admissibility, wiring, and review
   remain present.

Exit code 1 on errors; warnings alone exit 0.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
REFS = ROOT / "references"

REF_NAME = re.compile(r"^\d{2}-[a-z0-9][a-z0-9-]*\.md$")
MENTION = re.compile(r"`([^`]+?\.md)`")

POLICY_ANCHORS: dict[str, tuple[str, ...]] = {
    "SKILL.md": (
        "Use a positive readiness test",
        "at most two new artifacts",
        "that request is confirmation. Do not ask again for contract or planning approval",
        "Create only artifacts triggered by the current decision or risk",
        "enter red/green/refactor or implementation in the same run",
        "A red test against a test-local surrogate, an unregistered `V2`, a parallel harness, or a newly invented implementation path is invalid",
    ),
    "00-progress-router.md": (
        "## Positive READY Gate",
        "The user's explicit request to implement counts as confirmation",
        "Do not route backward merely because an optional document",
        "## Lean Fast Path",
        "Contract freeze, planning, red, and implementation may occur in the same run",
    ),
    "00-feature-grading-and-splitting.md": (
        "## Default Document Budget",
        "at most two new artifacts",
        "20% of expected task effort or 30 minutes",
        "An exception does not upgrade the whole feature",
    ),
    "05-conflict-scan.md": (
        "Assign a stable `N-ID`",
        "真实运行/装配入口",
        "复用否决证据",
        "选择点和退场条件",
    ),
    "06-test-strategy.md": (
        "## Default Sparse Coverage View",
        "## Risk-Triggered Full Matrix",
        "A standalone `02-测试矩阵.md` is a risk-triggered durable artifact, not the ordinary default",
        "生产 owner/SUT",
        "真实生产入口/装配根",
        "既有测试归宿/复用资产",
        "Bind every planned test to the stable `N-ID`, current production owner, real runtime/assembly entry, and nearest existing test home/reuse assets",
        "Do not rewrite matrix or progress documents after every",
    ),
    "06-planning.md": (
        "## Minimum Executable Plan",
        "Default existing-code work to `MODIFY_EXISTING` or `REUSE_EXTEND`",
        "## Execution Gate",
        "Do not ask for a second planning approval",
        "start `07-red-tests.md` or `08-implementation.md` in the same run",
    ),
    "04-interface-contract.md": (
        "Create or extend a dedicated interface contract only when at least one risk applies",
        "Repository age, multiple internal modules, or a desire to show every layer is not an entry condition",
        "A missing dedicated interface file is not a blocker when no trigger applies",
    ),
    "03-ambiguity-audit.md": (
        "Use an independent reviewer when public/external compatibility, irreversible migration, security/privacy/compliance, complex concurrency/state, cross-owner shared contracts, or formal audit requires separation of duties",
        "Otherwise the author may perform one labeled cold-read in the same run",
        "Do not create or attach a separate zero-finding report",
    ),
    "07-red-tests.md": (
        "baseline",
        "`UNEXPECTED-GREEN:<test-id>`",
        "`INVALID-RED:<test-id>`",
        "parallel SUT",
        "production entry",
        "cannot be waived into valid TDD evidence",
    ),
    "07-anti-cheat-and-red-replay.md": (
        "## Red Admissibility",
        "wrong SUT",
        "`superseded-invalid:<test-id>`",
        "real composition root",
    ),
    "08-implementation.md": (
        "stable `N-ID`",
        "parallel SUT",
        "non-test incoming edge",
        "real route, registry, export, or composition root",
    ),
    "09-review-and-verification.md": (
        "stable `N-ID`",
        "reuse rejection evidence",
        "non-test incoming edges",
        "real production route",
    ),
    "09-module-initial-review.md": (
        "A risk-triggered or independently owned module claims green or done",
        "Do not mirror the result into both `status.json` and `99-进度.md`",
    ),
    "10-counterexample-recovery.md": (
        "one update in the selected status/handoff source only when a pause, handoff, or closeout trigger exists",
        "Ordinary single-owner work does not create or synchronize status/progress files",
    ),
    "99-status-and-evidence.md": (
        "Ordinary single-owner work needs no dedicated status document",
        "Do not update status after every internal workflow stage",
        "Do not create or hand-maintain `workflow-state.json`, feature `status.json`, and `99-进度.md` in parallel",
        "choose one manual authority",
        "other views must be generated or treated as non-authoritative",
        "Do not report an untriggered artifact as “missing.”",
    ),
}


def ref_mentions(text: str) -> set[str]:
    """Backticked mentions that look like skill reference files (ASCII kebab).

    Workflow artifacts with Chinese names (00-整理后需求.md, 99-进度.md, ...)
    intentionally do not match.
    """
    out = set()
    for m in MENTION.finditer(text):
        name = m.group(1).split("/")[-1]
        if REF_NAME.match(name):
            out.add(name)
    return out


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    actual = {p.name for p in REFS.glob("*.md")}
    skill_text = SKILL.read_text(encoding="utf-8")

    # 1. Reference Map <-> directory
    map_match = re.search(r"## Reference Map\n(.*?)(?=\n## |\Z)", skill_text, re.S)
    if not map_match:
        errors.append("SKILL.md has no '## Reference Map' section")
        mapped = set()
    else:
        mapped = ref_mentions(map_match.group(1))
        for name in sorted(mapped - actual):
            errors.append(f"Reference Map lists missing file: {name}")
        for name in sorted(actual - mapped):
            errors.append(f"references/{name} is not listed in the Reference Map")

    # 2. Mentions resolve
    texts = {"SKILL.md": skill_text}
    for p in sorted(REFS.glob("*.md")):
        texts[p.name] = p.read_text(encoding="utf-8")
    for src, text in texts.items():
        for name in sorted(ref_mentions(text) - actual):
            errors.append(f"{src} mentions missing reference: {name}")

    # 3. Reachability from the router and SKILL.md rules (Reference Map excluded)
    rules_text = skill_text[: map_match.start()] if map_match else skill_text
    frontier = ref_mentions(rules_text) & actual
    reachable: set[str] = set()
    while frontier:
        name = frontier.pop()
        if name in reachable:
            continue
        reachable.add(name)
        frontier |= (ref_mentions(texts[name]) & actual) - reachable
    for name in sorted(actual - reachable):
        warnings.append(
            f"references/{name} is unreachable from the router or SKILL.md rules"
        )

    # 4. Cross-stage semantic policy anchors
    for name, anchors in POLICY_ANCHORS.items():
        text = texts.get(name, "")
        for anchor in anchors:
            if anchor not in text:
                errors.append(f"{name} is missing policy anchor: {anchor}")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(
        f"{len(actual)} reference files, {len(errors)} error(s), {len(warnings)} warning(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

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

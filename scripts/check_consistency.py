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
4. Critical cross-stage policy anchors for original-request-first routing,
   concrete request-gap gating, production-node identity, reuse,
   sparse/risk-triggered test mapping, red admissibility, wiring, review, a
   finite anchor-linked test boundary, bounded discovery, and mandatory
   workflow termination remain present.

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
        "Treat the durable original user request as the immutable **Delivery Anchor**",
        "Before selecting any stage, classify the anchor as `ANCHOR-SATISFIED`, `ANCHOR-UNMET`, or `ANCHOR-BLOCKED`",
        "Continue only from `ANCHOR-UNMET` by naming one concrete `request_gap`",
        "If no such gap exists, close or quarantine the finding",
        "Use a positive readiness test",
        "at most two new artifacts",
        "that request is confirmation. Do not ask again for contract or planning approval",
        "Create only artifacts triggered by the current decision or risk",
        "enter red/green/refactor or implementation in the same run",
        "A red test against a test-local surrogate, an unregistered `V2`, a parallel harness, or a newly invented implementation path is invalid",
        "Freeze a finite Test Obligation Set (`TOS`)",
        "Every obligation must cite the Delivery Anchor outcome/non-goal",
        "an unanchored obligation is `INVALID-OBLIGATION`, cannot enter red, and cannot block completion",
        "Tests, reviews, tools, and executors cannot add keys",
        "Freeze cumulative probe/pairwise/property/fuzz/mutation/adversarial discovery and repair limits",
        "A normal discovery limit records `DISCOVERY-CLOSED`",
        "`DELIVERY-DONE` starts with every original/accepted outcome observed through the intended production entry",
        "A finding defeats completion only when it is reproducible, maps to an anchor item",
        "Unanchored campaigns, obligations, gates, theoretical risks, coverage suggestions, and optional reviews are follow-ups",
        "When `DELIVERY-DONE` holds, perform one closeout/status sync, report completion, and stop",
    ),
    "00-progress-router.md": (
        "## Delivery Anchor and First Decision",
        "The **Delivery Anchor** is the immutable durable original user request/source plus only explicitly accepted deltas",
        "ANCHOR-SATISFIED:",
        "ANCHOR-UNMET:",
        "ANCHOR-BLOCKED:",
        "name exactly one current `request_gap` before continuing",
        "If no valid `request_gap` can be named, do not enter requirements, planning, test, review, discovery, or implementation",
        "## Positive READY Gate",
        "The user's explicit request to implement counts as confirmation",
        "Do not route backward merely because an optional document",
        "## Lean Fast Path",
        "Contract freeze, planning, red, and implementation may occur in the same run",
        "## Global Completion and Stop Rule",
        "Every row must cite the anchor outcome/non-goal",
        "An unanchored row is `INVALID-OBLIGATION`",
        "ORIGINAL-REQUEST-DONE =",
        "`DELIVERY-DONE` is true only when `ORIGINAL-REQUEST-DONE` is true",
        "new behavior:  PENDING -> RED -> GREEN -> VERIFIED",
        "repair:         VERIFIED/GREEN -> GAP -> [RED when recapture is needed] -> REPAIRING -> VERIFIED | BLOCKED",
        "`PASS`, `EXISTING-PASS`, and `ACCEPTED-NONTEST` are evidence kinds, not obligation states",
        "Every anchor-required implementation/refactor/write batch is integrated",
        "Every review, integration, safety, compatibility, or governed gate declared in advance as minimum credible anchor evidence has run once and closed",
        "Open a new red target only for a valid anchor-linked frozen `PENDING` obligation or a same-key `GAP`",
        "Reaching a limit closes that pass as `DISCOVERY-CLOSED`",
        "Default allowances are implicit",
        "Do not create an all-zero ledger",
        "Any second `INVALID-RED` after one correction for the obligation is `ANCHOR-BLOCKED`",
        "## Stage Selection Table (`ANCHOR-UNMET` Only)",
        "First decide whether the Delivery Anchor is satisfied; no stage, finding, risk, or missing artifact outranks this question",
    ),
    "00-feature-grading-and-splitting.md": (
        "## Default Document Budget",
        "at most two new artifacts",
        "20% of expected task effort or 30 minutes",
        "An exception does not upgrade the whole feature",
    ),
    "02-requirements-capture.md": (
        "The Delivery Anchor is the immutable original request/source plus the ordered set of explicitly accepted deltas",
        "do not create an Anchor document, ID namespace, or rewritten “clean” original",
        "Structured requirements, BDD examples, plans, and tests are faithful projections",
        "A reviewer, test, tool, executor, orchestrator, or external-drift finding is only evidence or a change candidate",
        "Never create a separate Delivery Anchor artifact",
    ),
    "03-bdd-example-mapping.md": (
        "BDD is a faithful lean-contract projection; it is not an authority that can expand the request",
        "trace it to the current Delivery Anchor source/delta",
        "A tool/reviewer finding may sharpen an already anchored outcome, but cannot create a new example scope without an accepted delta",
        "A new tool/reviewer idea is a change candidate, not an automatic blocker",
    ),
    "05-conflict-scan.md": (
        "Assign a stable `N-ID`",
        "真实运行/装配入口",
        "复用否决证据",
        "选择点和退场条件",
    ),
    "06-test-strategy.md": (
        "The plan declares the Delivery Anchor and one selected `request_gap` once",
        "## Default Sparse Coverage View",
        "## Risk-Triggered Full Matrix",
        "A standalone `02-测试矩阵.md` is a risk-triggered durable artifact, not the ordinary default",
        "生产 owner/SUT",
        "真实生产入口/装配根",
        "既有测试归宿/复用资产",
        "Bind every planned test to the stable `N-ID`, current production owner, real runtime/assembly entry, and nearest existing test home/reuse assets",
        "Do not rewrite matrix or progress documents after every",
        "## Finite Test Obligation Set",
        "Every row must trace through its existing acceptance/obligation ID",
        "`INVALID-OBLIGATION`",
        "Tests and review findings do not create obligations",
        "Stop at the first limit—or when the declared finite input scope is exhausted—and mark `DISCOVERY-CLOSED`",
        "the same delivery cannot reset or append budget",
    ),
    "06-planning.md": (
        "The Delivery Anchor is known",
        "Select exactly one current `request_gap`",
        "Declare the Delivery Anchor source and current gap **once at the plan header**",
        "## Minimum Executable Plan",
        "Default existing-code work to `MODIFY_EXISTING` or `REUSE_EXTEND`",
        "## Execution Gate",
        "Do not ask for a second planning approval",
        "start `07-red-tests.md` or `08-implementation.md` in the same run",
        "Freeze a finite Test Obligation Set (`TOS`)",
        "The frozen `TOS` is the complete current-work test boundary, not a starter list",
        "An obligation that cannot trace through its existing acceptance/obligation ID",
        "is `INVALID-OBLIGATION`",
        "Ordinary work implicitly uses `counterexample_admission_cap=1`",
        "the same delivery cannot reset, append, or rename a campaign",
        "Without these triggered limits, that discovery pass is not executable",
        "Mark `PLANNING-GAP` and stop before testing",
        "Materialize pairwise/combinatorial cases into the frozen `TOS`",
    ),
    "04-interface-contract.md": (
        "Create or extend a dedicated interface contract only when at least one risk applies",
        "Repository age, multiple internal modules, or a desire to show every layer is not an entry condition",
        "A missing dedicated interface file is not a blocker when no trigger applies",
    ),
    "03-ambiguity-audit.md": (
        "verify that derived requirements/BDD remain faithful to the Delivery Anchor",
        "Read the immutable original source, ordered accepted deltas",
        "Every derived requirement/example maps to the current Delivery Anchor source or accepted delta",
        "reviewer/tool suggestion without Anchor authority",
        "Use an independent reviewer when public/external compatibility, irreversible migration, security/privacy/compliance, complex concurrency/state, cross-owner shared contracts, or formal audit requires separation of duties",
        "Otherwise the author may perform one labeled cold-read in the same run",
        "Do not create or attach a separate zero-finding report",
    ),
    "07-red-tests.md": (
        "The selected obligation traces through its existing acceptance/contract ID",
        "If that trace is absent or the assertion cannot close the gap, record `INVALID-OBLIGATION`",
        "baseline",
        "`UNEXPECTED-GREEN:<test-id>`",
        "`INVALID-RED:<test-id>`",
        "parallel SUT",
        "production entry",
        "cannot be waived into valid TDD evidence",
        "Select only a `PENDING` obligation or an existing `GAP` obligation",
        "Any later `INVALID-RED` for that obligation is `BLOCKED`, regardless of category",
        "Do not derive another obligation from the red output",
    ),
    "07-anti-cheat-and-red-replay.md": (
        "minimum proof for the currently selected anchor-linked `request_gap`",
        "## Red Admissibility",
        "wrong SUT",
        "`superseded-invalid:<test-id>`",
        "real composition root",
        "Faithful `UNEXPECTED-GREEN` is existing proof, not an invalid red",
        "Any later invalid red for that anchor-linked obligation is `ANCHOR-BLOCKED`, regardless of category",
    ),
    "08-implementation.md": (
        "The write batch traces through an existing acceptance/obligation ID",
        "Every write in the batch must contribute to closing that gap",
        "stable `N-ID`",
        "parallel SUT",
        "non-test incoming edge",
        "real route, registry, export, or composition root",
        "Continue only concrete `PENDING` obligations from the frozen `TOS`",
        "return to the Delivery Anchor, recompute its remaining unmet clauses",
        "it never authorizes another red test",
        "predeclared finite implementation/repair allowance",
        "mark the obligation `BLOCKED` and stop",
    ),
    "09-review-and-verification.md": (
        "stable `N-ID`",
        "reuse rejection evidence",
        "non-test incoming edges",
        "real production route",
        "Review can find a gap in a frozen obligation; it cannot create a new obligation",
        "A missing accepted behavior or required seam is `PLANNING-GAP`",
        "do not restart sampling, adversarial discovery, or “find more tests.”",
        "If any frozen finding remains",
        "record the review gate closed once",
    ),
    "09-module-initial-review.md": (
        "A risk-triggered or independently owned module claims green or done",
        "Do not mirror the result into both `status.json` and `99-进度.md`",
        "Freeze the first review's complete finding set",
        "It must not choose another sample set or start a new discovery pass",
        "mark the independent-review gate closed",
    ),
    "09-integration-acceptance.md": (
        "Execute only the acceptance behaviors assigned",
        "do not open a post-implementation red loop",
        "allow one aggregate repair",
        "When assigned obligations pass, mark them `VERIFIED`, stop integration",
    ),
    "09-feature-completeness.md": (
        "The category lists below are prompts for reconciling those obligations, not a source of additional tests",
        "A missing accepted behavior or required seam is `PLANNING-GAP`",
        "The lessons pass cannot reopen the completed feature or its test set",
        "do not search for additional theoretical cases, rerun discovery, or create tests to improve a metric",
    ),
    "10-counterexample-recovery.md": (
        "one update in the selected status/handoff source only when a pause, handoff, or closeout trigger exists",
        "Ordinary single-owner work does not create or synchronize status/progress files",
        "at most one representative regression obligation for the distinct anchor-falsifying failure",
        "Recovery never launches another property/fuzz/mutation/adversarial discovery pass",
        "Reaching the admission cap closes discovery and preserves already admitted work",
        "Only a later accepted user/authoritative-source delta may create a new delivery",
        "If the finding does not satisfy the anchor-falsification test",
    ),
    "10-change-protocol.md": (
        "appending an accepted delta, without rewriting the original request or earlier accepted history",
        "Never edit or replace the original source or earlier accepted deltas",
        "Keep unaffected closed obligations closed",
        "A reviewer, test/discovery tool, executor, or orchestrator cannot self-accept expansion",
        "A new discovery campaign or refreshed cap belongs to a new accepted delivery",
        "frozen probe ID, request/attempt, wall-clock, sanitization, and no-reset limits",
    ),
    "00-orchestration-policy.md": (
        "Every writable or gate-consuming executor must close a named Delivery Anchor `request_gap`",
        "Executors may consume assigned anchor-linked obligations but cannot add them",
        "frozen campaign ID plus remaining cumulative wall-clock/attempted-case/admission budget",
        "Rerouting, another executor/session, or a renamed campaign cannot reset the cumulative counters",
        "A review executor consumes the anchor-linked owning obligation/gate's single primary-review, recheck, or adjudication slot",
        "Do not launch a chain of reviewers/adversarial executors",
        "Normal limit exhaustion closes that campaign as `DISCOVERY-CLOSED`",
    ),
    "99-status-and-evidence.md": (
        "- Delivery Anchor：<original source + ordered accepted delta refs；current state>",
        "- Anchor state / request_gap：<SATISFIED / UNMET + concrete existing ID or clause / BLOCKED + exact reason>",
        "Ordinary single-owner work needs no dedicated status document",
        "Do not update status after every internal workflow stage",
        "Do not create or hand-maintain `workflow-state.json`, feature `status.json`, and `99-进度.md` in parallel",
        "choose one manual authority",
        "other views must be generated or treated as non-authoritative",
        "Do not report an untriggered artifact as “missing.”",
        "completion names the finite frozen `TOS` total and shows every obligation `VERIFIED`",
        "Record `planning_gap_refreeze_used`",
        "Never create an all-zero ledger",
        "a reroute or session change cannot reset it",
        "When `DELIVERY-DONE` is evidenced, write one closeout and stop",
    ),
    "00-refactor-intake.md": (
        "route through `06-planning.md` to freeze it before writing the test",
        "Do not keep searching for more invariants after freeze",
        "Return to the router when the finite set is verified or blocked",
    ),
    "00-governance-ci-hooks.md": (
        "each scheduled fuzz/property job has a fixed target/invariant",
        "cross-run semantic deduplication",
        "never appends to the current or a `DELIVERY-DONE` TOS",
    ),
    "04-fixtures-and-probes.md": (
        "freeze one inline probe campaign: Delivery Anchor item/current `request_gap`",
        "rerouting, another script/executor/session, or a renamed endpoint/question cannot reset or append budget",
        "A normal request/time limit with sufficient anchor evidence records `DISCOVERY-CLOSED`",
        "never appends to or reopens a `DELIVERY-DONE` TOS by itself",
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

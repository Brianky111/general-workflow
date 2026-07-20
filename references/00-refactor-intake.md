# Refactor Intake

## Purpose

Prevent refactor requests from changing behavior accidentally. Establish the smallest trustworthy protection baseline from existing code, public behavior, and tests, then classify the work without backfilling a documentation program.

## Not a New Behavior Feature

A refactor does not create a new product-behavior feature, but an explicitly requested refactor/write batch is part of the Delivery Anchor and remains incomplete until implemented or evidence-backed no-op/superseded. Do not create a feature folder, raw-requirement copy, contract set, test matrix, or roster entry for it. Record the requested write and protection baseline in the current plan/handoff or an existing owning feature document. Use `10-change-protocol.md` only when accepted behavior actually changes.

## Entry Conditions

- The user asks to refactor, clean up, rewrite, restructure, simplify, `重构`, or `整理`.
- Planning selects `refactor before implementation`.
- A refactor commit or work batch is about to start.

Before intake, confirm `ANCHOR-UNMET` names the requested refactor/write batch or one of its accepted preservation constraints as the current `request_gap`. A cleanup suggestion found by an agent is not authorization to refactor.

## Protection Recertification

Before touching code, inspect the smallest available evidence set:

- the current public/runtime entry, active owner, callers, registrations, persistence/schema boundaries, and downstream effects;
- the nearest existing protection tests, their runner and baseline result, plus reusable fixtures/helpers;
- accepted behavior docs when they already exist and are relevant;
- recent diffs, PR/CI notes, and user-stated preservation constraints.

Do not read every workflow document, require approval timestamps, or create missing artifacts. Current code, observable behavior, and a green protection suite may serve as the refactor contract. If protection needed to prove an accepted preservation outcome is missing, identify the smallest finite anchor-linked characterization obligation around the existing production owner, then route through `06-planning.md` to freeze it before writing the test.

## Classification

Classify the requested work before implementation:

- **Pure refactor:** no change to observable outcomes, public signatures, data semantics, persisted shape, user-visible text, error/protocol/authorization behavior, or runtime ownership. Existing protection remains green throughout. Missing coverage becomes a finite characterization obligation in the refactor plan; it does not require behavior red.
- **Behavior-affecting refactor:** any of the above might change, or layer/module boundaries need to move. Route to `10-change-protocol.md` level A before coding.
- **Unprotected behavior:** the intended invariant is clear but no test reaches the current owner. Record one obligation per distinct preserved invariant, merge equivalent examples into one parameterized characterization, and freeze the set in `06-planning.md`. Only then add those planned tests in the existing test home, confirm `EXISTING-PASS` evidence against the current production path, mark the obligations `VERIFIED`, and refactor. Do not keep searching for more invariants after freeze. Missing workflow documents alone never create this classification.

Every refactor target must name the production `N-ID`, behavior being preserved, exact write boundary, protection command, and rollback. Do not justify a replacement or second owner solely from code aesthetics.

In a repository that never adopted this workflow, use the same rule; no special bootstrap is required.

## Plan Update

Record a compact preflight in the current task plan, handoff, or existing owning document:

```markdown
## 重构复核

| 项 | 证据 | 结论 |
|---|---|---|
| Delivery anchor / request gap | `<original request or accepted outcome>` | <requested refactor/write still open> |
| Production node | `<N-ID / owner / real entry>` | <existing owner; no parallel replacement> |
| Protected behavior | `<anchor-linked observable invariants>` | <unchanged / behavior change> |
| Baseline | `<existing test command + result>` | <green / characterization needed> |
| Finite protection obligation | `<existing ID:characterization / PENDING or VERIFIED>` | <`EXISTING-PASS` evidence / planned once> |
| Reused test assets | `<suite / fixture / helper>` | <reuse decision> |
| Write boundary | `<files/symbols>` | <writable / read-only / prohibited> |
| 回滚方式 | `<命令/分支/开关>` | <说明> |
```

If no executable plan exists, use `06-planning.md`; a standalone `02-规划.md` is not required.

After planning freezes any characterization obligations, consume exactly those items once in the existing test home. A faithful green result is `EXISTING-PASS` evidence and moves the obligation to `VERIFIED`; an invalid target gets the single mapping/setup correction allowed by the global TOS rule. Then implement the still-open requested refactor/write batch. Verified protection alone does not satisfy that original request. Return to the router when the finite set is verified or blocked—never search for another invariant during protection capture.

If local subagent tools are available and the refactor is non-trivial, read `00-orchestration-policy.md` after the refactor classification. The main thread remains the orchestrator; executors perform assigned audits, mappings, tests, or module edits.

## Output

- Compact refactor preflight in the selected plan/handoff surface.
- Pure-refactor / behavior-affecting / unprotected-behavior classification.
- Updated status evidence only at a human pause, handoff, or closeout when the project uses a status surface.
- Exact tests, CI, diffs, or review reports used as evidence.
- Frozen characterization obligations and used allowances when protection was missing; no standalone TOS artifact.

## Stop Conditions

Stop before coding if an anchor-linked preserved behavior is ambiguous, the requested work would change public/data/runtime behavior without an accepted change, required characterization is not finite/frozen, no safe characterization seam can be established, or evidence contradicts the pure-refactor classification. Once the frozen characterization set is `VERIFIED`, stop protection discovery and proceed with the requested refactor; do not mark the Delivery Anchor satisfied until that write is integrated or evidence-backed no-op/superseded. Missing workflow documents, unanchored invariants, or timestamps are not blockers.

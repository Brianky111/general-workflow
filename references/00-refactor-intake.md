# Refactor Intake

## Purpose

Prevent refactor requests from changing behavior accidentally. Establish the smallest trustworthy protection baseline from existing code, public behavior, and tests, then classify the work without backfilling a documentation program.

## Not a Feature

A refactor is work on existing behavior, never a requirement of its own. Do not create a feature folder, raw-requirement copy, contract set, test matrix, or roster entry for the refactor. Record the protection baseline and write boundary in the current plan/handoff or an existing owning feature document. Use `10-change-protocol.md` only when accepted behavior actually changes.

## Entry Conditions

- The user asks to refactor, clean up, rewrite, restructure, simplify, `重构`, or `整理`.
- Planning selects `refactor before implementation`.
- A refactor commit or work batch is about to start.

## Protection Recertification

Before touching code, inspect the smallest available evidence set:

- the current public/runtime entry, active owner, callers, registrations, persistence/schema boundaries, and downstream effects;
- the nearest existing protection tests, their runner and baseline result, plus reusable fixtures/helpers;
- accepted behavior docs when they already exist and are relevant;
- recent diffs, PR/CI notes, and user-stated preservation constraints.

Do not read every workflow document, require approval timestamps, or create missing artifacts. Current code, observable behavior, and a green protection suite may serve as the refactor contract. If the behavior lacks protection, add a characterization test around the existing production owner before restructuring it.

## Classification

Classify the requested work before implementation:

- **Pure refactor:** no change to observable outcomes, public signatures, data semantics, persisted shape, user-visible text, error/protocol/authorization behavior, or runtime ownership. Existing protection remains green throughout; characterization tests may be added before the refactor when coverage is missing, but no behavior red is required.
- **Behavior-affecting refactor:** any of the above might change, or layer/module boundaries need to move. Route to `10-change-protocol.md` level A before coding.
- **Unprotected behavior:** the intended invariant is clear but no test reaches the current owner. Add the smallest characterization test in the existing test home, confirm it is green against the current production path, then refactor. Missing workflow documents alone never create this classification.

Every refactor target must name the production `N-ID`, behavior being preserved, exact write boundary, protection command, and rollback. Do not justify a replacement or second owner solely from code aesthetics.

In a repository that never adopted this workflow, use the same rule; no special bootstrap is required.

## Plan Update

Record a compact preflight in the current task plan, handoff, or existing owning document:

```markdown
## 重构复核

| 项 | 证据 | 结论 |
|---|---|---|
| Production node | `<N-ID / owner / real entry>` | <existing owner; no parallel replacement> |
| Protected behavior | `<observable invariants>` | <unchanged / behavior change> |
| Baseline | `<existing test command + result>` | <green / characterization needed> |
| Reused test assets | `<suite / fixture / helper>` | <reuse decision> |
| Write boundary | `<files/symbols>` | <writable / read-only / prohibited> |
| 回滚方式 | `<命令/分支/开关>` | <说明> |
```

If no executable plan exists, use `06-planning.md`; a standalone `02-规划.md` is not required.

If local subagent tools are available and the refactor is non-trivial, read `00-orchestration-policy.md` after the refactor classification. The main thread remains the orchestrator; executors perform assigned audits, mappings, tests, or module edits.

## Output

- Compact refactor preflight in the selected plan/handoff surface.
- Pure-refactor / behavior-affecting / unprotected-behavior classification.
- Updated status evidence only at a human pause, handoff, or closeout when the project uses a status surface.
- Exact tests, CI, diffs, or review reports used as evidence.

## Stop Conditions

Stop before coding only if the preserved behavior itself is ambiguous, the requested work would change public/data/runtime behavior without an accepted change, no safe characterization seam can be established, or evidence contradicts the pure-refactor classification. Missing workflow documents or timestamps are not blockers.

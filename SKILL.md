---
name: general-workflow
description: Guide agent-led software work through a staged, document-governed general development workflow with progress detection, on-demand reference loading, and orchestrated subagent execution. Use when Codex needs to pick up an existing feature workflow, create requirements/contracts/plans/tests, continue TDD implementation, handle refactor or cleanup work with requirements recertification, coordinate subagents as executors while the main thread stays the orchestrator, run verification, or handle workflow changes without reading a full process manual up front.
---

# General Workflow

Use this skill as a progressive-disclosure router. Start from repository evidence, decide the current stage, then load only the reference needed for that stage.

## Required First Step

Read `references/00-progress-router.md` before reading any other reference file.

## Operating Rules

- Inspect repository evidence before choosing a stage: `docs/`, feature folders, status files, PR/CI notes, tests, and recent diffs when available.
- Treat refactor, cleanup, rewrite, restructure, or simplification requests as workflow work, not simple code edits. Before editing code, read `references/00-refactor-intake.md`, recertify requirements/contracts/plans, and classify pure refactor versus behavior or architecture change.
- Treat the current conversation as the orchestrator. It owns stage routing, scope, task decomposition, subagent prompts, integration, conflict resolution, final verification, and user communication.
- Treat subagents as executors. When execution is delegated, the main thread must not concurrently implement the same scope; it should coordinate, monitor, integrate, and verify. The main thread may do local execution only for tiny tasks, immediate unblockers, integration glue, final fixes after executor output, or when delegation is unavailable/unsafe; record the reason.
- At planning, refactor, implementation, and review stages, read `references/00-orchestration-policy.md` when local subagent tools exist and the task is non-trivial, separable, risky, or validation-heavy.
- Load one stage reference at a time. Do not read all files in `references/` unless the user explicitly asks for a full audit or migration.
- Load support references only when the selected stage asks for them or the evidence triggers their topic.
- If evidence is contradictory, read `references/99-status-and-evidence.md`, reconcile the state, then return to the router.
- If a stage requires user confirmation, stop at the gate and report the exact decision needed.
- Treat the original workflow document, if present, as source material only. Prefer the split reference documents for execution.

## Reference Map

- `00-progress-router.md`: determine current stage and next document.
- `00-orchestration-policy.md`: keep the main thread as orchestrator and use subagents as scoped executors.
- `00-refactor-intake.md`: re-check requirements before refactoring and classify behavior risk.
- `00-project-kickoff.md`: initialize architecture, glossary, governance, and workflow state.
- `00-feature-grading-and-splitting.md`: decide standard/lightweight path and whether to split large contracts.
- `00-governance-ci-hooks.md`: set or audit document governance, CI gates, hooks, and scheduled checks.
- `01-project-identification.md`: classify new project, old project, or new module in old project.
- `02-requirements-capture.md`: preserve raw request and produce structured requirements.
- `03-requirements-clarification.md`: surface ambiguities and record decisions.
- `03-ambiguity-audit.md`: run the independent ambiguity audit before a human gate.
- `04-interface-contract.md`: define external behavior, data models, invariants, and scenarios.
- `04-fixtures-and-probes.md`: capture external data through probes and govern contract/counterexample fixtures.
- `05-conflict-scan.md`: compare desired behavior with existing code and overlapping features.
- `06-planning.md`: choose implementation strategy and validation strength.
- `07-red-tests.md`: create and prove failing tests before implementation.
- `07-anti-cheat-and-red-replay.md`: enforce red-before-green, commit purity, and red replay rules.
- `08-implementation.md`: implement against frozen contracts without weakening tests.
- `09-review-and-verification.md`: verify behavior, evidence, UI, and regression scope.
- `09-module-initial-review.md`: perform the independent module-level review.
- `09-integration-acceptance.md`: run full integration, user-visible acceptance, and scenario regression capture.
- `10-change-protocol.md`: handle contract, requirement, or external-behavior changes.
- `10-counterexample-recovery.md`: turn reproducible failures into permanent regression tests.
- `99-status-and-evidence.md`: maintain progress state and evidence links.

## Default Response Shape

When taking over work, report:

1. Detected stage.
2. Evidence used.
3. Reference file loaded next.
4. Immediate action or blocking question.
5. Orchestration decision when relevant: executor scopes delegated, or a concise reason the main thread is executing directly.

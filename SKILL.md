---
name: general-workflow
description: Guide agent-led software delivery through an implementation-forward, evidence-driven workflow with progress detection, vertical feature slicing, concise BDD contracts, reuse-aware planning, code-bound TDD, and proportionate verification. Use when kicking off a project, decomposing modules/features/use cases, defining Given-When-Then behavior, creating or revising requirements/contracts/plans/tests, extending an existing codebase, connecting UI/API/domain/infrastructure, continuing implementation, recertifying refactors, verifying cross-feature or E2E behavior, or handling changes. Typical triggers include 新项目开工, 功能拆分, BDD, TDD, 接手/继续开发, 重构/整理, verify, and change requests.
---

# General Workflow

Use this skill as a progressive-disclosure router. Start from repository evidence, choose the smallest safe path to working code, then load only the reference needed for the next material decision or execution step.

## Required First Step

Read `references/00-progress-router.md` before reading any other reference file.

## Operating Rules

- Treat working code plus trustworthy verification as the primary deliverable. Documentation pays only for an unresolved decision, a handoff, or a material risk; never finish an authorized build/change request with documents alone when the work is ready to implement.
- Inspect repository evidence before choosing a stage: current production entry points and owners, call/registration paths, nearby tests and their runner, reusable fixtures/helpers/fakes, docs, status, PR/CI notes, and recent diffs. For existing-code work, code and tests are mandatory planning inputs rather than a post-contract afterthought.
- Use a positive readiness test. Normal work is ready when observable behavior and non-goals are clear, no blocking product decision remains, changed public/data semantics are explicit, the existing-code write seam is known, and a credible verification path exists. A faithful raw-source + structured-requirement + BDD bundle is the default frozen behavior contract; a separate interface contract is required only for a material public/runtime boundary change.
- When the user already asked to implement and the compact contract is a faithful restatement with no behavior-changing choice, that request is confirmation. Do not ask again for contract or planning approval. Stop only for a choice that changes user-visible behavior, data meaning, external compatibility, irreversible outcomes, security/compliance posture, or accepted scope.
- Default to the lean path. Before code, ordinary work may create at most two new artifacts, 160 non-empty Markdown lines, and one human pause, and should consume at most 20% of the expected work or 30 minutes. Exceed a limit only for a named risk trigger and state which decision or evidence the extra material supports.
- Treat one requirement = one feature boundary = one source of truth as the organizing instinct. A feature is a user-visible vertical slice that may cross frontend, shared contracts, backend, persistence, and cross-feature events; it is not synonymous with one backend directory. Route every incoming request into exactly one source: a new feature, a merge into an unconfirmed sibling, or a delta revision of a confirmed one. Never create a second document set for the same behavior. Place requests on the hierarchy in `00-business-taxonomy.md` only when that distinction affects ownership or delivery.
- Treat numbered `00-…` through `99-…` artifacts as conditional dashboard slots, not a mandatory set. Create only artifacts triggered by the current decision or risk. An untriggered interface document, conflict report, full test matrix, audit report, or state mirror is `N/A`, not a missing gate. Update the selected status surface only at a human pause, handoff, or closeout.
- Bind every existing-code test/implementation loop to a stable production node (`N-ID`): current owner, real runtime or composition-root path, nearest existing test home, and reused test assets. A red test against a test-local surrogate, an unregistered `V2`, a parallel harness, or a newly invented implementation path is invalid. Prefer modifying or extending the current owner; `NEW` or `REPLACEMENT` nodes require explicit reuse-rejection evidence, a non-test runtime edge, wiring verification, and—when side by side—a selection and retirement rule.
- Once readiness holds, write the smallest executable plan and enter red/green/refactor or implementation in the same run. Missing optional documents, approval timestamps, matrix `N/A` cells, or status mirrors must not delay code. Record evidence at meaningful checkpoints rather than after every internal micro-step.
- Treat refactor, cleanup, rewrite, restructure, or simplification requests as workflow work, not new features. Read `00-refactor-intake.md`, reuse the owning behavior contract and existing green protection, and record only the delta needed to prove behavior preservation.
- Maintain a scope firewall. The frozen behavior, code-reality scan, and executable plan define what may change; code topology explains why those paths are sufficient. Quarantine unrelated bugs, failing tests, or design smells unless they directly block current evidence. Do not opportunistically repair neighboring systems.
- Treat the current conversation as the orchestrator. It owns stage routing, scope, task decomposition, subagent prompts, integration, conflict resolution, final verification, and user communication.
- Treat subagents as executors. When execution is delegated, the main thread must not concurrently implement the same scope; it should coordinate, monitor, integrate, and verify. The main thread may do local execution only for tiny tasks, immediate unblockers, integration glue, final fixes after executor output, or when delegation is unavailable/unsafe; record the reason.
- Before opening a new executor, worktree, branch, or implementation loop for a bound feature, close any existing loop for that feature first. Collect the handoff, integrate or reject code/test/doc changes, update the one selected status surface when one is used, verify, commit or record no-op/blocker evidence, and release or advance ownership. Do not stack worktrees to compensate for unfinished integration.
- Open a writable worktree only with a concrete worktree charter: one feature/micro-batch/bug objective, the accepted requirement or bug/counterexample ID, planned write paths, required red/green or verification evidence, handoff location, and closeout rule. Vague goals such as "investigate", "continue", "fix failures", "clean up", or "see what breaks" are read-only discovery until planning turns them into an approved charter.
- One session binds to one feature scope at a time. Claim scopes through owner fields and release them by closing out progress, per `references/00-orchestration-policy.md`; parallel features run in parallel sessions.
- At planning, refactor, implementation, and review stages, read `references/00-orchestration-policy.md` when local subagent tools exist and the task is non-trivial, separable, risky, or validation-heavy.
- Load one stage reference at a time. Do not read all files in `references/` unless the user explicitly asks for a full audit or migration.
- Load support references only when the selected stage asks for them or the evidence triggers their topic.
- Return to `00-progress-router.md` after a meaningful contract, implementation-batch, or evidence checkpoint. Do not re-route merely to manufacture an optional artifact or to mirror unchanged state.
- If evidence is contradictory, read `references/99-status-and-evidence.md`, reconcile the state, then return to the router.
- If a risk-triggered stage requires user confirmation, stop at the gate and report the exact behavior or safety decision needed; do not pause for reversible internal design choices.
- Treat the original workflow document, if present, as source material only. Prefer the split reference documents for execution.

## Reference Map

This map is an index for discovery only. Stage selection must go through `00-progress-router.md`.

- `00-progress-router.md`: determine current stage and next document.
- `00-orchestration-policy.md`: keep the main thread as orchestrator and use subagents as scoped executors.
- `00-refactor-intake.md`: re-check requirements before refactoring and classify behavior risk.
- `00-project-kickoff.md`: initialize architecture, glossary, governance, and workflow state.
- `00-pacing-mode.md`: default to incremental delivery and use blueprint batching only by explicit, justified opt-in.
- `00-business-taxonomy.md`: place requests on the product/module/feature/use-case/sub-feature/task hierarchy and map one vertical feature slice across its declared code homes.
- `00-feature-grading-and-splitting.md`: apply the lean readiness test, documentation budget, and risk-triggered expansion rules.
- `00-governance-ci-hooks.md`: set or audit document governance, CI gates, hooks, and scheduled checks.
- `01-project-identification.md`: classify code reality and the amount of reuse scanning needed, usually without a dedicated artifact.
- `02-requirements-capture.md`: preserve raw request, triage similar requirements (merge/revise/new), and produce structured requirements.
- `03-bdd-example-mapping.md`: discover observable rules, examples, and questions with Given/When/Then before interface design.
- `03-requirements-clarification.md`: surface ambiguities and record decisions.
- `03-ambiguity-audit.md`: cold-read the compact contract and record only actual findings or a concise clean result.
- `04-interface-contract.md`: document only material public/runtime boundary deltas and risk-triggered invariants.
- `04-fixtures-and-probes.md`: capture external data through probes and govern contract/counterexample fixtures.
- `05-conflict-scan.md`: map existing production owners, runtime paths, reusable code/tests, and real conflicts before choosing a write seam.
- `06-planning.md`: write the smallest executable, reuse-first code and verification plan, then start implementation when ready.
- `06-test-strategy.md`: map each behavior sparsely to the cheapest trustworthy existing test home and any necessary wiring evidence.
- `07-red-tests.md`: prove an admissible failure through the selected real production node and existing test infrastructure.
- `07-anti-cheat-and-red-replay.md`: verify both red-before-green order and SUT/runtime binding; invalidate wrong-target reds.
- `08-implementation.md`: modify the selected production owner, prove wiring and regressions, and avoid shadow implementations.
- `09-review-and-verification.md`: verify behavior, evidence, UI, and regression scope.
- `09-module-initial-review.md`: perform the independent module-level review.
- `09-integration-acceptance.md`: run real-layer, cross-feature, UI, contract, and E2E acceptance.
- `09-feature-completeness.md`: audit the test matrix and Definition of Done before closing and archiving a feature round.
- `10-change-protocol.md`: handle contract, requirement, or external-behavior changes.
- `10-counterexample-recovery.md`: turn reproducible failures into permanent regression tests.
- `99-status-and-evidence.md`: reconcile evidence at pauses, handoffs, and closeout using one human-maintained status source when needed.

## Default Response Shape

When taking over work, report:

1. Detected stage and whether the work is `READY` for code.
2. Repository evidence used, including existing production and test anchors for existing-code work.
3. Frozen behavior or the one concrete blocker; list optional documents only when their risk trigger applies.
4. Immediate code/test action and the verification command or evidence expected.
5. Orchestration decision when relevant: executor scopes delegated, or a concise reason for direct execution.

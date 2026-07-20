# Progress Router

Use this file first. Its job is to select the smallest next reference to read.

## Evidence Scan

Inspect, when available:

- the current user request, especially refactor, cleanup, restructure, rewrite, simplification, delegation, parallel, or multi-agent wording
- whether a local multi-agent/subagent tool is present in the active tool list
- module boundaries, executor-sized tasks, independent review tasks, and any work that can safely be delegated
- active worktrees, branches, executor owner fields, handoff notes, uncommitted changes, and unmerged executor output for the same feature or micro-batch
- suspected bugs, failing tests, or design smells discovered outside the accepted feature scope, and whether they block current contract evidence
- proposed worktree purpose, target requirement/bug ID, approved write set, expected evidence, and closeout rule
- for existing code: the current production owner, runtime entry/registration path, nearest existing test suite and runner, reusable fixtures/helpers/fakes, and the baseline test result
- `docs/architecture.md`, `docs/glossary.md`, `docs/requirements-index.md`, `docs/domain-models.md`
- `docs/<module>/00-模块概述.md` for module boundaries
- the feature's active round `docs/<module>/<feature>/<round>/`: `00-*.md`, `01-*.md`, `02-*.md`, `99-进度.md`; `archive/` holds past rounds' frozen truth
- the round's `00-行为示例.md` or lightweight `## BDD 行为示例`, including `R/EX` traceability and pending questions
- the round's `use-cases/*.md`, `interfaces/*.md`, and `conflicts/*.md` for split use cases and contracts
- the round's `02-测试矩阵.md`, `09-集成验收.md`, and `09-完整性审计.md`
- declared frontend, shared-contract, backend, adapter, and E2E code homes for the feature slice
- `docs/workflow-state.json` (including its `mode` field), `docs/<module>/<feature>/status.json` (including `activeRound`)
- tests, recent diffs, PR descriptions, CI results, and review comments

Do not assume status files are authoritative. Prefer Git/PR/CI/test evidence when they conflict.

Evidence may live in the current request, an issue, an existing feature document, or a compact `00-功能.md`; a missing standalone file is not itself a workflow gap. For lean work, one compact source may hold the structured requirement, BDD examples, changed boundary clauses, executable plan, and sparse verification map.

## Positive READY Gate

Evaluate this before routing by missing artifacts. Work is `READY` for code when all are true:

1. Observable behavior and non-goals are clear enough to distinguish success from failure.
2. No unresolved choice would change user-visible behavior, data meaning, external compatibility, irreversible effects, security/compliance posture, or accepted scope.
3. Any changed public API, event/schema, persistence meaning, or state transition is explicit; unchanged boundaries can be inherited from existing code and contracts.
4. Existing-code work names the production owner/runtime path and the nearest existing test home; new work names the intended runtime integration point.
5. At least one credible verification path exists for each changed behavior, with wiring/assembly evidence when a connection itself can fail.

The user's explicit request to implement counts as confirmation when the compact contract is a faithful restatement and no item 2 choice exists. If `READY`, route to code-reality planning, an admissible red, or implementation. Do not route backward merely because an optional document, approval timestamp, matrix cell, or status mirror is absent.

Expand beyond the lean path only for a named risk: contradictory intent; public or external compatibility; unknown third-party behavior; irreversible migration or money/permission effects; security/privacy/compliance; concurrency, idempotency, distributed consistency, or a complex state machine; cross-owner events/shared models; safety-critical behavior; or genuinely independent multi-owner delivery. Read `00-feature-grading-and-splitting.md` for the expansion and budget rules.

## Stage Selection Table

| Evidence | Current stage | Read next |
|---|---|---|
| A same-feature executor/worktree/branch is active, unmerged, uncommitted, lacks a handoff, or its document/status changes are not reconciled | Orchestration closeout | `00-orchestration-policy.md` |
| A writable worktree/executor is requested but no concrete feature, micro-batch, bug/counterexample ID, write set, expected evidence, or closeout rule is defined | Worktree charter missing | `00-orchestration-policy.md`, then route to planning/status instead of opening it |
| A new repository explicitly adopts project-wide workflow governance and lacks a decision needed for the first vertical slice | Minimal project kickoff | `00-project-kickoff.md` |
| The user explicitly requests blueprint batching, or multiple owners require a shared pre-implementation freeze | Pacing mode | `00-pacing-mode.md` |
| A named risk may require more than the lean budget or a split contract | Risk grading | `00-feature-grading-and-splitting.md` |
| User asks to refactor/cleanup/restructure/rewrite/simplify, or a plan selects refactor-before-implementation | Refactor intake | `00-refactor-intake.md` |
| Governance or CI strength is questioned, or a change weakens the guardrails themselves (CI workflows, hooks, audit scripts, CODEOWNERS) or edits existing fixtures against append-only rules | Governance audit | `00-governance-ci-hooks.md` |
| Whether existing behavior/structure must be reused is genuinely unclear after a quick repository scan | Project identification | `01-project-identification.md` |
| New request overlaps or resembles an existing feature's requirement | Similarity triage | `02-requirements-capture.md` |
| Observable behavior is not captured in a structured requirement | Requirements capture | `02-requirements-capture.md` |
| Structured behavior exists but concrete Given/When/Then examples are absent or stale | BDD Example Mapping | `03-bdd-example-mapping.md` |
| A real unresolved question would change observable behavior or a material safety boundary | Clarification gate | `03-requirements-clarification.md` |
| The compact requirement/BDD bundle has not received a cold-read proportionate to its risk | Ambiguity audit | `03-ambiguity-audit.md` |
| A material public/runtime boundary changes and the delta is not explicit in existing contracts or the compact bundle | Interface contract delta | `04-interface-contract.md` |
| Contract uses external service examples, protocol samples, or mock data without matching captures in `docs/<module>/<feature>/fixtures/contract/` | Fixtures and probes | `04-fixtures-and-probes.md` |
| Existing-code work does not yet identify the current production owner, runtime path, reuse candidates, nearest existing test home, or real conflict | Code reality and reuse scan | `05-conflict-scan.md` |
| The compact contract is ready but no executable reuse-first write/test plan names the production node and verification command | Planning | `06-planning.md` |
| A named risk requires expanded coverage, but the sparse verification map does not yet prove the risky connection or invariant | Risk-triggered test strategy | `06-test-strategy.md` |
| An executable plan contains a material behavior/safety/compatibility decision the user has not made | Combined decision gate | Ask the exact decision, record it in the owning compact contract, then return to `06-planning.md` |
| The next changed behavior lacks an admissible failure through its approved production node and existing test infrastructure, and the batch is not a pure refactor | Red tests | `07-red-tests.md` |
| Test/implementation commits need audit or red proof is suspect | Anti-cheat/red replay | `07-anti-cheat-and-red-replay.md` |
| An admissible red exists and implementation is incomplete, refactor intake classified the batch as pure refactor, or the remaining scope is visual-track only | Implementation | `08-implementation.md` |
| Implementation exists but evidence is incomplete | Review and verification | `09-review-and-verification.md` |
| A risk-triggered or independently owned module claims done but independent review is missing | Module initial review | `09-module-initial-review.md` |
| A connection risk, cross-feature effect, persistence truth, public contract, or critical UI path lacks real-layer evidence | Integration acceptance | `09-integration-acceptance.md` |
| High-risk/governed work has integration evidence but still needs a final independent evidence reconciliation | Feature completeness | `09-feature-completeness.md` |
| Reproducible bug, property-test seed, fuzz failure, or mutant survivor affects the accepted feature contract or blocks current evidence | Counterexample recovery | `10-counterexample-recovery.md` |
| Reproducible bug or failing test is outside the accepted feature scope and does not block current evidence | Scope quarantine | Record as out-of-scope finding in progress/status; keep routing the current feature |
| Requirement/contract drift or external behavior changed | Change protocol | `10-change-protocol.md` |
| The selected human-maintained status source contradicts Git/test/CI evidence at a pause, handoff, or closeout | State reconciliation | `99-status-and-evidence.md` |
| Planned behavior and required risk evidence pass, the production runtime selects the changed owner, and status (when used) is consistent | Feature closeout | Sync the one selected status source per `99-status-and-evidence.md`, report completion, and stop |

## Lean Fast Path

For an authorized ordinary change, prefer this continuous path:

```text
raw source + concise structured behavior + BDD examples
→ actual-question clarification only
→ one cold read (findings or concise clean result)
→ freeze compact behavior contract
→ existing-code owner/runtime/test-home scan
→ smallest executable plan and sparse verification map
→ admissible red → green → refactor
→ targeted regression and wiring evidence
→ one closeout update
```

Contract freeze, planning, red, and implementation may occur in the same run. A clean audit, an empty risk category, or the absence of an optional file never creates another user gate. If a test against the actual production owner is unexpectedly green, treat it as existing behavior evidence or sharpen the behavioral difference; never create a parallel SUT merely to manufacture red.

## Orchestration Overlay

Subagent availability does not select the workflow stage. After choosing the stage, decide whether to load `00-orchestration-policy.md`.

Load it when the task is non-trivial and any of these are true:

- local subagent tools are available;
- the work has executor-sized modules, tests, reviews, probes, or audits;
- independent evidence would reduce risk;
- the main thread would otherwise start implementing while also trying to coordinate.

In orchestrated mode, the current conversation is the orchestrator. It may inspect state, plan, launch executors, monitor outputs, integrate results, resolve conflicts, run final verification, and report to the user. It must not simultaneously implement the same delegated scope.

Before launching another executor/worktree for a feature, run the closeout gate in `00-orchestration-policy.md`. If a previous loop has not been integrated into the current document set and Git evidence, route to orchestration closeout and then `99-status-and-evidence.md` before selecting the next implementation loop.

Before opening any writable worktree, require the worktree charter in `00-orchestration-policy.md`. If the request is exploratory or vague, use a read-only executor/discovery pass in the current workspace and return to planning before code edits.

## Tie Breakers

- If multiple stages match, choose the earliest unresolved material risk, not the earliest missing artifact. Orchestration closeout and real safety/behavior blockers outrank readiness; optional documentation never does.
- If the user explicitly asks for a later-stage task, check earlier evidence only for substantive blockers. Skip missing optional documents and do not report them as prerequisites.
- If refactor is requested, run refactor intake before code changes even when the repository appears to be at implementation or review. Never record the refactor as a new feature or requirement.
- If an incoming request resembles an existing feature, run the similarity triage in `02-requirements-capture.md` before creating a new source of truth: one requirement owns one behavior source.
- If clarification changes an accepted rule, example, precondition, outcome, or failure bottom line, route back to `03-bdd-example-mapping.md` before ambiguity audit or contract work.
- If refactor intake classified the batch as pure refactor, skip `07-red-tests.md`: route to `08-implementation.md` with the existing green protection suite and its baseline evidence.
- Red/green work advances one behavior-sized micro-batch at a time, but several ready micro-batches may continue in the same run. Re-route when evidence changes the contract/scope or at a meaningful checkpoint, not after every green test solely to update documents.
- A micro-batch is not finished just because an executor returned or a worktree exists. Treat it as unfinished until the orchestrator has integrated or rejected code/test/doc changes, run verification, recorded the handoff in the selected status surface when one exists, and released or advanced ownership.
- Do not route every discovered bug into repair. If the bug is outside the accepted behavior and not needed to prove current verification, quarantine it as a follow-up or blocker note. If fixing it would expand behavior, architecture, or ownership, use `10-change-protocol.md` before editing.
- If local subagent tools are present, make an orchestration decision after stage selection. Do not treat tool availability alone as a stage or as permission for the main thread and executors to work on the same scope in parallel.
- If the repository has no workflow docs and the user has not asked for project-wide governance, do not bootstrap it. Use the lean compact contract in the current issue/conversation or one existing project document and begin the first vertical slice when ready.

## Output

State the detected stage, `READY` result, decisive evidence (including production/test anchors for existing code), selected next reference, and immediate code/test action or exact blocker before making changes.

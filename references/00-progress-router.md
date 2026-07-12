# Progress Router

Use this file first. Its job is to select the smallest next reference to read.

## Evidence Scan

Inspect, when available:

- the current user request, especially refactor, cleanup, restructure, rewrite, simplification, delegation, parallel, or multi-agent wording
- whether a local multi-agent/subagent tool is present in the active tool list
- module boundaries, executor-sized tasks, independent review tasks, and any work that can safely be delegated
- `docs/architecture.md`, `docs/glossary.md`, `docs/requirements-index.md`, `docs/domain-models.md`
- `docs/features/<feature>/00-*.md`, `01-*.md`, `02-*.md`, `99-进度.md`
- `docs/features/<feature>/interfaces/*.md` and `conflicts/*.md` for split contracts
- `docs/workflow-state.json` (including its `mode` field), `docs/features/<feature>/status.json`
- tests, recent diffs, PR descriptions, CI results, and review comments

Do not assume status files are authoritative. Prefer Git/PR/CI/test evidence when they conflict.

For lightweight features, the matching sections inside `00-功能.md` count as the structured requirement, contract, and plan artifacts when the table below asks whether those exist.

## Stage Selection Table

| Evidence | Current stage | Read next |
|---|---|---|
| New repository lacks architecture, glossary, governance, or workflow state, and the user has confirmed adopting this workflow | Project kickoff | `00-project-kickoff.md` |
| Workflow docs exist but no pacing mode is recorded, or `mode` is `blueprint` and the current batch gate for the work at hand is unverified | Pacing mode | `00-pacing-mode.md` |
| Feature size/path is unclear | Feature grading | `00-feature-grading-and-splitting.md` |
| User asks to refactor/cleanup/restructure/rewrite/simplify, or a plan selects refactor-before-implementation | Refactor intake | `00-refactor-intake.md` |
| Governance or CI strength is questioned, or a change weakens the guardrails themselves (CI workflows, hooks, audit scripts, CODEOWNERS) or edits existing fixtures against append-only rules | Governance audit | `00-governance-ci-hooks.md` |
| No feature folder or no project classification | Project identification | `01-project-identification.md` |
| New request overlaps or resembles an existing feature's requirement | Similarity triage | `02-requirements-capture.md` |
| Raw request exists but no structured requirement | Requirements capture | `02-requirements-capture.md` |
| Structured requirement has unresolved questions | Clarification gate | `03-requirements-clarification.md` |
| Requirement or contract draft needs independent cold-read before approval | Ambiguity audit | `03-ambiguity-audit.md` |
| Requirement is accepted but no behavior contract exists | Interface contract | `04-interface-contract.md` |
| Contract uses external service examples, protocol samples, or mock data without matching captures in `docs/features/<feature>/fixtures/contract/` | Fixtures and probes | `04-fixtures-and-probes.md` |
| Existing code may overlap or contradict the contract, and `01-代码冲突与重叠.md` is missing or does not cover the contract | Conflict scan | `05-conflict-scan.md` |
| Contract/conflict notes exist but no implementation plan | Planning | `06-planning.md` |
| Plan exists but no failing target tests are proven, and the batch is not a pure refactor | Red tests | `07-red-tests.md` |
| Test/implementation commits need audit or red proof is suspect | Anti-cheat/red replay | `07-anti-cheat-and-red-replay.md` |
| Red tests exist and implementation is incomplete, or refactor intake classified the batch as pure refactor | Implementation | `08-implementation.md` |
| Implementation exists but evidence is incomplete | Review and verification | `09-review-and-verification.md` |
| One module claims done but independent review is missing | Module initial review | `09-module-initial-review.md` |
| All modules pass review but end-to-end evidence is missing | Integration acceptance | `09-integration-acceptance.md` |
| Reproducible bug, property-test seed, fuzz failure, or mutant survivor exists | Counterexample recovery | `10-counterexample-recovery.md` |
| Requirement/contract drift or external behavior changed | Change protocol | `10-change-protocol.md` |
| Status, progress, and evidence disagree | State reconciliation | `99-status-and-evidence.md` |
| Integration acceptance passed, regression capture per the integration report is complete, and status is consistent | Feature closeout | Sync state per `99-status-and-evidence.md`, report completion, and stop |

## Orchestration Overlay

Subagent availability does not select the workflow stage. After choosing the stage, decide whether to load `00-orchestration-policy.md`.

Load it when the task is non-trivial and any of these are true:

- local subagent tools are available;
- the work has executor-sized modules, tests, reviews, probes, or audits;
- independent evidence would reduce risk;
- the main thread would otherwise start implementing while also trying to coordinate.

In orchestrated mode, the current conversation is the orchestrator. It may inspect state, plan, launch executors, monitor outputs, integrate results, resolve conflicts, run final verification, and report to the user. It must not simultaneously implement the same delegated scope.

## Tie Breakers

- If multiple stages match, choose the earliest incomplete gate.
- If the user explicitly asks for a later-stage task, still check earlier gates for blockers and report any missing prerequisite.
- If refactor is requested, run refactor intake before code changes even when the repository appears to be at implementation or review. Never record the refactor as a new feature or requirement.
- If an incoming request resembles an existing feature, run the similarity triage in `02-requirements-capture.md` before creating any new feature folder: one requirement owns one document set.
- If refactor intake classified the batch as pure refactor, skip `07-red-tests.md`: route to `08-implementation.md` with the existing green tests as protection evidence.
- If local subagent tools are present, make an orchestration decision after stage selection. Do not treat tool availability alone as a stage or as permission for the main thread and executors to work on the same scope in parallel.
- If the repository has no workflow docs and the user has not asked for this workflow, do not bootstrap governance uninvited: confirm adoption first, and until then start with project identification and the minimum folder/doc structure the current task needs.

## Output

State the detected stage, evidence, and selected next reference before making changes.

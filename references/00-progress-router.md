# Progress Router

Use this file first. Its job is to select the smallest next reference to read.

## Evidence Scan

Inspect, when available:

- `docs/architecture.md`, `docs/glossary.md`, `docs/requirements-index.md`
- `docs/features/<feature>/00-*.md`, `01-*.md`, `02-*.md`, `99-进度.md`
- `docs/workflow-state.json`, `docs/features/<feature>/status.json`
- tests, recent diffs, PR descriptions, CI results, and review comments

Do not assume status files are authoritative. Prefer Git/PR/CI/test evidence when they conflict.

## Stage Selection Table

| Evidence | Current stage | Read next |
|---|---|---|
| New repository lacks architecture, glossary, governance, or workflow state | Project kickoff | `00-project-kickoff.md` |
| Feature size/path is unclear | Feature grading | `00-feature-grading-and-splitting.md` |
| No feature folder or no project classification | Project identification | `01-project-identification.md` |
| Raw request exists but no structured requirement | Requirements capture | `02-requirements-capture.md` |
| Structured requirement has unresolved questions | Clarification gate | `03-requirements-clarification.md` |
| Requirement or contract draft needs independent cold-read before approval | Ambiguity audit | `03-ambiguity-audit.md` |
| Requirement is accepted but no behavior contract exists | Interface contract | `04-interface-contract.md` |
| Contract uses external service examples, protocol samples, or mock data | Fixtures and probes | `04-fixtures-and-probes.md` |
| Existing code may overlap or contradict the contract | Conflict scan | `05-conflict-scan.md` |
| Contract/conflict notes exist but no implementation plan | Planning | `06-planning.md` |
| Plan exists but no failing target tests are proven | Red tests | `07-red-tests.md` |
| Test/implementation commits need audit or red proof is suspect | Anti-cheat/red replay | `07-anti-cheat-and-red-replay.md` |
| Red tests exist and implementation is incomplete | Implementation | `08-implementation.md` |
| Implementation exists but evidence is incomplete | Review and verification | `09-review-and-verification.md` |
| One module claims done but independent review is missing | Module initial review | `09-module-initial-review.md` |
| All modules pass review but end-to-end evidence is missing | Integration acceptance | `09-integration-acceptance.md` |
| Reproducible bug, property-test seed, fuzz failure, or mutant survivor exists | Counterexample recovery | `10-counterexample-recovery.md` |
| Requirement/contract drift or external behavior changed | Change protocol | `10-change-protocol.md` |
| Status, progress, and evidence disagree | State reconciliation | `99-status-and-evidence.md` |

## Tie Breakers

- If multiple stages match, choose the earliest incomplete gate.
- If the user explicitly asks for a later-stage task, still check earlier gates for blockers and report any missing prerequisite.
- If the repository has no workflow docs yet, start with project identification and create the minimum folder/doc structure needed.

## Output

State the detected stage, evidence, and selected next reference before making changes.

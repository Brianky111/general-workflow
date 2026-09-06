# Feature Grading and Splitting

## Purpose

Choose the lightest workflow that closes a named Delivery Anchor gap safely. Default to an incremental lean path; add documents and gates only for a risk already mapped to the original/accepted outcome, including a repository governance rule predeclared as minimum evidence for that outcome.

## Entry Conditions

- A feature or change starts.
- The agent must decide whether the core contract is enough to implement.
- A concrete compatibility, migration, security, concurrency, state-machine, or ownership risk mapped to the selected original/accepted outcome may require a dedicated artifact. An agent-imagined concern without that mapping is optional assurance/follow-up, not an entry condition.

## Lean Core Contract

For an ordinary feature, the sufficient contract is:

1. the immutable durable original source plus explicitly accepted deltas — a task, issue, message, attachment, or a short preserved excerpt; preserve history and do not copy it into a new file when a stable source already exists;
2. concise structured requirements — goal, non-goals, scope, changed public/data behavior, and blocking assumptions;
3. BDD behavior examples — inline by default, using stable acceptance IDs and concrete Given/When/Then outcomes.

The structured requirement and BDD examples may share one file. This core contract replaces separate interface, conflict, test-matrix, and status artifacts unless a risk trigger below requires one. Code-native schemas and tests may be the detailed technical truth when they do not introduce an unresolved product choice.

## READY Check

For the selected `request_gap`, freeze the core contract and proceed when all are true:

- observable outcomes and non-goals are clear;
- no unresolved question can change user-visible behavior, external compatibility, data meaning, security posture, or an irreversible effect;
- changed public interfaces, schemas, state transitions, or persistence semantics are explicit, or the contract states that none change;
- the intended write boundary and any concrete existing-code conflict are understood well enough to avoid scope drift;
- every acceptance behavior has a credible verification approach;
- every anchor-linked risk exception, including any governance rule predeclared as minimum evidence for this outcome, has the smallest finite necessary treatment.

When the user already authorized the work and the core contract is a faithful restatement, that authorization is sufficient: do not ask the user to confirm the same intent again. Record the freeze in the contract or its source reference and continue into planning, tests, and implementation in the same run. If implementation reveals a behavior change, reopen only the affected clause through `10-change-protocol.md`.

## Default Document Budget

Before code, default to:

- at most two new artifacts;
- at most 160 nonblank Markdown lines across them;
- at most one human pause;
- documentation work no more than 20% of expected task effort or 30 minutes, whichever limit is reached first.

Reuse or amend an existing artifact before creating another. Exceed the budget only by naming the risk exception, the decision or evidence the extra material enables, and why a smaller section is insufficient. Template completeness, repository age, module count, subagent availability, or a desire to be exhaustive are not exceptions.

## Risk-Triggered Expansion

Add only the artifact or section named by the risk:

- **Public or external compatibility:** a dedicated interface contract and compatibility/consumer evidence.
- **Unknown external protocol:** probes, captured fixtures, and explicit failure/retry semantics.
- **Migration or irreversible data effects:** migration, rollback, and recovery decisions with a human gate.
- **Security, privacy, compliance, payment, or other high-cost effects:** the relevant threat, approval, and audit evidence.
- **Concurrency, idempotency, distributed consistency, or a complex state machine:** invariants, transition/event ownership, and focused adversarial tests.
- **Cross-owner shared schemas, events, or state:** an ownership/interface artifact and cross-feature verification.
- **Concrete legacy conflict or uncertain migration boundary:** a conflict appendix covering the actual locations and chosen handling; an old repository alone does not require an empty report.
- **Long-running multi-owner delivery, formal audit, or regulated traceability:** one explicit status/evidence source and any required trace table.

An exception does not upgrade the whole feature to every standard artifact or add behavior to the Delivery Anchor. Expand only the affected anchor boundary and return to its selected incomplete outcome, then re-evaluate the anchor before any further stage.

## Splitting

Keep the core contract together. Split a dedicated contract only when independent owners or reviewers need separate approval boundaries, an external protocol needs isolated fixtures/failure semantics, or the risk-specific material would exceed the document budget. Parallel execution or three modules alone is not a reason to duplicate documents.

When splitting, keep one index that points to authoritative sections; never define the same behavior or schema twice. Shared entities remain in the project shared-model source when one exists.

## Output

Record `lean` or the named risk-triggered expansion at the head of the core contract. Record only budget exceptions and their reasons; do not create a grading document or ask for a grading-only confirmation.

## Stop Conditions

Stop only for a real decision that blocks the selected original/accepted outcome: observable behavior, compatibility, data meaning, security, irreversible effects, or ownership. Otherwise complete the READY check and continue in the same run. A theoretical or unanchored risk is recorded as follow-up and cannot block `ANCHOR-SATISFIED`.

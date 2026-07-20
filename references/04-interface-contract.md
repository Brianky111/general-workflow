# Interface Contract

## Purpose

Document a public or high-risk boundary only when the lean core contract is not sufficient. An ordinary feature's durable source, structured requirement, and BDD examples already form its behavior contract.

## Entry Conditions

Create or extend a dedicated interface contract only when at least one risk applies:

- public API, event, SDK, file format, or external compatibility changes;
- an unknown external protocol needs probes, fixtures, retry, or failure semantics;
- a migration or irreversible data effect needs before/after and rollback rules;
- security, privacy, compliance, payment, or another high-cost boundary needs explicit review;
- concurrency, idempotency, distributed consistency, or a complex state machine needs invariants;
- shared schemas, events, or state cross feature/team/owner boundaries.

Repository age, multiple internal modules, or a desire to show every layer is not an entry condition. When no trigger exists, keep changed interface details inside the core contract or code-native schema and return to the READY check.

## Actions

Document only the affected boundary:

1. State the relevant acceptance IDs and changed observable behavior.
2. Define changed commands, endpoints, events, files, or runtime schemas with units, casing, enums, nullability, versions, and error forms where compatibility depends on them.
3. Define only the applicable state transitions, ownership, idempotency, timing, migration, rollback, or security invariants.
4. Use one representative input/output/failure example for each changed public method or message; do not duplicate unchanged code-native definitions.
5. Link producer and consumer evidence, fixtures, or probes when an external/shared boundary exists.
6. Record the implementation write boundary and any cross-owner responsibility needed to prevent scope drift.
7. Reuse the core acceptance IDs. Do not create a second full behavior map or repeat the same example through every absent layer.

For external-system uncertainty, read `04-fixtures-and-probes.md`. Split the contract only when independent owners or reviewers require distinct approval boundaries or the risk-specific material cannot fit the document budget.

## Revision Shape

Write a delta by default: changed clauses, compatibility impact, preserved behavior, and required verification. Keep the previous accepted contract as history.

Write a complete snapshot only when public compatibility tooling, a consumer-facing specification, formal audit, or regulation requires an authoritative full version. Record that exception and why a delta is insufficient.

## Contract Freeze

Run the targeted `03-ambiguity-audit.md` check. A clean audit plus a faithful restatement of work the user already authorized freezes the contract without another confirmation.

Use the one allowed human pause only when the interface introduces a real unresolved choice about user-visible behavior, compatibility, data meaning, migration, security, irreversible effects, or ownership. Combine that decision with any other pre-code questions; do not add a contract-review ceremony after the same answer is recorded.

Once the triggered risk is resolved, apply the READY check in `00-feature-grading-and-splitting.md` and continue into planning, tests, and implementation in the same run. A missing dedicated interface file is not a blocker when no trigger applies.

## Output

- Ordinary feature: no separate output; keep the changed boundary in the core contract or authoritative code schema.
- Risk-triggered feature: one focused interface section or `01-接口.md`, within the default two-artifact/160-line budget unless the named exception justifies more.
- Revision: a delta unless compatibility or audit requires a complete snapshot.

## Stop Conditions

Stop only for an unresolved material interface decision or missing real-world evidence that makes the boundary unsafe to freeze. Missing exhaustive UI states, four-question forms, full-stack walkthroughs, or a document-PR gate do not block ordinary implementation.

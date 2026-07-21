# Change Protocol

## Purpose

Change the current Delivery Anchor state by appending an accepted delta, without rewriting the original request or earlier accepted history. Revalidate only the affected projections and return to implementation quickly.

## Entry Conditions

- The user changes intent or extends an accepted behavior.
- An accepted authoritative product/public contract source changes.
- An external-drift candidate outside an existing compatibility promise is explicitly accepted as a delta.
- Similarity triage classifies a request as a revision of an existing feature.

An implementation/test mismatch or drift covered by an existing compatibility promise means that same anchor outcome is unmet; repair it without changing the Anchor. A finding that merely suggests the accepted clause should change remains a candidate until one of the entry conditions above authorizes a delta.

## Actions

1. Append the new durable source to the existing Delivery Anchor history and identify the affected acceptance IDs or contract clauses. Never edit or replace the original source or earlier accepted deltas.
2. Record the accepted delta and effective Anchor transition: what changes, what remains stable, compatibility impact, and the finite verification obligations added, removed, or superseded. Use existing source/delta references; do not invent an Anchor ID system.
3. Update only the affected structured requirement, BDD example, interface clause, and `TOS` rows as faithful projections of the new current Anchor state. Keep unaffected closed obligations closed; do not rerun or rewrite unaffected stages.
4. Route each changed behavior/public/data clause to exactly one owning feature. Update a compact solution frame only when the aggregate outcome/non-goals, participant/owner map, dependency order, rollout/rollback, or aggregate proof changes; never copy child-feature behavior into the solution.
5. Preserve prior accepted evidence, counterexamples, and superseded projections as history where the repository already keeps that history.
6. Run a targeted ambiguity audit, apply READY, and continue into tests and implementation in the same run when no real blocking choice remains.

The user's explicit change request or an accepted authoritative product/contract update authorizes a faithful delta and updates only the current effective Anchor state. External drift outside an existing compatibility promise does so only after explicit acceptance; inside that promise it is evidence against the same outcome, not a delta. A reviewer, test/discovery tool, executor, or orchestrator cannot self-accept expansion by relabeling a finding as a named risk. Such a finding cannot enter Anchor history or expand scope. Do not require a second change-proposal approval that merely restates an authoritative delta. Ask once only when implementation requires a materially different product, compatibility, data, security, irreversible-effect, or ownership decision.

## Levels

- **Level A: observable behavior, public contract, architecture, or named-risk delta.** Update the affected core contract and append only its finite `TOS` delta. Use one combined human pause only for an unresolved material choice. A new round, full document snapshot, or reopening of unaffected tests is not automatic.
- **Level B: bug fix or admitted counterexample repayment without intended contract change.** Reuse an existing failing test when it captures the defect; otherwise admit at most one representative regression obligation under the declared cap, fix to green, and link evidence. If the fix changes accepted behavior, upgrade only the affected clause to level A.
- **Level C: pure display adjustment.** Change style, copy, or layout with appropriate visual evidence. Any logic change upgrades to B or A.

**Probe exception:** a disposable probe may verify one uncertain external question without a change proposal only under `04-fixtures-and-probes.md`'s frozen probe ID, request/attempt, wall-clock, sanitization, and no-reset limits. Store the one selected shareable capture under the project's fixture convention when it becomes contract evidence; discard probe-only implementation code. A probe result may justify an authoritative delta, but cannot itself start another probe/test campaign or reopen a closed delivery.

For candidate reproducible bugs, property-test seeds, fuzz failures, integration red scenarios, or mutation survivors, read `10-counterexample-recovery.md` to deduplicate and apply the frozen admission cap before adding any obligation.

## Delta and Snapshot Policy

Default to an append-only delta reference in the existing core contract, change note, issue, or PR. The original source plus ordered accepted deltas remains the Delivery Anchor history; derived snapshots show current effective behavior but never replace that history. Open a new round only when independent ownership, long-running handoff, or audit history needs it.

Maintain one current effective contract per feature. Consolidate an accepted delta by changing only the affected clauses and their projections; do not concatenate complete historical snapshots or force readers through a chain of rounds to learn current behavior. Keep design choices, test/governance procedures, and optional robustness findings outside user requirements unless an accepted delta actually changes observable behavior, public/data semantics, compatibility, ownership, or a named safety boundary.

Write a complete post-change snapshot only when public compatibility tooling, external consumers, formal audit, or regulation requires one authoritative full contract. State the named exception before exceeding the default pre-code budget from `00-feature-grading-and-splitting.md`.

## Output

- Ordinary change: one concise Anchor transition linked to the prior accepted source, its new durable delta source, and updated test evidence.
- Risk-triggered change: the smallest focused interface, migration, security, ownership, or traceability addition.
- No duplicate status artifact unless status is independently triggered by `99-status-and-evidence.md`.

## Stop Conditions

Stop only for an unresolved material change decision, unsafe missing external evidence, an Anchor/projection conflict with no authoritative resolution, or an unbounded verification delta. Only an accepted user/authoritative-source delta, or an admitted distinct anchor-falsifying counterexample under the existing delivery cap, may change the frozen `TOS`; a test/review/tool/orchestrator result or unaccepted drift candidate alone cannot change the Anchor or scope. A new discovery campaign or refreshed cap belongs to a new accepted delivery, not a reroute inside this one. After the finite affected delta passes, evaluate `DELIVERY-DONE` and stop. A missing new round, full contract rewrite, or repeated approval is not a blocker.

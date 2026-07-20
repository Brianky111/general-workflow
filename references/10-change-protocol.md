# Change Protocol

## Purpose

Change accepted behavior without silently rewriting history or rebuilding an unaffected document set. Record a focused delta, revalidate the affected contract, and return to implementation quickly.

## Entry Conditions

- The user changes intent or extends an accepted behavior.
- External behavior or a shared/public contract drifts.
- Implementation or a test proves an accepted clause wrong or incomplete.
- Similarity triage classifies a request as a revision of an existing feature.

## Actions

1. Link the new durable source and identify the affected acceptance IDs or contract clauses.
2. Record the delta: what changes, what remains stable, compatibility impact, and required verification.
3. Update only the affected structured requirement, BDD example, interface clause, and test evidence. Do not rerun or rewrite unaffected stages.
4. Preserve prior accepted evidence and counterexamples as history.
5. Run a targeted ambiguity audit, apply READY, and continue into tests and implementation in the same run when no real blocking choice remains.

The user's explicit change request authorizes a faithful delta. Do not require a second change-proposal approval that merely restates it. Ask once only when implementation requires a materially different product, compatibility, data, security, irreversible-effect, or ownership decision.

## Levels

- **Level A: observable behavior, public contract, or architecture delta.** Update the affected core contract and any risk-triggered artifact. Use one combined human pause only for an unresolved material choice. A new round or full document snapshot is not automatic.
- **Level B: bug fix or counterexample repayment without intended contract change.** Write or identify the reproducing red test, fix to green, and link evidence. If the fix changes accepted behavior, upgrade only the affected clause to level A.
- **Level C: pure display adjustment.** Change style, copy, or layout with appropriate visual evidence. Any logic change upgrades to B or A.

**Probe exception:** a disposable probe may verify uncertain external behavior without a change proposal. Store shareable captures under the project's fixture convention when they become contract evidence; discard probe-only implementation code. See `04-fixtures-and-probes.md`.

For reproducible bugs, property-test seeds, fuzz failures, integration red scenarios, or mutation survivors, read `10-counterexample-recovery.md`.

## Delta and Snapshot Policy

Default to a delta in the existing core contract, change note, issue, or PR. Open a new round only when independent ownership, long-running handoff, or audit history needs it.

Write a complete post-change snapshot only when public compatibility tooling, external consumers, formal audit, or regulation requires one authoritative full contract. State the named exception before exceeding the default pre-code budget from `00-feature-grading-and-splitting.md`.

## Output

- Ordinary change: one concise delta linked to the prior accepted source and updated test evidence.
- Risk-triggered change: the smallest focused interface, migration, security, ownership, or traceability addition.
- No duplicate status artifact unless status is independently triggered by `99-status-and-evidence.md`.

## Stop Conditions

Stop only for an unresolved material change decision or unsafe missing external evidence. A missing new round, full contract rewrite, or repeated approval is not a blocker.

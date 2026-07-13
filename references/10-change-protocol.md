# Change Protocol

## Purpose

Handle requirement, contract, fixture, or external-behavior changes without silently rewriting history.

## Entry Conditions

- User changes intent.
- External service behavior drifts.
- Implementation proves the contract is wrong or incomplete.
- Tests or the completeness audit reveal a missing scenario, UI state, cross-feature effect, or assembly contract that changes accepted behavior.
- Similarity triage in `02-requirements-capture.md` classifies a new request as a revision of an existing feature's confirmed requirement.

## Actions

1. Identify the source of change: user intent, code reality, external drift, or test discovery.
2. Record what changes and what remains stable.
3. Update requirements and BDD behavior examples before contracts, tests, or implementation.
4. Preserve old evidence where useful; do not delete counterexamples casually.
5. Re-route to the earliest affected stage after the change is accepted.

## Levels

- **Level A: behavior, contract, or architecture change.** Stop, write a change proposal, wait for approval, then open a new round and update architecture/shared models/requirements/BDD examples/contracts/plans/test matrix/tests/implementation in order.
- **Level B: bug fix or counterexample repayment.** First write a reproducing red test, then fix to green; the fix merges on green CI without a human gate. If the fix proves the contract is wrong, upgrade to level A.
- **Level C: pure display adjustment.** Change only style, copy, or layout; use human visual acceptance and update visual baselines. Any logic change upgrades to B or A.

**Probe exception:** verifying uncertain external behavior with a disposable probe needs no change proposal. The probe's output stored in `fixtures/contract/` becomes the official data source; the probe code itself is discarded, never merged as implementation (see `04-fixtures-and-probes.md`).

For reproducible bugs, property-test seeds, fuzz failures, integration red scenarios, or mutation survivors, read `10-counterexample-recovery.md`.

## Output

Documented change record and updated stage docs.

## Stop Conditions

Stop for confirmation when the change alters user-visible behavior, external compatibility, data meaning, or previous acceptance criteria.

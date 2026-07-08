# Change Protocol

## Purpose

Handle requirement, contract, fixture, or external-behavior changes without silently rewriting history.

## Entry Conditions

- User changes intent.
- External service behavior drifts.
- Implementation proves the contract is wrong or incomplete.
- Tests reveal a missing scenario that changes accepted behavior.

## Actions

1. Identify the source of change: user intent, code reality, external drift, or test discovery.
2. Record what changes and what remains stable.
3. Update requirements or contracts before updating tests or implementation.
4. Preserve old evidence where useful; do not delete counterexamples casually.
5. Re-route to the earliest affected stage after the change is accepted.

## Levels

- **Level A: contract or architecture change.** Stop, write a change proposal, wait for approval, then update architecture/shared models/requirements/contracts/plans/tests/implementation in order.
- **Level B: bug fix or counterexample repayment.** First write a reproducing red test, then fix to green. If the fix proves the contract is wrong, upgrade to level A.
- **Level C: pure display adjustment.** Change only style, copy, or layout; use human visual acceptance and update visual baselines. Any logic change upgrades to B or A.

For reproducible bugs, property-test seeds, fuzz failures, integration red scenarios, or mutation survivors, read `10-counterexample-recovery.md`.

## Output

Documented change record and updated stage docs.

## Stop Conditions

Stop for confirmation when the change alters user-visible behavior, external compatibility, data meaning, or previous acceptance criteria.

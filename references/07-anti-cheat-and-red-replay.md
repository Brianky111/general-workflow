# Anti-Cheat and Red Replay

## Purpose

Make test-first history auditable instead of relying on agent claims.

## Entry Conditions

- Red tests are being committed.
- Implementation changes tests or fixtures.
- A reviewer suspects tests were added after implementation or weakened.

## Commit Discipline

- Red-test commit comes before implementation commit.
- Test commits may touch only test paths and may append new counterexamples.
- Implementation commits normally must not touch tests, `fixtures/contract/`, or `fixtures/counterexamples/`.
- Refactor commits must not change public signatures or tests.

## Red Replay

CI should check out each red-test commit and run the newly added or marked red cases. The expected result is failure for the expected reason, such as `尚未实现` or the target defect. Existing tests must not crash for unrelated reasons.

## Prohibitions

- Do not write implementation first and backfill tests.
- Do not cross hard stops: unanswered questions or unfrozen contracts block later artifacts.
- Do not weaken tests by deleting assertions, loosening expectations, adding `skip`/`only`, or changing expected values to match wrong code.
- Do not hardcode against known test inputs.
- Do not hide failure with fallback defaults, swallowed exceptions, or test-environment branches.

## Legal Paths After Failure

Only two paths are valid:

1. fix the implementation,
2. use `10-change-protocol.md` to change the contract.

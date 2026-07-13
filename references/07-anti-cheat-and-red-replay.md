# Anti-Cheat and Red Replay

## Purpose

Make test-first history auditable instead of relying on agent claims.

## Entry Conditions

- Red tests are being committed.
- Implementation changes tests or fixtures.
- A reviewer suspects tests were added after implementation or weakened.

## Commit Discipline

- Red-test commit comes before implementation commit.
- Apply commit order per behavior-sized micro-batch; do not use one early trivial red commit to excuse later implementation-first batches.
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

## Rationalization Table

Excuses are predictable; rebut them before they win. Following the letter of a rule while violating its spirit is still a violation.

| Excuse | Rebuttal |
|---|---|
| Too simple to need a test | Simple code breaks too; watching the test fail is what proves the test itself works |
| Writing the test afterwards is the same | A test written after passes immediately, and an immediate pass proves nothing |
| We already had one red commit for the feature | TDD evidence is per micro-batch; later behavior still needs its own expected red before green |
| Deleting hours of work is wasteful | Sunk-cost fallacy; code that never went red-then-green is a liability, not an asset |
| It's just a refactor, this tiny behavior tweak is fine | Changed behavior is not a refactor; route to the change protocol |
| This case is flaky, skip it for now | Skip is cheating; fix the environment or stop and report |
| The failure is intermittent, rerunning fixes it | Reproducible means mandatory; a failure with a seed or input goes to counterexample recovery |
| Merge first, backfill evidence later | Status must never run ahead of evidence; without evidence it is not done |

## Legal Paths After Failure

Only two paths are valid:

1. fix the implementation,
2. use `10-change-protocol.md` to change the contract.

## Output

An audit conclusion with evidence: commit order and path purity verified (commit hashes), red replay result (CI link or command output), and any violations found with the rule each one breaks. Then return to the router.

## Stop Conditions

Stop and report to the user if a violation is confirmed (implementation-first history, weakened tests, hardcoded answers, or bypassed stops); do not silently repair audit findings.

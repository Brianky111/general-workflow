# Red Tests

## Purpose

Prove the target behavior fails before implementation.

## Entry Conditions

- Plan identifies tests to add.
- Implementation for the target behavior has not started, or prior implementation must be guarded by new regression tests.

## Actions

1. Add the smallest tests that encode the contract scenarios.
2. Name assertions with scenario IDs (`S1`, `E1`, `B1`) and invariant IDs (`P1`) where applicable.
3. Use `fixtures/contract/` for mocked external data and `fixtures/counterexamples/` for recovered failures.
4. Run only the relevant tests first.
5. Confirm failure reason matches the missing behavior or `尚未实现`, not setup breakage.
6. Record commands, failing output summary, and seed/input values for reproducibility.
7. Do not weaken existing tests or skip unrelated failures without explicit rationale.

Read `07-anti-cheat-and-red-replay.md` before committing red tests.

## Output

Commit or record red-test evidence before implementation. Update progress/status docs with test paths and failure evidence.

## Stop Conditions

Do not implement until the red failure is reproducible or the user explicitly authorizes a non-TDD exception.

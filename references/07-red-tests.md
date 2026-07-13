# Red Tests

## Purpose

Prove one behavior-sized target fails before implementing it. Repeat red -> green -> refactor for each planned micro-batch; do not accumulate the entire feature's red suite before writing any implementation.

## Entry Conditions

- Plan identifies tests to add.
- Implementation for the target behavior has not started, or prior implementation must be guarded by new regression tests.

## Actions

1. Select the next `P:<test-id>` cell or tightly related cells from the Feature Test Matrix; resolve the stable test ID through the evidence register and state the exact behavior and test layer.
2. Add the smallest test that encodes the contract scenario. Name assertions with scenario IDs (`S1`, `E1`, `B1`) and invariant IDs (`P1`) where applicable.
3. At the Domain layer, test rules, values, and legal/illegal state transitions without infrastructure.
4. At the Use Case layer, test inputs/queries, result, required side effects, and forbidden side effects on failure. Prefer Fakes; use Stubs for fixed answers and Mocks/spies only for business-significant interactions or order.
5. At the frontend layer, test user-observable behavior with semantic queries: validation, disabled/in-flight behavior, loading/success/error/retry states, and duplicate submission where applicable.
6. At contract, adapter, cross-feature, or E2E layers, use the fixture/environment declared in the matrix and prove the connection itself is currently missing or wrong.
7. Use `fixtures/contract/` for captured external data and `fixtures/counterexamples/` for recovered failures.
8. Run only the relevant test first and confirm the failure matches the missing behavior or `尚未实现`, not setup breakage.
9. Record command, failing output summary, seed/input, test ID, matrix row, and failure reason for reproducibility. Keep the cell planned until green; attach red evidence in the register or batch status.
10. Do not weaken existing tests or skip unrelated failures without explicit rationale.

Read `07-anti-cheat-and-red-replay.md` before committing red tests.

## Output

Commit or record red-test evidence before implementation. Update the matrix row and progress/status docs with test paths and failure evidence, then route this micro-batch to `08-implementation.md`.

## Stop Conditions

Do not implement until the red failure is reproducible or the user explicitly authorizes a non-TDD exception.

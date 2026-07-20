# Red Tests

## Purpose

Prove one behavior-sized target fails before implementing it. Repeat red -> green -> refactor for each planned micro-batch; do not accumulate the entire feature's red suite before writing any implementation.

## Entry Conditions

- The executable compact plan/test mapping identifies a stable acceptance/test ID, `N-ID`, production owner/entry, nearest existing test home, and reuse assets.
- `NEW`/`REPLACEMENT` targets have recorded reuse rejection evidence, a planned non-test incoming edge, and a planned real-production wiring test; side-by-side targets also have a selection point and retirement condition.
- Implementation for the target behavior has not started, or prior implementation must be guarded by new regression tests.

## Actions

1. Select the next planned test or tightly related tests from the sparse map/risk matrix. Resolve the authoritative acceptance/test ID, behavior, layer, `N-ID`, production entry, and test home through the plan or evidence register.
2. Before editing, run the nearest existing test slice or production probe as the baseline. Record its command/result and inspect the established runner, suite, factories, fixtures, and helpers; extend them by default.
3. Add the smallest test for one accepted behavior or invariant. Reuse its authoritative `AC` or existing ID and bind the `N-ID` in the plan/evidence; do not invent parallel trace IDs merely for the test name.
4. Target the planned production SUT. Unit tests may call the node directly, but its current or planned real runtime reachability must be recorded; assembly tests must enter through the real route, registry, export, or composition root. Fakes/stubs may replace collaborators, never the SUT, production owner, or registration under proof.
5. Do not define a business SUT in test code, target an unregistered parallel implementation, or introduce a second runner/harness/helper system to manufacture red. New test infrastructure needs its own approved conflict/plan item.
6. At Domain/Use Case layers, prove the rule, result, required effects, and forbidden effects. At frontend and connection layers, prove user-visible behavior or the declared contract/adapter/wiring failure using the matrix fixture/environment.
7. Use `fixtures/contract/` for captured external data and `fixtures/counterexamples/` for recovered failures.
8. Run the relevant test first. An admissible red fails through the intended `N-ID` for the missing behavior, target defect, or approved `尚未实现` stub—not because of discovery, compilation, setup, fixture, wrong-SUT, or missing unplanned registration.
9. If the test passes immediately against the real owner, record `UNEXPECTED-GREEN:<test-id>` and stop. Do not retarget a new SUT or falsify an assertion to force red; determine whether existing behavior/evidence should become `PASS` or whether planning must define a genuinely distinguishing case.
10. If the test hits the wrong SUT, an unregistered replacement, a stale topology node, or setup/harness failure, record `INVALID-RED:<test-id>`, do not implement, and route back to `05-conflict-scan.md`, planning, or the test mapping as appropriate.
11. For an admissible red, record baseline, command, failing output, seed/input, test ID, matrix row, `N-ID`, production entry, existing test home/reuse assets, and exact failure reason in the commit, CI artifact, or executor handoff. Keep coverage planned until green.
12. Do not weaken existing tests or skip unrelated failures without explicit rationale.

Read `07-anti-cheat-and-red-replay.md` before accepting or committing red evidence.

## Output

Commit or record admissible red evidence before implementation, then route the micro-batch to `08-implementation.md`. Do not churn matrix/progress documents after each red command; batch evidence at the next planned integration/review/closeout sync unless coverage, ownership, `N-ID`, risk, or blocker changed.

## Stop Conditions

Do not implement until the red failure is reproducible and admissible. `UNEXPECTED-GREEN` means no missing implementation has been proven. `INVALID-RED`, a wrong or parallel SUT/harness, missing reuse rejection evidence, or missing production wiring cannot be waived into valid TDD evidence; return to the real owner and executable plan. A user-authorized non-TDD exception may skip the red-order requirement only when test-first is genuinely impractical—it never waives real `N-ID`, production reachability, reuse, wiring, or regression evidence.

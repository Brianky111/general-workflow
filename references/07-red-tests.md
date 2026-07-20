# Red Tests

## Purpose

Consume one frozen `PENDING` test obligation, or recapture one existing `GAP` obligation with unused aggregate-repair allowance, by proving its target fails before implementation. Repeat red -> green -> refactor only for the finite obligation keys already admitted to the current plan; do not accumulate the entire feature's red suite or discover replacement obligations here.

## Entry Conditions

- The executable compact plan/test mapping contains a finite frozen Test Obligation Set (`TOS`) and identifies one concrete `PENDING` obligation or one `GAP` obligation whose existing finding set has an unused repair/recheck allowance, with its acceptance/test ID, proof kind, `N-ID`, production owner/entry, nearest existing test home, and reuse assets.
- The selected obligation traces through its existing acceptance/contract ID to the plan-level Delivery Anchor and current `request_gap`; the test does not repeat the full source or create a new anchor/gap ID.
- `NEW`/`REPLACEMENT` targets have recorded reuse rejection evidence, a planned non-test incoming edge, and a planned real-production wiring test; side-by-side targets also have a selection point and retirement condition.
- Implementation for the target behavior has not started, or prior implementation must be guarded by new regression tests.

## Actions

1. Select only a `PENDING` obligation or an existing `GAP` obligation with unused aggregate-repair allowance from the frozen `TOS`; never create a new key. Before editing, resolve its inherited plan-level Anchor/gap, authoritative acceptance/test ID, proof kind, behavior, layer, `N-ID`, production entry, and test home. If that trace is absent or the assertion cannot close the gap, record `INVALID-OBLIGATION`, do not write or run a new red, exclude the item from completion/blocker counts, and return to planning/router to select a real unmet gap. If no valid pending/gap obligation exists, evaluate `DELIVERY-DONE` or `BLOCKED` instead of writing another test.
2. Before editing, run the nearest existing test slice or production probe as the baseline. Record its command/result and inspect the established runner, suite, factories, fixtures, and helpers; extend them by default.
3. Add the smallest test that discharges that one accepted obligation and proves the selected `request_gap`. Reuse its authoritative `AC` or existing ID and bind the `N-ID` in the plan/evidence; do not invent a new behavior, gap, obligation, or parallel trace ID merely for the test name. Parameterize equivalent inputs under the same rule/failure bottom line.
4. Target the planned production SUT. Unit tests may call the node directly, but its current or planned real runtime reachability must be recorded; assembly tests must enter through the real route, registry, export, or composition root. Fakes/stubs may replace collaborators, never the SUT, production owner, or registration under proof.
5. Do not define a business SUT in test code, target an unregistered parallel implementation, or introduce a second runner/harness/helper system to manufacture red. New test infrastructure needs its own approved conflict/plan item.
6. At Domain/Use Case layers, prove the rule, result, required effects, and forbidden effects. At frontend and connection layers, prove user-visible behavior or the declared contract/adapter/wiring failure using the matrix fixture/environment.
7. Use `fixtures/contract/` for captured external data and `fixtures/counterexamples/` for recovered failures.
8. Run the relevant test first. An admissible red fails through the intended `N-ID` for the missing behavior, target defect, or approved `尚未实现` stub—not because of discovery, compilation, setup, fixture, wrong-SUT, or missing unplanned registration.
9. If the test passes immediately against the real owner, record `UNEXPECTED-GREEN:<test-id>` with evidence kind `EXISTING-PASS` and mark the same obligation `VERIFIED` when the assertion faithfully proves the selected `request_gap`. Close that gap as an evidence-backed no-op when no authorized write remains for it. Do not retarget a new SUT, invent another edge case, or falsify an assertion to force red. Correct the test once only when the frozen contract already contains a material distinction that this test failed to express.
10. If the test hits the wrong SUT, an unregistered replacement, a stale topology node, or setup/harness failure, record `INVALID-RED:<test-id>`, do not implement, and make at most one mapping/setup correction for the obligation through `05-conflict-scan.md`, planning, or the test mapping. Any later `INVALID-RED` for that obligation is `BLOCKED`, regardless of category; renaming or reclassifying the test, seed, SUT, `N-ID`, or failure does not reset the recorded allowance.
11. For an admissible red, record baseline, command, failing output, seed/input, test ID, matrix row, `N-ID`, production entry, existing test home/reuse assets, and exact failure reason in the commit, CI artifact, or executor handoff. Keep coverage planned until green.
12. Do not weaken existing tests or skip unrelated failures without explicit rationale.
13. Do not derive another obligation from the red output. A distinct failure is only a candidate for the bounded admission rules in `10-counterexample-recovery.md`; duplicate/already-covered failures stay on the current obligation, and out-of-scope failures are quarantined.

Read `07-anti-cheat-and-red-replay.md` before accepting or committing red evidence.

## Output

Commit or record admissible red evidence with the existing obligation/gap ID before implementation, mark the same obligation `RED`, then route it to `08-implementation.md`. An obligation with `EXISTING-PASS` evidence becomes `VERIFIED` without implementation and closes its gap only when no authorized write remains. Do not churn matrix/progress documents after each red command; batch evidence at the next planned integration/review/closeout sync unless ownership, `N-ID`, accepted risk, or blocker changed.

## Stop Conditions

Do not implement until the red failure is reproducible, admissible, and tied to the selected Delivery Anchor gap. `INVALID-OBLIGATION` never enters red and never blocks Delivery Anchor completion. `UNEXPECTED-GREEN` means no missing implementation has been proven and must not trigger a search for another red. `INVALID-RED`, a wrong or parallel SUT/harness, missing reuse rejection evidence, or missing production wiring cannot be waived into valid TDD evidence; correct the same valid obligation once, then stop as `BLOCKED` on any later invalid red, regardless of category. A user-authorized non-TDD exception may skip the red-order requirement only when test-first is genuinely impractical—it never waives the Delivery Anchor, selected `request_gap`, real `N-ID`, production reachability, reuse, wiring, regression evidence, or the finite `TOS` boundary.

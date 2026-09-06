# Implementation

## Purpose

Make red tests pass while staying inside the accepted contract and plan.

## Entry Conditions

- Red tests are admissible and fail for the expected reason, the batch is a pure refactor recertified through `00-refactor-intake.md` with existing green tests as protection evidence, or the module is visual-track (no test phase; evidence is screenshots or previews at acceptance).
- The implementation scope is clear.
- The write batch traces through an existing acceptance/obligation ID to the plan-level Delivery Anchor and exactly one selected `request_gap`. Its declared production effect directly closes that gap; it does not repeat the full source or create a new anchor/gap ID.
- The executable compact plan assigns this implementation a `RED` obligation from the finite frozen `TOS` (or an explicit pure-refactor/visual obligation) and names the stable `N-ID`, current production owner/entry, nearest existing test home/reuse assets, code topology, write set, read-only paths, and any applicable scope firewall.
- A `NEW`/`REPLACEMENT` has recorded reuse rejection evidence, a planned non-test incoming edge, and a planned real-production wiring test; side-by-side work also has a selection point and retirement condition.
- Writable worktree/executor work has an approved charter: purpose, target ID, write set, evidence, handoff, and closeout rule.
- For refactor work, the observable behavior and existing green protection baseline have been recertified through `00-refactor-intake.md`.
- If execution is orchestrated through subagents, the plan defines executor write sets and the main thread is not implementing the same assigned scope.
- No prior executor/worktree loop for the same feature, module, or micro-batch is awaiting handoff, selected-status reconciliation, code/test integration, commit, no-op record, or blocker decision.

## Actions

1. If the batch is a refactor, confirm it is pure refactor before editing code: no public signature, test, contract, data, error, protocol, or user-visible behavior change.
2. Re-state the charter before editing: inherited plan gap/existing obligation ID, `N-ID`, one objective, production owner/entry, allowed write paths, required evidence, and closeout rule. If the Anchor/gap trace is absent, the obligation is `INVALID-OBLIGATION`: do not edit code, do not count it as a blocker, and return to planning/router to select a real unmet gap. If the remaining charter is missing or vague, do not edit code; route back to planning or run read-only discovery.
3. Implement only the declared `N-ID`. Existing-code work modifies or extends the current owner by default; do not add a parallel SUT, service, model, parser, client, store, runner, or harness merely to make the red test pass.
4. Use `NEW`/`REPLACEMENT` only as approved. Connect its planned non-test incoming edge and make the wiring test pass through the real route, registry, export, or composition root; a directly constructed test graph or unit green is insufficient. For side-by-side work, also verify the selection point and retirement condition.
5. Implement the smallest code change that satisfies the current admissible red and directly makes the selected `request_gap`'s acceptance predicate true. Every write in the batch must contribute to closing that gap; internal prerequisites remain inside the batch and do not create a separately completable task. Preserve existing behavior unless the Delivery Anchor's accepted delta says otherwise.
6. Map every changed production path and new public symbol to its approved `N-ID`; every new production node needs a non-test incoming edge. Reject an extra active owner unless side-by-side coexistence was approved.
7. Avoid silent fallback, broad catch blocks, hidden defaults, or unrecorded assumptions.
8. Stay inside the planned write set. If the needed fix touches an adjacent path for the same selected gap and owner, update the compact reuse map/plan in place and continue. Stop before editing when the path expands scope, changes ownership/contract, introduces an unapproved production node, or cannot directly support closure of the selected gap.
9. When encountering a nearby bug, failing unrelated test, bad abstraction, dead code, or style issue, classify it:
   - already covered and in-scope because it blocks the current obligation or selected regression: reuse that obligation/evidence and continue; do not add another test;
   - a distinct in-scope failure not covered by the frozen set: report it as a counterexample candidate; only the orchestrator may admit one under the declared cap before work continues;
   - blocking but scope-expanding: stop and route to `10-change-protocol.md`;
   - out-of-scope: keep it read-only and record it in the current handoff/status source only when it is material enough to preserve.
10. If this scope was assigned to an executor, do not implement it in the main thread. Monitor, integrate, or verify instead.
11. In orchestrated work, executors edit only assigned write sets and the explicitly assigned handoff/status surface; the main thread owns integration and final verification.
12. Run the target after the planned gap-closing implementation pass, plus required wiring/selection tests for `NEW`/`REPLACEMENT`. If the same valid obligation remains red, consume only its predeclared finite implementation/repair allowance. When that attempt/time limit is reached, mark the obligation `BLOCKED` and stop; repeated command invocations or a new executor do not renew it. Refactor only while the target remains green and without changing behavior.
13. Run the relevant regression slice. Pure refactor batches keep the protection suite green throughout. Visual-track modules deliver screenshots or preview links instead of filler tests and wait for human-eye acceptance. Existing unrelated failures are evidence to record, not permission to repair unrelated code.
14. Keep the existing obligation/gap ID, red/green commands and outputs, direct write effect, and any actually consumed allowance in commits, the existing TOS row, CI, or the executor handoff. When the write has directly closed the selected `request_gap` and target, required wiring, and selected regression pass, mark the same valid obligation `GREEN`; after its planned review/evidence reconciliation, mark it `VERIFIED`. If tests pass but the write did not close the gap, the batch remains incomplete and cannot select another gap. At the next planned integration/review/closeout sync, batch the applicable evidence label to `PASS:<test-id>@<evidence>`. Update documents immediately only if ownership, `N-ID`, accepted risk, allowance use, or blocker changes; do not claim completion before evidence is synchronized.
15. For orchestrated work, close the executor/worktree loop before assigning the same scope again: integrate or reject code/test/doc changes, run verification, update the one selected status source when used, commit or record an evidence-backed no-op/blocker, and release or advance ownership.
16. Continue only concrete `PENDING` obligations from the frozen `TOS` that are Delivery-Anchor-linked in the same run. After a write closes the current selected gap, return to the Delivery Anchor, recompute its remaining unmet clauses, and select the next gap only from that set. When none remains, return to `00-progress-router.md`, evaluate `DELIVERY-DONE`, and do not search for another behavior or red target.

Read `07-anti-cheat-and-red-replay.md` if a green implementation requires changing tests, fixtures, public signatures, or contract assumptions.

## Output

Code changes tied to the Delivery Anchor, selected `request_gap`, frozen valid obligation, and `N-ID`; evidence that the write directly closed that gap; green/refactor and wiring evidence; batched coverage/evidence updates at the scheduled sync; material candidate/OOS findings without automatic scope expansion; and executor/worktree closeout state when orchestration was used.

## Stop Conditions

Stop if a valid anchor-linked implementation reveals an invalid red/wrong SUT, duplicate active owner, unapproved parallel harness, missing reuse rejection evidence or non-test incoming edge, failed/missing wiring proof, missing side-by-side selection or retirement condition, contract ambiguity, existing behavior conflict, unexpected external drift, an unplanned write path, a vague or missing worktree charter, an unadmitted counterexample/scope-expanding bug fix, a write batch that cannot directly close its selected gap, or a refactor that cannot stay behavior-preserving. Reject `INVALID-OBLIGATION` before implementation and reselect from real anchor gaps; it is not a completion blocker. Exhaustion of the valid frozen `TOS` stops implementation and routes to completion evaluation; it never authorizes another red test.

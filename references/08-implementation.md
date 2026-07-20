# Implementation

## Purpose

Make red tests pass while staying inside the accepted contract and plan.

## Entry Conditions

- Red tests are admissible and fail for the expected reason, the batch is a pure refactor recertified through `00-refactor-intake.md` with existing green tests as protection evidence, or the module is visual-track (no test phase; evidence is screenshots or previews at acceptance).
- The implementation scope is clear.
- The executable compact plan names the stable `N-ID`, current production owner/entry, nearest existing test home/reuse assets, code topology, write set, read-only paths, and any applicable scope firewall for this micro-batch.
- A `NEW`/`REPLACEMENT` has recorded reuse rejection evidence, a planned non-test incoming edge, and a planned real-production wiring test; side-by-side work also has a selection point and retirement condition.
- Writable worktree/executor work has an approved charter: purpose, target ID, write set, evidence, handoff, and closeout rule.
- For refactor work, the observable behavior and existing green protection baseline have been recertified through `00-refactor-intake.md`.
- If execution is orchestrated through subagents, the plan defines executor write sets and the main thread is not implementing the same assigned scope.
- No prior executor/worktree loop for the same feature, module, or micro-batch is awaiting handoff, selected-status reconciliation, code/test integration, commit, no-op record, or blocker decision.

## Actions

1. If the batch is a refactor, confirm it is pure refactor before editing code: no public signature, test, contract, data, error, protocol, or user-visible behavior change.
2. Re-state the charter before editing: target ID, `N-ID`, one objective, production owner/entry, allowed write paths, required evidence, and closeout rule. If it is missing or vague, do not edit code; route back to planning or run read-only discovery.
3. Implement only the declared `N-ID`. Existing-code work modifies or extends the current owner by default; do not add a parallel SUT, service, model, parser, client, store, runner, or harness merely to make the red test pass.
4. Use `NEW`/`REPLACEMENT` only as approved. Connect its planned non-test incoming edge and make the wiring test pass through the real route, registry, export, or composition root; a directly constructed test graph or unit green is insufficient. For side-by-side work, also verify the selection point and retirement condition.
5. Implement the smallest code change that satisfies the current admissible red and contract. Preserve existing behavior unless the contract/change protocol says otherwise.
6. Map every changed production path and new public symbol to its approved `N-ID`; every new production node needs a non-test incoming edge. Reject an extra active owner unless side-by-side coexistence was approved.
7. Avoid silent fallback, broad catch blocks, hidden defaults, or unrecorded assumptions.
8. Stay inside the planned write set. If the needed fix touches an adjacent path for the same accepted behavior and owner, update the compact reuse map/plan in place and continue. Stop before editing only when the path expands scope, changes ownership/contract, or introduces an unapproved production node.
9. When encountering a nearby bug, failing unrelated test, bad abstraction, dead code, or style issue, classify it:
   - in-scope because it blocks this contract/matrix row: add or update the counterexample/test evidence and continue;
   - blocking but scope-expanding: stop and route to `10-change-protocol.md`;
   - out-of-scope: keep it read-only and record it in the current handoff/status source only when it is material enough to preserve.
10. If this scope was assigned to an executor, do not implement it in the main thread. Monitor, integrate, or verify instead.
11. In orchestrated work, executors edit only assigned write sets and the explicitly assigned handoff/status surface; the main thread owns integration and final verification.
12. Run the target test until green, plus required wiring/selection tests for `NEW`/`REPLACEMENT`. Refactor immediately while they remain green without changing behavior.
13. Run the relevant regression slice. Pure refactor batches keep the protection suite green throughout. Visual-track modules deliver screenshots or preview links instead of filler tests and wait for human-eye acceptance. Existing unrelated failures are evidence to record, not permission to repair unrelated code.
14. Keep red/green commands and outputs in commits, CI, or the executor handoff. At the next planned integration/review/closeout sync, batch the applicable `P:<test-id>` cells to `PASS:<test-id>@<evidence>` only after target, wiring when required, and regression tests pass. Update documents immediately only if coverage, ownership, `N-ID`, risk, or blocker changes; do not claim completion before evidence is synchronized.
15. For orchestrated work, close the executor/worktree loop before assigning the same scope again: integrate or reject code/test/doc changes, run verification, update the one selected status source when used, commit or record an evidence-backed no-op/blocker, and release or advance ownership.
16. Continue ready red/green batches in the same run. Return to `00-progress-router.md` at a meaningful contract/scope/evidence checkpoint or when planned behavior is ready for review.

Read `07-anti-cheat-and-red-replay.md` if a green implementation requires changing tests, fixtures, public signatures, or contract assumptions.

## Output

Code changes tied to `N-ID`, green/refactor and wiring evidence, batched coverage/evidence updates at the scheduled sync, material OOS findings if any, and executor/worktree closeout state when orchestration was used.

## Stop Conditions

Stop if implementation reveals an invalid red/wrong SUT, duplicate active owner, unapproved parallel harness, missing reuse rejection evidence or non-test incoming edge, failed/missing wiring proof, missing side-by-side selection or retirement condition, contract ambiguity, existing behavior conflict, unexpected external drift, an unplanned write path, a vague or missing worktree charter, a scope-expanding bug fix, or a refactor that cannot stay behavior-preserving.

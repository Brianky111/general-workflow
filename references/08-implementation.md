# Implementation

## Purpose

Make red tests pass while staying inside the accepted contract and plan.

## Entry Conditions

- Red tests exist and fail for the expected reason, the batch is a pure refactor recertified through `00-refactor-intake.md` with existing green tests as protection evidence, or the module is visual-track (no test phase; evidence is screenshots or previews at acceptance).
- The implementation scope is clear.
- For refactor work, requirements, contracts, and plan have been recertified through `00-refactor-intake.md`.
- If execution is orchestrated through subagents, the plan defines executor write sets and the main thread is not implementing the same assigned scope.

## Actions

1. If the batch is a refactor, confirm it is pure refactor before editing code: no public signature, test, contract, data, error, protocol, or user-visible behavior change.
2. Implement the smallest code change that satisfies the current red micro-batch and contract.
3. Preserve existing behavior unless the contract/change protocol says otherwise.
4. Avoid silent fallback, broad catch blocks, hidden defaults, or unrecorded assumptions.
5. If this scope was assigned to an executor, do not implement it in the main thread. Monitor, integrate, or verify instead.
6. In orchestrated work, executors edit only assigned write sets and progress sections; the main thread owns integration and final verification.
7. Run the target test until green. Refactor immediately while it remains green: improve names, boundaries, duplication, or dependency direction without changing behavior.
8. Run the relevant regression slice. Pure refactor batches have no red phase: keep the protection suite green throughout. Visual-track modules deliver screenshots or preview links instead of filler tests and wait for human-eye acceptance.
9. Update the evidence register and replace the applicable `P:<test-id>` coverage cells with `PASS:<test-id>@<evidence>` only after the target and relevant regression tests pass. Update status/progress from the same evidence.
10. Return to `00-progress-router.md`: select the next red micro-batch while matrix rows remain, otherwise proceed to review.

Read `07-anti-cheat-and-red-replay.md` if a green implementation requires changing tests, fixtures, public signatures, or contract assumptions.

## Output

Code changes, green/refactor evidence, updated matrix row, and progress notes.

## Stop Conditions

Stop if implementation reveals contract ambiguity, existing behavior conflict, unexpected external drift, or a refactor that cannot stay behavior-preserving.

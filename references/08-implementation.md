# Implementation

## Purpose

Make red tests pass while staying inside the accepted contract and plan.

## Entry Conditions

- Red tests exist and fail for the expected reason, or the batch is a pure refactor recertified through `00-refactor-intake.md` with existing green tests as protection evidence.
- The implementation scope is clear.
- For refactor work, requirements, contracts, and plan have been recertified through `00-refactor-intake.md`.
- If execution is orchestrated through subagents, the plan defines executor write sets and the main thread is not implementing the same assigned scope.

## Actions

1. If the batch is a refactor, confirm it is pure refactor before editing code: no public signature, test, contract, data, error, protocol, or user-visible behavior change.
2. Implement the smallest code change that satisfies the contract.
3. Preserve existing behavior unless the contract/change protocol says otherwise.
4. Avoid silent fallback, broad catch blocks, hidden defaults, or unrecorded assumptions.
5. If this scope was assigned to an executor, do not implement it in the main thread. Monitor, integrate, or verify instead.
6. In orchestrated work, executors edit only assigned write sets and progress sections; the main thread owns integration and final verification.
7. Run the red tests until green, then run broader regression checks.
8. Update status/progress with evidence, not with unsupported completion claims.

Read `07-anti-cheat-and-red-replay.md` if a green implementation requires changing tests, fixtures, public signatures, or contract assumptions.

## Output

Code changes, green test evidence, and updated progress notes.

## Stop Conditions

Stop if implementation reveals contract ambiguity, existing behavior conflict, unexpected external drift, or a refactor that cannot stay behavior-preserving.

# Implementation

## Purpose

Make red tests pass while staying inside the accepted contract and plan.

## Entry Conditions

- Red tests exist and fail for the expected reason.
- The implementation scope is clear.

## Actions

1. Implement the smallest code change that satisfies the contract.
2. Preserve existing behavior unless the contract/change protocol says otherwise.
3. Avoid silent fallback, broad catch blocks, hidden defaults, or unrecorded assumptions.
4. Run the red tests until green, then run broader regression checks.
5. Update status/progress with evidence, not with unsupported completion claims.

Read `07-anti-cheat-and-red-replay.md` if a green implementation requires changing tests, fixtures, public signatures, or contract assumptions.

## Output

Code changes, green test evidence, and updated progress notes.

## Stop Conditions

Stop if implementation reveals contract ambiguity, existing behavior conflict, or unexpected external drift.

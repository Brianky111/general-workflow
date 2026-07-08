# Review and Verification

## Purpose

Verify that the implementation satisfies the contract and did not weaken workflow guarantees.

## Entry Conditions

- Implementation exists.
- Target tests are green or there is a known blocker.

## Actions

1. Re-run target tests and the broadest practical regression command.
2. Compare implemented behavior to contract scenarios and invariants.
3. Inspect diffs for test weakening, skipped cases, silent fallback, and unrelated scope.
4. If a single module claims done, read `09-module-initial-review.md`.
5. If all modules claim done, read `09-integration-acceptance.md`.
6. For UI work, capture or inspect visible output when possible.
7. Summarize evidence with exact commands and results.

## Output

Review notes, verification evidence, and any follow-up fixes.

## Stop Conditions

Do not mark complete if required evidence is missing, tests are skipped without approval, or contract coverage is incomplete.

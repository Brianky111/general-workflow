# Review and Verification

## Purpose

Verify that the implementation satisfies the contract and did not weaken workflow guarantees.

## Entry Conditions

- Implementation exists.
- Target tests are green or there is a known blocker.

## Actions

1. Re-run target tests and the broadest practical regression command.
2. Compare implemented behavior to raw/structured requirements, contract scenarios, and invariants.
3. Inspect diffs for test weakening, skipped cases, silent fallback, and unrelated scope.
4. For refactors, verify public signatures, data semantics, error behavior, protocol behavior, authorization behavior, and user-visible outcomes did not drift unless `10-change-protocol.md` approved it.
5. For orchestrated work, verify the main thread acted as orchestrator: executor scopes were explicit, the main thread did not implement the same delegated scope concurrently, and final acceptance is based on local evidence.
6. Verify module ownership, integration boundaries, and that no executor overwrote another executor's scope or progress evidence.
7. If a single module claims done, read `09-module-initial-review.md`.
8. If all modules claim done, read `09-integration-acceptance.md`.
9. For UI work, capture or inspect visible output when possible.
10. Summarize evidence with exact commands and results.

## Output

Review notes, verification evidence, and any follow-up fixes.

## Stop Conditions

Do not mark complete if required evidence is missing, tests are skipped without approval, contract coverage is incomplete, refactor recertification is missing, executor claims cannot be verified, or orchestrated work blurred main-thread and executor ownership.

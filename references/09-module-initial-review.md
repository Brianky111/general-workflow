# Module Initial Review

## Purpose

Run an independent module-level review after CI mechanics pass.

## Entry Conditions

- A module claims green or done.
- Target tests pass.
- The module has not received independent review evidence.
- The reviewer is independent: never the executor who implemented the module.

## Three Judgments

1. **Coverage judgment:** compare method/message/UI-flow list, scenario IDs, invariant IDs, and Feature Test Matrix cells against the evidence register and actual tests; list unknown test IDs, unsupported `PASS`, uncovered rows, or wrongly layered cases.
2. **Anti-hardcoding sample:** add or run one or two boundary examples outside the known fixtures.
3. **Assertion-strength check:** ensure assertion strength matches the Chinese description. A test that says “should equal 20” but only asserts “greater than 0” is weak.

## Output

Write a concise Chinese review report. Every conclusion needs evidence: file path and line number, command output, or CI link.

On pass, record `reviewer` and `reviewEvidence` in the module's `status.json` entry and the 审查 line of its `99-进度.md` section, then return to the router.

## Stop Conditions

No evidence means not reviewed. If coverage or assertion strength fails, route back to `07-red-tests.md` or `08-implementation.md`.

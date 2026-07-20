# Module Initial Review

## Purpose

Run an independent module-level review after CI mechanics pass.

## Entry Conditions

- A risk-triggered or independently owned module claims green or done.
- Target tests pass.
- The module has not received independent review evidence.
- The reviewer is independent: never the executor who implemented the module.

## Three Judgments

1. **Coverage judgment:** compare the authoritative acceptance IDs, changed boundary clauses, sparse/risk-triggered verification map, stable production `N-ID` values, and actual tests; list unsupported `PASS`, wrong-SUT, missing wiring, uncovered behavior, or wrongly layered cases.
2. **Anti-hardcoding sample:** add or run one or two boundary examples outside the known fixtures.
3. **Assertion-strength check:** ensure assertion strength matches the Chinese description. A test that says “should equal 20” but only asserts “greater than 0” is weak.

## Output

Write a concise evidence-backed review in the current handoff, PR, or existing review surface. Create a dedicated report only for long-running multi-owner, high-risk, or formally audited work.

On pass, record `reviewer` and `reviewEvidence` once in the selected status/handoff source when one exists, then return to the router. Do not mirror the result into both `status.json` and `99-进度.md`.

## Stop Conditions

No evidence means not reviewed. If coverage or assertion strength fails, route back to `07-red-tests.md` or `08-implementation.md`.

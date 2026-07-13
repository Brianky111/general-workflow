# Feature Completeness Audit

## Purpose

Decide whether a feature is genuinely complete rather than merely implemented or unit-green. This is the final evidence audit before archiving a change round.

## Entry Conditions

- Module review evidence exists.
- Integration acceptance has exercised the real vertical slice.
- The feature has a current `02-测试矩阵.md` or equivalent lightweight section.

## Definition of Done Audit

Check only applicable items, but require evidence or an explicit accepted `N/A` reason for each.

### Specification

- User goal, non-goals, actors, scenarios, BDD Rules/Examples, permissions, state transitions, concurrency/retry behavior, and recovery behavior are settled and mutually traceable.
- UI states, public schemas, state machine, events, invariants, and cross-feature ownership are explicit in the contract.
- Every accepted BDD example/invariant maps through the test matrix to implementation and evidence; every requirement scenario reaches at least one accepted example.

### Backend and domain

- Domain rules and state transitions have focused unit coverage.
- Use cases prove results, required side effects, and forbidden side effects on failure.
- Repositories/adapters use real schemas or captured fixtures and have integration evidence.
- Dependency failures, idempotency, duplicate delivery, and concurrency are handled when the risk exists.

### Frontend and user experience

- Applicable loading, empty, success, validation, permission, network/server error, retry, disabled/in-flight, and duplicate-submit states work.
- User-visible state comes from persisted/system truth; reload or a new session does not reveal a frontend-only success.
- Critical UI has human-visible evidence; applicable accessibility and visual checks pass.

### Connections and regression

- Runtime contract checks prove frontend/backend or service/service agreement on fields, units, casing, enums, errors, and events.
- Cross-feature handlers and downstream effects have workflow evidence; modules do not reach into each other's persistence as a shortcut.
- Critical E2E paths use the broadest practical real stack and all numbered acceptance scenarios are accounted for.
- Static checks, target tests, broad regression, and selected adversarial/non-functional checks pass.
- Reproducible failures, property seeds, fuzz cases, and surviving mutants have entered counterexample recovery.

## Actions

1. Walk the Feature Test Matrix row and cell at a time. Resolve every test ID through the evidence register and verify each `PASS:<test-id>@<evidence>` against the actual test, command, CI/trace, fixture, and assertion. Required cells may end only as supported `PASS` or accepted `N/A:<reason>`.
2. Reconcile the matrix, integration report, `status.json`, `99-进度.md`, CI, screenshots/traces, and current Git state. Evidence wins over status text.
3. List uncovered or weak rows and route each to the owning stage: contract, test strategy, red tests, implementation, or integration acceptance.
4. Record the audit in `09-完整性审计.md` with four sections: passed evidence, accepted `N/A`, remaining gaps, and closure decision.
5. Only on a pass, update state to done, move the active round into `archive/`, clear `activeRound`, and report the evidence summary. Keep feature-level fixtures in place.
6. Run the lessons pass after closure: propose reusable glossary, architecture, CI, template, or workflow improvements for governed approval.

## Output

An evidence-backed `docs/<module>/<feature>/<round>/09-完整性审计.md`. A pass is the workflow terminal state; a fail routes back without archiving.

## Stop Conditions

Do not mark complete because coverage percentage is high, because all unit tests pass, because the UI looked right once, or because status files say done. A `P:`, `GAP`, blank cell, bare checkmark, unknown test ID, unsupported `PASS`, missing assembly evidence, or frontend-only state blocks closure.

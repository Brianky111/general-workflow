# Feature Completeness Audit

## Purpose

Independently reconcile evidence for a governed or high-risk feature before archiving or making a formal completion claim. Ordinary work closes through targeted review/regression without creating this artifact.

## Entry Conditions

- A named high-risk, formal-audit, regulated, or governed-round trigger requires final independent reconciliation.
- Required module/review and real-layer integration evidence exists.
- The sparse verification map or risk-triggered matrix identifies all required proof.

## Definition of Done Audit

Check only applicable, assigned items. Omit irrelevant categories instead of writing `N/A` proof.

### Specification

- User goal, non-goals, actors, scenarios, BDD Rules/Examples, permissions, state transitions, concurrency/retry behavior, and recovery behavior are settled and mutually traceable.
- UI states, public schemas, state machine, events, invariants, and cross-feature ownership are explicit in the contract.
- Every changed acceptance behavior/invariant maps through the sparse or risk-triggered verification plan to its production `N-ID`, implementation, and evidence.

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

1. Walk only the assigned sparse/risk-triggered proof rows. Resolve every claimed pass against the actual production `N-ID`, test, command, CI/trace, fixture, wiring, and assertion.
2. Reconcile Git, CI, tests, screenshots/traces, integration evidence, and the one selected status source when one exists. Evidence wins over status text; do not require both `status.json` and `99-进度.md`.
3. List uncovered or weak rows and route each to the owning stage: contract, test strategy, red tests, implementation, or integration acceptance.
4. Record passed evidence, remaining gaps, and the closure decision in the existing governed review/round surface. Create `09-完整性审计.md` only when the governing scheme explicitly requires it.
5. Only on a pass, update the selected status source. Move a round into `archive/` and clear `activeRound` only when the project actually uses governed rounds. Keep permanent counterexample fixtures in place.
6. Run the lessons pass after closure: propose reusable glossary, architecture, CI, template, or workflow improvements for governed approval.

## Output

An evidence-backed final reconciliation in the governed review/round surface, with a dedicated `09-完整性审计.md` only when required. A pass is the high-risk/governed terminal state; a fail routes back without archiving.

## Stop Conditions

Do not mark complete because coverage percentage is high, because unit tests alone pass when a connection risk exists, because the UI looked right once, or because status says done. Any assigned `P:`/`GAP`, unknown test ID, wrong production `N-ID`, unsupported pass, missing wiring/assembly evidence, or frontend-only state blocks closure. Missing irrelevant matrix columns or duplicate status files do not.

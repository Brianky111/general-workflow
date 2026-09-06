# Feature Completeness Audit

## Purpose

Independently decide whether every outcome in the original user request and explicitly accepted deltas is complete through the real production path before a governed/high-risk archive or formal completion claim. The `TOS`, matrix, gate, and status surfaces are subordinate evidence, not an alternative definition of feature scope.

## Entry Conditions

- The original user request and explicitly accepted deltas define a finite outcome set, and at least one outcome still needs a formal production-completion judgment.
- An explicitly accepted high-risk, formal-audit, regulated, or governed-round rule requires final independent reconciliation; a reviewer-created risk label alone is not an entry condition.
- Required module/review and real-layer integration evidence exists, and the sparse verification map or risk-triggered matrix identifies only subordinate proof for those outcomes.

## Definition of Done Audit

First check the finite original/accepted outcomes against the real production runtime. Then check only the finite obligations assigned as their evidence before execution. The category lists below are prompts for reconciling those obligations, not a source of additional tests. Omit irrelevant categories instead of writing `N/A` proof.

### Specification

- The user goal, non-goals, actors, scenarios, and assigned BDD Rules/Examples are settled and mutually traceable; permissions, state transitions, concurrency/retry, and recovery appear only when selected by the frozen scope/risk set.
- Assigned UI states, public schemas, state machines, events, invariants, and cross-feature ownership are explicit in the contract.
- Every outcome from the original request or accepted delta maps to its production `N-ID`, real entry, implementation result, and minimum credible evidence; risk/invariant rows remain subordinate to one of those outcomes.

### Backend and domain

- Assigned domain/state obligations have focused rule evidence.
- Assigned use-case obligations prove results, required side effects, and forbidden side effects on failure.
- Assigned repository/adapter risks use real schemas or captured fixtures and have integration evidence.
- Dependency failures, idempotency, duplicate delivery, and concurrency are handled only when the frozen contract/risk set selected them.

### Frontend and user experience

- UI states assigned by the frozen contract/risk set work; the generic state list is not an instruction to add every possible state during audit.
- When persistence truth is assigned, user-visible state survives reload/new session rather than existing only in frontend memory.
- Assigned critical UI has human-visible evidence; selected accessibility and visual checks pass.

### Connections and regression

- Assigned runtime-contract checks prove agreement on the selected fields, units, casing, enums, errors, or events.
- Assigned cross-feature handlers/downstream effects have workflow evidence; modules do not reach into each other's persistence as a shortcut.
- Assigned critical E2E paths use the planned real stack and the frozen acceptance scenarios are accounted for.
- Static checks, target tests, the selected regression command, and pre-budgeted adversarial/non-functional checks support their mapped anchor outcomes; an unrelated or optional check cannot redefine completion.
- Only distinct reproducible in-scope failures admitted within the declared cap have entered counterexample recovery; duplicate seeds, equivalent mutants, already-covered cases, and unadmitted findings do not expand the set.

## Actions

1. Reconcile every original/accepted outcome directly against its actual production `N-ID`, real entry, observable result, and forbidden effects. Only then reconcile its subordinate risk IDs and finite `TOS`. A missing accepted behavior or required seam is `PLANNING-GAP`, not a new audit test, and consumes the single re-freeze correction. A missing governance row or optional proof layer is a follow-up, not a planning gap.
2. Reconcile Git, CI, tests, screenshots/traces, integration evidence, and the one selected status source when one exists. Evidence wins over status text; do not require both `status.json` and `99-进度.md`.
3. Route an existing obligation back only for a reproducible finding that falsifies its anchor outcome in production or destroys that outcome's minimum credible evidence. Weak optional assertions, naming/trace defects, governance/process issues, theoretical edges, and proof layers with no frozen source are follow-up/change candidates, not audit-created tests or completion blockers.
4. Record passed evidence, remaining gaps, and the closure decision in the existing governed review/round surface. Create `09-完整性审计.md` only when the governing scheme explicitly requires it.
5. Only on a pass, update the selected status source. Move a round into `archive/` and clear `activeRound` only when the project actually uses governed rounds. Keep permanent counterexample fixtures in place.
6. After closure, record optional glossary, architecture, CI, template, or workflow lessons as future proposals. The lessons pass cannot reopen the completed feature or its test set.

## Output

An anchor-first final reconciliation in the governed review/round surface: original/accepted outcome -> real production result -> minimum evidence -> closure or delivery-blocking finding. A dedicated `09-完整性审计.md` remains conditional. A pass marks all mapped obligations `VERIFIED`, applies `DELIVERY-DONE`, closes once, and stops. On fail, freeze only the complete delivery-blocking finding set, route affected existing obligations through one aggregate repair, and run one verification audit over exactly that set without archiving. If any frozen finding remains, its obligation is `BLOCKED`; relabeling it cannot open another audit. Governance/naming/optional-enhancement follow-ups stay outside that set.

## Stop Conditions

Do not mark an original/accepted outcome complete because coverage is high, unit tests pass, the UI looked right once, or status says done. Block closure only when a reproducible real-production result contradicts that outcome, its intended production `N-ID` is wrong/unreachable, or required wiring/assembly/persistence evidence is the minimum credible proof and remains missing or unsupported. An assigned `P:`/`GAP`, unknown test ID, naming/trace/governance defect, optional coverage weakness, irrelevant matrix column, or duplicate status file does not block by itself; record it as follow-up unless it causes one of those anchor failures. Repair only the frozen delivery-blocking gaps. Once the original/accepted outcomes and their minimum evidence pass, stop; do not search for additional theoretical cases, rerun discovery, or create tests to improve a metric.

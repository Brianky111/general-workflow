# Feature Grading and Splitting

## Purpose

Choose workflow weight and document granularity before writing detailed contracts.

## Entry Conditions

- A new feature starts.
- The agent is unsure whether full standard flow is necessary.
- A contract is becoming too large or should be split for parallel work.

## Feature Path

- **Standard path:** default. Complete stages 0-5.
- **Lightweight path:** allowed only when all are true:
  - no new external dependency,
  - two or fewer touched modules,
  - no high-cost or irreversible decision.

For lightweight work, preserve raw requirements separately, but structured requirements, interface, and plan may be merged into `00-功能.md`. Old projects still need a code conflict/overlap section. Implementation, review, anti-cheat, and evidence rules do not weaken.

Bug fixes are not feature grading; route to `10-change-protocol.md` level B.

## Large Feature Split Triggers

Split `01-接口.md` into `interfaces/<module>.md` when any trigger applies:

1. three or more stable modules,
2. multiple agents need parallel implementation,
3. external protocol/system needs probes, fixtures, and failure semantics,
4. enhanced/adversarial modules need clearer invariants and counterexample handling,
5. the contract is too long for review,
6. the module will be reused by multiple features.

## Split Shape

Keep `01-接口.md` as an index containing module map, shared model references, cross-module order, reading order, and scenario walkthrough entry. Put method four-questions, field tables, invariants, and failure semantics in module files. Shared entities belong in `domain-models.md`, not copied across modules.

## Stop Conditions

Stop for confirmation if the chosen path reduces documentation burden or changes review gates.

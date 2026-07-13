# Interface Contract

## Purpose

Define the full vertical-slice behavior the code must satisfy before implementation begins. "Interface" includes user interaction, runtime schemas, APIs/events, state transitions, and cross-feature effects; it is not only an HTTP signature.

## Entry Conditions

- Requirements are accepted or have no blocking intent questions.
- No current contract exists, or the contract does not cover required scenarios.

## Actions

1. Define the end-to-end user flow and every applicable UI state: loading, empty, success, validation, permission denied, network/server error, retry, disabled/in-flight, and duplicate submission.
2. Define public behavior: commands, API endpoints, events, files, and runtime schemas shared across frontend/backend or service boundaries. Make units, casing, enums, nullability, versioning, and error forms explicit.
3. Define domain state machines, legal/illegal transitions, data meanings, validation rules, and error behavior.
4. Define cross-feature ownership: which feature owns each state change or event, which features consume it, expected idempotency, and which downstream effects are synchronous or eventually consistent.
5. Add a data model table: `| 字段 | 中文含义 | 示例值 | 来源 | 必填 |`, followed by one complete JSON example.
6. For every method or message, answer four fixed questions: purpose, input example, output example, and failure behavior with explicit loud/silent declaration.
7. Write invariants as `P1`, `P2` statements that hold for all inputs; enhanced/adversarial modules must have them.
8. Map every acceptance scenario across UI -> contract -> application/use case -> domain -> adapter/persistence -> downstream feature effect, and include one walkthrough using the same example data. Cite the `D` decision IDs each clause implements.
9. Add glossary increments for new domain terms.
10. If external systems are involved, read `04-fixtures-and-probes.md` before inventing examples.
11. For large features, read `00-feature-grading-and-splitting.md`, then split module contracts under `interfaces/<module>.md` and keep `01-接口.md` as the index.

## Output

Create or update the active round's `docs/<module>/<feature>/<round>/01-接口.md` and optional `interfaces/*.md`, written in Chinese. For lightweight features, write the contract as a module-sectioned part of `00-功能.md` instead of a separate file. A revision round writes the complete contract after the change, never a delta.

## Contract Gate

The contract is a document-PR human gate. Before user review, always route the draft through `03-ambiguity-audit.md` — the audit is an unconditional second net, not a fallback for known problems. Merge preconditions: the audit report is attached and the `## 待确认反问` section is empty.

For lightweight features this gate merges with the planning gate into one document-PR review of `00-功能.md` (see `00-feature-grading-and-splitting.md`); run the audit and checklist once against that file.

Offer the user this review checklist:

1. Is every field's meaning understandable in plain language?
2. Does the example data survive the scenario walkthrough without broken links or missing fields?
3. Are all failures loud? Are the declared silent cases justified?
4. Do the invariants read as bottom lines that hold for any input?
5. Do raw external-system fields appear only in adapter-layer docs?
6. Do frontend and backend agree on fields, units, casing, enums, errors, and loading/retry semantics through a runtime-checkable contract?
7. Are state ownership, cross-feature events, idempotency, and downstream effects explicit?
8. Are existing-code conflicts and overlaps clearly explained: current behavior, target behavior, risk, and why the decision is deferred to planning?

Merge freezes the contract. Code stubs are generated after the planning gate — `06-planning.md` owns that instruction; CI owns doc-vs-stub signature comparison. Questions raised before the freeze go to the question list; questions raised after the freeze go to `10-change-protocol.md`.

## Stop Conditions

Stop for user review when contract choices affect product behavior, user-visible text, external compatibility, or data semantics, and always at the contract gate before planning or implementation. A method without example data is incomplete; an old project without a concrete conflict report is incomplete.

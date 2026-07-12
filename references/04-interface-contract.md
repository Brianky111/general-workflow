# Interface Contract

## Purpose

Define the behavior the code must satisfy before implementation begins.

## Entry Conditions

- Requirements are accepted or have no blocking intent questions.
- No current contract exists, or the contract does not cover required scenarios.

## Actions

1. Define public behavior: commands, API endpoints, UI flows, events, or files.
2. Define data models, field meanings, validation rules, and error behavior.
3. Add a data model table: `| 字段 | 中文含义 | 示例值 | 来源 | 必填 |`, followed by one complete JSON example.
4. For every method, answer four fixed questions: purpose, input example, output example, and failure behavior with explicit loud/silent declaration.
5. Write invariants as `P1`, `P2` statements that hold for all inputs; enhanced/adversarial modules must have them.
6. Map every acceptance scenario to contract behavior and include one end-to-end scenario walkthrough using the same example data.
7. Add glossary increments for new domain terms.
8. If external systems are involved, read `04-fixtures-and-probes.md` before inventing examples.
9. For large features, read `00-feature-grading-and-splitting.md`, then split module contracts under `interfaces/<module>.md` and keep `01-接口.md` as the index.

## Output

Create or update `docs/features/<feature>/01-接口.md` and optional `interfaces/*.md`, written in Chinese. For lightweight features, write the contract as a module-sectioned part of `00-功能.md` instead of a separate file.

## Contract Gate

The contract is a document-PR human gate. Before user review, always route the draft through `03-ambiguity-audit.md` — the audit is an unconditional second net, not a fallback for known problems. Merge preconditions: the audit report is attached and the `## 待确认反问` section is empty.

Offer the user this review checklist:

1. Is every field's meaning understandable in plain language?
2. Does the example data survive the scenario walkthrough without broken links or missing fields?
3. Are all failures loud? Are the declared silent cases justified?
4. Do the invariants read as bottom lines that hold for any input?
5. Do raw external-system fields appear only in adapter-layer docs?
6. Are existing-code conflicts and overlaps clearly explained: current behavior, target behavior, risk, and why the decision is deferred to planning?

Merge freezes the contract. Then generate code stubs from the doc (signatures plus Chinese comments plus `throw new Error('尚未实现')`); CI owns doc-vs-stub signature comparison. Questions raised before the freeze go to the question list; questions raised after the freeze go to `10-change-protocol.md`.

## Stop Conditions

Stop for user review when contract choices affect product behavior, user-visible text, external compatibility, or data semantics, and always at the contract gate before planning or implementation. A method without example data is incomplete; an old project without a concrete conflict report is incomplete.

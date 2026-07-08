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

Create or update `docs/features/<feature>/01-接口.md` and optional `interfaces/*.md`.

## Stop Conditions

Stop for user review when contract choices affect product behavior, user-visible text, external compatibility, or data semantics.

Before approval, route to `03-ambiguity-audit.md` if any field default, failure semantics, scenario conflict, or old/new behavior conflict remains unresolved.

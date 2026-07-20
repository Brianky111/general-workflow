# Requirements Capture

## Purpose

Preserve a durable source and express only the behavior needed for a safe, testable implementation. For an ordinary feature, the raw source plus concise structured requirements and BDD examples form the complete core contract.

## Entry Conditions

- User intent has no durable source or concise behavior contract.
- The request is scattered across chat, issue text, screenshots, or notes.
- A new request may overlap an existing feature boundary.

Refactor, cleanup, or restructure requests route to `00-refactor-intake.md`. When behavior docs are missing, capture only the behavior the refactor must preserve; do not invent a new feature named after the refactor.

## Durable Raw Source

Link the existing task, issue, message, attachment, or accepted specification when it is stable and accessible. Create `00-原始需求.md` only when the source would otherwise be lost, is split across ephemeral inputs, or formal audit requires an append-only snapshot. Do not duplicate a durable source merely to satisfy the workflow.

## Similarity Triage

Keep one authoritative contract for one behavior. Scan the feature roster when one exists, nearby structured requirements, module boundaries, glossary terms, and relevant code/tests.

Classify the request:

- **New:** independently observable and independently acceptable behavior. Create or use its own core contract.
- **Merge:** extends an unconfirmed contract within the same behavior boundary. Append the source and examples to that contract.
- **Revision:** changes an already accepted behavior or frozen contract. Route to `10-change-protocol.md` and record a delta by default.

Make an evidence-backed classification without pausing when one option is clearly faithful to the request. Ask once only when the alternatives materially change user-visible scope, contract ownership, compatibility, or history. Present the concrete overlap, the two plausible outcomes, and a recommendation; do not create a feature folder merely to hold the question.

## Structured Requirement

Keep the ordinary structured requirement concise and include:

- source reference;
- goal and non-goals;
- actors or affected users when relevant;
- observable acceptance behaviors with stable IDs;
- changed UI, public schema, state, persistence, or downstream effects;
- concrete exclusions and blocking assumptions;
- the selected `lean` path or a named risk exception from `00-feature-grading-and-splitting.md`.

Use `AC1`, `AC2`, ... for the lean path and express the corresponding Given/When/Then examples inline through `03-bdd-example-mapping.md`. Existing S/E/B and R/EX IDs may remain authoritative when already established or when regulated traceability requires them. Do not create parallel ID systems for the same behavior.

Cover failure, permission, boundary, concurrency, recovery, persistence, UI, or cross-feature cases only when the request or code risk makes them applicable. Do not write per-category `N/A` proof.

## Questions and Authorization

Mark only unresolved choices that can change observable behavior, external compatibility, data meaning, security, irreversible effects, or ownership. Decide reversible internal design choices yourself and record them only when they constrain later work.

When the user explicitly authorized implementation and the structured requirement faithfully restates that request, do not ask for a second confirmation. A new product choice or material assumption still routes to `03-requirements-clarification.md`.

## READY Transition

After the BDD examples are concrete and the targeted ambiguity audit has no blocking finding, apply the READY check in `00-feature-grading-and-splitting.md`. The raw source, structured requirement, and BDD examples are sufficient for an ordinary feature; missing dedicated interface, conflict, matrix, or status files do not block READY unless their risk trigger exists.

Freeze the core contract at its source/commit reference and continue into planning, tests, and implementation in the same run. Do not require a separate requirement/BDD human gate for a faithful restatement already authorized by the user.

## Output

Prefer one `00-功能.md` or the repository's existing task/spec location containing structured requirements and inline BDD examples. Use separate `00-原始需求.md` or `00-行为示例.md` only when source durability, independent ownership, document size, or formal traceability justifies it. Stay within the default pre-code budget: two new artifacts, 160 nonblank lines, one human pause, and at most 20% of expected effort or 30 minutes.

## Stop Conditions

Stop only for a real blocking behavior, compatibility, data, security, irreversible-effect, or ownership decision. Otherwise finish the core contract and continue in the same run.

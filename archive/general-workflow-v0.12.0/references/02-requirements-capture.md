# Requirements Capture

## Purpose

Preserve the original request as immutable delivery history and express only the behavior needed for a safe, testable implementation. For an ordinary feature, the Delivery Anchor plus concise structured requirements and BDD examples form the complete core contract.

## Entry Conditions

- User intent has no durable source or concise behavior contract.
- The request is scattered across chat, issue text, screenshots, or notes.
- A new request may overlap an existing feature boundary.

Refactor, cleanup, or restructure requests route to `00-refactor-intake.md`. When behavior docs are missing, capture only the behavior the refactor must preserve; do not invent a new feature named after the refactor.

## Durable Raw Source

Link the existing task, issue, message, attachment, or accepted specification when it is stable and accessible. Create `00-原始需求.md` only when the source would otherwise be lost, is split across ephemeral inputs, or formal audit requires an append-only snapshot. Do not duplicate a durable source merely to satisfy the workflow.

## Delivery Anchor

The Delivery Anchor is the immutable original request/source plus the ordered set of explicitly accepted deltas. Keep it inline in the existing task, issue, change note, or core contract by linking those sources; do not create an Anchor document, ID namespace, or rewritten “clean” original. An accepted delta updates the current effective Anchor state while every earlier source remains unchanged and reviewable.

Structured requirements, BDD examples, plans, and tests are faithful projections of the current Anchor state, not authorities that can reinterpret it. When a projection conflicts with the Anchor, correct the projection or record a concrete `request_gap`; never edit history to make downstream work look consistent. A reviewer, test, tool, executor, orchestrator, or external-drift finding is only evidence or a change candidate until the user or an accepted authoritative product/contract source authorizes a delta under `10-change-protocol.md`; drift covered by an existing compatibility promise instead shows that same outcome is unmet.

## Similarity Triage

Keep one authoritative contract for one behavior. Scan the feature roster when one exists, nearby structured requirements, module boundaries, glossary terms, and relevant code/tests.

Before classifying a similar name as New/Merge/Revision, run the solution candidate gate in `00-solution-framing.md`. If the request describes an application, client, platform, program, migration, or rollout containing several independently acceptable capabilities, construction stages, or an aggregate acceptance result, frame/update the solution first and then triage each routed behavior against its owning feature. Never merge the aggregate request itself into a feature contract.

Treat names only as discovery hints. A shared product prefix or a suffix such as Android, iOS, web, or desktop does not prove a shared behavior boundary. Decide from observable acceptance, whether one contract can own the whole result faithfully, participant sources/owners, construction dependencies, and aggregate proof. `btw-client-Android`, for example, may be an Android-client solution even if `btw-client` is an existing feature; only an Android-specific delta to the same capability qualifies for Merge or Revision.

Classify the request:

- **New:** independently observable and independently acceptable behavior. Create or use its own core contract and establish its Anchor from the durable source.
- **Merge:** extends an unconfirmed contract within the same behavior boundary. Append the source to that Anchor and update its faithful projections.
- **Revision:** changes an already accepted behavior or frozen contract. Route to `10-change-protocol.md` and append an accepted delta without rewriting earlier sources.

Make an evidence-backed classification without pausing when one option is clearly faithful to the request. Ask once only when the alternatives materially change user-visible scope, contract ownership, compatibility, or history. Present the concrete overlap, the two plausible outcomes, and a recommendation; do not create a feature folder merely to hold the question.

## Structured Requirement

Keep the ordinary structured requirement concise as a projection of the current Delivery Anchor state and include:

- original source and accepted-delta references;
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

Do not promote a tool or reviewer finding into a requirement. It may correct an inaccurate projection of behavior already in the Anchor, identify a concrete `request_gap`, or wait as a change candidate until an authorized delta changes the Anchor.

## READY Transition

After the BDD examples are concrete and the targeted ambiguity audit has no blocking finding, apply the READY check in `00-feature-grading-and-splitting.md`. The raw source, structured requirement, and BDD examples are sufficient for an ordinary feature; missing dedicated interface, conflict, matrix, or status files do not block READY unless their risk trigger exists.

Freeze the current effective Delivery Anchor state and its faithful core-contract projection at the existing source/commit reference, then continue into planning, tests, and implementation in the same run. Do not require a separate requirement/BDD human gate for a faithful restatement already authorized by the user.

## Output

Prefer one `00-功能.md` or the repository's existing task/spec location containing the Anchor source links, structured requirements, and inline BDD examples. Use separate `00-原始需求.md` or `00-行为示例.md` only when source durability, independent ownership, document size, or formal traceability justifies it. Never create a separate Delivery Anchor artifact. Stay within the default pre-code budget: two new artifacts, 160 nonblank lines, one human pause, and at most 20% of expected effort or 30 minutes.

## Stop Conditions

Stop only for a real blocking behavior, compatibility, data, security, irreversible-effect, or ownership decision. Otherwise finish the core contract and continue in the same run.

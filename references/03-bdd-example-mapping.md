# BDD Example Mapping

## Purpose

Project the current Delivery Anchor state into a few concrete, observable examples that can guide tests and implementation. BDD is a faithful lean-contract projection; it is not an authority that can expand the request, nor automatically a separate document or human gate.

## Entry Conditions

- The structured requirement states a goal and observable acceptance behaviors.
- An accepted behavior changed or lacks a concrete example.
- A named risk needs additional boundary or failure examples.

Pure refactors and bug fixes reuse accepted behavior unless a counterexample proves a gap. Do not restate unchanged behavior merely to refresh a template.

The immutable original source plus ordered accepted deltas is the Delivery Anchor defined in `02-requirements-capture.md`. Reuse its existing source links and acceptance IDs; do not create an Anchor file or BDD-specific scope. When an accepted delta changes the current Anchor state, revise only the affected examples while preserving the earlier source/delta history.

## Lean Example Form

For an ordinary feature, keep one stable acceptance ID from requirement through test evidence:

```markdown
### AC1：<可观察行为>
- Given：<相关前置状态>
- When：<一个业务触发>
- Then：<可观察结果>
- 失败底线：<不得发生的副作用；不适用时省略>
- 验证：<最低可信层或命令，允许在实现时补具体路径>
```

Do not create separate S/E/B, R/EX, D, P, and matrix-row IDs for the same lean behavior. Preserve an existing ID scheme when it is already authoritative. Use a separate Rule/Example index only when formal traceability, independent owners, or a genuinely large behavior set requires it.

## Actions

1. Reuse each structured requirement's acceptance ID, trace it to the current Delivery Anchor source/delta, and write at least one concrete Given/When/Then example.
2. Keep Given to relevant state, When to one business trigger, and Then to observable outcomes. State forbidden side effects only when failure could otherwise cause them.
3. Add alternative, error, boundary, permission, concurrency, recovery, persistence, UI, or cross-feature examples only when the Anchor or an accepted named risk makes them applicable. A tool/reviewer finding may sharpen an already anchored outcome, but cannot create a new example scope without an accepted delta. Do not prove every absent category with `N/A`.
4. Trace an example directly to its source requirement by sharing the same ID or a simple link; do not build a bidirectional table when the relationship is already one-to-one and obvious.
5. Keep examples technology-neutral unless a public technology or protocol is itself part of observable behavior.
6. Route only genuine behavior choices to `03-requirements-clarification.md`. Decide reversible technical details without asking the user.
7. Record a dedicated `.feature` file only when the project actually runs executable Gherkin; do not keep competing Markdown and Gherkin truths.

## READY Gate

The behavior portion is sufficient when:

- every accepted behavior has a concrete example;
- examples faithfully project the current Delivery Anchor state and do not contradict its original source, accepted deltas, or each other;
- every real failure risk names the observable result and any material forbidden side effect;
- no unresolved question can change user-visible behavior, compatibility, data meaning, security, irreversible effects, or ownership;
- a credible verification approach exists for each behavior.

Run the targeted check in `03-ambiguity-audit.md`. A clean result plus existing user authorization freezes the core contract without another confirmation. Then apply the READY check in `00-feature-grading-and-splitting.md` and continue into planning, tests, and implementation in the same run.

## Risk-Triggered Expansion

Expand examples only for an affected risk already present in the Delivery Anchor or explicitly accepted as a delta:

- public/external compatibility: consumer and failure examples;
- migration or irreversible effects: before/after and rollback outcomes;
- security or permission boundaries: allowed and denied examples;
- concurrency, idempotency, or complex state: interleavings, duplicates, and illegal transitions;
- cross-owner events/state: producer, consumer, timing, and retry outcomes;
- formal audit: explicit source-to-example traceability.

The expansion counts against the document budget unless the named risk exception explains why it must exceed it.

## Output

Default to an inline BDD section in the structured requirement or `00-功能.md`. Create `00-行为示例.md` or use-case files only for a named expansion trigger. Link the existing Anchor sources; do not add a separate Anchor, behavior-confirmation timestamp, or ID layer when the same authorized core-contract reference proves acceptance.

## Stop Conditions

Stop only for a concrete `request_gap`, blocking behavior decision, or Anchor/projection contradiction that cannot be resolved from evidence. A new tool/reviewer idea is a change candidate, not an automatic blocker. Missing optional categories, a separate trace table, or a dedicated BDD file do not block implementation.

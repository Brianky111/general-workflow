# BDD Example Mapping

## Purpose

Turn the structured requirement into a few concrete, observable examples that can guide tests and implementation. BDD is part of the lean core contract; it is not automatically a separate document or human gate.

## Entry Conditions

- The structured requirement states a goal and observable acceptance behaviors.
- An accepted behavior changed or lacks a concrete example.
- A named risk needs additional boundary or failure examples.

Pure refactors and bug fixes reuse accepted behavior unless a counterexample proves a gap. Do not restate unchanged behavior merely to refresh a template.

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

1. Reuse each structured requirement's acceptance ID and write at least one concrete Given/When/Then example.
2. Keep Given to relevant state, When to one business trigger, and Then to observable outcomes. State forbidden side effects only when failure could otherwise cause them.
3. Add alternative, error, boundary, permission, concurrency, recovery, persistence, UI, or cross-feature examples only when the request, code, or named risk makes them applicable. Do not prove every absent category with `N/A`.
4. Trace an example directly to its source requirement by sharing the same ID or a simple link; do not build a bidirectional table when the relationship is already one-to-one and obvious.
5. Keep examples technology-neutral unless a public technology or protocol is itself part of observable behavior.
6. Route only genuine behavior choices to `03-requirements-clarification.md`. Decide reversible technical details without asking the user.
7. Record a dedicated `.feature` file only when the project actually runs executable Gherkin; do not keep competing Markdown and Gherkin truths.

## READY Gate

The behavior portion is sufficient when:

- every accepted behavior has a concrete example;
- examples do not contradict the raw source or each other;
- every real failure risk names the observable result and any material forbidden side effect;
- no unresolved question can change user-visible behavior, compatibility, data meaning, security, irreversible effects, or ownership;
- a credible verification approach exists for each behavior.

Run the targeted check in `03-ambiguity-audit.md`. A clean result plus existing user authorization freezes the core contract without another confirmation. Then apply the READY check in `00-feature-grading-and-splitting.md` and continue into planning, tests, and implementation in the same run.

## Risk-Triggered Expansion

Expand examples only for the affected risk:

- public/external compatibility: consumer and failure examples;
- migration or irreversible effects: before/after and rollback outcomes;
- security or permission boundaries: allowed and denied examples;
- concurrency, idempotency, or complex state: interleavings, duplicates, and illegal transitions;
- cross-owner events/state: producer, consumer, timing, and retry outcomes;
- formal audit: explicit source-to-example traceability.

The expansion counts against the document budget unless the named risk exception explains why it must exceed it.

## Output

Default to an inline BDD section in the structured requirement or `00-功能.md`. Create `00-行为示例.md` or use-case files only for a named expansion trigger. Do not add a separate behavior-confirmation timestamp when the same authorized core-contract reference proves acceptance.

## Stop Conditions

Stop only for a blocking behavior decision or a contradiction that cannot be resolved from evidence. Missing optional categories, a separate trace table, or a dedicated BDD file do not block implementation.

# Test Strategy and Feature Test Matrix

## Purpose

Freeze a finite set of required proofs, discharge each at the cheapest trustworthy layer, and prove only named risky connections through the real production assembly. Use a sparse coverage map for ordinary work and expand to a full matrix only when risk triggers; passing unit tests or reporting coverage percentage alone never proves completeness, and the possibility of stronger coverage never authorizes an unbounded test loop.

## Contents

- Confidence Ladder
- Default sparse coverage view
- Risk-triggered full matrix
- Evidence register
- Build Procedure
- Verification Gate and output

## Entry Conditions

- The compact behavior contract is ready.
- The plan declares the Delivery Anchor and one selected `request_gap` once, using the original request or a user-/authoritative-source-accepted delta plus an existing acceptance/contract ID or exact source clause; rows inherit that context and do not repeat the full source.
- The code-reality/reuse map assigns stable `N-ID` values and records each node's production owner/entry plus nearest existing test home and reuse assets.
- A plan needs a sparse behavior-to-proof map, or a named connection/safety/compatibility risk needs expanded verification.

## Confidence Ladder

Choose only the layers needed for the risk; do not duplicate every scenario at every layer.

| Layer | Primary question |
|---|---|
| Static checks | Does it compile, type-check, lint, and respect layer boundaries? |
| Domain unit | Is one business rule, value object, calculation, or state transition legal? |
| Use-case unit | Is the flow ordered correctly, with the right result and side effects? |
| Frontend logic/component/page | Does the UI expose the right states and respond as a user would expect? |
| Adapter/repository integration | Do persistence, mappers, SDK adapters, and real schemas agree? |
| Contract | Do producer and consumer agree on fields, units, casing, enums, errors, and events? |
| Feature integration | Does the feature run from the real production route/composition root through the intended registered nodes, rather than a test-only assembly? |
| Cross-feature workflow | Do owned events and downstream effects connect without hidden database coupling? |
| E2E acceptance | Can a user complete the critical path through real UI/API/persistence and still see truth after reload? |
| Risk checks | Do adversarial, security, concurrency, performance, accessibility, and visual checks cover the selected risks? |

## Feature Test Mapping

Keep the default sparse coverage view in the minimum executable plan, current task plan, or existing owning document. A standalone `02-测试矩阵.md` is a risk-triggered durable artifact, not the ordinary default. Add the risk-triggered full matrix only when a trigger below applies.

### Cell notation

- `P:T-UC-EX1` — planned test with a stable test ID.
- `PASS:T-UC-EX1@<evidence>` — executed-test evidence kind; when accepted, the owning obligation becomes `VERIFIED`.
- `GAP:<reason>` — required proof is missing and blocks the planning or completion gate.
- `EXISTING-PASS:<test-id>@<evidence>` — evidence kind showing the real production owner already satisfies the frozen obligation; mark its state `VERIFIED`, with no manufactured red.

Never use a bare checkmark. Do not create a fixed nine-layer table filled with `N/A`; ordinary behavior lists only the few tests that add confidence.

## Default Sparse Coverage View

Create one row per distinct changed acceptance behavior or invariant and name only the selected protection obligations. Reuse the authoritative `AC` or existing `R/EX/P` ID plus a proof-kind suffix; do not invent another document or trace-ID layer:

```markdown
| 行为示例/不变量（existing ID） | 上游场景 | 用户可见结果与失败底线 | 风险标签 | 有限义务键 / 保护测试（层级） | 被测 N-ID / 生产 owner / 真实入口 | 总状态 |
|---|---|---|---|---|---|---|
| R1/EX1 正常提交 | S1 | 显示成功；失败时不得保存 | 普通规则 | `R1/EX1:rule` / P:T-UC-EX1（Use Case） | N3 / `route -> handler -> service` | PENDING |
| R1/EX2 非法状态 | E1 | 明确拒绝；不得调用外部依赖 | 副作用 | `R1/EX2:rule` / P:T-D-EX2（Domain） | N2 / `handler -> aggregate` | PENDING |
```

One test may protect several rows, but each relationship stays explicit. A row that genuinely needs no executable test must state the accepted non-test evidence and approval instead of inventing filler coverage.

## Finite Test Obligation Set

The sparse map or triggered matrix is the finite Test Obligation Set (`TOS`) for the current work. Default to one rule obligation per distinct changed behavior/invariant. Add at most one connection obligation per named seam that can fail independently; do not duplicate the same behavior at every layer. Equivalent examples, seeds, and boundary values share a parameterized obligation when they have the same rule and failure bottom line.

Every row must trace through its existing acceptance/obligation ID to the one plan-level Delivery Anchor and selected `request_gap`; do not repeat the full source reference in each row. A row without that trace, or whose assertion cannot prove the selected gap, is `INVALID-OBLIGATION`. This is not a TOS state and is never part of the completion denominator: it cannot enter red, consume repair/campaign allowances, become `BLOCKED`, or prevent Delivery Anchor completion. Correct an omitted faithful trace through the one `PLANNING-GAP` re-freeze allowance; otherwise retain the item only as a non-authorizing candidate/follow-up.

Tests and review findings do not create obligations. After planning freezes the set, only an accepted anchor delta or a distinct reproducible anchor-falsifying counterexample admitted under the delivery-level integer cap may append a row. Discovery is off by default, its empty campaign set is closed by default, and unused allowance counters are not materialized. A triggered probe, pairwise/generated-case, property, fuzz, mutation, or adversarial pass needs a frozen campaign ID, invariant/scope, command/configuration, wall-clock or attempted-case/mutant/request limits, and cap consumption. Stop at the first limit—or when the declared finite input scope is exhausted—and mark `DISCOVERY-CLOSED`; the same delivery cannot reset or append budget through a reroute, executor, session, or renamed campaign. Duplicate cases/seeds, equivalent mutants, already-covered inputs, and theoretical concerns do not append rows.

## Risk-Triggered Full Matrix

Expand the sparse view only when at least one trigger applies:

- a `NEW`, `REPLACEMENT`, or side-by-side node needs production wiring or cutover proof;
- a schema, protocol, persistence adapter, generated client, or external fixture crosses a boundary;
- a cross-feature event, user-critical end-to-end path, authorization rule, state machine, concurrency/idempotency rule, or irreversible action is involved;
- the plan selects enhanced or adversarial validation.

Add one column only for each triggered seam from the Confidence Ladder. Omit irrelevant layer columns instead of filling them with `N/A`. For example, a replacement crossing a contract and production registration may use:

```markdown
| 行为/不变量（existing ID） | 规则测试 | 契约 | Wiring / Feature 集成 | E2E | 总状态 |
|---|---|---|---|---|---|
| R1/EX1 | P:T-UC-EX1 | P:T-CT-EX1 | P:T-WIRE-EX1 | P:T-E2E-EX1 | PENDING |
```

Every triggered column contains a stable test ID or `GAP:<reason>`. `NEW`/`REPLACEMENT` always triggers wiring coverage through the real production route, registry, export, or composition root. Side-by-side work also covers the runtime selection point and retirement condition.

## Evidence Register

For ordinary single-owner work, the sparse row may carry the test path, command, and reuse facts directly. Use the expanded register below only when durable multi-owner handoff, a risk-triggered matrix, CI evidence reconciliation, or formal traceability needs it.

```markdown
| 测试 ID | 覆盖场景（existing ID） | 层级 | 被测 N-ID / 生产 owner/SUT | 真实生产入口/装配根 | 既有测试归宿/复用资产 | 测试文件 | 命令与环境 | Fixture/seed 与允许替身边界 | 关键断言 | 负责人 | 状态与证据 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T-UC-EX1 | R1/EX1, S1 | Use Case unit | N3 / `<symbol>` | `route -> handler -> N3` | `<nearest test>`；<runner/factory> | `<path>` | `<command>` | <只替代 collaborator> | 结果正确；保存一次 | `<owner>` | PENDING |
| T-WIRE-EX1 | R1/EX1, S1 | Feature integration | N3 / `<registered symbol>` | `<real composition root>` | `<integration suite>` | `<path>` | `<command + env>` | <不得替换 SUT/registration> | 实际入口解析 N3；断开注册即失败 | `<owner>` | PENDING |
```

## Build Procedure

1. Start from the plan-level Delivery Anchor and selected `request_gap`, then create one sparse coverage row for every changed acceptance behavior or invariant needed to prove that gap. Preserve the repository's existing ID so rows inherit the mapping without repeating the source, and write the user-visible result plus material forbidden side effects first; do not let test design create a new gap.
2. Bind every planned test to the stable `N-ID`, current production owner, real runtime/assembly entry, and nearest existing test home/reuse assets from the conflict scan.
3. Reuse the established runner, suite, factories, fixtures, and helpers by default. A new parallel SUT or harness requires an approved conflict/plan item; never create one merely to obtain a red failure.
4. Assign the lowest layer that proves the rule precisely. Add a higher layer only for a triggered connection or risk; fakes/stubs may replace collaborators, never the SUT, production owner, or registration under proof.
5. For `NEW`/`REPLACEMENT`, require reuse rejection evidence, a non-test incoming edge, and a wiring test from the real production composition root. For side-by-side work, test the selection point and retirement condition.
6. Expand to the full matrix only for the listed triggers. Shared schemas need contract coverage, cross-feature events need workflow coverage, and user-critical paths need representative E2E acceptance.
7. Freeze the finite obligation rows and any discovery/admission budgets before execution. Cover applicable assigned UI states and failure side effects without copying the same scenario across every layer. Select adversarial checks only for recorded risks.

## Verification Gate

The verification plan is executable when:

- every changed acceptance behavior or invariant has a sparse row under the authoritative ID;
- every row traces through an existing ID to the plan-level Delivery Anchor/selected `request_gap`, and its assertion can close a proof need subordinate to that gap; no `INVALID-OBLIGATION` is treated as executable or blocking;
- every row names precise protection tests or approved non-test evidence, with no unsupported checkmarks or `GAP`;
- every planned test's sparse row or optional evidence-register entry records its `N-ID`, production entry/assembly root, existing test home/reuse assets, path, command/environment, allowed doubles, owner, and key assertion;
- every `NEW`/`REPLACEMENT` has reuse rejection evidence, a non-test incoming edge, and real-production wiring coverage; side-by-side work has selection and retirement coverage;
- every risk trigger has the corresponding dynamic full-matrix column and no required connection is represented only by a directly constructed test graph.
- the `TOS` is finite and frozen; discovery is absent by default, and every actually selected discovery pass has explicit execution and admission limits.

Planning freezes required proof and ownership, not the later evidence value. Strengthen assertions or correct SUT binding inside the same obligation; do not add proof kinds or cases merely because more coverage is possible. Weakening accepted proof, changing `N-ID`, changing ownership, or expanding a named risk reopens only the affected plan/change delta.

Do not rewrite matrix or progress documents after every red/green command or micro-step. Keep command output in commits, CI, or the executor handoff, and batch `P:` to `PASS:` evidence updates at the next planned integration, review, or closeout sync. Update immediately only when the frozen obligation set, ownership, `N-ID`, accepted risk, or blocker changes; status must not claim completion before the evidence sync.

## Output

Record the sparse map in the minimum executable plan or existing owning contract. Create or update `02-测试矩阵.md` only for a named risk trigger, durable multi-owner handoff, or formal traceability need; include only triggered layer columns. Link rows to the authoritative acceptance IDs, stable `N-ID` values, production/test anchors, and evidence.

Return to `06-planning.md` only when it delegated this risk decision; otherwise continue directly to an admissible red once the Verification Gate passes.

## Stop Conditions

Do not enter implementation while required proof for the selected anchor gap is `GAP`, the valid `TOS` or a discovery pass is unbounded, a test targets the wrong/unregistered SUT, or a triggered wiring/contract/safety check is absent. Do not enter red for an `INVALID-OBLIGATION`, and do not let it block completion; reject it and reselect from real anchor gaps. Do not mark complete while required anchor-linked evidence remains planned or unsupported. When every Delivery Anchor gap is closed, all valid frozen obligations are `VERIFIED`, and `DELIVERY-DONE` holds, stop; do not search for a stronger matrix. The absence of a standalone matrix is not a blocker when the sparse plan is sufficient.
